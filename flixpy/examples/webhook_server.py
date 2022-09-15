import aiohttp.web

import flix


@flix.webhook(secret="572399cf-065a-4413-a2ec-6b288d3b6928")
async def on_event(event: flix.WebhookEvent) -> None:
    print("Got event:", event)


@on_event.handle(flix.PublishEditorialEvent)
async def on_publish_editorial(event: flix.PublishEditorialEvent) -> None:
    print(f"Published from Flix to {event.target_app}")


@on_event.handle(flix.PublishFlixEvent)
async def on_publish_flix(event: flix.PublishFlixEvent) -> None:
    print(f"Published to Flix from {event.source_app}")


if __name__ == "__main__":
    # you can also set the secret separately:
    # on_event.set_secret("572399cf-065a-4413-a2ec-6b288d3b6928")
    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.post("/events", on_event)])
    aiohttp.web.run_app(app, port=8888)
