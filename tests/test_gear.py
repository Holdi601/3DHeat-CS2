import numpy as np

from heat3d_cs2.gear import _resolved, _side, hit_regions, parse_kv, to_frame, weapons_vdata
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
