from nba_api.stats.endpoints import*
from nba_api.stats.static import*
import json
import requests

def format_player_dict(player_dict):
	#Why must we call the 0 index for the dictionary key to work?? ASK!!
	print("Full name:", player_dict[0]["full_name"])
	print("Status:", player_dict[0]["is_active"])

def format_team_dict(team_dict):
	print("Name:", team_dict[0]["full_name"])
	print("City:", team_dict[0]["city"])
	print("State:", team_dict["state"])
	print("Year founded:", team_dict["year_founded"])

def main(): 
	print ("-----------NBA Bot Menu---------")

	menu_option = int(input("1. Teams\n2. Players\n3. Games Today\nUsing numbers select an option: "))
	if (menu_option == 1):
		team_city = input("Enter the city of the team you want to search for: ")
		team_dict = teams.find_teams_by_city(team_city)
		format_team_dict(team_dict)

	elif (menu_option == 2):
		player_name = input("Please enter player first name you would like to search for: ")
		player_dict = players.find_players_by_full_name(player_name)
		format_player_dict(player_dict)

main()

r = requests.get(f'https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json')
data = json.loads(r.text)
##print(data)

#Gets into the games LIST
data = data["scoreboard"]["games"]

for count,game in enumerate(data):
	print("Game",count+1,"-",game["gameCode"][9:],"@",game["gameStatusText"])

	

#pretty_json = json.dumps(data, indent=4)

#print(pretty_json)

