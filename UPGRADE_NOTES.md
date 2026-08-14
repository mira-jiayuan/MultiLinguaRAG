# MultiLinguaRAG V3 Update

This update changes the project from **“answer in the query language”** to **independent language control**.

## Replace these existing files

- `app.py`
- `src/multilinguarag/generator.py`
- `src/multilinguarag/rag.py`
- `src/multilinguarag/cli.py`
- `tests/test_generator.py`
- `README.md`
- `INTERVIEW_GUIDE.md`
- `docs/index.html`

## Add this new file

- `docs/demo-preview-v3.svg`

## Main behavior after the update

```text
Source documents: English
Query: Chinese
Answer language: Japanese

→ retrieve English evidence
→ generate Japanese answer
→ cite the original English sources
```

## GitHub upload

Upload the files from this ZIP at the repository root and allow GitHub to overwrite files with the same paths.

Suggested commit message:

```text
feat: decouple source query and answer languages
```
