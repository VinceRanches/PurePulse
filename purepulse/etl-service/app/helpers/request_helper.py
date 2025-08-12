import logging
from typing import Dict

import httpx

# Configure logger for this module
logger = logging.getLogger(__name__)

async def post_request(
    endpoint: str,
    payload: Dict = None,
    headers: Dict = None
) -> Dict:
    return await __make_request(
        method="POST",
        endpoint=endpoint,
        payload=payload,
        headers=headers
    )


async def get_request(
    endpoint: str,
    params: Dict = None,
    headers: Dict = None
) -> Dict:
    return await __make_request(
        method="GET",
        endpoint=endpoint,
        payload=params,
        headers=headers
    )


async def __make_request(
    method: str,
    endpoint: str,
    payload: Dict = None,
    headers: Dict = None
) -> Dict:
    try:
        async with httpx.AsyncClient() as client:
            match method.upper():
                case "POST":
                    response = await client.post(
                        url=endpoint,
                        json=payload,
                        headers=headers
                    )
                case "GET":
                    response = await client.get(
                        url=endpoint,
                        params=payload,
                        headers=headers
                    )
                case _:
                    raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            return {
                "status": response.status_code,
                "data": response.json()
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error for {method} {endpoint}: {e.response.status_code} - {e}")
        return {
            "status": e.response.status_code,
            "error": str(e),
            "data": e.response.json() if e.response.content else {},
            "response_text": e.response.text
        }

    except httpx.RequestError as e:
        logger.error(f"Request error for {method} {endpoint}: {e}")
        return {
            "status": httpx.codes.INTERNAL_SERVER_ERROR,
            "error": "Failed to connect to the service",
            "data": {}
        }

    except Exception as e:
        logger.error(f"Unexpected error for {method} {endpoint}: {e}")
        return {
            "status": httpx.codes.INTERNAL_SERVER_ERROR,
            "error": "An unexpected error occurred",
            "data": {}
        }
