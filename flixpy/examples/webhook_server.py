"""Demonstrates a webhook server.

This code creates an asynchronous HTTP server which listens for
event from Flix.
"""

from __future__ import annotations

import asyncio

import flix


@flix.webhook(path="/events", secret="572399cf-065a-4413-a2ec-6b288d3b6928")
async def on_event(event: flix.WebhookEvent) -> None:
    """Handle all events."""
    print("Got event:", event)


@on_event.handle(flix.PublishEditorialEvent)
async def on_publish_editorial(event: flix.PublishEditorialEvent) -> None:
    """Handle publishes to editorial from Flix."""
    print(f"Published from Flix to {event.target_app}")


@on_event.handle(flix.PublishFlixEvent)
async def on_publish_flix(event: flix.PublishFlixEvent) -> None:
    """Handle publishes back to Flix from editorial."""
    print(f"Published to Flix from {event.source_app}")


if __name__ == "__main__":
    # you can also set the secret separately:
    # on_event.set_secret("572399cf-065a-4413-a2ec-6b288d3b6928")
    asyncio.run(flix.run_webhook_server(on_event, port=8888))
