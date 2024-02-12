"""Demonstrates how to register a new webhook with the Flix Server.

This example registers a new webhook called "My webhook"
which listens for editorial publishes and exports to Storyboard Pro.
"""

from __future__ import annotations

import asyncio

import flix


async def register_webhook() -> None:
    """Register a webhook with Flix."""
    async with flix.Client("localhost", 8080) as client:
        await client.authenticate("admin", "admin")
        webhook = await client.post(
            "/webhook",
            body={
                "name": "My webhook",
                "events": [
                    {
                        "id": 2,  # publish to editorial
                    },
                    {
                        "id": 3,  # export to sbp
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
