# CMSC 14200 - Project

Final project for UChicago class CMSC 14200. Project members: Aidan Parker, Dylan Hu, Kevin Gugelmann, and Junfei Sun.

## Requirements

This project targets Python versions 3.8 and above.

## Dev workflow

### Planning a new feature / bug fix / documentation
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

### Setting up local environment to work on an issue
> By this point, you should already have a development branch for your issue
1. Open your terminal
2. Navigate to your git directory (probably `project-dylanhu-gugelmann-aidanparker-junfeisun/`)
4. Update git locally so it's aware of any local and remote changes
    ```
    git fetch origin
    ```
5. Ensure you will have no conflicts
    ```
    git status .
    ```
    > If you have any local changes, refer to the section "**Existing changes on the wrong branch?**"
    
    > Otherwise, continue:
7. Switch to your issue's development branch (e.g. `gui/king-piece-display`)
    ```
    git checkout gui/king-piece-display
    ```

### Existing changes on the wrong branch?
