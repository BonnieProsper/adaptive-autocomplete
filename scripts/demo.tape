# Requires VHS: https://github.com/charmbracelet/vhs
#
# Usage:
#   brew install vhs             # macOS
#   sudo snap install vhs        # Linux
#   vhs scripts/demo.tape        # writes docs/demo.gif
#
# The resulting GIF goes in docs/ and is embedded in the README via:
#   ![demo](docs/demo.gif)
#
# Tweak Width/Height and Sleep values if your terminal renders differently.

Output docs/demo.gif

Require echo

Set Shell bash
Set FontSize 14
Set Width 900
Set Height 580
Set Theme "Dracula"
Set Padding 16
Set TypingSpeed 40ms

# Boot: activate venv so `aac` is on PATH
Hide
Type "source .venv/bin/activate"
Enter
Sleep 500ms
Show

# 1. Suggest
Type "aac suggest prog --limit 5"
Sleep 500ms
Enter
Sleep 2500ms

# 2. Typo recovery
Type "aac suggest programing --limit 5"
Sleep 500ms
Enter
Sleep 3000ms

# 3. Learn
Type "aac record prog programming"
Sleep 500ms
Enter
Sleep 800ms

Type "aac record prog programming"
Sleep 300ms
Enter
Sleep 800ms

Type "aac record prog programming"
Sleep 300ms
Enter
Sleep 800ms

# 4. Suggest again - programming now at top
Type "aac suggest prog --limit 5"
Sleep 500ms
Enter
Sleep 2000ms

# 5. Explain
Type "aac explain prog --limit 3"
Sleep 500ms
Enter
Sleep 2500ms

# 6. Compare presets
Type "aac compare programing --presets stateless production --limit 4"
Sleep 500ms
Enter
Sleep 5000ms

Sleep 1500ms
