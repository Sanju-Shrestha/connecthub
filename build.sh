#!/usr/bin/env bash
# build.sh – Render build script
# Runs on every deployment after code is pulled from GitHub

# Exit on any error – deployment fails if any command fails
set -o errexit

# Install all Python dependencies
pip install -r requirements.txt

# Collect all static files into staticfiles/
# --no-input: do not ask for confirmation
# --clear: remove old staticfiles first (ensures clean state)
python manage.py collectstatic --no-input --clear

# Apply any pending database migrations
python manage.py migrate
