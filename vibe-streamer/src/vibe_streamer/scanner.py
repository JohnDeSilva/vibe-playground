import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Video file extensions we support
VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"}


def scan_directories(root_dirs: List[str]) -> Dict[str, Any]:
    """
    Scans the given root directories and builds a consolidated library.
    Expected structure:
    Root Directory / Series Name / Season X / Episode File

    Returns:
        {
            "Series Name": {
                "Season Name": [
                    {
                        "name": "Episode File.mkv",
                        "path": "/absolute/path/to/file.mkv"
                    },
                    ...
                ]
            }
        }
    """
    library = {}

    logger.info(f"Starting directory scan. Root directories: {root_dirs}")

    for root_dir in root_dirs:
        logger.info(f"Scanning root directory: {root_dir}")
        root_path = Path(root_dir)
        if not root_path.exists():
            logger.warning(f"Root directory does not exist: {root_dir}")
            continue
        if not root_path.is_dir():
            logger.warning(f"Root path is not a directory: {root_dir}")
            continue

        for series_dir in root_path.iterdir():
            if not series_dir.is_dir() or series_dir.name.startswith("."):
                continue

            logger.info(f"Found series directory: {series_dir.name}")
            series_name = series_dir.name
            if series_name not in library:
                library[series_name] = {}

            for season_dir in series_dir.iterdir():
                if not season_dir.is_dir() or season_dir.name.startswith("."):
                    continue

                logger.info(
                    f"Found season directory: {season_dir.name} in {series_name}"
                )
                season_name = season_dir.name
                if season_name not in library[series_name]:
                    library[series_name][season_name] = []

                for episode_file in season_dir.iterdir():
                    if (
                        episode_file.is_file()
                        and episode_file.suffix.lower() in VIDEO_EXTENSIONS
                    ):
                        logger.info(f"Found episode file: {episode_file.name}")
                        episode_info = {
                            "name": episode_file.name,
                            "path": str(episode_file.absolute()),
                        }

                        # Avoid duplicates if the same episode exists in different root dirs
                        # (We just check by name for simplicity)
                        existing_names = [
                            ep["name"] for ep in library[series_name][season_name]
                        ]
                        if episode_info["name"] not in existing_names:
                            library[series_name][season_name].append(episode_info)

                # Sort episodes alphabetically
                library[series_name][season_name].sort(key=lambda x: x["name"])

    # We might want to remove series/seasons that have no episodes
    clean_library = {}
    for series, seasons in library.items():
        clean_seasons = {}
        for season, episodes in seasons.items():
            if episodes:
                clean_seasons[season] = episodes
        if clean_seasons:
            clean_library[series] = clean_seasons

    return clean_library
