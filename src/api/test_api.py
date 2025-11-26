from src.api.teams import download_team_logos, fetch_all_teams

# TEST: Fetch teams
teams = fetch_all_teams()
print(f"Fetched {len(teams)} teams (FBS + FCS)")

# TEST: Download logos
download_team_logos()

print("All tasks complete.")
