import os, sys, numpy as np; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import carry_limit as C, pick_limit as P
th = C.KneeThermal(); th.Tw, th.Th = 89.4, 75.4                    # hot start (64.4 hold steady, h 8)
lim = C.CarryLimiter(th, 1.1); r = lim.remaining() / C.MARGIN
assert 480 < r < 590, r                                            # profile sim: 531 s to 120 C
assert C.CarryLimiter(C.KneeThermal(), 1.0).remaining() / C.MARGIN > 2000   # cold x1.0: 2380 s
assert C.CarryLimiter(C.KneeThermal(h=12.0), 1.0).remaining() == np.inf     # h 12 x1.0 continuous
g = C.CarryGovernor(C.KneeThermal(Tw=89.4, Th=75.4)); assert C.R081Rule is C.R096Rule
assert abs(g.rule.remaining() - 300) < 1e-6 and g.remaining() <= 300
for _ in range(3000): g.step(84.4, 0.1, 0.0, True)               # 300 s bout (walking with load)
assert g.rule.remaining() < 1e-6
for _ in range(300): g.step(0.0, 0.1, 0.0, False)                 # 30 s break: bout not reset
assert g.rule.remaining() < 1e-6
for _ in range(300): g.step(0.0, 0.1, 0.0, False)                 # 60 s set down: bout reset, duty 420 s left
assert abs(g.rule.remaining() - 300) < 1
r = C.R096Rule()                                                   # standing holding the load counts as carry
for _ in range(3000): r.step(True, 0.1)
for _ in range(600): r.step(False, 0.1)
for _ in range(3000): r.step(True, 0.1)
for _ in range(600): r.step(False, 0.1)
assert abs(r.remaining() - 120) < 2, r.remaining()                # duty cap: 720 - 600
# shared state: hot carry blocks a pick that the table would allow
th2 = C.KneeThermal(Tw=118.0, Th=100.0); assert not th2.pick_ok(150, P.allowed_dwell(150))
assert C.KneeThermal(Tw=89.4, Th=75.4).pick_ok(150, P.allowed_dwell(150))
print('OK')
