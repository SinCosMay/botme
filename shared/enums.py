from enum import StrEnum


class Platform(StrEnum):
    CODEFORCES = "codeforces"
    LEETCODE = "leetcode"


class AssignmentStatus(StrEnum):
    ASSIGNED = "assigned"
    SOLVED = "solved"
    EXPIRED = "expired"
