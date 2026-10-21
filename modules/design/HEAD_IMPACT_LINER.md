# P-161 Head-first fall protection: standoff check + crown/brow crush liner + visor recess (RL ID, 2026-10-21)
Inputs: T&R FMEA head-impact gate; Controls 2975e93 (11/24 head-first) and f1663cc `controls/fall/l3_headfirst_replay.json` (11 runs, v_normal 3.78–4.91 m/s, nearly vertical; upper-body KE 163–301 J; model m_head 0.48 kg, too light). Head+neck 1.104 kg credited (CONTRACTS row Head). Scripts: `head_standoff_check.py` → `head_standoff_check.json`; `head_impact_liner.py` → `head_impact_liner.json`. Covers only; no mechanism, sensor window or FOV change.

## 1. Standoff (primary, Robot Lab redirect)
Rigid-body pitch sweep of head_shell.stl vs candidate first-contact points (margin = how far the candidate is below the head's lowest point along the floor normal; +ve = candidate first):
| forward pitch θ | chest pad (x147, y1530, existing) | epaulette E1 (x125, y1680, +15 mm proud of shoulder cover) | brow bumper B1 (on head, x115 y1800) |
|---|---|---|---|
| 80° | +83.8 | +36.1 | +5.4 |
| 90° (prone) | +42.3 | +20.3 | +10.3 |
| 95° | +19.9 | +11.1 | +11.6 |
| 100° | **−3.5** | +0.9 | +11.9 |
| 110° | −51.7 | −21.0 | +10.6 |
| 120° | −100.8 | −44.9 | +6.5 |
| 130° | −150.5 | −71.0 | −1.5 |
**Finding (honest trade):** the existing chest pad already lands first for any rigid forward pitch up to ~98°. A head-first contact therefore means the head was ≥ ~100° (past horizontal, crown-down), i.e. the body is near-inverted or neck/waist flexed — consistent with Controls' "nearly vertical" velocities. In that regime no torso/shoulder cover can land first without standing proud of the crown line: an epaulette only buys ~2–3° (to ~101°) at +15 mm, and keeping it first to 120° would need it ~60 mm proud above the shoulder cover — a backpack/pauldron silhouette that breaks the slim look and would intrude on Arms' abduction envelope (SHOULDER_PAD.md: Arms still to confirm pad vs head/cap at max abduction; a torso epaulette sits right in that zone). **Not recommended.** The arm pads (P-051) ride on the arm and only land first if the arms are raised/braced — a Controls behaviour, not a cover.
**Per-run margin: cannot be given yet.** l3_headfirst_replay.json carries v_world only, no body/head orientation at contact. Ask Controls to add torso pitch/roll + neck angles at first contact (and the 1.104 kg rerun); then `head_standoff_check.py` gives a per-run margin directly.
**Conclusion:** the only cover that is reliably first in crown-down contact is on the head itself → crown/brow liner (B1 column) sized below; the 163–301 J upper-body energy must go to a Controls fall strategy (tuck/brace/arms first) — 1.5×301 = 452 J through the head would need ~0.6 m of foam at 100 g and would load the neck far beyond the XM430/6806 path. Flag to Robot Lab/T&R.

## 2. Liner energy (head mass only)
E = ½·1.104·5.0² = 13.8 J (replay max 4.91 → 13.3 J); gate ×1.5 = **20.7 J**. (Floor 6.8 J at 3.52 m/s superseded.) Effective mass: 1.104 kg assumes the neck decouples the body; if Controls' rerun shows body mass coupling, rescale with the json table (E 10–40 J listed).

## 3. Allowable deceleration — NOT closable from published data
| item | published shock rating | source |
|---|---|---|
| ZED X Mini | **none published** (only IMU range ±12 g, IP67, aluminium body) | https://www.stereolabs.com/store/products/zed-x-mini-stereo-camera ; https://static.generation-robots.com/media/zed-x-datasheet-v1.2.pdf |
| Dynamixel XM430-W350 (×2) | **none published** (static: radial 40 N @10 mm from horn, axial 20 N; "Electrical Shock Error" is electrical) | https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm430-w350/ |
| 6806-2RS yaw / 6800-2RS pitch bearings | static rating C0 per manufacturer — not yet pulled (SKF page fetch failed); ask Head owner for the chosen brand's C0 | HEAD_BALANCER.md |
| head PCB | none in head: GMSL2 board JCB022 sits on AGX301 (CONTRACTS Head row); ZED IMU is internal to the camera | CONTRACTS.md |
→ **Ask owners:** Head (ZED shock test level from Stereolabs; bearing C0), Actuators/Head (XM430 shock from ROBOTIS). Limit = lowest ÷ 1.5, TBD. Note: XM430 axial 20 N is a static horn load, not a g rating; the 6806 bearing carries head loads (HEAD_BALANCER.md).
Sizing therefore stated as minimum allowable g it implies.

## 4. Liner sizing (plateau model F = σ·A, usable stroke 0.7·t, E = F·stroke; static σ — EPP rate factor 1.45–1.57 from MATERIALS_DB not applied, conservative for stroke, unconservative for peak g)
| material (MATERIALS_DB) | σ@50% | t | area for 100 g (1083 N) | peak g at that area, 20.7 J |
|---|---|---|---|---|
| Plastazote LD29 (XLPE_LD29) | 126 kPa | **25 mm** | 86 cm² | ≥109 g needed to stop in 17.5 mm |
| EPP80 ARPRO 5170 (EPP80) | 700 kPa | 25 mm | 15.5 cm² | same energy rule; contact area too small to control on a 190 mm dome |
**Proposed:** LD29, 25 mm, crown cap Ø~110 mm (≈95 cm²) + brow band 25 mm×~150×30 — inside a raised CF shell (shell grows ~27 mm at crown/brow; head height +27 mm, look reviewed: reads as a helmet ridge, acceptable). Holds peak ≈ 1200 N / 1.104 kg ≈ **110 g** at full 20.7 J; if the owners' rating ÷1.5 is below ~110 g, thickness scales t ≈ 26 mm × (110/g_allow) (table in json). LD29 max 95 °C OK in head. **Mass +0.012 kg [EST]** (foam ~8 g + bond/skin), shell growth +0.010 → **+0.022 kg** pair-less total, against head line (Arbiter to book). Multi-hit: LD29 is closed-cell XLPE with partial recovery; treat as post-fall inspection item.

## 5. Visor
Rim (CF shell lip + 25 mm brow liner) stands **≥ 20 mm proud** of the visor outer face everywhere on the visor perimeter, so the visor stays clear even at 17.5 mm full liner stroke; visor becomes a **replaceable wear part** (4× M2.5 into shell inserts, gasketed) — T&R post-fall inspection item. Requires Head module check that the brow lip stays outside the ZED FOV (ID does not move the sensor window). Contact-geometry check vs the 24 runs pending Controls orientation data.

## 6. Shell laminate (Materials review)
Proposed **1.5 mm** CF 2×2 twill (≈6 plies 200 gsm, Easy Composites XC110 basis per R-027) [EST]; at brow/crown under the liner add 2 local plies (2.0 mm). Check basis: liner limits contact force to ~1.2 kN spread over ≥86 cm² → ~0.14 MPa contact pressure; shell bending as a clamped plate across liner patch, and puncture against a 10 mm floor-edge indentor at 1.2 kN — Materials to compute with their XC110 allowables.

## Open items
Controls: body/neck orientation at contact + 1.104 kg rerun + coupled effective mass. Head/Actuators: ZED, XM430 shock ratings, bearing C0. Head: FOV vs brow lip. Materials: laminate check, LD29 rate/multi-hit. Arbiter: +0.022 kg [EST]. Robot Lab/T&R: upper-body 163–301 J needs a Controls fall strategy; covers can't take it.
