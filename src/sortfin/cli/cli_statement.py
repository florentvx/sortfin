from __future__ import annotations

import argparse
import logging
from pathlib import Path
import datetime as dt

import yaml

from ..account import Account
from ..account_path import AccountPath
from ..asset import Asset
from ..session import Session, initialize_session
from ..to_yaml import from_list_to_session, from_session_to_list


def load_session_from_yaml(file_path: Path) -> Session:
    """Load a session from a YAML file."""
    with Path.open(file_path) as file:
        session_dict = yaml.safe_load(file)
    return from_list_to_session(session_dict)

def save_session_to_yaml(session: Session, file_path: Path) -> None:
    """Save a session to a YAML file."""
    session_dict = from_session_to_list(session)
    with Path.open(file_path, "w") as file:
        yaml.safe_dump(session_dict, file)

def datetime_from_str(date_str: str, with_time: bool) -> dt.datetime:
    format_str="%Y-%m-%d %H:%M:%S" if with_time else "%Y-%m-%d"
    res = dt.datetime.strptime(date_str, format_str)
    if not with_time:
        res=res.replace(hour=23, minute=59, second=59, microsecond=999999)
    res=res.replace(tzinfo=dt.timezone.utc)
    return res

def main(logger: logging.Logger|None = None) -> None:
    """Handle command line arguments and execute."""
    if logger is None:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        logger = logging.getLogger(__name__)

    session_name="<UNSET>"
    session_path = Path.cwd() / ".sortfin" / ".session"
    if session_path.exists():
        with session_path.open("r") as session_file:
            session_name=session_file.readline()
    else:
        if not session_path.parent.exists():
            session_path.parent.mkdir()
        session_path.touch()
        print("No session file found. Creating a new one.")

    parser = argparse.ArgumentParser(description="Accounting Library CLI")
    subparser = parser.add_subparsers(dest="command",
                                      help="Sub-command to execute")

    create_parser = subparser.add_parser("create",
                                         help="Create a new session")
    create_parser.add_argument("file_name", type=str,
                               help="Name of new file")
    create_parser.add_argument("asset_name", type=str,
                               help="Name of the base asset")
    create_parser.add_argument("asset_symbol", type=str,
                               help="Symbol of the base asset")
    create_parser.add_argument("--initial_date", type=str, default=None,
                               help="Initial Date")

    checkout_parser = subparser.add_parser("checkout",
                                           help="Checkout an existing session")
    checkout_parser.add_argument("file_name", type=str,
                                 help="Name of the YAML file (without extension)")

    newdate_parser = subparser.add_parser("new-date",
                                          help="Create a new date in the session")
    newdate_parser.add_argument("--date", type=str, default=None,
                                help="Date to create in the session (format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)")
    
    diff_parser = subparser.add_parser("diff",
                                       help="Compare a statement with another (`date` - `date_ref`)")
    diff_parser.add_argument("--date_ref", type=str, default=None,
                             help="Date of the reference statement")
    diff_parser.add_argument("--date", type=str, default=None,
                             help="Date of the statement")
    

    print_structure_parser = subparser.add_parser("print-structure",
                                                  help="Print the structure of the session")
    print_structure_parser.add_argument("--date", type=str, default=None,
                                        help="Date of the session to print structure for")

    print_summary_parser = subparser.add_parser("print-summary",
                                                help="Print the summary of the session")
    print_summary_parser.add_argument("--account_path", type=str, default=None,
                                      help="Path to the account")

    add_account_parser = subparser.add_parser("add-account",
                                              help="Add a new account within a folder account")
    add_account_parser.add_argument("folder_path", type=str,
                                    help="Path to the folder account where the new account will be added")
    add_account_parser.add_argument("account_name", type=str,
                                    help="Name of the account to add")
    add_account_parser.add_argument("account_type", choices=["terminal", "folder"],
                                    help="Type of the account (terminal or folder)")

    change_account_value_parser = subparser.add_parser("change-account-value",
                                                       help="Change the value of an account")
    change_account_value_parser.add_argument("account_path", type=str,
                                             help="Path to the terminal account")
    change_account_value_parser.add_argument("account_value", type=float,
                                             help="New value of the terminal account")

    add_asset_parser = subparser.add_parser("add-asset",
                                            help="Add a new asset to the session")
    add_asset_parser.add_argument("asset_name", type=str,
                                  help="Name of the new asset")
    add_asset_parser.add_argument("asset_symbol", type=str,
                                  help="Symbol of the new asset")
    add_asset_parser.add_argument("asset_pair", type=str,
                                  help="Name of the existing asset to pair with the new asset") #noqa: E501
    add_asset_parser.add_argument("rate", type=float,
                                  help="Rate for the new asset and existing asset pair")

    change_asset_parser = subparser.add_parser("change-account-asset",
                                               help="Change asset of account")
    change_asset_parser.add_argument("account_path", type=str,
                                     help="Path to the account")
    change_asset_parser.add_argument("asset_name", type=str,
                                     help="Name of the new asset")

    args = parser.parse_args()
    if session_name == "<UNSET>" and args.command not in ["create", "checkout"]:
        logger.error("Session name not set. Please create a new session first.")
        return
    file_path = Path(session_name + ".yaml")

    if args.command == "create":
        initial_date = dt.datetime.now(tz=dt.timezone.utc)
        if args.initial_date is not None:
            initial_date=datetime_from_str(
                args.initial_date,
                with_time=args.initial_date.find(":") != -1
            )
            
        asset_name = "USD"
        asset_symbol = "$"
        if args.asset_name is None:
            if args.asset_symbol is not None:
                logger.error(
                    "Please provide the asset name"
                    " using --asset_name (as symbol provided)",
                )
                return
        else:
            asset_name = args.asset_name
            asset_symbol = args.asset_symbol
            if args.asset_symbol is None:
                asset_symbol = asset_name[0].upper()
                msg=(
                    "Asset symbol not provided"
                    f" using first letter of asset name: {asset_symbol}")
                logger.error(msg)
        session = initialize_session(Asset(asset_name, asset_symbol), initial_date)
        file_path = Path(args.file_name + ".yaml")
        save_session_to_yaml(session, Path(args.file_name + ".yaml"))
        session_path.write_text(args.file_name)
        msg=f"Session created and saved to {file_path}"
        logger.info(msg)
        return

    if args.command == "checkout":
        session_path.write_text(args.file_name)
        return

    session = load_session_from_yaml(file_path)
    modified = False

    if args.command == "new-date":
        new_date = dt.datetime.now(tz=dt.timezone.utc)
        if args.date is not None:
            new_date = datetime_from_str(args.date, with_time=args.date.find(":") != -1)
        session.copy_statement(session.get_date(new_date, is_exact_date=True, is_before=True), new_date)
        modified = True
        msg=f"New date {new_date} added to session"
        logger.info(msg)

    if args.command == "diff":
        my_session_dates = session.dates()
        if len(my_session_dates) < 2:
            raise ValueError(
                "Not enough dates in the session to perform a diff. "
                "Please add at least two statements.",
            )
        diff_date = my_session_dates[-1]
        diff_dateref = my_session_dates[-2]
        if args.date is not None:
            diff_date=datetime_from_str(args.date, with_time=args.date.find(":") != -1)
        if args.date_ref is not None:
            diff_dateref=datetime_from_str(args.date_ref, with_time=args.date_ref.find(":") != -1)
        diff_result = session.diff(diff_dateref, diff_date)
        logger.info(diff_result)
        return

    if args.command == "print-structure":
        print_structure_date : dt.datetime|None = None
        if args.date is not None:
            print_structure_date = datetime_from_str(
                args.date,
                with_time=args.date.find(":") != -1,
            )
        logger.info(session.print_structure(print_structure_date))
        return

    if args.command == "print-summary":
        logger.info(session.print_summary(date=None, acc_path=AccountPath(args.account_path)))
        return

    if args.command == "add-account":
        if not args.account_name or not args.folder_path or not args.account_type:
            logger.error(
                "Please provide the account name and folder path"
                " using --account_name and --folder_path and --account_type",
            )
            return
        folder_path = AccountPath(args.folder_path)
        new_account : Account
        if args.account_type == "terminal":
            new_account = Account(
                args.account_name,
                unit=session.get_account(folder_path).unit,
                value=0.0,
            )
        elif args.account_type == "folder":
            new_account = Account(
                args.account_name,
                unit=session.get_account(folder_path).unit,
                sub_accounts=[],
            )
        else:
            msg=f"Account type {args.account_type} not recognized"
            raise ValueError(msg)
        session.add_account(folder_path, new_account)
        modified = True

    elif args.command == "change-account-value":
        if not args.account_path or args.account_value is None:
            logger.error(
                "Please provide the account path and new value"
                " using --account_path and --account_value",
            )
            return
        msg=f"Account Value: {args.account_value}"
        logger.info(msg)
        account_to_modify = session.get_account(AccountPath(args.account_path))
        if not account_to_modify.is_terminal:
            msg=f"Account {args.account_path} is not a terminal account"
            logger.info(msg)
            return
        account_to_modify.value = args.account_value
        modified = True

    elif args.command == "add-asset":
        if not args.asset_name or not args.asset_symbol or \
            not args.asset_pair or args.rate is None:
            logger.error(
                "Please provide the asset name, symbol, existing asset and rate"
                " using --asset_name, --asset_symbol, --asset_versus, and --rate",
            )
            return
        new_asset = Asset(args.asset_name, args.asset_symbol)
        asset_pair = args.asset_pair.split("/")
        if len(asset_pair) != 2: #noqa: PLR2004
            logger.error(
                "Please provide the existing asset pair in the format"
                " `asset1/asset2`",
            )
            return
        asset_versus_input = asset_pair[1]
        inv_rate = False
        if asset_versus_input == args.asset_name:
            asset_versus_input = asset_pair[0]
            inv_rate = True
        elif asset_pair[0] != args.asset_name:
            msg="Asset pair does not match the new asset"
            raise ValueError(msg)
        asset_versus = session.asset_db.get_asset_from_name(asset_versus_input)
        if asset_versus is None:
            msg=f"Asset {asset_versus_input} not found in the asset database"
            raise ValueError(msg)
        session.asset_db.add_asset(new_asset)
        if not inv_rate:
            session.get_fxmarket().add_quote(
                session.asset_db, new_asset.name, asset_versus.name, args.rate,
            )
        else:
            session.get_fxmarket().add_quote(
                session.asset_db, asset_versus.name, new_asset.name, args.rate,
            )
        modified = True

    elif args.command == "change-account-asset":
        if not args.account_path or not args.asset_name:
            logger.error(
                "Please provide the account path and new asset name"
                " using --account_path and --asset_name",
            )
            return
        account_to_modify = session.get_account(AccountPath(args.account_path))
        if session.asset_db.get_asset_from_name(args.asset_name) is None:
            msg=f"asset not found: {args.asset_name}"
            raise ValueError(msg)
        account_to_modify.unit =args.asset_name
        modified = True

    if modified:
        save_session_to_yaml(session, file_path)
        msg=f"Session modified and saved to {file_path}"
        logger.info(msg)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    main(logger)
