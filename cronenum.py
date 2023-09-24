#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A script to enumerate scheduled tasks

The script goes through cron locations and is meant to be run both
as a user and an admin. For making sure nothing is run we don't know
about as an admin and to search for vulnerabilities when doing a
penetration test.

To do:
- Add more enumeration ways

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
"""

import os
import argparse
import subprocess

# ANSI escape codes
ANSI_RESET = "\033[0m"
ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_BLUE = "\033[94m"
ANSI_MAGENTA = "\033[95m"
ANSI_CYAN = "\033[96m"
ANSI_LIGHT_GRAY = "\033[97m"

ANSI_BOLD = "\033[1m"
ANSI_BOLD_OFF = "\033[22m"
ANSI_ITALIC = "\033[3m"
ANSI_ITALIC_OFF = "\033[23m"
ANSI_UNDERLINE = "\033[4m"
ANSI_UNDERLINE_OFF = "\033[24m"
ANSI_BLINK = "\033[5m"
ANSI_BLINK_OFF = "\033[25m"
ANSI_INVERT_COLORS = "\033[7m"
ANSI_INVERT_COLORS_OFF = "\033[27m"

# Output formatting (Doesn't work on all terminals)
RESET = ANSI_RESET
ERROR = ANSI_RED + ANSI_BLINK
HEADER1 = ANSI_GREEN + ANSI_BOLD + ANSI_UNDERLINE
HEADER2 = ANSI_MAGENTA + ANSI_UNDERLINE
FILENAME = ANSI_YELLOW
FILETYPE = ANSI_ITALIC
SEPARATOR = ANSI_CYAN

# System cron paths to search, directories and files
system_cron_paths = [
    '/etc/cron.d/',
    '/etc/cron.daily/',
    '/etc/cron.hourly/',
    '/etc/cron.monthly/',
    '/etc/cron.weekly/',
    '/etc/crontab'
]


def separator(char):
    """
    Prints a separator line across the screen

    :param char: character used for the line
    """
    print(f"\n{SEPARATOR}{char * int(cols)}{RESET}\n")


def find_users():
    """
    Get a list of all users on the system by reading /etc/passwd

    :return: List off all users
    """
    try:
        users = [line.split(':')[0] for line in open('/etc/passwd')]
        return users
    except Exception as e:
        print(f"{ERROR}Error reading /etc/passwd: {e}{RESET}\n")
        return []


def print_user_cron_jobs(users):
    """
    Function to search and list user-level cron jobs using crontab

    :param users: List of users.
    """
    for user in users:
        try:
            cron_jobs = subprocess.check_output(
                ['crontab', '-l', '-u', user], stderr=subprocess.STDOUT, text=True)
            if cron_jobs:
                separator("-")
                print(f"{HEADER2}User: {user}{RESET}")
                print(cron_jobs)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:  # No cron jobs
                pass
            elif e.returncode == 126:  # Permission denied
                print(
                    f"{ERROR}Permission denied to retrieve cron jobs for {user}.{RESET}")
            else:
                print(
                    f"{ERROR}Error retrieving cron jobs for {user}: {e.output}{RESET}")
        except PermissionError as pe:
            print(
                f"{ERROR}Permission denied to run 'crontab -l -u {user}'. Please run this script with sudo.{RESET}")


def print_with_filetype(filepath):
    """
    Prints the filename including path and it's filetype

    Param filepath: the filename including path
    """
    try:
        result = subprocess.run(['file', filepath], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, check=True)
        filetype = result.stdout.split(": ")[1].strip()
        print(
            f"{FILENAME}File: {filepath}{RESET} ({filetype})\n")
    except Exception as e:
        print(
            f"{FILENAME}File: {filepath}{RESET}")


def print_system_cron_jobs():
    """
    Function to list system-level cron jobs
    """

    for path in system_cron_paths:
        try:
            if os.path.exists(path):
                separator("=")
                if os.path.isdir(path):
                    print(f"{HEADER2}Cron Jobs in {path}:{RESET}")
                    for filename in os.listdir(path):
                        filepath = os.path.join(path, filename)
                        if os.path.isfile(filepath):
                            separator("-")
                            print_with_filetype(filepath)
                            try:
                                if show_lines > 0:
                                    with open(filepath, 'r') as cron_file:
                                        for i in range(show_lines):
                                            line = cron_file.readline()
                                            if not line:  # EOF
                                                break
                                            print(line.strip())
                                        if cron_file.readline():
                                            print("...")
                                elif show_files:
                                    with open(filepath, 'r') as cron_file:
                                        print(cron_file.read())
                            except Exception as e:
                                print(f"Error reading {filepath}: {e}")
                elif os.path.isfile(path):
                    try:
                        with open(path, 'r') as cron_file:
                            print(
                                f"{HEADER2}Cron Jobs in {path}:{RESET}\n")
                            print(cron_file.read())
                    except Exception as e:
                        print(
                            f"{ERROR}Error reading {path}: {e}{RESET}")
        except PermissionError as pe:
            print(
                f"{ERROR}Permission denied to access {path}. Please run this script with sudo.{RESET}")


# Check that the script is run, not just imported
if __name__ == "__main__":

    # check os
    if os.name != 'posix':
        print("This script is intended for Linux.")
        exit(1)

    # parse args
    parser = argparse.ArgumentParser(
        description="A tool to enumerate cron jobs")
    parser.add_argument(
        "-f", "--files", help="Show full contents of the files in cron directories.", action="store_true")
    parser.add_argument(
        "-l", "--lines", help="The maximum number of lines to show per file. Overrides -f. Default 5.", type=int, nargs='?', const=5, default=-1)
    args = parser.parse_args()

    show_lines = args.lines
    show_files = args.files
    if args.lines > -1 and args.files:  # both -f and -l, l overrides f
        show_files = False
    elif args.lines == -1 and not args.files:  # no arguments, set to 5 as default, looks the best :D
        show_lines = 5

    # get tty size
    try:
        rows, cols = os.popen('stty size', 'r').read().split()
    except Exception:
        rows = 30
        cols = 70

    # get user list
    users = find_users()
    print("\nListing all cron jobs        (-h for help)")
    separator("=")

    # find users cron jobs
    print(f"{HEADER1}User-Level Cron Jobs:{RESET}")
    print_user_cron_jobs(users)
    separator("=")

    # find system cron jobs
    print(f"{HEADER1}System-Level Cron Jobs:{RESET}")
    print_system_cron_jobs()
    separator("=")
