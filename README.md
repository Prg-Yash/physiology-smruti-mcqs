# Physiology MCQ Quiz

Static quiz app for physiology MCQs, designed to deploy directly on GitHub Pages.

## Features

- 1,505 questions across 10 categories
- Fully static frontend (no server, no database)
- Client-side quiz engine with instant feedback
- Results and answer summary saved in browser localStorage
- Responsive UI for desktop and mobile

## Static Architecture

- `index.html`: category listing and stats
- `quiz.html`: quiz flow, scoring, and progress tracking
- `results.html`: result summary and answer review
- `mcqs_data.json`: all quiz data

No backend is required for deployment.

## Quick Start (Local)

Open `index.html` in a browser, or serve the folder with any static server.

Example with Python:

```bash
python -m http.server 8080
```

Then open `http://localhost:8080`.

## GitHub Pages Deployment (Recommended)

1. Push this project to a GitHub repository.
2. Go to repository `Settings` -> `Pages`.
3. Under `Build and deployment`:
4. Set `Source` to `Deploy from a branch`.
5. Select branch `main` (or your default branch) and folder `/ (root)`.
6. Save.
7. Wait for deployment, then open the generated Pages URL.

Notes:

- `.nojekyll` is included for static compatibility.
- Because answers are in JSON, correct options are visible client-side.

## Data Format

`mcqs_data.json` uses this structure:

```json
{
   "stats": {
      "total_mcqs": 1505,
      "categories": {
         "Category Name": 123
      }
   },
   "mcqs": {
      "Category Name": [
         {
            "question": "Question text",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 0,
            "page": 1
         }
      ]
   }
}
```

## Legacy Flask Mode (Optional)

The old Flask app still exists (`app.py` + `templates/`) if you want server-rendered mode for local experiments.

## Project Files

```text
.
├── index.html
├── quiz.html
├── results.html
├── mcqs_data.json
├── .nojekyll
├── app.py
├── templates/
└── README.md
```
