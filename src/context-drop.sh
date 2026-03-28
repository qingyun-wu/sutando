#!/bin/bash
# Sutando context drop — triggered by macOS hotkey via Automator Quick Action.
#
# What it does:
#   1. Gets currently selected text (via clipboard)
#   2. Writes it to context-drop.txt in the workspace
#   3. The cron loop picks it up next pass and processes it
#
# Setup:
#   1. Open Automator → New → Quick Action
#   2. Set "Workflow receives" = "no input" in "any application"
#   3. Add action: "Run Shell Script" → point to this file
#   4. Save as "Sutando: Drop Context"
#   5. System Settings → Keyboard → Keyboard Shortcuts → Services
#      → assign a shortcut (e.g. ⌃⌥Space)
#
# Alternatively, bind via System Settings → Keyboard Shortcuts → App Shortcuts.

WORKSPACE="$(cd "$(dirname "$0")/.." && pwd)"
DROP_FILE="$WORKSPACE/context-drop.txt"
LOG_FILE="$WORKSPACE/src/context-drop.log"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Copy current selection to clipboard (cmd+c), then read clipboard
# Uses osascript to send Cmd+C to the frontmost app
# Save current clipboard to restore later
OLD_CLIPBOARD=$(pbpaste 2>/dev/null)

# Try multiple methods to get selected text:

# Method 1: Accessibility API (works in apps that block simulated keystrokes like Discord)
SELECTED=$(osascript -e '
tell application "System Events"
  try
    set frontApp to name of first application process whose frontmost is true
    tell process frontApp
      set selectedText to value of attribute "AXSelectedText" of (first text area whose focused is true)
      return selectedText
    end tell
  on error
    return ""
  end try
end tell
' 2>/dev/null)

# Method 2: Simulated Cmd+C (fallback for apps where AX doesn't work)
if [ -z "$SELECTED" ]; then
  osascript -e 'tell application "System Events" to keystroke "c" using command down'
  sleep 0.3
  SELECTED=$(pbpaste 2>/dev/null)
  # If clipboard didn't change, nothing was copied
  if [ "$SELECTED" = "$OLD_CLIPBOARD" ]; then
    SELECTED=""
  fi
fi

if [ -z "$SELECTED" ]; then
  echo "[$TIMESTAMP] Nothing selected" >> "$LOG_FILE"
  osascript -e 'display notification "Nothing selected — select text first" with title "Sutando"'
  exit 0
fi

# Write to drop file with timestamp
cat > "$DROP_FILE" << EOF
timestamp: $TIMESTAMP
---
$SELECTED
EOF

echo "[$TIMESTAMP] Dropped: ${#SELECTED} chars" >> "$LOG_FILE"

# Notify user
osascript -e "display notification \"${#SELECTED} chars dropped — processing next pass\" with title \"Sutando\""
