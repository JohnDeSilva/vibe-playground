import pytest


@pytest.fixture(autouse=True)
def protect_user_dirs(tmp_path, monkeypatch):
    """
    Ensure no test can ever overwrite the user's actual config or DB.
    We patch all the paths to point to tmp_path.
    """
    import vibe_streamer.config
    import vibe_streamer.db
    import vibe_streamer.jellyfin

    config_file = tmp_path / "config.json"
    db_file = tmp_path / "library.db"
    cache_dir = tmp_path / "cache" / "images"

    monkeypatch.setattr(vibe_streamer.config, "CONFIG_FILE", config_file)
    monkeypatch.setattr(vibe_streamer.db, "DB_FILE", db_file)
    monkeypatch.setattr(vibe_streamer.jellyfin, "CACHE_DIR", cache_dir)

    # Reload config instance so it points to the new path
    # But note that the Config() instance in vibe_streamer.config
    # has already been initialized with the old path.
    # So we should also patch the already-initialized object or reset it.
    vibe_streamer.config.config.libraries = {}
    vibe_streamer.config.config.jellyfin_url = ""
    vibe_streamer.config.config.jellyfin_api_key = ""
