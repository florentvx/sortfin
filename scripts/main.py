import sys
from pathlib import Path
import datetime as dt

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.sortfin.cli.cli_statement import load_session_from_yaml

path = Path(r"C:\workspace\sortfin\sessions")
session = load_session_from_yaml(path / "popo2.yaml")

main_date = dt.datetime(2025,6,18, 23, 59, 59, tzinfo=dt.timezone.utc)
study_date = session.get_date(main_date, is_exact_date=True, is_before=True)


session.print_structure(study_date)

diff_date = session.get_date(main_date, is_after=True,)
diff_dateref = diff_date

diff_date=session.get_date(
    diff_date,
    branch=session.DEFAULT_WORKING_BRANCH,
    is_exact_date=True,
    is_before=True,
)

branch_ref = session.DEFAULT_BRANCH
branch_diff = session.DEFAULT_WORKING_BRANCH if diff_dateref == diff_date \
    else session.DEFAULT_BRANCH

diff_result = session.diff(diff_dateref, diff_date, branch_ref, branch_diff)
print(diff_result)
