# R-083: torso EtherCAT junction, 5× Würth 749014012 (0–70 °C) (RL Thermal, 2026-10-14)
Electronics §18.2e (4101f47); Arbiter R-083 sets the limit at **≤ 60 °C worst case**. 35 °C ambient.

## Where it sits and what is near it
- The junction PCB is in the torso on the brain tray, fed by AGX301 1GbE#1 (`electronics/R1_ARCHITECTURE.md` §4). The exact position is not in CAD.
- **Neighbours** (`torso/R1_ARCHITECTURE.md` §10/§13.4, A41):
  - The Thor (120 W) cold plate and the DCM3623 (≈ 14 W loss, on the cold plate) are in the duct.
  - Duct: front-low intake → 2 × 40 mm blowers (~21 CFM, sized for a +10 K air rise) → Thor fins → exhaust high on the upper back under the shoulder bulkhead. The HS200 regen clamp resistor sits on the exhaust side.
  - The pack (11–17 W, +9–12 K) is in the lower chest behind a sealed CFRP partition, upstream.
  - No leg or arm drives are in the torso.
- **Own heat:** transformers ≈ 0; junction PCB ESC/PHYs ≈ 1–2 W [EST], so about +5–8 K board over local air.
- **J-T2 assumptions used:**
  - Duct exhaust is +10 K at full fan.
  - With the fans PWM'd down to walking-load Thor power (Torso §13.4, the runtime lever), the exhaust is ≈ +20 K.
  - Still air outside does not matter much, because the duct is fan-driven.

## Local air / board temperature
| placement | walking | standing still | worst (fans PWM'd low / regen clamp active) | ≤ 60 °C? |
|---|---|---|---|---|
| **in the duct, downstream of Thor / on the exhaust side** | 45 + 6 ≈ 51 | ≈ 52 | 55 + 8 ≈ **63–66** (clamp resistor +5 K local) | **NO** |
| closed pocket beside Thor, no duct flow | — | — | 70–85+ (Thor bay natural 306 W/m² case, R1) | **NO** (fails even 70) |
| **duct intake side, upstream of the blowers** (cold side of the Thor plate, partitioned from the pack) | 35–38 + 6 ≈ 42–44 | ≈ 45 | ≈ **50** (pack-lid conduction + low-PWM recirculation) | **YES, ≥ 10 K margin** |
| fan failure (any placement) | — | — | rises until the TMS570 throttles Thor / SS1 | transient only, covered by the fan-tach rule |

## Ruling
- **≤ 60 °C worst case: NO for any placement downstream of Thor, in the exhaust, or in a closed pocket.** **YES only on the intake side**, upstream of the blowers.
- The 70 °C part rating is also exceeded downstream if fans are PWM'd low.
- **Mitigation:**
  - (a) **Relocate the junction PCB to the duct intake side.** Front-low, above the pack lid, on the partition's cold face with a ≥ 5 mm stand-off; the EtherCAT branches route from there.
  - or (b) keep it on the brain tray and **swap to a reinforced 250 Vrms LAN transformer rated ≥ 85 °C** (Electronics to cite). With a 1–2 W board this gives ≥ 19 K margin at the 66 °C worst case.
  - Ducting it into the exhaust stream is not a fix.

## Shoulder bay with 2× RP06-11012SRAW always-on (Electronics 3027135, ≈ 0.53 W loss each)
- Basis (7f2fa7d): bay air 40 °C walking / 48–53 °C still air with the RP40s only.
- **One RP06 per bay:** +0.8 K walking, +2.3 K still air ⇒ **≈ 41 / 50–55 °C**, ≥ 5 K under the RP40 60 °C derate.
- **If both sit in one bay:** +1.5 / +4.6 K ⇒ 42 / 53–58 °C, 2 K margin. Thermal recommends one per bay.
- **RP06 self-heat** ≈ 0.53 W × ~17–19 K/W ≈ +9–10 K ⇒ case ≈ 51 / 60–65 °C, well inside its derating range (RP03-class full load to ≈ 90 °C ambient; Electronics to confirm the RP06 curve).
- **The A43 shoulder-bay heat map holds.**
