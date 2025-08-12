#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Get the local Git user name and email
AUTHOR_NAME=$(git config user.name)
AUTHOR_EMAIL=$(git config user.email)

# Check if the values were retrieved successfully
if [ -z "$AUTHOR_NAME" ] || [ -z "$AUTHOR_EMAIL" ]; then
  echo "Error: Git user.name and/or user.email not configured."
  exit 1
fi

# Export the variables so commits have proper identity
export GIT_AUTHOR_NAME="$AUTHOR_NAME"
export GIT_AUTHOR_EMAIL="$AUTHOR_EMAIL"
export GIT_COMMITTER_NAME="$AUTHOR_NAME"
export GIT_COMMITTER_EMAIL="$AUTHOR_EMAIL"

echo "Setting Git author to: $GIT_AUTHOR_NAME <$GIT_AUTHOR_EMAIL>"

# Ask for confirmation
read -p "Are you sure you want to release? (y/n): " confirm
if [ "$confirm" != "y" ]; then
  echo "Release cancelled."
  exit 1
fi

# Run python-semantic-release
semantic-release version
