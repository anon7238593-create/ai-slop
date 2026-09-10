#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Fast Atomic Artifacts Publisher (Blobless Tree-Plumbing)
# ==============================================================================
# Publishes a generated directory to the 'artifacts' branch without downloading
# heavy media blobs or historical commits. Preserves all other directories on
# the artifacts branch using low-level git tree manipulation.
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

# 1. Write the new target directory into Git's object store (isolated index)
TMP_INDEX=$(mktemp -u)
NEW_SUBTREE=$(GIT_INDEX_FILE="$TMP_INDEX" git --work-tree="$ARTIFACT_DIRECTORY" add -A && GIT_INDEX_FILE="$TMP_INDEX" git write-tree)
rm -f "$TMP_INDEX"
echo "==> Generated subtree for '$TARGET_DIR': $NEW_SUBTREE"

if [ -n "${COMMIT_DESCRIPTION:-}" ]; then
  COMMIT_MSG=$(printf "%s\n\n%s" "$COMMIT_TITLE" "$COMMIT_DESCRIPTION")
else
  COMMIT_MSG="$COMMIT_TITLE"
fi

MAX_ATTEMPTS=15
ATTEMPT=0
SUCCESS=0

while [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; do
  ATTEMPT=$((ATTEMPT + 1))
  echo "==> [Attempt $ATTEMPT/$MAX_ATTEMPTS] Publishing '$TARGET_DIR' to 'artifacts' branch..."

  # 2. Blobless shallow fetch: fetches ONLY the commit/tree object (~10 KB, 0 blobs downloaded)
  FETCH_SUCCESS=0
  if git fetch --filter=blob:none --depth=1 origin artifacts 2>/dev/null; then
    FETCH_SUCCESS=1
  fi

  if [ "$FETCH_SUCCESS" -eq 1 ] && git rev-parse --verify -q FETCH_HEAD >/dev/null; then
    PARENT_COMMIT=$(git rev-parse FETCH_HEAD)

    # Check if the target directory has changed
    OLD_SUBTREE=$(git ls-tree FETCH_HEAD | awk -F"\t" -v target="$TARGET_DIR" '$2 == target {split($1, a, " "); print a[3]}')
    if [ -n "$OLD_SUBTREE" ] && [ "$OLD_SUBTREE" = "$NEW_SUBTREE" ]; then
      echo "Notice: No changes for '$TARGET_DIR'; artifacts are already up to date."
      SUCCESS=1
      break
    fi

    # Build new root tree: keep all other folders from remote, insert/replace TARGET_DIR
    NEW_ROOT_TREE=$( (git ls-tree FETCH_HEAD | awk -F"\t" -v target="$TARGET_DIR" '$2 != target'; printf "040000 tree %s\t%s\n" "$NEW_SUBTREE" "$TARGET_DIR") | git mktree )
    NEW_COMMIT=$(git commit-tree "$NEW_ROOT_TREE" -p "$PARENT_COMMIT" -m "$COMMIT_MSG")
  else
    # Initial creation of artifacts branch if it does not yet exist
    NEW_ROOT_TREE=$(printf "040000 tree %s\t%s\n" "$NEW_SUBTREE" "$TARGET_DIR" | git mktree)
    NEW_COMMIT=$(git commit-tree "$NEW_ROOT_TREE" -m "$COMMIT_MSG")
  fi

  # 3. Push commit directly to remote artifacts branch
  if git push origin "$NEW_COMMIT:refs/heads/artifacts"; then
    echo "==> Successfully pushed '$TARGET_DIR' to 'origin/artifacts'!"
    SUCCESS=1
    break
  fi

  echo "Warning: Push to 'artifacts' was rejected (concurrent remote update)."
  backoff_seconds=$(( (RANDOM % 5) + 2 ))
  echo "Waiting ${backoff_seconds}s before next attempt..."
  sleep "$backoff_seconds"
done

if [ "$SUCCESS" -ne 1 ]; then
  echo "Error: Failed to push '$TARGET_DIR' to artifacts branch after $MAX_ATTEMPTS attempts." >&2
  exit 1
fi
