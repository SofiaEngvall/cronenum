A script to enumerate scheduled tasks on a Linux system

The script goes through cron locations and is meant to be run both
as a user and an admin. For making sure nothing is run we don't know
about as an admin and to search for vulnerabilities when doing a
penetration test.

To do:
- Add more enumeration ways
- add a switch to inspect a certain directory -d making the script forego it's normal operation and just focus on the dir

Please report errors <3

Author: Sofia Engvall, FixIt42
Links: https://www.youtube.com/@FixIt42, https://www.twitch.tv/FixIt42
License: MIT
Repository: https://github.com/SofiaEngvall/cronenum
Version: 0.4

Usage:
    python cronenum.py
    python cronenum.py -f      Shows full files in cron directories, can be very long
    python cronenum.py -l [n]  Shows a maximum of n lines from all files in directories, default 5. Overrides -f
