import datetime as dt

from ..colors import Color  # noqa: TID252
from ..session import Session  # noqa: TID252


def show_branches(session: Session) -> str:
    """Display all branches in the session."""
    return "Branches:\n" + "\n".join(session.branches())

def show_dates(session: Session, branch: str) -> str:
    """Display all dates in the specified branch of the session."""
    datetime_list=list(map(dt.datetime.isoformat,session.dates(branch=branch)))
    date_list = [d.split("T")[0] for d in datetime_list]
    final_list = [date_list[0]]
    for i in range(1, len(date_list)):
        if date_list[i] == date_list[i-1]:
            final_list[i-1] = datetime_list[i-1].split("+")[0]
            final_list += [datetime_list[i].split("+")[0]]
        else:
            final_list += [date_list[i]]
    return f"Dates (of branch {branch})\n" + "\n".join(final_list) + "\n"

def show_diff(
        session: Session,
        branch_ref: str, date_ref: dt.datetime,
        branch: str, date: dt.datetime,
    ) -> str:
    """Show the differences between two dates in specified branches of the session."""
    diff_date=session.get_date(
        date,
        branch=branch,
        is_exact_date=True,
        is_before=True,
    )
    diff_dateref = session.get_date(
        date_ref,
        branch=branch_ref,
        is_exact_date=True,
        is_before=True,
    )
    msg = (
        f"Showing Diff. between:\n"
        f" -     {diff_date} {Color.GREEN}{branch}{Color.RESET}\n"
        f" - vs. {diff_dateref} {Color.GREEN}{branch_ref}{Color.RESET}\n\n"
    )
    return msg + session.diff(diff_dateref, diff_date, branch_ref, branch)
