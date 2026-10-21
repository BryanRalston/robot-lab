"""J10 sim/v3 hardware update (RL Controls, 2026-10-20). Idempotent: refuses to run twice.

Applies, on top of arm_inertials_r3 (a618ce0) and Torso sim_torso_body_r1 (ad9878e), which are already in:
 1. Forearm 287 (Arms R8b f9eba88): hand body +17 mm; +0.0214 kg/side at mid-extension (z -0.2585 in forearm frame).
 2. Knee D69 rev B fins as built: +0.0932 kg/knee (actuators DECISIONS 'D69 rev B fins as built'), lumped at the thigh
    COM [EST location]. Motors unchanged (2x 07613D), so the armature is unchanged.
 3. Sole: fallback SP 67A 6 mm frame (TARGETS 2026-10-20 10:17 PM; RULINGS R-104 fallback), 0.098 kg/foot.
    Foot box 18 -> 24 mm, contact on the pad face (single box geom, bottom 6 mm lower). E ~4.8 MPa (Gent, 67A, SOLE_PAD_SPEC):
    k = E*A/t >> MuJoCo default contact stiffness, so the default solref is kept [EST].
 4. Chest pad (R-079/R-088): 0.091 kg pad+land at (0.100, 0, 0.220) torso frame (R1_ARCHITECTURE 25.1), 98x98x88 geom;
    PC plate net +0.013 [EST, R1_ARCHITECTURE 25.1] at x 0.150.
 5. Neck XM430 4.1 N·m already in (eac9a46 / gen). Head masses unchanged.
"""
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
XML = os.path.join(ROOT, 'sim', 'v3', 'humanoid_v3.xml')
s = open(XML, encoding='utf-8').read()
if 'chest_pad' in s:
    sys.exit('already applied')


def add_mass(text, body, dm, p):
    """Merge a point mass dm at p (body frame) into the body's <inertial>."""
    pat = re.compile(r'(<body name="%s"[^>]*>(?:<joint[^>]*/>)*)<inertial pos="([^"]+)" mass="([^"]+)" (fullinertia|diaginertia)="([^"]+)"/>' % body)
    m = pat.search(text)
    assert m, body
    import numpy as np
    c = np.array([float(v) for v in m.group(2).split()]); M = float(m.group(3)); I = [float(v) for v in m.group(5).split()]
    p = np.array(p, float)
    if m.group(4) == 'diaginertia':
        I = I + [0.0, 0.0, 0.0]
    J = np.array([[I[0], I[3], I[4]], [I[3], I[1], I[5]], [I[4], I[5], I[2]]])
    Mn = M + dm; cn = (M * c + dm * p) / Mn

    def shift(m_, r):
        return m_ * (np.dot(r, r) * np.eye(3) - np.outer(r, r))
    Jn = J + shift(M, c - cn) + shift(dm, p - cn)
    new = '<inertial pos="%.4f %.4f %.4f" mass="%.4f" fullinertia="%.6f %.6f %.6f %.6f %.6f %.6f"/>' % (
        *cn, Mn, Jn[0, 0], Jn[1, 1], Jn[2, 2], Jn[0, 1], Jn[0, 2], Jn[1, 2])
    return text[:m.start()] + m.group(1) + new + text[m.end():]


def inertial_pos(text, body):
    m = re.search(r'<body name="%s"[^>]*>(?:<joint[^>]*/>)*<inertial pos="([^"]+)"' % body, text)
    return [float(v) for v in m.group(1).split()]


for side in 'LR':
    s = add_mass(s, f'{side}_forearm', 0.0214, (0, 0, -0.2585))
    s = s.replace(f'<body name="{side}_hand" pos="0.000 0.000 -0.250">', f'<body name="{side}_hand" pos="0.000 0.000 -0.267">')
    s = add_mass(s, f'{side}_thigh', 0.0932, inertial_pos(s, f'{side}_thigh'))
    s = add_mass(s, f'{side}_foot', 0.098, (0.060, 0.0, -0.083))
for lr in 'lr':
    s = s.replace(f'<geom name="{lr}_forearm" type="capsule" fromto="0 0 -0.04 0 0 -0.240"',
                  f'<geom name="{lr}_forearm" type="capsule" fromto="0 0 -0.04 0 0 -0.257"')
    old = f'<geom name="{lr}_foot" type="box" pos="0.060 0 -0.071" size="0.120 0.05 0.009" friction="1.0"/>'
    assert old in s, old
    s = s.replace(old, f'<geom name="{lr}_foot" type="box" pos="0.060 0 -0.074" size="0.120 0.05 0.012" friction="1.0"/>')
s = add_mass(s, 'torso', 0.091, (0.100, 0.0, 0.220))
s = add_mass(s, 'torso', 0.013, (0.150, 0.0, 0.220))
tg = '<geom name="torso" type="box" pos="0 0 0.180" size="0.11 0.17 0.130"/>'
assert tg in s
s = s.replace(tg, tg + '<geom name="chest_pad" type="box" pos="0.100 0 0.220" size="0.044 0.049 0.049" mass="0"/>')
open(XML, 'w', encoding='utf-8').write(s)
import mujoco
print('mass', round(float(mujoco.MjModel.from_xml_path(XML).body_mass.sum()), 4))
