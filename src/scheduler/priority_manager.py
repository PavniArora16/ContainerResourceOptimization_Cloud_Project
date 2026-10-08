from enum import IntEnum


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


def assign_priority(priority_value):

    if priority_value >= 1.5:
        return Priority.CRITICAL

    elif priority_value >= 1.0:
        return Priority.HIGH

    elif priority_value >= 0.5:
        return Priority.MEDIUM

    else:
        return Priority.LOW


def priority_score(priority):
    return int(priority)