import discord
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

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
        await message.channel.send(f'Hello! {message.author}')

    if message.content.startswith('$get_matches_RM'):

        # Make a request to the Football Data API to get match information
        uri = 'https://api.football-data.org/v4/teams/86/matches?status=SCHEDULED'
        headers = {'X-Auth-Token': 'API_KEY'}  # Replace 'YOUR_API_KEY' with your actual API key
        response = requests.get(uri, headers=headers)
        # await message.channel.send(f'Response content: {response.text}')
        print(response.text)
        a=""
        if response.status_code == 200:
            # If the request is successful, print match information
            count=0
            for match in response.json()['matches']:
                a=a+'UPCOMING FOR REAL MADRID:' f'Match: {match["homeTeam"]["name"]} vs {match["awayTeam"]["name"]}'+'\n'
            await message.channel.send(a)
            
        else:
            # If the request is unsuccessful, print an error message
            await message.channel.send(f'Error: Unable to fetch match information. Status code: {response.status_code}')
   
    if message.content.startswith('$get_standings_CL'):
        # Replace 'YOUR_API_KEY' with your actual API key
        uri = 'https://api.football-data.org/v4/competitions/PD/standings'
        headers = {'X-Auth-Token': 'API_KEY'}
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
        api_key = 'YOUR_API_KEY'
        
        # Get today's date in the required format
        today_date = datetime.now().strftime('%Y-%m-%d')

        # Make a request to the Football Data API for today's matches
        uri = f'https://api.football-data.org/v4/matches'
        headers = {'X-Auth-Token': api_key}
        params = {'season': '2023', 'competition': 'CL'}
        response = requests.get(uri, headers=headers, params=params)
        print(response)
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

