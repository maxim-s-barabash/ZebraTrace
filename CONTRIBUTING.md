# Contributing to ZebraTrace

Thanks for your interest in this project. General information regarding source code management, builds, coding standards, and more can be found here:

We track bugs in the corresponding GitHub Issue trackers.

Source Repositories:

You can use the code from these repositories to experiment, test, build, create patches, issue pull requests, etc.

- ZebraTrace - Project repository hosted on GitHub.  
  Browse Repository https://github.com/maxim-s-barabash/ZebraTrace

- ZebraTrace.wiki - Project help documentation and examples.  
  Browse Repository https://github.com/maxim-s-barabash/ZebraTrace/wiki

## Commits

ZebraTrace uses Conventional Changelog, which structure Git commit messages in a way that allows automatic generation of changelogs.
Commit messages must be structured as follows:

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

- `<type>`: A noun specifying the type of change, followed by a colon and a space. The types allowed are:
  - `feat`: A new feature
  - `fix`: A bug fix
  - `refactor`: Code change that neither fixes a bug or adds a feature (not relevant for end user)
  - `perf`: Change improves performance
  - `style`: Change does not affect the code (e.g., formatting, whitespaces)
  - `test`: Adding missing tests
  - `chore`: Change of build process or auxiliary tools
  - `docs`: Documentation only changes
- `<scope>`: Optional. A term of free choice specifying the place of the commit change, enclosed in parentheses. Examples:
  - `feat(binding-coap): ...`
  - `fix(cli): ...`
  - `docs: ...` (no scope, as it is optional)
- `<subject>`: A succinct description of the change, e.g., `add support for magic`
  - Use the imperative, present tense: "add", not "added" nor "adds"
  - Do not capitalize first letter: "add", not "Add"
  - No dot (.) at the end
- `<body>`: Optional. Can include the motivation for the change and contrast this with previous behavior.
  - Just as in the subject, use the imperative, present tense: "change" not "changed" nor "changes"
- `<footer>`: Optional. Can be used to automatically close GitHub Issues and to document breaking changes.
  - The prefix `BREAKING CHANGE: ` idicates API breakage (corresponding to a major version change) and everything after is a description what changed and what needs to be done to migrate
  - GitHub Issue controls such as `Fixes #123` or `Closes #4711` must come before a potential `BREAKING CHANGE: `.

Examples:

```
docs: improve how to contribute
```

```
feat(core): add support for magic

Closes #110
```

```
feat(core): add support for magic

Simplify the API by reducing the number of functions.

Closes #110
BREAKING CHANGE: Change all calls to the API to the new `do()` function.
```

## Pull Requests and Feature Branches

- Do not merge with master while developing a new feature or providing a fix in a new branch
- Do a rebase if updates in the master such as a fix are required:

```
git checkout master && git pull && git checkout - && git rebase master
```

- Pull Requests are merged using rebase
