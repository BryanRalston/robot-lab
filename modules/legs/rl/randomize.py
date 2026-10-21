"""Per-environment dynamics randomization for the v3 humanoid.

Brax calls this as domain_randomize(mjx_model) with the rng already bound.
Draws stay fixed for an env for the whole run (Playground's pattern). Kp, latency
and push timing are resampled in the env reset instead.
"""
import jax
from mujoco import mjx


def make_randomizer(payload_id, floor_id, foot_ids, carry_low, carry_high, pos_low=None, pos_high=None):
    """pos_low/pos_high: payload body position box (torso frame), R-117. None keeps the XML position."""
    payload_id = int(payload_id)
    floor_id = int(floor_id)
    foot_ids = tuple(int(i) for i in foot_ids)

    def domain_randomize(model: mjx.Model, rng: jax.Array):
        @jax.vmap
        def rand(rng):
            rng, k = jax.random.split(rng)
            scale = jax.random.uniform(k, (model.nbody,), minval=0.95, maxval=1.05)
            scale = scale.at[0].set(1.0)
            scale = scale.at[payload_id].set(1.0)
            mass = model.body_mass * scale
            rng, k = jax.random.split(rng)
            if carry_high <= carry_low:
                payload = jax.numpy.array(0.001)
            else:
                payload = jax.random.uniform(k, minval=carry_low, maxval=carry_high)
            mass = mass.at[payload_id].set(payload)
            robot = jax.numpy.sum(mass) - mass[0] - mass[payload_id]
            factor = jax.numpy.minimum(1.0, 66.5 / jax.numpy.maximum(robot, 1.0))
            mass = mass * factor
            mass = mass.at[0].set(model.body_mass[0])
            mass = mass.at[payload_id].set(payload)
            ratio = mass / jax.numpy.maximum(model.body_mass, 1e-8)
            inertia = model.body_inertia * ratio[:, None]
            # A 20 kg box uses diaginertia 0.20, 0.15, 0.20 in gait_lib.
            inertia = inertia.at[payload_id].set(payload * jax.numpy.array([0.01, 0.0075, 0.01]))

            rng, k = jax.random.split(rng)
            ipos = model.body_ipos + jax.random.uniform(k, model.body_ipos.shape, minval=-0.02, maxval=0.02)
            ipos = ipos.at[0].set(model.body_ipos[0])

            rng, k1, k2 = jax.random.split(rng, 3)
            fric = model.geom_friction
            fric = fric.at[floor_id, 0].set(jax.random.uniform(k1, minval=0.5, maxval=1.2))
            foot_f = jax.random.uniform(k2, (len(foot_ids),), minval=0.5, maxval=1.2)
            fric = fric.at[foot_ids, 0].set(foot_f)

            bpos = model.body_pos
            if pos_low is not None:
                rng, k = jax.random.split(rng)
                p = jax.random.uniform(k, (3,), minval=jax.numpy.array(pos_low), maxval=jax.numpy.array(pos_high))
                bpos = bpos.at[payload_id].set(p)
            return mass, inertia, ipos, fric, bpos

        body_mass, body_inertia, body_ipos, geom_friction, body_pos = rand(rng)
        in_axes = jax.tree_util.tree_map(lambda x: None, model)
        in_axes = in_axes.tree_replace({
            'body_mass': 0,
            'body_inertia': 0,
            'body_ipos': 0,
            'geom_friction': 0,
            'body_pos': 0,
        })
        model = model.tree_replace({
            'body_mass': body_mass,
            'body_inertia': body_inertia,
            'body_ipos': body_ipos,
            'geom_friction': geom_friction,
            'body_pos': body_pos,
        })
        return model, in_axes

    return domain_randomize
