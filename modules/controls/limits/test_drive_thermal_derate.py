"""R-141 drive derate: ramped temperature traces through the curve, latch, hysteresis, stale reads, min-combination."""
import math
import pytest
from drive_thermal_derate import (DerateConfig, DriveIO, DriveDerateSupervisor, curve, combine_min,
                                  sit_timing_margin, static_hold_ok, friction_hold, RUN, STOPPING, STOPPED, MF_OVERTEMP, EMCY_OVERTEMP,
                                  CROUCH, KNEEL, CONTACT_CONFIRMED, MO_OFF, HOLD_DERATED, TUCK, UnsupportedMoOff)

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
    kw.setdefault('kneel_enabled', True)   # kneel-path tests; the R-146 interim default is tested separately
    kw.setdefault('t_stop', 83.0)
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


def run_n(sup, n):
    for _ in range(n):
        sup.step(DT)


def to_contact(io, sup):
    """latch -> crouch done -> kneel -> supported contact -> MO_OFF"""
    ramp(io, sup, 'l_knee', 70, 83.2, rate_K_s=3.0)
    sup.crouch_done(); sup.step(DT)
    assert sup.state == KNEEL
    sup.set_support(True, True, 0.02, True)
    run_n(sup, 1)
    assert sup.state == CONTACT_CONFIRMED
    run_n(sup, 60)
    assert sup.state == MO_OFF


def test_stop_latch_whole_robot_crouch_kneel_contact_mo_off():
    io, sup, sits = make()
    kneels = []
    sup.request_kneel = lambda: kneels.append(1)
    ramp(io, sup, 'l_knee', 70, 82.9, rate_K_s=3.0)
    assert sup.state == RUN
    ramp(io, sup, 'l_knee', 82, 83.2, rate_K_s=3.0)
    assert sup.state == CROUCH and len(sits) == 1 and 'l_knee' in sits[0]
    assert all(io.mo.values())
    assert io.limit['l_knee'] == 500 and io.limit['r_knee'] == 1000
    sup.crouch_done(); sup.step(DT)
    assert sup.state == KNEEL and kneels == [1] and all(io.mo.values())
    sup.set_support(True, True, 0.02, True); run_n(sup, 60)
    assert sup.state == MO_OFF and not any(io.mo.values())   # every drive off
    assert [s for _, s in sup.log] == [CROUCH, KNEEL, CONTACT_CONFIRMED, MO_OFF]


def test_crouch_ends_on_crouch_s_without_flag():
    io, sup, _ = make()
    ramp(io, sup, 'l_knee', 70, 83.2, rate_K_s=5.0)
    run_n(sup, int(sup.c.crouch_s / DT) + 2)
    assert sup.state == KNEEL and all(io.mo.values())


def test_guard_mo_never_off_without_contact_and_support():
    """MO=0 must never be written unless knee contact AND CoM support AND low speed were confirmed."""
    for flags in [(False, False, 0.0, True), (True, False, 0.0, True), (False, True, 0.0, True), (True, True, 0.5, True),
                  (True, True, 0.0, False), (True, True, 0.0)]:   # torque above friction / flag missing
        io, sup, _ = make()
        ramp(io, sup, 'l_knee', 70, 83.2, rate_K_s=5.0)
        sup.crouch_done()
        sup.set_support(*flags)
        run_n(sup, 10000)                      # well past every timeout
        assert all(io.mo.values()), flags
        assert sup.state == HOLD_DERATED
    # direct call is refused too
    io, sup, _ = make()
    ramp(io, sup, 'l_knee', 70, 83.2, rate_K_s=5.0)
    with pytest.raises(UnsupportedMoOff):
        sup._mo_off()
    assert all(io.mo.values())


def test_contact_flicker_returns_to_kneel():
    io, sup, _ = make()
    ramp(io, sup, 'l_knee', 70, 83.2, rate_K_s=5.0)
    sup.crouch_done(); sup.step(DT)
    sup.set_support(True, True, 0.02, True); run_n(sup, 20)       # 20 ms < confirm_s 50 ms
    assert sup.state == CONTACT_CONFIRMED and all(io.mo.values())
    sup.set_support(True, False, 0.02, True); sup.step(DT)
    assert sup.state == KNEEL and all(io.mo.values())


def test_kneel_timeout_holds_derated_then_tuck_on_trip():
    io, sup, _ = make()
    tucks = []
    sup.request_tuck = tucks.append
    ramp(io, sup, 'l_knee', 70, 83.2, rate_K_s=5.0)
    sup.crouch_done(); sup.step(DT)
    run_n(sup, int(sup.c.kneel_timeout_s / DT) + 2)
    assert sup.state == HOLD_DERATED and all(io.mo.values()) and io.limit['l_knee'] == 500
    run_n(sup, 2000)
    assert sup.state == HOLD_DERATED and not tucks
    io.fault['l_knee'] = (MF_OVERTEMP, EMCY_OVERTEMP); sup.step(DT)
    assert sup.state == TUCK and len(tucks) == 1 and all(io.mo.values())   # tuck still uses torque


def test_kneel_impossible_and_crouch_timeout():
    io, sup, _ = make()
    ramp(io, sup, 'l_knee', 70, 83.2, rate_K_s=5.0)
    sup.kneel_impossible(); sup.step(DT)
    assert sup.state == HOLD_DERATED
    io, sup, _ = make(crouch_s=5.0, crouch_timeout_s=1.0)
    ramp(io, sup, 'l_knee', 70, 83.2, rate_K_s=5.0)
    run_n(sup, 1002)
    assert sup.state == HOLD_DERATED and all(io.mo.values())


def test_hysteresis_and_explicit_reenable():
    io, sup, _ = make()
    to_contact(io, sup)
    ramp(io, sup, 'l_knee', 84, 79, rate_K_s=3.0)
    assert sup.re_enable() is False and sup.state == MO_OFF      # 79 >= 78
    ramp(io, sup, 'l_knee', 79, 77, rate_K_s=3.0)
    run_n(sup, 5)
    assert sup.state == MO_OFF                                   # no auto-resume
    assert sup.re_enable() is True and sup.state == RUN
    assert all(io.mo.values()) and io.limit['l_knee'] == 1000    # nominal restored on re-enable
    sup.step(DT)
    assert io.limit['l_knee'] == round(curve(77, sup.c) * 1000)


def test_drive_fault_latches_stop():
    io, sup, sits = make()
    sup.step(DT)
    io.fault['r_knee'] = (MF_OVERTEMP, EMCY_OVERTEMP)
    sup.step(DT)
    assert sup.state == CROUCH and 'fault' in sits[0]


def test_stale_reads_failsafe_then_stop():
    io, sup, sits = make(stale_stop_s=1.0)
    sup.step(DT)
    io.temp['l_knee'] = None
    for _ in range(19): sup.step(DT)
    assert sup.scale('l_knee') == 1.0            # within 20 ms
    for _ in range(5): sup.step(DT)
    assert sup.scale('l_knee') == 0.5 and sup.state == RUN    # fail-safe derate
    for _ in range(1000): sup.step(DT)
    assert sup.state == CROUCH and 'no valid temperature' in sits[0]


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
    assert sup.state == CROUCH


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
    assert DerateConfig().t_stop == 82.0                # R-146(a) interim
    assert sit_timing_margin(0.3, 1.2) > 1.5          # plate slope (430684c): 3.3 s for 1 K
    assert sit_timing_margin(1.19, 1.2, t_stop=84.0) < 0   # drive-only bound, 1 K worst-case truncated band
    assert sit_timing_margin(1.19, 1.2) > 0                # 2 K nominal band at 83


def test_static_hold_flag_vs_d94_friction():
    assert friction_hold('l_knee') == 7.0 and friction_hold('r_ankle_pitch') == 8.0 and friction_hold('waist_pitch') == 7.0
    assert static_hold_ok({'l_knee': 3.0, 'l_hip_pitch': -6.9, 'l_ankle_pitch': 7.9})
    assert not static_hold_ok({'l_knee': 64.4})            # D94 crouch knee: must never allow MO=0
    assert not static_hold_ok({'l_knee': 3.0, 'waist_pitch': 7.5})
    assert not static_hold_ok({})


def test_guard_torque_flag_blocks_mo_off_in_supported_contact():
    io, sup, _ = make()
    ramp(io, sup, 'l_knee', 70, 83.2, rate_K_s=5.0)
    sup.crouch_done(); sup.step(DT)
    sup.set_support(True, True, 0.0, static_hold_ok({'l_knee': 20.0}))
    run_n(sup, 3000)
    assert all(io.mo.values()) and sup.state == HOLD_DERATED


def test_r146_interim_defaults_crouch_hold_then_tuck_logged_as_fall():
    c = DerateConfig()
    assert c.t_stop == 82.0 and c.kneel_enabled is False
    io = FakeIO(('l_knee', 'r_knee')); tucks = []; falls = []
    sup = DriveDerateSupervisor(('l_knee', 'r_knee'), io, c)
    sup.request_tuck = tucks.append; sup.on_fall = falls.append
    ramp(io, sup, 'l_knee', 70, 81.9, rate_K_s=3.0)
    assert sup.state == RUN
    ramp(io, sup, 'l_knee', 81, 82.2, rate_K_s=3.0)
    assert sup.state == CROUCH
    sup.set_support(True, True, 0.0, True)          # even with all flags, the interim never kneels or turns MO off
    run_n(sup, int(c.crouch_s / DT) + 5)
    assert sup.state == HOLD_DERATED and all(io.mo.values()) and io.limit['l_knee'] == 500
    run_n(sup, 3000)
    assert sup.state == HOLD_DERATED
    io.fault['l_knee'] = (MF_OVERTEMP, EMCY_OVERTEMP); sup.step(DT)
    assert sup.state == TUCK and len(tucks) == 1 and len(falls) == 1 and len(sup.fall_events) == 1
    assert all(io.mo.values())
    assert [s for _, s in sup.log] == [CROUCH, HOLD_DERATED, TUCK]


def test_prone_lower_guard_speed_and_force():
    from drive_thermal_derate import ProneLowerGuard
    g = ProneLowerGuard()
    assert g.speed_limit(0.0) == 0.10 and g.speed_limit(0.05) == 0.10
    assert g.speed_limit(0.5) == 0.40 and 0.10 < g.speed_limit(0.12) < 0.40
    assert g.clamp(0.01, 0.6) == 0.10 and g.clamp(0.3, 0.05) == 0.05
    # simulated lower: commanded 0.5 m/s, clamped each step -> contact at <= 0.1 m/s
    gap, dt = 0.4, 0.001
    while gap > 0:
        v = g.clamp(gap, 0.5); gap -= v * dt
    g.observe(1.0, True, v, 4000.0)
    assert v <= 0.10 + 1e-9 and g.ok and g.peak_force == 4000.0
    g.observe(1.1, True, 0.0, 9000.0)          # 9.0 kN > 8.8 kN
    assert not g.ok and g.violations[-1][1] == 'chest_force'
    g2 = ProneLowerGuard(); g2.observe(0.5, True, 0.3, 100.0)
    assert not g2.ok and g2.violations[0][1] == 'contact_speed'


def test_safe_stop_zmp_k_scoped_to_kneel_mode():
    import json, os
    here = os.path.dirname(os.path.abspath(__file__))
    c = json.load(open(os.path.join(here, '..', 'controller_config.json')))['drive_thermal_derate']
    assert c['safe_stop_zmp_k'] == [40.0, 12.0]
    src = open(os.path.join(here, 'kneel_prone_wbc.py')).read()
    assert 'ZMP_K = (12.0, 7.0)' in src


def test_chest_lower_wbc_contact_speed_nominal():
    import chest_lower_wbc as C
    r = C.run()
    assert r['chest_contact_speed_mps'] is not None and r['chest_contact_speed_mps'] <= 0.10
    assert r['peak_chest_N'] <= 8800 and r['t_d94_flag_mo0_s'] is not None
    assert r['peak_tau_Nm']['elbow'] <= 38.0 + 1e-6
