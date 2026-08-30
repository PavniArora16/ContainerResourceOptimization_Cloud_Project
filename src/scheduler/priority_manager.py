from enum import IntEnum


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


def assign_priority(priority_value):
    """
    Convert a numerical priority value
    into a scheduling priority.
    """

    if priority_value >= 9:
        return Priority.CRITICAL

    elif priority_value >= 5:
        return Priority.HIGH

    elif priority_value >= 2:
        return Priority.MEDIUM

    else:
        return Priority.LOW


def priority_score(priority):
    """
    Return a numerical score that can be
    used by the resource allocator.
    """

    return int(priority)