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

# Ensure GitHub Release is created before committing artifacts to the branch
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "$ARTIFACT_DIRECTORY/.release_created" ] && [ "${SKIP_RELEASE:-false}" != "true" ]; then
  echo "==> Triggering artifact release creation before committing to artifacts branch..."
  bash "$SCRIPT_DIR/create_release.sh"
fi

# Fetch release URL if available
RELEASE_URL=""
if [ -f "$ARTIFACT_DIRECTORY/.release_url" ]; then
  RELEASE_URL="$(cat "$ARTIFACT_DIRECTORY/.release_url")"
elif [ -f "$ARTIFACT_DIRECTORY/manifest.json" ]; then
  RELEASE_URL="$(python3 -c 'import json; print(json.load(open("'"$ARTIFACT_DIRECTORY"'/manifest.json")).get("release_url", ""))' 2>/dev/null || true)"
fi

# Clean up marker files so they aren't tracked in git index
rm -f "$ARTIFACT_DIRECTORY/.release_created" "$ARTIFACT_DIRECTORY/.release_tag" "$ARTIFACT_DIRECTORY/.release_url"

# 1. Write the new target directory into Git's object store (isolated index)
TMP_INDEX=$(mktemp -u)
GIT_INDEX_FILE="$TMP_INDEX" git --work-tree="$ARTIFACT_DIRECTORY" add -A

# Exclude oversized files (>=95MB) from Git commit to avoid GitHub 100MB file limit errors.
# Oversized files are already preserved and hosted on the GitHub Release!
OVERSIZED_FILES=$(find "$ARTIFACT_DIRECTORY" -type f -size +95M 2>/dev/null || true)
if [ -n "$OVERSIZED_FILES" ]; then
  echo "==> Notice: Excluding media files >=95MB from Git branch (hosted in GitHub Release):"
  while IFS= read -r large_file; do
    [ -n "$large_file" ] || continue
    rel_path="${large_file#$ARTIFACT_DIRECTORY/}"
    echo "    - $rel_path ($(du -h "$large_file" | cut -f1))"
    GIT_INDEX_FILE="$TMP_INDEX" git --work-tree="$ARTIFACT_DIRECTORY" rm --cached -f "$rel_path" >/dev/null
  done <<< "$OVERSIZED_FILES"
fi

NEW_SUBTREE=$(GIT_INDEX_FILE="$TMP_INDEX" git write-tree)
rm -f "$TMP_INDEX"
echo "==> Generated subtree for '$TARGET_DIR': $NEW_SUBTREE"

if [ -n "${COMMIT_DESCRIPTION:-}" ]; then
  COMMIT_MSG=$(printf "%s\n\n%s" "$COMMIT_TITLE" "$COMMIT_DESCRIPTION")
else
  COMMIT_MSG="$COMMIT_TITLE"
fi

if [ -n "$RELEASE_URL" ]; then
  COMMIT_MSG=$(printf "%s\n\nRelease: %s" "$COMMIT_MSG" "$RELEASE_URL")
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
