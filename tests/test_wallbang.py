"""Which hits went through a wall: the shot traced through a made-up level."""

import numpy as np
import pandas as pd
import pytest

from heat3d_cs2 import glb, impact, wallbang
from heat3d_cs2.mapexport import parts_from, surface_of, to_viewer


def box(lo, hi):
    """A closed box's 12 triangles, wound to face out, in the game's frame."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], float)
    f = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4],
                  [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    return v, f


def sheet(x, half=100.0):
    """A single open sheet across x (a fence)."""
    v = np.array([[x, -half, -half], [x, half, -half], [x, half, half], [x, -half, half]], float)
    return v, np.array([[0, 1, 2], [0, 2, 3]])


def level(parts, tmp_path):
    """Parts (name, game-frame points, triangles) written as `map` writes them, read back for tracing."""
    out = [(name, to_viewer(p), t) for name, p, t in parts]
    glb.write(tmp_path / "de_test.glb", out)
    return wallbang.load(tmp_path / "de_test.glb")


def test_walls_count_their_thickness_and_surfaces(tmp_path):
    wood = box((100, -100, -100), (108, 100, 100))
    concrete = box((300, -100, -100), (316, 100, 100))
    lv = level([("structure:wood_panel", *wood), ("structure:concrete", *concrete)], tmp_path)
    count, thick, names, grates = lv.trace(np.array([0.0, 0, 0]), np.array([500.0, 0, 0]))
    assert count == 2 and names == ["wood_panel", "concrete"] and grates == 0
    assert thick == pytest.approx(24.0)
    # Along the wall, clear.
    assert lv.trace(np.array([0.0, 150, 0]), np.array([500.0, 150, 0]))[0] == 0


def test_overlapping_pieces_are_one_wall(tmp_path):
    a = box((100, -100, -100), (120, 100, 100))
    b = box((110, -50, -50), (130, 50, 50))
    lv = level([("structure:brick", *a), ("structure:brick", *b)], tmp_path)
    count, thick, names, _ = lv.trace(np.array([0.0, 0, 0]), np.array([500.0, 0, 0]))
    assert count == 1 and thick == pytest.approx(30.0) and names == ["brick"]


def test_a_fence_bullets_pass_is_a_grate_not_a_wall(tmp_path):
    fence = sheet(200.0)
    lv = level([("structure:passbullets:chainlink", *fence)], tmp_path)
    count, thick, names, grates = lv.trace(np.array([0.0, 0, 0]), np.array([500.0, 0, 0]))
    assert (count, grates, names) == (0, 1, [])


def test_a_graze_or_an_open_sheet_is_no_wall(tmp_path):
    lv = level([("structure:metal", *sheet(200.0)), ("structure:wood", *box((300, -100, -100), (300.2, 100, 100)))], tmp_path)
    assert lv.trace(np.array([0.0, 0, 0]), np.array([500.0, 0, 0]))[0] == 0


def test_more_than_a_bullet_passes_is_not_known(tmp_path):
    lv = level([("structure:concrete", *box((100, -100, -100), (150, 100, 100))),
                ("structure:solidmetal", *box((100, 300, -100), (102, 500, 100))),
                ("structure:foliage", *box((100, 600, -100), (200, 800, 100)))], tmp_path)
    origins = np.array([[0.0, 0, 0], [0.0, 400, 0], [0.0, 700, 0]])
    points = origins + [500.0, 0, 0]
    c = wallbang.columns(lv, origins, points)
    # 1.27 m of concrete and solid metal: the bullet did not come that way.
    assert np.isnan(c["wallbang"][:2]).all() and list(c["wallSurfaces"][:2]) == ["", ""]
    # A bush is passed like a fence.
    assert (c["wallbang"][2], c["wallGrates"][2]) == (0.0, 1.0)


def test_the_ends_of_the_shot_are_not_traced(tmp_path):
    # A wall the victim leans on (within FAR of the point struck) is not one the shot went through.
    lv = level([("structure:plaster", *box((498, -100, -100), (510, 100, 100)))], tmp_path)
    assert lv.trace(np.array([0.0, 0, 0]), np.array([500.0, 0, 0]))[0] == 0


def test_long_shots_cross_many_cells(tmp_path):
    lv = level([("structure:concrete", *box((3000, 1990, 90), (3010, 2010, 110)))], tmp_path)
    a, b = np.array([0.0, 0, 0]), np.array([6000.0, 4000, 200])
    assert lv.trace(a, b)[0] == 1
    assert lv.trace(a, b + [0, 400, 0])[0] == 0


def test_columns_trace_only_known_shots(tmp_path):
    lv = level([("structure:wood", *box((100, -100, -100), (104, 100, 100)))], tmp_path)
    origins = np.array([[0.0, 0, 0], [0.0, 0, 0], [np.nan] * 3])
    points = np.array([[500.0, 0, 0], [-500.0, 0, 0], [500.0, 0, 0]])
    c = wallbang.columns(lv, origins, points)
    assert list(c["wallbang"][:2]) == [1.0, 0.0] and np.isnan(c["wallbang"][2])
    assert c["wallThickness"][0] == pytest.approx(4 * wallbang.METRES, abs=1e-3)
    assert list(c["wallSurfaces"]) == ["wood", "", ""]
    none = wallbang.columns(None, origins, points)
    assert np.isnan(none["wallbang"]).all() and set(none["wallSurfaces"]) == {""}


def test_the_hurt_row_gives_the_shot_from_the_eye_to_the_point_struck():
    row = {"tick": 100, "hitgroup": "head", "attacker_steamid": "1", "user_X": 0.0, "user_Y": 0.0, "user_Z": 0.0,
           "user_yaw": 180.0, "user_duck_amount": 0.0, "attacker_X": -500.0, "attacker_Y": 0.0, "attacker_Z": 0.0,
           "attacker_pitch": 0.0, "attacker_yaw": 0.0, "attacker_duck_amount": 0.0}
    p = impact.hit_points(pd.DataFrame([row]), None)
    assert (p["_fromX"][0], p["_fromZ"][0]) == (-500.0, impact.EYE)
    # The face, in front of the victim's standing point, at eye height.
    assert -10 < p["_atX"][0] < 0 and p["_atZ"][0] == pytest.approx(64, abs=1.5)


def test_pass_bullet_groups_are_kept_apart_in_the_export():
    assert surface_of("physics_passbullets_window_chainlink", {"SurfaceProperty": "chainlink",
                                                               "InteractAs": ["passbullets", "window"]}) == "passbullets:chainlink"
    assert surface_of("physics_group_metal", {"SurfaceProperty": "metal", "InteractAs": []}) == "metal"
    assert surface_of("physics_csgo_grenadeclip", {"SurfaceProperty": "default", "InteractAs": ["csgo_grenadeclip"]}) is None
    wall = np.array([[0, 0, 0], [0, 100, 0], [0, 100, 100], [0, 0, 100]], float) * 0.0254
    tris = np.array([[0, 1, 2], [0, 2, 3]])
    names = {n for n, _, _ in parts_from([("physics_passbullets_metal", {"SurfaceProperty": "metal", "InteractAs": ["passbullets"]}, wall, tris),
                                          ("physics_group_metal", wall, tris)])}
    assert names == {"structure:passbullets:metal", "structure:metal"}


def test_the_level_is_found_in_the_levels_folder(tmp_path):
    (tmp_path / "cs2").mkdir()
    (tmp_path / "cs2" / "de_test.glb").write_bytes(b"")
    assert wallbang.find("de_test", tmp_path) == tmp_path / "cs2" / "de_test.glb"
    assert wallbang.find("de_other", tmp_path) is None
    assert wallbang.find("", tmp_path) is None


def hits(**columns):
    """Hurt rows: an AK-47 (item 7) chest hit on an unarmoured enemy, unless told otherwise."""
    n = max(len(v) if isinstance(v, list) else 1 for v in columns.values()) if columns else 1
    row = {"dmg_health": 35, "dmg_armor": 0, "armor": 0, "hitgroup": "chest", "weapon": "ak47", "attacker_team_num": 2, "user_team_num": 3}
    row.update(columns)
    return pd.DataFrame({k: v if isinstance(v, list) else [v] * n for k, v in row.items()})


def test_the_damage_says_whether_anything_was_passed():
    # An AK-47's 36 points lose 2 % per 500 units flown: at 500 units a chest hit deals 35.
    flown = np.full(6, 500.0)
    h = hits(dmg_health=[35, 31, 27, 141, 10, 11], dmg_armor=[0, 0, 4, 0, 0, 0], armor=[0, 0, 96, 0, 0, 0],
             hitgroup=["chest", "chest", "chest", "head", "chest", "chest"], attacker_team_num=[2, 2, 2, 2, 3, 3])
    lost = wallbang.damage_lost(h, np.full(6, 7.0), flown)
    # Full damage; 4 short (anything passed costs more); through armour (ratio 1.55: 77.5 %) in full; a bare head
    # (x4); a team-mate's third, short and in full.
    assert list(lost) == [0.0, 1.0, 0.0, 0.0, 1.0, 0.0]


def test_the_damage_cannot_tell_without_the_weapon_or_a_place():
    h = hits(weapon=["m4a1", "ak47", "ak47", "hegrenade"], hitgroup=["chest", "generic", "chest", "chest"], dmg_health=[30, 30, 0, 30])
    lost = wallbang.damage_lost(h, np.full(4, np.nan), np.full(4, 500.0))
    # `m4a1` is the M4A4 or the M4A1-S: not known by name alone; nor a hit with no place, no damage, or a grenade.
    assert np.isnan(lost).all()
    # The shot's item number tells the M4A1-S (60): 38 points, 6 % lost per 500 units.
    assert wallbang.damage_lost(hits(weapon="m4a1", dmg_health=35), np.array([60.0]), np.array([500.0]))[0] == 0.0


def test_the_damage_decides_and_the_trace_says_what_was_passed(tmp_path):
    lv = level([("structure:wood_panel", *box((100, -100, -100), (104, 100, 100))),
                ("structure:passbullets:metalrailing", *sheet(200.0, half=20.0))], tmp_path)
    origins = np.zeros((4, 3))
    points = np.array([[500.0, 100, 0], [500.0, 100, 0], [500.0, 0, 0], [-500.0, 0, 0]])
    flown = np.linalg.norm(points, axis=1)
    full = int(36 * 0.98 ** (flown[0] / 500))
    h = hits(dmg_health=[full, 20, full, 10])
    c = wallbang.columns(lv, origins, points, h, np.full(4, 7.0))
    # Full damage through the traced wood: the line was off, no wallbang. Short: through the wood. Full damage
    # through a railing: the game counts it. Short with nothing on the line: through something not in the level.
    assert list(c["wallbang"]) == [0.0, 1.0, 1.0, 1.0]
    assert list(c["wallSurfaces"]) == ["", "wood_panel", "metalrailing", ""]
    assert c["wallCount"][0] == 0 and c["wallCount"][1] == 1 and np.isnan(c["wallCount"][3])
    # Without a level, the damage alone.
    alone = wallbang.columns(None, origins, points, h, np.full(4, 7.0))
    assert list(alone["wallbang"]) == [0.0, 1.0, 0.0, 1.0] and np.isnan(alone["wallCount"]).all()


def test_hashed_surface_names_are_put_back():
    from heat3d_cs2.mapexport import murmur2, surface_name

    assert murmur2(b"default") == 1977497166
    assert surface_name("vrf_unknown_key_2838185980") == "metalrailing"
    assert surface_name("vrf_unknown_key_12") == "vrf_unknown_key_12"
