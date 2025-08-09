import datetime as dt

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
