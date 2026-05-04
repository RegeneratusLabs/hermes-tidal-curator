"""
Tidal Curator - Base Skill
Provides core Tidal API functionality for other skills to use
"""

import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

try:
    import tidalapi
    TIDAL_AVAILABLE = True
except ImportError:
    TIDAL_AVAILABLE = False
    tidalapi = None


@dataclass
class Track:
    """Simple track representation"""
    id: int
    name: str
    artist: str
    album: str
    duration: int
    
    @classmethod
    def from_tidal(cls, tidal_track) -> 'Track':
        return cls(
            id=tidal_track.id,
            name=tidal_track.name,
            artist=tidal_track.artist.name if hasattr(tidal_track.artist, 'name') else str(tidal_track.artist),
            album=tidal_track.album.name if hasattr(tidal_track, 'album') and hasattr(tidal_track.album, 'name') else "Unknown",
            duration=getattr(tidal_track, 'duration', 0)
        )


class TidalCurator:
    """
    Base skill for Tidal integration.
    Other skills import and use this to interact with Tidal.
    """
    
    def __init__(self, hermes_home: Path = None):
        self.hermes_home = hermes_home or Path.home() / ".hermes"
        self.session_file = self.hermes_home / "tidal_session.json"
        self.api_delay = 2  # Seconds between API calls
        self._session = None
        
        if not TIDAL_AVAILABLE:
            raise ImportError("tidalapi not installed. Run: pip install tidalapi")
    
    # ==================== AUTHENTICATION ====================
    
    def is_authenticated(self) -> bool:
        """Check if we have a valid Tidal session"""
        if not self.session_file.exists():
            return False
        
        try:
            session = tidalapi.Session()
            session.load_session_from_file(self.session_file)
            return session.check_login()
        except:
            return False
    
    def start_auth(self) -> str:
        """
        Start OAuth flow. Returns URL for user to visit.
        
        Usage:
            url = tidal.start_auth()
            print(f"Visit: {url}")
            # User visits URL and logs in
            tidal.complete_auth()
        """
        self._session = tidalapi.Session()
        login, future = self._session.login_oauth()
        self._auth_future = future
        return login.verification_uri_complete
    
    def complete_auth(self, timeout: int = 300) -> bool:
        """
        Complete authentication after user visits URL.
        
        Args:
            timeout: Seconds to wait for auth (default 5 minutes)
            
        Returns:
            True if authenticated successfully
        """
        if not hasattr(self, '_auth_future'):
            raise RuntimeError("start_auth() must be called first")
        
        try:
            self._auth_future.result(timeout=timeout)
            if self._session.check_login():
                self._session.save_session_to_file(self.session_file)
                return True
        except Exception as e:
            print(f"Auth error: {e}")
        
        return False
    
    def _get_session(self) -> Optional[tidalapi.Session]:
        """Get active session (internal use)"""
        if self._session and self._session.check_login():
            return self._session
        
        if self.session_file.exists():
            try:
                session = tidalapi.Session()
                session.load_session_from_file(self.session_file)
                if session.check_login():
                    self._session = session
                    return session
            except:
                pass
        
        return None
    
    def get_user_info(self) -> Optional[Dict]:
        """Get current user info"""
        session = self._get_session()
        if not session:
            return None
        
        user = session.user
        return {
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}".strip(),
            'email': getattr(user, 'email', None)
        }
    
    # ==================== PLAYLISTS ====================
    
    def get_playlist(self, name: str) -> Optional[Any]:
        """Find playlist by name"""
        session = self._get_session()
        if not session:
            return None
        
        playlists = session.user.playlists()
        for p in playlists:
            if p.name == name:
                return p
        return None
    
    def create_playlist(self, name: str, description: str = "") -> Optional[Any]:
        """Create new playlist"""
        session = self._get_session()
        if not session:
            return None
        
        try:
            playlist = session.user.create_playlist(name, description)
            time.sleep(self.api_delay)
            return playlist
        except Exception as e:
            print(f"Error creating playlist: {e}")
            return None
    
    def get_or_create_playlist(self, name: str, description: str = "") -> Optional[Any]:
        """Get existing playlist or create new one"""
        existing = self.get_playlist(name)
        if existing:
            return existing
        return self.create_playlist(name, description)
    
    def get_playlist_tracks(self, playlist) -> List[Track]:
        """Get all tracks in a playlist"""
        try:
            tidal_tracks = playlist.tracks()
            return [Track.from_tidal(t) for t in tidal_tracks]
        except Exception as e:
            print(f"Error getting tracks: {e}")
            return []
    
    # ==================== TRACKS ====================
    
    def search_track(self, artist: str, title: str, limit: int = 5) -> Optional[Track]:
        """
        Search for a specific track.
        
        Args:
            artist: Artist name
            title: Track title
            limit: Number of search results to check
            
        Returns:
            Track object if found, None otherwise
        """
        session = self._get_session()
        if not session:
            return None
        
        query = f"{artist} {title}"
        
        try:
            results = session.search(query, models=[tidalapi.media.Track], limit=limit)
            time.sleep(self.api_delay)
            
            if results and results.get("tracks"):
                # Return first match (could add fuzzy matching here)
                return Track.from_tidal(results["tracks"][0])
        except Exception as e:
            print(f"Search error: {e}")
        
        return None
    
    def search_tracks(self, queries: List[Dict[str, str]]) -> List[Track]:
        """
        Search for multiple tracks.
        
        Args:
            queries: List of {'artist': str, 'title': str} dicts
            
        Returns:
            List of found Track objects
        """
        found = []
        for q in queries:
            track = self.search_track(q['artist'], q['title'])
            if track:
                found.append(track)
        return found
    
    def add_tracks_to_playlist(self, playlist, tracks: List[Track]) -> Dict[str, any]:
        """
        Add tracks to a playlist.
        
        Args:
            playlist: Tidal playlist object
            tracks: List of Track objects to add
            
        Returns:
            Dict with 'success', 'added', 'failed' counts
        """
        if not tracks:
            return {'success': True, 'added': 0, 'failed': 0}
        
        added = 0
        failed = 0
        
        for track in tracks:
            try:
                playlist.add([track.id])
                added += 1
                time.sleep(self.api_delay)
            except Exception as e:
                print(f"Error adding track {track.name}: {e}")
                failed += 1
        
        return {
            'success': failed == 0,
            'added': added,
            'failed': failed
        }
    
    def add_track_by_search(self, playlist, artist: str, title: str) -> bool:
        """
        Convenience method: search for track and add to playlist.
        
        Returns:
            True if successful
        """
        track = self.search_track(artist, title)
        if track:
            result = self.add_tracks_to_playlist(playlist, [track])
            return result['success'] and result['added'] > 0
        return False


# CLI for setup/testing
if __name__ == "__main__":
    import sys
    
    curator = TidalCurator()
    
    if len(sys.argv) < 2:
        print("Tidal Curator - Base Skill")
        print("\nUsage:")
        print("  python curator.py auth          # Authenticate with Tidal")
        print("  python curator.py status        # Check auth status")
        print("  python curator.py test          # Test adding a track")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "auth":
        if curator.is_authenticated():
            user = curator.get_user_info()
            print(f"Already authenticated as {user['name']}")
        else:
            url = curator.start_auth()
            print(f"Visit this URL to authenticate:\n{url}\n")
            print("Waiting for authorization...")
            if curator.complete_auth():
                user = curator.get_user_info()
                print(f"✓ Authenticated as {user['name']}")
            else:
                print("✗ Authentication failed")
    
    elif cmd == "status":
        if curator.is_authenticated():
            user = curator.get_user_info()
            print(f"✓ Authenticated as {user['name']}")
        else:
            print("✗ Not authenticated")
            print("Run: python curator.py auth")
    
    elif cmd == "test":
        if not curator.is_authenticated():
            print("Not authenticated. Run: python curator.py auth")
            sys.exit(1)
        
        # Test: create playlist and add track
        playlist = curator.get_or_create_playlist(
            "Hermes Test Playlist",
            "Testing Tidal Curator skill"
        )
        print(f"Playlist: {playlist.name}")
        
        track = curator.search_track("Mac Miller", "Hurt Feelings")
        if track:
            print(f"Found: {track.artist} - {track.name}")
            result = curator.add_tracks_to_playlist(playlist, [track])
            print(f"Added: {result['added']}, Failed: {result['failed']}")
        else:
            print("Track not found")
    
    else:
        print(f"Unknown command: {cmd}")
