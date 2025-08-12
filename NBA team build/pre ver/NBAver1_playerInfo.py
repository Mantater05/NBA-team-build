from nba_api.stats.endpoints import CommonPlayerInfo
import pandas as pd
import datetime
from tabulate import tabulate

# Set display options to show all rows and columns
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns

# Define a list of player IDs
player_ids = ["977"]

# Create a list to store player information
player_info_list = []

# Loop through each player ID
for player_id in player_ids:
    # Create an instance of the CommonPlayerInfo endpoint
    player_info = CommonPlayerInfo(player_id=player_id)

    # Get the player's information data frame
    player_info_df = player_info.get_data_frames()[0]

    # Extracting specific information from the DataFrame using .at[]
    player_name = player_info_df.at[0, 'DISPLAY_FIRST_LAST']
    player_num = player_info_df.at[0, 'JERSEY']
    team_name = player_info_df.at[0, 'TEAM_NAME']
    team_ab = player_info_df.at[0, 'TEAM_ABBREVIATION']
    position = player_info_df.at[0, 'POSITION']
    height = player_info_df.at[0, 'HEIGHT']
    weight = player_info_df.at[0, 'WEIGHT']
    country = player_info_df.at[0, 'COUNTRY']
    is_active = not (datetime.datetime.now().year > player_info_df.at[0, 'TO_YEAR'])

    # Append the player's information to the list
    player_info_list.append([
        player_name,
        player_num,
        f"{team_name} ({team_ab})",
        position,
        height,
        f"{weight} lbs",
        country,
        "Yes" if is_active else "No"
    ])

# Print the table
print("Player Information:")
print(tabulate(player_info_list, headers=["Player", "Number", "Team", "Position", "Height", "Weight", "Country", "Active"], tablefmt="github"))