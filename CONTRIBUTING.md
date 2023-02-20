# Contributing to Checkers Game

## Development environment and code styling
We strongly recommend setting up a [Python virtual environment](README.md#setting-up-and-requirements) to prevent dependency conflicts.

### Code Style
The code style follows the PEP8 style guide. We recommend using a linter and autoformatter, such as flake8 and autopep8.

For docstrings we are following the Google style Python docstrings. See [examples](https://gist.github.com/redlotus/3bc387c2591e3e908c9b63b97b11d24e).

## Planning a new feature / bug fix / documentation
1. On GitHub, go to the Issues tab
2. Click on "New issue"
3. Title what you plan to work on – **Be precise**
4. In the comment box, outline any expected outcomes and/or implementation details – bullet points are generally best
5. Under 'Assignees', assign yourself
6. Under 'Labels':
    1. Select the type of issue (e.g. `enhancement` for a new feature)
    2. Select the component you're working on (e.g. `comp: gui` for GUI)
7. Click on "Submit new issue"
8. Create a development branch in the format "\<component>/\<issue-title>"
    1. For component, choose from: `logic`/`gui`/`tui`/`bot`
    2. For issue title, write in snake case and ideally limit to 25 char (e.g. "Display king pieces differently from regular pieces" -> "gui/king-piece-display"

## Setting up local environment to work on an issue
> By this point, you should already have a [development branch](#planning-a-new-feature--bug-fix--documentation) for your issue

1. Open your terminal
2. Navigate to your git directory (probably `project-dylanhu-gugelmann-aidanparker-junfeisun/`)
3. Update git locally so it's aware of any local and remote changes
    ```
    git fetch origin
    ```
4. Ensure you will have no conflicts (skip this step if you know local is 
   clean)
    ```
    git status .
    ```
    > If you have any local changes, refer to the section "[Existing changes on the wrong branch?](#existing-changes-on-the-wrong-branch)"

5. Switch to your issue's development branch (e.g. `gui/king-piece-display`)
    ```
    git checkout gui/king-piece-display
    ```

6. Update your development branch with the main branch
   ```
   git fetch
   git rebase main
   ```
   > Now you're ready to start working on your issue!

## Existing changes on the wrong branch?
1. Open your terminal
2. Navigate to your git directory (probably `project-dylanhu-gugelmann-aidanparker-junfeisun/`)
3. Stash your changes – they'll disappear from text editor, but aren't lost!
    ```
    git stash
    ```
4. Switch to the correct branch

    > If you're trying to switch to a development branch for an issue, refer to the section "[Setting up local environment to work on an issue](#setting-up-local-environment-to-work-on-an-issue)"

5. Pop your stashed changes – they'll reappear in your text editor
    ```
    git stash pop
    ```
    > Now you're ready to continue working on your changes, or commit them if ready – but in the correct branch

## Merging your work into the main branch
> By this point, you should have committed and pushed all your changes **on your development branch**

1. Make a pull request
2. _Optional:_ request code review, and wait for approval
3. Select the dropdown of the green button, and choose "Squash and merge"
4. Click on the green button that now says "Squash and merge"
5. Again, click on the green button (**don't change any of the text**) – this completes the squash and merge
6. _Only if you're done with the issue_: delete the development branch
7. Locally, switch to another branch to continue working
    
    > If you're trying to switch to another development branch for an issue, 
    > refer to the section "[Setting up local environment to work on an issue](#setting-up-local-environment-to-work-on-an-issue)"
