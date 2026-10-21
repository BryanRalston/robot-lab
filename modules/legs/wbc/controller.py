"""1 kHz whole-body QP + 100 Hz LIPM footstep MPC for the v3 humanoid.

WBC decision variables are generalized accelerations and both foot wrenches.
Hard constraints: floating-base dynamics, R1.2 (and catalog) torque limits,
leg joint velocity limits, and the sole wrench cone from gait_lib (mu 0.8,
CoP inside the sole, |Mz| <= 0.05 Fz). Tasks: centroidal linear and angular
momentum, stance/swing foot pose (swing yaw and roll tracked explicitly),
pelvis attitude, and a joint-posture null space.

The plan path (use_plan) tracks a cruise slice of walk_1p2_r2. _plan_mpc closes
that loop at 100 Hz: sagittal and lateral DCM / capture-point foot placement,
a bounded step-time change (playback rate), and stance-yaw feedback through
yaw_off and the swing-foot yaw. --cruise scales the slice (rate = cruise / v_plan,
velocities * rate, feedforward * rate^2 about gravity). The trail foot is held
down and the landing is accepted early so double support is longer than the
slice's ~3% , and a vertical impedance task kills the touchdown bounce.

The FSM path below is the earlier LIPM stepper. Acceptance runs use the plan path.
"""
import os, sys
import numpy as np
import mujoco
from scipy import sparse as sp

_LEGS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _LEGS not in sys.path:
    sys.path.insert(0, _LEGS)
os.environ.setdefault('LEGS_MASS', '65')
os.environ.setdefault('LEGS_LIMITS', 'r1')
from gait_lib import load, Robot, LEG, G, SOLE, HEEL, TOE, HALFW, MU, LIM_R1

# avail ω column of results/r2/requirements.md (contract available speed)
VEL_LIM = {
    'hip_yaw': 6.13, 'hip_roll': 3.64, 'hip_pitch': 12.16,
    'knee': 16.03, 'ankle_pitch': 13.7, 'ankle_roll': 13.7,
}
FC = 0.06                 # sole-center x in the foot frame (matches the gait plan)
TH_TO = np.deg2rad(25.0) # toe-roll amplitude from walk_plan
YAW_MZ = 0.05            # |Mz| <= YAW_MZ * Fz, same couple limit as gait_lib
DS_FRAC = 0.15
# Realized double support on the open-loop slice was 3.3% (design DS_FRAC
# is 0.15). Hold the trailing foot after the plan lifts it, and start
# sharing load before the plan's touchdown. The playback clock is not
# what creates that overlap.
DS_PAD_LO = 0.120
import os as _os
GATE = _os.environ.get('WBC_GATE', '0') == '1'
GATE_TD = float(_os.environ.get('WBC_GATE_TD', '60'))      # N, touchdown detect
GATE_TO = float(_os.environ.get('WBC_GATE_TO', '0.12'))    # s, timeout fallback
GATE_RAMP = float(_os.environ.get('WBC_GATE_RAMP', '0.05'))  # s, load-transfer ramp
GATE_HOLD = float(_os.environ.get('WBC_GATE_HOLD', '0.85'))  # x mg held on stance while waiting
GATE_RATE = float(_os.environ.get('WBC_GATE_RATE', '0.5'))   # clock rate while waiting
DS_PAD_TD = 0.070
T_NOM = 0.42
PEL_Z = 1.02
HALF_W = 0.13


def _mj(s):
    return 10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5


def _mj_d(s):
    return 30 * s ** 2 - 60 * s ** 3 + 30 * s ** 4


def _mj_dd(s):
    return 60 * s - 180 * s ** 2 + 120 * s ** 3


def _bump(s):
    """Vertical swing hump, value / d/ds / d2/ds2. Apex is 1 at s=0.5 after *64."""
    g = s ** 3 - 3 * s ** 4 + 3 * s ** 5 - s ** 6
    gd = 3 * s ** 2 - 12 * s ** 3 + 15 * s ** 4 - 6 * s ** 5
    gdd = 6 * s - 36 * s ** 2 + 60 * s ** 3 - 30 * s ** 4
    return g, gd, gdd


def rpy_R(roll, pitch, yaw):
    cr, sr = np.cos(roll), np.sin(roll)
    cp, spn = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    Ry = np.array([[cp, 0, spn], [0, 1, 0], [-spn, 0, cp]])
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def rotvec(R_des, R):
    """World rotation vector taking R to R_des (small-angle)."""
    Re = R_des @ R.T
    return 0.5 * np.array([Re[2, 1] - Re[1, 2], Re[0, 2] - Re[2, 0], Re[1, 0] - Re[0, 1]])


def yaw_pitch_roll(R):
    pitch = np.arctan2(-R[2, 0], np.hypot(R[2, 1], R[2, 2]))
    yaw = np.arctan2(R[1, 0], R[0, 0])
    roll = np.arctan2(R[2, 1], R[2, 2])
    return roll, pitch, yaw


def ankle_from_toe(toe, yaw, pitch):
    return toe + rpy_R(0.0, pitch, yaw) @ np.array([-TOE, 0.0, SOLE])


def toe_from_ankle(ankle, yaw, pitch=0.0):
    return ankle + rpy_R(0.0, pitch, yaw) @ np.array([TOE, 0.0, -SOLE])


def sole_center(ankle_xy, yaw):
    return ankle_xy + np.array([FC * np.cos(yaw), FC * np.sin(yaw)])


def foot_cone(heel, toe, halfw, mu, yaw_frac):
    """G w >= 0, w = [Fx,Fy,Fz,Mx,My,Mz] at the ankle in the foot frame.

    Cop formulas (gait_lib): cop_x = (-My - SOLE Fx)/Fz, cop_y = (Mx - SOLE Fy)/Fz.
    """
    s = SOLE
    return np.array([
        [0, 0, 1, 0, 0, 0],
        [-s, 0, -heel, 0, -1, 0],
        [s, 0, toe, 0, 1, 0],
        [0, s, halfw, -1, 0, 0],
        [0, -s, halfw, 1, 0, 0],
        [-1, 0, mu, 0, 0, 0],
        [1, 0, mu, 0, 0, 0],
        [0, -1, mu, 0, 0, 0],
        [0, 1, mu, 0, 0, 0],
        [0, 0, yaw_frac, 0, 0, -1],
        [0, 0, yaw_frac, 0, 0, 1],
    ], float)


def _skew(v):
    return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


class WalkController:
    def __init__(self, m, carry=False, cruise=1.20, balance_s=0.16, shift_s=0.22):
        self.m = m
        self.carry = carry
        self.cruise = float(cruise)
        self.balance_s = float(balance_s)
        self.shift_s = float(shift_s)
        self.nv = m.nv
        self.nu = m.nu
        self.dt = m.opt.timestep
        self.robot = Robot(m)
        self.ds = mujoco.MjData(m)
        self.dg = mujoco.MjData(m)
        self.pelvis = m.body('pelvis').id
        self.torso = m.body('torso').id
        self.foot = {s: m.body(f'{s.upper()}_foot').id for s in 'lr'}
        self.foot_geom = {s: m.geom(f'{s}_foot').id for s in 'lr'}
        jid = m.actuator_trnid[:, 0]
        self.act_va = m.jnt_dofadr[jid].copy()
        self.act_qa = m.jnt_qposadr[jid].copy()
        self.act_name = [m.actuator(i).name for i in range(m.nu)]
        self.tau_max = m.actuator_ctrlrange[:, 1].copy()
        self.gear = m.actuator_gear[:, 0].copy()
        self.qa, self.va = {}, {}
        for side in 'lr':
            for j in LEG:
                jnt = m.joint(f'{side}_{j}')
                self.qa[side + j] = m.jnt_qposadr[jnt.id]
                self.va[side + j] = m.jnt_dofadr[jnt.id]
        self.jnt_id = {}
        self.qmin = np.full(m.nv, -1e6)
        self.qmax = np.full(m.nv, 1e6)
        self.vmax = np.full(m.nv, 1e4)
        for i in range(m.njnt):
            name = m.joint(i).name
            if not name or m.jnt_type[i] == mujoco.mjtJoint.mjJNT_FREE:
                continue
            dof = m.jnt_dofadr[i]
            self.jnt_id[name] = i
            lo, hi = m.jnt_range[i]
            self.qmin[dof] = lo + 0.02
            self.qmax[dof] = hi - 0.02
            self.vmax[dof] = 12.0
        for side in 'lr':
            for j, lim in VEL_LIM.items():
                self.vmax[self.va[side + j]] = lim
        self.arm_amp = 0.0 if carry else 0.35
        self.yaw_amp = 0.12
        self.shoulder_base = -0.6 if carry else 0.0
        self.elbow_base = -1.2 if carry else -0.3
        self.waist_pitch_ref = -0.25 if carry else 0.0
        # indices of a few posture joints
        self._posture_names = (
            ['waist_yaw', 'waist_pitch', 'neck_yaw', 'neck_pitch']
            + [f'{s}_{j}' for s in 'lr' for j in
               ('shoulder_pitch', 'shoulder_roll', 'shoulder_yaw', 'elbow',
                'wrist_roll', 'wrist_pitch', 'wrist_yaw')]
        )
        self.phase = 'balance'
        self.s = 0.0
        self.t_left = 0.4
        self.T_step = T_NOM
        self.stance = 'l'
        self.swing = 'r'
        self.trail = 'r'
        self.lead = 'l'
        self.ds_s = 0.0
        self.ds_T = DS_FRAC * T_NOM
        self.plant = {}
        self.swing_p0 = np.zeros(3)
        self.swing_p1 = np.zeros(3)
        self.swing_yaw0 = 0.0
        self.swing_yaw1 = 0.0
        self.swing_pitch0 = 0.0
        self.trail_toe = np.zeros(3)
        self.trail_yaw = 0.0
        self.yaw_land = 0.0
        self.q_seed = None
        self.q_ref = None
        self.v_ref = np.zeros(m.nv)
        self.x_ref = 0.0
        self.y_ref = 0.0
        self.com_z_ref = 0.9
        self.omega = np.sqrt(G / 0.93)
        self.v_int = 0.0
        self.yaw_ref_prev = 0.0
        self.steps_done = 0
        self.landings = []
        self.x_prev = None
        self.qp_ok = 0
        self.qp_fail = 0
        self.last_ms = 0.0
        self.last_tau = np.zeros(m.nu)
        self.last_status = ''
        self.last_base_res = 0.0
        self.cmd_cop = {'l': np.full(2, np.nan), 'r': np.full(2, np.nan)}
        self.dbg_swing = (np.zeros(3), np.zeros(3), 0.0)
        self.dbg_qacc_knee = 0.0
        self.fz = {'l': 0.0, 'r': 0.0}
        self.k = 0
        self.mass = float(m.body_subtreemass[1])
        self.mg = self.mass * G
        self.plan_on = False
        self.rate = 1.0
        self.rate_nom = 1.0
        self.v_plan = 1.2
        self.foot_off = np.zeros(3)
        self.yaw_off = 0.0
        self.yaw_int = 0.0
        self.swing_yaw = 0.0
        self.phase_t = 0.0
        self.contact_mode = 'ss'
        self.dcm_off = np.zeros(2)
        self._dcm_side = None
        self._hold_key = None
        self._hold_p = np.zeros(3)
        self._hold_yaw = 0.0
        self.foot_tgt = None
        self.foot_tgt_yaw = 0.0
        self.foot_tgt_on = False
        self.load_override = None
        self.g_dof = None
        self.dbg_line = ''
        self.swing_iv = {}

    # ---------------------------------------------------------------- setup
    def initialize(self, d):
        m = self.m
        r = self.robot
        if self.carry:
            r.set_arms(self.shoulder_base, self.elbow_base)
            r.q[m.jnt_qposadr[m.joint('waist_pitch').id]] = self.waist_pitch_ref
        feet = {
            'l': (np.array([0.0, HALF_W, SOLE]), 0.0, 0.0),
            'r': (np.array([0.0, -HALF_W, SOLE]), 0.0, 0.0),
        }
        q = r.ik_com(r.q.copy(), feet, np.array([FC, 0.0]), PEL_Z, np.array([1.0, 0, 0, 0]), iters=8)
        d.qpos[:] = q
        d.qvel[:] = 0
        d.qpos[2] -= 0.001  # engage all four corners of each sole
        mujoco.mj_forward(m, d)
        self.z0 = float(d.qpos[2])
        mujoco.mj_subtreeVel(m, d)
        com = d.subtree_com[1].copy()
        self.com_z_ref = float(com[2])
        self.x_ref = float(com[0])
        self.y_ref = float(com[1])
        self.y_ref0 = float(com[1])
        self.omega = float(np.sqrt(G / max(self.com_z_ref, 0.4)))
        self.mass = float(m.body_subtreemass[1])
        self.mg = self.mass * G
        for s in 'lr':
            p, R, *_ = self._body(d, self.foot[s])
            roll, pitch, yaw = yaw_pitch_roll(R)
            ankle = np.array([p[0], p[1], SOLE])
            self.plant[s] = self._make_plant(ankle, yaw)
        self.q_seed = d.qpos.copy()
        self.q_ref = d.qpos.copy()
        self.phase = 'balance'
        self.k = 0
        return dict(mass=self.mass, com_z=self.com_z_ref, omega=self.omega,
                    pelvis_z=self.z0, cruise=self.cruise)

    def _make_plant(self, ankle, yaw):
        ankle = np.asarray(ankle, float).copy()
        ankle[2] = SOLE
        R = rpy_R(0.0, 0.0, yaw)
        return dict(ankle=ankle, yaw=float(yaw), pitch=0.0, R=R,
                    toe=toe_from_ankle(ankle, yaw, 0.0),
                    sole=sole_center(ankle[:2], yaw))

    def v_profile(self, t):
        if getattr(self, 'stand_only', False):
            return 0.0
        # Speed starts as the first foot leaves, after the lateral weight shift.
        t0 = self.balance_s + self.shift_s
        tramp = 0.28
        if t < t0:
            return 0.0
        if t < t0 + tramp:
            return self.cruise * (t - t0) / tramp
        return self.cruise

    def _sole_corners(self, ankle_xy, yaw, margin=0.01):
        c, s = np.cos(yaw), np.sin(yaw)
        R = np.array([[c, -s], [s, c]])
        ankle = np.asarray(ankle_xy, float)
        out = []
        for x in (HEEL + margin, TOE - margin):
            for y in (-HALFW + margin, HALFW - margin):
                out.append(ankle + R @ np.array([x, y]))
        return out

    def _project_sole(self, p, ankle_xy, yaw, margin=0.01):
        c, s = np.cos(yaw), np.sin(yaw)
        R = np.array([[c, -s], [s, c]])
        local = R.T @ (np.asarray(p, float) - np.asarray(ankle_xy, float))
        local[0] = float(np.clip(local[0], HEEL + margin, TOE - margin))
        local[1] = float(np.clip(local[1], -(HALFW - margin), HALFW - margin))
        return np.asarray(ankle_xy, float) + R @ local

    def _hull(self, pts):
        pts = sorted((float(p[0]), float(p[1])) for p in pts)
        if len(pts) <= 1:
            return [np.array(p) for p in pts]

        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        lower = []
        for p in pts:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        upper = []
        for p in reversed(pts):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        return [np.array(p) for p in lower[:-1] + upper[:-1]]

    def _project_poly(self, p, corners):
        hull = self._hull(corners)
        p = np.asarray(p, float)
        n = len(hull)
        if n == 0:
            return p.copy()
        if n == 1:
            return hull[0].copy()
        # inside test (boundary counts as inside)
        inside = False
        for i in range(n):
            a, b = hull[i], hull[(i + 1) % n]
            if ((a[1] > p[1]) != (b[1] > p[1])) and (
                    p[0] < (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1] + 1e-15) + a[0]):
                inside = not inside
        if inside:
            return p.copy()
        best, best_d = hull[0], 1e9
        for i in range(n):
            a, b = hull[i], hull[(i + 1) % n]
            ab = b - a
            den = float(ab @ ab) + 1e-15
            t = float(np.clip(((p - a) @ ab) / den, 0.0, 1.0))
            q = a + t * ab
            dist = float(np.sum((q - p) ** 2))
            if dist < best_d:
                best, best_d = q, dist
        return best

    def _foot_yaw_xy(self, d, side):
        p = d.xpos[self.foot[side]]
        R = d.xmat[self.foot[side]].reshape(3, 3)
        yaw = float(np.arctan2(R[1, 0], R[0, 0]))
        return p[:2].copy(), yaw

    def _zmp_target(self, d, com_xy, cd_xy, v_cmd):
        """Feasible COM acceleration from a ZMP inside the current support.

        The unconstrained ZMP is the one that realizes a PD acceleration about
        the leashed COM reference. Projecting it into the sole (one foot in
        single support, the convex hull of both in balance and double support)
        keeps the centroidal task inside the wrench cone. A large miss is left
        for the footstep MPC.
        """
        om2 = self.omega ** 2
        com_xy = np.asarray(com_xy, float)
        cd_xy = np.asarray(cd_xy, float)
        if self.phase == 'ss':
            # Keep the CoP near the middle of the stance sole. Projecting a
            # ZMP that sits under the COM onto this foot lands on the inner
            # edge and rolls the foot over.
            ankle, yaw = self._foot_yaw_xy(d, self.stance)
            c, s = np.cos(yaw), np.sin(yaw)
            R = np.array([[c, -s], [s, c]])
            center = ankle + R @ np.array([FC, 0.0])
            v_chase = v_cmd if self.steps_done >= 2 else float(cd_xy[0])
            a_pd = np.array([
                2.5 * (self.x_ref - com_xy[0]) + 3.0 * (v_chase - cd_xy[0]),
                2.0 * (self.y_ref - com_xy[1]) + 1.5 * (0.0 - cd_xy[1]),
            ])
            off = R.T @ (-a_pd / om2)
            off[0] = float(np.clip(off[0], -0.045, 0.045))
            off[1] = float(np.clip(off[1], -0.018, 0.018))
            p = center + R @ off
            return p, om2 * (com_xy - p)
        a_pd = np.array([
            2.5 * (self.x_ref - com_xy[0]) + 3.0 * (v_cmd - cd_xy[0]),
            14.0 * (self.y_ref - com_xy[1]) + 5.0 * (0.0 - cd_xy[1]),
        ])
        a_pd[0] = float(np.clip(a_pd[0], -2.2, 2.2))
        a_pd[1] = float(np.clip(a_pd[1], -2.2, 2.2))
        p_des = com_xy - a_pd / om2
        corners = []
        for s in 'lr':
            ankle, yaw = self._foot_yaw_xy(d, s)
            corners.extend(self._sole_corners(ankle, yaw, margin=0.008))
        p = self._project_poly(p_des, corners)
        return p, om2 * (com_xy - p)

    # ---------------------------------------------------------------- kinematics
    def _body(self, d, body):
        R = d.xmat[body].reshape(3, 3).copy()
        p = d.xpos[body].copy()
        jp = np.zeros((3, self.nv))
        jr = np.zeros((3, self.nv))
        mujoco.mj_jacBody(self.m, d, jp, jr, body)
        return p, R, jp @ d.qvel, jr @ d.qvel, jp, jr

    def _com_jac(self, d):
        J = np.zeros((3, self.nv))
        mujoco.mj_jacSubtreeCom(self.m, d, J, self.pelvis)
        return J

    def _Ag(self, d):
        """Centroidal momentum matrix about the whole-robot COM. Rows: linear, angular."""
        nv = self.nv
        Ag = np.zeros((6, nv))
        c = d.subtree_com[self.pelvis]
        for b in range(1, self.m.nbody):
            mb = self.m.body_mass[b]
            if mb <= 0:
                continue
            jp = np.zeros((3, nv))
            jr = np.zeros((3, nv))
            mujoco.mj_jac(self.m, d, jp, jr, d.xipos[b], b)
            Rm = d.ximat[b].reshape(3, 3)
            Ic = Rm @ np.diag(self.m.body_inertia[b]) @ Rm.T
            Ag[0:3] += mb * jp
            Ag[3:6] += mb * _skew(d.xipos[b] - c) @ jp + Ic @ jr
        return Ag

    def _bias_mass(self, d):
        m = self.m
        ds = self.ds
        flags = m.opt.disableflags
        m.opt.disableflags = flags | int(mujoco.mjtDisableBit.mjDSBL_CONTACT
                                          | mujoco.mjtDisableBit.mjDSBL_LIMIT
                                          | mujoco.mjtDisableBit.mjDSBL_FRICTIONLOSS)
        try:
            ds.qpos[:] = d.qpos
            ds.qvel[:] = d.qvel
            ds.qacc[:] = 0
            mujoco.mj_inverse(m, ds)
            h = ds.qfrc_inverse.copy()
            M = np.zeros((self.nv, self.nv))
            # MuJoCo >= 3.3: mj_fullM(m, d, dst) reads the CSR inertia d.M
            mujoco.mj_fullM(m, ds, M)
        finally:
            m.opt.disableflags = flags
        return M, h

    def _perturbed(self, d, eps=1e-5):
        q2 = d.qpos.copy()
        mujoco.mj_integratePos(self.m, q2, d.qvel, eps)
        ds = self.ds
        ds.qpos[:] = q2
        ds.qvel[:] = d.qvel
        mujoco.mj_kinematics(self.m, ds)
        mujoco.mj_comPos(self.m, ds)
        return ds

    # ---------------------------------------------------------------- references
    def _foot_target(self, side):
        """World pose target (p, R, v, w, a) for a foot at the current phase."""
        if self.phase == 'balance' or (self.phase == 'ds' and side == self.lead) or (
                self.phase == 'ss' and side == self.stance):
            pl = self.plant[side]
            return pl['ankle'].copy(), pl['R'].copy(), np.zeros(3), np.zeros(3), np.zeros(3)
        if self.phase == 'ds' and side == self.trail:
            return self._heel_off_target()
        if self.phase == 'ss' and side == self.swing:
            return self._swing_target()
        pl = self.plant[side]
        return pl['ankle'].copy(), pl['R'].copy(), np.zeros(3), np.zeros(3), np.zeros(3)

    def _heel_off_target(self):
        sd = 1.0 / max(self.ds_T, 1e-3)
        s = float(np.clip(self.ds_s, 0.0, 1.0))

        def pose(ss):
            th = TH_TO * _mj(np.clip(ss, 0, 1))
            p = ankle_from_toe(self.trail_toe, self.trail_yaw, th)
            R = rpy_R(0.0, th, self.trail_yaw)
            return p, R, th

        p, R, th = pose(s)
        ds = 1e-3
        pp, Rp, _ = pose(s + ds)
        pm, Rm, _ = pose(s - ds)
        v = (pp - pm) / (2 * ds) * sd
        a = (pp - 2 * p + pm) / (ds ** 2) * sd ** 2
        w = rotvec(Rp, Rm) / (2 * ds) * sd
        return p, R, v, w, a

    def _swing_target(self):
        s = float(np.clip(self.s, 0.0, 1.0))
        # s_dot from the countdown (see _advance)
        sd = (1.0 - s) / max(self.t_left, 1e-3) if self.t_left > 1e-3 and s < 0.999 else 0.0
        p0, p1 = self.swing_p0, self.swing_p1
        y0, y1 = self.swing_yaw0, self.swing_yaw1
        p0th = self.swing_pitch0

        def pose(ss):
            ss = float(np.clip(ss, 0, 1))
            u = min(1.0, ss / 0.5)
            pitch = p0th * (1.0 - _mj(u))
            yaw = y0 + (y1 - y0) * _mj(ss)
            p = p0 + (p1 - p0) * _mj(ss)
            g, _, _ = _bump(ss)
            p = p.copy()
            # s*(1-s)^2 peaks at s=1/3, leaves the ground immediately, and
            # arrives with zero vertical speed (a sine hump slams the landing).
            lift = 0.05 * (27.0 / 4.0) * ss * (1.0 - ss) ** 2
            p[2] = p0[2] + (p1[2] - p0[2]) * _mj(ss) + lift
            p[:2] = p0[:2] + (p1[:2] - p0[:2]) * _mj(ss)
            R = rpy_R(0.0, pitch, yaw)
            return p, R

        p, R = pose(s)
        ds = 1e-3
        pp, Rp = pose(s + ds)
        pm, Rm = pose(s - ds)
        v = (pp - pm) / (2 * ds) * sd
        a = (pp - 2 * p + pm) / (ds ** 2) * (sd ** 2)
        w = rotvec(Rp, Rm) / (2 * ds) * sd
        return p, R, v, w, a

    def _alphas(self):
        if self.phase == 'balance':
            return {'l': 0.5, 'r': 0.5}
        if self.phase == 'ss':
            a = {'l': 0.0, 'r': 0.0}
            a[self.stance] = 1.0
            return a
        # DS: the foot that just landed takes about half the weight at once,
        # then the rest across the double-support interval. Starting from zero
        # fights the contact impulse and bounces the pelvis.
        s = float(np.clip(self.ds_s, 0, 1))
        lead = 0.45 + 0.55 * _mj(s)
        a = {'l': 0.0, 'r': 0.0}
        a[self.lead] = lead
        a[self.trail] = 1.0 - lead
        return a

    def _stance_mask(self):
        if self.phase == 'balance':
            return {'l': True, 'r': True}
        if self.phase == 'ds':
            return {'l': True, 'r': True}
        return {'l': self.stance == 'l', 'r': self.stance == 'r'}

    # ---------------------------------------------------------------- MPC
    def _predict(self, c, cd, p, T):
        if T <= 1e-4:
            return c.copy(), cd.copy()
        wT = self.omega * T
        ch, sh = np.cosh(wT), np.sinh(wT)
        cT = p + (c - p) * ch + (cd / self.omega) * sh
        cdT = (c - p) * self.omega * sh + cd * ch
        return cT, cdT

    def _place(self, c_td, cd_td, T, v_des, stance_sole, pelvis_xy, side, yaw):
        """Next sole position. Sagittal: LIPM QP vs a nominal step. Lateral: width + capture."""
        # Sagittal: a cruise-length step, shortened when we are slower than the
        # command (lets the COM fall forward) and lengthened when we are faster.
        # Hip-roll travel is only about ±12 deg, so the lateral target stays
        # inside roughly 10–16.5 cm from the pelvis.
        T = float(np.clip(T, 0.35, 0.60))
        px = stance_sole[0] + (0.55 * v_des + 0.45 * cd_td[0]) * T
        px += 0.20 * (cd_td[0] - v_des)
        px = float(np.clip(px, stance_sole[0] + 0.12, stance_sole[0] + 0.62))
        px = float(np.clip(px, pelvis_xy[0] - 0.02, pelvis_xy[0] + 0.55))
        extra = float(np.clip(0.18 * cd_td[1] + 0.30 * (c_td[1] - pelvis_xy[1]), -0.035, 0.035))
        py = pelvis_xy[1] + side * HALF_W + extra
        near = pelvis_xy[1] + side * 0.10
        far = pelvis_xy[1] + side * 0.165
        lo, hi = (min(near, far), max(near, far))
        if side > 0:
            py = max(py, stance_sole[1] + 0.16)
        else:
            py = min(py, stance_sole[1] - 0.16)
        py = float(np.clip(py, lo, hi))
        sole = np.array([px, py])
        ankle_xy = sole - np.array([FC * np.cos(yaw), FC * np.sin(yaw)])
        return np.array([ankle_xy[0], ankle_xy[1], SOLE]), sole

    def _mpc(self, d):
        mujoco.mj_subtreeVel(self.m, d)
        c = d.subtree_com[1][:2].copy()
        cd = d.subtree_linvel[1][:2].copy()
        pelvis_xy = d.qpos[:2].copy()
        t = float(d.time)
        v_now = self.v_profile(t)
        self.v_int = float(np.clip(self.v_int + (v_now - cd[0]) * 0.01, -0.25, 0.25))
        v_des = v_now + 0.35 * self.v_int
        # support polygon center used as the LIPM ZMP guess
        if self.phase == 'ss':
            pz = getattr(self, 'p_zmp', None)
            if pz is not None and np.all(np.isfinite(pz)):
                p_zmp = np.asarray(pz, float).copy()
            else:
                p_zmp = self.plant[self.stance]['sole'].copy()
            side = 1.0 if self.swing == 'l' else -1.0
            s_swing = self.s
            trem0 = max(self.t_left, 0.08)
            stance_for_sep = self.plant[self.stance]['sole']
            stance_side = self.stance
        elif self.phase == 'ds':
            p_zmp = self.plant[self.lead]['sole'].copy()
            side = 1.0 if self.trail == 'l' else -1.0
            s_swing = 0.0
            trem0 = max(self.ds_T * (1 - self.ds_s), 0.0) + T_NOM * (1 - DS_FRAC)
            stance_for_sep = self.plant[self.lead]['sole']
            stance_side = self.lead
        else:
            return
        hy = float(d.qpos[self.qa[stance_side + 'hip_yaw']])
        excess = hy - float(np.clip(hy, -0.18, 0.18))
        yaw_cmd = float(np.clip(0.8 * excess, -0.30, 0.30))
        pel_yaw = yaw_pitch_roll(d.xmat[self.pelvis].reshape(3, 3))[2]
        if abs(pel_yaw) > 0.22:
            yaw_cmd = float(np.clip(0.4 * yaw_cmd + 0.6 * pel_yaw, -0.35, 0.35))
        self.yaw_land += 0.25 * (yaw_cmd - self.yaw_land)
        best = None
        xi = c + cd / self.omega
        lat_out = abs(xi[1] - p_zmp[1])
        for trem_k in (0.70, 1.0, 1.25, 0.50):
            Trem = float(np.clip(trem0 * trem_k, 0.10, 0.55))
            for Tstep in (0.42, 0.50, 0.58):
                c_td, cd_td = self._predict(c, cd, p_zmp, Trem)
                v_td = self.v_profile(t + Trem + Tstep)
                # Plan the step for the cruise, not the ramp value, so the first
                # step is a real step. The Raibert term shortens it while vx is low.
                v_use = max(v_td, 0.80 * self.cruise) + 0.25 * self.v_int
                v_use = float(np.clip(v_use, 0.4, self.cruise + 0.05))
                ankle, sole = self._place(c_td, cd_td, Tstep, v_use, p_zmp, pelvis_xy, side, self.yaw_land)
                c2, cd2 = self._predict(c_td, cd_td, sole, Tstep * (1 - DS_FRAC))
                cost = (cd2[0] - v_use) ** 2 + 2.2 * cd2[1] ** 2
                cost += 0.15 * (Tstep - T_NOM) ** 2 + 0.04 * (Trem - trem0) ** 2
                if lat_out > 0.07:
                    cost += 6.0 * (lat_out - 0.07) * Trem
                # reachability already clamped; penalize a saturated forward step
                if sole[0] > p_zmp[0] + 0.70:
                    cost += 1.0
                if best is None or cost < best[0]:
                    best = (cost, Trem, Tstep, ankle, sole)
        _, Trem, Tstep, ankle, sole = best
        self.T_step = Tstep
        if self.phase == 'ss':
            self.t_left = Trem
            # filter the cartesian target so a push doesn't teleport the spline
            self.swing_p1 = self.swing_p1 + 0.55 * (ankle - self.swing_p1)
            self.swing_p1[2] = SOLE
            self.swing_yaw1 += 0.55 * (self.yaw_land - self.swing_yaw1)
        else:
            self._next_ankle = ankle.copy()
            self._next_yaw = float(self.yaw_land)
            self._next_T = Tstep

    def _ik(self, d):
        """Posture reference for the null space (legs via IK, arms/waist from the plan)."""
        if self.q_seed is None:
            self.q_seed = d.qpos.copy()
        q = self.q_seed.copy()
        # pelvis attitude reference
        xl = self.plant['l']['ankle'][0]
        xr = self.plant['r']['ankle'][0]
        if self.phase == 'ss' and self.swing == 'l':
            xl = self.swing_p1[0]
        elif self.phase == 'ss' and self.swing == 'r':
            xr = self.swing_p1[0]
        dl = (xl - xr) / 0.60
        yaw_ref = -self.yaw_amp * dl
        self._yaw_ref = float(yaw_ref)
        half = 0.5 * yaw_ref
        quat = np.array([np.cos(half), 0.0, 0.0, np.sin(half)])
        feet = {}
        for s in 'lr':
            p, R, *_ = self._foot_target(s)
            roll, pitch, yaw = yaw_pitch_roll(R)
            feet[s] = (p, yaw, pitch)
        # Solve the legs from the pelvis we actually have. Using the nominal
        # 1.02 m makes the swing-knee reference too straight whenever the
        # pelvis has sagged, so the foot never clears.
        com_xy = d.subtree_com[1][:2].copy()
        try:
            q = self.robot.ik_com(q, feet, com_xy, float(d.qpos[2]), quat, iters=2)
        except Exception:
            pass
        # arms and waist (ik_com does not touch them)
        m = self.m
        q[m.jnt_qposadr[m.joint('waist_yaw').id]] = -yaw_ref
        q[m.jnt_qposadr[m.joint('waist_pitch').id]] = self.waist_pitch_ref
        for s, sg in (('l', 1.0), ('r', -1.0)):
            q[m.jnt_qposadr[m.joint(f'{s}_shoulder_pitch').id]] = self.shoulder_base + sg * self.arm_amp * dl
            q[m.jnt_qposadr[m.joint(f'{s}_elbow').id]] = self.elbow_base
            q[m.jnt_qposadr[m.joint(f'{s}_shoulder_roll').id]] = sg * 0.15
        # clamp into the model range
        for name, jid in self.jnt_id.items():
            dof = m.jnt_dofadr[jid]
            qa = m.jnt_qposadr[jid]
            q[qa] = np.clip(q[qa], self.qmin[dof] + 0.01, self.qmax[dof] - 0.01)
        if self.q_ref is not None:
            # joint velocity reference from the IK change (MPC period)
            v = np.zeros(self.nv)
            mujoco.mj_differentiatePos(m, v, 0.01, self.q_ref, q)
            self.v_ref = np.clip(v, -8, 8)
        self.q_ref = q
        self.q_seed = q

    # ---------------------------------------------------------------- WBC
    def _wbc(self, d):
        import time
        t0 = time.perf_counter()
        m = self.m
        nv, nu = self.nv, self.nu
        nw = 12
        n = nv + nw
        M, h = self._bias_mass(d)
        mujoco.mj_subtreeVel(m, d)
        # Jacobians now and at q + v eps (for Jdot qvel and A_G dot qvel)
        Jcom = self._com_jac(d)
        vcom = Jcom @ d.qvel
        feet = {}
        for s in 'lr':
            p, R, v, w, jp, jr = self._body(d, self.foot[s])
            feet[s] = dict(p=p, R=R, v=v, w=w, jp=jp, jr=jr)
        Ag = self._Ag(d)
        hmom = Ag @ d.qvel
        Jdot_com = np.zeros(3)
        Jdot_foot = {s: (np.zeros(3), np.zeros(3)) for s in 'lr'}
        Adot = np.zeros(6)
        if np.linalg.norm(d.qvel) > 1e-4:
            eps = 1e-5
            dp = self._perturbed(d, eps)
            Jcom2 = self._com_jac(dp)
            Jdot_com = ((Jcom2 @ d.qvel) - vcom) / eps
            for s in 'lr':
                p2, R2, v2, w2, jp2, jr2 = self._body(dp, self.foot[s])
                # _body uses d.qvel inside, but dp.qvel was set equal to d.qvel
                Jdot_foot[s] = ((jp2 @ d.qvel - feet[s]['v']) / eps,
                                (jr2 @ d.qvel - feet[s]['w']) / eps)
            Ag2 = self._Ag(dp)
            Adot = (Ag2 @ d.qvel - hmom) / eps
        # restore shadow after the perturbation before anyone else uses it
        Jw = np.zeros((nv, nw))
        for i, s in enumerate('lr'):
            R = feet[s]['R']
            jp, jr = feet[s]['jp'], feet[s]['jr']
            Jw[:, 6 * i:6 * i + 3] = jp.T @ R
            Jw[:, 6 * i + 3:6 * i + 6] = jr.T @ R
        # costs
        P = np.eye(n) * 1e-6
        qv = np.zeros(n)
        def add_task(J, rhs, w):
            # J is (k, nv), minimize ||sqrt(w) (J qacc - rhs)||^2
            Wj = (J.T * np.asarray(w, float)) @ J if np.ndim(w) else (w * (J.T @ J))
            # support per-row weights
            if np.ndim(w):
                JW = J * np.asarray(w)[:, None]
                P[:nv, :nv] += J.T @ JW
                qv[:nv] += -(J.T @ (np.asarray(w) * rhs))
            else:
                P[:nv, :nv] += w * (J.T @ J)
                qv[:nv] += -w * (J.T @ rhs)
        # centroidal linear momentum -> COM acceleration consistent with a
        # ZMP that lies inside the current sole (balance, stance, or both feet)
        v_cmd = self.v_profile(float(d.time))
        com = d.subtree_com[1]
        cd = d.subtree_linvel[1]
        # Ankle-strategy acceleration on the first two steps pitches the stance
        # foot onto its toe. Track speed with the feet once a step has landed
        # ahead; until then follow the velocity we already have.
        v_int = v_cmd if self.steps_done >= 2 else min(v_cmd, max(float(cd[0]), 0.0))
        self.x_ref += v_int * self.dt
        if abs(self.x_ref - com[0]) > 0.12:
            self.x_ref = com[0] + np.sign(self.x_ref - com[0]) * 0.12
        # Lateral reference: shift onto the upcoming stance foot while both
        # feet are down, then hold a point inboard of that sole during swing.
        if self.phase == 'ss':
            y_tgt = 0.50 * self.plant[self.stance]['sole'][1]
        elif self.phase == 'ds':
            y_tgt = 0.45 * self.plant[self.lead]['sole'][1]
        elif (not getattr(self, 'stand_only', False)
              and float(d.time) > self.balance_s):
            y_tgt = 0.55 * HALF_W  # first stance foot is the left one
        else:
            y_tgt = getattr(self, 'y_ref0', 0.0)
        self.y_ref += float(np.clip(y_tgt - self.y_ref, -0.004, 0.004))
        p_zmp, a_xy = self._zmp_target(d, com[:2], cd[:2], v_cmd)
        a_des = np.zeros(3)
        a_des[0] = float(np.clip(a_xy[0], -4.0, 4.0))
        a_des[1] = float(np.clip(a_xy[1], -4.0, 4.0))
        a_des[2] = float(np.clip(
            90.0 * (self.com_z_ref - com[2]) + 20.0 * (0.0 - cd[2]), -12.0, 12.0))
        self.a_des = a_des
        self.p_zmp = p_zmp
        add_task(Jcom, a_des - Jdot_com, np.array([30.0, 36.0, 70.0]))
        # centroidal angular momentum rate: damp spin, help upright the pelvis
        Rp = d.xmat[self.pelvis].reshape(3, 3)
        yaw_ref = getattr(self, '_yaw_ref', 0.0)
        R_des = rpy_R(0.0, 0.0, yaw_ref)
        er = rotvec(R_des, Rp)
        L = hmom[3:6]
        hdot_ang = -6.0 * L + np.array([50.0, 50.0, 12.0]) * er
        add_task(Ag[3:6], hdot_ang - Adot[3:6], np.array([0.04, 0.04, 0.015]))
        # pelvis orientation (distributes the centroidal moment onto the torso)
        jp, jr = np.zeros((3, nv)), np.zeros((3, nv))
        mujoco.mj_jacBody(m, d, jp, jr, self.pelvis)
        w_pel = jr @ d.qvel
        yaw_dot = (yaw_ref - self.yaw_ref_prev) / 0.01
        self.yaw_ref_prev = yaw_ref
        w_des = np.array([0.0, 0.0, yaw_dot])
        a_pel = np.array([90.0, 90.0, 35.0]) * er + np.array([14.0, 14.0, 6.0]) * (w_des - w_pel)
        # Jdot of pelvis angular vel
        if np.linalg.norm(d.qvel) > 1e-4:
            # reuse a one-step difference already not stored; finite diff jr quickly
            dp = self.ds  # still at the perturbed pose from above if we perturbed
            # _perturbed overwrote ds; if qvel was tiny we skipped it. Recompute only if needed.
        jdot_w = np.zeros(3)
        if np.linalg.norm(d.qvel) > 1e-4:
            jr2 = np.zeros((3, nv))
            mujoco.mj_jacBody(m, self.ds, np.zeros((3, nv)), jr2, self.pelvis)
            jdot_w = (jr2 @ d.qvel - w_pel) / 1e-5
        add_task(jr, a_pel - jdot_w, np.array([16.0, 16.0, 3.0]))
        # feet
        stance = self._stance_mask()
        alphas = self._alphas()
        for i, s in enumerate('lr'):
            p_des, R_des_f, v_des, w_des_f, a_ff = self._foot_target(s)
            p, R, v, w = feet[s]['p'], feet[s]['R'], feet[s]['v'], feet[s]['w']
            jp, jr = feet[s]['jp'], feet[s]['jr']
            e_p = p_des - p
            e_r = rotvec(R_des_f, R)
            jd_v, jd_w = Jdot_foot[s]
            if stance[s]:
                kp = np.array([50.0, 50.0, 140.0])
                kd = np.array([14.0, 14.0, 22.0])
                wt = np.array([24.0, 24.0, 50.0])
                kpr = np.array([220.0, 90.0, 70.0])  # roll, pitch, yaw in world; roll weighted below
                kdr = np.array([18.0, 12.0, 8.0])
                # express angular weights in the foot frame (roll / pitch / yaw)
                a_lin = a_ff + kp * e_p + kd * (v_des - v)
                a_ang = kpr * e_r + kdr * (w_des_f - w)
                # boost foot-frame roll: rotate the angular residual weight
                Rf = R
                J_ang = Rf.T @ jr
                rhs_ang = Rf.T @ (a_ang - jd_w)
                w_ang = np.array([40.0, 10.0, 8.0])  # roll, pitch, yaw
                add_task(jp, a_lin - jd_v, wt)
                add_task(J_ang, rhs_ang, w_ang)
            else:
                kp = np.array([160.0, 160.0, 200.0])
                kd = np.array([22.0, 22.0, 24.0])
                a_lin = np.clip(a_ff + kp * e_p + kd * (v_des - v), -25.0, 25.0)
                kpr = np.array([120.0, 80.0, 100.0])
                kdr = np.array([12.0, 10.0, 10.0])
                a_ang = kpr * e_r + kdr * (w_des_f - w)
                Rf = R
                add_task(jp, a_lin - jd_v, np.array([6.0, 6.0, 10.0]))
                add_task(Rf.T @ jr, Rf.T @ (a_ang - jd_w), np.array([5.0, 3.0, 4.0]))
                if s == self.swing:
                    self.dbg_swing = (e_p.copy(), a_lin.copy(), float(np.linalg.norm(jp)))
        # posture null space
        if self.q_ref is not None:
            v = np.zeros(nv)
            # acceleration-level PD on actuated joints
            for i in range(nu):
                dof = self.act_va[i]
                qa = self.act_qa[i]
                name = self.act_name[i]
                leg = any(name.endswith(j) for j in LEG)
                swing_leg = self.phase == 'ss' and name.startswith(self.swing + '_')
                if swing_leg:
                    # Joint-space swing from the IK pose. A pure cartesian lift
                    # was realized by extending into the floor and jumping.
                    kp, kd, w = 80.0, 10.0, 6.0
                elif leg:
                    kp, kd, w = 16.0, 3.0, 0.12
                elif name.startswith('waist'):
                    kp, kd, w = 55.0, 8.0, 0.7
                else:
                    kp, kd, w = 36.0, 5.0, 0.35
                qacc_des = kp * (self.q_ref[qa] - d.qpos[qa]) + kd * (self.v_ref[dof] - d.qvel[dof])
                P[dof, dof] += w
                qv[dof] += -w * qacc_des
        # wrench regularization and load share
        for i, s in enumerate('lr'):
            o = nv + 6 * i
            fz_des = alphas[s] * self.mg
            reg = np.array([1e-5, 1e-5, 2e-4, 8e-4, 8e-4, 1e-3])
            P[o:o + 6, o:o + 6] += np.diag(reg)
            qv[o + 2] += -2e-4 * fz_des
        # constraints
        rows = []
        lo = []
        hi = []
        def add_row(coeff, l, u):
            rows.append(coeff)
            lo.append(l)
            hi.append(u)
        # base dynamics: (M qacc + h - Jw w)[:6] = 0
        for r in range(6):
            coeff = np.zeros(n)
            coeff[:nv] = M[r]
            coeff[nv:] = -Jw[r]
            add_row(coeff, -h[r], -h[r])
        # torque limits
        for i in range(nu):
            dof = int(self.act_va[i])
            coeff = np.zeros(n)
            coeff[:nv] = M[dof]
            coeff[nv:] = -Jw[dof]
            lim = self.tau_max[i]
            add_row(coeff, -lim - h[dof], lim - h[dof])
        # wrench cones. Row 0 of each cone is Fz, given a finite upper bound.
        for i, s in enumerate('lr'):
            if stance[s] and self.phase == 'ds' and s == self.trail and self.ds_s > 0.35:
                heel = TOE - 0.02  # toe line once heel-off is underway
            else:
                heel = HEEL
            G = foot_cone(heel, TOE, HALFW, MU, YAW_MZ)
            for r in range(G.shape[0]):
                coeff = np.zeros(n)
                coeff[nv + 6 * i:nv + 6 * i + 6] = G[r]
                if not stance[s]:
                    # swing: only w = 0 is inside a cone whose Fz upper bound is 0
                    if r == 0:
                        add_row(coeff, 0.0, 0.0)
                    else:
                        add_row(coeff, 0.0, 0.0 if False else 1e6)
                        # with Fz fixed at 0 the other inequalities collapse to w=0,
                        # but OSQP needs them feasible at 0. Keep the cone.
                        lo[-1] = 0.0
                        hi[-1] = 1e6
                else:
                    if r == 0:
                        add_row(coeff, 15.0 if alphas[s] > 0.15 else 0.0, 2.4 * self.mg)
                    else:
                        add_row(coeff, 0.0, 1e6)
        # joint accel bounds from velocity and position limits
        qacc_lo = np.full(nv, -1e4)
        qacc_hi = np.full(nv, 1e4)
        dt = self.dt
        for dof in range(6, nv):
            v = d.qvel[dof]
            lo_v = (-self.vmax[dof] - v) / dt
            hi_v = (self.vmax[dof] - v) / dt
            # position: q + v dt + 0.5 qacc dt^2 inside range
            qa = None
            # map dof -> qpos for hinges (dof adr offset by the free joint's extra quat coord)
            # hinge qpos = dof + 1 because free joint is 7 qpos / 6 dof
            qadr = dof + 1
            if qadr < m.nq:
                q = d.qpos[qadr]
                lo_p = 2 * (self.qmin[dof] - q - v * dt) / dt ** 2
                hi_p = 2 * (self.qmax[dof] - q - v * dt) / dt ** 2
            else:
                lo_p, hi_p = -1e4, 1e4
            lo_b = max(lo_v, lo_p)
            hi_b = min(hi_v, hi_p)
            if lo_b > hi_b:
                lo_b, hi_b = -80.0, 80.0
            # Keep the QP inside a band the torque limits can actually produce.
            lo_c = float(np.clip(lo_b, -80.0, 80.0))
            hi_c = float(np.clip(hi_b, -80.0, 80.0))
            if lo_c > hi_c:
                pin = 80.0 if lo_b > 0.0 else -80.0
                lo_c = hi_c = pin
            qacc_lo[dof] = lo_c
            qacc_hi[dof] = hi_c
        for dof in range(nv):
            coeff = np.zeros(n)
            coeff[dof] = 1.0
            add_row(coeff, qacc_lo[dof], qacc_hi[dof])
        A = np.vstack(rows)
        l = np.asarray(lo, float)
        u = np.asarray(hi, float)
        # symmetrize and hand the upper triangle to OSQP
        P = 0.5 * (P + P.T)
        x = self._solve(P, qv, A, l, u)
        self.last_ms = (time.perf_counter() - t0) * 1e3
        if x is None:
            self.qp_fail += 1
            self.last_status = 'fail'
            tau = self.last_tau.copy()
        else:
            self.qp_ok += 1
            qacc = x[:nv]
            w = x[nv:]
            self.last_base_res = float(np.linalg.norm(M[:6] @ qacc + h[:6] - Jw[:6] @ w))
            tau_dof = M @ qacc + h - Jw @ w
            tau = np.zeros(nu)
            for i in range(nu):
                tau[i] = tau_dof[self.act_va[i]] / max(self.gear[i], 1e-8)
            tau = np.clip(tau, -self.tau_max, self.tau_max)
            tau = self._waist_zone(d, tau)
            self.last_tau = tau
            self.last_status = 'ok'
            for i, s in enumerate('lr'):
                fx, fy, fz, mx, my, mz = w[6 * i:6 * i + 6]
                self.fz[s] = float(fz)
                if fz > 20 and stance[s]:
                    self.cmd_cop[s] = np.array([(-my - SOLE * fx) / fz, (mx - SOLE * fy) / fz])
                else:
                    self.cmd_cop[s] = np.full(2, np.nan)
            self.x_prev = x
            self.dbg_qacc_knee = float(qacc[self.va['rknee']]) if 'rknee' in self.va else 0.0
        d.ctrl[:] = self.last_tau
        return self.last_tau

    def _waist_zone(self, d, tau):
        """Actuators D102 (bd21ff0) waist-pitch stop-zone torque zero, soft_limits.apply_waist_stop_zone (1ed4d73)."""
        import sys as _s, os as _o
        _p = _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), '..', '..', 'controls', 'limits')
        if _p not in _s.path: _s.path.insert(0, _p)
        from soft_limits import apply_waist_stop_zone
        m = self.m if hasattr(self, 'm') else None
        names = [m.actuator(i).name for i in range(m.nu)] if m is not None else []
        return apply_waist_stop_zone(names, lambda n: float(d.qpos[self.act_qa[names.index(n)]]), tau)

    def _solve(self, P, q, A, l, u):
        Ps = sp.csc_matrix(np.triu(P))
        As = sp.csc_matrix(A)
        try:
            prob = osqp_setup(Ps, q, As, l, u)
        except Exception as exc:
            self.last_status = f'setup {exc}'
            return None
        if self.x_prev is not None and len(self.x_prev) == len(q):
            try:
                prob.warm_start(x=self.x_prev)
            except Exception:
                pass
        res = prob.solve()
        status = res.info.status
        ok = status in ('solved', 'solved inaccurate') or (
            'maximum iterations' in status and res.info.prim_res < 1e-2)
        if not ok or res.x is None or not np.all(np.isfinite(res.x)):
            # retry without the joint-acceleration bounds (last nv rows)
            nv = self.nv
            l2 = l.copy()
            u2 = u.copy()
            l2[-nv:] = -1e5
            u2[-nv:] = 1e5
            prob2 = osqp_setup(Ps, q, As, l2, u2)
            res = prob2.solve()
            status = res.info.status
            ok = res.x is not None and np.all(np.isfinite(res.x)) and (
                status in ('solved', 'solved inaccurate') or 'maximum iterations' in status)
            if not ok:
                self.last_status = status
                return None
        return np.array(res.x, float)

    # ---------------------------------------------------------------- gait clock
    def _advance(self, d):
        dt = self.dt
        t = float(d.time)
        if self.phase == 'balance':
            if t >= self.balance_s + self.shift_s and not getattr(self, 'stand_only', False):
                self._begin_swing('r', 'l')
            return
        if self.phase == 'ss':
            frac = min(1.0, dt / max(self.t_left, 1e-4))
            self.s += (1.0 - self.s) * frac
            self.t_left -= dt
            # early contact
            fz = self._measured_fz(d, self.swing)
            if fz < 8.0 and self.s > 0.08:
                self.swing_cleared = True
            landed = (self.s > 0.55 and fz > 30.0 and getattr(self, 'swing_cleared', False))
            if landed or self.s >= 0.995 or self.t_left <= 0.0:
                self.s = 1.0
                self._begin_ds(d)
            return
        # DS
        self.ds_s += dt / max(self.ds_T, 1e-3)
        if self.ds_s >= 1.0:
            self._begin_swing(self.trail, self.lead)

    def _measured_fz(self, d, side):
        gid = self.foot_geom[side]
        fz = 0.0
        for i in range(d.ncon):
            c = d.contact[i]
            if gid not in (c.geom1, c.geom2):
                continue
            f = _contact_force_on(self.m, d, i, gid)
            if f is not None and f[2] > 0:
                fz += f[2]
        return fz

    def _begin_swing(self, swing, stance):
        self.phase = 'ss'
        self.swing = swing
        self.stance = stance
        self.s = 0.0
        # liftoff pose: end of heel-off if we have one, else the plant
        if swing in self.plant and self.phase:
            p, R, *_ = self._heel_off_target() if getattr(self, '_did_ds', False) else (None, None)
        self._did_ds = False
        pl = self.plant[swing]
        # sample heel-off at s=1 as the departure pose when a DS just finished;
        # on the first step there was no heel-off
        if getattr(self, '_ds_finished', False):
            self.ds_s = 1.0
            p, R, v, w, a = self._heel_off_target()
            self.swing_p0 = p.copy()
            self.swing_pitch0 = TH_TO
            self.swing_yaw0 = self.trail_yaw
        else:
            self.swing_p0 = pl['ankle'].copy()
            self.swing_pitch0 = 0.0
            self.swing_yaw0 = pl['yaw']
        ankle = getattr(self, '_next_ankle', None)
        if ankle is None:
            # nominal first step, replaced by MPC on the next tick
            direction = 1.0 if swing == 'l' else -1.0
            step_len = float(np.clip(self.cruise * T_NOM, 0.35, 0.65))
            sole = pl['sole'] + np.array([step_len, 0.0])
            sole[1] = direction * HALF_W
            ankle = np.array([sole[0] - FC, sole[1], SOLE])
            yaw = 0.0
        else:
            yaw = getattr(self, '_next_yaw', 0.0)
        self.swing_p1 = np.asarray(ankle, float).copy()
        self.swing_p1[2] = SOLE
        self.swing_yaw1 = float(yaw)
        self.T_step = getattr(self, '_next_T', T_NOM)
        self.t_left = self.T_step * (1.0 - DS_FRAC)
        self._ds_finished = False
        self.swing_cleared = False

    def _begin_ds(self, d):
        # swing foot has landed; it becomes the lead stance, old stance will toe-off.
        # Plant the measured ankle, flattened, so a late or early contact is not
        # dragged across the floor toward the preview target.
        landed = self.swing
        old = self.stance
        p = d.xpos[self.foot[landed]]
        R = d.xmat[self.foot[landed]].reshape(3, 3)
        yaw = float(np.arctan2(R[1, 0], R[0, 0]))
        ankle = np.array([p[0], p[1], SOLE])
        self.plant[landed] = self._make_plant(ankle, yaw)
        self.lead = landed
        self.trail = old
        self.trail_yaw = self.plant[old]['yaw']
        self.trail_toe = self.plant[old]['toe'].copy()
        self.phase = 'ds'
        self.ds_s = 0.0
        self.ds_T = max(DS_FRAC * self.T_step, 0.12)
        self._did_ds = True
        self._ds_finished = True
        self.steps_done += 1
        self.landings.append(dict(
            t=None, side=landed, x=float(ankle[0]), y=float(ankle[1]),
            yaw=yaw, width=float(abs(ankle[1] - self.plant[old]['ankle'][1]))))

    def use_plan(self, path, d):
        """Track a periodic slice of a scenarios.py walk (1 kHz QP around that reference)."""
        z = np.load(path)
        Q = z['Q'].astype(float)
        V = z['V'].astype(float)
        C = z['com'].astype(float)
        AL = z['AL'].astype(float)
        dt = float(z['t'][1] - z['t'][0])

        def seam(nfr):
            best = None
            for i in range(200, len(Q) - nfr - 1):
                dq = Q[i + nfr] - Q[i]
                dq[0] = 0.0
                dq[3:7] = 0.0
                e = float(np.max(np.abs(dq)))
                if best is None or e < best[0]:
                    best = (e, i, float(Q[i + nfr, 0] - Q[i, 0]))
            return best

        err, i0, dx = seam(200)
        nfr = 200
        if err > 0.02:
            err2, i2, dx2 = seam(400)
            if err2 < err:
                err, i0, dx, nfr = err2, i2, dx2, 400
        sl = slice(i0, i0 + nfr + 1)
        self.plan_Q = Q[sl].copy()
        self.plan_V = V[sl].copy()
        self.plan_C = C[sl].copy()
        self.plan_AL = AL[sl].copy()
        self.plan_TAU = z['TAU'].astype(float)[sl].copy()
        self.plan_FZ = z['FZ'].astype(float)[sl].copy()
        self.plan_COP = z['COP'].astype(float)[sl].copy()
        lim = self.tau_max
        self.pd_kp = np.clip(lim * 4.0, 40.0, 800.0)
        arm = np.maximum(self.m.dof_armature[self.act_va], 0.05)
        self.pd_kd = 2.0 * np.sqrt(self.pd_kp * arm) + 0.02 * self.pd_kp
        self.plan_dt = dt
        self.period = nfr * dt
        self.cycle_dx = dx
        self.plan_err = err
        q0 = self.plan_Q[0].copy()
        v0 = self.plan_V[0].copy()
        # Cruise slice starts several meters down the plan. Shift x to 0 so
        # pelvis_x/time is the walked speed.
        x0 = float(q0[0])
        self.plan_Q[:, 0] -= x0
        self.plan_C[:, 0] -= x0
        q0[0] -= x0
        self.x_origin = x0
        d.qpos[:] = q0
        d.qvel[:] = v0
        mujoco.mj_forward(self.m, d)
        lo = min(d.geom_xpos[self.foot_geom[s]][2] - 0.009 for s in 'lr')
        # A sole that sits exactly on z=0 only reports an edge. Sink 1.5 mm
        # so the flat foot gets all four corners.
        drop = float(lo + 0.0015)
        d.qpos[2] -= drop
        self.z_drop = drop
        self.plan_Q[:, 2] -= drop
        mujoco.mj_forward(self.m, d)
        self.z0 = float(d.qpos[2])
        mujoco.mj_subtreeVel(self.m, d)
        com = d.subtree_com[1]
        self.com_z_ref = float(com[2])
        self.x_ref = float(com[0])
        self.y_ref = float(com[1])
        self.y_ref0 = float(com[1])
        self.omega = float(np.sqrt(G / max(self.com_z_ref, 0.4)))
        self.phase_t = 0.0
        self.v_plan = float(dx / self.period) if self.period > 1e-6 else float(self.cruise)
        # --cruise scales the slice. 0.5 and 0.8 must not collapse to the same run.
        self.rate_nom = float(np.clip(self.cruise / max(self.v_plan, 0.2), 0.30, 1.35))
        self.rate = self.rate_nom
        d.qvel[:] *= self.rate_nom
        self.foot_off = np.zeros(3)
        self.yaw_off = 0.0
        self.yaw_int = 0.0
        self.swing_yaw = 0.0
        self.t_since = 0.0
        self.swing_lo = 0.0
        self._ds_u = 1.0
        self.freeze_swing = False
        self.gate_wait = None; self.gate_td = None; self.gate_lo = 0.0; self.gate_st = None
        self.e_xi = np.zeros(2)
        self.dcm_off = np.zeros(2)
        self._dcm_side = None
        self._hold_key = None
        self.contact_mode = 'ss'
        self.foot_tgt = None
        self.foot_tgt_on = False
        self.load_override = None
        self.g_dof = None
        self.plan_on = True
        self.phase = 'plan'
        self.s = 0.0
        self.q_ref = d.qpos.copy()
        self.q_seed = d.qpos.copy()
        for s in 'lr':
            p = d.xpos[self.foot[s]]
            R = d.xmat[self.foot[s]].reshape(3, 3)
            yaw = float(np.arctan2(R[1, 0], R[0, 0]))
            self.plant[s] = self._make_plant(np.array([p[0], p[1], SOLE]), yaw)
        self._precompute_plan_feet()
        self._cache_gravity(d.qpos)
        return dict(seam_err=err, period=self.period, dx=dx, z_drop=self.z_drop,
                    pelvis_z=self.z0, com_z=self.com_z_ref, x_origin=x0,
                    v_plan=self.v_plan, rate_nom=self.rate_nom, cruise=self.cruise)

    def _sample_plan(self):
        cycle = int(np.floor(self.phase_t / self.period))
        local = float(self.phase_t - cycle * self.period)
        u = local / self.plan_dt
        i = int(u)
        f = float(u - i)
        n = len(self.plan_Q) - 1
        if i >= n:
            i = n - 1
            f = 1.0
        q = (1.0 - f) * self.plan_Q[i] + f * self.plan_Q[i + 1]
        q = q.copy()
        q[0] += cycle * self.cycle_dx
        nq = np.linalg.norm(q[3:7])
        if nq > 0:
            q[3:7] /= nq
        v = (1.0 - f) * self.plan_V[i] + f * self.plan_V[i + 1]
        a = (self.plan_V[min(i + 1, n)] - self.plan_V[i]) / self.plan_dt
        al = (1.0 - f) * self.plan_AL[i] + f * self.plan_AL[i + 1]
        c = (1.0 - f) * self.plan_C[i] + f * self.plan_C[i + 1]
        c = c.copy()
        c[0] += cycle * self.cycle_dx
        cd = (self.plan_C[min(i + 1, n)] - self.plan_C[i]) / self.plan_dt
        # Time-scale the slice. Positions stay; speed follows --cruise.
        rate = float(getattr(self, 'rate', 1.0))
        v = v * rate
        a = a * (rate * rate)
        cd = cd * rate
        return q, v, a, al, c, cd

    def _sample_tau(self):
        local = float(self.phase_t - int(np.floor(self.phase_t / self.period)) * self.period)
        u = local / self.plan_dt
        i = int(u)
        f = float(u - i)
        n = len(self.plan_TAU) - 1
        if i >= n:
            i, f = n - 1, 1.0
        return (1.0 - f) * self.plan_TAU[i] + f * self.plan_TAU[i + 1]

    def _sample_contact(self):
        """Planned vertical force and sole CoP for the cruise slice."""
        local = float(self.phase_t - int(np.floor(self.phase_t / self.period)) * self.period)
        u = local / self.plan_dt
        i = int(u)
        f = float(u - i)
        n = len(self.plan_FZ) - 1
        if i >= n:
            i, f = n - 1, 1.0
        fz = (1.0 - f) * self.plan_FZ[i] + f * self.plan_FZ[i + 1]
        cop = np.zeros((2, 2))
        for s in range(2):
            a = self.plan_COP[i, s]
            b = self.plan_COP[min(i + 1, n), s]
            if np.isfinite(a[0]) and np.isfinite(b[0]):
                cop[s] = (1.0 - f) * a + f * b
            elif np.isfinite(a[0]):
                cop[s] = a
            elif np.isfinite(b[0]):
                cop[s] = b
            else:
                cop[s] = (0.06, 0.0)
        return fz, cop

    def _wrap(self, a):
        return float((a + np.pi) % (2.0 * np.pi) - np.pi)

    def _precompute_plan_feet(self):
        """Foot poses of the cruise slice, and each foot's swing window."""
        m = self.m
        dg = self.dg
        n = len(self.plan_Q)
        xy = np.zeros((n, 2, 2))
        yaw = np.zeros((n, 2))
        z = np.zeros((n, 2))
        for k in range(n):
            dg.qpos[:] = self.plan_Q[k]
            mujoco.mj_kinematics(m, dg)
            for si, s in enumerate('lr'):
                b = self.foot[s]
                p = dg.xpos[b]
                R = dg.xmat[b].reshape(3, 3)
                xy[k, si] = p[:2]
                z[k, si] = p[2]
                yaw[k, si] = np.arctan2(R[1, 0], R[0, 0])
        self.plan_fxy = xy
        self.plan_fyaw = yaw
        self.plan_fzht = z
        self.plan_down = z < (SOLE + 0.012)
        dt = self.plan_dt
        nfr = n - 1
        self.swing_iv = {}
        for si, s in enumerate('lr'):
            air = ~self.plan_down[:nfr, si]
            iv = []
            i = 0
            while i < nfr:
                if not air[i]:
                    i += 1
                    continue
                j = i
                while j < nfr and air[j]:
                    j += 1
                iv.append([i * dt, j * dt])
                i = j
            if len(iv) >= 2 and air[0] and air[-1]:
                lo = iv[-1][0]
                td = iv[0][1] + self.period
                iv = [[lo, td]] + iv[1:-1]
            self.swing_iv[s] = iv

    def _plan_foot_at(self, local, side, cycle):
        local = float(local % self.period)
        u = local / self.plan_dt
        i = int(u)
        f = float(u - i)
        n = len(self.plan_Q) - 1
        if i >= n:
            i, f = n - 1, 1.0
        si = 0 if side == 'l' else 1
        xy = (1.0 - f) * self.plan_fxy[i, si] + f * self.plan_fxy[min(i + 1, n), si]
        xy = np.array(xy, float)
        xy[0] += cycle * self.cycle_dx
        z = (1.0 - f) * self.plan_fzht[i, si] + f * self.plan_fzht[min(i + 1, n), si]
        yaw = (1.0 - f) * self.plan_fyaw[i, si] + f * self.plan_fyaw[min(i + 1, n), si]
        return np.array([xy[0], xy[1], float(z)]), float(yaw)

    def _event_pose(self, t_ev, local, cycle, side):
        """Plan foot pose at a swing edge. t_ev may sit past the seam."""
        if t_ev >= self.period:
            local_ev = t_ev - self.period
            cyc = cycle if local <= local_ev else cycle + 1
            return self._plan_foot_at(local_ev, side, cyc)
        if local + 1e-9 < t_ev and (t_ev - local) > 0.5 * self.period:
            return self._plan_foot_at(t_ev, side, cycle - 1)
        return self._plan_foot_at(t_ev, side, cycle)

    def _swing_at(self, local):
        for s, ivs in self.swing_iv.items():
            for lo, td in ivs:
                t = local
                if td > self.period and t < (td - self.period):
                    t = t + self.period
                if lo <= t < td:
                    dur = max(td - lo, 1e-3)
                    return s, float((t - lo) / dur), float(t - lo), float(td - t), float(dur), float(lo), float(td)
        return None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    def _sole_xy(self, ankle_xy, yaw):
        return np.asarray(ankle_xy, float) + FC * np.array([np.cos(yaw), np.sin(yaw)])

    def _cache_gravity(self, q):
        m = self.m
        dg = self.dg
        flags = m.opt.disableflags
        m.opt.disableflags = flags | int(mujoco.mjtDisableBit.mjDSBL_CONTACT
                                          | mujoco.mjtDisableBit.mjDSBL_LIMIT
                                          | mujoco.mjtDisableBit.mjDSBL_FRICTIONLOSS)
        try:
            dg.qpos[:] = q
            dg.qvel[:] = 0.0
            dg.qacc[:] = 0.0
            mujoco.mj_inverse(m, dg)
            self.g_dof = dg.qfrc_inverse.copy()
        finally:
            m.opt.disableflags = flags

    def _quat_yaw(self, q):
        w, x, y, z = q[3:7]
        return float(np.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z)))

    def _q_at(self, local):
        """Cruise-slice qpos at a phase in [0, period). Joint angles only."""
        local = float(local % self.period) if self.period else 0.0
        u = local / self.plan_dt
        n = len(self.plan_Q) - 1
        i = int(u)
        if i >= n:
            i, f = n - 1, 1.0
        else:
            f = float(u - i)
        return (1.0 - f) * self.plan_Q[i] + f * self.plan_Q[i + 1]

    def _plan_mpc(self, d):
        """100 Hz closed loop on the cruise slice.

        Sagittal and lateral foot placement follow the DCM (capture point)
        predicted to touchdown. Step timing is a bounded playback-rate change
        around rate_nom = cruise / v_plan. yaw_off integrates heading and
        stance-foot yaw error; the swing foot lands at that yaw and the stance
        hip yaw servo uses the same offset.
        """
        q_ref, v_ref, _, al, c_ref, cd_ref = self._sample_plan()
        self._cache_gravity(q_ref)
        mujoco.mj_subtreeVel(self.m, d)
        com = d.subtree_com[1]
        cd = d.subtree_linvel[1]
        cycle = int(np.floor(self.phase_t / self.period)) if self.period > 0 else 0
        local = float(self.phase_t - cycle * self.period)
        # Foot to step with is the unloaded leg in the slice (same test the
        # open-loop cruise used). The geometric window is only the double
        # support pads; those two disagree for ~70 ms at each transition.
        geo, s_ph, t_since, t_to, dur, lo, td = self._swing_at(local)
        swing = None
        if al[0] < 0.15 <= al[1]:
            swing = 'l'
        elif al[1] < 0.15 <= al[0]:
            swing = 'r'
        self._plan_al = al
        self.swing = swing

        # --- yaw_off: heading and stance-foot slip ---
        # Proportional to the heading error, with a small leaky integral.
        # Swing-foot yaw is 0.30 * yaw_off, which is the gain the slice was
        # tracked with. A saturated offset held for the whole step yawed the
        # pelvis through the stance foot.
        Rp = d.xmat[self.pelvis].reshape(3, 3)
        yaw_m = float(np.arctan2(Rp[1, 0], Rp[0, 0]))
        yaw_r = self._quat_yaw(q_ref)
        ey = self._wrap(yaw_r - yaw_m)
        stance = None if swing is None else ('r' if swing == 'l' else 'l')
        fy = 0.0
        if stance is not None:
            R_st = d.xmat[self.foot[stance]].reshape(3, 3)
            yaw_st = float(np.arctan2(R_st[1, 0], R_st[0, 0]))
            _, yaw_pl = self._plan_foot_at(local, stance, cycle)
            fy = self._wrap(yaw_pl - yaw_st)
        self.yaw_int = float(np.clip(0.98 * self.yaw_int + ey * 0.001, -0.03, 0.03))
        self.yaw_off = float(np.clip(ey + 0.20 * fy + 0.30 * self.yaw_int, -0.15, 0.15))
        self.swing_yaw = float(np.clip(0.30 * self.yaw_off, -0.08, 0.08))

        # --- DCM foot placement and step timing ---
        # Reference velocity is the slice at rate_nom. The timing trim (self.rate)
        # must not look like a speed error, or the step chases its own clock.
        omega = max(self.omega, 1.0)
        xi = com[:2] + cd[:2] / omega
        v_nom = cd_ref[:2] * (self.rate_nom / max(self.rate, 0.25))
        xi_p = c_ref[:2] + v_nom / omega
        e_xi = (xi - xi_p) + np.array([
            0.12 * (float(cd[0]) - self.cruise),
            0.0,
        ])
        self.foot_tgt_on = False
        self.load_override = None
        self.foot_off[:] = 0.0
        self.t_since = float(t_since)
        self.swing_lo = float(lo)
        # Double support pads follow the geometric trail foot, and only while
        # that foot is the one the slice has unloaded.
        mode = 'ds' if swing is None else 'swing'
        if swing is not None:
            if swing != self._dcm_side:
                self._dcm_side = swing
                self.dcm_off[:] = 0.0
            # ±4 cm at 4 mm/tick. 8 cm on this sole rolled it onto two
            # contacts and the walk ended sooner. Push recovery uses the
            # timing term below once the error is past 10 cm.
            ay = abs(float(e_xi[1]))
            lat = float(np.clip(0.45 * float(e_xi[1]), -0.040, 0.040))
            lat_step = 0.004
            # Lengthen when the DCM is ahead of the plan. Shortening this
            # torque tracker ran away, so a slow COM is not stepped shorter.
            sag = float(np.clip(0.20 * max(0.0, float(e_xi[0]) - 0.03), 0.0, 0.030))
            self.dcm_off[1] += float(np.clip(lat - self.dcm_off[1], -lat_step, lat_step))
            self.dcm_off[0] += float(np.clip(sag - self.dcm_off[0], -0.0015, 0.0015))
            pad = geo == swing
            fz_sw = self._measured_fz(d, swing)
            # The slice drops this foot's load ~70 ms before the sole leaves.
            # Freeze it while it is still carrying weight so the other foot
            # can land. That gap was the airborne bounce.
            self.freeze_swing = (not pad) and fz_sw > 50.0
            if pad and (s_ph > 0.45 and fz_sw > 60.0 or t_to < DS_PAD_TD):
                mode = 'landing'
            elif self.freeze_swing or (pad and t_since < DS_PAD_LO):
                mode = 'ds_hold'
            else:
                mode = 'swing'
            # A few percent only. Speeding the slice to 1.10 pitched the
            # robot once the foot was already on its edge. Do not slow it.
            hurry = 0.0
            if float(e_xi[0]) > 0.06:
                hurry += 0.15 * (float(e_xi[0]) - 0.06)
            if ay > 0.10:
                hurry += 0.08 * min(ay - 0.10, 0.15)
            self.rate = float(np.clip(
                self.rate_nom * (1.0 + hurry), self.rate_nom * 0.98, self.rate_nom * 1.03))
            self.e_xi = np.array(e_xi, float)
            self.foot_off[0] = float(self.dcm_off[0])
            self.foot_off[1] = float(self.dcm_off[1])
            self.foot_off[2] = 0.0
            self.foot_tgt_on = False
        else:
            self.rate = float(self.rate_nom)
            self.dcm_off *= 0.8
            self.freeze_swing = False
        # --- r7 touchdown gate (WBC_GATE=1): hold the stance load until the
        # landing foot is actually down (fz > GATE_TD), slow the clock while
        # waiting, ramp the hold off after touchdown, release on timeout.
        self.gate_lo = 0.0
        if GATE:
            t = float(d.time)
            land = getattr(self, '_dcm_side', None)
            if land is not None and swing is None:
                st = 'r' if land == 'l' else 'l'
                li = 0 if land == 'l' else 1
                fz_l = self._measured_fz(d, land)
                if self.gate_wait is None and al[li] > 0.15 and fz_l < GATE_TD and self.gate_td is None:
                    self.gate_wait = t
                if self.gate_wait is not None:
                    if fz_l >= GATE_TD or t - self.gate_wait > GATE_TO:
                        self.gate_wait = None; self.gate_td = t
                    else:
                        self.rate = float(self.rate_nom) * GATE_RATE
                        self.gate_lo = GATE_HOLD * self.mg; self.gate_st = st
                if self.gate_td is not None:
                    r_ = (t - self.gate_td) / GATE_RAMP
                    if r_ < 1.0:
                        self.gate_lo = GATE_HOLD * self.mg * (1.0 - r_); self.gate_st = st
            elif swing is not None:
                self.gate_wait = None; self.gate_td = None
        self.contact_mode = mode
        self.phase = 'ds' if mode in ('ds', 'ds_hold', 'landing') else 'ss'
        self.dbg_line = (f'rate={self.rate:.2f} {mode:8} off=({self.foot_off[0]:+.3f},'
                         f'{self.foot_off[1]:+.3f},{self.foot_off[2]:+.3f}) yaw={self.yaw_off:+.3f} '
                         f'exi=({float(e_xi[0]):+.3f},{float(e_xi[1]):+.3f})')

    def _ref_acc(self, ds, v_ref, a_ref, bodies):
        """J a + Jdot v for each body and the COM, evaluated on the reference state."""
        m = self.m
        nv = self.nv

        def jacs(data):
            out = {}
            for b in bodies:
                jp = np.zeros((3, nv))
                jr = np.zeros((3, nv))
                mujoco.mj_jacBody(m, data, jp, jr, b)
                out[b] = (jp, jr)
            Jc = np.zeros((3, nv))
            mujoco.mj_jacSubtreeCom(m, data, Jc, self.pelvis)
            out['com'] = Jc
            return out

        J0 = jacs(ds)
        q_save = ds.qpos.copy()
        eps = 1e-4
        mujoco.mj_integratePos(m, ds.qpos, v_ref, eps)
        mujoco.mj_kinematics(m, ds)
        mujoco.mj_comPos(m, ds)
        J1 = jacs(ds)
        ds.qpos[:] = q_save
        mujoco.mj_kinematics(m, ds)
        mujoco.mj_comPos(m, ds)
        acc = {}
        for b in bodies:
            jp, jr = J0[b]
            jp2, jr2 = J1[b]
            acc[b] = (jp @ a_ref + (jp2 - jp) @ v_ref / eps,
                      jr @ a_ref + (jr2 - jr) @ v_ref / eps)
        Jc = J0['com']
        acc['com'] = Jc @ a_ref + (J1['com'] - Jc) @ v_ref / eps
        return acc

    def _ik_swing(self, q_ref, v_ref, swing):
        """Move the swing-leg joints so that foot hits the MPC target.

        Returns the position command and a velocity command whose swing-leg
        part matches a held or speed-limited foot. The plan feedforward is
        left for the caller to scale down when this correction is large.
        """
        q = q_ref.copy()
        v = np.array(v_ref, float, copy=True)
        if (not self.foot_tgt_on) or swing is None or self.foot_tgt is None:
            return q, v
        m = self.m
        nv = self.nv
        dg = self.dg
        cols = [int(self.va[swing + j]) for j in LEG]
        qas = [int(self.qa[swing + j]) for j in LEG]
        body = self.foot[swing]
        tgt = np.asarray(self.foot_tgt, float)
        yaw_des = float(self.foot_tgt_yaw)
        for _ in range(3):
            dg.qpos[:] = q
            mujoco.mj_kinematics(m, dg)
            p = dg.xpos[body]
            R = dg.xmat[body].reshape(3, 3)
            yaw = float(np.arctan2(R[1, 0], R[0, 0]))
            err = np.zeros(4)
            err[:3] = tgt - p
            err[3] = self._wrap(yaw_des - yaw)
            if float(np.linalg.norm(err)) < 2e-3:
                break
            jp = np.zeros((3, nv))
            jr = np.zeros((3, nv))
            mujoco.mj_jacBody(m, dg, jp, jr, body)
            J = np.vstack([jp[:, cols], jr[2:3, cols]])
            W = np.diag([1.0, 1.0, 1.2, 0.20])
            H = J.T @ W @ J + 2e-3 * np.eye(6)
            dq = np.linalg.solve(H, J.T @ (W @ err))
            dq = np.clip(dq, -0.12, 0.12)
            for n_i, qa in enumerate(qas):
                dof = cols[n_i]
                q[qa] = float(np.clip(q[qa] + dq[n_i], self.qmin[dof] + 0.01, self.qmax[dof] - 0.01))
        mode = self.contact_mode
        dg.qpos[:] = q
        mujoco.mj_kinematics(m, dg)
        jp = np.zeros((3, nv))
        mujoco.mj_jacBody(m, dg, jp, np.zeros((3, nv)), body)
        z = float(dg.xpos[body][2])
        shape_v = mode == 'ds_hold' or (mode in ('landing', 'swing') and z < SOLE + 0.06)
        if shape_v:
            v_other = v.copy()
            for c in cols:
                v_other[c] = 0.0
            v_base = jp @ v_other
            if mode == 'ds_hold':
                v_des = np.zeros(3)
            else:
                v_des = jp @ v
                clear = max(0.0, z - SOLE)
                vz_cap = -0.08 - 0.70 * float(np.clip(clear / 0.06, 0.0, 1.0))
                if v_des[2] < vz_cap:
                    v_des[2] = vz_cap
            Jv = jp[:, cols]
            dv = np.linalg.solve(Jv @ Jv.T + 1e-3 * np.eye(3), v_des - v_base)
            v_sw = np.clip(Jv.T @ dv, -8.0, 8.0)
            for n_i, c in enumerate(cols):
                v[c] = float(v_sw[n_i])
        return q, v

    def _wbc_plan(self, d):
        """1 kHz QP: track the planned motion, with cone, torque, and speed limits."""
        import time
        t0 = time.perf_counter()
        m = self.m
        nv, nu = self.nv, self.nu
        nw = 12
        n = nv + nw
        q_ref, v_ref, a_ref, al, c_ref, cd_ref = self._sample_plan()
        M, h = self._bias_mass(d)
        ds = self.ds
        ds.qpos[:] = q_ref
        ds.qvel[:] = v_ref
        mujoco.mj_kinematics(m, ds)
        mujoco.mj_comPos(m, ds)
        mujoco.mj_subtreeVel(m, d)
        mujoco.mj_subtreeVel(m, ds)
        c_ref3 = ds.subtree_com[1].copy()
        cd_ref3 = ds.subtree_linvel[1].copy()
        Jcom = self._com_jac(d)
        feet = {}
        for s in 'lr':
            p, R, v, w, jp, jr = self._body(d, self.foot[s])
            feet[s] = dict(p=p, R=R, v=v, w=w, jp=jp, jr=jr, fz=self._measured_fz(d, s))
        Jw = np.zeros((nv, nw))
        for i, s in enumerate('lr'):
            R = feet[s]['R']
            Jw[:, 6 * i:6 * i + 3] = feet[s]['jp'].T @ R
            Jw[:, 6 * i + 3:6 * i + 6] = feet[s]['jr'].T @ R
        P = np.eye(n) * 1e-6
        qv = np.zeros(n)

        def add_task(J, rhs, w):
            ww = np.asarray(w, float)
            if np.ndim(ww):
                JW = J * ww[:, None]
                P[:nv, :nv] += J.T @ JW
                qv[:nv] += -(J.T @ (ww * rhs))
            else:
                P[:nv, :nv] += ww * (J.T @ J)
                qv[:nv] += -ww * (J.T @ rhs)

        com = d.subtree_com[1]
        cd = d.subtree_linvel[1]
        # Centroidal linear momentum, light on purpose: the torque objective
        # is what keeps the cruise slice up, and a stiff COM task pitches it.
        pd_c = np.array([
            8.0 * (c_ref3[0] - com[0]) + 3.0 * (cd_ref3[0] - cd[0]),
            10.0 * (c_ref3[1] - com[1]) + 3.0 * (cd_ref3[1] - cd[1]),
            40.0 * (c_ref3[2] - com[2]) + 8.0 * (cd_ref3[2] - cd[2]),
        ])
        pd_c = np.clip(pd_c, [-3.0, -3.0, -8.0], [3.0, 3.0, 8.0])
        self.a_des = pd_c
        add_task(Jcom, pd_c, np.array([0.02, 0.02, 0.05]))
        Rp = d.xmat[self.pelvis].reshape(3, 3)
        Rr = ds.xmat[self.pelvis].reshape(3, 3)
        er = rotvec(Rr, Rp)
        jr_p = np.zeros((3, nv))
        mujoco.mj_jacBody(m, d, np.zeros((3, nv)), jr_p, self.pelvis)
        add_task(jr_p, 20.0 * er, np.array([0.01, 0.01, 0.005]))
        yaw = float(np.arctan2(Rp[1, 0], Rp[0, 0]))
        yaw_r = float(np.arctan2(Rr[1, 0], Rr[0, 0]))
        ey = (yaw_r - yaw + np.pi) % (2.0 * np.pi) - np.pi
        swing = self.swing
        mode = self.contact_mode
        q_cmd = q_ref.copy()
        # DCM shift of the swing foot. XY only; yaw is the hip_yaw joint below
        # so a heading correction does not drag the sole sideways.
        if swing is not None and float(np.linalg.norm(self.foot_off[:2])) > 1e-4:
            jp_s = np.zeros((3, nv))
            mujoco.mj_jacBody(m, ds, jp_s, None, self.foot[swing])
            cols = [int(self.va[swing + j]) for j in LEG]
            Jxy = jp_s[:2, cols]
            reach = 0.22
            dq = np.linalg.solve(Jxy @ Jxy.T + 1e-4 * np.eye(2), self.foot_off[:2])
            dq = np.clip(Jxy.T @ dq, -reach, reach)
            for n_i, jn in enumerate(LEG):
                dof = cols[n_i]
                qa = int(self.qa[swing + jn])
                q_cmd[qa] = float(np.clip(q_cmd[qa] + dq[n_i], self.qmin[dof] + 0.01, self.qmax[dof] - 0.01))
        if swing is not None:
            # Swing-foot yaw follows yaw_off. Negative hip yaw on this model
            # swings the foot the way the stance-yaw servo wants.
            dof = int(self.va[swing + 'hip_yaw'])
            qa = int(self.qa[swing + 'hip_yaw'])
            q_cmd[qa] = float(np.clip(q_cmd[qa] - self.swing_yaw,
                                       self.qmin[dof] + 0.01, self.qmax[dof] - 0.01))
        # Keep the trail foot at the liftoff pose, then blend back onto the
        # slice so the release is continuous. This is the extra double support.
        if swing is not None and mode == 'ds_hold' and self.freeze_swing:
            # Sole is still carrying load after the slice let go of it.
            # Hold the measured leg pose; do not play the liftoff.
            for jn in LEG:
                dof = int(self.va[swing + jn])
                qa = int(self.qa[swing + jn])
                q_cmd[qa] = float(d.qpos[qa])
                v_ref[dof] = 0.0
            self._ds_u = 0.0
        elif swing is not None and mode == 'ds_hold':
            u_ds = float(np.clip(self.t_since / max(DS_PAD_LO, 1e-3), 0.0, 1.0))
            # Pose from before the plan's liftoff, while that foot was loaded.
            q_lo = self._q_at(self.swing_lo - 0.060)
            for jn in LEG:
                dof = int(self.va[swing + jn])
                qa = int(self.qa[swing + jn])
                q_cmd[qa] = float(np.clip(
                    (1.0 - u_ds) * float(q_lo[qa]) + u_ds * q_cmd[qa],
                    self.qmin[dof] + 0.01, self.qmax[dof] - 0.01))
                v_ref[dof] *= u_ds
            self._ds_u = u_ds
        else:
            self._ds_u = 1.0
        # Bleed a fast swing-down, hold the trail foot, resist a bounce.
        for s in 'lr':
            z = float(feet[s]['p'][2])
            vz = float(feet[s]['v'][2])
            clear = z - SOLE
            if mode == 'ds_hold' and s == swing and clear < 0.025:
                add_task(feet[s]['jp'][2:3], np.array([36.0 * (SOLE - z) - 8.0 * vz]), 3.0)
            elif s == swing and mode == 'landing' and 0.0 < clear < 0.08:
                # Put the foot down before the stance foot has left, then bleed
                # the last centimetre so the landing does not bounce both soles off.
                vz_des = -0.18 if clear > 0.025 else -0.05
                add_task(feet[s]['jp'][2:3], np.array([14.0 * (vz_des - vz)]), 5.0)
            elif s == swing and 0.0 < clear < 0.05 and vz < -0.20:
                vz_des = -0.08 - 0.50 * float(np.clip(clear / 0.05, 0.0, 1.0))
                add_task(feet[s]['jp'][2:3], np.array([10.0 * (vz_des - vz)]), 2.5)
            if feet[s]['fz'] > 40.0 and vz > 0.10 and s != swing:
                add_task(feet[s]['jp'][2:3], np.array([-22.0 * vz]), 4.0)
        tff = self._sample_tau()
        g = self.g_dof
        # Cruise scales the slice. Stance feedforward stays on that scale.
        # The swing leg is slowed with the liftoff/landing pace so the trail
        # foot is not yanked up during the extra double support.
        s2 = float(self.rate_nom) ** 2
        ds_u = float(getattr(self, '_ds_u', 1.0))
        tau_des = np.zeros(nu)
        for i in range(nu):
            dof = int(self.act_va[i])
            qa_i = int(self.act_qa[i])
            raw = float(tff[dof])
            if g is None:
                ff = raw
            else:
                ff = float(g[dof] + s2 * (raw - g[dof]))
                # Don't yank the trail foot up while it is being held down.
                if (swing is not None and ds_u < 0.98
                        and self.act_name[i].startswith(swing + '_')):
                    ff = float(g[dof] + (ds_u ** 2) * s2 * (raw - g[dof]))
            tau_des[i] = (ff
                          + self.pd_kp[i] * (q_cmd[qa_i] - d.qpos[qa_i])
                          + self.pd_kd[i] * (v_ref[dof] - d.qvel[dof]))
        ep = float(np.arctan2(-Rr[2, 0], np.hypot(Rr[2, 1], Rr[2, 2]))
                   - np.arctan2(-Rp[2, 0], np.hypot(Rp[2, 1], Rp[2, 2])))
        wp = d.qvel[3:6]
        wrv = v_ref[3:6]
        for si, s in enumerate('lr'):
            if al[si] < 0.2:
                continue
            i_ap = self.act_name.index(f'{s}_ankle_pitch')
            i_hp = self.act_name.index(f'{s}_hip_pitch')
            i_hy = self.act_name.index(f'{s}_hip_yaw')
            # Measured on this model, both legs: negative hip/ankle pitch torque
            # raises the nose; negative hip yaw torque increases pelvis yaw.
            # Yaw is clipped to 14 Nm. The sole cone only allows |Mz| <= 0.05 Fz
            # (~20 Nm at half body weight), and a larger command rolls the foot.
            wy_e = float(wp[1] - wrv[1])
            wz_e = float(wp[2] - wrv[2])
            tau_des[i_ap] += al[si] * float(np.clip(-220.0 * ep + 25.0 * wy_e, -28.0, 28.0))
            tau_des[i_hp] += al[si] * float(np.clip(-520.0 * ep + 40.0 * wy_e, -55.0, 55.0))
            # Half the old ±22 Nm. That moment was the whole yaw couple the
            # cone allows, so the CoP had nothing left and the foot rolled.
            tau_des[i_hy] += al[si] * float(np.clip(-160.0 * self.yaw_off + 10.0 * wz_e, -12.0, 12.0))
        # tau = (M qacc + h - J^T w) on each actuator. Track tau_des.
        tw = 2.0
        for i in range(nu):
            dof = int(self.act_va[i])
            row = np.zeros(n)
            row[:nv] = M[dof]
            row[nv:] = -Jw[dof]
            rhs = float(tau_des[i] * self.gear[i] - h[dof])
            P += tw * np.outer(row, row)
            qv += -tw * rhs * row
        if self.load_override is not None:
            alphas = np.asarray(self.load_override, float)
        else:
            alphas = np.asarray(al, float)
        if float(alphas.sum()) > 1e-6:
            alphas = alphas / alphas.sum()
        else:
            alphas = np.array([0.5, 0.5])
        fz_ref, cop_ref = self._sample_contact()
        fz_ref = np.array(fz_ref, float, copy=True)
        # Share weight with a trail foot that is still on the ground, and with
        # a swing foot that has touched down early. The plan's force is ~0
        # there, which is why realized double support was 3.3%.
        if swing is not None and mode in ('ds_hold', 'landing'):
            on_ground = (feet[swing]['fz'] > 30.0
                         or float(feet[swing]['p'][2]) < SOLE + 0.006)
            if on_ground:
                share = 0.45 if mode == 'ds_hold' else 0.40
                si = 0 if swing == 'l' else 1
                fz_ref[si] = share * self.mg
                fz_ref[1 - si] = (1.0 - share) * self.mg
                cop_ref = np.array(cop_ref, float, copy=True)
                cop_ref[si] = (0.06, 0.0)
        for i, s in enumerate('lr'):
            o = nv + 6 * i
            if self.load_override is not None:
                fz_r = float(max(alphas[i], 0.0) * self.mg)
            else:
                fz_r = float(max(fz_ref[i], 0.0))
            cx, cy = float(cop_ref[i, 0]), float(cop_ref[i, 1])
            cx = float(np.clip(cx, HEEL, TOE))
            cy = float(np.clip(cy, -HALFW, HALFW))
            # My = -cop_x Fz, Mx = cop_y Fz with Fx = Fy = 0.
            ref = np.array([0.0, 0.0, fz_r, cy * fz_r, -cx * fz_r, 0.0])
            reg = np.array([2e-3, 2e-3, 5e-2, 4e-3, 4e-3, 8e-3])
            P[o:o + 6, o:o + 6] += np.diag(reg)
            qv[o:o + 6] += -reg * ref
            self.fz[s] = 0.0
        rows, lo, hi = [], [], []

        def add_row(coeff, l, u):
            rows.append(coeff)
            lo.append(l)
            hi.append(u)

        for r in range(6):
            coeff = np.zeros(n)
            coeff[:nv] = M[r]
            coeff[nv:] = -Jw[r]
            add_row(coeff, -h[r], -h[r])
        for i in range(nu):
            dof = int(self.act_va[i])
            coeff = np.zeros(n)
            coeff[:nv] = M[dof]
            coeff[nv:] = -Jw[dof]
            lim = self.tau_max[i]
            add_row(coeff, -lim - h[dof], lim - h[dof])
        for i, s in enumerate('lr'):
            _cm = float(_os.environ.get('WBC_COP_M', '0'))   # r7: QP CoP margin inside the sole (m)
            G = foot_cone(HEEL + _cm, TOE - _cm, HALFW - _cm, MU, YAW_MZ)
            # A wrench is a real contact force. Zero it when the foot is in the
            # air, including a planned stance foot that has not landed yet.
            ankle_z = float(feet[s]['p'][2])
            near = ankle_z < SOLE + 0.008 or feet[s]['fz'] > 40.0
            # ds_hold / landing keep a wrench on a foot that is actually down.
            swing_air = s == swing and not (mode in ('ds_hold', 'landing') and near)
            airborne = feet[s]['fz'] < 30.0 and (
                swing_air or (s != swing and ankle_z > SOLE + 0.015))
            for r in range(G.shape[0]):
                coeff = np.zeros(n)
                coeff[nv + 6 * i:nv + 6 * i + 6] = G[r]
                if airborne:
                    add_row(coeff, 0.0, 0.0 if r == 0 else 1e6)
                elif r == 0:
                    lo_fz = 15.0 if (s != swing and alphas[i] > 0.15) else 0.0
                    if GATE and self.gate_lo > 0 and s == self.gate_st:
                        lo_fz = max(lo_fz, float(self.gate_lo))
                    add_row(coeff, lo_fz, 1.55 * self.mg)
                else:
                    add_row(coeff, 0.0, 1e6)
        dt = self.dt
        for dof in range(nv):
            coeff = np.zeros(n)
            coeff[dof] = 1.0
            if dof < 6:
                add_row(coeff, -1e4, 1e4)
                continue
            v = d.qvel[dof]
            lo_v = (-self.vmax[dof] - v) / dt
            hi_v = (self.vmax[dof] - v) / dt
            qadr = dof + 1
            q = d.qpos[qadr] if qadr < m.nq else 0.0
            lo_p = 2 * (self.qmin[dof] - q - v * dt) / dt ** 2
            hi_p = 2 * (self.qmax[dof] - q - v * dt) / dt ** 2
            lo_b = max(lo_v, lo_p)
            hi_b = min(hi_v, hi_p)
            cap = 800.0
            if lo_b > hi_b:
                lo_b, hi_b = -cap, cap
            lo_c = float(np.clip(lo_b, -cap, cap))
            hi_c = float(np.clip(hi_b, -cap, cap))
            if lo_c > hi_c:
                pin = cap if lo_b > 0.0 else -cap
                lo_c = hi_c = pin
            add_row(coeff, lo_c, hi_c)
        A = np.vstack(rows)
        x = self._solve(P, qv, A, np.asarray(lo, float), np.asarray(hi, float))
        self.last_ms = (time.perf_counter() - t0) * 1e3
        if x is None:
            self.qp_fail += 1
            if not self.last_status:
                self.last_status = 'fail'
        else:
            self.qp_ok += 1
            qacc = x[:nv]
            w = x[nv:]
            self.last_base_res = float(np.linalg.norm(M[:6] @ qacc + h[:6] - Jw[:6] @ w))
            tau_dof = M @ qacc + h - Jw @ w
            tau = np.zeros(nu)
            for i in range(nu):
                tau[i] = tau_dof[self.act_va[i]] / max(self.gear[i], 1e-8)
            self.last_tau = self._waist_zone(d, np.clip(tau, -self.tau_max, self.tau_max))
            self.last_status = 'ok'
            self.x_prev = x
            for i, s in enumerate('lr'):
                self.fz[s] = float(w[6 * i + 2])
        d.ctrl[:] = self.last_tau

    def step(self, d):
        if getattr(self, 'plan_on', False):
            if self.k % 10 == 0:
                self._plan_mpc(d)
            self._wbc_plan(d)
            self.phase_t += self.dt * getattr(self, 'rate', 1.0)
            self.s = float((self.phase_t % self.period) / self.period)
            self.k += 1
            return
        if self.k % 10 == 0 and self.phase != 'balance':
            self._mpc(d)
            self._ik(d)
        elif self.k % 10 == 0:
            self._ik(d)
        self._wbc(d)
        self._advance(d)
        if self.landings and self.landings[-1]['t'] is None:
            self.landings[-1]['t'] = float(d.time)
        self.k += 1


    def _measured_wrench(self, d, side):
        """Contact wrench on one foot about the ankle, in the foot frame."""
        gid = self.foot_geom[side]
        ankle = d.xpos[self.foot[side]]
        R = d.xmat[self.foot[side]].reshape(3, 3)
        f = np.zeros(3)
        moment = np.zeros(3)
        for i in range(d.ncon):
            fi = _contact_force_on(self.m, d, i, gid)
            if fi is None:
                continue
            f += fi
            moment += np.cross(d.contact[i].pos - ankle, fi)
        return np.concatenate([R.T @ f, R.T @ moment])


def _contact_force_on(m, d, i, geom_id):
    """Force (N) applied to geom_id by contact i, world frame.

    mj_contactForce's normal is the +compression axis. For this model the
    reconstructed vector fr·frame is the force on geom2 (the foot, when geom1
    is the floor): summing it over a quiet stance matches body weight.
    """
    c = d.contact[i]
    if geom_id not in (c.geom1, c.geom2):
        return None
    fr = np.zeros(6)
    mujoco.mj_contactForce(m, d, i, fr)
    f = fr[0] * c.frame[0:3] + fr[1] * c.frame[3:6] + fr[2] * c.frame[6:9]
    if c.geom2 == geom_id:
        return f
    return -f


def osqp_setup(P, q, A, l, u):
    import osqp
    prob = osqp.OSQP()
    prob.setup(P, q, A, l, u, verbose=False, eps_abs=1e-4, eps_rel=1e-4,
               max_iter=200, polishing=False, warm_starting=True, check_termination=8)
    return prob


def measured_cop(m, d, foot_geom):
    """Pressure-weighted CoP in world, and total +z force, for one foot geom."""
    fz = 0.0
    cop = np.zeros(3)
    for i in range(d.ncon):
        f = _contact_force_on(m, d, i, foot_geom)
        if f is None or f[2] <= 1.0:
            continue
        fz += f[2]
        cop += f[2] * d.contact[i].pos
    if fz <= 1.0:
        return None, 0.0
    return cop / fz, fz


def cop_margin_mm(cop_w, ankle, R):
    """Clearance of a world CoP to the sole rectangle, mm. Negative is outside."""
    local = R.T @ (cop_w - ankle)
    mx = min(local[0] - HEEL, TOE - local[0])
    my = min(HALFW + local[1], HALFW - local[1])
    return float(min(mx, my) * 1000.0), local[:2].copy()
