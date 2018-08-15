# import
import discord
import time
import datetime
import platform
import sqlite3
		
# set size of string by adding spaces
def set_string_size(string, len1):
	len0 = len(string)
	if (len0 > len1):
		return string
	for a in range(len0, len1):
		string = string + " "
	return string

# info cmds
async def cmds_info(message, umsg, startup, owners, client, conn, cur):
	
	# args/variables
	args = umsg.split(' ')
	channel = message.channel
	member = message.author
	bot_version = '0.1.0'
	
	# help
	if (args[0].lower() == 'help'):
		
		# contextual help
		if (len(args) > 1):
			if (args[1].lower() == 'help'):
				embed = discord.Embed(title='Help Command', type='rich', description='**Usage:**\n`!help` - Shows the command list')
				await client.send_message(channel, content=None, embed=embed)
			elif (args[1].lower() == 'about'):
				embed = discord.Embed(title='About Command', type='rich', description='**Usage:**\n`!about` - Shows info about the bot')
				await client.send_message(channel, content=None, embed=embed)
			elif (args[1].lower() == 'info'):
				embed = discord.Embed(title='Info Command', type='rich', description='**Usage:**\n`!info` - Shows technical & bot information')
				await client.send_message(channel, content=None, embed=embed)
			elif (args[1].lower() == 'get'):
				embed = discord.Embed(title='Get Command', type='rich', description='**Usage:**\n`!get [level name/id]` - Retrieves the download link for a level with the given name or id')
				await client.send_message(channel, content=None, embed=embed)
			elif (args[1].lower() == 'browse'):
				embed = discord.Embed(title='Browse Command', type='rich', description='**Usage:**\n`!browse` - Lists all levels in default order (oldest-newest)\n`!browse <sort type>` - Lists all levels in a given order\n**Sort Types**\n`oldest` - Sorts oldest-newest\n`newest` - Sorts newest-oldest\n`rating high` - Sorts highest-lowest rating\n`rating low` - Sorts lowest-highest rating')
				await client.send_message(channel, content=None, embed=embed)
			elif (args[1].lower() == 'rate'):
				embed = discord.Embed(title='Rate Command', type='rich', description='**Usage:**\n`!rate [+/-] [level name/id]` - Rate a level with a given name or id')
				await client.send_message(channel, content=None, embed=embed)
			elif (args[1].lower() == 'upload'):
				embed = discord.Embed(title='Upload Command', type='rich', description='**Usage:**\n`!upload [level name]` - Upload a level and give it a specified name (must attach a .butt file)')
				await client.send_message(channel, content=None, embed=embed)
			elif (args[1].lower() == 'delete'):
				embed = discord.Embed(title='Delete Command', type='rich', description='**Usage:**\n`!delete [level name/id]` - Delete a level with a given name or id (provided you are a mod or the level owner)')
				await client.send_message(channel, content=None, embed=embed)
			elif (args[1].lower() == 'changelog'):
				embed = discord.Embed(title='Changelog Command', type='rich', description='**Usage:**\n`!changelog` - Displays the ESJBot changelog)')
				await client.send_message(channel, content=None, embed=embed)
			elif (args[1].lower() == 'todo'):
				embed = discord.Embed(title='To-Do Command', type='rich', description='**Usage:**\n`!todo` - Displays the current ESJBot to-do list)')
				await client.send_message(channel, content=None, embed=embed)
			else:
				await client.send_message(channel, 'That command does not exist!')
		
		# command list
		else:
			embed = discord.Embed(title='ESJBot Help', type='rich', description='Use `!help <command>` for usage')
			embed.add_field(name='Command List:',value='`help` `get` `browse` `upload` `rate` `delete` `about` `info` `changelog` `todo`',inline=False)
			await client.send_message(channel, content=None, embed=embed)
	
	# about
	if (args[0].lower() == 'about'):
		cur.execute('SELECT Count(*) FROM levels')
		t = cur.fetchone()
		level_count = list(t)
		embed = discord.Embed(title='About ESJBot', type='rich', description='Simple ESJ level browser, based on the original bot by Chratis\n\nCreated by Yuvira\n\n**Version:** ' + bot_version + '\n**Levels:** ' + str(level_count[0]) + '\n\n[GitHub Repo](https://github.com/Yuvira/ESJBot)')
		embed.set_thumbnail(url=client.user.avatar_url)
		await client.send_message(channel, content=None, embed=embed)

	# info
	if (args[0].lower() == 'info'):
		before = time.monotonic()
		await (await client.ws.ping())
		after = time.monotonic()
		ping = (after - before) * 1000
		cur.execute('SELECT Count(*) FROM levels')
		t = cur.fetchone()
		level_count = list(t)
		t = time.time() - startup
		uptime = str(int(t/86400)) + 'd '
		t = t % 86400
		uptime = uptime + str(int(t/3600)) + 'h '
		t = t % 3600
		uptime = uptime + str(int(t/60)) + 'm '
		t = t % 60
		uptime = uptime + str(int(t)) + 's'
		msg = "```============[ Technical Info ]============\n"
		msg += "::DiscordPY Version :: " + set_string_size(str(discord.__version__), 17) + "::\n"
		msg += "::Python Version    :: " + set_string_size(str(platform.python_version()), 17) + "::\n"
		msg += "::Websocket Ping    :: " + set_string_size("{0:.0f}ms".format(ping), 17) + "::\n"
		msg += "===============[ Bot Info ]===============\n"
		msg += "::Bot Version       :: " + set_string_size(str(bot_version), 17) + "::\n"
		msg += "::Levels            :: " + set_string_size(str(level_count[0]), 17) + "::\n"
		msg += "::Uptime            :: " + set_string_size(uptime, 17) + "::\n"
		msg += "==========================================```"
		await client.send_message(channel, msg)
		
	# changelog
	if (args[0].lower() == 'changelog'):
		f = open('changelog.txt', 'r')
		await client.send_message(channel, f.read())
		
	# to-do list
	if (args[0].lower() == 'todo'):
		f = open('todo.txt', 'r')
		await client.send_message(channel, f.read())
