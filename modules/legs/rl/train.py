"""Train the v3 walk policy with Brax PPO on MJX.

Run inside the WSL venv. Long runs log to /root/rl-runs and to modules/legs/rl/logs.
"""
import os

os.environ.setdefault('XLA_PYTHON_CLIENT_MEM_FRACTION', '0.70')
os.environ.setdefault('JAX_DEFAULT_MATMUL_PRECISION', 'high')

import argparse
import functools
import json
import logging
import sys
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUNS = os.environ.get('RL_RUNS', '/root/rl-runs')


def _load_cfg():
    import yaml
    with open(os.path.join(HERE, 'train_cfg.yaml'), encoding='utf-8') as f:
        return yaml.safe_load(f)


def _env_from_stage(stage, noise=1.0):
    from joystick import HumanoidWalk
    xml = 'humanoid_mjx_rough.xml' if stage.get('rough') else 'humanoid_mjx.xml'
    overrides = {
        'noise_level': float(noise),
        'vx_range': list(stage['vx']),
        'vy_range': list(stage['vy']),
        'yaw_range': list(stage['yaw']),
        'stand_prob': float(stage['stand_prob']),
        'gait_init_prob': float(stage['gait_init_prob']),
        'push_enable': bool(stage['push']),
        'push_force_range': list(stage['push_force']),
        'push_gate_prob': float(stage['push_gate_prob']),
        'ref_weight': float(stage['ref_weight']),
        'integrator': str(stage.get('integrator', 'implicitfast')),
        'iterations': int(stage.get('iterations', 4)),
        'ls_iterations': int(stage.get('ls_iterations', 8)),
        'naconmax': int(stage.get('naconmax', 80)),
        'njmax': int(stage.get('njmax', 256)),
        'dr_gains': True,
    }
    # J10 knobs (RETRAIN_PLAN_J10.md). Absent keys keep the job-4 defaults.
    for key in ('heading_obs', 'tracking_sigma', 'heading_sigma', 'leg_action_mult', 'knee_cont_nm', 'resample_steps'):
        if key in stage:
            overrides[key] = stage[key]
    for key, val in (stage.get('rewards') or {}).items():
        overrides[f'reward_scales.{key}'] = float(val)
    return HumanoidWalk(xml_path=os.path.join(HERE, xml), config_overrides=overrides)


def _randomizer(env, carry, stage=None):
    from randomize import make_randomizer
    m = env.mj_model
    return make_randomizer(
        m.body('payload').id,
        m.geom('floor').id,
        [m.geom('l_foot').id, m.geom('r_foot').id],
        float(carry[0]),
        float(carry[1]),
        *(_payload_bounds(stage) if float(carry[1]) > float(carry[0]) else (None, None)),
    )


def _payload_bounds(stage):
    from payload_pos import bounds
    return bounds(stage)


def network_factory(obs_size, action_size, preprocess_observations_fn):
    from brax.training.agents.ppo import networks as ppo_networks
    import jax
    return ppo_networks.make_ppo_networks(
        obs_size,
        action_size,
        preprocess_observations_fn=preprocess_observations_fn,
        policy_hidden_layer_sizes=(512, 256, 128),
        value_hidden_layer_sizes=(512, 256, 128),
        activation=jax.nn.swish,
        policy_obs_key='state',
        value_obs_key='privileged_state',
        distribution_type='tanh_normal',
    )


def _plot_curves(name, log_path):
    """Write one PNG of whatever episode and training series the jsonl actually has."""
    if not os.path.isfile(log_path):
        return None
    rows = []
    with open(log_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        return None
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    steps = [r.get('step', i) for i, r in enumerate(rows)]
    groups = [
        ('reward', ('episode_reward',)),
        ('speed', ('speed_per_step', 'cmd_vx')),
        ('upright_z', ('up_per_step', 'z_per_step')),
        ('reward_terms', ('rew_track', 'rew_ref', 'rew_torque', 'fell')),
        ('sps', ('training/sps', 'sps')),
    ]
    series = []
    for title, needles in groups:
        found = []
        for key in rows[-1].keys():
            if any(n in key for n in needles) and 'std' not in key:
                ys = [r.get(key) for r in rows]
                if any(isinstance(v, (int, float)) for v in ys):
                    found.append((key, ys))
        if found:
            series.append((title, found))
    if not series:
        return None
    fig, axes = plt.subplots(len(series), 1, figsize=(8, 2.4 * len(series)), sharex=True)
    if len(series) == 1:
        axes = [axes]
    for ax, (title, found) in zip(axes, series):
        for key, ys in found:
            ax.plot(steps, [float('nan') if v is None else v for v in ys], label=key)
        ax.set_ylabel(title)
        ax.legend(fontsize=7, loc='best')
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel('env steps')
    fig.suptitle(name)
    fig.tight_layout()
    out_dir = os.path.join(HERE, 'curves')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f'{name}.png')
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def _vram():
    import subprocess
    try:
        out = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
            text=True,
        ).strip().split(',')
        return int(out[0]), int(out[1])
    except Exception as exc:
        return -1, str(exc)


def _jsonable(v):
    if hasattr(v, 'item') and getattr(v, 'ndim', None) == 0:
        v = v.item()
    if isinstance(v, (float, int, np.floating, np.integer)):
        return float(v)
    if isinstance(v, np.ndarray) and v.shape == ():
        return float(v)
    return None


def _latest_ckpt(stage):
    root = os.path.join(RUNS, stage)
    if not os.path.isdir(root):
        return None
    steps = [d for d in os.listdir(root) if d.isdigit()]
    if not steps:
        return None
    return os.path.join(root, max(steps))


def _save_policy_npz(step, params, path):
    """Flatten the Brax param pytree. Keys are path strings with '__' separators."""
    import jax
    normalizer, policy, value = params

    def pack(prefix, tree):
        items = {}
        leaves = jax.tree_util.tree_flatten_with_path(tree)[0]
        for keypath, leaf in leaves:
            parts = []
            for k in keypath:
                if hasattr(k, 'key'):
                    parts.append(str(k.key))
                elif hasattr(k, 'name'):
                    parts.append(str(k.name))
                else:
                    parts.append(str(k))
            name = prefix + '__'.join(parts)
            items[name] = np.asarray(leaf)
        return items

    blob = {}
    blob.update(pack('norm__', normalizer))
    blob.update(pack('pi__', policy))
    blob.update(pack('v__', value))
    blob['step'] = np.array(step)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.savez(path, **blob)
    return sorted(blob)


def _write_meta(npz_path, env, stage, name):
    """Sidecar that eval_box.py reads so the replay matches the training env exactly."""
    cfg = env._config
    meta = {
        'stage': name,
        'policy_obs_dim': int(env.observation_size['state'][0]) if isinstance(env.observation_size, dict) else None,
        'heading_obs': bool(cfg.heading_obs),
        'leg_action_mult': float(cfg.leg_action_mult),
        'payload_empty_frac': 0.0,
        'xml': os.path.basename(env.xml_path),
        'model_mass_kg': float(env.mj_model.body_mass.sum()),
    }
    with open(npz_path[:-4] + '.meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
    return meta


def smoke_step(n=8, stage_override=None):
    import jax
    from mujoco_playground._src.wrapper import wrap_for_brax_training

    print('devices', jax.devices(), flush=True)
    stage = {
        'vx': [0.6, 1.0], 'vy': [-0.2, 0.2], 'yaw': [-0.3, 0.3],
        'stand_prob': 0.1, 'gait_init_prob': 0.8, 'push': True,
        'push_force': [50.0, 150.0], 'push_gate_prob': 0.2,
        'ref_weight': 1.0, 'carry': [0.001, 0.001], 'rough': False,
    }
    if stage_override is not None:
        stage = dict(stage_override)
    env = _env_from_stage(stage)
    print('obs', env.observation_size, 'act', env.action_size, flush=True)
    rngs = jax.random.split(jax.random.PRNGKey(0), n)
    rand = _randomizer(env, stage['carry'])
    wrapped = wrap_for_brax_training(
        env, episode_length=200, action_repeat=1,
        randomization_fn=functools.partial(rand, rng=rngs),
        full_reset=False,
    )
    reset = jax.jit(wrapped.reset)
    step = jax.jit(wrapped.step)
    t0 = time.time()
    state = reset(rngs)
    state.obs['state'].block_until_ready()
    print(f'reset {time.time() - t0:.1f}s vram {_vram()}', flush=True)
    print('state', state.obs['state'].shape, 'z', np.asarray(state.data.qpos[:, 2])[:4], flush=True)
    action = jax.numpy.zeros((n, env.action_size))
    t0 = time.time()
    for i in range(5):
        state = step(state, action)
        state.obs['state'].block_until_ready()
        z = np.asarray(state.data.qpos[:, 2])
        up = np.asarray(state.metrics['up_per_step'])
        spd = np.asarray(state.metrics['speed_per_step'])
        rew = np.asarray(state.reward)
        print(
            f'step {i} z {z.mean():.3f} up {up.mean():.3f} speed {spd.mean():.3f} '
            f'rew {rew.mean():.3f} fell {float(np.asarray(state.metrics["fell"]).mean()):.2f} '
            f'finite {bool(np.isfinite(rew).all())}',
            flush=True,
        )
    print(f'steps {time.time() - t0:.1f}s vram {_vram()}', flush=True)
    if not np.isfinite(np.asarray(state.reward)).all():
        raise SystemExit('non-finite reward')


def _patch_jax_for_brax():
    """Brax 0.14 calls jax.device_put_replicated. JAX 0.11 removed it from the public API.

    The implementation in jax._src.api still adds the leading device axis that pmap expects.
    Assigning it onto the jax module skips the deprecation __getattr__.
    """
    import jax
    import jax._src.api as jax_api
    jax.device_put_replicated = jax_api.device_put_replicated


def train_stage(name, stage, cfg, num_envs, timesteps, num_evals, run_evals=True):
    import jax
    _patch_jax_for_brax()
    from brax.training.agents.ppo import train as ppo_train

    os.makedirs(RUNS, exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True)
    log_path = os.path.join(HERE, 'logs', f'{name}.jsonl')
    env = _env_from_stage(stage)
    rand = _randomizer(env, stage['carry'], stage)
    batch = int(cfg['batch_size'])
    minibatch = int(cfg['num_minibatches'])
    # Keep batch * minibatch == num_envs. Scale batch with the env count.
    if batch * minibatch != num_envs:
        batch = max(1, num_envs // minibatch)
        if batch * minibatch != num_envs:
            raise SystemExit(f'batch {batch} * {minibatch} != num_envs {num_envs}')
    restore = None
    if stage.get('restore'):
        restore = _latest_ckpt(stage['restore'])
        if restore is None:
            raise SystemExit(f'missing checkpoint for {stage["restore"]}')
        print('restore', restore, flush=True)

    t0 = time.time()

    def progress(step, metrics):
        row = {'step': int(step), 'wall_s': round(time.time() - t0, 1)}
        used, total = _vram()
        row['vram_mib'] = used
        row['vram_total_mib'] = total if isinstance(total, int) else None
        for k, v in metrics.items():
            num = _jsonable(v)
            if num is not None and np.isfinite(num):
                row[k] = num
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(row) + '\n')
        interesting = {k: row[k] for k in row if 'episode' in k or k in ('step', 'vram_mib', 'wall_s') or 'sps' in k}
        print('PROGRESS', json.dumps(interesting)[:800], flush=True)
        try:
            plotted = _plot_curves(name, log_path)
            if plotted:
                print('curve', plotted, flush=True)
        except Exception as exc:
            print('curve_failed', exc, flush=True)

    def save_params(step, make_policy, params):
        path = os.path.join(RUNS, name, f'policy_{int(step)}.npz')
        keys = _save_policy_npz(step, params, path)
        latest = os.path.join(HERE, 'logs', f'{name}_policy_latest.npz')
        _save_policy_npz(step, params, latest)
        print(f'saved {path} nkeys {len(keys)}', flush=True)
        if step == 0:
            with open(os.path.join(HERE, 'logs', 'policy_keys.txt'), 'w', encoding='utf-8') as f:
                f.write('\n'.join(keys))

    print(
        f'start {name} envs {num_envs} batch {batch} steps {timesteps} '
        f'integrator {stage.get("integrator", "implicitfast")} '
        f'iter {stage.get("iterations", 4)} nacon {stage.get("naconmax", 80)} '
        f'devices {jax.devices()}',
        flush=True,
    )
    # Meta for mid-run checkpoints (logs/<stage>_policy_latest.npz) so eval_box can score them.
    _write_meta(os.path.join(HERE, 'logs', f'{name}_policy_latest.npz'), env, stage, name)
    make_policy, params, metrics = ppo_train.train(
        environment=env,
        num_timesteps=int(timesteps),
        episode_length=int(cfg['episode_length']),
        num_envs=int(num_envs),
        batch_size=int(batch),
        num_minibatches=int(minibatch),
        unroll_length=int(cfg['unroll_length']),
        num_updates_per_batch=int(cfg['num_updates_per_batch']),
        learning_rate=float(cfg['learning_rate']),
        entropy_cost=float(cfg['entropy_cost']),
        discounting=float(cfg['discounting']),
        clipping_epsilon=float(cfg['clipping_epsilon']),
        reward_scaling=float(cfg['reward_scaling']),
        max_grad_norm=float(cfg['max_grad_norm']),
        normalize_observations=True,
        seed=int(cfg['seed']),
        num_evals=int(num_evals),
        num_eval_envs=int(cfg['num_eval_envs']),
        deterministic_eval=True,
        run_evals=run_evals,
        log_training_metrics=True,
        training_metrics_steps=1_000_000,
        network_factory=network_factory,
        randomization_fn=rand,
        wrap_env_fn=functools.partial(
            __import__('mujoco_playground._src.wrapper', fromlist=['wrap_for_brax_training']).wrap_for_brax_training,
            full_reset=False,
        ),
        progress_fn=progress,
        policy_params_fn=save_params,
        save_checkpoint_path=os.path.join(RUNS, name),
        restore_checkpoint_path=restore,
    )
    final = os.path.join(HERE, 'logs', f'{name}_final.npz')
    _save_policy_npz(timesteps, params, final)
    _write_meta(final, env, stage, name)
    print(f'DONE {name} wall_s {time.time() - t0:.1f} vram {_vram()}', flush=True)
    return params


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stage', default='walk_a')
    p.add_argument('--smoke-step', action='store_true')
    p.add_argument('--num-envs', type=int, default=None)
    p.add_argument('--timesteps', type=int, default=None)
    p.add_argument('--num-evals', type=int, default=None)
    p.add_argument('--no-eval', action='store_true')
    args = p.parse_args()
    if args.smoke_step:
        # --smoke-step alone keeps the job-4 smoke; with --stage j10_* it smokes that stage's env.
        override = _load_cfg()['stages'][args.stage] if args.stage.startswith('j10') else None
        smoke_step(stage_override=override)
        return
    cfg = _load_cfg()
    os.environ['XLA_PYTHON_CLIENT_MEM_FRACTION'] = str(cfg.get('mem_fraction', 0.70))
    os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE', 'false')
    os.makedirs(RUNS, exist_ok=True)
    os.environ.setdefault('JAX_COMPILATION_CACHE_DIR', os.path.join(RUNS, 'jax_cache'))
    stage = cfg['stages'][args.stage]
    num_envs = args.num_envs or int(cfg['num_envs'])
    timesteps = args.timesteps or int(stage['timesteps'])
    num_evals = args.num_evals or int(cfg['num_evals'])
    train_stage(args.stage, stage, cfg, num_envs, timesteps, num_evals, run_evals=not args.no_eval)


if __name__ == '__main__':
    main()
