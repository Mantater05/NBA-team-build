# Import necessary libraries
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import CommonPlayerInfo
import sqlite3

# Function to retrieve all NBA players
def get_all_nba_players():
    # Get all NBA players from the nba_api
    return players.get_players()

# Function to retrieve all NBA teams
def get_all_nba_teams():
    # Get all NBA teams from the nba_api
    return teams.get_teams()

def add_to_db(player_id, 
              player_name, 
              player_num, 
              team_name, 
              team_ab, 
              position, 
              height, 
              weight, 
              country, 
              is_active):
    
    insert = '''
        INSERT INTO Players (
            player_id, 
            full_name, 
            jersey_num, 
            team_name, 
            team_ab, 
            pos, 
            height, 
            weight, 
            country, 
            is_active
        )
                                    
        VALUES (?,?,?,?,?,?,?,?,?,?)'''
    
    try:
        myCursor.execute(insert, 
            [
                player_id,
                player_name, 
                player_num, 
                team_name, 
                team_ab, 
                position, 
                height, 
                weight, 
                country, 
                is_active
            ]
        ) 
    
        db.commit()

    except sqlite3.IntegrityError:
        pass

def get_player_id(player_table):
    # Extract player IDs into a list
    return([player[0] for player in player_table])

def get_player_info(player_ids, player_table):
    # Loop through each player ID to fetch detailed information
    for player_id in player_ids:
        print(f"Fetching info for player ID: {player_id}")
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
        #is_active = 'Active' if player_info_df.at[0, 'TO_YEAR'] >= pd.Timestamp.now().year else 'Not Active'
        is_active = next(iter([player[1] for player in player_table if player[0] == player_id]))

        add_to_db(player_id, 
                player_name, 
                player_num, 
                team_name, 
                team_ab, 
                position, 
                height, 
                weight, 
                country, 
                is_active)

def main():
    # Get all NBA players
    all_nba_players = get_all_nba_players()
    all_nba_teams = get_all_nba_teams()

    # Create a table with NBA player information
    player_table = [
        [
            player['id'],
            'Active' if player['is_active'] else 'Not Active'
        ]
        for player in all_nba_players
    ]

    # Create a table with NBA team information
    team_table = [
        # Extract relevant information from each team dictionary
        [team['id'], 
        team['full_name'], 
        team['abbreviation'], 
        team['nickname'], 
        team['city'],
        team['state'],
        team['year_founded']] 
        for team in all_nba_teams
]

    player_ids = get_player_id(player_table)
    get_player_info(player_ids, player_table)
    print('Command executed.')

#myCursoe global
with sqlite3.connect('nba_info.db') as db:
    myCursor = db.cursor()

main()
