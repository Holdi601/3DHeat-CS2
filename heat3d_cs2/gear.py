"""
CS2's catalogue and model pack, from the user's own installation.

- `catalog`: every weapon, grenade and piece of equipment (`scripts/weapons.vdata`: class, price, damage, magazine,
  fire rate, armour penetration, speed; names from `scripts/items/items_game.txt` and the English localisation) and
  every agent (the player models), with their side.
- `models`: the agents' third-person bodies and the weapons' world models, exported by Source2Viewer's command line
  and simplified to the viewer's budget, one `.glb` each, with `model-pack.json`.

Source2Viewer writes glTF in metres, Y up, the game's X (forward) as glTF Z and the game's Y (left) as glTF X; the
viewer's figure frame is x forward, y up, z right: (z, y, -x) of the glTF, a rotation, so the winding stays.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from .mapexport import GAME_FOLDER, find_source2viewer, steam_libraries
from .modelpack import Pack, levels_dir, merge, write_catalog
from .vpk import Vpk

SOURCE = "heat3d-cs2"


def _version() -> str:
    try:
        return (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "?"
WEAPON_CLASS = {
    "WEAPONTYPE_PISTOL": "pistol", "WEAPONTYPE_SUBMACHINEGUN": "smg", "WEAPONTYPE_RIFLE": "rifle",
    "WEAPONTYPE_SHOTGUN": "shotgun", "WEAPONTYPE_SNIPER_RIFLE": "sniper", "WEAPONTYPE_MACHINEGUN": "lmg",
    "WEAPONTYPE_KNIFE": "knife", "WEAPONTYPE_GRENADE": "grenade", "WEAPONTYPE_C4": "c4", "WEAPONTYPE_TASER": "taser",
    "WEAPONTYPE_EQUIPMENT": "equipment", "WEAPONTYPE_STACKABLEITEM": "equipment", "WEAPONTYPE_BREACHCHARGE": "equipment",
    "WEAPONTYPE_SHIELD": "equipment", "WEAPONTYPE_FISTS": "melee", "WEAPONTYPE_MELEE": "melee",
}
VISUAL_CLASS = {"pistol": "pistol", "submachinegun": "smg", "rifle": "rifle", "shotgun": "shotgun",
                "sniperrifle": "sniper", "machinegun": "lmg", "knife": "knife", "grenade": "grenade", "c4": "c4",
                "taser": "taser", "equipment": "equipment", "stackableitem": "equipment", "fists": "melee",
                "melee": "melee", "breachcharge": "equipment", "shield": "equipment"}
#: The agents' model folders and the units they belong to, for the agents whose item has no name of its own.
FACTIONS = {"ctm_fbi": "FBI", "ctm_sas": "SAS", "ctm_st6": "SEAL Team 6", "ctm_swat": "SWAT", "ctm_gign": "GIGN",
            "ctm_gsg9": "GSG-9", "ctm_idf": "IDF", "ctm_gendarmerie": "Gendarmerie Nationale", "ctm_diver": "SEAL Frogmen",
            "ctm_heavy": "Heavy Assault (CT)", "tm_phoenix": "Phoenix", "tm_leet": "Elite Crew", "tm_balkan": "Sabre",
            "tm_anarchist": "Anarchists", "tm_pirate": "Pirates", "tm_professional": "The Professionals",
            "tm_separatist": "Separatists", "tm_jumpsuit": "Jumpsuit", "tm_jungle_raider": "Guerrilla Warfare",
            "tm_phoenix_heavy": "Heavy Assault (T)"}
NUMBERS = {"m_nPrice": "price", "m_nDamage": "damage", "m_iMaxClip1": "magazine", "m_flCycleTime": "cycle",
           "m_flArmorRatio": "armourRatio", "m_flPenetration": "penetration", "m_flRange": "range",
           "m_flRangeModifier": "rangeModifier", "m_flMaxSpeed": "maxSpeed", "m_nKillAward": "killAward",
           "m_flHeadshotMultiplier": "headshot", "m_nNumBullets": "pellets", "m_bIsFullAuto": "fullAuto"}


def find_game(given: str | None = None) -> Path:
    """The CS2 install's `game/csgo` folder."""
    folders = [Path(given)] if given else [lib / "steamapps" / "common" / GAME_FOLDER for lib in steam_libraries()]
    for f in folders:
        for c in (f / "game" / "csgo", f / "csgo", f):
            if (c / "pak01_dir.vpk").is_file() and (c / "gameinfo.gi").is_file():
                return c
    raise FileNotFoundError("no CS2 install found (game/csgo/pak01_dir.vpk) - pass --game <CS2 folder>")


def game_build(csgo: Path) -> str:
    try:
        inf = dict(l.split("=", 1) for l in (csgo / "steam.inf").read_text().splitlines() if "=" in l)
        return f"{inf.get('PatchVersion', '?')}-{inf.get('ClientVersion', '?')}"
    except OSError:
        return "unknown"


# --- KeyValues (items_game.txt, the localisation) -------------------------------------------------------------------

_KV_TOKEN = re.compile(r'"((?:[^"\\]|\\.)*)"|([{}])|//[^\n]*|\[[^\]\n]*\]|([^\s{}"]+)')


def parse_kv(text: str) -> dict:
    """KeyValues text as nested dicts; a key given twice keeps both, the later one's fields merged over."""
    root: dict = {}
    stack = [root]
    key = None
    for m in _KV_TOKEN.finditer(text):
        s, brace, bare = m.group(1), m.group(2), m.group(3)
        if brace == "{":
            d = stack[-1].get(key)
            if not isinstance(d, dict):
                d = {}
                stack[-1][key] = d
            stack.append(d)
            key = None
        elif brace == "}":
            if len(stack) > 1:
                stack.pop()
            key = None
        elif s is not None or bare is not None:
            tok = s if s is not None else bare
            if key is None:
                key = tok
            else:
                stack[-1][key] = tok
                key = None
    return root


def localisation(vpk: Vpk) -> dict[str, str]:
    raw = vpk.read("resource/csgo_english.txt")
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8-sig", "replace")
    tokens = parse_kv(text).get("lang", {}).get("Tokens", {})
    return {k.lower(): v for k, v in tokens.items() if isinstance(v, str)}


def _resolved(defs: dict, prefabs: dict, depth: int = 0) -> dict:
    """An item with its prefabs' fields under its own (prefab chains, several prefabs per item)."""
    out: dict = {}
    for p in (defs.get("prefab") or "").split():
        if p in prefabs and depth < 12:
            for k, v in _resolved(prefabs[p], prefabs, depth + 1).items():
                out[k] = v
    for k, v in defs.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = {**out[k], **v}
        else:
            out[k] = v
    return out


def _side(item: dict) -> str:
    c = {k.lower() for k, v in (item.get("used_by_classes") or {}).items() if str(v) != "0"}
    t, ct = "terrorists" in c, "counter-terrorists" in c
    return "both" if t and ct else "T" if t else "CT" if ct else ""


# --- weapons.vdata (KV3 text, decompiled by Source2Viewer) ----------------------------------------------------------

_VALUE = re.compile(r'^\t\t(m_\w+) = (.+)$')


def _kv3_value(s: str):
    s = s.strip()
    if s.startswith("["):
        vals = [_kv3_value(x) for x in s.strip("[] ").split(",") if x.strip()]
        return vals[0] if len(vals) == 1 else vals
    if ":" in s and s.split(":", 1)[0].isidentifier() and '"' in s:
        s = s.split(":", 1)[1]
    s = s.strip('"')
    if s in ("true", "false"):
        return s == "true"
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def weapons_vdata(text: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^\t(\w+) = ?$", line)
        if m:
            cur = out.setdefault(m.group(1), {})
            continue
        m = _VALUE.match(line)
        if m and cur is not None:
            cur[m.group(1)] = _kv3_value(m.group(2))
    return out


def _s2v_text(tool: Path, pak: Path, inner: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out.txt"
        run = subprocess.run([str(tool), "-i", str(pak), "-d", "-f", inner, "-o", str(out)],
                             capture_output=True, text=True, timeout=300, cwd=tmp)
        if not out.is_file():
            raise RuntimeError(f"Source2Viewer did not decompile {inner}:\n{run.stdout[-600:]}{run.stderr[-600:]}")
        return out.read_text(encoding="utf-8", errors="replace")


def build_catalog(csgo: Path, tool: Path, vdata_text: str | None = None) -> tuple[list[dict], dict]:
    """The catalogue's items, and per item the model path inside the package (for `models`)."""
    pak = csgo / "pak01_dir.vpk"
    vpk = Vpk(pak)
    loc = localisation(vpk)
    ig = parse_kv(vpk.read("scripts/items/items_game.txt").decode("utf-8-sig", "replace")).get("items_game", {})
    prefabs = ig.get("prefabs", {})
    if vdata_text is None:
        try:
            vdata_text = _s2v_text(tool, pak, "scripts/weapons.vdata_c")
        except RuntimeError:
            print("note: this Source2Viewer cannot read the game's weapons.vdata (update Source2Viewer, or pass --vdata "
                  "<decompiled weapons.vdata>); the catalogue is written without prices, damage and the other numbers")
            vdata_text = ""
    vdata = weapons_vdata(vdata_text)
    name_of = lambda tok: loc.get(str(tok or "").lstrip("#").lower(), "")  # noqa: E731
    items: list[dict] = []
    models: dict[str, str] = {}
    seen = set()
    for _num, defs in (ig.get("items") or {}).items():
        if not isinstance(defs, dict):
            continue
        it = _resolved(defs, prefabs)
        nm = it.get("name", "")
        if nm.startswith("weapon_") and str(defs.get("baseitem", "0")) == "1" or nm in vdata and nm not in seen:
            if nm in seen:
                continue
            v = vdata.get(nm, {})
            cls = WEAPON_CLASS.get(str(v.get("m_WeaponType", "")), "") or VISUAL_CLASS.get(
                str((it.get("visuals") or {}).get("weapon_type", "")).lower(), "")
            if not cls:
                cls = "knife" if "knife" in nm or "bayonet" in nm else "equipment"
            label = name_of(it.get("item_name")) or nm.replace("weapon_", "").upper()
            nums = {o: v[k] for k, o in NUMBERS.items() if k in v}
            model = str(v.get("m_szWorldModel") or it.get("model_world") or it.get("model_player") or "")
            e = {"id": nm, "kind": "weapon", "name": label, "class": cls, "nation": _side(it), "key": label,
                 "numbers": nums}
            if v.get("m_nPrimaryAmmoType"):
                e["ammo"] = v["m_nPrimaryAmmoType"]
            items.append(e)
            seen.add(nm)
            if model:
                models[nm] = model
        elif str(defs.get("model_player", "")).startswith("agents/") and nm.startswith("customplayer_"):
            uid = nm[len("customplayer_"):]
            if uid in seen:
                continue
            label = name_of(it.get("item_name")) or uid
            folder = max((f for f in FACTIONS if uid.startswith(f)), key=len, default=uid)
            group = label.split(" | ", 1)[1] if " | " in label else FACTIONS.get(folder, folder)
            if label.lower().startswith("default ") or label == uid:
                variant = uid[len(folder):].strip("_").replace("variant", "").replace("var", "")
                label = f"{group} ({variant.upper()})" if variant else group
            items.append({"id": uid, "kind": "person", "name": label, "class": "agent", "group": group,
                          "nation": _side(it), "key": uid, "numbers": {}, "rarity": it.get("item_rarity", "")})
            seen.add(uid)
            models[uid] = it["model_player"]
    return items, models


# --- models ---------------------------------------------------------------------------------------------------------

def _read_glb(path: Path) -> list[tuple[str, np.ndarray, np.ndarray]]:
    """Every mesh primitive of a glb, with its node's world transform applied: (mesh name, verts, faces)."""
    b = path.read_bytes()
    n = struct.unpack("<I", b[12:16])[0]
    g = json.loads(b[20:20 + n])
    binoff = 20 + n + 8
    out = []

    def acc(i):
        a = g["accessors"][i]
        bv = g["bufferViews"][a["bufferView"]]
        dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[a["componentType"]]
        w = {"VEC3": 3, "SCALAR": 1, "VEC4": 4, "VEC2": 2}[a["type"]]
        at = binoff + bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        stride = bv.get("byteStride")
        if stride and stride != w * np.dtype(dt).itemsize:
            raw = np.frombuffer(b, np.uint8, a["count"] * stride, at).reshape(-1, stride)[:, :w * np.dtype(dt).itemsize]
            return np.ascontiguousarray(raw).view(dt).reshape(a["count"], w)
        return np.frombuffer(b, dt, a["count"] * w, at).reshape(a["count"], w) if w > 1 else np.frombuffer(b, dt, a["count"], at)

    def walk(i, m):
        nd = g["nodes"][i]
        local = np.array(nd["matrix"], np.float64).reshape(4, 4).T if "matrix" in nd else np.eye(4)
        if "matrix" not in nd and ("translation" in nd or "rotation" in nd or "scale" in nd):
            from math import isfinite  # noqa: F401
            x, y, z, w = nd.get("rotation", [0, 0, 0, 1])
            r = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                          [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                          [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
            local = np.eye(4)
            local[:3, :3] = r * np.array(nd.get("scale", [1, 1, 1]))
            local[:3, 3] = nd.get("translation", [0, 0, 0])
        m = m @ local
        if "mesh" in nd:
            mesh = g["meshes"][nd["mesh"]]
            for p in mesh["primitives"]:
                if p.get("mode", 4) != 4 or "indices" not in p:
                    continue
                v = acc(p["attributes"]["POSITION"]).astype(np.float64)
                v = v @ m[:3, :3].T + m[:3, 3]
                out.append((mesh.get("name") or nd.get("name") or "", v, acc(p["indices"]).astype(np.int64).reshape(-1, 3)))
        for c in nd.get("children", []):
            walk(c, m)

    for r in g["scenes"][g.get("scene", 0)]["nodes"]:
        walk(r, np.eye(4))
    return out


def to_frame(v: np.ndarray) -> np.ndarray:
    return np.stack([v[:, 2], v[:, 1], -v[:, 0]], 1)


def export_glb(tool: Path, pak: Path, inner: str, tmp: Path) -> Path:
    out = tmp / (Path(inner).stem + ".glb")
    run = subprocess.run([str(tool), "-i", str(pak), "-d", "-f", inner, "--gltf_export_format", "glb", "-o", str(out)],
                         capture_output=True, text=True, timeout=600, cwd=tmp)
    if not out.is_file():
        raise RuntimeError(f"not exported: {(run.stdout + run.stderr).strip().splitlines()[-1:]}")
    return out


_SKIP_AGENT = re.compile(r"firstperson|defusekit|_arms$|viewmodel", re.I)


#: CS2's hit groups, as the demos' damage events name them, and how a hit capsule is put in one: by where its
#: centre is, as a share of the model's height (y) and off the middle (z, metres; negative = the model's left).
HIT_GROUPS = ("head", "chest", "stomach", "left_arm", "right_arm", "left_leg", "right_leg")


def _components(v: np.ndarray, f: np.ndarray) -> list[np.ndarray]:
    """The triangles of each separate piece of a mesh (the hit capsules), by shared vertices."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    n = len(v)
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]]])
    _, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)), directed=False)
    tl = lab[f[:, 0]]
    return [np.nonzero(tl == k)[0] for k in np.unique(tl)]


def hit_regions(meshes: list) -> list:
    """The agent's hit capsules (its physics model) grouped into CS2's hit groups, as `dm` nodes."""
    v, f = merge([(v, f) for _, v, f in meshes])
    if not len(f):
        return []
    from .modelpack import weld

    v, f = weld(to_frame(v), f, 1e-4)
    h = float(v[:, 1].max() - v[:, 1].min()) or 1.0
    base = float(v[:, 1].min())
    groups: dict[str, list] = {}
    for tri in _components(v, f):
        c = v[np.unique(f[tri])].mean(0)
        y = (c[1] - base) / h
        side = "left" if c[2] < 0 else "right"
        if y > 0.83:
            g = "head"
        elif abs(c[2]) > 0.17 and y > 0.42:
            g = f"{side}_arm"
        elif y < 0.48:
            g = f"{side}_leg"
        elif y > 0.63:
            g = "chest"
        else:
            g = "stomach"
        groups.setdefault(g, []).append(f[tri])
    out = []
    for g in HIT_GROUPS:
        if g in groups:
            ff = np.concatenate(groups[g])
            vv, f2 = weld(v, ff, 1e-5)
            vv[:, 1] -= base
            out.append((g, vv, f2, {"part": "hull", "group": g}))
    return out


def unit_parts(kind: str, meshes: list) -> dict:
    if kind == "person":
        keep = [(v, f) for n, v, f in meshes if not _SKIP_AGENT.search(n.rsplit(".", 1)[-1])]
    else:
        # A weapon's world model: everything; the viewer's frame puts the barrel along x.
        keep = [(v, f) for _, v, f in meshes]
    v, f = merge(keep)
    if not len(f):
        return {}
    v = to_frame(v)
    if kind == "person":
        v[:, 1] -= v[:, 1].min()  # stands on its feet
    return {"hull": (v, f)}


def run_catalog(game: str | None, out: str | None, s2v: str | None, vdata: str | None = None) -> int:
    csgo = find_game(game)
    tool = find_source2viewer(s2v)
    items, models = build_catalog(csgo, tool, Path(vdata).read_text(encoding="utf-8", errors="replace") if vdata else None)
    folder = Path(out) if out else (levels_dir() / "cs2" if levels_dir() else None)
    if folder is None:
        raise ValueError("no output folder: pass --out or set HEAT3D_LEVELS")
    pack = folder.parent / "model-packs" / "cs2" / "model-pack.json" if not out else None
    have = {}
    if pack and pack.is_file():
        have = json.loads(pack.read_text(encoding="utf-8")).get("units", {})
    for it in items:
        if it["id"] in have:
            it["model"] = f"model-packs/cs2/{have[it['id']]['file']}"
    ver = _version()
    write_catalog(folder / "catalog.json", "cs2", game_build(csgo), f"{SOURCE} {ver}", items)
    kinds: dict[str, int] = {}
    for it in items:
        kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
    print(f"catalogue: {len(items)} items {kinds} -> {folder / 'catalog.json'}")
    return 0


def run_models(game: str | None, out: str | None, s2v: str | None, only: list[str] | None, force: bool) -> int:
    csgo = find_game(game)
    tool = find_source2viewer(s2v)
    items, models = build_catalog(csgo, tool, "")
    folder = Path(out) if out else (levels_dir() / "model-packs" / "cs2" if levels_dir() else None)
    if folder is None:
        raise ValueError("no output folder: pass --out or set HEAT3D_LEVELS")
    ver = _version()
    gb = game_build(csgo)
    pack = Pack(folder, "cs2", gb, f"{SOURCE} {ver}")
    vpk = Vpk(csgo / "pak01_dir.vpk")
    done = failed = same = 0
    by_id = {i["id"]: i for i in items}
    with tempfile.TemporaryDirectory() as tmpd:
        tmp = Path(tmpd)
        for uid, model in sorted(models.items()):
            if only and not any(o.lower() in uid.lower() for o in only):
                continue
            it = by_id[uid]
            inner = model if model.endswith("_c") else model + "_c"
            if inner.lower() not in vpk.entries:
                print(f"  {uid}: model {inner} not in the package")
                failed += 1
                continue
            arc, off, ln, _ = vpk.entries[inner.lower()]
            fp = hashlib.sha1(f"{inner}:{arc}:{off}:{ln}".encode()).hexdigest()[:16]
            if not force and pack.fresh(uid, fp):
                same += 1
                continue
            try:
                glb = export_glb(tool, csgo / "pak01_dir.vpk", inner, tmp)
                parts = unit_parts(it["kind"], _read_glb(glb))
                phys = glb.with_name(glb.stem + "_physics.glb")
                dm = hit_regions(_read_glb(phys)) if it["kind"] == "person" and phys.is_file() else None
                for f in tmp.iterdir():
                    if f.is_file():
                        f.unlink()
                domain = "person" if it["kind"] == "person" else "item"
                e = pack.add(uid, parts, domain, it["class"], key=it["key"], fingerprint=fp, dm=dm,
                             extra={"name": it["name"], "nation": it["nation"], "model": inner})
                done += 1
                print(f"  {uid}: {e['tris']} tris, {e['height']} m tall, {e['length']} m long, {e['dm']} hit groups", flush=True)
            except Exception as ex:  # noqa: BLE001
                failed += 1
                print(f"  {uid}: FAILED {ex}", flush=True)
            if (done + failed) % 20 == 0:
                pack.save()
    pack.save()
    print(f"models: {done} written, {same} unchanged, {failed} failed; {pack.bytes / 1e6:.1f} MB; {pack.index_path}")
    return 0 if done or same or not failed else 1
