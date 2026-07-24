"""Adapters from source-specific logs to the canonical event contract."""

from .ednet import iter_ednet_events

__all__ = ["iter_ednet_events"]
