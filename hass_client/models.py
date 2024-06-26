"""Models used for messages to/from the HA Websocket API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, NotRequired, TypedDict

MESSAGE_TYPE_AUTH: Final[str] = "auth"
MESSAGE_TYPE_AUTH_REQUIRED: Final[str] = "auth"


@dataclass
class AuthRequiredMessage:
    """
    Message received in the auth phase (first message from server after connect).

    https://developers.home-assistant.io/docs/api/websocket#authentication-phase
    """

    type: str  # auth_required
    ha_version: str  # 2021.5.3


@dataclass
class AuthCommandMessage:
    """
    Message sent in the auth phase (first message from client to server).

    https://developers.home-assistant.io/docs/api/websocket#authentication-phase
    """

    type: str  # auth
    access_token: str


@dataclass
class AuthResultMessage:
    """
    Message received as result on the auth command.

    https://developers.home-assistant.io/docs/api/websocket#authentication-phase
    """

    type: str  # auth_ok or auth_invalid
    ha_version: str | None
    message: str | None  # in case of error


@dataclass
class Message:
    """
    Base Message format for exchanging messages with the server.

    https://developers.home-assistant.io/docs/api/websocket/#command-phase
    """

    type: str
    id: int


class CommandMessage(Message):
    """
    Message when sending a command from client to server.

    https://developers.home-assistant.io/docs/api/websocket/#command-phase
    """


@dataclass
class Context:
    """Context received in an event or result message."""

    id: str
    parent_id: str | None
    user_id: str | None


CommandResultData = dict[str, Any] | list[dict[str, Any]]


class CommandResultMessage(Message):
    """
    Message when receiving the result of a command.

    https://developers.home-assistant.io/docs/api/websocket/#command-phase
    """

    success: bool
    result: CommandResultData


@dataclass
class Event:
    """
    Event object received in Event message.

    https://developers.home-assistant.io/docs/api/websocket/#subscribe-to-events
    """

    event_type: str  # e.g. state_changed
    time_fired: str  # UTC timestamp
    origin: str  # e.g. LOCAL
    context: Context
    data: dict[str, Any]


@dataclass
class Area:
    """Representation of a Home Assistant Area object within the AreaRegistry."""

    aliases: list[str]
    area_id: str
    name: str
    picture: str | None


@dataclass
class Device:
    """Representation of a Home Assistant Device object within the DeviceRegistry."""

    area_id: str | None
    configuration_url: str | None
    config_entries: list[str]
    connections: list[tuple[str, str]]
    disabled_by: str | None
    entry_type: str | None
    hw_version: str | None
    id: str
    identifiers: list[tuple[str, str]]
    manufacturer: str | None
    model: str | None
    name_by_user: str | None
    name: str
    sw_version: str | None
    via_device_id: str | None


@dataclass
class Entity:
    """Representation of a Home Assistant Entity object within the EntityRegistry."""

    area_id: str | None
    config_entry_id: str | None
    device_id: str | None
    disabled_by: str | None
    entity_category: str | None
    entity_id: str
    has_entity_name: bool
    hidden_by: str | None
    icon: str | None
    id: str
    name: str
    options: dict[str, Any]
    original_name: str
    platform: str
    translation_key: str | None
    unique_id: str
    aliases: list[str] | None
    capabilities: dict[str, Any] | None
    device_class: str | None
    original_device_class: str | None
    original_icon: str | None


@dataclass
class CallServiceResult:
    """Representation of the result received when calling a service."""

    context: Context


@dataclass
class State:
    """Representation of an (entity) State object as received from the api."""

    entity_id: str
    state: str
    attributes: dict[str, Any]
    last_changed: str
    last_updated: str
    last_reported: str
    context: Context


@dataclass
class UnitSystemDetails:
    """Representation of the Unit system details object as received from the api."""

    length: str  # e.g. km
    accumulated_precipitation: str  # e.g. mm
    mass: str  # e.g. g
    pressure: str  # e.g. Pa
    temperature: str  # e.g. "°C
    volume: str  # e.g. L
    wind_speed: str  # e.g. L


@dataclass
class Config:
    """Representation of the Hass Config object as received from the api."""

    latitude: float
    longitude: float
    elevation: float
    unit_system: UnitSystemDetails
    location_name: str
    time_zone: str
    components: list[str]
    config_dir: str
    whitelist_external_dirs: list[str]
    allowlist_external_dirs: list[str]
    allowlist_external_urls: list[str]
    version: str
    config_source: str
    safe_mode: bool
    state: str
    external_url: str | None
    internal_url: str | None
    currency: str
    country: str
    language: str


@dataclass
class CompressedState:
    """Representation of the compacted State differences object as received from the api."""

    c: str | Context | None  # context (id only or full Context obj)
    s: str | None  # state
    a: dict[str, Any] | None  # state attributes
    lc: float | None  # last_changed as timestamp
    lu: float | None  # last_updated as timestamp (if differs from last changed)


StateDiff = TypedDict(
    "StateDiff",
    {
        # '+' = in case of attribute additions
        "+": NotRequired[CompressedState],
        # '-' = in case of attribute removals
        "-": NotRequired[CompressedState],
    },
)


@dataclass
class EntityStateEvent:
    """Compact Entity State(event) object received in Event message."""

    # ruff: noqa: E501 pylint: disable=line-too-long
    # {"a":{"light.test":{"s":"on","a":{"min_color_temp_kelvin":2000,"max_color_temp_kelvin":6535,"min_mireds":153,"max_mireds":500,"effect_list":["None","candle","fire"],"supported_color_modes":["color_temp","xy"],"color_mode":"xy","brightness":255,"hs_color":[21.3,78.431],"rgb_color":[255,126,55],"xy_color":[0.5983,0.36],"effect":"None","mode":"normal","dynamics":"dynamic_palette","friendly_name":"Test Light","supported_features":44},"c":"01H0640ES8JCY1NGTNW3V41T5T","lc":1683832716.072648}}}}
    # {"c":{"light.test":{"+":{"lu":1683838800.736819,"c":"01H069T4V03S8D116YDW0GP2WC","a":{"brightness":89}}}}}}

    # NOTE: dict key = entity_id
    a: dict[str, CompressedState] | None  # entity added (or first message)
    c: dict[str, StateDiff] | None  # entity changed
    r: list[str] | None  # entity removed (list of removed entity_ids)


class EntityStateMessage(Message):
    """Compact Entity State(diff) object received in Event message."""

    event: EntityStateEvent
