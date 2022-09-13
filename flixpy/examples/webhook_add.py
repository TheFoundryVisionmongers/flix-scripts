import asyncio

import flix


async def main():
    async with flix.Client("localhost", 8080) as client:
        await client.authenticate("admin", "admin")
        webhook = await client.post(
            "/webhook",
            {
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
                "url": "https://flix.company.com:8888/events",
                "retry_count": 3,
            },
        )
        print("Secret:", webhook["secret"])


if __name__ == "__main__":
    asyncio.run(main())
