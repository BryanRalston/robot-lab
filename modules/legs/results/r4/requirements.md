# Legs r4 requirement table at 66.5 kg (R-017 hard limit), CONTRACTS R1.2 limits

Mass in model: 66.50 kg (carry runs +20 kg). Need = 1.5 × max non-carry ID peak (R-004/R-011 basis). Carry check: avail / carry_20kg_1p0 peak ≥ 1.2 (R-014).

| joint | peak N·m [scenario] | need 1.5× (R-011 @65 kg) | R1.2 avail | avail/need | carry 1.0 peak | avail/carry | RMS N·m | peak ω rad/s [scen] | ω@30% | q range deg |
|---|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | 45.9 [stairs_18cm] | 69 (66) | 70 | 1.016 | 42.1 | 1.66 | 14.8 | 0.57 [walk_1p2] | 0.24 | [-2, 4] |
| hip_roll | 122.4 [stairs_18cm] | 184 (180) | 204 | 1.111 | 114.0 | 1.79 | 51.1 | 1.23 [push_recover] | 1.13 | [-11, 14] |
| hip_pitch | 225.1 [stairs_18cm] | 338 (334) | 350 | 1.036 | 233.4 | 1.50 | 88.7 | 8.11 [walk_1p2] | 8.09 | [-76, 11] |
| knee | 159.8 [walk_1p2] | 240 (235) | 258 | 1.077 | 162.4 | 1.59 | 77.8 | 13.33 [stairs_18cm] | 13.27 | [22, 117] |
| ankle_pitch | 209.3 [walk_1p0] | 314 (309) | 311 | 0.991 | 241.5 | 1.29 | 57.4 | 9.43 [stairs_18cm] | 6.92 | [-60, 12] |
| ankle_roll | 42.5 [push_recover] | 64 (62) | 177 | 2.779 | 32.1 | 5.52 | 17.6 | 1.23 [push_recover] | 0.83 | [-14, 11] |

Per-scenario checks:
- walk_0p8: CoP inside sole True, residual p99 36.3 N, frames >5% BW 29, max GRF 1.15 BW
- walk_1p0: CoP inside sole True, residual p99 37.4 N, frames >5% BW 32, max GRF 1.21 BW
- walk_1p2: CoP inside sole True, residual p99 38.0 N, frames >5% BW 91, max GRF 1.21 BW
- carry_20kg_1p0: CoP inside sole True, residual p99 48.3 N, frames >5% BW 29, max GRF 1.14 BW
- stairs_18cm: CoP inside sole True, residual p99 34.6 N, frames >5% BW 18, max GRF 1.31 BW
- sit_to_stand_r3: CoP inside sole True, residual p99 4.5 N, frames >5% BW 0, max GRF 0.55 BW, hip min -74.6°, seat 0.46 m
- push_recover: CoP inside sole True, residual p99 55.1 N, frames >5% BW 19, max GRF 1.08 BW
