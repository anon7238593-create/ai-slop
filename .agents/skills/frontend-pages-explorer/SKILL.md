---
name: frontend-pages-explorer
description: >-
  Automatically use this skill whenever working on GitHub Pages, the media explorer website, template.html, build_pages.py, static showcase pages, UI tabs (#collision, #gcd, #voronoi, #traversal), or video player and SVG inspection frontends.
---

# Frontend & GitHub Pages Showcase Skill

## Purpose
Maintain and enhance the interactive web explorer hosted at https://anon7238593-create.github.io/ai-slop/ with zero heavy dependencies, sub-second load times, and clean dark UI.

## Key Files
- `.github/scripts/build_pages.py`: Ingests manifests and compiles `_site/index.html`.
- `.github/scripts/template.html`: Dark UI template, URL hash routing, spotlights.
- `probability/index.html`: Interactive probability visualizer.

## Procedures

### 1. Adding a New Media Section
1. Update `build_pages.py` to ingest the new folder's `manifest.json`.
2. Add a navigation tab and showcase view in `template.html`.
3. Support search/filter, sorting, and pagination without third-party frameworks.

### 2. Local Preview
```bash
python3 .github/scripts/build_pages.py --mock --output-dir /tmp/ai-slop-site
cd /tmp/ai-slop-site && python3 -m http.server 8000
```
