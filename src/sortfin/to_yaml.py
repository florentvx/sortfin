from __future__ import annotations
import datetime as dt

from .asset import asset
from .price import price
from .account import account
from .fx_market import fx_market
from .statement import statement

def from_assetdb_to_dict(asset_db: set[asset]):
    return [
        [a.name, a.symbol, a.decimal_symbol, a.separator_symbol, a.decimal_param, a.separator_param]
        for a in asset_db
    ]

def from_dict_to_assetdb(adb_list):
    return {
        asset(a[0], a[1], a[2], a[3], a[4], a[5])
        for a in adb_list
    }

def get_asset_from_database(name: str, asset_db: set[asset]):
    return [x for x in asset_db if x.name == name][0]

def from_price_to_tuple(price: price) -> tuple[float, str]:
    return (price.value, price.unit.name)
    

def from_tuple_to_price(t: tuple[float, str], asset_db: set[asset]):
    return price(t[0], get_asset_from_database(t[1], asset_db))

type account_dict = tuple[str, str, float|list[account_dict]]

def from_account_to_dict(account: account) -> account_dict:
    if account.sub_accounts is None:
        t = from_price_to_tuple(account.get_price())
        return (account.name, t[1], t[0])
    else:
        return (
            account.name,
            account.unit.name,
            [from_account_to_dict(sa) for sa in account.sub_accounts]
        )

def from_dict_to_account(account_dict: account_dict, asset_db: set[asset]) -> account:
    account_asset = get_asset_from_database(account_dict[1], asset_db)
    if isinstance(account_dict[2], float) or isinstance(account_dict[2], int):
        return account(
            account_dict[0],
            account_asset,
            value=account_dict[2]
        )
    else:
        return account(
            account_dict[0],
            account_asset,
            sub_accounts=[from_dict_to_account(sa, asset_db) for sa in account_dict[2]]
        )

fxmkt_list = list[tuple[str, str, float]]

def from_fxmkt_to_dict(fx_mkt: fx_market) -> fxmkt_list:
    return [
        (t[0].name, t[1].name, v)
        for t, v in fx_mkt.quotes.items()
    ]

def from_dict_to_fxmkt(fx_list: fxmkt_list, asset_db: set[asset]):
    res = fx_market()
    if len(fx_list) == 1 and fx_list[0][0] == fx_list[0][1]:
        res.set_single_asset(get_asset_from_database(fx_list[0][0], asset_db))
        return res
    for q in fx_list:
        res.add_quote(
            get_asset_from_database(q[0], asset_db),
            get_asset_from_database(q[1], asset_db),
            q[2]
        )
    return res

def from_statement_to_dict(state: statement):
    return [
        state.date.isoformat(),
        from_assetdb_to_dict(state.fx_market.get_asset_database()),
        from_fxmkt_to_dict(state.fx_market),
        from_account_to_dict(state.account),
    ]

def from_dict_to_statement(state_dict):
    asset_db = from_dict_to_assetdb(state_dict[1])
    return statement(
        dt.datetime.fromisoformat(state_dict[0]),
        from_dict_to_fxmkt(state_dict[2], asset_db),
        from_dict_to_account(state_dict[3], asset_db)
    )