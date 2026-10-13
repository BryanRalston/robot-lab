# Harness mass model (M3, R-017 owner Actuators)

`harness.py` -> `harness.json`. Bus 20S 68–84 V, EtherCAT daisy chain per limb, drives on the actuators.

Leg trunk current: peak 33.2 A (peak_limb 2256 W / 68 V), rms 7.0 A [EST 1.6 × mean].

| item | n | length m | AWG | cond | kg | I rms / pk A | ΔV pk % | ΔT K |
|---|---|---|---|---|---|---|---|---|
| legL trunk pack->hip | 1 | 0.4 | 12 | 2 | 0.027 | 7.0 / 33.2 | 0.20 | 2.5 |
| legL hip->knee | 1 | 0.4 | 14 | 2 | 0.018 | 4.9 / 26.5 | 0.26 | 2.2 |
| legL knee->ankle | 1 | 0.4 | 16 | 2 | 0.012 | 2.8 / 16.6 | 0.26 | 1.3 |
| legL drive drops (8) | 8 | 0.08 | 18 | 2 | 0.013 | 4.0 / 12.0 | 0.06 | 4.8 |
| armL trunk pack->shoulder | 1 | 0.35 | 16 | 2 | 0.010 | 1.2 / 4.4 | 0.06 | 0.2 |
| armL along arm | 1 | 0.55 | 18 | 2 | 0.011 | 0.7 / 2.6 | 0.09 | 0.1 |
| armL drive drops (7) | 7 | 0.06 | 20 | 2 | 0.005 | 1.5 / 5.0 | 0.03 | 1.2 |
| handL power (24 V from wrist DC/DC, 2 cond) | 1 | 0.15 | 22 | 2 | 0.001 | 0.5 / 2.0 | 0.05 | 0.2 |
| legR trunk pack->hip | 1 | 0.4 | 12 | 2 | 0.027 | 7.0 / 33.2 | 0.20 | 2.5 |
| legR hip->knee | 1 | 0.4 | 14 | 2 | 0.018 | 4.9 / 26.5 | 0.26 | 2.2 |
| legR knee->ankle | 1 | 0.4 | 16 | 2 | 0.012 | 2.8 / 16.6 | 0.26 | 1.3 |
| legR drive drops (8) | 8 | 0.08 | 18 | 2 | 0.013 | 4.0 / 12.0 | 0.06 | 4.8 |
| armR trunk pack->shoulder | 1 | 0.35 | 16 | 2 | 0.010 | 1.2 / 4.4 | 0.06 | 0.2 |
| armR along arm | 1 | 0.55 | 18 | 2 | 0.011 | 0.7 / 2.6 | 0.09 | 0.1 |
| armR drive drops (7) | 7 | 0.06 | 20 | 2 | 0.005 | 1.5 / 5.0 | 0.03 | 1.2 |
| handR power (24 V from wrist DC/DC, 2 cond) | 1 | 0.15 | 22 | 2 | 0.001 | 0.5 / 2.0 | 0.05 | 0.2 |
| waist+neck+head bus | 1 | 0.8 | 18 | 2 | 0.016 | 1.5 / 6.0 | 0.30 | 0.7 |
| waist/neck drive drops (4) | 4 | 0.08 | 20 | 2 | 0.004 | 1.0 / 4.0 | 0.03 | 0.5 |
| compute/sensors 24 V feed | 1 | 0.4 | 18 | 2 | 0.008 | 6.0 / 8.0 | 0.20 | 10.8 |
| EtherCAT limb runs (4) incl. return | 4 | 1.6 | 4×26 ECAT |  | 0.090 | 0.0 / 0.0 | 0.00 | 0.0 |
| EtherCAT jumpers drive-to-drive | 30 | 0.12 | 4×26 ECAT |  | 0.050 | 0.0 / 0.0 | 0.00 | 0.0 |
| EtherCAT waist/neck/head | 1 | 1.0 | 4×26 ECAT |  | 0.014 | 0.0 / 0.0 | 0.00 | 0.0 |
| motor phase leads (34 drives, 3 x 20 AWG x 0.06 m) | 34 | 0.06 | 20 | 3 | 0.040 | 0.0 / 0.0 | 0.00 | 0.0 |
| encoder/thermistor leads (34, 6 x 28 AWG-class 0.06 m)  | 34 | 0.06 | 24 | 3 | 0.019 | 0.0 / 0.0 | 0.00 | 0.0 |

Connectors 0.284 kg: XT60 pair (Amass XT60PW, 30 A cont) ×4; XT30 pair (Amass XT30U, 15 A) ×38; MR30 3-pin phase (Amass) ×0; EtherCAT JST-GH 4-pin pair (latching) ×76; Pack Anderson-class main (Amass AS150U pair) ×1

Sleeving/ties 12 % 0.052, BMS/fuse/contactor leads 0.050.

**Total 0.821 kg vs target 1.46 (contract 2.00).** Worst voltage drop 0.30 % at peak, worst conductor ΔT 10.8 K at rms (free-air, h 10 W/m²K; bundle derate covered by ampacity 50 %).
Evidence level: wire mass per AWG and EtherCAT 14 g/m are vendor-typical [EST, datasheets to pull]; connector masses Amass/JST catalogue values [EST ±20 %]. Lengths from v3 limb geometry [EST ±20 %].
