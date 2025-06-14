
export COLOR_NC='\e[0m' # No Color
export COLOR_BLACK='\e[0;30m'
export COLOR_GRAY='\e[1;30m'
export COLOR_RED='\e[0;31m'
export COLOR_LIGHT_RED='\e[1;31m'
export COLOR_GREEN='\e[0;32m'
export COLOR_LIGHT_GREEN='\e[1;32m'
export COLOR_BROWN='\e[0;33m'
export COLOR_YELLOW='\e[1;33m'
export COLOR_BLUE='\e[0;34m'
export COLOR_LIGHT_BLUE='\e[1;34m'
export COLOR_PURPLE='\e[0;35m'
export COLOR_LIGHT_PURPLE='\e[1;35m'
export COLOR_CYAN='\e[0;36m'
export COLOR_LIGHT_CYAN='\e[1;36m'
export COLOR_LIGHT_GRAY='\e[0;37m'
export COLOR_WHITE='\e[1;37m'

# Function to update the shell prompt based on the presence of a .session file
function set_sortfin_prompt() {
    if [ -f ".sortfin/.info" ]; then
        content=$(cat .sortfin/.info)
        IFS="," read -r session branch date <<< "$content"
        IFS="T" read -r date0 time0 <<< "$date"
        export PS1="$COLOR_LIGHT_BLUE($session|$branch|$date0) $COLOR_GREEN\u@\h: $COLOR_YELLOW\w\n$COLOR_NC\$ "
    else
        export PS1="$COLOR_GREEN\u@\h: $COLOR_YELLOW\w\n$COLOR_NC\$ "
    fi
}

# Automatically update the prompt before each command
PROMPT_COMMAND=set_sortfin_prompt