"""
ALGAExecutor — core execution logic.

The executor dispatches a WorkOrder to a registered handler function.
Unknown actions are executed by a safe default that returns a
structured "unsupported action" result instead of raising.

Handlers are plain callables:
    handler(order: WorkOrder) -> dict[str, Any]
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from wosds.schema import WorkOrder

logger = logging.getLogger(__name__)

HandlerFn = Callable[[WorkOrder], dict[str, Any]]


class ALGAExecutor:
    """
    Dispatch-table executor.

    Register action handlers::

        executor = ALGAExecutor()
        executor.register("ping", lambda o: {"pong": True})

    Execute a work order::

        result = executor.execute(order)
    """

    def __init__(self) -> None:
        self._handlers: dict[str, HandlerFn] = {}
        self._register_defaults()

    # ------------------------------------------------------------------ #
    # public API                                                           #
    # ------------------------------------------------------------------ #

    def register(self, action: str, handler: HandlerFn) -> None:
        """Register *handler* for *action*, replacing any previous mapping."""
        self._handlers[action] = handler

    def execute(self, order: WorkOrder) -> dict[str, Any]:
        """
        Execute *order* and return a result dict.

        Always returns a dict — never raises on unknown actions.
        """
        handler = self._handlers.get(order.action, self._default_handler)
        logger.debug("ALGA executing order %s (action=%s)", order.id, order.action)
        result: dict[str, Any] = handler(order)
        logger.debug("ALGA result for %s: %s", order.id, result)
        return result

    # ------------------------------------------------------------------ #
    # built-in handlers                                                    #
    # ------------------------------------------------------------------ #

    def _register_defaults(self) -> None:
        self._handlers["ping"] = self._handle_ping
        self._handlers["echo"] = self._handle_echo
        self._handlers["compute"] = self._handle_compute

    @staticmethod
    def _default_handler(order: WorkOrder) -> dict[str, Any]:
        return {
            "status": "unsupported",
            "action": order.action,
            "message": f"No handler registered for action '{order.action}'",
        }

    @staticmethod
    def _handle_ping(order: WorkOrder) -> dict[str, Any]:
        return {"status": "ok", "pong": True, "order_id": order.id}

    @staticmethod
    def _handle_echo(order: WorkOrder) -> dict[str, Any]:
        return {"status": "ok", "echo": order.payload}

    @staticmethod
    def _handle_compute(order: WorkOrder) -> dict[str, Any]:
        a = order.payload.get("a", 0)
        b = order.payload.get("b", 0)
        op = order.payload.get("op", "add")
        ops: dict[str, Any] = {
            "add": lambda x, y: x + y,
            "sub": lambda x, y: x - y,
            "mul": lambda x, y: x * y,
        }
        if op not in ops:
            return {"status": "error", "error": f"unknown op '{op}'"}
        return {"status": "ok", "result": ops[op](a, b)}
