
# Map export (`map`)

`python -m heat3d_cs2 map <map> -o <file.glb>` writes a CS2 map as level
geometry: the world's **collision mesh**, in the frame and units the
[heatmap tables](output-table) are drawn in. Code:
[`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py),
[`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py).
Options and messages: [Commands](commands#map---a-maps-geometry-as-glb).

## Why the collision mesh

The collision mesh is what players stand on and hide behind - floors, walls,
stairs, boxes - without the decoration: no props that only look like
something, no textures, far fewer triangles than the render meshes. That is
what a heatmap needs under it: something to read positions against, not a
rendering of the map.

## How it is obtained

1. **Find the map.** A path ending in `.vpk` that exists is used as given.
   Otherwise `<name>.vpk` is looked for in
   `<CS2 folder>\game\csgo\maps\`, where the CS2 folder is `--game`, or
   `steamapps\common\Counter-Strike Global Offensive` in every Steam library
   found (see [Installing](installing#where-cs2-is-looked-for)).
2. **Find Source2Viewer's CLI**: `--source2viewer`, then
   `HEAT3D_SOURCE2VIEWER`, then `Source2Viewer-CLI` / `Source2Viewer-CLI.exe`
   on `PATH`.
3. **Export the world's physics.** Source2Viewer is run as

   ```text
   Source2Viewer-CLI -i <map>.vpk -d -f maps/<map>/world_physics.vmdl_c --gltf_export_format glb -o <temporary folder>
   ```

   It decodes Source 2's compiled physics from the map's own archive and
   writes the model (empty: the world has no render mesh of its own) and its
   physics beside it. The largest `.glb` written is the physics. If
   Source2Viewer fails or writes no `.glb`, the command stops and shows the
   last 800 characters of its output and of its errors.
4. **Read it.** Every node of the scene is walked with its transform
   (matrix, or translation-rotation-scale), and every triangle primitive is
   taken, with or without an index buffer, in world positions.
5. **Leave out what is not a wall or a floor.** A node whose name contains
   `clip` - player clips, NPC clips, grenade clips: the invisible walls that
   stop players and grenades - or `sky`, in any case, is dropped.
6. **Name the surface.** The physics groups are named by their surface; the
   name in lower case, with a leading `physics`, `physics_group` or
   `physics_passbullets` (and the underscore after it) removed is the surface:
   `physics_group_concrete` is `concrete`, `physics_passbullets_chainlink` is `chainlink`, a bare
   `physics_group` is `world`. Surfaces bullets pass through are kept.
7. **Back to the game's frame.** Source2Viewer writes glTF in metres with Y
   up: the game's (Y, Z, X) multiplied by 0.0254. That is undone - each point
   becomes the game's (X, Y, Z) in inches.
8. **Split ground from structure**, triangle by triangle: a face whose normal
   points up by at least 0.7 (its Z component, normalised) - slopes up to
   about 45 degrees, roughly the steepest a CS2 player walks - is **ground**;
   everything else, walls and ceilings included, is **structure**.
9. **Into the viewer's frame.** Every point is written as (X, Z, -Y): Y up,
   the game's Y negated - the frame the viewer draws the tables in, when it
   follows their `heat3d` hints. A rotation, not a mirror.
10. **Write the `.glb`.** If nothing is left (only clip brushes), the command
    stops with an error. Otherwise it prints the file, the map, the triangle
    count, how many are ground, and the number of parts.

Nothing here reads anything but the map's own `.vpk`, and nothing of
Source2Viewer is bundled or copied.

## The file

A glTF 2.0 binary (`.glb`), one buffer, written by `heat3d_cs2` (the
`asset.generator`):

| Aspect | What |
|---|---|
| Nodes | one per part, all at the root, no transforms, each with its own mesh of the same name |
| Node names | `ground:<surface>` or `structure:<surface>` (`ground:concrete`, `structure:metal`, `structure:world`), sorted by name |
| Primitives | one per mesh, triangles, `POSITION` (float32, with min/max) and `NORMAL` (float32), `uint32` indices |
| Shading | flat: one vertex per triangle corner, each carrying its triangle's normal |
| Materials, textures, UVs, colours | none |
| Units | game units (**inches**), not metres - unlike what glTF assumes |
| Frame | (X, Z, -Y) of the game: glTF's Y is the game's height, glTF's Z is the game's -Y |

The `ground:` / `structure:` prefix is the convention of all 3DHeat level
exporters: the viewer takes a part named that way at its word instead of
guessing from the geometry, so the floors get the ground shading and the
walls the structure drawing without any classification step.

Because the units are inches, another glTF viewer shows the map about 39
times too large (it reads them as metres); scale by 0.0254 there if it
matters. In 3DHeat it lies exactly under the table, which is in the same
units with scale 1.

## The check that the frame is right

The test `test_players_stand_on_the_exported_floor` (run only when a demo and
Source2Viewer are given, see [Development](development#tests)) exports the
map a demo was played on, takes 300 random position samples of the match, and
for each looks straight down for the highest ground triangle at most 4 units
above the player's feet. It requires that at least 98 % of the samples find
ground, and that the median height above it is under 5 units. A mirrored map
fails it: on a map mirrored by the wrong axis, a large share of the players
stand over nothing. The README reports the figures of this check over the
maps of the current competitive pool.

## What it does not do

- No render geometry, textures or decoration - see *why* above.
- Only what is in the map's `world_physics` model is exported. Whether
  moving parts (doors) or breakables are in it has not been checked.
- No simplification: the 3DHeat viewer simplifies on import with its
  **Simplification target** setting.
- Maps not in the installed game (workshop maps elsewhere on disk) work when
  their `.vpk` is passed as a path and holds `maps/<name>/world_physics.vmdl_c`;
  not verified.
