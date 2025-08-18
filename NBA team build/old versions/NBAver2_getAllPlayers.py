# Import necessary libraries
from nba_api.stats.static import players
from tabulate import tabulate

# Function to retrieve all NBA players
def get_all_nba_players():
    # Get all NBA players from the nba_api
    all_players = players.get_players()
    return all_players

# Function to print NBA players in a table format
def print_players(table):
    # Define the headers for the table
    headers = ['ID', 'Full Name', 'First Name', 'Last Name', 'Active Status']
    # Print the table using the tabulate library
    print(tabulate(table, headers, tablefmt='github'))

# Get all NBA players
all_nba_players = get_all_nba_players()

# Create a table with NBA player information
player_table = [
    # Extract relevant information from each player dictionary
    [player['id'], 
     player['full_name'], 
     player['first_name'], 
     player['last_name'], 
     'Active' if player['is_active'] else 'Not Active'] 
     for player in all_nba_players
]

# Print the NBA player table
print_players(player_table)