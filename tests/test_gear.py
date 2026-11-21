import numpy as np

from heat3d_cs2.gear import _resolved, _side, hit_regions, item_turn, parse_kv, to_frame, unit_parts, weapons_vdata
from heat3d_cs2.modelpack import lods_of, norm_key


def test_keyvalues_nested_with_comments_and_conditions():
    kv = parse_kv('"a" { "b" "1" // note\n "c" { "d" "x y" } [$WIN32] "e" "2" }')
    assert kv == {"a": {"b": "1", "c": {"d": "x y"}, "e": "2"}}


def test_prefabs_merge_under_the_item():
    prefabs = {"rifle": {"visuals": {"weapon_type": "Rifle"}, "used_by_classes": {"terrorists": "1"}}}
    it = _resolved({"prefab": "rifle", "name": "weapon_x", "used_by_classes": {"counter-terrorists": "1"}}, prefabs)
    assert it["visuals"]["weapon_type"] == "Rifle"
    assert _side(it) == "both"


def test_weapons_vdata_values():
    text = "{\n\tweapon_x = \n\t{\n\t\tm_nPrice = 2700\n\t\tm_flCycleTime = [ 0.1 ]\n\t\tm_bIsFullAuto = true\n\t\tm_szName = \"weapon_x\"\n\t}\n}\n"
    v = weapons_vdata(text)["weapon_x"]
    assert v == {"m_nPrice": 2700, "m_flCycleTime": 0.1, "m_bIsFullAuto": True, "m_szName": "weapon_x"}


def test_frame_is_a_rotation():
    # glTF (x left, y up, z forward) -> figure (x forward, y up, z right)
    assert to_frame(np.array([[1.0, 2.0, 3.0]])).tolist() == [[3.0, 2.0, -1.0]]


def test_hit_capsules_grouped_by_height():
    def box(c, s=0.05):
        v = np.array([[x, y, z] for x in (-s, s) for y in (-s, s) for z in (-s, s)]) + c
        f = np.array([[0, 1, 2], [1, 3, 2], [4, 6, 5], [5, 6, 7], [0, 4, 1], [1, 4, 5]])
        return v, f
    # glTF frame: y up, x to the model's left
    meshes = [("p", *box([0, 1.85, 0])), ("p", *box([0, 1.4, 0])), ("p", *box([0, 1.0, 0])),
              ("p", *box([0.1, 0.4, 0])), ("p", *box([-0.1, 0.4, 0])), ("p", *box([0, 0.0, 0]))]
    groups = [g for g, *_ in hit_regions(meshes)]
    assert groups[:3] == ["head", "chest", "stomach"]
    assert {"left_leg", "right_leg"} <= set(groups)


def test_levels_of_detail_within_budget():
    n = 80
    x, z = np.meshgrid(np.linspace(0, 1, n), np.linspace(0, 1, n))
    v = np.stack([x.ravel(), 0.1 * np.sin(6 * x.ravel()) * np.cos(5 * z.ravel()), z.ravel()], 1)
    a = (np.arange(n - 1)[:, None] * n + np.arange(n - 1)[None, :]).ravel()
    f = np.concatenate([np.stack([a, a + n, a + 1], 1), np.stack([a + 1, a + n, a + n + 1], 1)])
    lods = lods_of({"hull": (v, f)}, "item")
    assert [sum(len(x[1]) for x in lod.values()) <= b for lod, b in zip(lods, (3000, 800, 200))] == [True] * 3
    assert norm_key("T-72B3") == "t72b3"


def test_weapon_keeps_one_of_two_bodies():
    tri = (np.array([[0.0, 0, 0], [0, 1, 0], [0, 0, 1]]), np.array([[0, 1, 2]]))
    meshes = [("w.body_legacy", *tri), ("w.body_legacy", *tri), ("w.body_hd", *tri)]
    assert len(unit_parts("weapon", meshes)["hull"][1]) == 2
    assert len(unit_parts("weapon", [("w.body_hd", *tri)])["hull"][1]) == 1


def _blade(tip_axis: int, tip: float, edge_axis: int, edge: float):
    """A thin blade in the glTF frame: grip at the origin, tip at `tip` along one axis, edge toward the other."""
    v = np.zeros((4, 3))
    v[1, tip_axis] = tip
    v[2, edge_axis] = edge
    v[3, edge_axis] = -edge / 4  # the spine, thicker and shorter than the edge's reach
    return [("k.body_legacy", v, np.array([[0, 1, 2], [0, 3, 1]]))]


def test_items_lie_like_the_guns():
    # A knife's world model stands along the fist (glTF y), edge toward the hand's forward (glTF z): it comes out
    # tip toward +x, edge down, still flat in x-y.
    v, _ = unit_parts("weapon", _blade(1, 0.25, 2, 0.04), "knife", "weapons/models/knife/k/weapon_knife_k.vmdl_c")["hull"]
    assert np.allclose(v[1], [0.25, 0, 0]) and np.allclose(v[2], [0, -0.04, 0]) and np.allclose(v[:, 2], 0)
    # A gun already lies barrel forward (glTF z) and is left as it is.
    v, _ = unit_parts("weapon", _blade(2, 0.6, 1, -0.1), "rifle", "weapons/models/ak47/weapon_rif_ak47.vmdl_c")["hull"]
    assert np.allclose(v[1], [0.6, 0, 0]) and np.allclose(v[2], [0, -0.1, 0])
    # The health shot's needle (down along the fist) and the armour's front (glTF -x) turned to +x.
    v, _ = unit_parts("weapon", _blade(1, -0.08, 2, 0.01), "equipment", "weapons/models/healthshot/weapon_healthshot.vmdl_c")["hull"]
    assert np.allclose(v[1], [0.08, 0, 0])
    v, _ = unit_parts("weapon", _blade(0, -0.15, 1, 0.3), "equipment", "models/weapons/w_eq_armor.vmdl_c")["hull"]
    assert np.allclose(v[1], [0.15, 0, 0]) and np.allclose(v[2], [0, 0.3, 0])
    # Every turn is a rotation (the winding and handedness stay); the C4 and the taser are not turned.
    for cls, model in (("knife", ""), ("grenade", ""), ("equipment", "x/weapon_healthshot.vmdl"),
                       ("equipment", "weapons/models/defuser/defuser.vmdl_c")):
        m = item_turn(cls, model)
        assert m is not None and np.allclose(m @ m.T, np.eye(3)) and np.isclose(np.linalg.det(m), 1)
    assert item_turn("c4", "weapons/models/c4/weapon_c4.vmdl_c") is None
    assert item_turn("taser", "weapons/models/taser/weapon_pist_taser.vmdl_c") is None
    assert item_turn("equipment", "weapons/models/other/weapon_other.vmdl_c") is None
