# Demo Setup

## Static GitHub Pages preview

The `docs/` folder contains a static portfolio preview that does **not** run the RAG backend.
It is intended to help visitors understand the product experience immediately.

To publish it:

1. Open the repository on GitHub.
2. Go to **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select branch **main** and folder **/docs**.
5. Save.

GitHub will provide a public Pages URL after deployment.

## Live local Streamlit app

The actual RAG application is `app.py`.

```bash
uv sync
cp .env.example .env
uv run multilinguarag-ingest data/sample --recreate
uv run streamlit run app.py
```

The first live run downloads the configured embedding model. The static GitHub Pages preview does not require that download.
