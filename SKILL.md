---
name: tidal-curator
description: Base Tidal integration skill for Hermes. Provides playlist creation, track search, and track addition capabilities. Other skills can import and use this as a foundation.
tags: [music, tidal, base-skill, api, playlist]
---

# Tidal Curator - Base Skill

Foundation skill for Tidal integration. Provides core functionality that other skills can build upon.

## What It Provides

- **Authentication**: Handle Tidal OAuth and session management
- **Playlist Management**: Create, find, and manage playlists
- **Track Operations**: Search tracks, add to playlists
- **Rate Limiting**: Built-in API call throttling

## Usage in Other Skills

```python
from skills.tidal_curator import TidalCurator

# Initialize
tidal = TidalCurator()

# Check auth
if not tidal.is_authenticated():
    return "Please authenticate with Tidal first"

# Create playlist
playlist = tidal.create_playlist("My New Playlist", "Description")

# Search and add track
track = tidal.search_track("Mac Miller", "Hurt Feelings")
if track:
    tidal.add_tracks_to_playlist(playlist, [track])
```

## Setup

1. Run setup to authenticate:
   ```
   /skills/tidal-curator/setup
   ```

2. Or programmatically:
   ```python
   tidal = TidalCurator()
   url = tidal.start_auth()
   # User visits URL and logs in
   tidal.complete_auth()
   ```

## API Reference

### Authentication
- `is_authenticated()` → bool
- `start_auth()` → str (URL to visit)
- `complete_auth()` → bool

### Playlists
- `get_playlist(name)` → Playlist object
- `create_playlist(name, description)` → Playlist object
- `get_or_create_playlist(name, description)` → Playlist object

### Tracks
- `search_track(artist, title)` → Track object or None
- `search_tracks(queries)` → List[Track]
- `add_tracks_to_playlist(playlist, tracks)` → bool

### Utilities
- `get_user_info()` → Dict
- `get_playlist_tracks(playlist)` → List[Track]

---

## Supplementary Skills (absorbed into this skill)

### Tidal Dual Curator (`tidal-dual-curator`)

Daily music curation adding morning (9am) and evening (6pm) vibe tracks with artist context.

**What it does:**
- 🌅 Morning Vibe (9am): Confidence boosters, positive energy, hungry ambition
- 🌆 Evening Vibe (6pm): Chill storytelling, reflective, introspective
- Smart curation based on time of day
- Artist context with every track
- Rate limit safe (2 second delays)
- No duplicates

**Track Database:**
```
Morning: Aminé - SHINE, KIDS SEE GHOSTS - Reborn, Mac Miller - Paper Route
Evening: Horrorshow - The Rain, East Forest - Home, Mac Miller - Hurt Feelings
```

**Cron Setup:**
```bash
# Morning at 9am
0 9 * * * cd /path/to/curator && python dual_curator.py morning

# Evening at 6pm
0 18 * * * cd /path/to/curator && python dual_curator.py evening
```

---

### Tidal Playlist Creator (`tidal-playlist-creator`)

Create Tidal playlists from ListenBrainz data or custom track lists.

**Three Approaches:**
1. **Daily Curated Additions** (Recommended) — Add tracks gradually, rate-limit safe
2. **Direct Tidal API Creation (Bulk)** — Create playlists directly with tidalapi
3. **Export to Third-Party** — Generate files for TuneMyMusic/Soundiiz

**⚠️ Rate Limiting (CRITICAL):**
- HTTP 412 errors when adding tracks too fast
- Minimum 2 second delay between API calls
- Use `time.sleep(2)` between operations

---

### Tidal Recommendation (`tidal-recommendation`)

ListenBrainz-powered music recommendations with web search integration.

**Two Modes:**

1. **On-Demand Recommendations** — User asks for a vibe, Hermes analyzes + searches + recommends
2. **Scheduled Daily Curation** — Cron jobs for morning/evening automatic curation

**How it works:**
1. Fetches ListenBrainz history (user: your ListenBrainz username)
2. Analyzes taste profile (genres, artists, patterns)
3. Discovers new music via web search
4. Generates contextual recommendations
5. Adds tracks via tidal-curator base skill

---

## Related Skills

- `tidal-dual-curator` - Daily morning/evening curation (absorbed above)
- `tidal-playlist-creator` - Bulk playlist creation (absorbed above)
- `tidal-recommendation` - ListenBrainz recommendations (absorbed above)
