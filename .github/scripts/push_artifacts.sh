#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Atomic Artifacts Publisher
# ==============================================================================
# Publishes a generated directory to the 'artifacts' branch cleanly and safely.
# Avoids 'git rebase' merge conflicts by resetting locally to the latest remote
# HEAD on each retry attempt and creating a clean commit directly on top of it.
# Resolves push ref lock contention with exponential backoff and random jitter.
# ==============================================================================

if [ -z "${TARGET_DIR:-}" ] || [ -z "${ARTIFACT_DIRECTORY:-}" ] || [ -z "${COMMIT_TITLE:-}" ]; then
  echo "Error: TARGET_DIR, ARTIFACT_DIRECTORY, and COMMIT_TITLE environment variables must be set." >&2
  exit 1
fi

if [ ! -d "$ARTIFACT_DIRECTORY" ]; then
  echo "Error: ARTIFACT_DIRECTORY '$ARTIFACT_DIRECTORY' does not exist or is not a directory." >&2
  exit 1
fi

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

# Clean any working tree modifications from earlier build steps
git reset --hard HEAD || true
git clean -fd || true

MAX_ATTEMPTS=15
ATTEMPT=0
SUCCESS=0

while [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; do
  ATTEMPT=$((ATTEMPT + 1))
  echo "==> [Attempt $ATTEMPT/$MAX_ATTEMPTS] Publishing '$TARGET_DIR' to 'artifacts' branch..."

  # 1. Fetch latest remote state of artifacts branch
  git fetch origin artifacts || true

  # 2. Check out artifacts branch tracking origin/artifacts, or orphan if non-existent
  if git show-ref --verify --quiet refs/remotes/origin/artifacts; then
    git checkout -B artifacts origin/artifacts
    git reset --hard origin/artifacts
    git clean -fd
  else
    git checkout --orphan artifacts
    git rm -rf . || true
  fi

  # 3. Replace target directory with newly generated artifacts
  rm -rf "$TARGET_DIR"
  cp -R "$ARTIFACT_DIRECTORY" "$TARGET_DIR"
  git add "$TARGET_DIR"

  # 4. Check if there are actual changes compared to latest remote HEAD
  if git diff --staged --quiet; then
    echo "Notice: No staged changes for '$TARGET_DIR'; artifacts are already up to date."
    SUCCESS=1
    break
  fi

  # 5. Commit changes directly on top of latest remote HEAD
  if [ -n "${COMMIT_DESCRIPTION:-}" ]; then
    git commit -m "$COMMIT_TITLE" -m "$COMMIT_DESCRIPTION"
  else
    git commit -m "$COMMIT_TITLE"
  fi

  # 6. Attempt push to remote artifacts branch
  if git push origin HEAD:artifacts; then
    echo "==> Successfully pushed '$TARGET_DIR' to 'origin/artifacts'!"
    SUCCESS=1
    break
  fi

  echo "Warning: Push to 'artifacts' was rejected or ref locked (concurrent remote update)."
  # Exponential backoff with random jitter between 2 and 6 seconds to avoid lock collisions
  backoff_seconds=$(( (RANDOM % 5) + 2 ))
  echo "Waiting ${backoff_seconds}s before next attempt..."
  sleep "$backoff_seconds"
done

if [ "$SUCCESS" -ne 1 ]; then
  echo "Error: Failed to push '$TARGET_DIR' to artifacts branch after $MAX_ATTEMPTS attempts." >&2
  exit 1
fi
