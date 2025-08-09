from pathlib import Path

import yaml

from ..session import Session  # noqa: TID252
from ..to_yaml import from_list_to_session, from_session_to_list  # noqa: TID252


def load_session_from_yaml(file_path: Path) -> Session:
    """Load a session from a YAML file."""
    with Path.open(file_path) as file:
        session_dict = yaml.safe_load(file)
    return from_list_to_session(session_dict)

def save_session_to_yaml(session: Session, file_path: Path) -> None:
    """Save a session to a YAML file."""
    session_dict = from_session_to_list(session)
    with Path.open(file_path, "w") as file:
        yaml.safe_dump(session_dict, file)
