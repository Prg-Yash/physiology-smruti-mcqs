# Deployment Ready

## Status

This project is ready for direct deployment on GitHub Pages.

## Verified Static Setup

- Root static entry page: index.html
- Static quiz flow page: quiz.html
- Static result page: results.html
- Question source: mcqs_data.json
- GitHub Pages compatibility file: .nojekyll

## What Changed

- Removed runtime dependency on backend APIs for the primary flow.
- Replaced server-rendered routing with query-parameter routing.
- Implemented client-side scoring and progress tracking.
- Persisted results using localStorage per category.

## Deploy Checklist

- Push to GitHub.
- Enable Pages from main branch and / (root) folder.
- Open generated Pages URL.
- Confirm category selection, quiz flow, and results page work.

## Notes

- Flask files are still present for optional legacy/local use.
- Because all data is client-side, correct answers can be inspected in browser devtools.
