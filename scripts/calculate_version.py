#!/usr/bin/env python

"""
calculate_versions.py

A script that calculates a semver-compliant version string from a git
repository's commit messages, using commands embedded in commit messages.

Commands can be included in commit messages like '+major APM-123 Do thing'

Commands:
    +major                 Increment the major version
    +minor                 Increment the minor version
    +setstatus <status>    Set the prerelease status to <status>
    +clearstatus           Clear the prerelease status
    +startversioning       Reset version to v1.0.0-alpha
"""

import os.path
import itertools
import git
import semver
from enum import Enum


SCRIPT_LOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_LOCATION, ".."))
REPO = git.Repo(REPO_ROOT)


class CommitFlag(Enum):
    """
    A list of valid commit flags that can be used for modifying the
    semver-compliant version tag.
    """
    START_VERSIONING = "+startversioning"
    INCREMENT_MAJOR = "+major"
    INCREMENT_MINOR = "+minor"
    SET_PRE_REL_STATUS = "+setstatus"
    CLEAR_PRE_REL_STATUS = "+clearstatus"


def get_versionable_commits(repo):
    """Gets all the versionable commits for a repository"""
    # Ignore merge commits
    commits = [c for c in repo.iter_commits() if len(c.parents) == 1]

    # If there is a marker to start versioning from, use it. Else, start from the first commit
    return list(
        itertools.takewhile(lambda c: CommitFlag.START_VERSIONING.value not in c.message, commits)
    )


def is_status_set_command(commit):
    """Returns true if commit.message is a pre-release status setting command"""
    return (CommitFlag.SET_PRE_REL_STATUS.value in commit.message) or (
        CommitFlag.CLEAR_PRE_REL_STATUS.value in commit.message)


def is_major_inc(commit):
    """Returns true if commit.message contains a major inc command"""
    return CommitFlag.INCREMENT_MAJOR.value in commit.message


def is_minor_inc(commit):
    """Returns true if commit.message contains a minor inc command"""
    return CommitFlag.INCREMENT_MINOR.value in commit.message


def without_empty(commits):
    """Takes a list of commits and returns a list without empty commits"""
    pairs = zip(commits, commits[1:])

    for fst, snd in pairs:
        if fst.tree != snd.tree:
            # This means 'fst' isn't empty
            yield fst

    # Have to remember to yield the last one
    if commits:
        yield commits[-1]


def calculate_version(base_major=1, base_minor=0, base_pre="alpha"):
    """Calculates a semver based on commit history and special flags in commit messages"""
    major = base_major
    minor = base_minor
    pre = base_pre

    commits = get_versionable_commits(REPO)

    # Figure out what the current 'status' (prerelease) is
    status_sets = [c for c in commits if is_status_set_command(c)]

    if status_sets:
        most_recent_message = status_sets[0].message.strip()

        if most_recent_message.startswith(f"{CommitFlag.SET_PRE_REL_STATUS.value} "):
            pre = most_recent_message.split(" ")[
                1
            ]  # Take the first string after the command

        if most_recent_message == CommitFlag.CLEAR_PRE_REL_STATUS.value:
            pre = None

    # If there are any +major in commit messages, increment the counter
    major_incs = [c for c in commits if is_major_inc(c)]

    if major_incs:
        major += len(major_incs)
        minor = 0

    # If there are any +minor in commit messages, increment the counter
    # We only care about commits after the last major increment
    commits = list(itertools.takewhile(lambda c: not is_major_inc(c), commits))
    minor_incs = [c for c in commits if is_minor_inc(c)]

    if minor_incs:
        minor += len(minor_incs)

    # Now increment patch number for every commit since the last patch
    commits = list(itertools.takewhile(lambda c: not is_minor_inc(c), commits))
    commits = list(without_empty(commits))
    patch = len(commits)

    return "v" + str(semver.VersionInfo(major, minor, patch, pre))


if __name__ == "__main__":
    print(calculate_version())
