"""Demonstrates how to register a new webhook with the Flix Server.

This example registers a new webhook called "My webhook"
which listens for editorial publishes and exports to Storyboard Pro.
"""

from __future__ import annotations

import asyncio
import os

import flix

HOSTNAME = "localhost"
PORT = 8080
API_KEY = os.getenv("FLIX_API_KEY")
API_SECRET = os.getenv("FLIX_API_SECRET")


async def register_webhook() -> None:
    """Register a webhook with Flix."""
    async with flix.Client(HOSTNAME, PORT, api_key=API_KEY, api_secret=API_SECRET) as client:
        webhook = await client.post(
            "/webhook",
            body={
                "name": "My webhook",
                "events": [
                    {
                        "name": "Publish to editorial",  # publish to editorial
                    },
                    {
                        "name": "Sequence revision sent to SBP",  # export to sbp
                    },
                ],
                "protocol": "TCP",
                # URL where our webhook server is running
                "url": "https://flix.company.com:8888/events",
                "retry_count": 3,
            },
        )
        print("Secret:", webhook["secret"])


if __name__ == "__main__":
    asyncio.run(register_webhook())
