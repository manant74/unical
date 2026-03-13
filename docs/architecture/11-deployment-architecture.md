# 11. Deployment Architecture

← [Back to Index](index.md)

---

## Local Development

```bash
pip install -r requirements.txt
python setup_models.py           # one-time: downloads ~120MB embedding model
cp .env.example .env             # add GOOGLE_API_KEY and/or OPENAI_API_KEY
streamlit run app.py             # default port 8501
streamlit run app.py --server.port 8502  # custom port
```

## Runtime Requirements

| Component | Requirement |
|-----------|------------|
| Python | 3.10+ (type hints, match statements) |
| Memory | ~500MB for embedding model in memory |
| Disk | ~120MB for model cache + variable for ChromaDB |
| Network | API key access to Google or OpenAI |
| OS | Windows/Linux/macOS (ChromaDB has Windows file lock considerations) |

## Environment Configuration

```env
GOOGLE_API_KEY=...    # For Gemini models
OPENAI_API_KEY=...    # For GPT models (at least one required)
```

## Data Persistence

All data is stored locally in `data/` directory. No external database required. For deployment, mount `data/` as a persistent volume.

## Windows-Specific Considerations

- ChromaDB file locks on Windows require explicit `release_connections()` calls
- Use forward slashes or `os.path.join()` for path construction
- UTF-8 encoding specified explicitly in all file operations

---

← [Previous: Testing Architecture](10-testing-architecture.md) | [Back to Index](index.md) | Next: [Extension and Evolution Patterns →](12-extension-and-evolution-patterns.md)
