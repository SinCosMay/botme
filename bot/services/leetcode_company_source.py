import csv
import random
from dataclasses import dataclass
from io import StringIO

import httpx


class LeetCodeSourceError(Exception):
    pass


@dataclass
class CompanyQuestion:
    company: str
    title: str
    difficulty: str
    link: str
    topics: list[str]
    frequency: str | None
    acceptance_rate: str | None


def _pick_column(row: dict[str, str], keys: list[str]) -> str:
    lower_map = {k.strip().lower(): v for k, v in row.items()}
    for key in keys:
        value = lower_map.get(key.strip().lower())
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _parse_topics(raw: str) -> list[str]:
    if not raw:
        return []
    for sep in ("|", ";", ","):
        if sep in raw:
            return [part.strip() for part in raw.split(sep) if part.strip()]
    return [raw.strip()] if raw.strip() else []


async def _find_company_directory(client: httpx.AsyncClient, repo: str, company: str) -> str:
    url = f"https://api.github.com/repos/{repo}/contents"
    response = await client.get(url)
    if response.status_code != 200:
        raise LeetCodeSourceError("Could not load company index from GitHub")

    entries = response.json()
    if not isinstance(entries, list):
        raise LeetCodeSourceError("Unexpected GitHub directory response")

    target = company.strip().lower()
    exact = [e for e in entries if e.get("type") == "dir" and str(e.get("name", "")).strip().lower() == target]
    if exact:
        return str(exact[0]["name"])

    partial = [
        e
        for e in entries
        if e.get("type") == "dir" and target in str(e.get("name", "")).strip().lower()
    ]
    if partial:
        return str(partial[0]["name"])

    raise LeetCodeSourceError("Company not found in source repository")


async def _pick_csv_download_url(client: httpx.AsyncClient, repo: str, company_dir: str) -> str:
    url = f"https://api.github.com/repos/{repo}/contents/{company_dir}"
    response = await client.get(url)
    if response.status_code != 200:
        raise LeetCodeSourceError("Could not load company file list")

    entries = response.json()
    if not isinstance(entries, list):
        raise LeetCodeSourceError("Unexpected company directory response")

    csv_entries = [e for e in entries if str(e.get("name", "")).lower().endswith(".csv")]
    if not csv_entries:
        raise LeetCodeSourceError("No CSV question files found for this company")

    def score(name: str) -> int:
        n = name.lower()
        if "all" in n:
            return 0
        if "90" in n:
            return 1
        if "60" in n:
            return 2
        if "30" in n:
            return 3
        return 4

    csv_entries.sort(key=lambda e: (score(str(e.get("name", ""))), str(e.get("name", "")).lower()))
    download_url = csv_entries[0].get("download_url")
    if not download_url:
        raise LeetCodeSourceError("CSV file has no downloadable URL")
    return str(download_url)


async def pick_random_company_question(
    *,
    repo: str,
    company: str,
    topic: str | None = None,
    difficulty: str | None = None,
) -> CompanyQuestion:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "float-bot/1.0",
    }

    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        company_dir = await _find_company_directory(client, repo, company)
        csv_url = await _pick_csv_download_url(client, repo, company_dir)
        csv_response = await client.get(csv_url)

    if csv_response.status_code != 200:
        raise LeetCodeSourceError("Could not download question CSV")

    text = csv_response.text
    reader = csv.DictReader(StringIO(text))

    topic_key = (topic or "").strip().lower()
    difficulty_key = (difficulty or "").strip().lower()
    candidates: list[CompanyQuestion] = []

    for row in reader:
        title = _pick_column(row, ["Title", "Problem", "Question", "Name"])
        link = _pick_column(row, ["Link", "URL", "Problem Link"]) or "https://leetcode.com/problemset/"
        question_difficulty = _pick_column(row, ["Difficulty", "Level"]) or "N/A"
        topics = _parse_topics(_pick_column(row, ["Topics", "Tags", "Topic"]))
        frequency = _pick_column(row, ["Frequency", "Freq"]) or None
        acceptance = _pick_column(row, ["Acceptance", "Acceptance Rate", "AcceptanceRate"]) or None

        if difficulty_key and question_difficulty.strip().lower() != difficulty_key:
            continue

        if topic_key:
            lowered_topics = [t.lower() for t in topics]
            if topic_key not in lowered_topics and topic_key not in " ".join(lowered_topics):
                continue

        if not title:
            continue

        candidates.append(
            CompanyQuestion(
                company=company_dir,
                title=title,
                difficulty=question_difficulty,
                link=link,
                topics=topics,
                frequency=frequency,
                acceptance_rate=acceptance,
            )
        )

    if not candidates:
        raise LeetCodeSourceError("No matching questions found for filters")

    return random.choice(candidates)
