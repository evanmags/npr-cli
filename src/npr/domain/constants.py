from pathlib import Path

NPR_DIR = Path("~/.npr").expanduser()
NPRRC = NPR_DIR / "nprrc"
NPR_PIDFILE = NPR_DIR / "pid"
NPR_LOG_DIR = NPR_DIR / "log"
NPR_ACCESS_LOG = NPR_LOG_DIR / "access.log"
NPR_ERROR_LOG = NPR_LOG_DIR / "error.log"

NPR_CLI_SERVER_PORT = 9090
NPR_CLI_SERVER_HOST = "127.0.0.1"
NPR_CLI_SERVER_BIND = f"{NPR_CLI_SERVER_HOST}:{NPR_CLI_SERVER_PORT}"
NPR_CLI_SERVER_URL = f"http://{NPR_CLI_SERVER_BIND}"
