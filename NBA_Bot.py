import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

from discord.ui import *

from nba_api.stats.endpoints import*
from nba_api.stats.static import*
import json
import requests

# Global Variables
channel = None
channel_id = 0
option1 = False
option2 = False
option3 = False
user_input = ""

#load the .env file
load_dotenv()
#setting prefix for commands
intents = discord.Intents.all()

client = commands.Bot(command_prefix = ".",intents = intents)
TOKEN = os.getenv('TOKEN')

#creating on ready command to let us know the bot is online 
@client.event
async def on_ready():
    print("Bot is online. ")
    my_task.start()

@client.command()
async def botInfo(ctx):
    botInfoMsg = ["Welcome to the NBA BOT, a bot built to get your info on the NBA!", "To start please send .team"]
    for item in botInfoMsg:
        await ctx.send(item)

# Bot menu
@client.command()
async def botMenu(ctx):
    global channel_id
    channel = discord.utils.get(ctx.guild.channels, name="general")
    channel_id = channel.id
    print(channel_id)

    def check(msg):
        return msg.channel == ctx.channel and msg.author == ctx.author

    menuOption1 = Button(label="Teams Stats", style = discord.ButtonStyle.red)
    menuOption2 = Button(label="Players Stats", style = discord.ButtonStyle.blurple)
    menuOption3 = Button(label="Current Games", style = discord.ButtonStyle.green)
        
    view = View(timeout=60)

    view.add_item(menuOption1)
    view.add_item(menuOption2)
    view.add_item(menuOption3)

    # Interaction function for when "Team Stats Button is pressed"
    async def button_callback1(interaction):
        global option1, option2, user_input
        await interaction.response.edit_message(content = "Enter team name", view = None)
        user_input = await client.wait_for("message", check=check, timeout = 60.0)

        user_input = user_input.content

        option1 = True
    
        print(user_input)
        
        view.stop()
    
    async def button_callback2(interaction):
        global option2, user_input
        
        await interaction.response.edit_message(content = "Enter player full name", view = None)
        user_input = await client.wait_for("message", check=check, timeout = 60.0)
        user_input = user_input.content

        option2 = True

        view.stop()

    async def button_callback3(interaction):
        await interaction.response.edit_message(content = "Current Games", view = None)
        view.stop()

    menuOption1.callback = button_callback1
    menuOption2.callback = button_callback2
    menuOption3.callback = button_callback3

    await ctx.send("Bot Menu", view = view)

    #Waiting for button to be pressed or if timeout is met
    await view.wait()

    print("Done button phase")

    return

@tasks.loop(seconds=5)
async def my_task():
    global option1, option2, channel
    channel = client.get_channel(channel_id)
    print(channel)
    print(type(channel))
    print("In task function")
    
    if option1 == True:
        print("Sending message")
        team_dict = teams.find_teams_by_full_name(user_input)
        resulting_team_id = team_dict[0]["id"]
        team_data = teamdetails.TeamDetails(team_id=resulting_team_id)
        
        team_data = team_data.get_json()
        team_data = json.loads(team_data)["resultSets"]

        teamInfoEmbed = discord.Embed(title=team_dict[0]["full_name"], description="Year Founded: "+str(team_dict[0]["year_founded"]))
        teamInfoEmbed.add_field(name = "NBA Championships", value = "", inline = False)
        
        for list in team_data[3]["rowSet"]:
            nbaChampsDescription = str(list[0])+" NBA Champions against "+list[1]
            teamInfoEmbed.add_field(name = "", value = nbaChampsDescription, inline = True)
        
        for x in range(4,6):
            champsInfoDescription = ""
            if x==4:
                subtitle = "Conference Championships"
            else:
                subtitle = "Division Championships"
            
            teamInfoEmbed.add_field(name = subtitle, value = "", inline = False)   

            for list in team_data[x]["rowSet"]:
                if list == team_data[x]["rowSet"][-1]:
                    champsInfoDescription = champsInfoDescription + str(list[0])
                else:
                    champsInfoDescription = champsInfoDescription + str(list[0])+", "

            teamInfoEmbed.add_field(name = "", value = champsInfoDescription, inline = True)

        await channel.send(embed=teamInfoEmbed)
        
        for x in range(2):
            count = 0
            stop = 25

            if x == 0:
                num_total_players = len(team_data[6]["rowSet"])
                embedDescription = "**HOF players to play with this franchise**"
            else:
                num_total_players = len(team_data[7]["rowSet"])
                embedDescription = "**Players retired by this franchise**"
            
            while count < num_total_players:
                
                if (stop-count) < 25 or num_total_players < 25:
                    stop = num_total_players
                else:
                    stop = count+25

                if count != 0:
                    embedDescription = ""
                
                playerInfoEmbed = discord.Embed(title="", description=embedDescription)

                for num in range(count, stop):
                    if x == 0:
                        list = team_data[6]["rowSet"][num]
                        player_description = """```Position: {playerPosition}
Played for {teamName} for: {years}
                        ```""".format(playerPosition = list[2], teamName = team_dict[0]["full_name"], years = list[4])

                    else:
                        list = team_data[7]["rowSet"][num]
                        player_description = """```Position: {playerPosition}
Number retired: #{playerNum}
Played for {teamName} for: {years}
Declared retirement in the year: {retirementYear}
                        ```""".format(playerPosition = list[2], playerNum = str(list[3]), teamName = team_dict[0]["full_name"], years = list[4], retirementYear = list[5])
                    
                    player_name = list[1]

                    playerInfoEmbed.add_field(name = player_name, value = player_description, inline = True)

                    count += 1

                await channel.send(embed=playerInfoEmbed)

        
        option1 = False

    elif option2 == True:
        player_dict = players.find_players_by_full_name(user_input)
        player_name = player_dict[0]["full_name"]
        

        resulting_player_id = player_dict[0]["id"]
        career_data = playercareerstats.PlayerCareerStats(player_id=resulting_player_id)

        regular_season_data = career_data.season_totals_regular_season.get_json()
        regular_season_data = json.loads(regular_season_data)["data"]

        regular_season_rankings = career_data.season_rankings_regular_season.get_json()
        regular_season_rankings = json.loads(regular_season_rankings)["data"]

        post_season_data = career_data.season_totals_post_season.get_json()
        post_season_data = json.loads(post_season_data)["data"]

        post_season_rankings = career_data.season_rankings_post_season.get_json()
        post_season_rankings = json.loads(post_season_rankings)["data"]


        num_seasons = len(regular_season_data)
        

        for season in range(num_seasons):

            playerInfoEmbed = discord.Embed(title=player_name, description=regular_season_data[season][1])

            for x in range(4):
                try:

                    if x == 0:
                        field_name = "Regular Season Stats"
                        list = regular_season_data[season]
                    elif x == 1:
                        field_name = "Regular Season Rankings"
                        list = regular_season_rankings[season]
                        
                    elif x == 3:
                        field_name = "Post Season Stats"
                        list = post_season_data[season]
                    else:
                        field_name = "Post Season Rankings"
                        list = post_season_rankings[season]
                
                except:
                    player_description = "```N/A```"

                else:
                
                    if x%2 == 0:
                        player_total_pts = list[-1]

                    else:
                        player_total_pts = list[-2]

                    player_description = """```Games Played: {gamesPlayed}
Games Started: {gamesStarted} 
Minutes Played: {minsPlayed}
Field Goals Made: {fgm}
Field Goals Attempted: {fga}
Field Goal %: {fgp}
3-PT Made: {fg3m}
3-PT Attempted: {fg3a}
3-PT %: {fg3p}
Free Throws Made: {ftm}
Free Throws Attempted: {fta}
Free Throws %: {ftp}
Total Rebounds: {rebounds}
Total Assists: {assists}
Total Steals: {steals}
Total Blocks: {blocks}
Total Points: {totalPts}
                    ```""".format(gamesPlayed = list[6], gamesStarted = list[7], minsPlayed = list[8], fgm = list[9], fga = list[10], fgp = list[11], fg3m = list[12], fg3a = list[13], fg3p = list[14], ftm = list[15], fta = list[16], ftp = list[17], rebounds = list[20], assists = list[21], steals = list[22], blocks = list[23], totalPts = list[-2])
                
                playerInfoEmbed.add_field(name = field_name, value = player_description, inline = True)

            await channel.send(embed=playerInfoEmbed) 

        option2 = False

client.run(TOKEN)
