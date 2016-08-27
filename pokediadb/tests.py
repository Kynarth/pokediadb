import re


def check_output(output, ref):
    """Check if the reference string is in the output

    Check if the reference string is in output without taking into account
    whitespaces and carriage return.

    Args:
        output (str): Output to check.
        ref (str): Reference string to check if it's in the output

    Returns:
        bool: True if the ref string is in the output else False

    """
    return re.sub(r"\s", "", ref) in re.sub(r"\s", "", output)
