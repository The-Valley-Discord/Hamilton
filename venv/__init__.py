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

#non-command functions
async def build_embed(mode, title, data):
    if mode == 'discord log':
        embed = discord.Embed(color=0xD4AF37, description=data)

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