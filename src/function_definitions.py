"""HeyLou Function-Definitions fuer Mistral Function-Calling [CRUX-MK].

The module exposes the five HeyLou tool declarations and a deterministic adapter
that turns a real user request into a Mistral function-call plan. Unsupported or
adversarial requests are rejected before any tool call is emitted.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import Any, Mapping, Optional


DF_ID = "df-heylou-mistral-extension"


HEYLOU_FUNCTION_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "search_hotels",
        "description": (
            "Search HeyLou Travel-Knowledge-Graph for hotels matching location, dates, and preferences. "
            "Read-only, idempotent. Returns list of hotels with availability and base-rates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City or region, for example Hildesheim, Munich, or Cape Coral FL.",
                },
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                        "check_out": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                    },
                    "required": ["check_in", "check_out"],
                },
                "preferences": {
                    "type": "object",
                    "description": "Optional filters: room_type, max_price_eur, amenities.",
                    "properties": {
                        "room_type": {"type": "string"},
                        "max_price_eur": {"type": "number"},
                        "amenities": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "required": ["location", "dates"],
        },
    },
    {
        "name": "get_rates",
        "description": (
            "Fetch current rates from PMS/RMS backend for a hotel and date range. "
            "Read-only. Returns per-room-type rates with availability."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string", "description": "HeyLou hotel-ID, for example hildesheim."},
                "date_range": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                        "end": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                    },
                    "required": ["start", "end"],
                },
            },
            "required": ["hotel_id", "date_range"],
        },
    },
    {
        "name": "compare_otas",
        "description": (
            "Compare OTA prices for a hotel and dates against direct booking. "
            "Read-only. Returns spread and commission delta."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"},
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                    },
                    "required": ["check_in", "check_out"],
                },
            },
            "required": ["hotel_id", "dates"],
        },
    },
    {
        "name": "book_direct",
        "description": (
            "Direct booking via HeyLou, commission-free. K_0-RELEVANT: requires PHRONESIS_TICKET in real mode. "
            "Returns a confirmed booking with booking_id."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"},
                "room_type": {"type": "string"},
                "guest": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                    },
                    "required": ["email"],
                },
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                    },
                    "required": ["check_in", "check_out"],
                },
            },
            "required": ["hotel_id", "room_type", "guest", "dates"],
        },
    },
    {
        "name": "optimize_revenue",
        "description": (
            "Run revenue optimization for a hotel. Returns recommended rate changes per room type."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"},
                "occupancy_percent": {"type": "number"},
                "competitor_rate_eur": {"type": "number"},
            },
            "required": ["hotel_id"],
        },
    },
]


_POSITIVE_INTENT_TERMS: dict[str, tuple[str, ...]] = {
    "search_hotels": ("search", "find", "hotel", "availability", "available", "stay"),
    "get_rates": ("rate", "rates", "price", "availability", "pms", "rms"),
    "compare_otas": ("compare", "ota", "booking.com", "expedia", "hrs", "direct"),
    "book_direct": ("book", "reserve", "reservation", "guest", "direct"),
    "optimize_revenue": ("optimize", "revenue", "pricing", "yield", "occupancy"),
}

_ADVERSARIAL_TERMS = (
    "cancel",
    "delete",
    "exfiltrate",
    "ignore schema",
    "jailbreak",
    "leak",
    "refund",
    "reveal",
    "steal",
    "wipe",
)

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class FunctionCallPlan:
    """Decision emitted by the local Mistral adapter."""

    df_id: str
    accepted: bool
    function_name: Optional[str]
    arguments: dict[str, Any]
    reason: str
    required_fields: list[str]

    def to_mistral_tool_call(self) -> dict[str, Any]:
        if not self.accepted or self.function_name is None:
            raise ValueError(self.reason)
        return {"type": "function", "function": {"name": self.function_name, "arguments": self.arguments}}


def build_tool_payload() -> dict[str, Any]:
    """Build Mistral tools payload from function definitions."""

    return {"function_declarations": HEYLOU_FUNCTION_DEFINITIONS}


def get_function_names() -> list[str]:
    """Return all HeyLou function names."""

    return [fd["name"] for fd in HEYLOU_FUNCTION_DEFINITIONS]


def get_function_schema(name: str) -> Optional[dict[str, Any]]:
    """Lookup one function schema by name."""

    for fd in HEYLOU_FUNCTION_DEFINITIONS:
        if fd["name"] == name:
            return fd
    return None


def is_k0_relevant(name: str) -> bool:
    """K_0 filter: direct booking requires the guarded real-mode path."""

    return name == "book_direct"


def plan_function_call(request: Mapping[str, Any]) -> FunctionCallPlan:
    """Plan a Mistral function call from a structured user request.

    The planner uses the request's intent text and supplied arguments, validates
    against the declared schema, and emits a different rejection plan for
    adversarial or unsupported inputs.
    """

    text = str(request.get("message") or request.get("intent") or "").strip()
    args = _coerce_mapping(request.get("args") or request.get("arguments") or {})
    lowered = text.lower()

    if not text:
        return _reject("empty_request")
    if any(term in lowered for term in _ADVERSARIAL_TERMS):
        return _reject("adversarial_or_unsupported_intent")

    function_name = _select_function(lowered, args)
    if function_name is None:
        return _reject("no_matching_heylou_capability")

    schema = get_function_schema(function_name)
    if schema is None:
        return _reject("schema_not_registered")

    normalized_args = _normalize_arguments(function_name, args)
    missing_or_invalid = validate_arguments(function_name, normalized_args)
    if missing_or_invalid:
        return FunctionCallPlan(
            df_id=DF_ID,
            accepted=False,
            function_name=None,
            arguments={},
            reason="schema_validation_failed",
            required_fields=missing_or_invalid,
        )

    return FunctionCallPlan(
        df_id=DF_ID,
        accepted=True,
        function_name=function_name,
        arguments=normalized_args,
        reason="matched_heylou_mistral_capability",
        required_fields=list(schema["parameters"].get("required", [])),
    )


def validate_arguments(function_name: str, arguments: Mapping[str, Any]) -> list[str]:
    """Return missing or invalid required fields for the registered JSON-schema subset."""

    schema = get_function_schema(function_name)
    if schema is None:
        return ["function"]
    return _validate_object(schema["parameters"], arguments, "")


def _select_function(text: str, args: Mapping[str, Any]) -> Optional[str]:
    explicit = args.get("function_name")
    if isinstance(explicit, str) and get_function_schema(explicit):
        return explicit

    scores = {
        name: sum(1 for term in terms if term in text)
        for name, terms in _POSITIVE_INTENT_TERMS.items()
    }
    if args.get("guest") or "email" in args:
        scores["book_direct"] += 2
    if args.get("hotel_id") and args.get("date_range"):
        scores["get_rates"] += 2
    if args.get("hotel_id") and args.get("dates") and "compare" in text:
        scores["compare_otas"] += 2
    if args.get("location") and args.get("dates"):
        scores["search_hotels"] += 2
    if args.get("occupancy_percent") or args.get("competitor_rate_eur"):
        scores["optimize_revenue"] += 2

    winner, score = max(scores.items(), key=lambda item: item[1])
    return winner if score > 0 else None


def _normalize_arguments(function_name: str, args: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(args)
    normalized.pop("function_name", None)
    if function_name == "get_rates" and "dates" in normalized and "date_range" not in normalized:
        dates = _coerce_mapping(normalized.pop("dates"))
        normalized["date_range"] = {"start": dates.get("check_in"), "end": dates.get("check_out")}
    if function_name in {"get_rates", "compare_otas", "book_direct", "optimize_revenue"}:
        if "hotel_id" in normalized and isinstance(normalized["hotel_id"], str):
            normalized["hotel_id"] = normalized["hotel_id"].strip().lower().replace(" ", "-")
    return normalized


def _validate_object(schema: Mapping[str, Any], value: Any, prefix: str) -> list[str]:
    if schema.get("type") == "object" and not isinstance(value, Mapping):
        return [prefix.rstrip(".") or "arguments"]

    errors: list[str] = []
    properties = _coerce_mapping(schema.get("properties"))
    for key in schema.get("required", []):
        field_path = f"{prefix}{key}"
        if key not in value:
            errors.append(field_path)
            continue
        child_schema = _coerce_mapping(properties.get(key))
        child_value = value[key]
        if child_schema.get("type") == "object":
            errors.extend(_validate_object(child_schema, child_value, f"{field_path}."))
        elif not _is_valid_scalar(child_schema, child_value):
            errors.append(field_path)

    return errors


def _is_valid_scalar(schema: Mapping[str, Any], value: Any) -> bool:
    expected = schema.get("type")
    if expected == "string":
        if not isinstance(value, str) or not value.strip():
            return False
        description = str(schema.get("description", ""))
        if "ISO date" in description or _ISO_DATE_RE.match(value):
            return _valid_iso_date(value)
        return True
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "array":
        return isinstance(value, list)
    return True


def _valid_iso_date(value: str) -> bool:
    if not _ISO_DATE_RE.match(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _coerce_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _reject(reason: str) -> FunctionCallPlan:
    return FunctionCallPlan(
        df_id=DF_ID,
        accepted=False,
        function_name=None,
        arguments={},
        reason=reason,
        required_fields=[],
    )
