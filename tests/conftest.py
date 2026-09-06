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
