# Import necessary libraries
from nba_api.stats.static import teams
from tabulate import tabulate

# Function to retrieve all NBA teams
def get_all_nba_teams():
    # Get all NBA teams from the nba_api
    all_teams = teams.get_teams()
    return all_teams

# Function to print NBA teams in a table format
def print_teams(table):
    # Define the headers for the table
    headers = ['ID', 'Full Name', 'Abbreviation', 'City', 'Conference']
    # Print the table using the tabulate library
    print(tabulate(table, headers, tablefmt='github'))

# Get all NBA teams
all_nba_teams = get_all_nba_teams()

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

# Print the NBA team table
print_teams(team_table)