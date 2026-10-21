"""Elmo G-TWI drive thermal derate (Arbiter R-141 e8b74e7; Electronics §18.5 P-055 23f6992 + addendum 430684c).

Curve (on drive temperature, °C): scale 1.0 at <= 75, linear to 0.5 at 82, held at 0.5 to 84; at >= 84 latch a
controlled stop for the WHOLE robot (safe sit via the WBC/fall-mode path, then MO=0 on all drives). Resume needs
every drive < 78 °C AND an explicit re_enable(). The drive's own trip (85 °C, MF 0xD000 / EMCY 0x4310) is a fault
input that also latches the stop.

Actuation (430684c): CL[1]/PL[1] stay commissioned and are never written or saved. Each cycle the master writes
CiA-402 0x6072 "Max torque" (RxPDO 0x160D/0x1605) = round(scale * nominal_permille), per-mille of 0x6075.
Alternative (config): 0x6073 "Max current" (RxPDO 0x160E). Bench-verify items are listed in DRIVE_DERATE.md.

Temperature source (config): primary 0x22A2:00 (UINT16 °C, 1 kHz TxPDO); candidate 0x22A3:n; fallback SDO at
10 Hz round-robin. Stale/missing reads -> fail-safe scale after N cycles; implausible jumps are rejected.

Pure logic: no EtherCAT here. A DriveIO implementation (the master) does the I/O.
"""
import json
import math
import os
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = os.path.join(HERE, '..', 'controller_config.json')


@dataclass
class DerateConfig:
    t_start: float = 75.0          # R-141
    t_half: float = 82.0           # R-141: 0.5 here
    scale_min: float = 0.5
    t_stop: float = 84.0           # R-141 controlled stop
    t_resume: float = 78.0         # R-141 hysteresis
    t_drive_trip: float = 85.0     # drive's own shut-off [CR p.284]
    temp_source: str = '0x22A2:00'  # primary (430684c); '0x22A3:1'..4 candidate; 'sdo' fallback
    loop_hz: float = 1000.0
    sdo_hz: float = 10.0           # per drive, round-robin, when temp_source == 'sdo'
    stale_s_pdo: float = 0.020     # 20 missed 1 kHz samples
    stale_s_sdo: float = 0.5       # 5 missed 10 Hz samples
    stale_scale: float = 0.5       # fail-safe derate while stale
    stale_stop_s: float = 5.0      # still no valid temperature -> controlled stop
    max_rate_K_s: float = 3.0      # plausibility: plate tau >= 185 s, <= 0.3 K/s (430684c); 10x margin
    jump_floor_K: float = 2.0      # 1 °C integer resolution: always accept +-2 K steps
    jump_confirm: int = 3          # a jumped value is accepted if repeated this many consecutive reads
    limit_object: str = '0x6072'   # or '0x6073'
    nominal_permille: int = 1000   # per drive default (commissioned value), per-mille of 0x6075 [bench-verify]
    sit_timeout_s: float = 3.0     # MO=0 even if the sit-done flag never comes

    @classmethod
    def from_controller_config(cls, path=CFG_PATH):
        try:
            d = json.load(open(path)).get('drive_thermal_derate', {})
        except Exception:
            d = {}
        fields = cls.__dataclass_fields__
        return cls(**{k: v for k, v in d.items() if k in fields})

    @property
    def stale_s(self):
        return self.stale_s_sdo if self.temp_source == 'sdo' else self.stale_s_pdo


def curve(t, c: DerateConfig):
    """R-141 scale vs temperature (no latch)."""
    if t <= c.t_start:
        return 1.0
    if t >= c.t_half:
        return c.scale_min
    return 1.0 - (1.0 - c.scale_min) * (t - c.t_start) / (c.t_half - c.t_start)


MF_OVERTEMP = 0xD000
EMCY_OVERTEMP = 0x4310


class DriveIO:
    """Interface the EtherCAT master implements. No save (SV) and no CL/PL writes exist on purpose."""
    def read_temp(self, drive):           # -> float °C or None (missing / not refreshed this cycle)
        raise NotImplementedError
    def write_limit(self, drive, permille):  # 0x6072 (or 0x6073) in the cyclic RxPDO
        raise NotImplementedError
    def set_mo(self, drive, on):           # controlword enable / disable operation
        raise NotImplementedError
    def read_fault(self, drive):           # -> (mf:int, emcy:int) or (0, 0)
        return 0, 0


class _DriveState:
    def __init__(self, name, c: DerateConfig, nominal_permille):
        self.name, self.c, self.nominal = name, c, int(nominal_permille)
        self.t = None          # last accepted temperature
        self.age = math.inf    # seconds since last accepted read
        self.pending = None    # candidate jumped value
        self.pending_n = 0
        self.fault = False

    def update(self, raw, dt):
        c = self.c
        self.age += dt
        if raw is None or not math.isfinite(raw) or raw < -40 or raw > 150:
            return
        if self.t is None:
            self.t, self.age = float(raw), 0.0
            return
        allowed = max(c.jump_floor_K, c.max_rate_K_s * self.age)
        if abs(raw - self.t) <= allowed:
            self.t, self.age, self.pending, self.pending_n = float(raw), 0.0, None, 0
            return
        # implausible step: accept only if it repeats (upward accepted faster is not assumed: symmetric)
        if self.pending is not None and abs(raw - self.pending) <= c.jump_floor_K:
            self.pending_n += 1
        else:
            self.pending, self.pending_n = float(raw), 1
        if self.pending_n >= c.jump_confirm:
            self.t, self.age, self.pending, self.pending_n = float(raw), 0.0, None, 0

    @property
    def stale(self):
        return self.t is None or self.age > self.c.stale_s

    def scale(self):
        s = curve(self.t, self.c) if self.t is not None else self.c.stale_scale
        return min(s, self.c.stale_scale) if self.stale else s


RUN, STOPPING, STOPPED = 'RUN', 'STOPPING', 'STOPPED'


class DriveDerateSupervisor:
    """One per robot. step() every control cycle.

    request_safe_sit(): called once when the stop latches (WBC/fall-mode path: safe posture or sit).
    sit_done(): set by the WBC when the robot is seated/safe; then MO=0 on every drive.
    """
    def __init__(self, drives, io: DriveIO, c: DerateConfig = None, nominal_permille=None,
                 request_safe_sit=None, tau_nominal=None):
        self.c = c or DerateConfig()
        self.io = io
        nominal_permille = nominal_permille or {}
        self.d = {n: _DriveState(n, self.c, nominal_permille.get(n, self.c.nominal_permille)) for n in drives}
        self.tau_nominal = dict(tau_nominal or {})   # joint torque at nominal limit (N·m) = Kt*ratio*I or contract
        self.state = RUN
        self.reason = ''
        self.request_safe_sit = request_safe_sit or (lambda reason: None)
        self._sit_done = False
        self._stop_t = 0.0
        self.last_written = {}

    # ---- WBC hooks
    def sit_done(self):
        self._sit_done = True

    def re_enable(self):
        """Explicit operator/supervisor re-enable. Only succeeds when every drive is fresh and < t_resume and no fault."""
        if self.state != STOPPED:
            return self.state == RUN
        if all((not s.stale) and s.t < self.c.t_resume and not s.fault for s in self.d.values()):
            for n in self.d:
                self.io.write_limit(n, self.d[n].nominal)   # restore nominal
                self.last_written[n] = self.d[n].nominal
                self.io.set_mo(n, True)
            self.state, self.reason, self._sit_done = RUN, '', False
            return True
        return False

    def _latch(self, reason):
        if self.state == RUN:
            self.state, self.reason, self._stop_t, self._sit_done = STOPPING, reason, 0.0, False
            self.request_safe_sit(reason)

    # ---- cycle
    def step(self, dt=None):
        dt = dt or 1.0 / self.c.loop_hz
        for n, s in self.d.items():
            s.update(self.io.read_temp(n), dt)
            mf, emcy = self.io.read_fault(n)
            # current fault input (not sticky here; the robot stop latch is sticky)
            s.fault = (mf & MF_OVERTEMP) == MF_OVERTEMP or emcy == EMCY_OVERTEMP
            if s.fault:
                self._latch(f'{n}: drive over-temperature fault (MF 0xD000/EMCY 0x4310)')
            elif s.t is not None and not s.stale and s.t >= self.c.t_stop:
                self._latch(f'{n}: {s.t:.0f} C >= {self.c.t_stop:.0f} C')
            elif s.stale and s.age > self.c.stale_stop_s:
                self._latch(f'{n}: no valid temperature for {s.age:.1f} s')
        if self.state == STOPPING:
            self._stop_t += dt
            if self._sit_done or self._stop_t >= self.c.sit_timeout_s:
                for n in self.d:
                    self.io.set_mo(n, False)
                self.state = STOPPED
        # limits are written every cycle (cyclic RxPDO), also while stopping (the sit runs derated)
        for n, s in self.d.items():
            pm = int(round(self.scale(n) * s.nominal))
            self.io.write_limit(n, pm)
            self.last_written[n] = pm
        return self.state

    def scale(self, drive):
        return self.d[drive].scale()

    def torque_limits(self):
        """Derated joint torque limits for the WBC (N·m): scale * tau_nominal (tau_nominal = Kt*ratio*I_nom)."""
        return {j: self.scale(j) * t for j, t in self.tau_nominal.items() if j in self.d}


def combine_min(*limit_sets):
    """Element-wise min of several {joint: N·m} limit dicts (drive derate, pick, carry, knee winding, contract).
    Joints missing from a set are unconstrained by that set."""
    out = {}
    for ls in limit_sets:
        for j, v in (ls or {}).items():
            out[j] = min(out.get(j, math.inf), float(v))
    return out


# ---- timing check (R-141 stop at 84 vs drive trip at 85)
def sit_timing_margin(dTdt_K_s, sit_s, latency_s=0.05, t_stop=84.0, t_trip=85.0):
    """Seconds left before the drive's own trip after the sit completes (positive = OK)."""
    return (t_trip - t_stop) / dTdt_K_s - (sit_s + latency_s)


def default_tau_nominal():
    """Joint torque at the commissioned (nominal) limit, N·m, keyed by joint name. Uses the CONTRACTS R1.2
    available peaks / MJCF ctrlranges already baked into modules/legs/rl/gains.npz (tau_lim). That equals
    Kt*ratio*I_nom only if the commissioned limit is set to the contract peak [EST until commissioning]."""
    import numpy as np
    g = np.load(os.path.join(HERE, '..', '..', 'legs', 'rl', 'gains.npz'))
    return {str(n): float(t) for n, t in zip(g['joint_names'].tolist(), g['tau_lim'])}
