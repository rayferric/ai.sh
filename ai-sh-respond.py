import sys
import yaml
import os
import asyncio
import aiohttp
import json
from datetime import datetime


async def main():
    # read config
    config_path = os.path.join(os.path.dirname(__file__), "ai-sh-config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    api_key = config.get("openai_api_key")
    model = config.get("model")
    prompt = " ".join(sys.argv[1:])

    # get current time: "Monday, June 2, 2025, 5:32 PM"
    now = datetime.now().strftime("%A, %B %d, %Y, %-I:%M %p")

    # get username
    user = os.getenv("USER")

    # get cwd
    cwd_str = os.getcwd()

    # list files in cwd, sort by latest modification date, limit to 5
    files = sorted(
        (
            (f, os.path.getmtime(f))
            for f in os.listdir(os.getcwd())
            if not os.path.islink(f)
        ),
        key=lambda x: x[1],
        reverse=True,
    )[:5]
    file_list = "\n".join(
        [
            f"- {name} ({datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')})"
            for name, mtime in files
        ]
    )

    # read ai history
    history_path = os.path.join(os.path.dirname(__file__), ".ai_history")
    history_str = ""
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            history = f.read()
        # split by empty lines, remove empty entries
        history_entries = [
            entry.strip() for entry in history.split("\n\n") if entry.strip() != ""
        ]
        # take last 3 entries
        history_entries = history_entries[-3:]
        # stringify
        history_str = "\n".join(history_entries)
    if not history_str:
        history_str = "(no suggestions yet)"
    history_str = history_str.replace("\\n", "\\\\n")

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

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": True,
                },
            ) as resp:
                if resp.status == 401:
                    full_cmd = "echo 'OpenAI API key is not provided. Please edit \"ai.sh/ai-sh-config.yaml\".'"
                    print(full_cmd)
                    return

                full_cmd = ""
                async for line in resp.content:
                    if line.startswith(b"data: "):
                        data = line[len(b"data: ") :].strip()
                        if data == b"[DONE]":
                            break
                        data = json.loads(data)
                        text = data["choices"][0]["delta"].get("content", "")
                        full_cmd += text

                # output to bash
                print(full_cmd)

                # append to history with cwd
                if not os.path.exists(history_path):
                    with open(history_path, "w") as f:
                        f.write("")
                now_file_fmt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(history_path, "a") as f:
                    f.write(
                        f"\n- {now_file_fmt}, at {os.getcwd()}, prompt: '{prompt}'\n"
                    )
                    f.write(f"\t{full_cmd}\n")
        except Exception as e:
            print(f"Request failed: {e}", file=sys.stderr)


asyncio.run(main())
