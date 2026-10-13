#!/usr/bin/env bash
# Usage: ./publish.sh <github-username> [repo-name]
# Needs the GitHub CLI logged in (gh auth login). Creates a PUBLIC repo and pushes.
set -euo pipefail
USER_NAME="${1:?usage: ./publish.sh <github-username> [repo-name]}"
REPO="${2:-crypto-kg-vault}"
git branch -M main
gh repo create "$USER_NAME/$REPO" --public --source=. --remote=origin --push \
  --description "Obsidian knowledge-graph vault for Ethereum and L2 DeFi research (seed snapshot 2026-10-13)"
echo "https://github.com/$USER_NAME/$REPO"
echo "Zip for members: https://github.com/$USER_NAME/$REPO/archive/refs/heads/main.zip"
