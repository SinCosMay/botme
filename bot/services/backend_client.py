import httpx


class BackendClientError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class BackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def _extract_detail(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text or "Backend request failed"

        if isinstance(payload, dict):
            detail = payload.get("detail")
            if isinstance(detail, str):
                return detail
        return response.text or "Backend request failed"

    async def _request(self, method: str, path: str, *, json: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.request(method=method, url=url, json=json)
        except httpx.RequestError as exc:
            raise BackendClientError("Could not reach backend service") from exc

        if response.status_code >= 400:
            raise BackendClientError(
                self._extract_detail(response),
                status_code=response.status_code,
            )

        if not response.content:
            return {}
        return response.json()

    async def register(self, discord_id: str, cf_handle: str) -> dict:
        return await self._request(
            "POST",
            "/v1/users/register",
            json={"discord_id": discord_id, "cf_handle": cf_handle},
        )

    async def assign_problem(self, discord_id: str, mode: str = "random", **kwargs) -> dict:
        payload = {"discord_id": discord_id, "mode": mode}
        payload.update(kwargs)
        return await self._request("POST", "/v1/problems/assign", json=payload)

    async def import_leetcode(self, problems: list[dict]) -> dict:
        return await self._request(
            "POST",
            "/v1/leetcode/import/company-problems",
            json={"problems": problems},
        )

    async def assign_leetcode(self, discord_id: str, company: str, difficulty: str | None = None) -> dict:
        return await self._request(
            "POST",
            "/v1/leetcode/assign",
            json={"discord_id": discord_id, "company": company, "difficulty": difficulty},
        )

    async def mark_lc_solved(self, discord_id: str, slug: str, proof_url: str | None = None) -> dict:
        return await self._request(
            "POST",
            "/v1/submissions/leetcode/mark-solved",
            json={"discord_id": discord_id, "slug": slug, "proof_url": proof_url},
        )

    async def verify_submission(self, discord_id: str) -> dict:
        return await self._request(
            "POST",
            "/v1/submissions/verify",
            json={"discord_id": discord_id},
        )

    async def profile(self, discord_id: str) -> dict:
        return await self._request("GET", f"/v1/users/{discord_id}/profile")
