import aiohttp
import json
import os


async def query_llm(
    system_prompt: str,
    user_prompt: str,
    provider: str,
    api_key: str,
    model: str,
    stream_callback=None,
) -> str:
    if provider == "openai":
        endpoint = "https://api.openai.com/v1/chat/completions"
    elif provider == "openrouter":
        endpoint = "https://openrouter.ai/api/v1/chat/completions"
    else:
        raise ValueError(f"Unknown provider: {provider}")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": True,
                # disable reasoning for OpenRouter models
                **(
                    {"reasoning": {"enabled": False}}
                    if provider == "openrouter"
                    else {}
                ),
            },
        ) as resp:
            if resp.status == 401:
                config_path = os.path.join(
                    os.path.dirname(__file__), "ai-sh-config.json"
                )
                raise PermissionError(
                    f"API key is not provided or invalid. "
                    f'Please edit "{config_path}".'
                )

            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(
                    f"API request failed with status {resp.status}: {error_text}"
                )

            full_response = ""
            async for line in resp.content:
                if line.startswith(b"data: "):
                    data = line[len(b"data: ") :].strip()
                    if data == b"[DONE]":
                        break
                    try:
                        data = json.loads(data)
                        text = data["choices"][0]["delta"].get("content", "")
                        full_response += text
                        if stream_callback:
                            await stream_callback(text)
                    except (json.JSONDecodeError, KeyError):
                        continue

            return full_response
