from __future__ import annotations

import datetime as dt

from .account import Account
from .asset import Asset
from .asset_database import AssetDatabase
from .fx_market import FxMarket
from .price import Price
from .session import Session
from .statement import Statement


def _from_assetdb_to_list(asset_db: AssetDatabase) -> list:
    return [
        [
            a.name, a.symbol,
            a.decimal_symbol, a.separator_symbol,
            a.decimal_param, a.separator_param,
        ]
        for a in asset_db
    ]

def _from_list_to_assetdb(adb_list: list) -> AssetDatabase:
    asset_db = AssetDatabase()
    for a in adb_list:
        ao = Asset(a[0], a[1], a[2], a[3], a[4], a[5])
        asset_db.add_asset(ao)
    return asset_db

def _get_asset_from_database(name: str, asset_db: AssetDatabase) -> Asset:
    return next(x for x in asset_db if x.name == name)

def _from_price_to_tuple(price: Price) -> tuple[float, str]:
    return (price.value, price.unit.name)

def _from_tuple_to_price(t: tuple[float, str], asset_db: AssetDatabase) -> Price:
    return Price(t[0], _get_asset_from_database(t[1], asset_db))

type AccountDict = tuple[str, str, float|list[AccountDict]]

def _from_account_to_list(asset_db: AssetDatabase, account: Account) -> AccountDict:
    if account.sub_accounts is None:
        t = _from_price_to_tuple(account.get_price(asset_db))
        return (account.name, t[1], t[0])
    return (
        account.name,
        account.unit,
        [_from_account_to_list(asset_db, sa) for sa in account.sub_accounts],
    )

def _from_list_to_account(
        account_dict: AccountDict,
        asset_db: AssetDatabase,
    ) -> Account:
    account_asset = _get_asset_from_database(account_dict[1], asset_db)
    if isinstance(account_dict[2], float|int):
        return Account(
            account_dict[0],
            account_asset.name,
            value=account_dict[2],
        )
    return Account(
        account_dict[0],
        account_asset.name,
        sub_accounts=[
            _from_list_to_account(sa, asset_db)
            for sa in account_dict[2]
        ],
    )

fxmkt_list = list[tuple[str, str, float]]

def _from_fxmkt_to_list(fx_mkt: FxMarket) -> fxmkt_list:
    return [
        (t[0], t[1], v)
        for t, v in fx_mkt.quotes.items()
    ]

def _from_list_to_fxmkt(fx_list: fxmkt_list, asset_db: AssetDatabase) -> FxMarket:
    res = FxMarket()
    if len(fx_list) == 1 and fx_list[0][0] == fx_list[0][1]:
        return res
    for q in fx_list:
        res.add_quote(
            asset_db,
            _get_asset_from_database(q[0], asset_db).name,
            _get_asset_from_database(q[1], asset_db).name,
            q[2],
        )
    return res

def from_statement_to_list(state: Statement, asset_db: AssetDatabase) -> list:
    """Convert a statement object to a list of values for YAML serialization."""
    return [
        state.date.isoformat(),
        _from_fxmkt_to_list(state.fx_market),
        _from_account_to_list(asset_db, state.account),
    ]

def from_list_to_statement(serialized_list: list, asset_db: AssetDatabase) -> Statement:
    """Convert a list of values to a statement object."""
    return Statement(
        dt.datetime.fromisoformat(serialized_list[0]),
        _from_list_to_fxmkt(serialized_list[1], asset_db),
        _from_list_to_account(serialized_list[2], asset_db),
    )

def from_session_to_list(session: Session) -> list:
    """Convert a session object to a list of values for YAML serialization."""
    key_list = session.keys()
    return [
        _from_assetdb_to_list(session.asset_db),
        [
            (
                date.isoformat(),
                branch,
                from_statement_to_list(session.data[date], session.asset_db),
            )
            for (date, branch) in key_list
        ],
    ]

def from_list_to_session(serialized_list: list) -> Session:
    """Convert a list of values to a session object."""
    asset_db = _from_list_to_assetdb(serialized_list[0])
    session = Session(asset_db)
    for date_str, branch, statement_list in serialized_list[1]:
        date = dt.datetime.fromisoformat(date_str)
        session.data[(date, branch)] = from_list_to_statement(statement_list, asset_db)
    return session
