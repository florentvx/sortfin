import yaml
import argparse
from pathlib import Path
from  ..statement import statement
from ..account_path import account_path
from ..asset import asset
from ..account import account
from ..statement import initialize_statement
from ..to_yaml import from_dict_to_statement, from_statement_to_dict

def load_statement_from_yaml(file_path: Path) -> statement:
    with open(file_path, 'r') as file:
        state_dict = yaml.safe_load(file)
    return from_dict_to_statement(state_dict)

def save_statement_to_yaml(state: statement, file_path: Path):
    state_dict = from_statement_to_dict(state)
    with open(file_path, 'w') as file:
        yaml.safe_dump(state_dict, file)

def main() -> None:
    session_name='<UNSET>'
    session_path = Path.cwd() / ".sortfin" / ".session"
    with session_path.open() as session_file:
        session_name=session_file.readline()

    parser = argparse.ArgumentParser(description="Accounting Library CLI")
    #parser.add_argument('file_name', type=str, help="Name of the YAML file (without extension)")
    subparser = parser.add_subparsers(dest='command', help='Sub-command to execute')
    
    create_parser = subparser.add_parser('create', help='Create a new statement')
    create_parser.add_argument('file_name', type=str, help="Name of new file")
    create_parser.add_argument('asset_name', type=str, help="Name of the base asset")
    create_parser.add_argument('asset_symbol', type=str, help="Symbol of the base asset")
    
    checkout_parser = subparser.add_parser('checkout', help='Checkout an existing statement')
    checkout_parser.add_argument('file_name', type=str, help="Name of the YAML file (without extension)")

    diff_parser = subparser.add_parser('diff', help='Compare a statement with another')
    diff_parser.add_argument('compare_file', type=str, help="Name of the second YAML file (without extension)")

    _ = subparser.add_parser('print-structure', help='Print the structure of the statement')
    
    print_summary_parser = subparser.add_parser('print-summary', help='Print the summary of the statement')
    print_summary_parser.add_argument('--account_path', type=str, help="Path to the account", default=None)

    add_account_parser = subparser.add_parser('add-account', help='Add a new account within a folder account')
    add_account_parser.add_argument('folder_path', type=str, help="Path to the folder account where the new account will be added")
    add_account_parser.add_argument('account_name', type=str, help="Name of the account to add")
    add_account_parser.add_argument('account_type', choices=['terminal', 'folder'], help="Type of the account (terminal or folder)")

    change_account_value_parser = subparser.add_parser('change-account-value', help='Change the value of an account')
    change_account_value_parser.add_argument('account_path', type=str, help="Path to the terminal account")
    change_account_value_parser.add_argument('account_value', type=float, help="New value of the terminal account")

    add_asset_parser = subparser.add_parser('add-asset', help='Add a new asset to the statement')
    add_asset_parser.add_argument('asset_name', type=str, help="Name of the new asset")
    add_asset_parser.add_argument('asset_symbol', type=str, help="Symbol of the new asset")
    add_asset_parser.add_argument('asset_pair', type=str, help="Name of the existing asset to pair with the new asset")
    add_asset_parser.add_argument('rate', type=float, help="Rate for the new asset and existing asset pair")

    change_asset_parser = subparser.add_parser('change-account-asset', help='Change asset of account')
    change_asset_parser.add_argument('account_path', type=str, help="Path to the account")
    change_asset_parser.add_argument('asset_name', type=str, help="Name of the new asset")  

    # parser.add_argument('action', choices=['create', 'diff', 'print_summary', 'print_structure', 'add_account', 'add_asset', 'change_account_asset', 'change_account_value'], help="Action to perform")
    # parser.add_argument('--compare_file', type=str, help="Name of the second YAML file for diff action (without extension)")
    # parser.add_argument('--account_name', type=str, help="Name of the account to add or modify")
    # parser.add_argument('--account_path', type=str, help="Path to the account to modify")
    # parser.add_argument('--folder_path', type=str, help="Path to the folder account where the new account will be added or modified")
    # parser.add_argument('--asset_name', type=str, help="Name of the asset to add or set for an account")
    # parser.add_argument('--asset_symbol', type=str, help="Symbol of the asset to add")
    # parser.add_argument('--asset_pair', type=str, help="Name of the existing asset to pair with the new asset")
    # parser.add_argument('--rate', type=float, help="Rate for the new asset and existing asset pair")
    # parser.add_argument('--new_value', type=float, help="New value for the account")
    # parser.add_argument('--account_type', choices=['terminal', 'folder'], help="New type for the account")
    # parser.add_argument('--new_type', choices=['terminal', 'folder'], help="New type for the account")

    args = parser.parse_args()
    if session_name == '<UNSET>' and args.command not in ['create', 'checkout']:
        print("Session name not set. Please create a new statement first.")
        return
    file_path = Path(session_name + ".yaml")

    if args.command == 'create':
        asset_name = "USD"
        asset_symbol = "$"
        if args.asset_name is None:
            if args.asset_symbol is not None:
                print("Please provide the asset name using --asset_name (as symbol provided)")
                return
        else:
            asset_name = args.asset_name
            asset_symbol = args.asset_symbol
            if args.asset_symbol is None:
                asset_symbol = asset_name[0].upper()
                print(f"Asset symbol not provided, using first letter of asset name: {asset_symbol}")
        state = initialize_statement(asset(asset_name, asset_symbol))
        file_path = Path(args.file_name + ".yaml")
        save_statement_to_yaml(state, Path(args.file_name + ".yaml"))
        session_path.write_text(args.file_name)
        print(f"Statement created and saved to {file_path}")
        return
    elif args.command == 'checkout':
        session_path.write_text(args.file_name)
        return
    
    state = load_statement_from_yaml(file_path)
    modified = False

    if args.command == 'diff':
        if not args.compare_file:
            print("Please provide the name of the second YAML file using --compare_file")
            return
        state2 = load_statement_from_yaml(Path(args.compare_file + ".yaml"))
        diff_result = state.diff(state2)
        print(diff_result)
        return
    
    elif args.command == 'print-structure':
        state.print_structure(do_print=True)
        return
    
    elif args.command == 'print-summary':
        state.print_summary(account_path(args.account_path), do_print=True)
    
    elif args.command == 'add-account':
        if not args.account_name or not args.folder_path or not args.account_type:
            print("Please provide the account name and folder path using --account_name and --folder_path and --account_type")
            return
        folder_path = account_path(args.folder_path)
        new_account : account
        if args.account_type == 'terminal':
            new_account = account(args.account_name, unit=state.get_account(folder_path).unit, value=0.0)
        elif args.account_type == 'folder':
            new_account = account(args.account_name, unit=state.get_account(folder_path).unit, sub_accounts=[])
        else:
            raise ValueError(f"Account type {args.account_type} not recognized")
        state.add_account(folder_path, new_account)
        modified = True

    elif args.command == 'change-account-value':
        if not args.account_path or args.account_value is None:
            print("Please provide the account path and new value using --account_path and --account_value")
            return
        print(f"Account Value: {args.account_value}")
        account_to_modify = state.get_account(account_path(args.account_path))
        if not account_to_modify.is_terminal:
            print(f"Account {args.account_path} is not a terminal account")
            return
        account_to_modify.value = args.account_value
        modified = True

    elif args.command == 'add-asset':
        if not args.asset_name or not args.asset_symbol or not args.asset_pair or args.rate is None:
            print("Please provide the asset name, symbol, existing asset, and rate using --asset_name, --asset_symbol, --asset_versus, and --rate")
            return
        new_asset = asset(args.asset_name, args.asset_symbol)
        asset_pair = args.asset_pair.split('/')
        if len(asset_pair) != 2:
            print("Please provide the existing asset pair in the format 'asset1/asset2'")
            return
        asset_versus_input = asset_pair[1]
        inv_rate = False
        if asset_versus_input == args.asset_name:
            asset_versus_input = asset_pair[0]
            inv_rate = True
        else:
            assert asset_pair[0] == args.asset_name, "Asset pair does not match the new asset"
        asset_versus = state.fx_market.get_asset_from_input(asset_versus_input)
        if not inv_rate:
            state.fx_market.add_quote(new_asset, asset_versus, args.rate)
        else:
            state.fx_market.add_quote(asset_versus, new_asset, args.rate)
        modified = True
    
    elif args.command == 'change-account-asset':
        if not args.account_path or not args.asset_name:
            print("Please provide the account path and new asset name using --account_path and --asset_name")
            return
        account_to_modify = state.get_account(account_path(args.account_path))
        account_to_modify.unit = state.fx_market.get_asset_from_input(args.asset_name)
        modified = True

    if modified:
        save_statement_to_yaml(state, file_path)
        print(f"Statement modified and saved to {file_path}")

if __name__ == "__main__":
    main()
