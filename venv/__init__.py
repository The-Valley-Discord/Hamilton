import asyncio
import discord
import sqlite3
from discord.ext import commands

#Discord Currency bot instance
discordbot = commands.Bot(command_prefix='h$')

#command functions
@discordbot.command()
async def ping(ctx):
    qualified = False
    if "Moderators" in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == True:
        await ctx.send(embed=await build_embed('discord log', 'Ping', 'My name is Alexander Hamilton.'))

discordbot.remove_command('help')
@discordbot.command()
async def help(ctx, mode="user"):
    if mode == "user":
        text =  "**Information and Commands:**\n" \
                "My name is Alexander Hamilton. I manage different currencies for events and general activities. \n\n" \
                "**score (currency) (user mention)** - check the amount of currency a user has\n" \
                "**leaderboard (currency)** - check the top stonks in a given currency\n" \
                "**help banker** - list of commands for currency owners\n" \
                "**help mod** - list of commands for moderators"
        await ctx.send(embed=await build_embed('discord log', 'Help', text))
    elif mode == "mod":
        text = "***Mod Commands:***\n\n" \
               "**mint (currency) (currency abbreviation)** - create currency\n" \
               "**bank (currency) (user mention)** - make user currency owner\n" \
               "**burn (currency) (user mention)** - remove a user from the list of currency owners\n" \
               "**enable (currency)** - enable a currency\n" \
               "**disable (currency)** - disable a currency\n" \
               "**set (amount) (currency) (user mention)** - set the currency score for a user. **only use this to fix owner mistakes**"
        await ctx.send(embed=await build_embed('discord log', 'Help', text))
    elif mode == "banker":
        text = "***Owner Commands:***\n\n" \
               "**award (amount) (currency) (user mention)** - give an amount of currency to a user"
        await ctx.send(embed=await build_embed('discord log', 'Help', text))

@discordbot.command()
async def mint(ctx, currency, abbreviation):
    qualified = False
    exists = False
    if "Moderators" in [r.name for r in ctx.message.author.roles]:
        qualified = True
        name_exists = await check_row('currency', 'name', currency)
        sname_exists = await check_row('currency', 's_name', abbreviation)
    if qualified == False:
        text = str("You don't have the votes.")
        await ctx.send(embed=await build_embed('discord log', 'Message', text))
    if name_exists == True or sname_exists == True:
        exists = True
        text = str("That currency already exists.")
        await ctx.send(embed=await build_embed('discord log', 'Message', text))
    if qualified == True and exists == False:
        currency_object = {
            'name': currency,
            's_name': abbreviation,
            'enabled': "True"
        }
        write = await write_to_db('currency', currency_object)

        if write == True:
            text = f"{currency} successfully minted."
            await ctx.send(embed=await build_embed('discord log', 'Message', text))

@discordbot.command()
async def bank(ctx, currency, owner):
    qualified = False
    if "Moderators" in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == False:
        text = str("You don't have the votes.")
        await ctx.send(embed=await build_embed('discord log', 'Message', text))
    if qualified == True:
        currency_id = await get_currency_id(currency)

        if currency_id != None:
            banker_object = {
                'owner_id': owner,
                'currency_id': str(currency_id[0]),
            }
            write = await write_to_db('owners', banker_object)

            if write == True:
                text = f"{owner} is now a banker for {currency_id[1]}."
                await ctx.send(embed=await build_embed('discord log', 'Message', text))
        else:
            text = f"{currency} does not exist."
            await ctx.send(embed=await build_embed('discord log', 'Message', text))

@discordbot.command()
async def burn(ctx, currency, owner):
    qualified = False
    if "Moderators" in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == False:
        text = str("You don't have the votes.")
        await ctx.send(embed=await build_embed('discord log', 'Message', text))
    if qualified == True:
        currency_id = await get_currency_id(currency)
        if currency_id != None:
            is_owner = await check_owner(currency_id[0], owner)
            if is_owner == True:
                write = await delete_owner(str(currency_id[0]), owner)
                if write == True:
                    text = f"{owner} is no longer a banker for {currency_id[1]}."
                    await ctx.send(embed=await build_embed('discord log', 'Message', text))
            elif is_owner == False:
                text = f"{owner} is not a banker for {currency_id[1]}."
                await ctx.send(embed=await build_embed('discord log', 'Message', text))
        else:
            text = f"{currency} does not exist."
            await ctx.send(embed=await build_embed('discord log', 'Message', text))
@discordbot.command()
async def award(ctx, amount, currency, user):
    currency_id = await get_currency_id(currency)
    if currency_id == None:
        text = f"{currency} does not exist."
        await ctx.send(embed=await build_embed('discord log', 'Message', text))
    else:
        author = str(f'<@!{ctx.message.author.id}>')
        qualified = await check_owner(str(currency_id[0]), author)

        if qualified == False:
            text = str("You don't have the votes.")
            await ctx.send(embed=await build_embed('discord log', 'Message', text))
        if qualified == True and currency_id[3] == 'True':
                user_object = {
                    'user_id': user,
                    'currency_id': str(currency_id[0]),
                    'total': amount
                }
                print(user_object)
                write = await write_to_db('users', user_object)

                if write == True:
                    text = f"{user} was awarded {amount} {currency_id[1]}."
                    await ctx.send(embed=await build_embed('discord log', 'Message', text))
        elif currency_id[3] == 'False':
            text = str(f"{currency_id[1]} not currently enabled.")
            await ctx.send(embed=await build_embed('discord log', 'Message', text))

@discordbot.command()
async def set(ctx, amount, currency, user):
    currency_id = await get_currency_id(currency)
    if currency_id == None:
        text = f"{currency} does not exist."
        await ctx.send(embed=await build_embed('discord log', 'Message', text))
    else:
        if "Moderators" in [r.name for r in ctx.message.author.roles]:
            qualified = True

        if qualified == False:
            text = str("You don't have the votes.")
            await ctx.send(embed=await build_embed('discord log', 'Message', text))
        if qualified == True:
                user_object = {
                    'user_id': user,
                    'currency_id': str(currency_id[0]),
                    'total': amount
                }
                write = await set_balance(user_object)

                if write == True:
                    text = f"{user}'s balance for {currency_id[1]} was set to {amount}."
                    await ctx.send(embed=await build_embed('discord log', 'Message', text))

@discordbot.command()
async def enable(ctx, currency):
    qualified = False
    if "Moderators" in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == False:
        text = str("You don't have the votes.")
        await ctx.send(embed=await build_embed('discord log', 'Message', text))
    if qualified == True:
        currency_id = await get_currency_id(currency)

        if currency_id != None:
            currency_object = {
                'currency_id': str(currency_id[0]),
                'enabled': "True"
            }
            await toggle(currency_object)
            text = f"{currency_id[1]} has been enabled."
            await ctx.send(embed=await build_embed('discord log', 'Message', text))
        else:
            text = f"{currency} does not exist."
            await ctx.send(embed=await build_embed('discord log', 'Message', text))

@discordbot.command()
async def disable(ctx, currency):
    qualified = False
    if "Moderators" in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == False:
        text = str("You don't have the votes.")
        await ctx.send(embed=await build_embed('discord log', 'Message', text))
    if qualified == True:
        currency_id = await get_currency_id(currency)

        if currency_id != None:
            currency_object = {
                'currency_id': str(currency_id[0]),
                'enabled': "False"
            }
            await toggle(currency_object)
            text = f"{currency_id[1]} has been disabled."
            await ctx.send(embed=await build_embed('discord log', 'Message', text))
        else:
            text = f"{currency} does not exist."
            await ctx.send(embed=await build_embed('discord log', 'Message', text))

@discordbot.command()
async def score(ctx, currency, user):
    currency_id = await get_currency_id(currency)
    if currency_id == None:
        text = f"{currency} does not exist."
        await ctx.send(embed=await build_embed('discord log', 'Message', text))
    else:
        user_object = {
            'id': user,
            'currency_id': str(currency_id[0])
        }
        score = await get_score(user_object)
        if score != None:
            text = f"{user} has {score[2]} {currency_id[1]}."
            await ctx.send(embed=await build_embed('discord log', 'Message', text))
        else:
            text = f"{user} has zero {currency_id[1]}."
            await ctx.send(embed=await build_embed('discord log', 'Message', text))

@discordbot.command()
async def leaderboard(ctx, currency):
    currency_id = await get_currency_id(currency)
    if currency_id == None:
        text = f"{currency} does not exist."
        await ctx.send(embed=await build_embed('discord log', 'Message', text))
    else:

        board = await get_leaderboard(str(currency_id[0]))
        if board != None:
            await ctx.send(f"Current leaderboard for {currency_id[1]}:")
            await ctx.send(embed=await build_embed('leaderboard', 'Leaberboard', board))
        else:
            text = f"No current totals for {currency_id[1]}"
            await ctx.send(embed=await build_embed('discord log', 'Message', text))


#non-command functions
async def build_embed(mode, title, data):
    if mode == 'discord log':
        embed = discord.Embed(color=0xD4AF37, description=data)

    if mode == 'leaderboard':
        text = "\n"
        for item in data:
            text+=str(f"{item[0]}:   {item[2]}\n")
        embed = discord.Embed(color=0xD4AF37, description=text)

    return embed

# sqlite3 functions
async def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect('hamilton.db')
        print("Connected to hamilton.db")
    except Error as e:
        print(e)

    return conn

async def write_to_db(table, data):
    try:
        conn = await create_connection()
        conn.execute(
            f"INSERT INTO {table}({','.join(data.keys())}) VALUES({','.join(['?' for v in data.values()])})", tuple(data.values())
        )

        return True
    except conn.Error as error:
        print("Failed to write single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def set_balance(data):
    try:
        conn = await create_connection()
        conn.execute(
            "UPDATE users SET total=:total WHERE user_id=:user_id AND currency_id=:currency_id", {"total": data['total'], "user_id": data['user_id'], "currency_id": data['currency_id']}
        )

        return True
    except conn.Error as error:
        print("Failed to write single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def toggle(currency):
    try:
        conn = await create_connection()
        conn.execute(
            "UPDATE currency SET enabled=:enabled WHERE currency_id=:currency_id", {"enabled": currency['enabled'], "currency_id": currency['currency_id']}
        )

        return True
    except conn.Error as error:
        print("Failed to write single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def check_row(table, column, data):
    exists = False
    try:
        conn = await create_connection()
        record = conn.execute(
            f"SELECT * FROM {table} where {column}=:data", {"data": data}
        ).fetchone()
        if record != None:
            exists = True
        else:
            exists = False

        return exists
    except conn.Error as error:
        print("Failed to write single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def delete_owner(currency_id, owner_id):
    try:
        conn = await create_connection()
        record = conn.execute(
            f"DELETE FROM owners WHERE currency_id=:currency_id AND owner_id=:owner_id", {"currency_id": currency_id, "owner_id": owner_id}
        ).fetchone()
        return True
    except conn.Error as error:
        print("Failed to delete single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def get_currency_id(value):
    try:
        conn = await create_connection()
        record = conn.execute(
            "SELECT * FROM currency where name=:value", {"value": value}
        ).fetchone()
        if record == None:
            record = conn.execute(
                "SELECT * FROM currency where s_name=:value", {"value": value}
            ).fetchone()

        return record
    except conn.Error as error:
        print("Failed to write single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def get_score(user):
    try:
        conn = await create_connection()
        record = conn.execute(
            "SELECT * FROM users WHERE user_id=:id AND currency_id=currency_id", {"id": user['id'], "currency_id": user['currency_id']}
        ).fetchone()

        return record
    except conn.Error as error:
        print("Failed to read single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def get_leaderboard(currency_id):
    try:
        conn = await create_connection()
        records = conn.execute(
            "SELECT * FROM users WHERE currency_id=currency_id", {"currency_id": currency_id}
        ).fetchall()

        sorted_records = sorted(records, key=lambda x: x[2], reverse=True)

        return sorted_records
    except conn.Error as error:
        print("Failed to read single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

async def check_owner(currency_id, owner_id):
    exists = False
    try:
        conn = await create_connection()
        record = conn.execute(
            "SELECT * FROM owners WHERE currency_id=:currency_id AND owner_id=:owner_id", {"currency_id": currency_id, "owner_id": owner_id}
        ).fetchone()
        if record != None:
            exists = True
        else:
            exists = False

        return exists
    except conn.Error as error:
        print("Failed to read single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

#Run the bot
discordbot.run("")