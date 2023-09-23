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
License: MIT
Repository: https://github.com/SofiaEngvall/cronenum
Version: 0.3

Usage:
    python cronenum.py
    python cronenum.py -f   Shows full files in cron directories, can be very long
    python cronenum.py -l   Shows
"""

import os
import subprocess
import argparse

# ANSI escape codes for coloring
COLOR_RESET = "\033[0m"
COLOR_ERROR = COLOR_RED = "\033[91m"
COLOR_HEADER = COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_FILENAME = COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"
COLOR_CYAN = "\033[96m"
COLOR_LIGHT_GRAY = "\033[97m"


def find_users():
    """
    Get a list of all users on the system

    :return: List off all users
    """
    try:
        users = [line.split(':')[0] for line in open('/etc/passwd')]
        return users
    except Exception as e:
        print(f"{COLOR_ERROR}Error reading /etc/passwd: {e}{COLOR_RESET}\n")
        exit(1)


def print_user_cron_jobs(users):
    """
    Function to search and list user-level cron jobs

    :param users: List of users.
    """

    for user in users:
        print(f"{COLOR_MAGENTA}User: {user}{COLOR_RESET}")

        # Use the 'crontab' command to list the user's cron jobs
        try:
            cron_jobs = subprocess.check_output(
                ['crontab', '-l', '-u', user], stderr=subprocess.STDOUT, text=True)
            if cron_jobs:
                print(cron_jobs)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:  # No cron jobs for the user
                print("No cron jobs found for this user.\n")
            elif e.returncode == 126:  # Permission denied
                print(
                    f"{COLOR_ERROR}Permission denied to retrieve cron jobs for {user}.{COLOR_RESET}\n")
            else:
                print(
                    f"{COLOR_ERROR}Error retrieving cron jobs for {user}: {e.output}{COLOR_RESET}\n")
        except PermissionError as pe:
            print(f"{COLOR_ERROR}Permission denied to run 'crontab -l -u {user}'. Please run this script as an administrator (e.g., with sudo).{COLOR_RESET}\n")
        print(f"{COLOR_YELLOW}{separator1}{COLOR_RESET}\n")


def print_system_cron_jobs():
    """
    Function to search and list system-level cron jobs
    """
    system_cron_paths = [
        '/etc/cron.d/',
        '/etc/cron.daily/',
        '/etc/cron.hourly/',
        '/etc/cron.monthly/',
        '/etc/cron.weekly/',
        '/etc/crontab'
    ]

    for path in system_cron_paths:
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    print(f"{COLOR_MAGENTA}Cron Jobs in {path}:{COLOR_RESET}\n")
                    for filename in os.listdir(path):
                        filepath = os.path.join(path, filename)
                        if os.path.isfile(filepath):
                            try:
                                # Run the 'file' command on the file
                                result = subprocess.run(
                                    ['file', filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                                filetype = result.stdout.split(": ")[1]
                                print(
                                    f"{COLOR_FILENAME}File: {path}{filename}{COLOR_RESET} : {filetype}")
                            except Exception as e:
                                print(
                                    f"{COLOR_FILENAME}File: {path}{filename}{COLOR_RESET}\n")
                            try:
                                if show_lines > 0:
                                    with open(filepath, 'r') as cron_file:
                                        for i in range(show_lines):
                                            line = cron_file.readline()
                                            # Stop reading if we reach the end of the file
                                            if not line:
                                                break
                                            # Remove newline characters and print each line
                                            print(line.strip())
                                        if cron_file.readline():
                                            print("...")
                                        print(
                                            f"{COLOR_YELLOW}\n{separator1}{COLOR_RESET}\n")
                                elif show_files:
                                    with open(filepath, 'r') as cron_file:
                                        cron_contents = cron_file.read()
                                        print(cron_contents)
                                        print(
                                            f"{COLOR_YELLOW}{separator1}{COLOR_RESET}\n")
                            except Exception as e:
                                print(f"Error reading {filepath}: {e}\n")
                elif os.path.isfile(path):
                    try:
                        with open(path, 'r') as cron_file:
                            cron_contents = cron_file.read()
                            print(
                                f"{COLOR_MAGENTA}Cron Jobs in {path}:{COLOR_RESET}\n")
                            print(cron_contents)
                            print(f"{COLOR_YELLOW}{separator2}{COLOR_RESET}\n")
                    except Exception as e:
                        print(
                            f"{COLOR_ERROR}Error reading {path}: {e}{COLOR_RESET}\n")
        except PermissionError as pe:
            print(f"{COLOR_ERROR}Permission denied to access {path}. Please run this script as an administrator (e.g., with sudo).{COLOR_RESET}\n")


# Check that the script is run, not just imported
if __name__ == "__main__":

    # check os
    if os.name != 'posix':
        print("This script is intended for Linux.")
        exit(1)

    # parse arguments
    parser = argparse.ArgumentParser(
        description="A tool to enumerate cron jobs")
    parser.add_argument(
        "-f", "--files", help="Show full contents of the files in cron directories.", action="store_true")
    parser.add_argument(
        "-l", "--lines", help="The maximum number of lines to show per file. Overrides -f. Default 5.", type=int, nargs='?', const=5, default=-1)
    args = parser.parse_args()
    show_lines = args.lines
    show_files = args.files if show_lines < 1 else False

    # init separators according to tty width
    try:
        rows, columns = os.popen('stty size', 'r').read().split()
        separator1 = "-" * int(columns)
        separator2 = "=" * int(columns)
    except Exception:
        separator1 = "-" * 80
        separator2 = "=" * 80

    # get user list
    users = find_users()
    print("Listing all cron jobs\n")
    print(f"{COLOR_YELLOW}{separator2}{COLOR_RESET}\n")

    # find users cron jobs
    print(f"{COLOR_HEADER}User-Level Cron Jobs:{COLOR_RESET}\n")
    print_user_cron_jobs(users)

    # find system cron jobs
    print(f"{COLOR_HEADER}System-Level Cron Jobs:{COLOR_RESET}\n")
    print_system_cron_jobs()
