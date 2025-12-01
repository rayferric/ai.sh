**AI suggestions in your terminal**

![](showcase.gif)

All you can get with GitHub CLI / copilot, and more:

- AI gets filesystem context and conversation history
- suggestions are executed in parent shell and saved to history (press Enter)
- no clutter, no bullshit

= overall improved experience + trivial to modify shall you need more features.

### Requirements:

- Python 3
- Bring your own OpenAI API key!
  https://platform.openai.com/api-keys
- Supported shells: `bash`, `zsh`, `fish`

### Safety Disclaimer! OpenAI sees:

- your request
- system username
- full current working directory path
- names of 5 last modified files in cwd
