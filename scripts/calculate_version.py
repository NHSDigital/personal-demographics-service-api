import git
import semver
import os.path
import itertools


SCRIPT_LOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_LOCATION, '..'))
REPO = git.Repo(REPO_ROOT)


def get_versionable_commits(repo):
    # Ignore merge commits
    commits = [c for c in repo.iter_commits() if len(c.parents) == 1]

    # If there is a marker to start versioning from, use it. Else, start from the first commit
    return list(itertools.takewhile(lambda c: '+startversioning' not in c.message, commits))


def commit_message_contains(s):
    def inner_f(commit):
        return s in commit.message
    return inner_f


is_major_inc = commit_message_contains('+major')
is_minor_inc = commit_message_contains('+minor')


def calculate_version(base_major=1, base_minor=0, base_revision=0, base_pre='alpha'):
    major = base_major
    minor = base_minor
    patch = base_revision

    # If there are any +major in commit messages, increment the counter
    commits = get_versionable_commits(REPO)
    major_incs = [c for c in commits if is_major_inc(c)]

    if major_incs:
        major += len(major_incs)
        minor = 0
        patch = 0


    # If there are any +minor in commit messages, increment the counter
    # We only care about commits after the last major increment
    commits = list(itertools.takewhile(lambda c: not is_major_inc(c), commits))
    minor_incs = [c for c in commits if is_minor_inc(c)]

    if minor_incs:
        minor += len(minor_incs)
        patch = 0

    # Now increment patch number for every commit since the last patch
    commits = list(itertools.takewhile(lambda c: not is_minor_inc(c), commits))
    patch = len(commits)

    return semver.VersionInfo(major, minor, patch, base_pre)


if __name__ == '__main__':
    print(calculate_version())
