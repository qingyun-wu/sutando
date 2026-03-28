#!/usr/bin/env python3
"""
Sutando contacts reader — search macOS Contacts via AppleScript.

Usage:
  python3 src/contacts.py search "Bob"         # search by name
  python3 src/contacts.py search "bob@x.com"   # search by email
  python3 src/contacts.py all                   # list all (first 50)

Output: name, email, phone for matching contacts.
"""

import json
import re
import subprocess
import sys


def search_contacts(query: str) -> list[dict]:
    # Ensure Contacts.app is running (AppleScript fails with -600 if not)
    import time
    subprocess.run(["open", "-ga", "Contacts"], capture_output=True, timeout=5)
    time.sleep(1)
    # Search by name or email
    script = f"""
tell application "Contacts"
    set output to ""
    set results to (every person whose name contains "{query}")
    if (count of results) > 20 then set results to items 1 thru 20 of results
    repeat with p in results
        set pName to name of p
        set pEmails to ""
        repeat with e in emails of p
            set pEmails to pEmails & (value of e) & ","
        end repeat
        set pPhones to ""
        repeat with ph in phones of p
            set pPhones to pPhones & (value of ph) & ","
        end repeat
        set output to output & pName & "|||" & pEmails & "|||" & pPhones & "\\n"
    end repeat
    return output
end tell
"""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return [{"error": result.stderr.strip()}]

    contacts = []
    seen = set()
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split("|||")
        if len(parts) < 2:
            continue
        name = parts[0].strip()
        if name in seen:
            continue
        seen.add(name)
        emails = [e.strip() for e in parts[1].split(",") if e.strip()]
        phones = [p.strip() for p in parts[2].split(",") if p.strip()] if len(parts) > 2 else []
        contacts.append({"name": name, "emails": emails, "phones": phones})
    return contacts


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 src/contacts.py search 'name or email'")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "search" and len(sys.argv) > 2:
        query = sys.argv[2]
        results = search_contacts(query)
        if not results:
            print(f"No contacts matching '{query}'")
            return
        if "error" in results[0]:
            print(f"Error: {results[0]['error']}")
            return
        for c in results:
            print(f"  {c['name']}")
            for e in c["emails"]:
                print(f"    email: {e}")
            for p in c["phones"]:
                print(f"    phone: {p}")
    elif cmd == "all":
        results = search_contacts("")
        if not results:
            print("No contacts.")
            return
        print(json.dumps(results, indent=2))
    else:
        print("Usage: python3 src/contacts.py search 'name'")
        sys.exit(1)


if __name__ == "__main__":
    main()
