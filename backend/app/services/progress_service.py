import math


def base_xp_for_rating(rating: int | None) -> int:
    if rating is None:
        return 25
    return max(20, math.floor(rating / 40))


def recompute_level(xp: int) -> int:
    return math.floor(math.sqrt(max(xp, 0) / 100)) + 1


def codeforces_rating_delta(problem_rating: int | None, user_rating: int) -> int:
    if problem_rating is None:
        return 10

    delta = (problem_rating - user_rating) / 80
    clamped = max(-15, min(30, delta))
    return round(10 + clamped)
