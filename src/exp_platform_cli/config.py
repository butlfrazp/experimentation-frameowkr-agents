"""Environment configuration helpers for external services."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


class MissingConfigError(RuntimeError):
    """Raised when required environment configuration is absent."""


@dataclass(frozen=True)
class EnvironmentConfig:
    """Configuration sourced from environment variables or .env files."""

    subscription: str
    resource_group_name: str
    workspace_name: str
    project_endpoint: str
    connection_string: str
    connection_name: str = "ads-foundry-connection"

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> EnvironmentConfig:
        """Build a config from a mapping, validating required keys."""

        def _lookup(key: str) -> str:
            value = values.get(key)
            if not value:
                raise MissingConfigError(f"Environment variable '{key}' is required")
            return value

        return cls(
            subscription=_lookup("SUBSCRIPTION_NAME"),
            resource_group_name=_lookup("RESOURCE_GROUP_NAME"),
            workspace_name=_lookup("WORKSPACE_NAME"),
            project_endpoint=_lookup("FOUNDRY_PROJECT_ENDPOINT"),
            connection_string=_lookup("AZURE_FOUNDRY_CONNECTION_STRING"),
            connection_name=values.get("CONNECTION_NAME", "ads-foundry-connection"),
        )

    @classmethod
    def from_env(cls) -> EnvironmentConfig:
        """Load configuration from ``os.environ``."""

        return cls.from_mapping(os.environ)
