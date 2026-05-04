# Hermes Tidal Curator

Tidal integration skill for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — playlist creation, track search, OAuth authentication, and ListenBrainz-powered curation.

## What It Does

- **OAuth authentication** with Tidal
- **Playlist management** — create, find, get-or-create
- **Track search** — search by artist/title, add to playlists
- **Rate limiting** — built-in 2-second delays to avoid 412 errors
- **ListenBrainz integration** — power recommendations from your listening history
- **Daily curation cron** — morning and evening playlist additions

## Installation

```bash
hermes skills install https://github.com/RegeneratusLabs/hermes-tidal-curator
```

## Setup

### 1. Authenticate with Tidal

```python
from skills.tidal_curator import TidalCurator

tidal = TidalCurator()
url = tidal.start_auth()
print(f"Visit: {url}")
tidal.complete_auth()
```

Or via CLI:
```bash
python curator.py auth
```

### 2. Configure Credentials

The skill stores your Tidal session in `~/.hermes/tidal_session.json` (auto-created after auth).

Required Python package:
```bash
pip install tidalapi
```

## Usage

```python
from skills.tidal_curator import TidalCurator

tidal = TidalCurator()

# Create or find a playlist
playlist = tidal.get_or_create_playlist(
    "My Summer Mix",
    "Chill vibes for hot afternoons"
)

# Search and add a track
track = tidal.search_track("East Forest", "Hold")
if track:
    tidal.add_tracks_to_playlist(playlist, [track])
```

## CLI Commands

```bash
python curator.py auth      # Authenticate with Tidal
python curator.py status    # Check auth status
python curator.py test      # Run a test: create playlist + add track
```

## API Reference

| Method | Returns | Description |
|--------|---------|-------------|
| `is_authenticated()` | bool | Check if Tidal session is valid |
| `start_auth()` | str | Get OAuth verification URL |
| `complete_auth()` | bool | Complete OAuth flow |
| `get_user_info()` | dict | Current user details |
| `get_playlist(name)` | Playlist | Find playlist by name |
| `create_playlist(name, desc)` | Playlist | Create new playlist |
| `get_or_create_playlist(name, desc)` | Playlist | Get or create |
| `search_track(artist, title)` | Track | Find a track |
| `add_tracks_to_playlist(playlist, tracks)` | dict | Add tracks (rate-limited) |

## Integration with Hermes

Load the skill in Hermes and use it in your prompts:

```
hermes chat -s tidal-curator
```

Then in conversation:
```
Add Mac Miller - Hurt Feelings to my "Evening Wind Down" playlist
```

## License

MIT
