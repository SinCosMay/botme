from typing import TypedDict


class AssignedProblem(TypedDict):
    assignment_id: str
    problem_id: str
    platform: str
    name: str
    url: str
