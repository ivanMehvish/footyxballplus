import discord
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import asyncio
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
API_KEY=os.getenv('API_KEY')
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send(f'HOLA FOOTBALL FANATIC!![{message.author}] Use $help for a list of available commands')
    
    if message.content.startswith('$help'):
        await message.channel.send('USE THE FOLLOWING COMMANDS TO INTERACT WITH ME!!\n $get_standings: Premier League real time standings\n $get_today_matches: List of scheduled matches today\n$get_matches: get upcoming fixtures for your team')

    if message.content.startswith('$get_matches'):
     await message.channel.send('Please enter the name of the team:')
     try:
        # Wait for the user's response
        user_response = await client.wait_for('message', timeout=100.0)
        team_name = user_response.content.lower()  # Convert team name to lowercase for case-insensitivity
        # Make a request to the Football Data API to get team information
        uri = f'https://api.football-data.org/v4/competitions/CL/teams'
        headers = {'X-Auth-Token': API_KEY}  # Replace 'YOUR_API_KEY' with your actual API key
        response = requests.get(uri, headers=headers)
        if response.status_code == 200:
            teams = response.json()['teams']
            print(teams)
            team_id = None
            # Find the ID of the selected team
            for team in teams:
                 if team_name in team['name'].lower() or any(alias.lower() == team_name for alias in team.get('shortName', [])):
                    team_id = team['id']
                    break
            if team_id is not None:
                # Make a request to the Football Data API to get match information for the selected team
                uri = f'https://api.football-data.org/v2/teams/{team_id}/matches?status=SCHEDULED'
                response = requests.get(uri, headers=headers)
                if response.status_code == 200:
                    # If the request is successful, print match information
                    matches = response.json()['matches']
                    if matches:
                        await message.channel.send(f'Upcoming matches for {team_name.capitalize()}:')
                        for match in matches:
                            home_team = match['homeTeam']['name']
                            away_team = match['awayTeam']['name']
                            match_time = match['utcDate']
                            await message.channel.send(f"{home_team} vs {away_team} - {match_time}")
                    else:
                        await message.channel.send(f"No upcoming matches found for {team_name.capitalize()}")
                else:
                    # If the request is unsuccessful, print an error message
                    await message.channel.send(f'Error: Unable to fetch match information. Status code: {response.status_code}')
            else:
                await message.channel.send('Team not found. Please make sure you entered the correct team name.')
        else:
            # If the request is unsuccessful, print an error message
            await message.channel.send(f'Error: Unable to fetch team information. Status code: {response.status_code}')
     except asyncio.TimeoutError:
        await message.channel.send('Timeout: No response received. Please try again.')
    if message.content.startswith('$get_standings'):
        # Replace 'YOUR_API_KEY' with your actual API key
        uri = 'https://api.football-data.org/v4/competitions/PL/standings'
        headers = {'X-Auth-Token': API_KEY}
        response = requests.get(uri, headers=headers)
        if response.status_code == 200:
            # Extract relevant information from the JSON response
            standings = response.json()['standings'][0]['table']
            
            # Format team positions as a table
            table = f"{'Position': <10}{'Team': <30}{'Points': <10}\n"
            for team in standings:
                table += f"{team['position']: <10}{team['team']['name']: <30}{team['points']: <10}\n"

            # Send the table to the Discord channel
            await message.channel.send(f'```\n{table}```')
        else:
            await message.channel.send(f'Error: Unable to fetch standings. Status code: {response.status_code}')
    if message.content.startswith('$get_today_matches'):
        # Replace 'YOUR_API_KEY' with your actual API key
        
        # Get today's date in the required format
        today_date = datetime.now().strftime('%Y-%m-%d')

        # Make a request to the Football Data API for today's matches
        uri = f'https://api.football-data.org/v4/matches'
        headers = {'X-Auth-Token': API_KEY}
        params = {'date':today_date}
        response = requests.get(uri, headers=headers, params=params)

        if response.status_code == 200:
            # Extract relevant information from the JSON response
            matches = response.json()['matches']
            
            # Format today's match list
            match_list = '\n'.join([f"{match['homeTeam']['name']} vs {match['awayTeam']['name']}" for match in matches])

            # Send the match list to the Discord channel
            await message.channel.send(f'Today\'s Matches:\n```\n{match_list}\n```')
        else:
            await message.channel.send(f'Error: Unable to fetch today\'s matches. Status code: {response.status_code}')
    
client.run(TOKEN)  # Replace 'YOUR_BOT_TOKEN' with your actual bot token


