from __future__ import annotations

from typing import TYPE_CHECKING

from ..account_path import AccountPath  # noqa: TID252
from ..asset import Asset  # noqa: TID252
from ..session import Session  # noqa: TID252

if TYPE_CHECKING:
    import datetime as dt

def add_asset(  # noqa: PLR0913
        session: Session,
        branch: str,
        date: dt.datetime,
        asset_name: str,
        asset_symbol: str,
        asset_pair: str,
        rate: float,
        decimal_param: int,
    ) -> tuple[bool, str]:
    """Add a new asset to the session."""
    new_asset = Asset(asset_name, asset_symbol, decimal_param=decimal_param)
    asset_pair = asset_pair.split("/")
    if len(asset_pair) != 2: #noqa: PLR2004
        return False, (
            "Please provide the existing asset pair in the format"
            " `asset1/asset2`.\n",
        )
    asset_versus_input = asset_pair[1]
    inv_rate = False
    if asset_versus_input == asset_name:
        asset_versus_input = asset_pair[0]
        inv_rate = True
    elif asset_pair[0] != asset_name:
        return False, f"Asset pair does not reference the new asset: {asset_pair}.\n"
    asset_versus = session.asset_db.get_asset_from_name(asset_versus_input)
    if asset_versus is None:
        return False, f"Asset {asset_versus_input} not found in the asset database"
    session.asset_db.add_asset(new_asset)
    fx_mkt_list = session.get_fxmarket_list(date=date, branch=branch)
    for fx_mkt in fx_mkt_list:
        if not inv_rate:
            fx_mkt.add_quote(
                session.asset_db, new_asset.name, asset_versus.name, rate,
            )
        else:
            fx_mkt.add_quote(
                session.asset_db, asset_versus.name, new_asset.name, rate,
            )
    return True, (
        f"Asset added successfully to branch {branch}, date >= {date} "
        f"with {asset_pair} @ {rate}.\n"
    )

def checkout_date(
        session: Session,
        current_branch: str,
        current_date: dt.datetime,
        new_branch: str,
        new_date: dt.datetime,
    ) -> tuple[bool, str, dt.datetime, str]:
    """Check out a new date in the session (creating a working branch if necessary)."""
    new_info_date = session.get_date(
        new_date,
        branch=new_branch,
        is_exact_date=True,
        is_before=True,
    )
    if current_branch == Session.DEFAULT_WORKING_BRANCH and session.is_different(
        current_date,
        current_date,
        Session.DEFAULT_WORKING_BRANCH,
        Session.DEFAULT_BRANCH,
    ):
        return False, current_branch, current_date, (
            f"Working branch at date {current_date} is different from main branch."
            "Save or discard changes before checking out another date.\n"
        )

    session.delete_statement(
        current_date,
        Session.DEFAULT_WORKING_BRANCH,
    )
    msg = f"Deleted working branch at date {current_date}.\n"

    if session.try_get_date(
        new_info_date,
        branch=new_branch,
        is_exact_date=True,
    )[0] is None:
        session.copy_statement(
            new_info_date,
            new_info_date,
            branch_copy=Session.DEFAULT_BRANCH,
            branch_paste=new_branch,
        )
        msg += f"Created working branch at date {new_info_date}.\n"

    msg+=f"Checked out date {new_info_date} in branch {current_branch}\n"
    return True, new_branch, new_info_date, msg

def delete_date(
        session: Session,
        branch: str, # args.branch
        current_date: dt.datetime,
        date_to_delete: dt.datetime,
    ) -> tuple[bool, str]:
    """Delete a date from the session."""
    date_, msg = session.try_get_date(
        date_to_delete,
        branch=branch,
        is_exact_date=True,
    )
    if date_ is None:
        return False, msg
    if current_date == date_:
        return False, (
            "You cannot delete the current date. "
            "Please checkout another date before deleting.\n",
        )
    if branch == Session.DEFAULT_BRANCH and session.try_get_date(
        date_,
        branch=Session.DEFAULT_WORKING_BRANCH,
        is_exact_date=True,
    )[0] is not None:
        return False, (
            "You cannot delete a date from the main branch. "
            "Working branch is not fully merged yet.\n",
        )
    session.delete_statement(date_, branch)
    return True, f"Deleted date {date_} from session\n"

def change_fx_quote(  # noqa: PLR0913
        session: Session,
        branch: str,
        date: dt.datetime,
        asset1: str,
        asset2: str,
        new_quote: float,
    ) -> tuple[bool, str]:
    """Change the FX quote for a given pair of assets in the session."""
    fxmkt = session.get_fxmarket(date, branch=branch)
    return fxmkt.modify_quote(asset1, asset2, new_quote)

def change_account_value(
        session: Session,
        branch: str,
        date: dt.datetime,
        account_path: str,
        new_value: float,
    ) -> tuple[bool, str]:
    """Change the value of an account in the session."""
    account_to_modify = session.get_account(
        date,
        branch,
        AccountPath(account_path),
    )
    if not account_to_modify.is_terminal:
        return False, f"Account {account_path} is not a terminal account.\n"
    old_value = account_to_modify.value
    account_to_modify.value = new_value
    if old_value == new_value:
        return False, f"Account {account_path} value is already {new_value}.\n"
    return True, f"Account {account_path} Value: {old_value} -> {new_value}.\n"
