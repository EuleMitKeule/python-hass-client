"""Some simple tests/example for the Home Assistant client."""

import argparse
import asyncio
import logging
import sys
from contextlib import suppress

from aiohttp import ClientSession

from hass_client import HomeAssistantClient
from hass_client.exceptions import NotFoundError
from hass_client.models import Event

LOGGER = logging.getLogger()


def get_arguments() -> argparse.Namespace:
    """Get parsed passed in arguments."""
    parser = argparse.ArgumentParser(
        description="Home Assistant simple client for Python"
    )
    parser.add_argument("--debug", action="store_true", help="Log with debug level")
    parser.add_argument(
        "url", type=str, help="URL of server, ie http://homeassistant:8123"
    )
    parser.add_argument("token", type=str, help="Long Lived Token")
    arguments = parser.parse_args()
    return arguments


async def start_cli() -> None:
    """Run main."""
    args = get_arguments()
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level)

    async with ClientSession() as session:
        await connect(args, session)


class SomeError(Exception):
    pass


def handle_some_error():
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except SomeError as e:
                LOGGER.error("Some error: %s", e)
            except NotFoundError as e:
                LOGGER.error("Not found error: %s", e)

        return wrapper

    return decorator


@handle_some_error()
async def tick() -> None:
    LOGGER.info("Tick")
    await asyncio.sleep(1)
    raise SomeError("Some error")


async def connect(args: argparse.Namespace, session: ClientSession) -> None:
    """Connect to the server."""
    websocket_url = args.url.replace("http", "ws") + "/api/websocket"
    async with HomeAssistantClient(websocket_url, args.token, session) as client:
        await client.subscribe_events(log_events)

        @handle_some_error()
        async def throw_error(event: Event) -> None:
            await client.get_state("aoingbfoidng")

        await client.subscribe_events(throw_error)

        while True:
            await tick()


@handle_some_error()
async def log_events(event: Event) -> None:
    """Log node value changes."""
    if event.event_type != "state_changed":
        return
    if event.data["new_state"]["entity_id"] == "input_boolean.buro_licht_auto":
        LOGGER.info("Received event: %s", event.event_type)
        raise SomeError("Some error")


def main() -> None:
    """Run main."""
    with suppress(KeyboardInterrupt):
        asyncio.run(start_cli())

    sys.exit(0)


if __name__ == "__main__":
    main()
