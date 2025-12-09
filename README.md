**AI suggestions in your terminal**

![](showcase.gif)

All you can get with GitHub CLI / copilot, and more:

- AI gets filesystem context and conversation history
- suggestions are executed in parent shell and saved to history (press Enter)
- no clutter, no bullshit

= overall improved experience + trivial to modify shall you need more features.

### Requirements

- Python 3
- Bring your own API key!
  - OpenAI: https://platform.openai.com/api-keys
  - OpenRouter: https://openrouter.ai/keys
- Supported shells: `bash`, `zsh`

```sh
git clone https://github.com/rayferric/ai.sh.git
echo "source $(pwd)/ai.sh/ai.sh" >> ~/.${SHELL##*/}rc
source ~/.${SHELL##*/}rc
nano ./ai.sh/ai-sh-config.json # configure provider, API key, and model
```

### First Use Example

```
ai get current time in tokyo
```

### Safety Disclaimer! The provider sees:

- your request
- system username
- full current working directory path
- names of 5 last modified files in cwd
