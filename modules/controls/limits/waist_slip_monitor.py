"""Waist-pitch friction-limiter slip monitor (Actuators D102c eb5520f).
slip = q_output_encoder - q_motor_encoder / N (N = 100). Any slip beyond SLIP_TOL_RAD flags a slip event:
the joint must re-home before motion resumes. Energy dissipated in the limiter, E = T_slip * |slip|,
over 100 J flags a break-away check.
Braking limits at the output (D102c): CSG-25 grease 3.67 rad/s average, 5.86 rad/s momentary; bus about 5.75 rad/s.
Back-EMF exceeds 95 V above about 6.8 rad/s, so regen protection is owed jointly with Electronics."""
N = 100.0
T_SLIP_NM = 170.0
SLIP_TOL_RAD = 0.0035   # [EST] 0.2 deg: above encoder noise + windup (0.22 deg at 204 N.m, D102)
BREAKAWAY_J = 100.0
BRAKE_AVG_RADS, BRAKE_PEAK_RADS, BUS_RADS = 3.67, 5.86, 5.75


class WaistSlipMonitor:
    def __init__(self):
        self.ref = None; self.energy_J = 0.0; self.slipped = False; self.breakaway_check = False

    def update(self, q_out, q_motor):
        slip = q_out - q_motor / N
        if self.ref is None:
            self.ref = slip
        d = slip - self.ref
        if abs(d) > SLIP_TOL_RAD:
            self.energy_J += T_SLIP_NM * (abs(d) - SLIP_TOL_RAD)
            self.ref = slip - (SLIP_TOL_RAD if d > 0 else -SLIP_TOL_RAD)
            self.slipped = True
        if self.energy_J > BREAKAWAY_J:
            self.breakaway_check = True
        return dict(slip_rad=d, slipped=self.slipped, energy_J=self.energy_J, rehome_required=self.slipped, breakaway_check=self.breakaway_check)

    def rehome(self):
        self.ref = None; self.slipped = False; self.energy_J = 0.0
