if [ -n "$BASH_VERSION" ]; then
    _AI_SH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -n "$ZSH_VERSION" ]; then
    _AI_SH_ROOT="$(cd "$(dirname "${(%):-%N}")" && pwd)"
else
    echo "Unsupported shell. Only bash, zsh, and fish are supported."
    return 1
fi


function _push_to_shell_history() {
    if [ -n "$BASH_VERSION" ]; then
        history -s "$1"
    elif [ -n "$ZSH_VERSION" ]; then
        print -s -- "$1"
    fi
}

function ai() {
    prompt="$@"
    if [ $# -eq 0 ]; then
        printf "...> "
        read -r prompt
    fi

    # if bash, push ai() to history
    if [ -n "$BASH_VERSION" ]; then
        history -s "ai $prompt"
    fi

    cmd=$(python3 "$_AI_SH_ROOT/ai-sh-respond.py" "$prompt")
    echo "Suggested command:"
    echo -e "\n$cmd\n"
    printf "Press Enter to run, Ctrl+C to abort..."

    read -r
    echo ""
    eval "$cmd"
    _push_to_shell_history "$cmd"
}
