import requests
import os

API_URL = "https://api.opendota.com/api"

def fetch_recent_matches(player_id, limit=1):
    """Fetch the recent match history for a given player."""
    url = f"{API_URL}/players/{player_id}/recentMatches"
    response = requests.get(url)
    if response.status_code == 200:
        return [match["match_id"] for match in response.json()[:limit]]
    else:
        print(f"Failed to fetch recent matches for player {player_id}: {response.status_code}")
        return []

def fetch_match_details(match_id):
    """Fetch match details by match ID."""
    url = f"{API_URL}/matches/{match_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch match details for match ID {match_id}: {response.status_code}")
        return None
