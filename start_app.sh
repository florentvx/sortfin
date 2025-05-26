#!/bin/bash


# Optional: Source the SortFin prompt script if it exists
if [ -f "$(dirname "$0")/src/sortfin/sortfin_prompt.sh" ]; then
    source "$(dirname "$0")/src/sortfin/sortfin_prompt.sh"
fi
echo "Starting SortFin CLI..."
MY_DIR=$(dirname "$(readlink -f "$0")")
cd "$MY_DIR" || exit 1

echo "Found sortfin @: $(pwd)"


# Locate the Hatch environment directory
HATCH_ENV_DIR=$(hatch env find main)

# Locate the directory of the built sortfin-cli.exe
SORTFIN_CLI_DIR="$HATCH_ENV_DIR/Scripts"

# Add the directory to PYTHONPATH
export PATH="$SORTFIN_CLI_DIR:$PATH"

# Start a new Bash session
exec bash --rcfile <(echo "export PYTHONPATH=$PYTHONPATH; source ./src/sortfin/sortfin_prompt.sh; cd /c/workspace/sortfin/sessions;echo Hello World!")
