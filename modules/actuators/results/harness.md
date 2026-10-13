# Harness mass model R5 (O16, R-018 A2): datasheet g/m + routed lengths

`harness.py` → `harness.json`. Bus 20S 68–84 V, star from pack/BMS; EtherCAT line per branch from a torso junction. Coordinates from `v3/cad/model.py`; service-loop radii from `v3/cad/out/cables.json`.

**Cables.** Power: Lapp ÖLFLEX HEAT 180 SiF silicone single cores (datasheet kg/km: 4.0 mm² 50, 2.5 mm² 32, 1.5 mm² 20, 1.0 mm² 15, 0.75 mm² 12, 0.5 mm² 9, 0.25 mm² 5.4). EtherCAT: GORE GSC-03-84820-00 quadrax Cat5e 26 AWG, 3.3 mm, 23.0 kg/km.

**Routing rule.** Straight segments are Manhattan distances along the structure × 1.15. Each crossed joint adds a clock-spring loop: r_wrap × ROM + 50 mm. Each drive adds a 80 mm tee pigtail.

| run | n | route m | loops m | length m | joints crossed | cable | g/m | cond | kg | ΔV pk % | ΔT K | bend r/OD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| leg trunk pack->hip_pitch | 2 | 0.638 | 0.506 | 1.144 | waist yaw, waist pitch, hip yaw, hip roll | SiF 2.5 mm² | 32 | 2 | 0.146 | 0.77 | 6.2 | 14.1 |
| leg hip_pitch->knee | 2 | 0.483 | 0.198 | 0.681 | hip pitch | SiF 2.5 mm² | 32 | 2 | 0.087 | 0.37 | 3.1 | 15.6 |
| leg knee->ankle drives | 2 | 0.23 | 0.168 | 0.398 | knee | SiF 1.0 mm² | 15 | 2 | 0.024 | 0.33 | 3.4 | 18.0 |
| leg drive pigtails (7/leg) | 14 | 0.08 | 0 | 0.08 | - | SiF 1.0 mm² | 15 | 2 | 0.034 | 0.05 | 7.0 | - |
| arm trunk pack->shoulder_yaw | 2 | 0.71 | 0.7 | 1.41 | shoulder pitch, shoulder roll, shoulder yaw | SiF 0.5 mm² | 9 | 2 | 0.051 | 0.63 | 1.4 | 19.3 |
| arm elbow->wrist | 2 | 0.31 | 0.163 | 0.473 | elbow | SiF 0.5 mm² | 9 | 2 | 0.017 | 0.13 | 0.5 | 20.5 |
| arm drive pigtails (7/arm) | 14 | 0.08 | 0 | 0.08 | - | SiF 0.5 mm² | 9 | 2 | 0.020 | 0.04 | 2.3 | - |
| hand 24 V from wrist DC/DC | 2 | 0.115 | 0.228 | 0.343 | wrist roll | SiF 0.5 mm² | 9 | 2 | 0.012 | 0.07 | 0.3 | 16.2 |
| waist drives feed | 1 | 0.109 | 0.151 | 0.26 | waist yaw | SiF 1.0 mm² | 15 | 2 | 0.008 | 0.08 | 1.0 | 19.2 |
| neck/head bus | 1 | 0.259 | 0.26 | 0.519 | neck yaw, neck pitch | SiF 0.75 mm² | 12 | 2 | 0.012 | 0.14 | 0.6 | 14.2 |
| waist/neck pigtails (4) | 4 | 0.08 | 0 | 0.08 | - | SiF 0.5 mm² | 9 | 2 | 0.006 | 0.03 | 1.0 | - |
| compute 24 V feed | 1 | 0.037 | 0 | 0.037 | - | SiF 1.0 mm² | 15 | 2 | 0.001 | 0.01 | 15.8 | - |
| BMS->fuse->contactor->bus bar | 1 | 0.3 | 0 | 0.3 | - | SiF 4.0 mm² | 50 | 2 | 0.030 | 0.25 | 12.6 | - |
| e-stop loop (back button, completeness) | 1 | 0.32 | 0 | 0.32 | - | SiF 0.25 mm² | 5.4 | 2 | 0.003 | 0.01 | 0.0 | - |
| ECAT leg branch -> foot F/T | 2 | 1.797 | 0.977 | 3.414 | waist yaw, waist pitch, hip yaw, hip roll, hip pitch, knee, ankle (pitch+roll) | GORE GSC-03-84820-00 | 23.0 | 1 | 0.157 | 0.00 | 0.0 | 10.6 |
| ECAT arm branch -> hand/tactile | 2 | 1.11 | 1.091 | 2.841 | shoulder pitch, shoulder roll, shoulder yaw, elbow, wrist roll | GORE GSC-03-84820-00 | 23.0 | 1 | 0.131 | 0.00 | 0.0 | 10.3 |
| ECAT waist+neck+head | 1 | 0.524 | 0.411 | 1.335 | neck yaw, neck pitch, waist yaw | GORE GSC-03-84820-00 | 23.0 | 1 | 0.031 | 0.00 | 0.0 | 10.3 |
| head cameras data (2 x quad, completeness) | 2 | 0.222 | 0.26 | 0.482 | neck yaw, neck pitch | GORE GSC-03-84820-00 | 23.0 | 1 | 0.022 | 0.00 | 0.0 | 10.3 |
| IMU (torso, completeness) | 1 | 0.25 | 0 | 0.25 | - | GORE GSC-03-84820-00 | 23.0 | 1 | 0.006 | 0.00 | 0.0 | - |
| motor phase leads (34 drives, 3 x 0.5 mm2 x 0.06 m) | 34 | 0.06 | 0 | 0.06 | - | SiF 0.5 mm² | 9 | 3 | 0.055 | 0.00 | 0.0 | - |
| encoder/thermistor leads (34, 3 x 0.25 mm2 x 0.06 m) | 34 | 0.06 | 0 | 0.06 | - | SiF 0.25 mm² | 5.4 | 3 | 0.033 | 0.00 | 0.0 | - |

Joint ROM used (deg): hip yaw 90, hip roll 75, hip pitch 160, knee 150, ankle (pitch+roll) 90, waist yaw 120, waist pitch 60, shoulder pitch 240, shoulder roll 180, shoulder yaw 240, elbow 150, wrist roll 300, neck yaw 180, neck pitch 90. Hip pitch is from the Legs CAD (−120..+40); the others are [EST] human-range values.

Connectors 0.301 kg: XT60 pair (Amass XT60, 30 A) ×4 (7.8 g/pair distributor listing (Alise Ops)); XT30U pair (Amass, 15 A, drive tees) ×40 (1.8 g each half, AMOV listing); MR30 3-pin pair (Amass, phase) ×0 (1.2 g/pc AMOV listing; phases soldered, n=0); JST-GH 4-pin pair + crimps (ECAT/sensor) ×80 ([EST] JST datasheet gives no mass); AS150U pair (pack main) ×1 ([EST] datasheet gives no mass)

| block | kg |
|---|---|
| power wire (datasheet g/m × routed L) | 0.540 |
| EtherCAT + completeness data (datasheet g/m × routed L) | 0.346 |
| connectors | 0.301 |
| sleeving/ties 12 % [EST] | 0.106 |
| EtherCAT junction PCB [EST] | 0.020 |
| **total** | **1.314** |

Worst ΔV 0.77 % at peak (limit 2 %). Worst conductor ΔT 15.8 K at rms (free air h 10 W/m²K × 2 bundle factor, limit 30 K; SiF rated 180 °C). Minimum bend ratio at the drums is r/OD 10.3.
**Flex life.** SiF is datasheet-rated only for fixed install (6 × OD). GORE quadrax is rated for 15 mm static bend and has no published cycle rating. Both are therefore **not yet flex-qualified**; this is open item O20 (clock-spring cycle test, 1e6 cycles over the full ROM at r_min). The flex-rated igus CFBUS.040 (7.0 mm) needs r ≥ 70 mm, which does not fit the drums. Using it on the 5.07 m of EtherCAT loops would also add 0.182 kg.
