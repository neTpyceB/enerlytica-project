import json
import logging
from contextvars import ContextVar, Token
from datetime import datetime, timezone


_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


def bind_request_id(request_id: str) -> Token[str]:
    return _request_id_ctx.set(request_id)


def reset_request_id(token: Token[str]) -> None:
    _request_id_ctx.reset(token)


def get_request_id() -> str:
    return _request_id_ctx.get()


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, str] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_request_id(),
        }
        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)


def configure_logging() -> None:
    root_logger = logging.getLogger()
    if getattr(root_logger, "_enerlytica_logging_configured", False):
        return

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(JsonLogFormatter())

    root_logger.handlers = [stream_handler]
    root_logger.setLevel(logging.INFO)
    root_logger._enerlytica_logging_configured = True  # type: ignore[attr-defined]
