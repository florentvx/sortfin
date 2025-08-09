from __future__ import annotations

from typing import TYPE_CHECKING

from ..session import Session  # noqa: TID252

if TYPE_CHECKING:
    import datetime as dt


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
