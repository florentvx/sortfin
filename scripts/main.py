from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.sortfin.cli.cli_statement import load_statement_from_yaml

path = Path(r"C:\Workarea\temp\sortfin")

state = load_statement_from_yaml(path / "poop.yaml")
state.print_structure()