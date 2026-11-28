"""The view sidecar's line of sight: walls, smoke and the masks, on made-up geometry."""

import numpy as np

from heat3d_cs2 import view


def wall(x, half=200.0, z0=-50.0, z1=200.0):
    """A sheet across x as two triangles, (2, 3, 3) in the game's frame."""
    a, b, c, d = [x, -half, z0], [x, half, z0], [x, half, z1], [x, -half, z1]
    return np.array([[a, b, c], [a, c, d]], float)


def floor_far():
    """A small far-off triangle so the grid spans the test's space."""
    return np.array([[[-400, -400, -60], [600, -400, -60], [600, 600, -60]]], float)


def occluder(*walls):
    return view.Occluder(np.concatenate([*walls, floor_far()]))


def test_a_wall_blocks_the_line_across_it_and_not_one_beside_it():
    occ = occluder(wall(100.0, half=50.0))
    a = np.array([[0.0, 0, 50], [0.0, 120, 50]])
    b = np.array([[300.0, 0, 50], [300.0, 120, 50]])
    assert occ.blocked(a, b).tolist() == [True, False]


def test_a_line_in_a_solid_cube_that_misses_its_triangle_is_clear():
    # The wall's edge at y = 50: a line at y = 56 shares its cubes (12 units) but passes it.
    occ = occluder(wall(100.0, half=50.0))
    a = np.array([[0.0, 56.0, 50]])
    b = np.array([[300.0, 56.0, 50]])
    assert occ.blocked(a, b).tolist() == [False]


def test_the_ends_of_a_line_are_not_looked_at():
    # A wall 10 units in front of the eye: a player pressed to it is not hidden by it.
    occ = occluder(wall(10.0))
    assert occ.blocked(np.array([[0.0, 0, 50]]), np.array([[300.0, 0, 50]])).tolist() == [False]
    occ = occluder(wall(40.0))
    assert occ.blocked(np.array([[0.0, 0, 50]]), np.array([[300.0, 0, 50]])).tolist() == [True]


def test_smoke_blocks_while_it_stands():
    smokes = np.array([[150.0, 0, 60, 10.0, 20.0, 1]])
    a = np.array([[0.0, 0, 60]] * 3)
    b = np.array([[300.0, 0, 60], [300.0, 0, 60], [300.0, 400, 60]])
    t = np.array([15.0, 25.0, 15.0])
    assert view.smoked(a, b, t, smokes).tolist() == [True, False, False]


def test_an_he_grenade_clears_a_smoke_for_a_moment():
    smokes = np.array([[150.0, 0, 60, 10.0, 20.0, 1]])
    a = np.array([[0.0, 0, 60]] * 2)
    b = np.array([[300.0, 0, 60]] * 2)
    t = np.array([15.5, 18.0])
    assert view.smoked(a, b, t, smokes, clears=[(0, 15.0, 16.5)]).tolist() == [False, True]


def test_masks_say_which_enemies_were_in_sight_tick_by_tick():
    occ = occluder(wall(100.0, half=40.0))
    # Slot 0 (team 2) at the origin; slot 1 (team 3) walks out from behind the wall; slot 2 (team 2) a team-mate.
    ticks, slots, teams, pos = [], [], [], []
    for tk in range(0, 17):
        y1 = tk * 12.0  # behind the wall until the line to its side clears the edge at y = 40
        for s, team, p in ((0, 2, (0.0, 0.0, 0.0)), (1, 3, (200.0, y1, 0.0)), (2, 2, (0.0, 300.0, 0.0))):
            ticks.append(tk)
            slots.append(s)
            teams.append(team)
            pos.append(p)
    ticks, slots, teams, pos = np.array(ticks), np.array(slots), np.array(teams), np.array(pos)
    sees, smoky = view.sight_masks(ticks, slots, teams, pos, np.zeros(len(ticks)), ticks / 64.0, occ, np.zeros((0, 6)))
    obs0 = sees[slots == 0]
    # Hidden at first, in sight later; never sees a team-mate.
    assert obs0[0] == 0 and obs0[-1] == 0b10
    assert all(m in (0, 0b10) for m in obs0)
    first = int(np.argmax(obs0 == 0b10))
    assert all(obs0[first:] == 0b10)
    # Slot 2 has a clear line to slot 1 throughout (the wall is not between them at their places).
    assert all(sees[slots == 2] == 0b10)
    assert not smoky.any()
    # The in-between ticks (not multiples of EVERY) are checked where the line changed: the switch is exact.
    direct = [view.clear_lines(occ, view.eye_of(pos[(ticks == k) & (slots == 0)], np.zeros(1)),
                               pos[(ticks == k) & (slots == 1)], np.zeros(1), np.zeros(1), np.zeros((0, 6)))[1][0]
              for k in range(17)]
    assert first == direct.index(True)
