#!/usr/bin/env python3
"""Clean copied signal messages for pasting into Notion

Currently only works on Mac

What it does:
- Removes the pesky time units from copied messages.
- Reformats the copied text so it pastes properly into Notion (rather than single
newlines and bullets being ignored).

"""
import re
import subprocess


MONTHS = {"Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}
DAYS_OF_WEEK = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}


def read_from_clipboard():
    return subprocess.check_output(
        'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')


def write_to_clipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))


def is_date(line):
    """
      >>> is_date("Dec 13, 2020 12:55pm")
      True
      >>> is_date("Wed 9:55pm")
      True
      >>> is_date("40m")
      True
      >>> is_date("14h")
      True
      >>> is_date("now")
      True
      >>> is_date("5m")
      True
      >>> is_date("2h")
      True
      >>> is_date("now I went to the bathroom")
      False
      >>> is_date("lol")
      False
      >>> is_date("Dec 12")
      False
      >>> is_date("Tue")
      False

    """
    if len(line) > 20:
        # Longest line possible is "Dec 13, 2020 12:55pm"
        return False

    if line[:3] in MONTHS:
        # Match on " 13, 2020 12:55pm"
        return re.match(r"^ [1-3]?\d, \d{4} [0-1]?\d:[0-5]\d[ap]m$", line[3:]) is not None
    if line[:3] in DAYS_OF_WEEK:
        # Match on " 12:55pm"
        return re.match(r"^ [0-1]?\d:[0-5]\d[ap]m$", line[3:]) is not None

    if len(line) > 3:
        # The only thing left at this point is "40m", "12h", "now"
        return False

    # Match on "40m"
    if re.match(r"[1-5]?\dm", line):
        return True
    # Match on "12h"
    if re.match(r"1?\dh", line):
        return True
    # Match on "now"
    if line == "now":
        return True

    return False


def clean_signal(msg):
    cleaned_lines = []
    last_was_date = True
    for line in msg.split('\n'):
        if is_date(line) and not last_was_date:
            last_was_date = True
            cleaned_lines.append("")
        else:
            cleaned_lines.append(line)
            last_was_date = False
    return "\n".join(cleaned_lines)
        

if __name__ == "__main__":
    msg = read_from_clipboard()
    text = clean_signal(msg)
    write_to_clipboard(text)
