# import
import discord
import time
import random
import importlib
import sqlite3
import datetime
import asyncio

# modules
import cmds_info
import cmds_levels

# client
client = discord.Client()

# database connection/cursor
conn = sqlite3.connect('levels.db')
cur = conn.cursor()

# startup variables
prefix = '!'
token = 'token'

# startup time
startup = time.time()

# define important people
owners = ['188663897279037440'] # Yuvira
moderators = ['139526577850548225', '188663897279037440', '275262109980557312'] # thegamedesigner, Yuvira, Colon

# message received
@client.event
async def on_message(message):
	
	# if message received from user
	if (message.author.bot == False):
		
		# shorten variable name
		umsg = message.content
		
		# check prefix
		if (umsg.startswith(prefix)):
			
			# remove prefix
			umsg = umsg[1:]
			
			# shutdown
			if (message.author.id in owners):
				if (umsg.lower() == 'shutdown'):
					await client.send_message(message.channel, '*Shutting down...*')
					conn.close()
					await client.logout()
					sys.exit(0)
			
			# command lists
			await cmds_info.cmds_info(message, umsg, startup, owners, client, conn, cur)
			await cmds_levels.cmds_levels(message, umsg, moderators, client, conn, cur)
			
			# reload module
			if (message.author.id in owners):
				args = umsg.split(' ')
				if (args[0].lower() == 'reload' and len(args) == 2):
					try:
						if (args[1].lower() == 'info'):
							importlib.reload(cmds_info)
						elif (args[1].lower() == 'levels'):
							importlib.reload(cmds_levels)
						else:
							raise Exception
						await client.send_message(message.channel, 'Reloaded ' + args[1] + ' command module successfully!')
					except:
						await client.send_message(message.channel, 'Failed to load module!')

# startup
@client.event
async def on_ready():
	print('Logged in as:')
	print(client.user.name)
	print(client.user.id)
	print('------')
	cur.execute('SELECT Count(*) FROM levels')
	t = cur.fetchone()
	level_count = list(t)
	await client.change_presence(game=discord.Game(type=0, name=prefix+'help | With '+str(level_count[0])+' levels!'), status=None, afk=False)

# run
random.seed(time.time())
client.run(token)
