from regen_guard import guard_tau, bms_open_permitted
def test_bus():
    t, l = guard_tau(['knee'], [-50.0], [3.0], 87.0); assert t == [0.0] and l
    t, _ = guard_tau(['knee'], [50.0], [3.0], 87.0); assert t == [50.0]
def test_waist_speed():
    t, _ = guard_tau(['waist_pitch'], [-80.0], [6.0], 60.0); assert t == [0.0]
    t, _ = guard_tau(['waist_pitch'], [-80.0], [5.0], 60.0); assert t == [-80.0]
def test_bms():
    assert not bms_open_permitted(False, [6.5]) and bms_open_permitted(True, [6.5]) and bms_open_permitted(False, [2.0])
