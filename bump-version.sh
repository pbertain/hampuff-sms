#!/bin/bash

# Version bumping script for Hampuff SMS
# Usage: ./bump-version.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}

if [[ "$ENVIRONMENT" == "dev" ]]; then
    VERSION_FILE="version.dev.txt"
    echo "Bumping development version..."
elif [[ "$ENVIRONMENT" == "prod" ]]; then
    VERSION_FILE="version.prod.txt"
    echo "Bumping production version..."
else
    echo "Usage: $0 [dev|prod]"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(cat "$VERSION_FILE")
echo "Current $ENVIRONMENT version: $CURRENT_VERSION"

if [[ "$ENVIRONMENT" == "dev" ]]; then
    # Extract dev version parts
    if [[ $CURRENT_VERSION =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)-dev\.([0-9]+)$ ]]; then
        MAJOR=${BASH_REMATCH[1]}
        MINOR=${BASH_REMATCH[2]}
        PATCH=${BASH_REMATCH[3]}
        DEV_BUILD=${BASH_REMATCH[4]}
        
        # Increment dev build number
        NEW_DEV_BUILD=$((DEV_BUILD + 1))
        NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}-dev.${NEW_DEV_BUILD}"
    else
        # Fallback if format doesn't match
        NEW_VERSION="1.0.0-dev.1"
    fi
else
    # Extract prod version parts
    if [[ $CURRENT_VERSION =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        MAJOR=${BASH_REMATCH[1]}
        MINOR=${BASH_REMATCH[2]}
        PATCH=${BASH_REMATCH[3]}
        
        # Increment patch version for production
        NEW_PATCH=$((PATCH + 1))
        NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"
    else
        # Fallback if format doesn't match
        NEW_VERSION="1.0.0"
    fi
fi

echo "New $ENVIRONMENT version: $NEW_VERSION"

# Update version files
echo "$NEW_VERSION" > "$VERSION_FILE"
echo "$NEW_VERSION" > version.txt

echo "Version files updated:"
echo "  $VERSION_FILE: $NEW_VERSION"
echo "  version.txt: $NEW_VERSION"

echo ""
echo "To commit and push:"
echo "  git add $VERSION_FILE version.txt"
echo "  git commit -m \"Bump $ENVIRONMENT version to $NEW_VERSION\""
echo "  git push origin $(git branch --show-current)"
