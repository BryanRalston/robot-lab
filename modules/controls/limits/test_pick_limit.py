import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pick_limit as L
assert L.allowed_dwell(60) == float('inf') and abs(L.allowed_dwell(150) - 10.5) < 0.01
x = L.PickLimiter(); n = 0
while x.limit() > L.TAU_ON: x.step(150, 0.01); n += 1
assert abs(n * 0.01 - 10.5) < 0.05, n
x.step(60, 0.01); assert x.limit() == L.TAU_ON and x.rest_left > 180
for _ in range(65800): x.step(60, 0.01)
assert x.limit() == 345.0; print('OK')
