from nba_api.stats.static import players
from nba_api.stats.endpoints.playerdashboardbyshootingsplits import PlayerDashboardByShootingSplits
from nba_api.stats.endpoints import playercareerstats
import pandas as pd
import time
import random

# Get all players.
players_df = pd.DataFrame(players.get_players())
player_id_list = sorted(players_df['id'].tolist())

for player_id in player_id_list:

	if player_id > 1520:

		print(f"Fetching player {player_id}.")

		career = playercareerstats.PlayerCareerStats(player_id=player_id)
		seasons = pd.unique(career.get_data_frames()[0]['SEASON_ID'])

		df = pd.DataFrame()

		for season in seasons:

			if int(season[:4]) > 1995:
				# Find shooting stats
				player = PlayerDashboardByShootingSplits(player_id=player_id, season=season, timeout=60)
				shooting_data = player.get_data_frames()

				if shooting_data[0].shape[0] > 0:
					tbl = shooting_data[0]
					tbl['player_id'] = player_id
					tbl['GROUP_VALUE'] = tbl['GROUP_VALUE'].str[:4]
					if df.shape[0] == 0:
						df = tbl
					else:
						df = pd.concat([df, tbl], ignore_index=True)

				# Generate random pause
				'''
				pause = random.randint(1, 3)
				print(f"Season {season} done. Sleeping for {pause} second.")
				time.sleep(pause)
				'''
				print(f"Stacking {season}.")

		df.to_csv('player_dashboard_by_shooting_splits_overall.csv', mode='a', encoding='utf-8', index=False, header=False)

		# Generate random pause
		'''
		pause = random.randint(3, 5)
		print(f"Player {player_id} done. Sleeping for {pause} second(s).")
		time.sleep(pause)
		'''
		print(f"Player {player_id} export completed.")