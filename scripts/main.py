import datetime as dt
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.sortfin.cli.cli_statement import (
    load_session_from_yaml,
    load_session_info,
    save_session_to_yaml,
)
from src.sortfin.cmd import delete_date, show_dates
from src.sortfin.session import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main_path = Path(r"C:\workspace\sortfin\sessions")
info_path = main_path / ".sortfin" / ".info"

if info_path.exists():
    session_info = load_session_info(info_path)
    if session_info is not None:
        info_session, info_branch, info_date = session_info
else:
    if not info_path.parent.exists():
        info_path.parent.mkdir()
    info_path.touch()
    logger.error("No info file found. Creating a new one.\n")


file_path = main_path / (info_session + ".yaml")
session = load_session_from_yaml(file_path)

logger.info(show_dates(session, Session.DEFAULT_BRANCH))

modified, msg = delete_date(
    session, Session.DEFAULT_BRANCH, info_date,
    dt.datetime(2017, 11, 11, tzinfo=dt.timezone.utc),
)
logger.info(msg)
if modified:
    save_session_to_yaml(session, file_path)
    msg=f"Session modified and saved to {file_path}\n"
    logger.info(msg)

