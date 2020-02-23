import math


def rescale_js(
    value: float,
    deadzone: float = 0,
    rate: float = 1,
    exponential: float = 1.5,
) -> float:
    """Rescale a joystick input, applying a deadzone, exponential, and max rate.

    Args:
        value: the joystick value, in the interval [-1, 1].
        deadzone: the deadzone to apply.
        rate: the max rate to return (i.e. the value to be returned when 1 is given)
        exponential: the strength of the exponential to apply
                     (i.e. how non-linear should the response be)
    """
    sign = 1
    if value < 0:
        sign = -1
        value = -value
    # Apply deadzone
    if value < deadzone:
        return 0
    if not exponential:
        value = (value - deadzone) / (1 - deadzone)
    else:
        a = math.log(exponential + 1) / (1 - deadzone)
        value = (math.exp(a * (value - deadzone)) - 1) / exponential
    return rate * sign * value


def scale_value(
    value: float,
    input_lower: float,
    input_upper: float,
    output_lower: float,
    output_upper: float,
    exponent: float = 1,
) -> float:
    """Scales a value based on the input range and output range.
    For example, to scale a joystick throttle (1 to -1) to 0-1, we would:
        scale_value(joystick.getThrottle(), 1, -1, 0, 1)
    The output is then raised to the exponent argument.
    """
    input_distance = input_upper - input_lower
    output_distance = output_upper - output_lower
    ratio = (value - input_lower) / input_distance
    result = ratio * output_distance + output_lower
    return math.copysign(result ** exponent, result)
