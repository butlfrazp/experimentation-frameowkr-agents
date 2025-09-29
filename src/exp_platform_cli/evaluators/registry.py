"""Evaluator registry and helper utilities."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from ..models import EvaluatorConfig
from .base import BaseEvaluator


class EvaluatorRegistry:
    """Simple name-based registry for evaluator implementations."""

    def __init__(self) -> None:
        self._registry: dict[str, type[BaseEvaluator]] = {}

    def register(self, name: str, evaluator: type[BaseEvaluator]) -> None:
        self._registry[name.lower()] = evaluator

    def decorator(
        self, name: str | None = None
    ) -> Callable[[type[BaseEvaluator]], type[BaseEvaluator]]:
        def _wrap(cls: type[BaseEvaluator]) -> type[BaseEvaluator]:
            key = name or cls.__name__
            self.register(key, cls)
            return cls

        return _wrap

    def get(self, name: str) -> type[BaseEvaluator] | None:
        return self._registry.get(name.lower())

    def create(self, config: EvaluatorConfig) -> BaseEvaluator | None:
        for key in (config.name, config.id):
            if not key:
                continue
            impl = self.get(key)
            if impl:
                return impl(config)
        return None

    def available(self) -> Iterable[str]:
        return self._registry.keys()


registry = EvaluatorRegistry()


def load_evaluators(configs: Iterable[EvaluatorConfig]) -> list[BaseEvaluator]:
    """Instantiate evaluators for the given configuration list."""

    instances: list[BaseEvaluator] = []
    for cfg in configs:
        inst = registry.create(cfg)
        if inst is not None:
            instances.append(inst)
    return instances


register_evaluator = registry.decorator


__all__ = [
    "registry",
    "load_evaluators",
    "register_evaluator",
    "EvaluatorRegistry",
]
