"""
MonidClient — Unified wrapper for the Monid.ai HTTP API.

This is the SINGLE data layer for all external data needs:
- Company enrichment (account profiles, LOBs, tech stacks)
- People search (find contacts by company + title)
- Contact enrichment (email, phone, LinkedIn data)
- LinkedIn scraping (profile data, posts, activity)
- Technographic data (what tools a company uses)

Usage:
    from backend.utils.monid_client import monid

    # Discover tools for a task
    tools = await monid.discover("company enrichment by domain")

    # Run a specific tool dynamically
    result = await monid.run_with_mapping(
        provider="apollo",
        endpoint="/organizations/enrich",
        data={"company_name": "BNY", "company_domain": "bny.com"}
    )
"""

import httpx
import asyncio
import logging
from typing import Optional, Tuple
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MonidClient:
    """Async HTTP client for Monid.ai API (MCP data layer)."""

    # The Rosetta Stone: Maps our standard internal variables to various API parameter names
    FIELD_MAPPINGS = {
        "company_name": ["name", "company", "company_name", "organization", "q", "query", "search", "keyword"],
        "account_name": ["name", "company", "company_name", "organization", "q", "query", "search", "keyword"],
        "company_domain": ["domain", "website", "url", "company_url"],
        "account_domain": ["domain", "website", "url", "company_url"],
        "person_name": ["name", "person", "full_name", "contact"],
        "job_title": ["title", "job_title", "role", "position"],
        "linkedin_url": ["linkedin", "linkedin_url", "profile", "url", "social_url"]
    }

    def __init__(self):
        self.base_url = settings.MONID_BASE_URL
        self.api_key = settings.MONID_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self._poll_interval = 5      # seconds between polls
        self._max_poll_time = 300    # 5 minutes max wait

    # ── discover ───────────────────────────────
    async def discover(self, query: str, limit: int = 10, min_score: float = 0.5) -> dict:
        """Find available tools/endpoints for a task."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/discover",
                headers=self.headers,
                json={"query": query, "limit": limit, "minScore": min_score},
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Monid discover '{query}' → {len(data.get('endpoints', []))} results")
            return data

    # ── inspect ────────────────────────────────
    async def inspect(self, provider: str, endpoint: str) -> dict:
        """Get the input schema for a specific endpoint."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/inspect",
                headers=self.headers,
                json={"provider": provider, "endpoint": endpoint},
            )
            response.raise_for_status()
            return response.json()
            
    # ── dynamic schema mapping ──────────────────
    def build_dynamic_payload(self, schema: dict, data: dict) -> Tuple[dict, dict, dict]:
        """
        Dynamically generates the mapped body, query_params, and path_params 
        to perfectly match the specific tool's inputSchema requirements.
        """
        body, query_params, path_params = {}, {}, {}
        
        input_def = schema.get("input", {})
        
        def _map_properties(schema_section, target_dict):
            if not schema_section: return
            properties = schema_section.get("properties", {})
            for field_name in properties.keys():
                field_lower = field_name.lower()
                for key, mapped_names in self.FIELD_MAPPINGS.items():
                    if field_lower in mapped_names and key in data:
                        target_dict[field_name] = data[key]
                        break

        _map_properties(input_def.get("body"), body)
        _map_properties(input_def.get("queryParams"), query_params)
        _map_properties(input_def.get("pathParams"), path_params)
        
        return body, query_params, path_params
        
    async def run_with_mapping(self, provider: str, endpoint: str, data: dict, wait: bool = True) -> dict:
        """
        High-level wrapper that automatically inspects the schema, builds the precise 
        payload, and executes the run. Prevents 400 Bad Request schema mismatches.
        """
        logger.info(f"Inspecting schema for {provider} {endpoint} to map data...")
        schema = await self.inspect(provider, endpoint)
        
        body, query_params, path_params = self.build_dynamic_payload(schema, data)
        
        if not body and not query_params and not path_params:
            logger.warning(f"Could not map any data fields to {provider} {endpoint}. Sent data: {data}")
            
        return await self.run(
            provider=provider,
            endpoint=endpoint,
            body=body if body else None,
            query_params=query_params if query_params else None,
            path_params=path_params if path_params else None,
            wait=wait
        )

    # ── run ─────────────────────────────────────
    async def run(
        self,
        provider: str,
        endpoint: str,
        body: Optional[dict] = None,
        query_params: Optional[dict] = None,
        path_params: Optional[dict] = None,
        wait: bool = True,
    ) -> dict:
        """Execute a data endpoint."""
        payload = {"provider": provider, "endpoint": endpoint}
        if body:
            payload["input"] = {"body": body} if not payload.get("input") else {**payload.get("input", {}), "body": body}
        if query_params:
            payload["input"] = {"queryParams": query_params} if not payload.get("input") else {**payload.get("input", {}), "queryParams": query_params}
        if path_params:
            payload["input"] = {"pathParams": path_params} if not payload.get("input") else {**payload.get("input", {}), "pathParams": path_params}

        # Handle backward compatibility: older code passed body directly in 'input'
        # If payload['input'] is heavily nested, it's correct for v1/run.
        # However, Monid run endpoint requires `{"input": {"body": {...}, "queryParams": {...}}}`.
        # This structure matches the standard.

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/run",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Monid /run HTTP error: {e.response.status_code} - {e.response.text}")
                return {"status": "ERROR", "error": e.response.text}
            except Exception as e:
                logger.error(f"Monid /run unexpected error: {str(e)}")
                return {"status": "ERROR", "error": str(e)}

            logger.info(
                f"Monid run {provider}/{endpoint} → status={result.get('status')}, "
                f"runId={result.get('runId')}"
            )

            # If async run and we want to wait for completion
            if wait and result.get("status") == "RUNNING":
                return await self._poll_until_done(result["runId"])

            return result

    # ── poll ────────────────────────────────────
    async def _poll_until_done(self, run_id: str) -> dict:
        """Poll a run until it completes or times out."""
        elapsed = 0
        async with httpx.AsyncClient(timeout=30) as client:
            while elapsed < self._max_poll_time:
                await asyncio.sleep(self._poll_interval)
                elapsed += self._poll_interval

                try:
                    response = await client.get(
                        f"{self.base_url}/runs/{run_id}",
                        headers=self.headers,
                    )
                    response.raise_for_status()
                    result = response.json()
                except httpx.HTTPStatusError as e:
                    logger.error(f"Monid run poll HTTP error: {e.response.status_code} - {e.response.text}")
                    return {"status": "ERROR", "runId": run_id, "error": str(e)}
                except Exception as e:
                    logger.error(f"Monid run poll unexpected error: {str(e)}")
                    return {"status": "ERROR", "runId": run_id, "error": str(e)}

                status = result.get("status")
                if status in ("COMPLETED", "SUCCEEDED"):
                    logger.info(f"Monid run {run_id} completed in {elapsed}s")
                    return result
                elif status in ("FAILED", "ERROR"):
                    logger.error(f"Monid run {run_id} failed: {result}")
                    return result

        logger.warning(f"Monid run {run_id} timed out after {self._max_poll_time}s")
        return {"status": "TIMEOUT", "runId": run_id}

    # ── SPECIFIC WORKFLOWS ──────────────────────

    async def get_company_firmographics(self, company_name: str, company_domain: str = None) -> dict:
        """Level 1: Collect company firmographics."""
        query = f"company enrichment firmographics for {company_name}"
        discovery = await self.discover(query, limit=3)
        endpoints = discovery.get("results", [])
        if not endpoints:
            return {}
            
        best = endpoints[0]
        data = {"name": company_name}
        if company_domain:
            data["domain"] = company_domain
            
        result = await self.run_with_mapping(
            provider=best["provider"],
            endpoint=best["endpoint"],
            data=data,
            wait=True,
        )
        return result.get("output") or result.get("data") or {}

    async def get_people_in_department(self, company_name: str, department: str, company_domain: str = None) -> list:
        """Search people employees at a company in a specific department."""
        query = f"search people employees at company {company_name} in {department} department"
        discovery = await self.discover(query, limit=3)
        endpoints = discovery.get("results", [])
        if not endpoints:
            return []
            
        best = endpoints[0]
        data = {"company": company_name, "department": department}
        if company_domain:
            data["domain"] = company_domain
            
        result = await self.run_with_mapping(
            provider=best["provider"],
            endpoint=best["endpoint"],
            data=data,
            wait=True,
        )
        raw = result.get("output") or result.get("data") or {}
        return raw.get("people") or raw.get("results") or raw.get("employees") or []

    async def get_linkedin_profile(self, linkedin_url: str) -> dict:
        """Scrape LinkedIn profile for education and experience."""
        query = "linkedin profile scraper education experience"
        discovery = await self.discover(query, limit=3)
        endpoints = discovery.get("results", [])
        if not endpoints:
            return {}
            
        best = endpoints[0]
        result = await self.run_with_mapping(
            provider=best["provider"],
            endpoint=best["endpoint"],
            data={"linkedin_url": linkedin_url},
            wait=True,
        )
        return result.get("output") or result.get("data") or {}

    async def get_company_technographics(self, company_name: str, company_domain: str = None) -> dict:
        """Collect company technographics and tech stack."""
        query = f"company technology stack technographics for {company_domain or company_name}"
        discovery = await self.discover(query, limit=3)
        endpoints = discovery.get("results", [])
        if not endpoints:
            return {}
            
        best = endpoints[0]
        data = {"name": company_name}
        if company_domain:
            data["domain"] = company_domain
            
        result = await self.run_with_mapping(
            provider=best["provider"],
            endpoint=best["endpoint"],
            data=data,
            wait=True,
        )
        return result.get("output") or result.get("data") or {}

    async def get_linkedin_activity(self, linkedin_url: str) -> dict:
        """Scrape recent LinkedIn activity/posts."""
        query = "linkedin posts activity scraper"
        discovery = await self.discover(query, limit=3)
        endpoints = discovery.get("results", [])
        if not endpoints:
            return {}
            
        best = endpoints[0]
        result = await self.run(
            provider=best["provider"],
            endpoint=best["endpoint"],
            body={"profileUrl": linkedin_url, "maxItems": 10},
            wait=True,
        )
        return result.get("output") or result.get("data") or {}

    # ── balance ─────────────────────────────────
    async def check_balance(self) -> dict:
        """Check current Monid wallet balance."""
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self.base_url}/wallet/balance",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()


# ── Singleton instance ─────────────────────────
monid = MonidClient()
