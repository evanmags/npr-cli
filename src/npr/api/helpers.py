import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, Request
from flask.logging import default_handler

from npr.domain import Stream
from npr.domain.constants import (
    NPR_ACCESS_LOG,
    NPR_DIR,
    NPR_ERROR_LOG,
    NPR_LOG_DIR,
    NPRRC,
)


def marshal_stream_from_request(request: Request) -> Stream | None:
    if not request.is_json or request.json is None:
        return None

    return Stream(**request.json)


def init_npr_files():
    NPR_DIR.mkdir(exist_ok=True)
    NPR_LOG_DIR.mkdir(exist_ok=True)

    for f in [NPR_ACCESS_LOG, NPR_ERROR_LOG, NPRRC]:
        f.touch()


def init_logging(app: Flask):
    app.logger.removeHandler(default_handler)
    app.logger.removeHandler(
        RotatingFileHandler(
            NPR_ACCESS_LOG,
            maxBytes=1024 * 1024,
            backupCount=5,
        )
    )

    werk_logger = logging.getLogger("werkzeug")
    werk_logger.addHandler(
        RotatingFileHandler(
            NPR_ACCESS_LOG,
            maxBytes=1024 * 1024,
            backupCount=5,
        )
    )
