# LetsGo configuration example

Create `~/.letsgo/config` to customize the LetsGo prompt and colors. Each line
uses the format `name=value`. Values may include escape sequences like
`\033` for ANSI colors.

```
prompt=">> "
green="\033[32m"
red="\033[31m"
cyan="\033[36m"
reset="\033[0m"
```

Parameters:

- `prompt` – text displayed for the input prompt.
- `green`, `red`, `cyan` – ANSI color codes used for status messages, errors
  and the prompt.
- `reset` – code to reset terminal colors.
