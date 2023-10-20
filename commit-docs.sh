#!/bin/bash

TARGET_FOLDER="target"
BRANCH="docs_new"

if [ -z "$(git status --untracked-files=no --porcelain . -- ':!target')" ]; then 
    # Working directory clean excluding untracked files
    # Commit the changes in the target folder to the _docs branch
    rm -rf /tmp/target
    echo "Deleted old tmp folder"
    cp -R target /tmp
    echo "Copied target to tmp"
    rm -rf target
    git checkout $BRANCH  # Switch to the docs branch
    echo "Switched to $BRANCH"
    rm -rf target
    cp -R /tmp/target .
    git add "$TARGET_FOLDER"  # Stage changes in the target folder
    git commit -m "Updated release"  # Commit changes
    git push origin $BRANCH  # Push changes to the _docs branch on the remote repository
    echo "Pushed"

    # Return to the previous branch (optional)
    git checkout -
    cp -R /tmp/target .
    echo "Changes in '$TARGET_FOLDER' have been committed to the $BRANCH branch."
else 
  echo "Uncommitted changes in code outside of the target directory, please commit or stash before running this script"
fi