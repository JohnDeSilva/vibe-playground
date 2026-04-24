from pathlib import Path
from vibe_streamer.scanner import scan_directories

def test_scan_directories_with_daredevil(monkeypatch):
    """
    Test scanning the provided Daredevil directory.
    We will use the actual test path provided by the user.
    """
    test_root = "/run/user/1000/gvfs/smb-share:server=rv_nas.local,share=storage/current/video/tv"
    
    # If the directory doesn't exist (e.g. running in CI), we just pass
    if not Path(test_root).exists():
        return
        
    library = scan_directories([test_root])
    
    # Check if Daredevil is found
    assert "Daredevil - Born Again" in library, "Daredevil series not found in scanned library"
    
    daredevil = library["Daredevil - Born Again"]
    assert "Season 2" in daredevil, "Season 2 not found in Daredevil series"
    
    episodes = daredevil["Season 2"]
    assert len(episodes) > 0, "No episodes found in Season 2"
    
    # Check episode structure
    first_ep = episodes[0]
    assert "name" in first_ep
    assert "path" in first_ep
    assert "S02E01" in first_ep["name"]
    
def test_scan_directories_empty_list():
    assert scan_directories([]) == {}
