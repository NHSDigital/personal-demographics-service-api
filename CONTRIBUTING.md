# Contribution Guidelines

## Raising an Issue
If you raise an issue against this repository, please include as much information as possible to reproduce any bugs,
or specific locations in the case of content errors.

## Contributing code
To contribute code, please fork the repository and raise a pull request.

Ideally pull requests should be fairly granular and aim to solve one problem each. It would also be helpful if they
linked to an issue. If the maintainers cannot understand why a pull request was raised, it will be rejected,
so please explain why the changes need to be made (unless it is self-evident).

### Merge responsibility
* It is the responsibility of the reviewer to merge branches they have approved.
* It is the responsibility of the author of the merge to ensure their merge is in a mergeable state.
* It is the responsibility of the maintainers to ensure the merge process is unambiguous and automated where possible.

### Branch naming
Branch names should be of the format:

`apm-nnn-short-issue-description`

Multiple branches are permitted for the same ticket.

### Commit messages
Commit messages should be formatted as follows:
```
APM-NNN Summary of changes

Longer description of changes if explaining rationale is necessary,
limited to 80 columns and spanning as many lines as you need.
```

### Changelog
Every pull request must include a change to the changelog.

Add changes to the top of the current date. If the date is old, the reviewer should update the changelog to be correct before merging.
