from nba_api.stats.static import players
from nba_api.stats.endpoints.playerdashboardbyshootingsplits import PlayerDashboardByShootingSplits
from nba_api.stats.endpoints.playerdashptshotdefend import PlayerDashPtShotDefend
from nba_api.stats.endpoints.playercareerstats import PlayerCareerStats
import pandas as pd
import time
import random
import os.path

# Get all players.
players_df = pd.DataFrame(players.get_players())
player_id_list = sorted(players_df['id'].tolist())

def extractShootingData(threshold, type):

	for player_id in player_id_list:

		if player_id > threshold:

			print(f"Fetching player {player_id}.")

			# Get player's seasons
			career = PlayerCareerStats(player_id=player_id)
			seasons = pd.unique(career.get_data_frames()[0]['SEASON_ID'])

			# Initialize empty dataframe
			df = pd.DataFrame()

			# Iterate through seasons
			for season in seasons:
				# If season after 1995
				if int(season[:4]) > 1995:
					# Find shooting stats
					player = PlayerDashboardByShootingSplits(player_id=player_id, season=season, timeout=60)
					shooting_data = player.get_data_frames()
					# Shooting table dictionary
					table_dict = {
						"overall": 0, 
						"shot_distance_5ft": 1, 
						"shot_distance_8ft": 2, 
						"shot_area": 3, 
						"assisted_shot": 4, 
						"shot_type_summary": 5, 
						"shot_type_detail": 6,
						"assisted_by": 7
					}

					if shooting_data[0].shape[0] > 0:
						tbl = shooting_data[table_dict[type]]
						tbl['PLAYER_ID'] = player_id
						tbl['SEASON'] = season[:4]
						if df.shape[0] == 0:
							df = tbl
						else:
							df = pd.concat([df, tbl], ignore_index=True)

					print(f"Stacking {season}.")

			filename = f'player_dashboard_by_shooting_splits_{type}.csv'

			if os.path.isfile(filename):
				df.to_csv(filename, mode='a', encoding='utf-8', index=False, header=False)
			else:
				df.to_csv(filename, mode='w', encoding='utf-8', index=False, header=True)
				
			print(f"Player {player_id} export completed.")

def extractPlayerCareerStats(threshold, df_list):
	# Iterate through each player 
	for player_id in player_id_list:
		# Subset players based on their player_id
		if player_id > threshold:
			# Find player career stats
			print(f"Fetching player {player_id}.")
			career = PlayerCareerStats(player_id=player_id, per_mode36='PerGame')
			career_data = career.get_data_frames()
			# Initialize tables dictionary
			tbl_dict = [
				{'type': 'regular', 'filename': 'regular_season', 'index': 0},
				{'type': 'post', 'filename': 'post_season', 'index': 2},
				{'type': 'allstar', 'filename': 'all_star_season', 'index': 4}
			]
			# Iterate through each table
			for tbl in tbl_dict:
				# If table is among list of tables to export
				if tbl['type'] in df_list:
					# Fetch table by index and generate file name
					df = career_data[tbl['index']]
					df['SEASON_ID'] = df['SEASON_ID'].astype(str).str[:4]
					filename = f"career_totals_{tbl['filename']}.csv"
					# Export data to file
					if os.path.isfile(filename):
						df.to_csv(filename, mode='a', encoding='utf-8', index=False, header=False)
					else:
						df.to_csv(filename, mode='w', encoding='utf-8', index=False, header=True)

#extractShootingData(threshold=55, type='shot_distance_8ft')
extractPlayerCareerStats(threshold=0, df_list=['regular', 'post', 'allstar'])