# Open-source starting points for Robot Lab v0.1: design and capabilities
_Researched 2026-10-12. Focus: architecture, DoF, mechanisms, demonstrated capabilities, limits. Components are named only where they define capability._

## Candidates

### 1. Berkeley Humanoid Lite (UC Berkeley Hybrid Robotics, RSS 2025), TOP PICK
Links: [repo](https://github.com/hybridrobotics/berkeley-humanoid-lite) · [paper](https://arxiv.org/abs/2504.17249) · [docs](https://berkeley-humanoid-lite.gitbook.io/docs)
- **Architecture:** full humanoid with ~22 actuated joints (10 large + 12 small actuator modules). Every joint has its own BLDC motor, a **3D-printed cycloidal gearbox**, a FOC driver (B-G431B-ESC1) and a magnetic encoder. Each limb has its own 1 Mbps CAN bus at 250 Hz, and up to 64 devices per bus means the robot can be reconfigured into other morphologies. An Intel N95 mini PC runs low-level control and the RL policy. The IMU sits at the torso center. The torso is aluminum extrusion. Power comes from an onboard 6S LiPo (~30 min) or a tether.
- **Demonstrated (paper):** RL locomotion trained in IsaacLab with **zero-shot sim-to-real** walking. Two 5-DoF arms with grippers, VR-teleoperated (SteamVR), did writing, packing/unpacking, block pick-and-place and solving a Rubik's Cube. Measured actuator backlash was at most 0.0229 rad.
- **Limits:** small and low-torque. Plastic gearboxes wear. Short runtime. Simple grippers, no dexterous hands. Arms are teleoperated, not autonomous.

### 2. LeKiwi + SO-101 (Hugging Face LeRobot / UIUC)
Links: [LeKiwi](https://github.com/SIGRobotics-UIUC/LeKiwi) · [SO-ARM100/101](https://github.com/TheRobotStudio/SO-ARM100)
- **Architecture:** 3-wheel holonomic kiwi drive with omni wheels, a 6-DoF SO-101 arm on Feetech STS3215 bus servos, Raspberry Pi 5, wrist and base RGB cameras. A dual-arm variant has 2 arms, a depth camera and a 2-DoF neck.
- **Demonstrated:** leader-arm/keyboard teleop, data collection, and learned imitation policies through LeRobot.
- **Limits:** hobby servos, light payload, flat floors, no legs.

### 3. JPL Open Source Rover
Links: [repo](https://github.com/nasa-jpl/open-source-rover)
- **Architecture:** 6-wheel rocker-bogie with 10 motors (6 drive, 4 corner steering), goBILDA aluminum, ROS.
- **Demonstrated:** rough-terrain driving at ~1.6 m/s.
- **Limits:** no manipulation and not a humanoid. **No 3D printing needed.**

### 4. ToddlerBot (Stanford) / K-Scale
Small open ML-first humanoids, also print-heavy. Not verified in depth.

### 5. InMoov / Poppy
Printed humanoids on hobby servos, mostly for looks. No dynamic walking.

## Why Berkeley Humanoid Lite is the best foundation
It's the only open, buildable design that already does both things Robot Lab's spec targets: learned walking with sim-to-real transfer, and bimanual manipulation. Its architecture (a smart actuator per joint, a bus per limb, a central policy computer) is a scaled-down version of Optimus and Figure. Its IsaacLab training stack matches our MuJoCo/Isaac sim plan, so the skills and tooling carry up to the full design.

## What a realistic v0.1 could do
- Stand, walk with the released RL policy, and absorb small pushes.
- Teleoperated two-arm pick-and-place.
- ~30 min untethered, or longer tethered.
- **Not** in v0.1: dexterous hands, real payloads, autonomy, long runtime.
- Staging: one bench actuator, then one leg, then lower-body walking, then arms and teleop.

## 3D printing (Bryan has no printer)
- **Berkeley Humanoid Lite:** the gearboxes and limb shells are printed, which is most of the robot. Parts fit a 200 mm build volume. Order through JLCPCB, Craftcloud or Xometry (test 2 actuators first, because cycloidal fit is tolerance-critical), or buy a 200 mm-class printer, which is likely faster across 22 actuators.
- **SO-101 / LeKiwi:** printed links and plates. Buy printed-frame or assembled kits instead (WowRobo, PartaBot, Seeed, RobotEd, ForgeMotion; see the [SO-ARM100 kits list](https://github.com/TheRobotStudio/SO-ARM100#kits)).
- **JPL OSR:** nothing printed.
