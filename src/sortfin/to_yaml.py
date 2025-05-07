from __future__ import annotations

import datetime as dt

from .account import Account
from .asset import Asset
from .fx_market import FxMarket
from .price import Price
from .statement import Statement


def _from_assetdb_to_list(asset_db: set[Asset]) -> list[list[str]]:
    return [
        [
            a.name, a.symbol,
            a.decimal_symbol, a.separator_symbol,
            a.decimal_param, a.separator_param,
        ]
        for a in asset_db
    ]

def _from_list_to_assetdb(adb_list: list[list[str]]) -> set[Asset]:
    return {
        Asset(a[0], a[1], a[2], a[3], a[4], a[5])
        for a in adb_list
    }

def _get_asset_from_database(name: str, asset_db: set[Asset]) -> Asset:
    return next(x for x in asset_db if x.name == name)

def _from_price_to_tuple(price: Price) -> tuple[float, str]:
    return (price.value, price.unit.name)

def _from_tuple_to_price(t: tuple[float, str], asset_db: set[Asset]) -> Price:
    return Price(t[0], _get_asset_from_database(t[1], asset_db))

type AccountDict = tuple[str, str, float|list[AccountDict]]

def _from_account_to_list(account: Account) -> AccountDict:
    if account.sub_accounts is None:
        t = _from_price_to_tuple(account.get_price())
        return (account.name, t[1], t[0])
    return (
        account.name,
        account.unit.name,
        [_from_account_to_list(sa) for sa in account.sub_accounts],
    )

def _from_list_to_account(account_dict: AccountDict, asset_db: set[Asset]) -> Account:
    account_asset = _get_asset_from_database(account_dict[1], asset_db)
    if isinstance(account_dict[2], float|int):
        return Account(
            account_dict[0],
            account_asset,
            value=account_dict[2],
        )
    return Account(
        account_dict[0],
        account_asset,
        sub_accounts=[
            _from_list_to_account(sa, asset_db)
            for sa in account_dict[2]
        ],
    )

fxmkt_list = list[tuple[str, str, float]]

def _from_fxmkt_to_list(fx_mkt: FxMarket) -> fxmkt_list:
    return [
        (t[0].name, t[1].name, v)
        for t, v in fx_mkt.quotes.items()
    ]

def _from_list_to_fxmkt(fx_list: fxmkt_list, asset_db: set[Asset]) -> FxMarket:
    res = FxMarket()
    if len(fx_list) == 1 and fx_list[0][0] == fx_list[0][1]:
        res.set_single_asset(_get_asset_from_database(fx_list[0][0], asset_db))
        return res
    for q in fx_list:
        res.add_quote(
            _get_asset_from_database(q[0], asset_db),
            _get_asset_from_database(q[1], asset_db),
            q[2],
        )
    return res

def from_statement_to_list(state: Statement) -> list:
    """Convert a statement object to a list of values for YAML serialization."""
    return [
        state.date.isoformat(),
        _from_assetdb_to_list(state.fx_market.get_asset_database()),
        _from_fxmkt_to_list(state.fx_market),
        _from_account_to_list(state.account),
    ]

def from_list_to_statement(serialized_list: list) -> Statement:
    """Convert a list of values to a statement object."""
    asset_db = _from_list_to_assetdb(serialized_list[1])
    return Statement(
        dt.datetime.fromisoformat(serialized_list[0]),
        _from_list_to_fxmkt(serialized_list[2], asset_db),
        _from_list_to_account(serialized_list[3], asset_db),
    )
