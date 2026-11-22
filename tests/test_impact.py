"""Where on the body a hit struck: the shot's ray traced to the victim's posed body."""

import numpy as np
import pandas as pd
import pytest

from heat3d_cs2 import impact


def hurt(**kw):
    row = {"tick": 100, "hitgroup": "head", "attacker_steamid": "1", "user_X": 0.0, "user_Y": 0.0, "user_Z": 0.0,
           "user_yaw": 0.0, "user_duck_amount": 0.0, "attacker_X": -500.0, "attacker_Y": 0.0, "attacker_Z": 0.0,
           "attacker_pitch": 0.0, "attacker_yaw": 0.0, "attacker_duck_amount": 0.0}
    row.update(kw)
    return pd.DataFrame([row])


def test_a_shot_from_ahead_strikes_the_face_at_eye_height():
    # The victim faces the attacker (yaw 180: towards -x); the attacker's eye looks straight at the victim's head.
    p = impact.hit_points(hurt(user_yaw=180.0), None)
    assert p["hitFrom"][0] == "aim"
    x, y, z = p["hitLocalX"][0], p["hitLocalY"][0], p["hitLocalZ"][0]
    assert x > 0.1 and y == pytest.approx(64 * impact.METRES, abs=0.03) and abs(z) < 0.01
    # The shot travels backwards through the victim's frame.
    assert p["hitDirX"][0] == pytest.approx(-1.0) and p["hitMiss"][0] == 0.0


def test_the_games_bullet_is_taken_over_the_view_and_a_miss_is_snapped_into_the_part():
    bullets = pd.DataFrame([{"tick": 100, "user_steamid": "1", "origin_x": -500.0, "origin_y": 0.0, "origin_z": 52.0,
                             "angles_x": 0.0, "angles_y": 0.0}])
    # The bullet flies at chest height, but the game says the left leg: the point is on the leg, nearest the ray.
    p = impact.hit_points(hurt(hitgroup="left_leg", user_yaw=90.0), bullets)
    assert p["hitFrom"][0] == "bullet"
    # The thigh's top, where it comes nearest the ray: no higher than the hip and its radius.
    assert p["hitLocalY"][0] <= (impact.HIP + 4.6) * impact.METRES + 0.01 and p["hitMiss"][0] > 0


def test_a_crouch_lowers_the_head_and_generic_hits_have_no_place():
    up = impact.hit_points(hurt(user_yaw=180.0, attacker_pitch=0.0), None)["hitLocalY"][0]
    down = impact.hit_points(hurt(user_yaw=180.0, user_duck_amount=1.0, attacker_Z=-18.0), None)["hitLocalY"][0]
    assert up - down == pytest.approx(impact.CROUCH_DROP * impact.METRES, abs=0.03)
    assert np.isnan(impact.hit_points(hurt(hitgroup="generic"), None)["hitLocalX"][0])


def test_the_bullet_leaves_the_aim_by_the_spread_its_seed_draws():
    a, b = impact.Stream(7), impact.Stream(7)
    draws = [a.uniform() for _ in range(50)]
    assert draws == [b.uniform() for _ in range(50)] and all(0 <= x < 1 for x in draws) and len(set(draws)) == 50
    x, y = impact.spread(1234.0, 0.01, 0.002)
    assert 0 < np.hypot(x, y) <= 0.012
    # No seed, no spread; a shotgun's pellet spread is not drawn (which pellet struck is not known).
    assert impact.spread(np.nan, 0.01, 0.002) == (0.0, 0.0)
    sx, sy = impact.spread(1234.0, 0.0, 0.5, item=35)
    assert (sx, sy) == (0.0, 0.0)
    d = impact.bullet(0.0, 0.0, 0.01, 0.0)
    assert d[1] == pytest.approx(-0.01, abs=1e-4) and np.linalg.norm(d) == pytest.approx(1.0)
    bullets = pd.DataFrame([{"tick": 100, "user_steamid": "1", "origin_x": -500.0, "origin_y": 0.0, "origin_z": 64.0,
                             "angles_x": 0.0, "angles_y": 0.0, "seed": 99.0, "inaccuracy": 0.01, "spread": 0.0, "item_def_index": 7}])
    p = impact.hit_points(hurt(user_yaw=180.0), bullets)
    assert p["_weapon"][0] == 7 and p["hitDirX"][0] != pytest.approx(-1.0, abs=1e-9)
