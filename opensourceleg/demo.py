import time

from opensourceleg.osl import OpenSourceLeg
from opensourceleg.state_machine import Event, State

# ------------- FSM PARAMETERS ---------------- #

BODY_WEIGHT = 130

# STATE 1: EARLY STANCE

KNEE_K_ESTANCE = 130
KNEE_B_ESTANCE = 0
KNEE_THETA_ESTANCE = 5

LOAD_LSTANCE: float = -1.0 * BODY_WEIGHT * 0.3 * 4.4

ANKLE_K_ESTANCE = 50
ANKLE_B_ESTANCE = 0
ANKLE_THETA_ESTANCE = 20

# --------------------------------------------- #
# STATE 2: LATE STANCE

KNEE_K_LSTANCE = 150
KNEE_B_LSTANCE = 0
KNEE_THETA_LSTANCE = 5

LOAD_ESWING: float = -1.0 * BODY_WEIGHT * 0.2 * 4.4

ANKLE_K_LSTANCE = 90
ANKLE_B_LSTANCE = 0
ANKLE_THETA_LSTANCE = 0

# --------------------------------------------- #
# STATE 3: EARLY SWING

KNEE_K_ESWING = 30
KNEE_B_ESWING = 40
KNEE_THETA_ESWING = 85

KNEE_THETA_ESWING_TO_LSWING = 60
KNEE_DTHETA_ESWING_TO_LSWING = 3

ANKLE_K_ESWING = 20
ANKLE_B_ESWING = 0
ANKLE_THETA_ESWING = 30

# --------------------------------------------- #
# STATE 4: LATE SWING

KNEE_K_LSWING = 20
KNEE_B_LSWING = 60
KNEE_THETA_LSWING = 5

LOAD_ESTANCE: float = -1.0 * BODY_WEIGHT * 0.3 * 4.4
KNEE_THETA_LSWING_TO_ESTANCE = 20

ANKLE_K_LSWING = 20
ANKLE_B_LSWING = 0
ANKLE_THETA_LSWING = 30

# ------------- FSM TRANSITIONS --------------- #


def estance_to_lstance(osl: OpenSourceLeg) -> bool:
    """
    Transition from early stance to late stance when the loadcell
    reads a force greater than a threshold.
    """
    assert osl.loadcell is not None
    if osl.loadcell.fz < LOAD_ESTANCE:
        return True
    else:
        return False


def lstance_to_eswing(osl: OpenSourceLeg) -> bool:
    """
    Transition from late stance to early swing when the loadcell
    reads a force less than a threshold.
    """
    assert osl.loadcell is not None
    if osl.loadcell.fz > LOAD_ESWING:
        return True
    else:
        return False


def eswing_to_lswing(osl: OpenSourceLeg) -> bool:
    """
    Transition from early swing to late swing when the knee angle
    is greater than a threshold and the knee velocity is less than
    a threshold.
    """
    assert osl.knee is not None
    if (
        osl.knee.output_position < KNEE_THETA_ESWING_TO_LSWING
        and osl.knee.output_velocity < KNEE_DTHETA_ESWING_TO_LSWING
    ):
        return True
    else:
        return False


def eswing_to_estance(osl: OpenSourceLeg) -> bool:
    """
    Transition from early swing to early stance when the loadcell
    reads a force greater than a threshold.
    """
    assert osl.loadcell is not None
    if osl.loadcell.fz < LOAD_ESTANCE:
        return True
    else:
        return False


def lswing_to_estance(osl: OpenSourceLeg) -> bool:
    """
    Transition from late swing to early stance when the loadcell
    reads a force greater than a threshold or the knee angle is
    less than a threshold.
    """
    assert osl.knee is not None and osl.loadcell is not None
    if (
        osl.loadcell.fz < LOAD_ESTANCE
        or osl.knee.output_position > KNEE_THETA_LSWING_TO_ESTANCE
    ):
        return True
    else:
        return False


def main():
    osl = OpenSourceLeg(frequency=200)
    osl.units["position"] = "deg"  # type: ignore
    osl.units["velocity"] = "deg/s"  # type: ignore

    osl.add_joint(
        name="ankle",
        gear_ratio=41.4999,
    )

    osl.add_loadcell(
        dephy_mode=False,
    )

    osl.add_state_machine(spoof=True)

    early_stance = State(name="e_stance")
    early_stance.set_knee_impedance_paramters(
        theta=KNEE_THETA_ESTANCE, k=KNEE_K_ESTANCE, b=KNEE_B_ESTANCE
    )
    early_stance.make_knee_active()

    early_stance.set_ankle_impedance_paramters(
        theta=ANKLE_THETA_ESTANCE, k=ANKLE_K_ESTANCE, b=ANKLE_B_ESTANCE
    )
    early_stance.make_ankle_active()

    late_stance = State(name="l_stance")
    late_stance.set_knee_impedance_paramters(
        theta=KNEE_THETA_LSTANCE, k=KNEE_K_LSTANCE, b=KNEE_B_LSTANCE
    )
    late_stance.make_knee_active()

    late_stance.set_ankle_impedance_paramters(
        theta=ANKLE_THETA_LSTANCE, k=ANKLE_K_LSTANCE, b=ANKLE_B_LSTANCE
    )
    late_stance.make_ankle_active()

    early_swing = State(name="e_swing")
    early_swing.set_knee_impedance_paramters(
        theta=KNEE_THETA_ESWING, k=KNEE_K_ESWING, b=KNEE_B_ESWING
    )
    early_swing.make_knee_active()

    early_swing.set_ankle_impedance_paramters(
        theta=ANKLE_THETA_ESWING, k=ANKLE_K_ESWING, b=ANKLE_B_ESWING
    )
    early_swing.make_ankle_active()

    late_swing = State(name="l_swing")
    late_swing.set_knee_impedance_paramters(
        theta=KNEE_THETA_LSWING, k=KNEE_K_LSWING, b=KNEE_B_LSWING
    )
    late_swing.make_knee_active()

    late_swing.set_ankle_impedance_paramters(
        theta=ANKLE_THETA_LSWING, k=ANKLE_K_LSWING, b=ANKLE_B_LSWING
    )
    late_swing.make_ankle_active()

    foot_flat = Event(name="foot_flat")
    heel_off = Event(name="heel_off")
    toe_off = Event(name="toe_off")
    pre_heel_strike = Event(name="pre_heel_strike")
    heel_strike = Event(name="heel_strike")
    misc = Event(name="misc")

    assert osl.state_machine is not None
    osl.state_machine.add_state(state=early_stance, initial_state=True)
    osl.state_machine.add_state(state=late_stance)
    osl.state_machine.add_state(state=early_swing)
    osl.state_machine.add_state(state=late_swing)

    osl.state_machine.add_event(event=foot_flat)
    osl.state_machine.add_event(event=heel_off)
    osl.state_machine.add_event(event=toe_off)
    osl.state_machine.add_event(event=pre_heel_strike)
    osl.state_machine.add_event(event=heel_strike)
    osl.state_machine.add_event(event=misc)

    osl.state_machine.add_transition(
        source=early_stance,
        destination=late_stance,
        event=foot_flat,
        callback=estance_to_lstance,
    )

    osl.state_machine.add_transition(
        source=late_stance,
        destination=early_swing,
        event=heel_off,
        callback=lstance_to_eswing,
    )

    osl.state_machine.add_transition(
        source=early_swing,
        destination=late_swing,
        event=toe_off,
        callback=eswing_to_lswing,
    )

    osl.state_machine.add_transition(
        source=late_swing,
        destination=early_stance,
        event=heel_strike,
        callback=lswing_to_estance,
    )

    # osl.add_tui()

    with osl:
        # osl.home()
        osl.log.info(osl.ankle.motor_position)
        osl.log.info(osl.ankle.output_position)
        time.sleep(1)
        osl.home()
        osl.log.info(osl.ankle.motor_position)
        osl.log.info(osl.ankle.output_position)
        time.sleep(1)

        # osl.knee.set_mode(mode="impedance")
        # osl.knee.set_impedance_gains()
        # osl.knee.set_output_position(position=10)

        # time.sleep(2)

        # osl.update()

        # osl.log.info(osl.knee.motor_position)
        # osl.log.info(osl.knee.output_position)

        # osl.run(set_state_machine_parameters=True)


if __name__ == "__main__":
    main()