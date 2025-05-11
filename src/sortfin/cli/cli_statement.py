from __future__ import annotations

import argparse
import logging
from pathlib import Path

import yaml

from ..account import Account
from ..account_path import AccountPath
from ..asset import Asset
from ..statement import Statement, initialize_statement
from ..to_yaml import from_list_to_statement, from_statement_to_list


def load_statement_from_yaml(file_path: Path) -> Statement:
    """Load a statement from a YAML file."""
    with Path.open(file_path) as file:
        state_dict = yaml.safe_load(file)
    return from_list_to_statement(state_dict)

def save_statement_to_yaml(state: Statement, file_path: Path) -> None:
    """Save a statement to a YAML file."""
    state_dict = from_statement_to_list(state)
    with Path.open(file_path, "w") as file:
        yaml.safe_dump(state_dict, file)

def main(logger: logging.Logger|None = None) -> None: #noqa: C901, PLR0911, PLR0912, PLR0915
    """Handle command line arguments and execute."""
    if logger is None:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        logger = logging.getLogger(__name__)

    session_name="<UNSET>"
    session_path = Path.cwd() / ".sortfin" / ".session"
    with session_path.open() as session_file:
        session_name=session_file.readline()

    parser = argparse.ArgumentParser(description="Accounting Library CLI")
    subparser = parser.add_subparsers(dest="command",
                                      help="Sub-command to execute")

    create_parser = subparser.add_parser("create",
                                         help="Create a new statement")
    create_parser.add_argument("file_name", type=str,
                               help="Name of new file")
    create_parser.add_argument("asset_name", type=str,
                               help="Name of the base asset")
    create_parser.add_argument("asset_symbol", type=str,
                               help="Symbol of the base asset")

    checkout_parser = subparser.add_parser("checkout",
                                           help="Checkout an existing statement")
    checkout_parser.add_argument("file_name", type=str,
                                 help="Name of the YAML file (without extension)")

    diff_parser = subparser.add_parser("diff",
                                       help="Compare a statement with another")
    diff_parser.add_argument("compare_file", type=str,
                             help="Name of the second YAML file (without extension)")

    _ = subparser.add_parser("print-structure",
                             help="Print the structure of the statement")

    print_summary_parser = subparser.add_parser("print-summary",
                                                help="Print the summary of the statement") #noqa: E501
    print_summary_parser.add_argument("--account_path", type=str, default=None,
                                      help="Path to the account")

    add_account_parser = subparser.add_parser("add-account",
                                              help="Add a new account within a folder account") #noqa: E501
    add_account_parser.add_argument("folder_path", type=str,
                                    help="Path to the folder account where the new account will be added") #noqa: E501
    add_account_parser.add_argument("account_name", type=str,
                                    help="Name of the account to add")
    add_account_parser.add_argument("account_type", choices=["terminal", "folder"],
                                    help="Type of the account (terminal or folder)")

    change_account_value_parser = subparser.add_parser("change-account-value",
                                                       help="Change the value of an account") #noqa: E501
    change_account_value_parser.add_argument("account_path", type=str,
                                             help="Path to the terminal account")
    change_account_value_parser.add_argument("account_value", type=float,
                                             help="New value of the terminal account")

    add_asset_parser = subparser.add_parser("add-asset",
                                            help="Add a new asset to the statement")
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
        logger.error("Session name not set. Please create a new statement first.")
        return
    file_path = Path(session_name + ".yaml")

    if args.command == "create":
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
        state = initialize_statement(Asset(asset_name, asset_symbol))
        file_path = Path(args.file_name + ".yaml")
        save_statement_to_yaml(state, Path(args.file_name + ".yaml"))
        session_path.write_text(args.file_name)
        msg=f"Statement created and saved to {file_path}"
        logger.info(msg)
        return

    if args.command == "checkout":
        session_path.write_text(args.file_name)
        return

    state = load_statement_from_yaml(file_path)
    modified = False

    if args.command == "diff":
        if not args.compare_file:
            logger.error(
                "Please provide the name of the second YAML file"
                " using --compare_file",
            )
            return
        state2 = load_statement_from_yaml(Path(args.compare_file + ".yaml"))
        diff_result = state.diff(state2)
        logger.info(diff_result)
        return

    if args.command == "print-structure":
        logger.info(state.print_structure())
        return

    if args.command == "print-summary":
        logger.info(state.print_summary(AccountPath(args.account_path)))
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
                unit=state.get_account(folder_path).unit,
                value=0.0,
            )
        elif args.account_type == "folder":
            new_account = Account(
                args.account_name,
                unit=state.get_account(folder_path).unit,
                sub_accounts=[],
            )
        else:
            msg=f"Account type {args.account_type} not recognized"
            raise ValueError(msg)
        state.add_account(folder_path, new_account)
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
        account_to_modify = state.get_account(AccountPath(args.account_path))
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
        asset_versus = state.fx_market.get_asset_from_input(asset_versus_input)
        if not inv_rate:
            state.fx_market.add_quote(new_asset, asset_versus, args.rate)
        else:
            state.fx_market.add_quote(asset_versus, new_asset, args.rate)
        modified = True

    elif args.command == "change-account-asset":
        if not args.account_path or not args.asset_name:
            logger.error(
                "Please provide the account path and new asset name"
                " using --account_path and --asset_name",
            )
            return
        account_to_modify = state.get_account(AccountPath(args.account_path))
        account_to_modify.unit = state.fx_market.get_asset_from_input(args.asset_name)
        modified = True

    if modified:
        save_statement_to_yaml(state, file_path)
        msg=f"Statement modified and saved to {file_path}"
        logger.info(msg)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    main(logger)
