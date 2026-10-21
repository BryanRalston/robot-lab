"""MJX walking env for the v3 humanoid.

PD torques at 50 Hz on top of the phase-indexed r7 gait. The policy action is a
tanh residual in [-1, 1], scaled per joint. Brax's autoreset keeps the first
reset's physics state and does not restore info, so a fall writes the initial
command, phase and PD memory back into info before returning.
"""
from hip_stop_l90 import hip_stop_l90, clip_hip_l90, TERM_RAD as HIP_STOP_TERM
import os

import jax
import jax.numpy as jp
import mujoco
import numpy as np
from ml_collections import config_dict
from mujoco import mjx
from mujoco.mjx._src import math

from mujoco_playground._src import mjx_env

HERE = os.path.dirname(os.path.abspath(__file__))


def default_config() -> config_dict.ConfigDict:
    return config_dict.create(
        ctrl_dt=0.02,
        sim_dt=0.002,
        impl='jax',
        integrator='implicitfast',
        iterations=4,
        ls_iterations=8,
        naconmax=80,
        njmax=256,
        noise_level=1.0,
        vx_range=[0.4, 1.05],
        vy_range=[-0.25, 0.25],
        yaw_range=[-0.5, 0.5],
        stand_prob=0.08,
        gait_init_prob=0.85,
        push_enable=False,
        push_force_range=[50.0, 150.0],
        # Fraction of pushes that are the eval impulse: 300 N for 0.2 s.
        push_gate_prob=0.0,
        ref_weight=1.0,
        resample_steps=500,
        dr_gains=True,
        # J10 (RETRAIN_PLAN_J10.md). heading_obs appends sin/cos of the heading error (obs 109).
        heading_obs=False,
        tracking_sigma=0.25,
        heading_sigma=0.1,
        leg_action_mult=1.0,
        knee_cont_nm=76.9,
        # CONTRACTS R1.2 knee avail peak 258 N·m worst-angle (2x TBM2G-07613D + 2x RV12x4).
        # The PD clip is tau_lim*strength, and strength DR reaches 1.10, so training can exceed it.
        knee_peak_nm=258.0,
        reward_scales=config_dict.create(
            tracking_lin=2.0,
            tracking_ang=0.8,
            upright=0.5,
            height=0.4,
            ref_pose=1.0,
            contact=0.4,
            air_time=1.5,
            no_flight=1.0,
            torque=0.05,
            action_rate=0.1,
            vel_limit=0.15,
            joint_limit=0.8,
            alive=0.8,
            heading=0.0,
            knee_thermal=0.0,
            knee_peak=0.0,
        ),
    )


def obs_layout(heading_obs=False):
    """Policy observation, 107 numbers (109 with heading_obs). Privileged adds extras."""
    names = []
    names += [f'linvel_{c}' for c in 'xyz']
    names += [f'gyro_{c}' for c in 'xyz']
    names += [f'gravity_{c}' for c in 'xyz']
    names += ['cmd_vx', 'cmd_vy', 'cmd_yaw']
    names += ['payload_frac']
    names += [f'q_{i}' for i in range(30)]
    names += [f'qd_{i}' for i in range(30)]
    names += [f'last_act_{i}' for i in range(30)]
    names += ['phase_sin', 'phase_cos', 'phase_sin_swap', 'phase_cos_swap']
    if heading_obs:
        names += ['heading_err_sin', 'heading_err_cos']
    priv = list(names)
    priv += ['pelvis_z']
    priv += [f'tau_frac_{i}' for i in range(30)]
    priv += ['fz_l', 'fz_r', 'contact_l', 'contact_r', 'air_l', 'air_r']
    priv += ['strength', 'kp_scale', 'latency_frac']
    return names, priv


class HumanoidWalk(mjx_env.MjxEnv):
    def __init__(self, xml_path=None, config=None, config_overrides=None):
        super().__init__(config or default_config(), config_overrides)
        xml_path = xml_path or os.path.join(HERE, 'humanoid_mjx.xml')
        self._xml_path = xml_path
        self._mj_model = mujoco.MjModel.from_xml_path(xml_path)
        self._mj_model.opt.timestep = self.sim_dt
        integrator = str(self._config.integrator)
        self._mj_model.opt.integrator = {
            'implicitfast': mujoco.mjtIntegrator.mjINT_IMPLICITFAST,
            'euler': mujoco.mjtIntegrator.mjINT_EULER,
        }[integrator]
        self._mj_model.opt.iterations = int(self._config.iterations)
        self._mj_model.opt.ls_iterations = int(self._config.ls_iterations)
        impl = str(self._config.impl)
        self._mjx_model = mjx.put_model(self._mj_model, impl=impl)
        self._nu = int(self._mj_model.nu)
        if self._nu != 30 or self._mj_model.nq != 37:
            raise RuntimeError(f'unexpected model size nu={self._nu} nq={self._mj_model.nq}')

        gains = np.load(os.path.join(HERE, 'gains.npz'))
        ref = np.load(os.path.join(HERE, 'ref_cycle.npz'))
        self._joint_names = [str(s) for s in gains['joint_names'].tolist()]
        self._kp = jp.array(gains['kp'])
        self._kd = jp.array(gains['kd'])
        self._tau_lim = jp.array(gains['tau_lim'])
        self._w_lim = jp.array(gains['w_lim'])
        leg = np.array([n[:2] in ('l_', 'r_') and any(n.endswith(j) for j in (
            'hip_roll', 'hip_pitch', 'knee', 'ankle_pitch', 'ankle_roll')) for n in self._joint_names])
        scale = np.asarray(gains['action_scale'], dtype=np.float64)
        scale = np.where(leg, scale * float(self._config.leg_action_mult), scale)
        self._action_scale = jp.array(scale)
        self._knee_mask = jp.array([n.endswith('knee') for n in self._joint_names], dtype=jp.float32)
        self._carry = jp.array(gains['carry_offset'])
        self._home_q = jp.array(gains['home_q'])
        self._home_qpos = jp.array(gains['home_qpos'])
        self._ref_q = jp.array(ref['q'])
        self._ref_qd = jp.array(ref['qd'])
        self._ref_contact = jp.array(ref['contact'])
        self._ref_z = jp.array(ref['pelvis_z'])
        self._period = 1.0

        self._low = jp.array(self._mj_model.jnt_range[1:, 0])
        self._high = jp.array(self._mj_model.jnt_range[1:, 1])
        self._torso = int(self._mj_model.body('torso').id)
        self._payload = int(self._mj_model.body('payload').id)
        self._foot_ids = jp.array([self._mj_model.geom(n).id for n in ('l_foot', 'r_foot')])
        self._foot_halfz = jp.array([float(self._mj_model.geom_size[int(i), 2]) for i in self._foot_ids])
        q_noise = []
        for name in self._joint_names:
            if name.endswith('knee'):
                q_noise.append(0.05)
            elif name.endswith('ankle_pitch'):
                q_noise.append(0.08)
            elif name.endswith('ankle_roll'):
                q_noise.append(0.03)
            elif 'hip_' in name:
                q_noise.append(0.03)
            else:
                q_noise.append(0.02)
        self._q_noise = jp.array(q_noise)
        self._vx = tuple(self._config.vx_range)
        self._vy = tuple(self._config.vy_range)
        self._wz = tuple(self._config.yaw_range)
        scales = self._config.reward_scales
        self._scales = {k: float(scales[k]) for k in scales}

    @property
    def xml_path(self):
        return self._xml_path

    @property
    def action_size(self):
        return self._nu

    @property
    def mj_model(self):
        return self._mj_model

    @property
    def mjx_model(self):
        return self._mjx_model

    def _blend(self, table, phase, vx):
        n = table.shape[1]
        pos = phase * n
        i0 = jp.mod(jp.astype(jp.floor(pos), jp.int32), n)
        i1 = jp.mod(i0 + 1, n)
        a = pos - jp.floor(pos)
        speeds = (1.0 - a) * table[:, i0] + a * table[:, i1]
        u = jp.clip((vx - 0.8) / 0.2, 0.0, 2.0)
        w = jp.clip(u, 0.0, 1.0)
        low = (1.0 - w) * speeds[0] + w * speeds[1]
        w2 = jp.clip(u - 1.0, 0.0, 1.0)
        high = (1.0 - w2) * speeds[1] + w2 * speeds[2]
        return jp.where(u < 1.0, low, high)

    def _sample_command(self, rng):
        rng, k1, k2, k3, k4 = jax.random.split(rng, 5)
        vx = jax.random.uniform(k1, (), minval=self._vx[0], maxval=self._vx[1])
        vy = jax.random.uniform(k2, (), minval=self._vy[0], maxval=self._vy[1])
        wz = jax.random.uniform(k3, (), minval=self._wz[0], maxval=self._wz[1])
        stand = jax.random.uniform(k4, ()) < jp.float32(self._config.stand_prob)
        vx = jp.where(stand, 0.0, vx)
        vy = jp.where(stand, 0.0, vy)
        wz = jp.where(stand, 0.0, wz)
        return rng, jp.array([vx, vy, wz]), stand

    def _payload_frac(self):
        # J10: the 0.001 kg placeholder must read exactly 0. Job 4 gave 5e-5 with a 1e-6
        # normalizer std, so any eval feeding 0.0 put a -50 sigma input into walk_a/walk_b.
        mass = self._mjx_model.body_mass[self._payload]
        return jp.where(mass < 0.05, 0.0, jp.clip(mass / 20.0, 0.0, 1.5))

    @staticmethod
    def _yaw(data):
        w, x, y, z = data.qpos[3], data.qpos[4], data.qpos[5], data.qpos[6]
        return jp.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

    def _heading_err(self, data, info):
        e = self._yaw(data) - info['heading_ref']
        return jp.arctan2(jp.sin(e), jp.cos(e))

    def _is_stand(self, cmd):
        return (jp.abs(cmd[0]) < 0.12) & (jp.abs(cmd[1]) < 0.12) & (jp.abs(cmd[2]) < 0.2)

    def _target(self, cmd, phase, action, payload_frac):
        ref_q = self._blend(self._ref_q, phase, cmd[0])
        stand = self._is_stand(cmd)
        base = jp.where(stand, self._home_q, ref_q)
        target = base + payload_frac * self._carry + action * self._action_scale
        target = jp.clip(target, self._low, self._high)
        # L90 coupled hip stop (Legs 8569e3a): project hip (roll, yaw) targets into the surface.
        lr, ly = clip_hip_l90(target[1], target[0], 'L', xp=jp)
        rr, ry = clip_hip_l90(target[7], target[6], 'R', xp=jp)
        target = target.at[0].set(ly).at[1].set(lr).at[6].set(ry).at[7].set(rr)
        return target, stand, ref_q

    @staticmethod
    def _hip_stop_viol(data):
        q = data.qpos[7:]
        return (hip_stop_l90(q[1], q[0], 'L', xp=jp), hip_stop_l90(q[7], q[6], 'R', xp=jp))

    def _gravity(self, data):
        return math.rotate(jp.array([0.0, 0.0, -1.0]), math.quat_inv(data.qpos[3:7]))

    def _phase_obs(self, phase):
        ang = phase * jp.pi * 2.0
        return jp.array([jp.sin(ang), jp.cos(ang), jp.sin(ang + jp.pi), jp.cos(ang + jp.pi)])

    def _observe(self, data, info, tau, fz, contact, air, rng):
        lin = mjx_env.get_sensor_data(self.mj_model, data, 'local_linvel')
        gyro = mjx_env.get_sensor_data(self.mj_model, data, 'gyro')
        grav = self._gravity(data)
        q = data.qpos[7:] - self._home_q
        qd = data.qvel[6:]
        level = jp.float32(self._config.noise_level)
        rng, k1, k2, k3, k4, k5 = jax.random.split(rng, 6)
        lin_n = lin + jax.random.normal(k1, (3,)) * 0.1 * level
        gyro_n = gyro + jax.random.normal(k2, (3,)) * 0.2 * level
        grav_n = grav + jax.random.normal(k3, (3,)) * 0.05 * level
        q_n = q + jax.random.normal(k4, (self._nu,)) * self._q_noise * level
        qd_n = qd + jax.random.normal(k5, (self._nu,)) * 1.5 * level
        payload = self._payload_frac()
        phase = self._phase_obs(info['phase'])
        cmd = info['command']
        last = info['last_action']
        parts = [lin_n, gyro_n, grav_n, cmd, jp.array([payload]), q_n, qd_n, last, phase]
        cparts = [lin, gyro, grav, cmd, jp.array([payload]), q, qd, last, phase]
        if bool(self._config.heading_obs):
            he = self._heading_err(data, info)
            hobs = jp.array([jp.sin(he), jp.cos(he)])
            parts.append(hobs)
            cparts.append(hobs)
        state = jp.concatenate(parts)
        priv = jp.concatenate(cparts + [
            jp.array([data.qpos[2]]),
            tau / self._tau_lim,
            fz / 500.0,
            contact.astype(jp.float32),
            air,
            jp.array([info['strength'], info['kp_scale'], info['latency'] / 10.0]),
        ])
        state = jp.nan_to_num(state)
        priv = jp.nan_to_num(priv)
        obs = {'state': state, 'privileged_state': priv}
        return obs, rng, lin, gyro

    def _pd_scan(self, data, target, prev_target, latency, kp_scale, strength, fx, fy):
        model = self._mjx_model
        torso = self._torso
        kp = self._kp * kp_scale
        kd = self._kd * kp_scale

        def substep(data, i):
            use_prev = i < latency
            tgt = jp.where(use_prev, prev_target, target)
            q = data.qpos[7:]
            qd = data.qvel[6:]
            tau = kp * (tgt - q) - kd * qd
            has = self._w_lim > 0.0
            derate = 1.0 - jp.abs(qd) / (1.2 * jp.maximum(self._w_lim, 1e-6))
            derate = jp.where(has, jp.clip(derate, 0.0, 1.0), 1.0)
            tmax = self._tau_lim * strength * derate
            tau = jp.clip(tau, -tmax, tmax)
            xfrc = jp.zeros_like(data.xfrc_applied)
            xfrc = xfrc.at[torso, 0].set(fx)
            xfrc = xfrc.at[torso, 1].set(fy)
            data = data.replace(ctrl=tau, xfrc_applied=xfrc)
            data = mjx.step(model, data)
            return data, tau

        data, taus = jax.lax.scan(substep, data, jp.arange(self.n_substeps, dtype=jp.int32))
        return data, taus[-1]

    def reset(self, rng):
        rng, cmd, stand = self._sample_command(rng)
        rng, k_phase, k_yaw, k_gait, k_qn, k_qdn, k_kp, k_str, k_lat, k_push = jax.random.split(rng, 10)
        phase = jax.random.uniform(k_phase, ())
        phase = jp.where(stand, 0.0, phase)
        yaw = jax.random.uniform(k_yaw, (), minval=-jp.pi, maxval=jp.pi)
        use_gait = (~stand) & (jax.random.uniform(k_gait, ()) < jp.float32(self._config.gait_init_prob))
        phase = jp.where(use_gait, phase, 0.0)
        ref_q = self._blend(self._ref_q, phase, cmd[0])
        ref_qd = self._blend(self._ref_qd, phase, cmd[0])
        ref_z = self._blend(self._ref_z, phase, cmd[0])
        joints = jp.where(use_gait, ref_q, self._home_qpos[7:])
        joints = joints + jax.random.uniform(k_qn, (self._nu,), minval=-0.01, maxval=0.01)
        joints = jp.clip(joints, self._low, self._high)
        qd = jp.where(use_gait, ref_qd, jp.zeros(self._nu))
        qd = qd + jax.random.uniform(k_qdn, (self._nu,), minval=-0.05, maxval=0.05)
        z = jp.where(use_gait, ref_z, self._home_qpos[2])
        quat = jp.array([jp.cos(yaw * 0.5), 0.0, 0.0, jp.sin(yaw * 0.5)])
        c, s = jp.cos(yaw), jp.sin(yaw)
        qpos = jp.zeros(self._mj_model.nq).at[2].set(z).at[3:7].set(quat).at[7:].set(joints)
        qvel = jp.zeros(self._mj_model.nv)
        qvel = qvel.at[0].set(jp.where(use_gait, c * cmd[0] - s * cmd[1], 0.0))
        qvel = qvel.at[1].set(jp.where(use_gait, s * cmd[0] + c * cmd[1], 0.0))
        qvel = qvel.at[5].set(jp.where(use_gait, cmd[2], 0.0))
        qvel = qvel.at[6:].set(qd)

        data = mjx_env.make_data(
            self.mj_model,
            qpos=qpos,
            qvel=qvel,
            impl=self.mjx_model.impl.value,
            naconmax=int(self._config.naconmax),
            njmax=int(self._config.njmax),
        )
        data = mjx.forward(self._mjx_model, data)
        sole = data.geom_xpos[self._foot_ids, 2] - self._foot_halfz
        qpos = data.qpos.at[2].add(-(jp.min(sole) - 0.001))
        data = data.replace(qpos=qpos)
        data = mjx.forward(self._mjx_model, data)

        if self._config.dr_gains:
            kp_scale = jax.random.uniform(k_kp, (), minval=0.85, maxval=1.15)
            strength = jax.random.uniform(k_str, (), minval=0.85, maxval=1.10)
            latency = jax.random.randint(k_lat, (), 0, 11)
        else:
            kp_scale = jp.float32(1.0)
            strength = jp.float32(1.0)
            latency = jp.int32(0)
        next_push = jax.random.randint(k_push, (), 150, 301)
        zeros_a = jp.zeros(self._nu)
        target, _, _ = self._target(cmd, phase, zeros_a, self._payload_frac())
        info = {
            'rng': rng,
            'command': cmd,
            'phase': phase,
            'last_action': zeros_a,
            'prev_target': target,
            'kp_scale': kp_scale,
            'strength': strength,
            'latency': latency,
            'push_xy': jp.zeros(2),
            'push_left': jp.int32(0),
            'next_push': next_push,
            'step_count': jp.int32(0),
            'cmd_age': jp.int32(0),
            'feet_air_time': jp.zeros(2),
            'last_contact': jp.zeros(2, dtype=bool),
            'init_command': cmd,
            'init_phase': phase,
            'init_prev_target': target,
            'init_next_push': next_push,
            'heading_ref': yaw,
            'init_heading_ref': yaw,
            'knee_ms': jp.float32(0.0),
        }
        fz = jp.zeros(2)
        contact = jp.zeros(2, dtype=bool)
        tau = jp.zeros(self._nu)
        obs, rng, _, _ = self._observe(data, info, tau, fz, contact, info['feet_air_time'], rng)
        info['rng'] = rng
        metrics = self._zero_metrics()
        return mjx_env.State(data, obs, jp.array(0.0), jp.array(0.0), metrics, info)

    def _zero_metrics(self):
        keys = [
            'speed_per_step', 'cmd_vx_per_step', 'up_per_step', 'z_per_step',
            'rew_track_per_step', 'rew_ref_per_step', 'rew_torque_per_step',
            'fell',
        ]
        return {k: jp.array(0.0) for k in keys}

    def _rewards(self, data, info, action, tau, fz, contact, air, stand, ref_q, lin, gyro, done):
        cmd = info['command']
        lin_err = jp.sum(jp.square(lin[:2] - cmd[:2]))
        yaw_err = jp.square(gyro[2] - cmd[2])
        up = mjx_env.get_sensor_data(self.mj_model, data, 'upvector')[2]
        ref_z = self._blend(self._ref_z, info['phase'], cmd[0])
        z_tgt = jp.where(stand, self._home_qpos[2], ref_z)
        pose_ref = jp.where(stand, self._home_q, ref_q) + self._payload_frac() * self._carry
        ref_c = self._blend(self._ref_contact, info['phase'], cmd[0])
        desired = jp.where(stand, jp.ones(2), (ref_c > 0.5).astype(jp.float32))
        first = contact & (air > 0.0)
        # air passed in is the pre-reset timer; caller passes the value before zeroing.
        air_bonus = jp.sum(jp.maximum(info['feet_air_time'] - 0.25, 0.0) * first)
        air_bonus = air_bonus * (~stand) * (jp.linalg.norm(cmd[:2]) > 0.2)
        flying = (fz[0] < 20.0) & (fz[1] < 20.0) & (~stand)
        over_w = jp.maximum(jp.abs(data.qvel[6:]) - self._w_lim, 0.0) * (self._w_lim > 0.0)
        span = jp.maximum(self._high - self._low, 1e-3)
        mid = 0.5 * (self._high + self._low)
        norm = jp.abs(data.qpos[7:] - mid) / (0.5 * span)
        soft = jp.maximum(norm - 0.95, 0.0)
        sig = float(self._config.tracking_sigma)
        he = self._heading_err(data, info)
        knee_rms = jp.sqrt(jp.maximum(info['knee_ms'], 0.0))
        terms = {
            'tracking_lin': jp.exp(-lin_err / sig),
            'tracking_ang': jp.exp(-yaw_err / sig),
            'heading': jp.exp(-jp.square(he) / float(self._config.heading_sigma)),
            'knee_thermal': -jp.maximum(knee_rms / float(self._config.knee_cont_nm) - 1.0, 0.0),
            'knee_peak': -jp.sum(jp.square(jp.maximum(jp.abs(tau) * self._knee_mask - float(self._config.knee_peak_nm), 0.0)
                                           / float(self._config.knee_peak_nm))),
            'upright': jp.exp(-jp.square(1.0 - up) / 0.05),
            'height': jp.exp(-jp.square(data.qpos[2] - z_tgt) / 0.02),
            'ref_pose': jp.exp(-jp.mean(jp.square(data.qpos[7:] - pose_ref)) / 0.05),
            'contact': jp.mean(1.0 - jp.abs(desired - contact.astype(jp.float32))),
            'air_time': air_bonus,
            'no_flight': jp.where(flying, -1.0, 0.0),
            'torque': -jp.mean(jp.square(tau / self._tau_lim)),
            'action_rate': -jp.mean(jp.square(action - info['last_action'])),
            'vel_limit': -jp.sum(over_w),
            'joint_limit': -jp.sum(jp.square(soft)) - float(self._config.get('hip_stop_w', 100.0))
                           * sum(jp.square(h) for h in self._hip_stop_viol(data)),  # L90 coupled stop
            'alive': 1.0 - done,
        }
        scales = dict(self._scales)
        scales['ref_pose'] = float(self._config.ref_weight)
        reward = sum(scales[k] * terms[k] for k in terms) * self.dt
        reward = reward - done
        return reward, terms['tracking_lin'], terms['ref_pose'], terms['torque'], up

    def step(self, state, action):
        info = dict(state.info)
        rng = info['rng']
        action = jp.clip(action, -1.0, 1.0)
        step_count = info['step_count'] + jp.int32(1)
        cmd_age = info['cmd_age'] + jp.int32(1)
        resample = cmd_age >= jp.int32(self._config.resample_steps)
        rng, new_cmd, _ = self._sample_command(rng)
        cmd = jp.where(resample, new_cmd, info['command'])
        cmd_age = jp.where(resample, jp.int32(0), cmd_age)
        info['command'] = cmd

        rng, k_mag, k_ang, k_dur, k_gate, k_int = jax.random.split(rng, 6)
        push_on = jp.array(bool(self._config.push_enable))
        start_push = (info['push_left'] <= 0) & (step_count >= info['next_push']) & push_on
        mag = jax.random.uniform(
            k_mag, (), minval=self._config.push_force_range[0], maxval=self._config.push_force_range[1],
        )
        ang = jax.random.uniform(k_ang, (), minval=0.0, maxval=2.0 * jp.pi)
        dur = jax.random.randint(k_dur, (), 5, 11)
        gate = jax.random.uniform(k_gate, ()) < jp.float32(self._config.push_gate_prob)
        mag = jp.where(gate, 300.0, mag)
        dur = jp.where(gate, jp.int32(10), dur)
        new_force = jp.array([jp.cos(ang) * mag, jp.sin(ang) * mag])
        push_xy = jp.where(start_push, new_force, info['push_xy'])
        push_left = jp.where(start_push, dur, info['push_left'])
        interval = jax.random.randint(k_int, (), 150, 301)
        next_push = jp.where(start_push, step_count + interval, info['next_push'])
        apply = push_left > 0
        fx = jp.where(apply, push_xy[0], 0.0)
        fy = jp.where(apply, push_xy[1], 0.0)
        push_left = jp.where(apply, push_left - jp.int32(1), push_left)

        payload = self._payload_frac()
        target, stand, ref_q = self._target(cmd, info['phase'], action, payload)
        data, tau = self._pd_scan(
            state.data, target, info['prev_target'], info['latency'],
            info['kp_scale'], info['strength'], fx, fy,
        )
        fz = jp.array([
            mjx_env.get_sensor_data(self.mj_model, data, 'l_foot_touch')[0],
            mjx_env.get_sensor_data(self.mj_model, data, 'r_foot_touch')[0],
        ])
        contact = fz > 20.0
        air = info['feet_air_time']
        # Knee thermal proxy: ~10 s EMA of mean knee tau^2 vs rev B 76.9 N·m continuous.
        knee_sq = jp.sum(jp.square(tau) * self._knee_mask) / jp.maximum(jp.sum(self._knee_mask), 1.0)
        info['knee_ms'] = 0.998 * info['knee_ms'] + 0.002 * knee_sq
        info['heading_ref'] = info['heading_ref'] + cmd[2] * self.dt
        up = mjx_env.get_sensor_data(self.mj_model, data, 'upvector')[2]
        nan = jp.isnan(data.qpos).any() | jp.isnan(data.qvel).any()
        hv = self._hip_stop_viol(data)
        fell = (data.qpos[2] < 0.70) | (up < 0.50) | nan | (jp.maximum(hv[0], hv[1]) > HIP_STOP_TERM)
        done = fell.astype(jp.float32)

        # Air-time reward reads the timer before contact zeros it. Pass a copy via info.
        info_air = dict(info)  # carries heading_ref and knee_ms updated above
        info_air['feet_air_time'] = air
        # _rewards uses info['command'] and info['phase'] and info['last_action'].
        dummy_obs_info = info_air
        reward, track, ref_r, torque_r, up = self._rewards(
            data, dummy_obs_info, action, tau, fz, contact, air, stand, ref_q,
            mjx_env.get_sensor_data(self.mj_model, data, 'local_linvel'),
            mjx_env.get_sensor_data(self.mj_model, data, 'gyro'),
            done,
        )
        reward = jp.where(nan, -1.0, reward)
        new_air = jp.where(contact, 0.0, air + self.dt)
        walking = ~stand
        phase = jp.where(walking, jp.mod(info['phase'] + self.dt / self._period, 1.0), info['phase'])

        d = done > 0.5
        # Cached autoreset restores the first physics state. Match the info that built it.
        # Gains are not part of that state, so resample them on a fall.
        rng, k_kp, k_str, k_lat, k_push = jax.random.split(rng, 5)
        if self._config.dr_gains:
            new_kp = jax.random.uniform(k_kp, (), minval=0.85, maxval=1.15)
            new_str = jax.random.uniform(k_str, (), minval=0.85, maxval=1.10)
            new_lat = jax.random.randint(k_lat, (), 0, 11)
        else:
            new_kp = info['kp_scale']
            new_str = info['strength']
            new_lat = info['latency']
        new_next = jax.random.randint(k_push, (), 150, 301)
        cmd = jp.where(d, info['init_command'], cmd)
        phase = jp.where(d, info['init_phase'], phase)
        last_action = jp.where(d, jp.zeros(self._nu), action)
        prev_target = jp.where(d, info['init_prev_target'], target)
        push_xy = jp.where(d, jp.zeros(2), push_xy)
        push_left = jp.where(d, jp.int32(0), push_left)
        next_push = jp.where(d, new_next, next_push)
        step_count = jp.where(d, jp.int32(0), step_count)
        cmd_age = jp.where(d, jp.int32(0), cmd_age)
        new_air = jp.where(d, jp.zeros(2), new_air)
        contact_store = jp.where(d, jp.zeros(2, dtype=bool), contact)
        heading_ref = jp.where(d, info['init_heading_ref'], info['heading_ref'])
        knee_ms = jp.where(d, 0.0, info['knee_ms'])
        kp_scale = jp.where(d, new_kp, info['kp_scale'])
        strength = jp.where(d, new_str, info['strength'])
        latency = jp.where(d, new_lat, info['latency'])

        info.update({
            'rng': rng,
            'command': cmd,
            'phase': phase,
            'last_action': last_action,
            'prev_target': prev_target,
            'kp_scale': kp_scale,
            'strength': strength,
            'latency': latency,
            'push_xy': push_xy,
            'push_left': push_left,
            'next_push': next_push,
            'step_count': step_count,
            'cmd_age': cmd_age,
            'feet_air_time': new_air,
            'last_contact': contact_store,
            'heading_ref': heading_ref,
            'knee_ms': knee_ms,
        })
        obs, rng, lin, _ = self._observe(data, info, tau, fz, contact, new_air, rng)
        info['rng'] = rng
        metrics = {
            'speed_per_step': jp.nan_to_num(lin[0]),
            'cmd_vx_per_step': jp.nan_to_num(info['command'][0]),
            'up_per_step': jp.nan_to_num(up),
            'z_per_step': jp.nan_to_num(data.qpos[2]),
            'rew_track_per_step': jp.nan_to_num(track),
            'rew_ref_per_step': jp.nan_to_num(ref_r),
            'rew_torque_per_step': jp.nan_to_num(torque_r),
            'fell': done,
        }
        # EvalWrapper inserts metrics['reward'] before step. The episode scan
        # requires the same metric keys on the way out.
        for key, value in state.metrics.items():
            if key not in metrics:
                metrics[key] = value
        return state.replace(data=data, obs=obs, reward=reward, done=done, metrics=metrics, info=info)
