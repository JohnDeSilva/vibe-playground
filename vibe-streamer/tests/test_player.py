import pytest
import subprocess
import sys
from vibe_streamer.player import play_video

def test_play_video_file_not_found():
    with pytest.raises(FileNotFoundError):
        play_video("/non/existent/path.mkv")

def test_play_video_success(monkeypatch, tmp_path):
    # Create a dummy file
    dummy_file = tmp_path / "dummy.mkv"
    dummy_file.touch()
    
    # We want to intercept the subprocess.Popen call to verify arguments
    called_args = None
    
    def mock_popen(args, *a, **kw):
        nonlocal called_args
        called_args = args
        return None
        
    monkeypatch.setattr(subprocess, "Popen", mock_popen)
    
    play_video(str(dummy_file))
    
    assert called_args is not None
    
    # Verify no compression arguments are passed, just the executable and the raw file path
    if sys.platform == "win32":
        assert called_args == ["vlc", str(dummy_file)]
    elif sys.platform == "darwin":
        assert called_args == ["open", "-a", "VLC", str(dummy_file)]
    else:
        assert called_args == ["vlc", str(dummy_file)]
