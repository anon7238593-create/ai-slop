#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# GitHub Release Publisher for Artifacts
# ==============================================================================
# Creates a GitHub Release of generated artifacts BEFORE committing them to the
# 'artifacts' branch. This enables hosting large media assets (videos, PDFs, etc.)
# up to 2GB on GitHub Releases without being constrained by Git's 100MB blob limit
# or causing repository bloat.
#
# Environment variables:
#   TARGET_DIR          (Required) Directory name on artifacts branch (e.g. collision-videos)
#   ARTIFACT_DIRECTORY  (Required) Path to the local directory containing generated assets
#   RELEASE_TITLE       (Optional) Release title (defaults to COMMIT_TITLE or generated title)
#   COMMIT_TITLE        (Optional) Fallback for RELEASE_TITLE
#   COMMIT_DESCRIPTION  (Optional) Markdown description / notes to include in the release
#   RELEASE_NOTES       (Optional) Fallback for COMMIT_DESCRIPTION
#   RELEASE_TAG_PREFIX  (Optional) Prefix for git tag (defaults to TARGET_DIR)
#   RELEASE_TAG         (Optional) Explicit git tag name override
#   RELEASE_LATEST      (Optional) Whether to mark as latest release (default: false)
#   GH_TOKEN            (Optional) GitHub CLI authentication token (or GITHUB_TOKEN)
#   DRY_RUN             (Optional) If 'true', skips network calls and simulates release
# ==============================================================================

if [ -z "${TARGET_DIR:-}" ] || [ -z "${ARTIFACT_DIRECTORY:-}" ]; then
  echo "Error: TARGET_DIR and ARTIFACT_DIRECTORY environment variables must be set." >&2
  exit 1
fi

if [ ! -d "$ARTIFACT_DIRECTORY" ]; then
  echo "Error: ARTIFACT_DIRECTORY '$ARTIFACT_DIRECTORY' does not exist or is not a directory." >&2
  exit 1
fi

# Ensure GH_TOKEN is set from GITHUB_TOKEN if present
if [ -z "${GH_TOKEN:-}" ] && [ -n "${GITHUB_TOKEN:-}" ]; then
  export GH_TOKEN="$GITHUB_TOKEN"
fi

DRY_RUN="${DRY_RUN:-false}"

# Check GitHub CLI availability if not in dry-run mode
if [ "$DRY_RUN" != "true" ]; then
  if ! command -v gh &>/dev/null; then
    echo "Error: GitHub CLI ('gh') is not installed or not in PATH." >&2
    exit 1
  fi

  if ! gh auth status &>/dev/null; then
    echo "Warning: GitHub CLI is not authenticated." >&2
    if [ "${GITHUB_ACTIONS:-}" = "true" ] || [ "${CI:-}" = "true" ]; then
      echo "Error: GH_TOKEN or GITHUB_TOKEN must be set in GitHub Actions." >&2
      exit 1
    else
      echo "Notice: Non-CI environment detected without auth; skipping remote release creation."
      touch "$ARTIFACT_DIRECTORY/.release_created"
      exit 0
    fi
  fi
fi

# Determine repository name
REPO_NAME="${GITHUB_REPOSITORY:-}"
if [ -z "$REPO_NAME" ] && command -v gh &>/dev/null; then
  REPO_NAME=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "anon7238593-create/ai-slop")
fi
if [ -z "$REPO_NAME" ]; then
  REPO_NAME="anon7238593-create/ai-slop"
fi

# 1. Determine Tag and Title
TAG_PREFIX="${RELEASE_TAG_PREFIX:-$TARGET_DIR}"
TIMESTAMP=$(date -u +'%Y%m%d-%H%M%S')

if [ -n "${RELEASE_TAG:-}" ]; then
  TAG_NAME="$RELEASE_TAG"
elif [ -n "${GITHUB_RUN_ID:-}" ]; then
  TAG_NAME="${TAG_PREFIX}-${TIMESTAMP}-run${GITHUB_RUN_ID}"
else
  TAG_NAME="${TAG_PREFIX}-${TIMESTAMP}"
fi

TITLE="${RELEASE_TITLE:-${COMMIT_TITLE:-"Artifacts: ${TAG_PREFIX} (${TIMESTAMP})"}}"

echo "================================================================="
echo "GITHUB ARTIFACTS RELEASE CREATOR"
echo "Target Directory:   $TARGET_DIR"
echo "Artifact Directory: $ARTIFACT_DIRECTORY"
echo "Release Tag:        $TAG_NAME"
echo "Release Title:      $TITLE"
echo "Repository:         $REPO_NAME"
echo "Dry Run:            $DRY_RUN"
echo "================================================================="

# 2. Build Release Notes
NOTES_FILE=$(mktemp)
{
  if [ -n "${COMMIT_DESCRIPTION:-}" ]; then
    echo "$COMMIT_DESCRIPTION"
    echo ""
  elif [ -n "${RELEASE_NOTES:-}" ]; then
    echo "$RELEASE_NOTES"
    echo ""
  fi

  if [ -f "$ARTIFACT_DIRECTORY/README.md" ]; then
    if [ -n "${COMMIT_DESCRIPTION:-}" ] || [ -n "${RELEASE_NOTES:-}" ]; then
      echo "---"
      echo ""
    fi
    cat "$ARTIFACT_DIRECTORY/README.md"
  elif [ -z "${COMMIT_DESCRIPTION:-}" ] && [ -z "${RELEASE_NOTES:-}" ]; then
    echo "Media and visualization artifacts for \`$TARGET_DIR\` generated on $(date -u +'%Y-%m-%d %H:%M UTC')."
  fi
} > "$NOTES_FILE"

# 3. Collect Assets to Upload
UPLOAD_ASSETS=()

# Create full directory ZIP bundle
TEMP_ARCHIVE_DIR=$(mktemp -d)
ARCHIVE_FILE="${TEMP_ARCHIVE_DIR}/${TAG_NAME}.zip"
if command -v zip &>/dev/null; then
  echo "==> Packaging full artifact bundle into ZIP archive..."
  (cd "$ARTIFACT_DIRECTORY" && zip -r -q "$ARCHIVE_FILE" . -x ".*")
  if [ -f "$ARCHIVE_FILE" ]; then
    UPLOAD_ASSETS+=("$ARCHIVE_FILE")
    echo "    Created bundle: $(basename "$ARCHIVE_FILE") ($(du -h "$ARCHIVE_FILE" | cut -f1))"
  fi
fi

# Collect individual media assets and manifests
echo "==> Collecting individual files for release upload..."
while IFS= read -r f; do
  [ -f "$f" ] || continue
  bname="$(basename "$f")"
  case "$bname" in
    .*|*.tmp) continue ;;
    *)
      UPLOAD_ASSETS+=("$f")
      echo "    - $bname ($(du -h "$f" | cut -f1))"
      ;;
  esac
done < <(find "$ARTIFACT_DIRECTORY" -maxdepth 1 -type f | sort)

# Include key documents in immediate subdirectories (e.g. traversal walkthroughs)
if [ -d "$ARTIFACT_DIRECTORY/specific-node" ]; then
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    bname="$(basename "$f")"
    case "$bname" in
      *.pdf)
        UPLOAD_ASSETS+=("$f")
        echo "    - specific-node/$bname ($(du -h "$f" | cut -f1))"
        ;;
    esac
  done < <(find "$ARTIFACT_DIRECTORY/specific-node" -maxdepth 1 -type f | sort)
fi

echo "==> Total assets prepared for release: ${#UPLOAD_ASSETS[@]}"

# 4. Create the GitHub Release
RELEASE_URL="https://github.com/${REPO_NAME}/releases/tag/${TAG_NAME}"
BASE_DOWNLOAD_URL="https://github.com/${REPO_NAME}/releases/download/${TAG_NAME}"

if [ "$DRY_RUN" = "true" ]; then
  echo "==> [DRY RUN] Skipping actual 'gh release create' call."
  echo "    Simulated Release URL: $RELEASE_URL"
else
  TARGET_REF="${GITHUB_SHA:-master}"
  MAX_ATTEMPTS=3
  ATTEMPT=0
  SUCCESS=0

  while [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; do
    ATTEMPT=$((ATTEMPT + 1))

    if gh release view "$TAG_NAME" &>/dev/null; then
      echo "==> [Attempt $ATTEMPT/$MAX_ATTEMPTS] Release '$TAG_NAME' already exists. Updating release metadata and uploading assets with --clobber..."
      if gh release edit "$TAG_NAME" --title "$TITLE" --notes-file "$NOTES_FILE" && \
         gh release upload "$TAG_NAME" "${UPLOAD_ASSETS[@]}" --clobber; then
        SUCCESS=1
        break
      fi
    else
      echo "==> [Attempt $ATTEMPT/$MAX_ATTEMPTS] Creating GitHub Release '$TAG_NAME'..."
      if gh release create "$TAG_NAME" "${UPLOAD_ASSETS[@]}" \
           --title "$TITLE" \
           --notes-file "$NOTES_FILE" \
           --target "$TARGET_REF" \
           --latest="${RELEASE_LATEST:-false}"; then
        SUCCESS=1
        break
      fi
    fi

    echo "Warning: Release operation failed on attempt $ATTEMPT."
    if [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; then
      sleep 4
    fi
  done

  if [ "$SUCCESS" -ne 1 ]; then
    echo "Error: Failed to create GitHub Release '$TAG_NAME' after $MAX_ATTEMPTS attempts." >&2
    rm -f "$NOTES_FILE"
    rm -rf "$TEMP_ARCHIVE_DIR"
    exit 1
  fi

  # Query the actual release URL from GitHub
  ACTUAL_URL=$(gh release view "$TAG_NAME" --json url -q .url 2>/dev/null || true)
  if [ -n "$ACTUAL_URL" ]; then
    RELEASE_URL="$ACTUAL_URL"
  fi
fi

rm -f "$NOTES_FILE"
rm -rf "$TEMP_ARCHIVE_DIR"

echo "==> Release established: $RELEASE_URL"

# 5. Enrich manifest.json with release URLs and large media indicators
MANIFEST_PATH="$ARTIFACT_DIRECTORY/manifest.json"
if [ -f "$MANIFEST_PATH" ]; then
  echo "==> Updating manifest.json with release URLs..."
  python3 - <<PY
import json
import os

manifest_path = "$MANIFEST_PATH"
try:
    with open(manifest_path, "r", encoding="utf-8") as f:
        m = json.load(f)

    tag = "$TAG_NAME"
    rel_url = "$RELEASE_URL"
    base_download = "$BASE_DOWNLOAD_URL"
    archive_name = f"{tag}.zip"

    m["release_tag"] = tag
    m["release_url"] = rel_url
    m["release_archive_url"] = f"{base_download}/{archive_name}"

    # Collision videos metadata
    if "videos" in m and isinstance(m["videos"], list):
        for v in m["videos"]:
            fname = v.get("filename")
            if fname:
                v["release_download_url"] = f"{base_download}/{fname}"
                fpath = os.path.join("$ARTIFACT_DIRECTORY", fname)
                if os.path.isfile(fpath):
                    # Flag whether this file will be retained in git branch or release-only
                    v["has_git_blob"] = os.path.getsize(fpath) < 95 * 1024 * 1024

    # GCD grids metadata
    if "grids" in m and isinstance(m["grids"], list):
        for g in m["grids"]:
            fname = g.get("file")
            if fname:
                g["release_download_url"] = f"{base_download}/{fname}"

    # Voronoi diagrams metadata
    if "diagrams" in m and isinstance(m["diagrams"], list):
        for d in m["diagrams"]:
            fname = d.get("file")
            if fname:
                d["release_download_url"] = f"{base_download}/{fname}"
    elif "files" in m and isinstance(m["files"], list):
        for vf in m["files"]:
            fname = vf.get("file")
            if fname:
                vf["release_download_url"] = f"{base_download}/{fname}"

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("    Successfully injected release URLs into manifest.json.")
except Exception as e:
    print(f"    Notice: Could not update manifest.json: {e}")
PY
fi

# 6. Prepend Release Link Badge to README.md if present
README_PATH="$ARTIFACT_DIRECTORY/README.md"
if [ -f "$README_PATH" ]; then
  if ! grep -q "GitHub Release" "$README_PATH"; then
    echo "==> Prepending GitHub Release link to README.md..."
    HEADER_MD=$(cat <<EOF
> 📦 **GitHub Release**: [\`${TAG_NAME}\`](${RELEASE_URL}) &middot; **Full Bundle**: [\`${TAG_NAME}.zip\`](${BASE_DOWNLOAD_URL}/${TAG_NAME}.zip)

EOF
)
    TEMP_README=$(mktemp)
    printf "%s\n" "$HEADER_MD" > "$TEMP_README"
    cat "$README_PATH" >> "$TEMP_README"
    mv "$TEMP_README" "$README_PATH"
  fi
fi

# 7. Write completion markers
touch "$ARTIFACT_DIRECTORY/.release_created"
echo "$TAG_NAME" > "$ARTIFACT_DIRECTORY/.release_tag"
echo "$RELEASE_URL" > "$ARTIFACT_DIRECTORY/.release_url"

echo "==> Release process finished successfully for '$TARGET_DIR'."
