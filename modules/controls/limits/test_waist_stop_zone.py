import math
from soft_limits import waist_stop_zone_tau as z, apply_waist_stop_zone as a
d = math.radians
def test_zone():
    assert z(d(58.5), 100.0) == 0.0 and z(d(58.5), -100.0) == -100.0
    assert z(d(-28.0), -50.0) == 0.0 and z(d(-28.0), 50.0) == 50.0
    assert z(d(56.0), 100.0) == 100.0 and z(d(-26.0), -50.0) == -50.0
def test_apply():
    t = [10.0, 80.0]; a(['knee', 'waist_pitch'], lambda n: d(59.0), t); assert t == [10.0, 0.0]
