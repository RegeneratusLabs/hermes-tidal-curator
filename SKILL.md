---
name: tidal-curator
description: Base Tidal integration skill for Hermes. Provides OAuth authentication, playlist CRUD, track search, and rate-limit-safe track addition. Import into other skills as a foundation.
tags: [music, tidal, base-skill, api, playlist, oauth]
---

# Tidal Curator - Base Skill

Foundation skill for Tidal integration. Provides OAuth authentication and core playlist/track operations that other skills build upon.

**This is the base library.** If you want daily curation or recommendations, install the supplementary skills below.

## What It Provides

- **OAuth Authentication** — Tidal login via `tidalapi`
- **Playlist Management** — create, find, get-or-create
- **Track Operations** — search by artist/title, add to playlists
- **Rate Limiting** — built-in delays to avoid Tidal API 412 errors

## Installation

```bash
hermes skills install https://github.com/RegeneratusLabs/hermes-tidal-curator
pip install tidalapi
```

## Setup

Authenticate once:
```python
from skills.tidal_curator import TidalCurator

tidal = TidalCurator()
url = tidal.start_auth()
print(f"Visit: {url}")
tidal.complete_auth()
```

Session persists at `~/.hermes/tidal_session.json`.

## Usage

```python
from skills.tidal_curator import TidalCurator

tidal = TidalCurator()

# Check auth
if not tidal.is_authenticated():
    print("Run auth first")

# Create playlist
playlist = tidal.get_or_create_playlist("My Mix", "Description")

# Search and add
track = tidal.search_track("Mac Miller", "Hurt Feelings")
if track:
    tidal.add_tracks_to_playlist(playlist, [track])
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

---

## Supplementary Skills

Each is fully standalone and installable separately:

### [Tidal Dual Curator](https://github.com/RegeneratusLabs/hermes-tidal-dual-curator)

Daily morning (9am) and evening (6pm) Tidal playlist curation.

```bash
hermes skills install https://github.com/RegeneratusLabs/hermes-tidal-dual-curator
```

- Morning Vibe playlist — confident, ambitious, energetic
- Evening Wind Down playlist — chill, reflective, introspective
- ListenBrainz integration for personalized picks
- Cron-ready: `python dual_curator.py morning` / `evening`

### [Tidal Playlist Creator](https://github.com/RegeneratusLabs/hermes-tidal-playlist-creator)

Create Tidal playlists from ListenBrainz history or custom track lists.

```bash
hermes skills install https://github.com/RegeneratusLabs/hermes-tidal-playlist-creator
```

- Import from ListenBrainz (top tracks or recent listens)
- Custom track lists via JSON
- Export to TuneMyMusic / Soundiiz format
- Dry-run mode

### [Tidal Recommendation Engine](https://github.com/RegeneratusLabs/hermes-tidal-recommendation)

AI-powered music discovery for Tidal using ListenBrainz taste profile and web search.

```bash
hermes skills install https://github.com/RegeneratusLabs/hermes-tidal-recommendation
```

- Build taste profile from ListenBrainz listening history
- Recommend by vibe, seed artist, or personalized taste
- Tidal-ready output with direct links
- Works best inside Hermes (web search enabled)

## License

MIT
