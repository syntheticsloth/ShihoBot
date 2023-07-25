import asyncio
import re
from typing import Optional

import validators

import discord
from discord.ext import commands
from discord.commands import Option, OptionChoice, SlashCommandGroup, user_command
from discord.commands.permissions import default_permissions

from formatting.embed import gen_embed, embed_splitter
from formatting.constants import THUMB
from __main__ import log, db


class Tiering(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.refill_running = {}

    @staticmethod
    def convert_room(argument):
        if re.search(r'^\d{5}$', argument):
            return argument
        elif re.search(r'^\w+', argument):
            log.warning('Room Code not found, skipping')
            raise discord.ext.commands.BadArgument(message="This is not a valid room code.")
        else:
            raise discord.ext.commands.BadArgument(message="This is not a valid room code.")

    @staticmethod
    def convert_spot(argument):
        if re.search(r'^\d{5}$', argument):
            log.warning('Bad Argument - Spots Open')
            raise discord.ext.commands.BadArgument(
                message="This is not a valid option. Open spots must be a single digit number.")
        elif re.search(r'^\d$', argument):
            return argument
        elif re.search('^[Ff]$', argument):
            return "0"
        else:
            log.warning('Bad Argument - Spots Open')
            raise discord.ext.commands.BadArgument(
                message="This is not a valid option. Open spots must be a single digit number.")

    @staticmethod
    def has_modrole():
        async def predicate(ctx):
            document = await db.servers.find_one({"server_id": ctx.guild.id})
            if document['modrole']:
                role = discord.utils.find(lambda r: r.id == document['modrole'], ctx.guild.roles)
                return role in ctx.author.roles
            else:
                return False

        return commands.check(predicate)

    @commands.command(name='room',
                      aliases=['rm'],
                      description=('Changes the room name without having to go through the menu. If no arguments are'
                                   ' provided, the room will be changed to a dead room. Rooms must start with the'
                                   ' standard tiering prefix, i.e. "g#-".\nBoth parameters are optional.'),
                      help=('Usage:\n\n%room <room number> <open spots>\n\nExample:\n\n`%room 12345 1`\nFor just'
                            ' changing room number - `%room 12345`\nFor just changing open spots - `%room 3`'))
    @commands.cooldown(rate=2, per=600.00, type=commands.BucketType.channel)
    async def room(self, ctx, room_num: Optional[convert_room], open_spots: Optional[convert_spot]):
        currentname = ctx.channel.name
        namesuffix = ""
        if re.search(r'^[A-Za-z]\d-', currentname):
            nameprefix = re.match(r"^[A-Za-z]\d-", currentname).group(0)
        else:
            log.warning('Error: Invalid Channel')
            await ctx.send(embed=gen_embed(title='Invalid Channel',
                                           thumb_url=f'{THUMB}',
                                           content=(f'This is not a valid tiering channel. Please match the format'
                                                    ' g#-xxxxx to use this command.')))
            return
        if re.search(r'-[\df]$', currentname):
            namesuffix = re.search(r"-[\df]$", currentname).group(0)

        if room_num:
            if open_spots:
                open_spots = int(open_spots)
                if 0 < open_spots <= 4:
                    namesuffix = f'-{open_spots}'
                elif open_spots == 0:
                    namesuffix = '-f'
                else:
                    log.warning('Error: Invalid Input')
                    await ctx.send(embed=gen_embed(title='Input Error',
                                                   thumb_url=f'{THUMB}',
                                                   content=(f'That is not a valid option for this parameter. Open spots'
                                                            ' must be a value from 0-4.')))
                    return

            await ctx.channel.edit(name=f'{nameprefix}{room_num}{namesuffix}')
            await ctx.send(embed=gen_embed(title='Just this once',
                                           thumb_url=f'{THUMB}',
                                           content=f'Changed room code to {room_num}'))
        else:
            if open_spots:
                open_spots = int(open_spots)
                if 0 < open_spots <= 4:
                    namesuffix = f'-{open_spots}'
                    nameprefix = re.search(r"(^[A-Za-z]\d-.+)(?![^-])(?<!-[\df]$)", currentname).group(0)
                elif open_spots == 0:
                    namesuffix = '-f'
                    nameprefix = re.search(r"(^[A-Za-z]\d-.+)(?![^-])(?<!-[\df]$)", currentname).group(0)
                else:
                    log.warning('Error: Invalid Input')
                    await ctx.send(embed=gen_embed(title='Input Error',
                                                   thumb_url=f'{THUMB}',
                                                   content=(f'That is not a valid option for this parameter. Open spots'
                                                            ' must be a value from 0-4.')))
                    return
                await ctx.channel.edit(name=f'{nameprefix}{namesuffix}')
                await ctx.send(embed=gen_embed(title='Just this once',
                                               thumb_url=f'{THUMB}',
                                               content=f'Changed open spots to {open_spots}'))
            else:
                await ctx.channel.edit(name=f'{nameprefix}xxxxx')
                await ctx.send(embed=gen_embed(title='Just this once',
                                               thumb_url=f'{THUMB}',
                                               content=f'Closed room'))

    @discord.slash_command(name='room',
                           description=('Changes the room name. If no options are filled out, the room will close.'))
    async def sroom(self,
                    ctx: discord.ApplicationContext,
                    roomcode: Option(str, 'Room Code. Should be a 5 digit number from 00000-99999',
                                     required=False),
                    spots: Option(int, '# of spots open in room. Can be from 0-4.',
                                  min_value=0,
                                  max_value=4,
                                  required=False)):
        currentname = ctx.channel.name
        namesuffix = ""
        if re.search(r'^[A-Za-z]\d-', currentname):
            nameprefix = re.match(r"^[A-Za-z]\d-", currentname).group(0)
        else:
            log.warning('Error: Invalid Channel')
            await ctx.interaction.response.send_message(embed=gen_embed(
                title='Invalid Channel',
                thumb_url=f'{THUMB}',
                content=f'This is not a valid tiering channel. Please match the format g#-xxxxx to use this command.'),
                ephemeral=True)
            return

        await ctx.interaction.response.defer()
        if re.search(r'-[\df]$', currentname):
            namesuffix = re.search(r"-[\df]$", currentname).group(0)

        if roomcode:
            if not re.search(r'^\d{5}$', roomcode):
                await ctx.channel.edit(name=f'{nameprefix}xxxxx')
                await ctx.interaction.followup.send(embed=gen_embed(title='Just this once',
                                                                    thumb_url=f'{THUMB}',
                                                                    content=f'Closed room'))
                return
            if spots:
                if 0 < spots <= 4:
                    namesuffix = f'-{spots}'
                else:
                    namesuffix = '-f'

            new_room_title = f'{nameprefix}{roomcode}{namesuffix}'
            await ctx.interaction.channel.edit(name=new_room_title)
            await ctx.interaction.followup.send(embed=gen_embed(title='Just this once',
                                                                thumb_url=f'{THUMB}',
                                                                content=f'Changed name to {new_room_title}'))

        elif spots:
            if re.search(r'(-)(\d{5})(-)', currentname):
                roomcode = re.match(r"(-)(\d{5})(-)", currentname).group(1)
            else:
                roomcode = 'xxxxx'

            if 0 < spots <= 4:
                namesuffix = f'-{spots}'
            else:
                namesuffix = '-f'
            new_room_title = f'{nameprefix}{roomcode}{namesuffix}'
            await ctx.interaction.channel.edit(name=new_room_title)
            await ctx.interaction.followup.send(embed=gen_embed(title='Just this once',
                                                                thumb_url=f'{THUMB}',
                                                                content=f'Changed open spots to {spots} spots'))
        else:
            await ctx.channel.edit(name=f'{nameprefix}xxxxx')
            await ctx.interaction.followup.send(embed=gen_embed(title='Just this once',
                                                                thumb_url=f'{THUMB}',
                                                                content=f'Closed room'))

def setup(bot):
    bot.add_cog(Tiering(bot))
