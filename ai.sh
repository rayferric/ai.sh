# Sourced from .bashrc or .zshrc to set up AI tool aliases and functions

if [ -n "$BASH_SOURCE" ]; then
    _AI_SH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -n "$ZSH_VERSION" ]; then
    _AI_SH_ROOT="$(cd "$(dirname "${(%):-%N}")" && pwd)"
else
    _AI_SH_ROOT="$(cd "$(dirname "$0")" && pwd)"
fi

function ai() {
    prompt="$@"
    if [ $# -eq 0 ]; then
        printf "...> "
        read -r prompt
    fi

    cmd=$(python3 "$_AI_SH_ROOT/ai-sh-respond.py" "$prompt")
    echo "Suggested command:"
    echo -e "\n$cmd\n"
    printf "Press Enter to run, Ctrl+C to abort..."

    read -r
    echo ""
    eval "$cmd"
}
