# Development guide

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # optional; offline Mock LLM is the default
pytest -q
streamlit run app.py
```

Conventions: stdlib-first, typed functions, bounded loops (1 revise, 8 tool
calls, 60s agent budget), no secrets in code, `prompt.txt` is the product
constitution — re-read it before adding architecture. Run `pytest -q` before
every commit; keep the app bootable at every phase (§27).
