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
    t_stop: float = 82.0           # R-146(a) INTERIM (21d1738): >= 82 C (R-142 had 83, R-141 84). NOT valid for G4.
    kneel_enabled: bool = False    # R-146(a): kneel/prone path kept in code but disabled; crouch -> HOLD_DERATED -> TUCK
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
    # R-145 (5f5bd1d) stop sequence
    crouch_s: float = 2.0          # measured derated crouch (2b38a45)
    crouch_timeout_s: float = 2.6  # guard; crouch_s normally ends CROUCH first
    kneel_timeout_s: float = 1.2   # no supported contact by then -> HOLD_DERATED [EST; sim kneel time + margin]
    confirm_s: float = 0.05        # contact + support must hold this long before MO=0
    support_speed: float = 0.10    # m/s CoM speed limit for 'supported'

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


RUN = 'RUN'
CROUCH = 'CROUCH'                        # R-145: 2.0 s derated crouch (WBC)
KNEEL = 'KNEEL'                          # controlled kneel to ground contact (fall-mode config, knee pads)
CONTACT_CONFIRMED = 'CONTACT_CONFIRMED'  # knee contact + CoM supported, held for confirm_s
MO_OFF = 'MO_OFF'                        # MO=0 on all drives (only reachable from CONTACT_CONFIRMED)
HOLD_DERATED = 'HOLD_DERATED'            # fallback: kneel not possible -> hold derated torque until a drive trips
TUCK = 'TUCK'                            # fallback after the trip: fall-mode tuck
STOP_STATES = (CROUCH, KNEEL, CONTACT_CONFIRMED, MO_OFF, HOLD_DERATED, TUCK)
# legacy names kept for callers of the R-141 version
STOPPING, STOPPED = CROUCH, MO_OFF


class UnsupportedMoOff(RuntimeError):
    """MO=0 requested without knee contact + CoM support (R-145 prohibits MO=0 from an unsupported crouch)."""


class DriveDerateSupervisor:
    """One per robot. step() every control cycle.

    R-145 stop sequence (whole robot, latched):
      RUN --(any drive reading >= t_stop, drive over-temp fault, or no temperature for stale_stop_s)--> CROUCH
      CROUCH: request_safe_sit(reason); WBC runs the derated crouch (crouch_s, 2.0 s). crouch_done() or crouch_s
              elapsed -> KNEEL (request_kneel()). crouch_timeout_s without progress -> HOLD_DERATED.
      KNEEL: WBC/fall-mode kneels to the knee pads. set_support(knee_contact, com_supported, com_speed) each cycle.
             all flags true (contact, CoM inside knee+toe polygon, speed < support_speed) -> CONTACT_CONFIRMED.
             kneel_timeout_s, or kneel_impossible() -> HOLD_DERATED.
             'supported' also needs torque_ok: static holding torque < friction hold at every joint (D94).
      CONTACT_CONFIRMED: flags must hold for confirm_s, then MO=0 on all drives -> MO_OFF. Flags lost -> KNEEL.
      HOLD_DERATED: keep MO on at the derated limit (no brake/backdrive hold assumed); first drive trip
                    (MF 0xD000/EMCY 0x4310) -> TUCK (request_tuck()). MO is never commanded off here.
      MO_OFF: re_enable() when every drive < t_resume.
    MO=0 is sent only by _mo_off(), which raises UnsupportedMoOff unless the support flags are confirmed.
    """
    def __init__(self, drives, io: DriveIO, c: DerateConfig = None, nominal_permille=None,
                 request_safe_sit=None, tau_nominal=None, request_kneel=None, request_tuck=None):
        self.c = c or DerateConfig()
        self.io = io
        nominal_permille = nominal_permille or {}
        self.d = {n: _DriveState(n, self.c, nominal_permille.get(n, self.c.nominal_permille)) for n in drives}
        self.tau_nominal = dict(tau_nominal or {})   # joint torque at nominal limit (N·m) = Kt*ratio*I or contract
        self.state = RUN
        self.reason = ''
        self.request_safe_sit = request_safe_sit or (lambda reason: None)
        self.request_kneel = request_kneel or (lambda: None)
        self.request_tuck = request_tuck or (lambda reason: None)
        self.on_fall = lambda reason: None   # fall-event logger hook (Test fall budget)
        self.fall_events = []
        self._reset_seq()
        self.last_written = {}
        self.log = []    # (t, state) transitions

    def _reset_seq(self):
        self._t_state = 0.0
        self._t = getattr(self, '_t', 0.0)
        self._crouch_done = False
        self._kneel_impossible = False
        self._support = (False, False, math.inf, False)
        self._confirm_t = 0.0

    # ---- WBC / fall-mode hooks
    def crouch_done(self):
        self._crouch_done = True

    def sit_done(self):          # R-141 name: now only means the crouch finished
        self.crouch_done()

    def kneel_impossible(self):
        self._kneel_impossible = True

    def check_ankles(self, ankles):
        """ankles: {side: (pitch_rad, roll_rad)} measured. D96 coupling violated while kneeling -> kneel_impossible()
        (-> HOLD_DERATED); in any state the violation is logged. Returns True if all ankles are inside the limit."""
        bad = [sd for sd, (p, r) in ankles.items() if not ankle_limit_ok(p, r)]
        if bad:
            self.log.append((self._t, f'ankle_limit {",".join(bad)}'))
            if self.state == KNEEL:
                self.kneel_impossible()
        return not bad

    def set_support(self, knee_contact, com_supported, com_speed, torque_ok=False):
        """torque_ok: static holding torque of the settled pose is below the friction hold at EVERY joint
        (Actuators D94, 7d22c91: no brakes, roller screws backdrive, hold ~7-9 N·m). Use static_hold_ok()."""
        self._support = (bool(knee_contact), bool(com_supported), float(com_speed), bool(torque_ok))

    def supported(self):
        k, c, v, tq = self._support
        return k and c and v < self.c.support_speed and tq

    def _go(self, state):
        self.state, self._t_state = state, 0.0
        self.log.append((round(self._t, 4), state))

    def _mo_off(self):
        if not (self.state == CONTACT_CONFIRMED and self.supported() and self._confirm_t >= self.c.confirm_s):
            raise UnsupportedMoOff(f'MO=0 refused in {self.state}: support {self._support}')
        for n in self.d:
            self.io.set_mo(n, False)
        self._go(MO_OFF)

    def re_enable(self):
        """Explicit operator/supervisor re-enable. Only from MO_OFF, every drive fresh, < t_resume, no fault."""
        if self.state != MO_OFF:
            return self.state == RUN
        if all((not s.stale) and s.t < self.c.t_resume and not s.fault for s in self.d.values()):
            for n in self.d:
                self.io.write_limit(n, self.d[n].nominal)   # restore nominal
                self.last_written[n] = self.d[n].nominal
                self.io.set_mo(n, True)
            self.reason = ''
            self._reset_seq()
            self._go(RUN)
            return True
        return False

    def _latch(self, reason):
        if self.state == RUN:
            self.reason = reason
            self._reset_seq()
            self._go(CROUCH)
            self.request_safe_sit(reason)

    # ---- cycle
    def step(self, dt=None):
        dt = dt or 1.0 / self.c.loop_hz
        self._t += dt
        any_fault = False
        for n, s in self.d.items():
            s.update(self.io.read_temp(n), dt)
            mf, emcy = self.io.read_fault(n)
            # current fault input (not sticky here; the robot stop latch is sticky)
            s.fault = (mf & MF_OVERTEMP) == MF_OVERTEMP or emcy == EMCY_OVERTEMP
            any_fault |= s.fault
            if s.fault:
                self._latch(f'{n}: drive over-temperature fault (MF 0xD000/EMCY 0x4310)')
            elif s.t is not None and not s.stale and s.t >= self.c.t_stop:
                self._latch(f'{n}: {s.t:.0f} C >= {self.c.t_stop:.0f} C')
            elif s.stale and s.age > self.c.stale_stop_s:
                self._latch(f'{n}: no valid temperature for {s.age:.1f} s')
        self._t_state += dt
        st = self.state
        if st == CROUCH:
            if self._kneel_impossible:
                self._go(HOLD_DERATED)
            elif self._crouch_done or self._t_state >= self.c.crouch_s:
                if self.c.kneel_enabled:
                    self._go(KNEEL); self.request_kneel()
                else:                      # R-146(a) interim: hold the derated crouch until a drive trips
                    self._go(HOLD_DERATED)
            elif self._t_state >= self.c.crouch_timeout_s:
                self._go(HOLD_DERATED)
        elif st == KNEEL:
            if self._kneel_impossible or self._t_state >= self.c.kneel_timeout_s:
                self._go(HOLD_DERATED)
            elif self.supported():
                self._go(CONTACT_CONFIRMED); self._confirm_t = 0.0
        elif st == CONTACT_CONFIRMED:
            if not self.supported():
                self._go(KNEEL)
            else:
                self._confirm_t += dt
                if self._confirm_t >= self.c.confirm_s:
                    self._mo_off()
        elif st == HOLD_DERATED:
            if any_fault:
                self._go(TUCK); self.request_tuck(self.reason)
                # R-146(a): the trip-then-tuck end is a FALL event (Test logs it against the fall budget)
                self.fall_events.append((round(self._t, 4), 'R-146 interim: drive trip -> TUCK', self.reason))
                self.on_fall(self.reason)
        # limits are written every cycle (cyclic RxPDO), also during the whole stop sequence
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


# Actuators D94 (7d22c91, results/SAFE_SIT_HOLDING.md): friction hold at the joint with MO=0, N·m [EST there].
# Hip pitch 7-9 (7 used), knee 7, ankle 8. Every other joint: 7 (the conservative value asked for).
FRICTION_HOLD_NM = {'hip_pitch': 7.0, 'knee': 7.0, 'ankle_pitch': 8.0}
FRICTION_HOLD_DEFAULT_NM = 7.0


def friction_hold(joint):
    for k, v in FRICTION_HOLD_NM.items():
        if joint.endswith(k):
            return v
    return FRICTION_HOLD_DEFAULT_NM


def static_hold_ok(tau_static, margin=1.0):
    """tau_static: {joint: N·m} static holding torque of the settled end pose (from the model).
    True only if |tau| < margin * friction hold at every joint. Empty input -> False."""
    if not tau_static:
        return False
    return all(abs(t) < margin * friction_hold(j) for j, t in tau_static.items())


def combine_min(*limit_sets):
    """Element-wise min of several {joint: N·m} limit dicts (drive derate, pick, carry, knee winding, contract).
    Joints missing from a set are unconstrained by that set."""
    out = {}
    for ls in limit_sets:
        for j, v in (ls or {}).items():
            out[j] = min(out.get(j, math.inf), float(v))
    return out


# ---- timing check (R-141 stop at 84 vs drive trip at 85)
def sit_timing_margin(dTdt_K_s, sit_s, latency_s=0.05, t_stop=83.0, t_trip=85.0):
    """Seconds left before the drive's own trip after the sit completes (positive = OK)."""
    return (t_trip - t_stop) / dTdt_K_s - (sit_s + latency_s)


def default_tau_nominal():
    """Joint torque at the commissioned (nominal) limit, N·m, keyed by joint name. Uses the CONTRACTS R1.2
    available peaks / MJCF ctrlranges already baked into modules/legs/rl/gains.npz (tau_lim). That equals
    Kt*ratio*I_nom only if the commissioned limit is set to the contract peak [EST until commissioning]."""
    import numpy as np
    g = np.load(os.path.join(HERE, '..', '..', 'legs', 'rl', 'gains.npz'))
    return {str(n): float(t) for n, t in zip(g['joint_names'].tolist(), g['tau_lim'])}


# ---- D96 / P-157 ankle dorsiflexion soft limit with roll coupling (Actuators da63827, Legs a676435)
ANKLE_PITCH_SOFT_MIN = math.radians(-52.5)    # -0.916 rad: controlled limit at any roll (q<0 = dorsiflexion)
ANKLE_PITCH_STOP = -0.960                     # rad (-55.0 deg): mechanical end stop (P-157)
ANKLE_ROLL_COUPLE = math.radians(10.0)        # past -52.5 deg only with |roll| <= 10 deg (screw toggle -58.6 at roll 18)


def ankle_pitch_min(roll_rad):
    """Lowest allowed ankle pitch command (rad) at this ankle roll. The end stop is never commanded."""
    return ANKLE_PITCH_STOP + 0.005 if abs(roll_rad) <= ANKLE_ROLL_COUPLE else ANKLE_PITCH_SOFT_MIN


def ankle_limit_ok(pitch_rad, roll_rad):
    return pitch_rad >= ankle_pitch_min(roll_rad) - 1e-9


def clamp_ankle(pitch_cmd, roll_rad):
    return max(float(pitch_cmd), ankle_pitch_min(roll_rad))


class ProneLowerGuard:
    """T&R R-146 prone check (fef9348, R146_PRONE_LANDING.md L1) controller requirements for the prone lower:
      - chest-pad contact speed <= 0.1 m/s: speed_limit(gap) caps the commanded chest descent speed so that it is
        <= v_contact inside the approach zone (gap <= zone_m) and is ramped from v_far above it.
      - peak chest-pad force <= 8.8 kN: observe() records the peak and flags any exceedance (logged, test input).
    """
    def __init__(self, v_contact=0.10, v_far=0.40, zone_m=0.05, f_max_N=8800.0):
        self.v_contact, self.v_far, self.zone_m, self.f_max = v_contact, v_far, zone_m, f_max_N
        self.peak_force = 0.0
        self.contact_speed = None
        self.violations = []

    def speed_limit(self, gap_m):
        """Max allowed chest descent speed (m/s, >= 0) at a chest-pad-to-floor gap (m)."""
        if gap_m <= self.zone_m:
            return self.v_contact
        # linear ramp to v_far over the next 0.15 m
        return min(self.v_far, self.v_contact + (self.v_far - self.v_contact) * (gap_m - self.zone_m) / 0.15)

    def clamp(self, gap_m, v_down_cmd):
        """Clamp a commanded downward chest speed (positive = down)."""
        return min(float(v_down_cmd), self.speed_limit(gap_m))

    def observe(self, t, in_contact, v_down, force_N):
        if in_contact and self.contact_speed is None:
            self.contact_speed = float(v_down)
            if v_down > self.v_contact + 1e-9:
                self.violations.append((t, 'contact_speed', float(v_down)))
        self.peak_force = max(self.peak_force, float(force_N))
        if force_N > self.f_max:
            self.violations.append((t, 'chest_force', float(force_N)))

    @property
    def ok(self):
        return not self.violations
