import asyncio
from contextlib import suppress


def run() -> None:
    import uvicorn

    from wizaut.api import create_app
    from wizaut.config import WizautConfig

    config = WizautConfig.discover()

    with suppress(KeyboardInterrupt, asyncio.CancelledError):
        uvicorn.run(
            create_app(config),
            host=config.host,
            port=config.port,
        )
