# Harness mass model R5 (O16, R-018 A2): datasheet g/m + routed lengths

`harness.py` → `harness.json`. Bus 20S 68–84 V, star from pack/BMS; EtherCAT line per branch from a torso junction. Coordinates from `v3/cad/model.py`; service-loop radii from `v3/cad/out/cables.json`.

**Cables.** Power: Lapp ÖLFLEX HEAT 180 SiF silicone single cores (datasheet kg/km: 4.0 mm² 50, 2.5 mm² 32, 1.5 mm² 20, 1.0 mm² 15, 0.75 mm² 12, 0.5 mm² 9, 0.25 mm² 5.4). EtherCAT: GORE GSC-03-84820-00 quadrax Cat5e 26 AWG, 3.3 mm, 23.0 kg/km.

**Routing rule.** Straight segments are Manhattan distances along the structure × 1.15. Each crossed joint adds a clock-spring loop: r_wrap × ROM + 50 mm. Each drive adds a 80 mm tee pigtail.

| run | n | route m | loops m | length m | joints crossed | cable | g/m | cond | kg | ΔV pk % | ΔT K | bend r/OD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| leg trunk pack->hip_pitch | 2 | 0.638 | 0.529 | 1.167 | waist yaw, waist pitch, hip yaw, hip roll | SiF 2.5 mm² | 32 | 2 | 0.152 | 0.78 | 5.4 | 12.3 |
| leg hip_pitch->knee | 2 | 0.483 | 0.184 | 0.667 | hip pitch | SiF 1.5 mm² | 20 | 2 | 0.055 | 0.60 | 5.0 | 15.6 |
| leg knee->ankle drives | 2 | 0.23 | 0.156 | 0.386 | knee | SiF 1.0 mm² | 15 | 2 | 0.024 | 0.32 | 2.8 | 15.0 |
| leg drive pigtails (7/leg) | 14 | 0.08 | 0 | 0.08 | - | SiF 1.0 mm² | 15 | 2 | 0.034 | 0.05 | 7.0 | - |
| arm trunk pack->shoulder_yaw | 2 | 0.71 | 0.756 | 1.465 | shoulder pitch, shoulder roll, shoulder yaw | SiF 0.5 mm² | 9 | 2 | 0.052 | 0.65 | 1.3 | 17.6 |
| arm elbow->wrist | 2 | 0.31 | 0.155 | 0.466 | elbow | SiF 0.5 mm² | 9 | 2 | 0.017 | 0.12 | 0.5 | 18.7 |
| arm drive pigtails (7/arm) | 14 | 0.08 | 0 | 0.08 | - | SiF 0.5 mm² | 9 | 2 | 0.020 | 0.04 | 2.3 | - |
| hand 24 V from wrist DC/DC | 2 | 0.115 | 0.252 | 0.367 | wrist roll | SiF 0.5 mm² | 9 | 2 | 0.013 | 0.07 | 0.2 | 14.8 |
| waist drives feed | 1 | 0.109 | 0.201 | 0.31 | waist yaw | SiF 1.0 mm² | 15 | 2 | 0.010 | 0.09 | 0.8 | 16.0 |
| neck/head bus | 1 | 0.259 | 0.242 | 0.501 | neck yaw, neck pitch | SiF 0.75 mm² | 12 | 2 | 0.012 | 0.14 | 0.5 | 12.6 |
| waist/neck pigtails (4) | 4 | 0.08 | 0 | 0.08 | - | SiF 0.5 mm² | 9 | 2 | 0.006 | 0.03 | 1.0 | - |
| compute 24 V feed | 1 | 0.037 | 0 | 0.037 | - | SiF 1.0 mm² | 15 | 2 | 0.001 | 0.01 | 15.8 | - |
| BMS->fuse->contactor->bus bar | 1 | 0.3 | 0 | 0.3 | - | SiF 4.0 mm² | 50 | 2 | 0.030 | 0.25 | 12.5 | - |
| e-stop loop (back button, completeness) | 1 | 0.32 | 0 | 0.32 | - | SiF 0.25 mm² | 5.4 | 2 | 0.003 | 0.01 | 0.0 | - |
| ECAT leg branch -> foot F/T | 2 | 1.797 | 1.002 | 3.439 | waist yaw, waist pitch, hip yaw, hip roll, hip pitch, knee, ankle (pitch+roll) | Belden MachFlex MRTA2P26S | 25.9 | 1 | 0.178 | 0.00 | 0.0 | 8.3 |
| ECAT arm branch -> hand/tactile | 2 | 1.11 | 1.163 | 2.913 | shoulder pitch, shoulder roll, shoulder yaw, elbow, wrist roll | Belden MachFlex MRTA2P26S | 25.9 | 1 | 0.151 | 0.00 | 0.0 | 8.1 |
| ECAT waist+neck+head | 1 | 0.524 | 0.443 | 1.368 | neck yaw, neck pitch, waist yaw | Belden MachFlex MRTA2P26S | 25.9 | 1 | 0.035 | 0.00 | 0.0 | 8.1 |
| head cameras data (2 x quad, completeness) | 2 | 0.222 | 0.242 | 0.464 | neck yaw, neck pitch | Belden MachFlex MRTA2P26S | 25.9 | 1 | 0.024 | 0.00 | 0.0 | 8.1 |
| IMU (torso, completeness) | 1 | 0.25 | 0 | 0.25 | - | Belden MachFlex MRTA2P26S | 25.9 | 1 | 0.006 | 0.00 | 0.0 | - |
| motor phase leads (34 drives, 3 x 0.5 mm2 x 0.06 m) | 34 | 0.06 | 0 | 0.06 | - | SiF 0.5 mm² | 9 | 3 | 0.055 | 0.00 | 0.0 | - |
| encoder/thermistor leads (34, 3 x 0.25 mm2 x 0.06 m) | 34 | 0.06 | 0 | 0.06 | - | SiF 0.25 mm² | 5.4 | 3 | 0.033 | 0.00 | 0.0 | - |

Joint ROM used (deg): hip yaw 80.0, hip roll 27.0, hip pitch 145.0, knee 135.0, waist yaw 180.0, waist pitch 90.0, shoulder pitch 240.0, shoulder roll 195.0, shoulder yaw 300.0, elbow 140.0, wrist roll 340.0, wrist pitch 140.0, wrist yaw 80.0, neck yaw 160.0, neck pitch 80.0, ankle (pitch+roll) 135.0. Hip pitch is from the Legs CAD (−120..+40); the others are [EST] human-range values.

Connectors 0.257 kg: XT60 pair (Amass XT60, 30 A) ×4 (7.8 g/pair distributor listing (Alise Ops)); XT30U pair (Amass, 15 A, drive tees) ×40 (1.8 g each half, AMOV listing); MR30 3-pin pair (Amass, phase) ×0 (1.2 g/pc AMOV listing; phases soldered, n=0); JST-GH 4-pin pair (GHR-04V-S + 4 SSHL-002T + BM04B-GHS header) ×80 (CALC from jst_gh.pdf dims: housing 6.25x4.15x~10 mm PA9T ~50 % solid 0.15 g + header 0.20 g + 4 contacts 0.03 g); AS150U pair (pack main) ×1 (41.4 g/pair distributor listing (Rotorama))

| block | kg |
|---|---|
| power wire (datasheet g/m × routed L) | 0.515 |
| EtherCAT + completeness data (datasheet g/m × routed L) | 0.395 |
| connectors | 0.257 |
| sleeving/ties 12 % [EST] | 0.109 |
| EtherCAT junction PCB [EST] | 0.020 |
| **total** | **1.296** |

Worst ΔV 0.78 % at peak (limit 2 %). Worst conductor ΔT 15.8 K at rms (free air h 10 W/m²K × 2 bundle factor, limit 30 K; SiF rated 180 °C). Minimum bend ratio at the drums is r/OD 8.1 (MachFlex rated 7.5 × OD for 8e6 cycles; SILI-E / SiF ≥ 6 × OD).
**Flex (R5b, O20).** In every clock-spring loop the EtherCAT is Belden MachFlex MRTA2P26S: 2×2×26 AWG robotic cable, 4.2 mm, 25.9 g/m, 8e6 bend cycles at 7.5D and 8e6 torsion cycles at ±180°/m. It is used for the whole branch, so there are no splices. Belden does not specify 100 Ω impedance, so a TDR or EtherCAT link test is needed (O20b). Power cores inside the loops are Stäubli SILI-E super-flexible silicone (class 6, 0.07 mm strands). Stäubli publishes no cycle rating, so the clock-spring cycle test stays (O20a). igus CFBUS/CFROBOT and Lapp ETHERLINE Flex need 70–90 mm bend radius and do not fit the drums.
