# import
import discord
import time
import datetime
import random
import string
import json

# parse time data into text
def get_date(date):
	args = date.split('-')
	str = ''
	if args[1] == '01': str='Jan'
	elif args[1] == '02': str='Feb'
	elif args[1] == '03': str='Mar'
	elif args[1] == '04': str='Apr'
	elif args[1] == '05': str='May'
	elif args[1] == '06': str='Jun'
	elif args[1] == '07': str='Jul'
	elif args[1] == '08': str='Aug'
	elif args[1] == '09': str='Sept'
	elif args[1] == '10': str='Oct'
	elif args[1] == '11': str='Nov'
	elif args[1] == '12': str='Dec'
	if (args[2].startswith('0')): args[2]=args[2][1]
	str = str + ' ' + args[2] + ', ' + args[0] + ' at ' + args[3] + ':' + args[4]
	return str

# generate level id
def gen_id(cur):
	while (True):
		id = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(4))
		t = (id,)
		cur.execute('SELECT * FROM levels WHERE id=?', t)
		level = cur.fetchone()
		if (level == None):
			return id

# level cmds
async def cmds_levels(message, umsg, moderators, client, conn, cur):
	
	# args/variables
	args = umsg.split(' ')
	channel = message.channel
	member = message.author
	
	# get
	if (args[0].lower() == 'get'):
		
		# checks
		if (len(args) > 1):
			
			# try checking by id first
			search = umsg[4:].strip()
			s = (search,)
			cur.execute('SELECT * FROM levels WHERE id=?', s)
			t = cur.fetchone()
			if (t == None):
				
				# check by name
				cur.execute('SELECT Count(*) FROM levels WHERE name=? COLLATE NOCASE', s)
				n = cur.fetchone()
				
				# no level found, skip
				if (n[0] == 0):
					await client.send_message(channel, "Couldn't find a level with that name or id!")
					
				# multiple levels found, list
				elif (n[0] > 1):
					msg = 'Page 1\nMultiple levels share this name. Please use `!get [id]` to get the level you want'
					cur.execute('SELECT * FROM levels WHERE name=? COLLATE NOCASE LIMIT 10', s)
					for a in range(0,10):
						t = cur.fetchone()
						if (t != None):
							owner = await client.get_user_info(t[3])
							msg = msg + '\n' + str(a+1) + '. [`' + t[0] + '`] **' + t[4] + '** by **' + owner.display_name + '**'
						else:
							break
					embed = discord.Embed(title='Level List', type='rich', description=msg)
					await client.send_message(channel, content=None, embed=embed)
					t = None
				
				# one level found, return
				else: 
					cur.execute('SELECT * FROM levels WHERE name=? COLLATE NOCASE', s)
					t = cur.fetchone()
			
			# result exists, show level
			if (t != None):
				rating = (t[0], '+')
				cur.execute('SELECT Count(*) FROM ratings WHERE level=? AND rating=?', rating)
				upvotes = cur.fetchone()
				rating = (t[0], '-')
				cur.execute('SELECT Count(*) FROM ratings WHERE level=? AND rating=?', rating)
				downvotes = cur.fetchone()
				owner = await client.get_user_info(t[3])
				embed = discord.Embed(title=t[4], type='rich', description=t[5] + '\n\n[Download](' + t[6] + ')\n\n**Creator:** ' + owner.display_name + '\n**Rating:** ' + str(upvotes[0]) + ':thumbsup: ' + str(downvotes[0]) + ':thumbsdown:\n**ID:** `' + t[0] + '`\n\n Uploaded on ' + get_date(t[8]))
				await client.send_message(channel, content=None, embed=embed)
			
		else:
			await client.send_message(channel, 'You need to specify a level to get!')
		
	# browse
	if (args[0].lower() == 'browse'):
		
		# get and set some info first
		page = 1
		cur.execute('SELECT Count(*) FROM levels')
		t = cur.fetchone()
		limit = int((t[0]/10)+1)
		pm = None
		
		# generate list
		msg = 'Page ' + str(page)
		cur.execute('SELECT * FROM levels LIMIT 10 OFFSET ' + str((page-1)*10))
		for a in range(0,10):
			t = cur.fetchone()
			if (t != None):
				owner = await client.get_user_info(t[3])
				msg = msg + '\n' + str(a+1+((page-1)*10)) + '. [`' + t[0] + '`] **' + t[4] + '** by **' + owner.display_name + '**'
			else:
				break
		
		# check pm (can't reset reactions / can't paginate)
		if (message.server == None):
			pm = "Can't paginate in DMs, please use a server for multiple pages"
		
		# send list
		embed = discord.Embed(title='Level List', type='rich', description=msg)
		table = await client.send_message(channel, content=pm, embed=embed)
		
		# only paginate if more than one page of results
		if (message.server != None and limit > 1):
			
			# add reactions
			await client.add_reaction(table, '⏪')
			await client.add_reaction(table, '⏩')
			
			# pagination
			while (True):
				
				# handle reaction
				res = await client.wait_for_reaction(['⏪', '⏩'], user=member, timeout=60, message=table)
				if (res == None):
					break
				else:
					if (res.reaction.emoji == '⏪'):
						await client.remove_reaction(table, '⏪', member)
						if (page > 1):
							page -= 1
					elif (res.reaction.emoji == '⏩'):
						await client.remove_reaction(table, '⏩', member)
						if (page < limit):
							page += 1
				
				# generate new list and update existing
				msg = 'Page ' + str(page)
				cur.execute('SELECT * FROM levels LIMIT 10 OFFSET ' + str((page-1)*10))
				for a in range(0,10):
					t = cur.fetchone()
					if (t != None):
						owner = await client.get_user_info(t[3])
						msg = msg + '\n' + str(a+1+((page-1)*10)) + '. [`' + t[0] + '`] **' + t[4] + '** by **' + owner.display_name + '**'
					else:
						break
				embed = discord.Embed(title='Level List', type='rich', description=msg)
				await client.edit_message(table, new_content=None, embed=embed)
	
	# rate
	if (args[0].lower() == 'rate'):
		
		# checks
		if (len(args) > 2):
			if (args[1] == '+' or args[1] == '-'):
				
				# try checking by id first
				search = umsg[7:].strip()
				s = (search,)
				cur.execute('SELECT * FROM levels WHERE id=?', s)
				t = cur.fetchone()
				if (t == None):
					
					# check by name
					cur.execute('SELECT Count(*) FROM levels WHERE name=? COLLATE NOCASE', s)
					n = cur.fetchone()
					
					# no level found, skip
					if (n[0] == 0):
						await client.send_message(channel, "Couldn't find a level with that name or id!")
						
					# multiple levels found, list
					elif (n[0] > 1):
						msg = 'Page 1\nMultiple levels share this name. Please use `!rate [+/-] [id]` to get the level you want'
						cur.execute('SELECT * FROM levels WHERE name=? COLLATE NOCASE LIMIT 10', s)
						for a in range(0,10):
							t = cur.fetchone()
							if (t != None):
								owner = await client.get_user_info(t[3])
								msg = msg + '\n' + str(a+1) + '. [`' + t[0] + '`] **' + t[4] + '** by **' + owner.display_name + '**'
							else:
								break
						embed = discord.Embed(title='Level List', type='rich', description=msg)
						await client.send_message(channel, content=None, embed=embed)
						t = None
					
					# one level found, return
					else: 
						cur.execute('SELECT * FROM levels WHERE name=? COLLATE NOCASE', s)
						t = cur.fetchone()
				
				# result exists, rate level
				if (t != None):
					
					# delete existing rating
					rating = (t[0], member.id)
					cur.execute('DELETE FROM ratings WHERE level=? AND user=?', rating)
					
					# commit new rating
					rating = (t[0], member.id, args[1])
					cur.execute('INSERT INTO ratings VALUES (?,?,?)', rating)
					await client.send_message(channel, 'Level rated!')
				
			else:
				await client.send_message(channel, 'You need to specify a rating (+ or -)!')
		else:
			await client.send_message(channel, 'Insufficient arguments!')
	
	# upload
	if (args[0].lower() == 'upload'):
		
		# confirm file being uploaded
		if (len(message.attachments) > 0):
			if (len(message.attachments) < 2):
				att = message.attachments[0]
				if (att['filename'].endswith('.butt')):
					if (len(args) > 1):
						name = umsg[7:].strip()
						if (len(name) < 21):
							
							# check against user's existing levels
							t = (member.id, name)
							cur.execute('SELECT * FROM levels WHERE owner=? AND name=? COLLATE NOCASE', t)
							level = cur.fetchone()
							if (level == None):
								
								# generate level data and commit to database
								level = (gen_id(cur), channel.id, message.id, member.id, umsg[7:], 'Nothing to see here', att['url'], 0, datetime.datetime.now().strftime('%Y-%m-%d-%H-%M'))
								cur.execute('INSERT INTO levels VALUES (?,?,?,?,?,?,?,?,?)', level)
								conn.commit()
								await client.send_message(channel, name+' uploaded successfully!')
							
							else:
								await client.send_message(channel, 'You already have a level with that name! Please delete the existing level and upload again.')
							
						else:
							await client.send_message(channel, 'That level name is too long (must be 20 characters or less)!')
					else:
						await client.send_message(channel, 'You need to give a name for your level!')
				else:
					await client.send_message(channel, "That's not a .butt file!")
			else:
				await client.send_message(channel, 'You attached too many files!')
		else:
			await client.send_message(channel, "You didn't attach a file!")
	
	# delete
	if (args[0].lower() == 'delete'):
		
		# checks
		if (len(args) > 1):
			
			# try checking by id first
			search = umsg[7:].strip()
			s = (search,)
			cur.execute('SELECT * FROM levels WHERE id=?', s)
			t = cur.fetchone()
			if (t == None):
				
				# check by name
				cur.execute('SELECT Count(*) FROM levels WHERE name=? COLLATE NOCASE', s)
				n = cur.fetchone()
				
				# no level found, skip
				if (n[0] == 0):
					await client.send_message(channel, "Couldn't find a level with that name or id!")
					
				# multiple levels found, list
				elif (n[0] > 1):
					msg = 'Page 1\nMultiple levels share this name. Please use `!get [id]` to get the level you want'
					cur.execute('SELECT * FROM levels WHERE name=? COLLATE NOCASE LIMIT 10', s)
					for a in range(0,10):
						t = cur.fetchone()
						if (t != None):
							owner = await client.get_user_info(t[3])
							msg = msg + '\n' + str(a+1) + '. [`' + t[0] + '`] **' + t[4] + '** by **' + owner.display_name + '**'
						else:
							break
					embed = discord.Embed(title='Level List', type='rich', description=msg)
					await client.send_message(channel, content=None, embed=embed)
					t = None
				
				# one level found, return
				else: 
					cur.execute('SELECT * FROM levels WHERE name=? COLLATE NOCASE', s)
					t = cur.fetchone()
			
			# result exists
			if (t != None):
				
				# check authorization and delete
				if (member.id == t[3] or member.id in moderators):
					level = (t[0],)
					cur.execute('DELETE FROM levels WHERE id=?', level)
					await client.send_message(channel, 'Level deleted!')
				else:
					await client.send_message(channel, "You don't own that level!")
			
		else:
			await client.send_message(channel, 'You need to specify a level to delete!')
