"""Light CPU checks for the replay harness (J10). Run: MUJOCO_GL=disable python3 -m pytest -q test_eval_box.py"""
import os
import sys

import numpy as np
import pytest

os.environ.setdefault('MUJOCO_GL', 'disable')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eval_box as eb  # noqa: E402

GAINS = np.load(os.path.join(HERE, 'gains.npz'))
REF = np.load(os.path.join(HERE, 'ref_cycle.npz'))


@pytest.fixture(scope='module')
def box():
    return eb.load_box(0.0)[0]


@pytest.mark.parametrize('name', ['walk_a', 'walk_b'])
def test_legacy_empty_payload_matches_training(name):
    pol = eb.load_policy(os.path.join(HERE, f'policy_{name}.npz'))
    assert pol[3]['payload_empty_frac'] is None
    assert abs(eb.empty_payload_frac(pol) - 5e-5) < 1e-7


def test_carry_empty_payload_is_zero():
    pol = eb.load_policy(os.path.join(HERE, 'policy_carry.npz'))
    assert eb.empty_payload_frac(pol) == 0.0


def test_zero_payload_obs_is_rejected(box):
    """Regression for job 4: payload_frac 0.0 is ~50 sigma off for walk_a and must abort."""
    pol = eb.load_policy(os.path.join(HERE, 'policy_walk_a.npz'))
    with pytest.raises(SystemExit, match='sigma'):
        eb.run_episode(box, pol, GAINS, REF, cmd=np.array([1.2, 0.0, 0.0]), seconds=0.1,
                       mode='gait', payload_frac=0.0)


def test_walk_a_stays_up_with_matched_obs(box):
    pol = eb.load_policy(os.path.join(HERE, 'policy_walk_a.npz'))
    s, _ = eb.run_episode(box, pol, GAINS, REF, cmd=np.array([1.2, 0.0, 0.0]), seconds=3.0,
                          mode='gait', payload_frac=None)
    assert s['fell_at_s'] is None
    assert s['obs_z_max_t0'] < eb.OBS_Z_MAX


def test_drift_gate():
    assert eb.drift_ok({'final_y': 0.2, 'final_heading_deg': -3.0})
    assert not eb.drift_ok({'final_y': 0.8, 'final_heading_deg': 0.0})
    assert not eb.drift_ok({'final_y': 0.0, 'final_heading_deg': 12.0})


def test_heading_obs_zero_at_reference():
    class D:
        qpos = np.array([0, 0, 1, 1.0, 0, 0, 0])
    h = eb._heading_obs(D, 0.0)
    assert np.allclose(h, [0.0, 1.0])
    yaw = 0.3
    D.qpos = np.array([0, 0, 1, np.cos(yaw / 2), 0, 0, np.sin(yaw / 2)])
    assert np.allclose(eb._heading_obs(D, 0.0), [np.sin(yaw), np.cos(yaw)])


def test_payload_pos_dr_covers_both_points():
    """R-117: the DR box must cover P-042 and Legs' point; eval gate uses P-042."""
    import yaml
    import payload_pos as pp
    cfg = yaml.safe_load(open(os.path.join(HERE, 'train_cfg.yaml')))
    for name in ('j10_carry', 'j10_rough'):
        lo, hi = pp.bounds(cfg['stages'][name])
        assert pp.covers(lo, hi, pp.P042) and pp.covers(lo, hi, pp.LEGS), name
    lo, hi = pp.bounds({})
    assert pp.covers(lo, hi, pp.P042) and pp.covers(lo, hi, pp.LEGS)
    with pytest.raises(ValueError):
        pp.bounds({'payload_pos': [[0.4, 0, 0], [0.3, 0, 0]]})
    assert tuple(eb.P042) == pp.P042 and tuple(eb.LEGS_PAYLOAD) == pp.LEGS


def test_carry_box_places_payload_at_p042():
    m, _ = eb.load_box(20.0)
    assert np.allclose(m.body_pos[m.body('payload').id], [0.32, 0.0, 0.415])
    m2, _ = eb.load_box(20.0, payload_pos=eb.LEGS_PAYLOAD)
    assert np.allclose(m2.body_pos[m2.body('payload').id], [0.25, 0.0, 0.10])
