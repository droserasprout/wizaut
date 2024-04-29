import asyncio
from contextlib import suppress


def run() -> None:

    import uvicorn
    import uvicorn.config

    from wizaut.api import create_app
    from wizaut.config import WizautConfig

    uvicorn.config.LOGGING_CONFIG['loggers']['wizaut'] = {
        'handlers': ['default'],
        'level': 'DEBUG',
    }

    config = WizautConfig.discover()

    with suppress(KeyboardInterrupt, asyncio.CancelledError):
        uvicorn.run(
            create_app(config),
            host=config.host,
            port=config.port,
        )
