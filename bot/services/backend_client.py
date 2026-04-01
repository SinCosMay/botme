import httpx


class BackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def register(self, discord_id: str, cf_handle: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/v1/users/register",
                json={"discord_id": discord_id, "cf_handle": cf_handle},
            )
        response.raise_for_status()
        return response.json()

    async def assign_problem(self, discord_id: str, mode: str = "random", **kwargs) -> dict:
        payload = {"discord_id": discord_id, "mode": mode}
        payload.update(kwargs)
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self.base_url}/v1/problems/assign", json=payload)
        response.raise_for_status()
        return response.json()

    async def import_leetcode(self, problems: list[dict]) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/v1/leetcode/import/company-problems",
                json={"problems": problems},
            )
        response.raise_for_status()
        return response.json()

    async def assign_leetcode(self, discord_id: str, company: str, difficulty: str | None = None) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/v1/leetcode/assign",
                json={"discord_id": discord_id, "company": company, "difficulty": difficulty},
            )
        response.raise_for_status()
        return response.json()

    async def mark_lc_solved(self, discord_id: str, slug: str, proof_url: str | None = None) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/v1/submissions/leetcode/mark-solved",
                json={"discord_id": discord_id, "slug": slug, "proof_url": proof_url},
            )
        response.raise_for_status()
        return response.json()

    async def verify_submission(self, discord_id: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/v1/submissions/verify",
                json={"discord_id": discord_id},
            )
        response.raise_for_status()
        return response.json()

    async def profile(self, discord_id: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{self.base_url}/v1/users/{discord_id}/profile")
        response.raise_for_status()
        return response.json()
