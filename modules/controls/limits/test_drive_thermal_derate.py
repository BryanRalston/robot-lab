"""R-141 drive derate: ramped temperature traces through the curve, latch, hysteresis, stale reads, min-combination."""
import math
import pytest
from drive_thermal_derate import (DerateConfig, DriveIO, DriveDerateSupervisor, curve, combine_min,
                                  sit_timing_margin, RUN, STOPPING, STOPPED, MF_OVERTEMP, EMCY_OVERTEMP)

DT = 0.001


class FakeIO(DriveIO):
    def __init__(self, drives):
        self.temp = {d: 40.0 for d in drives}
        self.fault = {d: (0, 0) for d in drives}
        self.limit = {}
        self.mo = {d: True for d in drives}
        self.writes = []
    def read_temp(self, d): return self.temp[d]
    def write_limit(self, d, pm): self.limit[d] = pm; self.writes.append((d, pm))
    def set_mo(self, d, on): self.mo[d] = on
    def read_fault(self, d): return self.fault[d]


def make(drives=('l_knee', 'r_knee'), **kw):
    io = FakeIO(drives)
    sits = []
    sup = DriveDerateSupervisor(drives, io, DerateConfig(**kw), request_safe_sit=sits.append,
                                tau_nominal={'l_knee': 258.0, 'r_knee': 258.0})
    return io, sup, sits


def ramp(io, sup, drive, t0, t1, rate_K_s=0.3):
    t = t0
    n = int(abs(t1 - t0) / rate_K_s / DT)
    for i in range(n):
        t = t0 + (t1 - t0) * (i + 1) / n
        io.temp[drive] = float(int(t))          # integer °C like the drive object
        sup.step(DT)
    return t


def test_curve_points():
    c = DerateConfig()
    assert curve(70, c) == 1.0 and curve(75, c) == 1.0
    assert curve(78.5, c) == pytest.approx(0.75)
    assert curve(82, c) == 0.5 and curve(83.9, c) == 0.5


def test_ramp_derate_writes_permille_and_never_cl_pl():
    io, sup, _ = make()
    ramp(io, sup, 'l_knee', 70, 79, rate_K_s=3.0)
    assert sup.state == RUN
    assert io.limit['l_knee'] == round(curve(79, sup.c) * 1000)   # 0x6072 per-mille
    assert io.limit['r_knee'] == 1000
    assert not hasattr(io, 'save') and not hasattr(sup, 'write_cl')
    tl = sup.torque_limits()
    assert tl['l_knee'] == pytest.approx(258 * curve(79, sup.c)) and tl['r_knee'] == 258


def test_stop_latch_whole_robot_then_mo_off_after_sit():
    io, sup, sits = make()
    ramp(io, sup, 'l_knee', 70, 82.9, rate_K_s=3.0)
    assert sup.state == RUN
    ramp(io, sup, 'l_knee', 82, 83.2, rate_K_s=3.0)
    assert sup.state == STOPPING and len(sits) == 1 and 'l_knee' in sits[0]
    assert all(io.mo.values())                     # still powered during the sit
    assert io.limit['l_knee'] == 500 and io.limit['r_knee'] == 1000
    sup.sit_done(); sup.step(DT)
    assert sup.state == STOPPED and not any(io.mo.values())   # every drive off, not only the hot one


def test_sit_timeout_forces_mo_off():
    io, sup, _ = make(sit_timeout_s=0.5)
    ramp(io, sup, 'r_knee', 70, 84.5, rate_K_s=5.0)
    for _ in range(600):
        sup.step(DT)
    assert sup.state == STOPPED and not any(io.mo.values())


def test_hysteresis_and_explicit_reenable():
    io, sup, _ = make()
    ramp(io, sup, 'l_knee', 70, 84.5, rate_K_s=3.0)
    sup.sit_done(); sup.step(DT)
    ramp(io, sup, 'l_knee', 84, 79, rate_K_s=3.0)
    assert sup.re_enable() is False and sup.state == STOPPED      # 79 >= 78
    ramp(io, sup, 'l_knee', 79, 77, rate_K_s=3.0)
    for _ in range(5): sup.step(DT)
    assert sup.state == STOPPED                                    # no auto-resume
    assert sup.re_enable() is True and sup.state == RUN
    assert all(io.mo.values()) and io.limit['l_knee'] == 1000      # nominal restored on re-enable; next cycle applies the curve
    sup.step(DT)
    assert io.limit['l_knee'] == round(curve(77, sup.c) * 1000)


def test_drive_fault_latches_stop():
    io, sup, sits = make()
    sup.step(DT)
    io.fault['r_knee'] = (MF_OVERTEMP, EMCY_OVERTEMP)
    sup.step(DT)
    assert sup.state == STOPPING and 'fault' in sits[0]


def test_stale_reads_failsafe_then_stop():
    io, sup, sits = make(stale_stop_s=1.0)
    sup.step(DT)
    io.temp['l_knee'] = None
    for _ in range(19): sup.step(DT)
    assert sup.scale('l_knee') == 1.0            # within 20 ms
    for _ in range(5): sup.step(DT)
    assert sup.scale('l_knee') == 0.5 and sup.state == RUN    # fail-safe derate
    for _ in range(1000): sup.step(DT)
    assert sup.state == STOPPING and 'no valid temperature' in sits[0]


def test_sdo_rate_stale_window():
    io, sup, _ = make(temp_source='sdo')
    sup.step(DT)
    io.temp['l_knee'] = None
    for _ in range(400): sup.step(DT)            # 0.4 s without a 10 Hz sample is normal-ish
    assert sup.scale('l_knee') == 1.0
    for _ in range(200): sup.step(DT)
    assert sup.scale('l_knee') == 0.5


def test_sensor_jump_rejected_then_confirmed():
    io, sup, sits = make()
    sup.step(DT)                                  # 40 C accepted
    io.temp['l_knee'] = 95.0                      # single spike
    sup.step(DT)
    io.temp['l_knee'] = 40.0
    sup.step(DT)
    assert sup.state == RUN and sup.d['l_knee'].t == 40.0
    io.temp['l_knee'] = 95.0                      # persistent -> accepted after confirm -> stop
    for _ in range(3): sup.step(DT)
    assert sup.state == STOPPING


def test_min_combination():
    io, sup, _ = make()
    ramp(io, sup, 'l_knee', 70, 80, rate_K_s=3.0)
    drive = sup.torque_limits()
    pick = {'l_knee': 150.0}
    carry = {'r_knee': 120.0, 'l_knee': 300.0}
    winding = {'l_knee': 240.0, 'r_knee': 250.0}
    out = combine_min(drive, pick, carry, winding)
    assert out['l_knee'] == pytest.approx(min(258 * curve(80, sup.c), 150.0))
    assert out['r_knee'] == 120.0


def test_sit_timing_numbers():
    assert DerateConfig().t_stop == 83.0                # R-142
    assert sit_timing_margin(0.3, 1.2) > 1.5          # plate slope (430684c): 3.3 s for 1 K
    assert sit_timing_margin(1.19, 1.2) < 0           # drive-only adiabatic bound: flagged in DRIVE_DERATE.md
