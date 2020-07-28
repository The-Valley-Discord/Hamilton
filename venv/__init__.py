import asyncio
import discord
import sqlite3
from discord.ext import commands

#Discord Currency bot instance
discordbot = commands.Bot(command_prefix='h$')

@discordbot.command()
async def ping(ctx):
    qualified = False
    if "Moderators" in [r.name for r in ctx.message.author.roles]:
        qualified = True
    if qualified == True:
        await ctx.send(embed=await build_embed('discord log', 'Ping', 'Pong!'))

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
        cursor = conn.cursor()
        columns = ', '.join(str('`'+x+'`').replace('/', '_') for x in data.keys())
        values = ', '.join(str("'"+x+"'").replace('/', '_') for x in data.values())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % (table, columns, values)
        print(sql)
        cursor.execute(sql)
        cursor.close()
    except conn.Error as error:
        print("Failed to write single row to sqlite table", error)
    finally:
        if (conn):
            conn.commit()
            conn.close()
            print("The SQLLite connection is closed")

#Run the bot
discordbot.run("")