"""The layouts reader's parts that need no game: the entity dump and the outlines."""

import numpy as np

from heat3d_cs2.layouts import _hull, _yaw, parse_entities

DUMP = """
====1====
bomb_site_designation          "1"
classname                      "func_bomb_target"
origin                         [ 0.0, 0.0, 0.0 ]
model                          resource_name:"maps/de_x/entities/unnamed_1.vmdl"

====2====
enabled                        true
priority                       1
targetname                     "spawnpoints.standard"
classname                      "info_player_terrorist"
origin                         [ 10.5, -20.0, 3.0 ]
angles                         [ 0.0, 90.0, 0.0 ]
@OnMapSpawn Something 0
"""


def test_entity_dump():
    ents = parse_entities(DUMP)
    assert [e["classname"] for e in ents] == ["func_bomb_target", "info_player_terrorist"]
    assert ents[0]["model"] == "maps/de_x/entities/unnamed_1.vmdl"
    assert ents[0]["bomb_site_designation"] == "1"
    assert ents[1]["origin"] == [10.5, -20.0, 3.0]
    assert ents[1]["enabled"] is True and ents[1]["priority"] == 1


def test_outline_and_heading():
    pts = np.array([[0, 0], [10, 0], [10, 10], [0, 10], [5, 5], [2, 8]], float)
    hull = _hull(pts)
    assert len(hull) == 4 and {tuple(p) for p in hull} == {(0, 0), (10, 0), (10, 10), (0, 10)}
    # Facing the game's +x is facing the viewer's +x: a heading of 90.
    assert _yaw([0.0, 0.0, 0.0]) == 90.0
