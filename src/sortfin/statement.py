from __future__ import annotations
import datetime as dt
from .account_path import account_path
from .asset import asset
from .fx_market import fx_market
from .account import account

def initialize_statement(unit: asset):
    fx_mkt = fx_market()
    fx_mkt.set_single_asset(unit)
    return statement(dt.datetime.now(), fx_mkt, account(name="root", unit=unit, sub_accounts=[]))

class statement:
    def __init__(
            self, 
            date: dt.datetime, 
            fx_mkt: fx_market, 
            acc: account,
        ):
        self.date : dt.datetime = date
        self.fx_market : fx_market = fx_mkt
        self.account : account = acc
        self.print_summary(do_print=False) # forces the computation of all fx quotes needed
    
    def copy_statement(self, date: dt.datetime):
        return statement(date, self.fx_market.copy(), self.account.copy())
    
    def get_account(self, ap: account_path) -> account:
        return self.account.get_account(ap)
    
    def change_terminal_account(
            self, 
            ap: account_path, 
            value: float|None = None, 
            unit: asset|None = None,
        ) -> None:
        acc = self.get_account(ap)
        if acc.is_terminal:
            if value is not None:
                acc.value=value
            if unit is not None:
                acc.unit=unit 
        else:
            raise ValueError(f"account: [{acc}] is not terminal")
        
    def change_folder_account(self, ap:account_path, unit: asset):
        acc = self.get_account(ap)
        if not acc.is_terminal:
            if unit is not None:
                acc.unit=unit 
        else:
            raise ValueError(f"account: [{acc}] is terminal")
    
    def add_account(self, folder_path: account_path, new_account: account|str):
        folder_account = self.get_account(folder_path)
        if folder_account.sub_accounts is None:
            raise ValueError(f"Cannot add an account to a terminal account: {folder_account}")
        if isinstance(new_account, str):
            new_account = account(new_account, unit=folder_account.unit)
        folder_account.sub_accounts.append(new_account)
    
    def print_structure(self, do_print: bool = False) -> str:
        res = self.account.print_structure(do_print=False) + "\n" + str(self.fx_market)
        if do_print:
            print(res)
        return res
    
    def print_summary(self, path: account_path|None = None, unit: asset|None = None, do_print: bool = False) -> str:
        if unit is not None:
            if isinstance(unit, asset):
                unit = unit.name
        if unit is not None and not isinstance(unit, str):
                msg="unit must be an asset or a string"  
                raise ValueError(msg)
        res = f"Statement: {self.date.date().isoformat()}\n"
        res += self.account.print_account_summary(self.fx_market, path, unit, do_print=False)
        if do_print:
            print(res)
        return res
    
    def diff(self, other: statement) -> str:
        if not isinstance(other, statement):
            raise ValueError("The other object must be an instance of statement")
        
        res = ""
        if self.date != other.date:
            res += f"Date: {self.date} -> {other.date}\n"
        
        # Compare account structures
        diff_acc_struct = self.account.diff(other.account)
        if len(diff_acc_struct) > 0:
            res += "Account Structure Differences:\n"
            res +=diff_acc_struct
        
        # Compare FX markets
        res_fx = ""
        for (k, v) in self.fx_market.quotes.items():
            if k in other.fx_market.quotes:
                if v != other.fx_market.quotes[k]:
                    res_fx += f"{k[0].name}/{k[1].name}: {v} -> {other.fx_market.quotes[k]}\n"
            else:
                res_fx += f"{k[0].name}/{k[1].name}: {v} -> Not present in other statement\n"
        
        for (k, v) in other.fx_market.quotes.items():
            if k not in self.fx_market.quotes:
                res_fx += f"{k[0].name}/{k[1].name}: Not present in this statement -> {round(v,6)}\n"
        if len(res_fx) > 0:
            res += "FX Market Differences:\n"
            res += res_fx
        return res