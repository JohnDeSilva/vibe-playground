from pathlib import Path
from vibe_streamer.scanner import scan_directories


def test_scan_directories_with_mock(tmp_path):
    """
    Test scanning using dynamically created mock directories and files.
    """
    # Create the test directory structure
    series_a = tmp_path / "Series A"
    season_1 = series_a / "Season 1"
    season_2 = series_a / "Season 2"

    series_b = tmp_path / "Series B"
    season_b_1 = series_b / "Season 1"

    # Create the actual directories
    season_1.mkdir(parents=True)
    season_2.mkdir(parents=True)
    season_b_1.mkdir(parents=True)

    # Create mock video files
    ep1_path = season_1 / "S01E01.mkv"
    ep2_path = season_1 / "S01E02.mp4"
    ep3_path = season_2 / "S02E01.avi"
    ep4_path = season_b_1 / "S01E01.mkv"

    # Create a non-video file that should be ignored
    ignored_path = season_b_1 / "notes.txt"

    for f in [ep1_path, ep2_path, ep3_path, ep4_path, ignored_path]:
        f.touch()

    library = scan_directories([str(tmp_path)])

    # Verify Series A
    assert "Series A" in library
    assert "Season 1" in library["Series A"]
    assert "Season 2" in library["Series A"]

    s1_eps = library["Series A"]["Season 1"]
    assert len(s1_eps) == 2
    assert s1_eps[0]["name"] == "S01E01.mkv"
    assert s1_eps[0]["path"] == str(ep1_path.absolute())

    # Verify Series B and ensure non-video file was ignored
    assert "Series B" in library
    assert "Season 1" in library["Series B"]

    sb_eps = library["Series B"]["Season 1"]
    assert len(sb_eps) == 1
    assert sb_eps[0]["name"] == "S01E01.mkv"


def test_scan_directories_empty_list():
    assert scan_directories([]) == {}
