from __future__ import annotations

import argparse
import logging
from pathlib import Path
import datetime as dt

import yaml

from ..account import Account
from ..account_path import AccountPath
from ..asset import Asset
from ..colors import Color
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
    format_str="%Y-%m-%dT%H:%M:%S" if with_time else "%Y-%m-%d"
    res = dt.datetime.strptime(date_str, format_str)
    if not with_time:
        res=res.replace(hour=23, minute=59, second=59, microsecond=999999)
    res=res.replace(tzinfo=dt.timezone.utc)
    return res

def load_session_info(info_path: Path) -> tuple[str, str, dt.datetime]|None:
    session_info = None
    with info_path.open("r") as info_file:
        session_info=yaml.safe_load(info_file)
    if session_info is None:
        return None
    session_info_split = session_info.split(",")
    assert len(session_info_split) == 3
    return (
        session_info_split[0],
        session_info_split[1],
        dt.datetime.fromisoformat(session_info_split[2]),
    )

def save_session_info(
        session: str,
        branch: str,
        date: dt.datetime,
        file_path: Path,
    ) -> None:
    file_path.write_text(f"{session},{branch},{date.isoformat()}")
    return

def main(logger: logging.Logger|None = None) -> None:
    """Handle command line arguments and execute."""
    if logger is None:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        logger = logging.getLogger(__name__)

    info_session="<UNSET>"
    info_branch=None
    info_date=None
    info_path = Path.cwd() / ".sortfin" / ".info"
    
    if info_path.exists():
        session_info = load_session_info(info_path)
        if session_info is not None:
            info_session, info_branch, info_date = session_info
    else:
        if not info_path.parent.exists():
            info_path.parent.mkdir()
        info_path.touch()
        #TODO what happens if file empty??
        print("No info file found. Creating a new one.")
        
    parser = argparse.ArgumentParser(description="Accounting Library CLI")
    subparser = parser.add_subparsers(
        dest="command",
        help="Sub-command to execute",
    )

#region create

    create_parser = subparser.add_parser(
        "create",
        help="Create a new session",
    )
    create_parser.add_argument(
        "file_name",
        type=str,
        help="Name of new file",
    )
    create_parser.add_argument(
        "--asset_name",
        type=str,
        default="USD",
        help="Name of the base asset",
    )
    create_parser.add_argument(
        "--asset_symbol",
        type=str,
        default="$",
        help="Symbol of the base asset",
    )
    create_parser.add_argument(
        "--initial_date",
        type=str,
        default=None,
        help="Initial Date (format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS) (default=now utc)",
    )

#endregion

#region change-session

    checkout_session_parser = subparser.add_parser(
        "change-session",
        help="Change to another existing session",
    )
    checkout_session_parser.add_argument(
        "file_name",
        type=str,
        help="Name of the YAML file (without extension)",
    )

#endregion

#region show-branches

    _ = subparser.add_parser(
        "show-branches",
        help="Show all available branches",
    )
    
#endregion

#region show-dates

    showdates_parser = subparser.add_parser(
        "show-dates",
        help=(
            "show all different available dates"
            "by default: shows all branch of MAIN branch"
        ),
    )
    showdates_parser.add_argument(
        "--branch",
        type=str,
        default=Session.DEFAULT_BRANCH,
        help="Specify a branch in particular"
    )
    
#endregion

#region checkout-date

    showdates_parser = subparser.add_parser(
        "checkout-date",
        help="checkout an existing date",
    )
    showdates_parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date (format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS) (default=now utc)",
    )

#endregion

#region push

    push_parser = subparser.add_parser(
        "push",
        help="Push the current working branch to the main branch.\n",
    )
    push_parser.add_argument(
        "--branch",
        type=str,
        default=Session.DEFAULT_BRANCH,
        help="Branch to push to (default: main branch)",
    )

#endregion

#region restore
    restore_parser = subparser.add_parser(
        "restore",
        help="Restore the current working branch to the main branch.\n",
    )
    restore_parser.add_argument(
        "--branch",
        type=str,
        default=Session.DEFAULT_BRANCH,
        help="Branch to restore to (default: main branch)",
    )
#endregion

#region add-date

    newdate_parser = subparser.add_parser(
        "add-date",
        help="Create a new date in the session",
    )
    newdate_parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date to create in the session (format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS) (default: now utc)",
    )

#endregion

#region diff
    
    diff_parser = subparser.add_parser(
        "diff",
        help=(
            "Compare a statement with another (`date` of `branch` - `date_ref` of `branch_ref`)\n"
            "by default:\n"
            "- `date_ref` = current date\n"
            "- `date` = `date_ref`\n"
            "- if `date` == `date_ref` -> 'working' `branch` versus 'main' `branch`\n"
            "- otherwise 'main' `branch` versus 'main' `branch`\n"
        )
    )
    diff_parser.add_argument(
        "--date_ref",
        type=str,
        default=None,
        help="Date of the reference statement (format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
    )
    diff_parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date of the statement (format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
    )
    diff_parser.add_argument(
        "--branch_ref",
        type=str,
        default=None,
        help="Branch of the reference statement",
    )
    diff_parser.add_argument(
        "--branch",
        type=str,
        default=None,
        help="Branch of the statement",
    )

#endregion

#region print-structure

    print_structure_parser = subparser.add_parser(
        "print-structure",
        help="Print the structure of the current statement",
    )
    print_structure_parser.add_argument(
        "--branch",
        type=str,
        default=Session.DEFAULT_WORKING_BRANCH,
        help="Branch of the printed statement",
    )

#endregion

#region print-summary

    print_summary_parser = subparser.add_parser(
        "print-summary",
        help="Print the summary of the session",
    )
    print_summary_parser.add_argument(
        "--account_path",
        type=str,
        default=None,
        help="Path to the account",
    )
    print_summary_parser.add_argument(
        "--branch",
        type=str,
        default=Session.DEFAULT_WORKING_BRANCH,
        help="Branch of the printed statement",
    )

#endregion

#region add-account

    add_account_parser = subparser.add_parser(
        "add-account",
        help="Add a new account within a folder account",
    )
    add_account_parser.add_argument(
        "account_name",
        type=str,
        help="Name of the account to add",
    )
    add_account_parser.add_argument(
        "folder_path",
        type=str,
        help="Path to the folder account where the new account will be added",
    )
    add_account_parser.add_argument(
        "account_type",
        choices=["terminal", "folder"],
        help="Type of the account (terminal or folder)",
    )

#endregion

#region delete-account
    delete_account_parser = subparser.add_parser(
        "delete-account",
        help="Delete an account",
    )
    delete_account_parser.add_argument(
        "account_path",
        type=str,
        help="Path to the account to delete",
    )
#endregion

#region change-account-value

    change_account_value_parser = subparser.add_parser(
        "change-account-value",
        help="Change the value of an account",
    )
    change_account_value_parser.add_argument(
        "account_path",
        type=str,
        help="Path to the terminal account",
    )
    change_account_value_parser.add_argument(
        "account_value",
        type=float,
        help="New value of the terminal account",
    )

#endregion

#region add-asset

    add_asset_parser = subparser.add_parser(
        "add-asset",
        help="Add a new asset to the session",
    )
    add_asset_parser.add_argument(
        "asset_name",
        type=str,
        help="Name of the new asset",
    )
    add_asset_parser.add_argument(
        "asset_symbol",
        type=str,
        help="Symbol of the new asset",
    )
    add_asset_parser.add_argument(
        "asset_pair",
        type=str,
        help="Name of the existing asset to pair with the new asset",
    )
    add_asset_parser.add_argument(
        "rate",
        type=float,
        help="Rate for the new asset and existing asset pair",
    )

#endregion

#region change-account-asset

    change_asset_parser = subparser.add_parser(
        "change-account-asset",
        help="Change asset of account",
    )
    change_asset_parser.add_argument(
        "account_path",
        type=str,
        help="Path to the account",
    )
    change_asset_parser.add_argument(
        "asset_name",
        type=str,
        help="Name of the new asset",
    )
    
#endregion

    args = parser.parse_args()
    if info_session == "<UNSET>" and args.command not in ["create", "checkout"]:
        logger.error("Session name not set. Please create a new session first.")
        return
    

#region create

    if args.command == "create":
        initial_date = dt.datetime.now(tz=dt.timezone.utc)
        if args.initial_date is not None:
            initial_date=datetime_from_str(
                args.initial_date,
                with_time=args.initial_date.find(":") != -1
            )
            
        session = initialize_session(Asset(args.asset_name, args.asset_symbol), initial_date)
        file_path = Path(args.file_name + ".yaml")
        if file_path.exists():
            err_msg=f"file already exists: {file_path}"
            logger.error(err_msg)
            return
        save_session_to_yaml(session, file_path)
        save_session_info(args.file_name, Session.DEFAULT_WORKING_BRANCH, initial_date, info_path)
        msg=f"Session created and saved to {file_path}"
        logger.info(msg)
        return
    
#endregion

#region change-session

    if args.command == "change-session":
        file_path = Path(args.file_name + ".yaml")
        if not file_path.exists():
            err_msg=f"file does not exist: {file_path}"
            logger.error(err_msg)
            return
        last_date = load_session_from_yaml(file_path).dates()[-1]
        save_session_info(
            args.file_name,
            Session.DEFAULT_BRANCH,
            last_date,
            info_path,
        )
        return
    
#endregion

    file_path = Path(info_session + ".yaml")
    session : Session = load_session_from_yaml(file_path)
    modified = False

#region show-branches

    if args.command == "show-branches":
        logger.info("Branches:\n" + "\n".join(session.branches()))
        return
    
#endregion

#region show-dates

    elif args.command == "show-dates":
        datetime_list=list(map(dt.datetime.isoformat,session.dates(branch=args.branch)))
        date_list = [d.split("T")[0] for d in datetime_list]
        final_list = [date_list[0]]
        for i in range(1, len(date_list)):
            if date_list[i] == date_list[i-1]:
                final_list[i-1] = datetime_list[i-1].split("+")[0]
                final_list += [datetime_list[i].split("+")[0]]
            else:
                final_list += [date_list[i]]
        logger.info(f"Dates (of branch {args.branch})\n" + "\n".join(final_list))
        return

#endregion

#region checkout-date

    elif args.command == "checkout-date":
        modified = False
        if args.date is None:
            args.date = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        _date = datetime_from_str(args.date, with_time=args.date.find(":") != -1)
        new_info_date = session.get_date(
            _date,
            branch=info_branch,
            is_exact_date=True,
            is_before=True,
        )
        if not session.is_different(
            info_date,
            info_date,
            Session.DEFAULT_WORKING_BRANCH,
            Session.DEFAULT_BRANCH,
        ):
            session.delete_statement(
                info_date,
                Session.DEFAULT_WORKING_BRANCH,
            )
            msg=f"Deleted working branch at date {info_date} because it was identical to main branch"
            logger.info(msg)
            modified = True
        
        test=False
        try:
            session.get_date(
            new_info_date,
            branch=Session.DEFAULT_WORKING_BRANCH,
            is_exact_date=True,)
            test=True
        except ValueError:
            pass
        if not test:
            session.copy_statement(
                new_info_date,
                new_info_date,
                branch_copy=Session.DEFAULT_BRANCH,
                branch_paste=Session.DEFAULT_WORKING_BRANCH,
            )
            msg=f"Created working branch at date {new_info_date}"
            logger.info(msg)
            modified = True

        save_session_info(
            info_session,
            Session.DEFAULT_WORKING_BRANCH,
            new_info_date,
            info_path,
        )
        msg=f"Checked out date {new_info_date} in branch {info_branch}"
        logger.info(msg)
        if not modified:
            return

#endregion

#region push

    elif args.command == "push":
        if args.branch is None:
            args.branch = Session.DEFAULT_BRANCH
        session.copy_statement(
            date_copy=info_date,
            date_paste=info_date,
            branch_copy=Session.DEFAULT_WORKING_BRANCH,
            branch_paste=args.branch,
        )
        modified = True
        msg=f"Session pushed to branch {args.branch} at date {info_date}"
        logger.info(msg)


#endregion

#region restore

    elif args.command == "restore":
        if args.branch is None:
            args.branch = Session.DEFAULT_BRANCH
        session.copy_statement(
            date_copy=info_date,
            date_paste=info_date,
            branch_copy=args.branch,
            branch_paste=Session.DEFAULT_WORKING_BRANCH,
        )
        modified = True
        msg=f"Session pushed to branch {args.branch} at date {info_date}"
        logger.info(msg)


#endregion

#region add-date

    elif args.command == "add-date":
        new_date = dt.datetime.now(tz=dt.timezone.utc).replace(microsecond=0)
        if args.date is not None:
            new_date = datetime_from_str(args.date, with_time=args.date.find(":") != -1)

        session_closest_date_before = session.try_get_date(new_date, is_exact_date=True, is_before=True)
        session_closest_date_after = session.try_get_date(new_date, is_exact_date=True, is_after=True)
        if session_closest_date_before is None:
            #special case when you are creating a date anterior to first session date
            if session_closest_date_after is None:
                raise ValueError(
                    "No session date found before or after the new date. "
                    "Please add a date before the new date first.",
                )
            if (session_closest_date_after - new_date).days > 1:
                new_date=new_date.replace(hour=0, minute=0, second=0, microsecond=0)
            print(f"Copying statement from closest date after {session_closest_date_after} to new date {new_date}")
            session.copy_statement(
                session_closest_date_after,
                new_date,
            )
        else:
            if session_closest_date_after is None:
                if (new_date - session_closest_date_before).days > 1:
                    #when you are creating a date posterior to last session date
                    new_date=new_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                #when you are creating a date between two session dates
                if (session_closest_date_after - new_date).days > 1 and \
                    (new_date - session_closest_date_before).days > 1:
                    new_date=new_date.replace(hour=0, minute=0, second=0, microsecond=0)
            print(f"Copying statement from closest date before {session_closest_date_after} to new date {new_date}")
            session.copy_statement(
                session_closest_date_before,
                new_date,
            )

        # session.copy_statement(
        #     new_date,
        #     new_date,
        #     branch_copy=Session.DEFAULT_BRANCH,
        #     branch_paste=Session.DEFAULT_WORKING_BRANCH,
        # )
        modified = True
        msg=f"New date {new_date} added to session"
        logger.info(msg)

#endregion

#region diff

    elif args.command == "diff":
        my_session_dates = session.dates()
        if len(my_session_dates) < 2:
            raise ValueError(
                "Not enough dates in the session to perform a diff. "
                "Please add at least two statements.",
            )
        diff_date = info_date
        diff_dateref = info_date
        if args.date is not None:
            diff_date=datetime_from_str(args.date, with_time=args.date.find(":") != -1)
            diff_date=session.get_date(
                diff_date,
                branch=Session.DEFAULT_WORKING_BRANCH,
                is_exact_date=True,
                is_before=True,
            )
        if args.date_ref is not None:
            diff_dateref=datetime_from_str(args.date_ref, with_time=args.date_ref.find(":") != -1)
            diff_dateref = session.get_date(
                diff_dateref,
                branch=Session.DEFAULT_WORKING_BRANCH,
                is_exact_date=True,
                is_before=True,
            )
        branch_ref = args.branch_ref if args.branch_ref is not None else Session.DEFAULT_BRANCH
        branch_diff = args.branch if args.branch is not None else (
            Session.DEFAULT_WORKING_BRANCH if diff_dateref == diff_date else Session.DEFAULT_BRANCH
        )
        logging.info((
            f"Showing Diff. between:\n"
            f" - {diff_dateref} {Color.GREEN}{branch_ref}{Color.RESET}\n"
            f" - {diff_date} {Color.GREEN}{branch_diff}{Color.RESET}"
        ))
        diff_result = session.diff(diff_dateref, diff_date, branch_ref, branch_diff)
        logger.info(diff_result)
        return
    
#endregion

#region print-structure

    elif args.command == "print-structure":
        print(session.print_structure(date=info_date, branch=args.branch))
        return

#endregion

#region print-summary

    elif args.command == "print-summary":
        logger.info(
            session.print_summary(
                date=info_date,
                branch=Session.DEFAULT_WORKING_BRANCH,
                acc_path=AccountPath(args.account_path)
            ),
        )
        return

#endregion

#region add-account

    elif args.command == "add-account":
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
                unit=session.get_account(
                    info_date,
                    Session.DEFAULT_WORKING_BRANCH,
                    folder_path
                ).unit,
                value=0.0,
            )
        elif args.account_type == "folder":
            new_account = Account(
                args.account_name,
                unit=session.get_account(
                    info_date,
                    Session.DEFAULT_WORKING_BRANCH,
                    folder_path,
                ).unit,
                sub_accounts=[],
            )
        else:
            msg=f"Account type {args.account_type} not recognized"
            raise ValueError(msg)
        session.add_account(info_date, Session.DEFAULT_WORKING_BRANCH, folder_path, new_account)
        modified = True

#endregion

#region delete-account
    elif args.command == "delete-account":
        if not args.account_path:
            logger.error(
                "Please provide the account path using --account_path",
            )
            return
        account_to_delete = session.get_account(
            info_date,
            Session.DEFAULT_WORKING_BRANCH,
            AccountPath(args.account_path),
        )
        if account_to_delete.is_terminal:
            if account_to_delete.value != 0.0:
                msg=f"Account (terminal) {args.account_path} has a non-zero value ({account_to_delete.value}) and cannot be deleted"
                logger.info(msg)
                return
        else:
            if len(account_to_delete.sub_accounts) > 0:
                msg=f"Account (folder) {args.account_path} is not empty ({len(account_to_delete.sub_accounts)} sub-accounts detected) and cannot be deleted"
                logger.info(msg)
                return
        modified = session.delete_account(info_date, Session.DEFAULT_WORKING_BRANCH, AccountPath(args.account_path))
        if not modified:
            msg=f"Something went wrong while deleting account {args.account_path}"
            logger.info(msg)
            return

#region change-account-value

    elif args.command == "change-account-value":
        if not args.account_path or args.account_value is None:
            logger.error(
                "Please provide the account path and new value"
                " using --account_path and --account_value",
            )
            return
        msg=f"Account Value: {args.account_value}"
        logger.info(msg)
        account_to_modify = session.get_account(
            info_date,
            Session.DEFAULT_WORKING_BRANCH,
            AccountPath(args.account_path),
        )
        if not account_to_modify.is_terminal:
            msg=f"Account {args.account_path} is not a terminal account"
            logger.info(msg)
            return
        account_to_modify.value = args.account_value
        modified = True

#endregion

#region add-asset

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
        fx_mkt_list = session.get_fxmarket_list(date=info_date, branch=Session.DEFAULT_BRANCH) + \
            session.get_fxmarket_list(date=info_date, branch=Session.DEFAULT_WORKING_BRANCH)
        for fx_mkt in fx_mkt_list:
            if not inv_rate:
                fx_mkt.add_quote(
                    session.asset_db, new_asset.name, asset_versus.name, args.rate,
                )
            else:
                fx_mkt.add_quote(
                    session.asset_db, asset_versus.name, new_asset.name, args.rate,
                )
        modified = True

#endregion

#region change-account-asset

    elif args.command == "change-account-asset":
        if not args.account_path or not args.asset_name:
            logger.error(
                "Please provide the account path and new asset name"
                " using --account_path and --asset_name",
            )
            return
        account_to_modify = session.get_account(None, Session.DEFAULT_WORKING_BRANCH, AccountPath(args.account_path))
        if session.asset_db.get_asset_from_name(args.asset_name) is None:
            msg=f"asset not found: {args.asset_name}"
            raise ValueError(msg)
        account_to_modify.unit =args.asset_name
        modified = True

#endregion

    else:
        msg=f"Command {args.command} not recognized"
        logger.error(msg)
        return

    if modified:
        save_session_to_yaml(session, file_path)
        msg=f"Session modified and saved to {file_path}"
        logger.info(msg)
    return

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    main(logger)


#TODO: Checkout Date!!!
# -> Delete working branch if moving from date and statements are identical
