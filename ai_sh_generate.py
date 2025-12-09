import sys
import os
import asyncio
import json
from datetime import datetime
from ai_sh_api import query_llm

CTX_LISTDIR_LIMIT = 5
CTX_AI_HISTORY_LIMIT = 10


async def main():
    # read config
    config_path = os.path.join(os.path.dirname(__file__), "ai-sh-config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    prompt = " ".join(sys.argv[1:])

    # extract context for the agent:
    # - current time: "Monday, June 2, 2025, 5:32 PM"
    now = datetime.now().strftime("%A, %B %d, %Y, %-I:%M %p")
    # - system username
    user = os.getenv("USER")
    # - cwd
    cwd_str = os.getcwd()
    # - files in cwd, sort by latest modification date, limit to CTX_LISTDIR_LIMIT
    files = sorted(
        (
            (f, os.path.getmtime(f))
            for f in os.listdir(os.getcwd())
            if not os.path.islink(f)
        ),
        key=lambda x: x[1],
        reverse=True,
    )[:CTX_LISTDIR_LIMIT]
    file_list = "\n".join(
        [
            f"- {name} ({datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')})"
            for name, mtime in files
        ]
    )
    # - last suggestions from .ai_history
    history_path = os.path.join(os.path.dirname(__file__), ".ai_history")
    history_str = ""
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            history = f.read()
        # split by empty lines, remove empty entries
        history_entries = [
            entry.strip() for entry in history.split("\n\n") if entry.strip() != ""
        ]
        # take last CTX_AI_HISTORY_LIMIT entries
        history_entries = history_entries[-CTX_AI_HISTORY_LIMIT:]
        history_str = "\n".join(history_entries)
    if not history_str:
        history_str = "(no suggestions yet)"
    history_str = history_str.replace("\\n", "\\\\n")

    # assemble system prompt with the context
    system_prompt = f"""
[{now}]

Username: {user}
Current directory: {cwd_str}

Latest in current directory:
{file_list}

Your previous suggestions:
{history_str}

Output only a Linux shell command to achieve what the user asks for. Never answer directly.
""".strip()

    # query LLM with streaming
    try:
        full_cmd = await query_llm(
            system_prompt=system_prompt,
            user_prompt=prompt,
            provider=config.get("provider"),
            api_key=config.get("api_key"),
            model=config.get("model"),
        )

        # print resulting command (read back by ai.sh bash script)
        print(full_cmd)

        # append a new entry to .ai_history
        history_content = ""
        if os.path.exists(history_path):
            with open(history_path, "r") as f:
                history_content = f.read().strip()
        now_file_fmt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_content += (
            f"\n\n- {now_file_fmt}, at {os.getcwd()}, prompt: '{prompt}'\n\t{full_cmd}"
        )
        with open(history_path, "w") as f:
            f.write(history_content.strip())
    except PermissionError as e:
        full_cmd = f"echo '{str(e)}'"
        print(full_cmd)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)


asyncio.run(main())
