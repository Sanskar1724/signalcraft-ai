import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    from signalcraft import config, db
    p = tmp_path / "test.db"
    monkeypatch.setattr(config.settings, "db_path", p)
    db.init_db(p)
    return p


@pytest.fixture(autouse=True)
def _force_mock_llm(monkeypatch):
    """Tests stay offline/deterministic: never spend live quota (§26)."""
    from signalcraft import config
    monkeypatch.setattr(config.settings, "openrouter_api_key", "")
    monkeypatch.setattr(config.settings, "openai_api_key", "")
