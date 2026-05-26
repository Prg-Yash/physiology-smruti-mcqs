# Deployment Guide

## Recommended: GitHub Pages (Static)

This project now runs as a static site using:

- index.html
- quiz.html
- results.html
- mcqs_data.json

No Flask server is required for deployment.

## Steps

1. Push your repository to GitHub.
2. Open repository Settings -> Pages.
3. In Build and deployment:
4. Source: Deploy from a branch.
5. Branch: main (or default), Folder: / (root).
6. Save and wait for the deployment URL.

## Important Notes

- .nojekyll is included to avoid Jekyll processing.
- Quiz results are stored in browser localStorage.
- Correct answers are visible client-side because data is in JSON.

## Local Preview

You can preview locally with any static server.

Example:

```bash
python -m http.server 8080
```

Then open http://localhost:8080.

## Notes

- This repository is static-only; the Flask server and templates have been removed.
