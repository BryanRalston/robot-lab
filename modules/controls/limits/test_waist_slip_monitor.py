from waist_slip_monitor import WaistSlipMonitor
def test_no_slip():
    m = WaistSlipMonitor(); m.update(0.1, 10.0); r = m.update(0.101, 10.1); assert not r['slipped']
def test_slip_and_breakaway():
    m = WaistSlipMonitor(); m.update(0.0, 0.0); r = m.update(0.7, 0.0)
    assert r['slipped'] and r['rehome_required'] and r['breakaway_check'] and r['energy_J'] > 100
    m.rehome(); assert not m.update(0.7, 0.0)['slipped']
