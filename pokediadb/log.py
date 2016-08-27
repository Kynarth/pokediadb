"""Module to display different kind of messages in the terminal."""

import os
import textwrap

import click

from pokediadb.enums import Log


def format_message(msg, msg_type):
    """Format a message in function of message type and terminal's size.

    Args:
        msg (str): Message to format.
        msg_type (Log): Kind of message.

    Returns:
        str: Return formatted message.

    """
    print("Try get term-size")
    term_size = os.get_terminal_size()
    print("Term-size:", term_size)
    return textwrap.fill(
        msg, width=term_size.columns, initial_indent="",
        subsequent_indent=" " * len(msg_type.value)
    )


def info(msg, verbose=True):
    """Display information message.

    Args:
        msg (str): Message to display
        verbose (bool): If True the message is displayed.

    Returns:
        str: Return formatted message.

    """
    if not verbose:
        return

    click.secho(Log.INFO.value, fg="green", bold=True, nl=False)

    full_msg = Log.INFO.value + msg
    print("Try format message")
    msg = format_message(full_msg, Log.INFO)[len(Log.INFO.value):]
    print("Message formated")
    click.secho(msg, fg="green")

    return full_msg


# def warning(msg):
#     """Display warning message.

#     Args:
#         msg (str): Message to display

#     Returns:
#         str: Return formatted message.

#     """
#     click.secho(Log.WARNING.value, fg="yellow", bold=True, nl=False)

#     full_msg = Log.WARNING.value + msg
#     msg = format_message(full_msg, Log.WARNING)[len(Log.WARNING.value):]
#     click.secho(msg, fg="yellow")

#     return full_msg


def error(msg):
    """Display error message.

    Args:
        msg (str): Message to display

    Returns:
        str: Return formatted message.

    """
    click.secho(Log.ERROR.value, fg="red", bold=True, nl=False, err=True)

    full_msg = Log.ERROR.value + msg
    msg = format_message(full_msg, Log.ERROR)[len(Log.ERROR.value):]
    click.secho(msg, fg="red", err=True)

    return full_msg
