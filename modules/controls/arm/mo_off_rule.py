"""Actuators D100 (31875a1): a commanded MO=0 is never sent while standing. The robot always kneels or sits first, as for the knee.
This replaces the limp hip hold. Supervisor-side rule. It matches drive_thermal_derate.py, where MO_OFF is reachable only from
CONTACT_CONFIRMED (kneel/sit, support flags held 50 ms), and _mo_off() raises UnsupportedMoOff otherwise.
Planned faults (documented exceptions: the drive drops torque without a command from Controls, so this rule cannot apply):
  - E-stop / STO (Cat 0), operator-initiated
  - power loss / BMS cutoff / main fuse
  - drive hardware self-trip (overcurrent, over/undervoltage, encoder fault, drive over-temperature hard trip)
  - watchdog/comm loss with the drive set to disable on timeout
In each case the hips go limp and protection comes from the passive cover (ID 8c foam: L/R 127 N, hem 115 N)."""
SUPPORTED = ('kneel', 'sit', 'prone', 'contact_confirmed')
PLANNED_FAULTS = ('estop_sto', 'power_loss', 'bms_cutoff', 'drive_hw_trip', 'watchdog')

class UnsupportedMoOff(RuntimeError):
    pass

def mo_off_allowed(posture: str, fault: str | None = None) -> bool:
    if fault in PLANNED_FAULTS: return True  # not commanded by Controls; recorded only
    return posture in SUPPORTED

def command_mo_off(posture: str, fault: str | None = None):
    if not mo_off_allowed(posture, fault):
        raise UnsupportedMoOff(f'MO=0 refused in {posture!r}: kneel or sit first (D100)')
    return True
