import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.sortfin.account_path import AccountPath
from src.sortfin.cli.cli_statement import (
    load_session_from_yaml,
    load_session_info,
)
from src.sortfin.cmd import show_diff
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

ps = session.print_summary(
    date=info_date,
    branch=Session.DEFAULT_WORKING_BRANCH,
    acc_path=AccountPath("Accounts/Revolut"),
)
logger.info(ps)

pd = show_diff(
    session,
    branch_ref=Session.DEFAULT_BRANCH,
    date_ref=info_date,
    date=info_date,
    branch=Session.DEFAULT_WORKING_BRANCH,
)
logger.info(pd)
logger.info("END")


