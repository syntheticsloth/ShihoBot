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

    guides = SlashCommandGroup('guide', 'Commands to post various tiering guides',
                               default_member_permissions=discord.Permissions(manage_messages=True))

    @guides.command(name='carpal-avoidance',
                    description='Generates a guide for avoiding Carpal Tunnel or RSI')
    @default_permissions(manage_messages=True)
    async def vsliveguide(self,
                          ctx: discord.ApplicationContext,
                          channel: Option(discord.SlashCommandOptionType.channel,
                                          ('Channel to post guide in. If not specified, '
                                           'will post in current channel'),
                                          required=False)):
        await ctx.interaction.response.defer()
        if channel:
            dest_channel = channel
        else:
            dest_channel = ctx.interaction.channel
        embed = gen_embed(
            name=f"{ctx.guild.name}",
            icon_url=ctx.guild.icon.url,
            title='Carpal Tunnel & Tiering Wellness',
            content=('Graciously created by **Aris/Nio**, originally for PRSK, edited by **Neon**'
                     '\n***Disclaimer: This is not medical advice. This is for educational purposes only and is my'
                     " (aris') research and does not replace going to the doctor.***"))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="What is Carpal Tunnel Syndrome/RSI?",
            content=('**Carpal Tunnel Syndrome** is the irritation of the median nerve within the carpal tunnel at the'
                     ' base of your hand. When the nerve becomes irritated in this region due to pressure, inflammation'
                     ', and/or stretching (ie gaming), symptoms are likely to occur.\n\nRepetitive quick movements over'
                     ' long periods of time (ie, tiering) can damage the carpal tunnel nerve in your wrists. This may'
                     ' cause numbness and weakness in your hands over long periods of time, which can become'
                     ' permanent.\n\n**Repetitive Strain Injury (RSI)** is damage damage to your muscles, tendons or'
                     ' nerves caused by repetitive motions and constant use. Anyone can get a RSI.'))
        embed.set_footer(text=('https://esportshealthcare.com/carpal-tunnel-syndrome/\n'
                               'https://my.clevelandclinic.org/health/diseases/17424-repetitive-strain-injury'))
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="Symptoms of Carpal Tunnel Syndrome/RSI",
            content=('🔹 Feelings of pain or numbness in your fingers\n'
                     '🔹 Weakness when gripping objects with one or both hands\n'
                     '🔹 "Pins and needles" or swollen feeling in your fingers\n'
                     '🔹 Burning or tingling in the fingers, especially the thumb, index, and middle fingers\n'
                     '🔹 Pain or numbness that is worse at night\n\nIf you ever feel pain, **TAKE A BREAK!**'))
        embed.set_footer(text='https://www.hopkinsmedicine.org/health/conditions-and-diseases/carpal-tunnel-syndrome')
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="Before Playing",
            content=('Below is a helpful guide for warming up. Other guides for Gamer Stretches™ probably exist on the'
                     ' internet. If you have one you like, keep following it.\n\nTake off any wristwatches before'
                     ' playing - wearing them worsens carpal tunnel.\n\nGrab a jug of water or other drinks to keep'
                     ' hydration within arm\'s reach.'))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        await dest_channel.send(content='https://esportshealthcare.com/gamer-warm-up/')
        embed = gen_embed(
            title="While Playing",
            content=('**Try to keep good posture.**\nTyping ergonomics logic likely applies here.\n'
                     '🔹 Consider playing on index fingers; it\'s easier on your wrists. Put your phone or tablet flat'
                     ' on the table, and tap on it as if it was a keyboard.\n'
                     '🔹 Position your wrist straight/aligned and neutral, as if you were playing piano.\n'
                     '🔹 Try to look down at your screen with your eyes instead of moving your head.'
                     ' You may need to perform neck stretches if your neck hurts.'))
        embed.set_image(url='https://files.s-neon.xyz/share/unknown.png')
        embed.add_field(name='Keep your hands warm',
                        value='Play in a warm environment - hand pain and stiffness is more likely in a cold one.',
                        inline=False)
        embed.add_field(name='Ideally, your screen should be at eye level',
                        value=('I think theoretically the best way to accomplish this is to cast your phone/tablet to'
                               'a monitor/TV and play while looking straight at the monitor you casted to instead of'
                               ' your device screen.'),
                        inline=False)
        embed.set_footer(text=('Exercises and tips in this section from:\n'
                               'https://youtu.be/EiRC80FJbHU\n'
                               'https://bit.ly/3lD5ot9\n'
                               'https://bit.ly/38IZeVI'))
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="Routines",
            content=('**Every 20 minutes**, do the 20-20-20 rule: look at something 20 feet away, for about 20 seconds,'
                     ' to give your eyes a break. This is easily done while menuing in between songs.\n\n'
                     '**Every 60 minutes**, consider taking a 5 minute break to rest your hands.\n\n'
                     '**Every 2-3 hours**, shake out your hands and perform some hand/finger exercises. See below for'
                     ' an instructional video.\n\n'
                     '**1-2 times a day**, run your hands gently under warm water. Move your hands up and down under'
                     ' the water.\n\n'
                     '**If your hands hurt, take breaks more often.**'))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        await dest_channel.send(content='https://youtu.be/EiRC80FJbHU?t=85')
        embed = gen_embed(
            title="After Playing",
            content=('Below is a helpful guide for post-game stretches. Again, other guides for Gamer Stretches™'
                     ' probably exist on the internet. If you have one you like, keep following it.'))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        await dest_channel.send(content='https://esportshealthcare.com/gamer-stretches/')
        await ctx.interaction.followup.send(embed=gen_embed(
            title='Carpal Avoidance Guide',
            content=f'Carpal Tunnel & RSI Avoidance guide posted in {dest_channel.mention}'),
            ephemeral=True)

    @guides.command(name='cheerful-carnival',
                    description='Generates a guide for Cheerful Carnival events')
    @default_permissions(manage_messages=True)
    async def marathonguide(self,
                          ctx: discord.ApplicationContext,
                          channel: Option(discord.SlashCommandOptionType.channel,
                                          ('Channel to post guide in. If not specified, '
                                           'will post in current channel'),
                                          required=False)):
        await ctx.interaction.response.defer()
        if channel:
            dest_channel = channel
        else:
            dest_channel = ctx.interaction.channel
        embed = gen_embed(
            name=f"{ctx.guild.name}",
            icon_url=ctx.guild.icon.url,
            title='Cheerful Carnival Filling Info',
            content=("Adapted from Azufire's \"FILLER 101 [Cheerful Carnival]\" guide from R8SS."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="HOW TO MAKE A TEAM / SKILLS 101",
            content=("__ONLY 2 THINGS MATTER__: Max skill bonus (biggest score% boost) and TALENT\n\n"
                     "__BEST SKILLS (IN ORDER)__ *(example values are skill lvl 1, 4\* cards)*:\n"
                     "1. **Unit Scorer [UScorer]** NEEDS ALL CARDS FROM SAME UNIT (yes, VS works)\n"
                     "```\"Score boost 80% for 5 seconds; For every member of [UNIT] in your team, there will be an extra score boost of 10%, with a maximum boost of 130%\"```\n"
                     "2. **Life Scorer [LScorer]**\n"
                     "```\"Score boost 70% if life is under 800 (100% if life is over 800) for 5 seconds. For every 10 life, score is increased by +1% (up to 120%)\"```\n"
                     "3. **Perfect Scorer [PScorer]**\n"
                     "```\"110% score boost for 5 seconds for PERFECTs only.\"```\n"
                     "4. **Scorer**\n"
                     "```\"100% score boost for 5 seconds.\"```\n"
                     "5. **Healer (OK ONLY IN CC)**\n"
                     "```\"Recover 350 life; 80% score boost for 5 seconds.\"```\n"
                     "**NOTES**\n"
                     "Leader trigger is the most powerful (furthest card on left) - put your strongest skill card here\n\n"
                     "Other cards still trigger their skills in song - use your best skill cards in every team slot\n\n"
                     "DON'T USE Accuracy Scorer / Combo Scorer [AScorer/GScorer] 9/10 TIMES\n"
                     "```\"70% score boost for 5 seconds (120% until GREAT or lower)\"```\n"
                     "Tierers have skill issue and can't all perfect combo all the time\n\n"
                     "Use only if your tierers are built different/say it*s OK"))
        embed.set_image(url='https://svenxiety.xyz/junk/fill_best.png')
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="HEALERS? IN MY TIERING ROOM?",
            content=("In CC, you get more points if you are at or above max HP at the end of a song. Most rooms will want 1 player with a HEALER lead, or BIRTHDAY card if tierers have skill issue/are dying (birthday cards = stronger heal, weaker score boost)."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="TALENT LEVEL? SANDBAGGING?",
            content=("CC means you need to match with an enemy team of a similar talent level. If your lobby is too strong, matchmaking will take longer and matches are harder to win because you will be fighting other high talent teams.\n\n"
                     "Some fillers will bring the lowest level cards they can (\"sandbag\") to either barely hit 150k talent for pro rooms, OR as low as possible talent (while still having good skills) for gen rooms."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="WHAT'S AN ISV / HOW DO I CALCULATE?",
            content=("**ISV:** Internal Skill Value - used to measure team strength / order rooms\n\n"
                     "First value = leader skill value (number in front of %)\n\n"
                     "Second value = sum of ALL skill values in team\n\n"
                     "Ex: if you have a team of all 4* PScorers with base skill 110 → ISV = 110 / 550"))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="WHAT'S ROOM ORDER?",
            content=("Because player skills trigger in a specific order in multi lives based on player order in the room, some player skills will be more important than others.\n\n"
                     "For high tier runs with room orders, managers will tell you what team to use and what room slot to go in (P1 - P5).\n\n"
                     "Join when your number is called. Then when you load into the lobby, call the next number to join.\n\n"
                     "However, for CC, since matchmaking is frequently unstable, prioritize getting matches over maintaining room order. In the case of a disconnect/disband, simply rejoin as fast as possible to return to matchmaking."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        await ctx.interaction.followup.send(embed=gen_embed(
            title='Cheerful Carnival Filling Info',
            content=f'Cheerful Carnival guide posted in {dest_channel.mention}'),
            ephemeral=True)

    @guides.command(name='efficiency',
                    description='Generates an efficiency guide for tiering')
    @default_permissions(manage_messages=True)
    async def efficiencyguide(self,
                              ctx: discord.ApplicationContext,
                              channel: Option(discord.SlashCommandOptionType.channel,
                                              ('Channel to post guide in. If not specified, '
                                               'will post in current channel'),
                                              required=False)):
        await ctx.interaction.response.defer()
        if channel:
            dest_channel = channel
        else:
            dest_channel = ctx.interaction.channel
        embed = gen_embed(
            name=f"{ctx.guild.name}",
            icon_url=ctx.guild.icon.url,
            title='Tiering Etiquette and Efficiency',
            content='Efficiency guidelines adapted from Alpha Gathering, with additions by synthsloth.')
        # embed.set_image(url='https://files.s-neon.xyz/share/bandori-efficiency.png')
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Fast Menuing',
            content=("After completing a song, tap through the buttons on the bottom right to skip through the "
                     "screens as fast as you can.\n\n"
                     "The same applies for the song selection screen in Marathons and the ready up screen in Cheerful "
                     "Carnivals.\n\n"
                     "If you need to type something in chat, try to menu first to keep things going smoothly."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        # await dest_channel.send(content='https://twitter.com/Binh_gbp/status/1106789316607410176')
        embed = gen_embed(
            title='Energy Refilling',
            content=("For **Marathon** events, refill during the song selection screen.\n\n"
                     "For **Cheerful Carnival** events, refill during matchmaking."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Doormatting',
            content=("Doormatting is when you play on Easy, hit enough notes in a song, and then stop playing. This is for **fillers "
                     "only**.\n\n"
                     "You must hit **at least 50% of the notes** in a song, otherwise you will get a conduct warning.\n\n"
                     "For Hitorinbo Envy during Marathon events, it's suggested to hit all of the notes up until the end of "
                     "fever chance (43 notes) before going afk.\n\n"
                     "For Cheerful Carnival events, since song selection is random, ensure you hit at least half of the notes "
                     "in the selected song before you stop playing."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Room Swaps',
            content=("Have the room code typed in beforehand.\n\n"
                     "Join as soon as someone says the room is open (\"op\"). You can also spam the join button "
                     "when they say \"sc\".\n\n"
                     "If there is room order, pay attention to the spot you've been assigned and be ready to join as soon as "
                     "someone types it in chat (P2, P3, P4, P5 or 2, 3, 4, 5).\n\n"
                     "If you are P1, create the room beforehand. Try rolling codes until you get one that is easy to type.\n\n"
                     "For Marathon events, have the song Hitorinbo Envy selected from a Solo Show before you join to prevent "
                     "accidentally selecting the wrong song. Do not rely on selecting \"Recommended\" each round.\n\n"
                     "Make sure you're using the correct team."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Don\'t All Perfect',
            content=("Try not to All Perfect (AP). The messages \"Full Combo\" And \"Show Cleared\" have the same animation "
                     "length at the end of a song. However, \"ALL PERFECT\" has a longer animation. Every second counts!"))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Communication',
            content=("Try to have another device to communicate with others, otherwise use in-game stamps if you can't.\n\n"
                     "If the runner or a manager is in voice chat (VC), you can also join that.\n\n"
                     "Let the other people know if you need to leave a couple of rounds prior to doing so."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Fill Scheduling',
            content=("Please only sign up for hours you are able to do. Don't sign up for super long shifts if you cannot "
                     "make it through.\n\n"
                     "Expect to have to stay for the **entirety** of your shift.\n\n"
                     "In case you're unable to make it to your shift or need to end your shift early, let the managers and runners "
                     "know as soon as possible so a replacement can be found."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Rank Checking',
            content=("Do not leave the room to check your rank. Use Nenerobo to check your rank, leaderboard, cutoffs, etc.\n\n"
                     "Link your Discord account with Nenerobo prior to entering the room. Type /rank to begin the linking process.\n\n"))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Other Considerations',
            content=("Make sure you have a stable internet connection before entering a room. Disconnects will disrupt room order"
                     "and may lead to a conduct warning.\n\n"
                     "Make sure your device is fully charged and/or plugged in to avoid disruptions due to low battery "
                     "notifications.\n\n"
                     "Enable \"Do Not Disturb\" to avoid distractions.\n\n"
                     "For iOS users, utilize \"Guided Access\" to avoid accidentally exiting the app while playing."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        await ctx.interaction.followup.send(embed=gen_embed(
            title='Efficiency Guide',
            content=f'Tiering etiquette and efficiency guide posted in {dest_channel.mention}'),
            ephemeral=True)

    @guides.command(name='fill-teams',
                    description='Generates a guide for creating fill teams')
    @default_permissions(manage_messages=True)
    async def marathonguide(self,
                          ctx: discord.ApplicationContext,
                          channel: Option(discord.SlashCommandOptionType.channel,
                                          ('Channel to post guide in. If not specified, '
                                           'will post in current channel'),
                                          required=False)):
        await ctx.interaction.response.defer()
        if channel:
            dest_channel = channel
        else:
            dest_channel = ctx.interaction.channel
        embed = gen_embed(
            name=f"{ctx.guild.name}",
            icon_url=ctx.guild.icon.url,
            title='Fill Teams Guide',
            content=("Adapted from Alpha Gathering's fill teams guide and Azufire's \"FILLER 101\" guides from R8SS."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="HOW TO MAKE A TEAM / SKILLS 101",
            content=("__BEST SKILLS (IN ORDER)__ *(example values are skill lvl 1, 4\* cards)*:\n"
                     "1. **Unit Scorer [UScorer]** NEEDS ALL CARDS FROM SAME UNIT (yes, VS works)\n"
                     "```\"Score boost 80% for 5 seconds; For every member of [UNIT] in your team, there will be an extra score boost of 10%, with a maximum boost of 130%\"```\n"
                     "2. **Life Scorer [LScorer]**\n"
                     "```\"Score boost 70% if life is under 800 (100% if life is over 800) for 5 seconds. For every 10 life, score is increased by +1% (up to 120%)\"```\n"
                     "3. **Perfect Scorer [PScorer]**\n"
                     "```\"110% score boost for 5 seconds for PERFECTs only.\"```\n"
                     "4. **Scorer**\n"
                     "```\"100% score boost for 5 seconds.\"```\n"
                     "5. **Healer (OK ONLY IN CC)**\n"
                     "```\"Recover 350 life; 80% score boost for 5 seconds.\"```\n"
                     "**NOTES**\n"
                     "Leader trigger is the most powerful (furthest card on left) - put your strongest skill card here\n\n"
                     "Other cards still trigger their skills in song - use your best skill cards in every team slot\n\n"
                     "DON'T USE Accuracy Scorer / Combo Scorer [AScorer/GScorer] 9/10 TIMES\n"
                     "```\"70% score boost for 5 seconds (120% until GREAT or lower)\"```\n"
                     "Tierers have skill issue and can't all perfect combo all the time\n\n"
                     "Use only if your tierers are built different/say it*s OK"))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="Best Fill Team",
            content=("Your regular Marathon fill team. Focus on maximizing your ISV here."))
        embed.set_image(url='https://svenxiety.xyz/junk/fill_best.png')
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="Fill Team <180k Talent (Pro Room Sandbag)",
            content=("Your best possible fill team while staying under 180k talent. This is used for sandbagging in Pro rooms during CC events.\n\n"
                     "Unleveled 4\* cards are useful here, but 3\*, 2\* and 1\* cards can be swapped in as well. Prioritize scorer abilities."))
        embed.set_image(url='https://svenxiety.xyz/junk/fill_sb1.png')
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="Fill Team <120k Talent (Gen Room Sandbag)",
            content=("Your best possible fill team while staying under 120k talent. This is used for sandbagging in Gen rooms during CC events.\n\n"
                     "Unleveled 4\* cards are useful here, but 3\*, 2\* and 1\* cards can be swapped in as well. Prioritize scorer abilities and try to get talent as low as possible."))
        embed.set_image(url='https://svenxiety.xyz/junk/fill_sb2.png')
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="Sandbag Heal Team",
            content=("This team should be similar to the previous sandbag team, but with a Healer lead. Aim for less than 120k talent. Only your leader needs to be a Healer.\n\n"
                     "Use a regular Healer rather than a Birthday Healer, as regular Healers provide higher score boost."))
        embed.set_image(url='https://svenxiety.xyz/junk/fill_hsb.png')
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        await ctx.interaction.followup.send(embed=gen_embed(
            title='Fill Teams Guide',
            content=f'Fill teams guide posted in {dest_channel.mention}'),
            ephemeral=True)

    @guides.command(name='marathon',
                    description='Generates a guide for Marathon events')
    @default_permissions(manage_messages=True)
    async def marathonguide(self,
                          ctx: discord.ApplicationContext,
                          channel: Option(discord.SlashCommandOptionType.channel,
                                          ('Channel to post guide in. If not specified, '
                                           'will post in current channel'),
                                          required=False)):
        await ctx.interaction.response.defer()
        if channel:
            dest_channel = channel
        else:
            dest_channel = ctx.interaction.channel
        embed = gen_embed(
            name=f"{ctx.guild.name}",
            icon_url=ctx.guild.icon.url,
            title='Marathon Filling Info',
            content=("Adapted from Azufire's \"FILLER 101\" guide from R8SS."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="HOW TO MAKE A TEAM / SKILLS 101",
            content=("__ONLY 2 THINGS MATTER__: Hit 150k talent and max skill bonus (biggest score% boost)\n\n"
                     "__BEST SKILLS (IN ORDER)__ *(example values are skill lvl 1, 4\* cards)*:\n"
                     "1. **Unit Scorer [UScorer]** NEEDS ALL CARDS FROM SAME UNIT (yes, VS works)\n"
                     "```\"Score boost 80% for 5 seconds; For every member of [UNIT] in your team, there will be an extra score boost of 10%, with a maximum boost of 130%\"```\n"
                     "2. **Life Scorer [LScorer]**\n"
                     "```\"Score boost 70% if life is under 800 (100% if life is over 800) for 5 seconds. For every 10 life, score is increased by +1% (up to 120%)\"```\n"
                     "3. **Perfect Scorer [PScorer]**\n"
                     "```\"110% score boost for 5 seconds for PERFECTs only.\"```\n"
                     "4. **Scorer**\n"
                     "```\"100% score boost for 5 seconds.\"```\n"
                     "5. **Healer (BOOOOO)**\n"
                     "```\"Recover 350 life; 80% score boost for 5 seconds.\"```\n"
                     "**NOTES**\n"
                     "• Leader trigger is the most powerful (furthest card on left) - put your strongest skill card here\n\n"
                     "• Other cards still trigger their skills in song - use your best skill cards in every team slot\n\n"
                     "• DON'T USE Accuracy Scorer / Combo Scorer [AScorer/GScorer] 9/10 TIMES\n"
                     "```\"70% score boost for 5 seconds (120% until GREAT or lower)\"```\n"
                     "Tierers have skill issue and can't all perfect combo all the time\n\n"
                     "Use only if your tierers are built different/say it's OK"))
        embed.set_image(url='https://svenxiety.xyz/junk/fill_best.png')
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="WHAT'S AN ISV / HOW DO I CALCULATE?",
            content=("**ISV:** Internal Skill Value - used to measure team strength / order rooms\n\n"
                     "First value = leader skill value (number in front of %)\n\n"
                     "Second value = sum of ALL skill values in team\n\n"
                     "Ex: if you have a team of all 4* PScorers with base skill 110 → ISV = 110 / 550"))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="WHAT'S ROOM ORDER?",
            content=("Because player skills trigger in a specific order in multi lives based on player order in the room, some player skills will be more important than others.\n\n"
                     "For high tier runs with room orders, managers will tell you what room slot to go in (P1 - P5).\n\n"
                     "Join when your number is called. Then when you load into the lobby, call the next number to join.\n\n"
                     "For lower tier runs, placing the strongest fillers as P4 and P5 is typically good enough."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title="WHAT'S EBI / EBI JAIL?",
            content=("Ebi = Hitorinbo Envy, the only song that matters.\n\n"
                     "It's the shortest song in the game, meta pick for tierers, and you will probably play it if it’s a Marathon event (for hours at a time, usually, hence \"ebi jail\")."))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        await ctx.interaction.followup.send(embed=gen_embed(
            title='Marathon Filling Info',
            content=f'Marathon Filling guide posted in {dest_channel.mention}'),
            ephemeral=True)

    @guides.command(name='terms',
                    description='Generates a list of terms for tiering')
    @default_permissions(manage_messages=True)
    async def termsguide(self,
                              ctx: discord.ApplicationContext,
                              channel: Option(discord.SlashCommandOptionType.channel,
                                              ('Channel to post guide in. If not specified, '
                                               'will post in current channel'),
                                              required=False)):
        await ctx.interaction.response.defer()
        if channel:
            dest_channel = channel
        else:
            dest_channel = ctx.interaction.channel
        embed = gen_embed(
            name=f"{ctx.guild.name}",
            icon_url=ctx.guild.icon.url,
            title='Tiering Terms',
            content=("Tiering terms from R8SS, with additions by synthsloth"))
        # embed.set_image(url='https://files.s-neon.xyz/share/bandori-efficiency.png')
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Cards',
            content=("**Ascorer:** Accuracy Scorer card. \"*Score +xx% for 5s and Score +xxx% until a GREAT or worse "
                     "tap is recorded.*\"\n\n"
                     "**Fes:** Colorful Festival card, AKA Colofes or Colorfes\n\n"
                     "**Gscorer:** Another name for Ascorer (Accuracy Scorer)\n\n"
                     "**Healer:** Healer card. \"*Life Recovery +350 and Score +x% for 5s.*\"\n\n"
                     "**Lscorer:** Life Scorer card. \"*Score +x% for 5s if your Life is below 800 upon activating "
                     "or Score +y% if above 800, and +1% every time your Life increases by 10 (max z%).*\"\n\n"
                     "**PLocker:** Perfect Locker card. \"*BAD or better taps change to PERFECT taps for 5.5s and "
                     "Score +x% for 5s.*\"\n\n"
                     "**Pscorer:** Perfect Scorer card. \"*Score +x% for PERFECT taps for 5s*\"\n\n"
                     "**Scorer:** Regular scorer card. \"*Score +x% for 5s.*\"\n\n"
                     "**Uscorer:** Unit Scorer card. \"*Score +x% for 5s. Score +10% for every [Unit] Character, "
                     "excluding self, plus an extra 10% (up to +y%) when all Characters are from [Unit].*\""))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Mechanics',
            content=("**AP:** All Perfect\n\n"
                     "**BP:** \"Battle Power\". Another name for Talent\n\n"
                     "**Cans/Boosts/Energy/Drinks:** The amount of energy you use per game. The higher its amount, "
                     "the higher the rewards\n\n"
                     "**CC:** Cheerful Carnival\n\n"
                     "**EB:** Event Bonus\n\n"
                     "**Encore:** 6th skill activation. It's triggered by the player with the highest score (co-op) "
                     "or your leader card (solo show)\n\n"
                     "**EP:** Event Points\n\n"
                     "**FC:** Full Combo\n\n"
                     "**ISV:** Internal Skill Value\n\n"
                     "**MR:** Mastery Rank\n\n"
                     "**Nats:** Energy that regenerates over time (1 energy per 30 mins)\n\n"
                     "**Podium:** Top 3 players of any event\n\n"
                     "**SF:** Short for Super Fever. Tap all the notes during Fever Chance to get extra rewards "
                     "(but NOT extra event points!)\n\n"
                     "**SL:** Short for skill level"))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        embed = gen_embed(
            title='Tiering',
            content=("**Boat:** To push someone out of their rank\n\n"
                     "**Conduct Warning:** A warning from the game after repeated disconnects. This warning will "
                     "prevent you from joining shows for a certain amount of time. The length of time increases "
                     "with each disconnect.\n\n"
                     "**DC:** Disconnect\n\n"
                     "**Doormat:** During Marathon filling, playing on Easy and hitting every note until the end of "
                     "Fever, and then stopping playing. Allows the filler to do more things during filling\n\n"
                     "**Fillers:** People who help the tierer achieve their goal\n\n"
                     "**Grief:** Ruining something. Whether that's super fever, menuing or anything else\n\n"
                     "**MM:** Short for matchmaking\n\n"
                     "**Menuing:** Tapping the screen after the song ends to play the next one as fast as possible\n\n"
                     "**op:** Open, means the room is open and you can join\n\n"
                     "**Otsu:** Abbreviation of \"otsukaresama\", meaning \"good work\" or \"nice job\". Used when "
                     "leaving a room or after event end\n\n"
                     "**Park:** Achieving a set number of event points and stopping there (for example 6,666,666 or "
                     "20,000,000)\n\n"
                     "**Pub:** Either opening the room to public or playing in co-op\n\n"
                     "**Runner:** A tierer, typically one going for a high tier and being hosted by a server\n\n"
                     "**sc:** \"Scores\", \"spam code\", \"show clear\", etc. During room swaps, indicates you can start "
                     "spamming the \"Join\" button"))
        embed.set_footer(text=discord.Embed.Empty)
        await dest_channel.send(embed=embed)
        await ctx.interaction.followup.send(embed=gen_embed(
            title='Tiering Terms',
            content=f'Tiering terms guide posted in {dest_channel.mention}'),
            ephemeral=True)

    # @guides.command(name='new-players',
    #                 description='Generates a guide for helping new players adjust to tiering')
    # @default_permissions(manage_messages=True)
    # async def vsliveguide(self,
    #                       ctx: discord.ApplicationContext,
    #                       channel: Option(discord.SlashCommandOptionType.channel,
    #                                       ('Channel to post guide in. If not specified, '
    #                                        'will post in current channel'),
    #                                       required=False)):
    #     await ctx.interaction.response.defer()
    #     if channel:
    #         dest_channel = channel
    #     else:
    #         dest_channel = ctx.interaction.channel
    #     embed = gen_embed(
    #         name=f"{ctx.guild.name}",
    #         icon_url=ctx.guild.icon.url,
    #         title='New Tiering Member Tips & Tricks',
    #         content=('Graciously created by **feathers**, edited by **Neon**'
    #                  '\n\nHi all, I’m here to make a special additional post regarding new players, rules, and tiering'
    #                  ' etiquette. The trend lately has been that brand new players tend to have difficulty knowing what'
    #                  ' questions they should be asking, and aren’t familiar with the intensity of tiering and the need'
    #                  ' to rely on fellow players to support each other properly for success. By **no means** should'
    #                  ' joining in be discouraged, but I wanted to take some time to emphasize the impact of being a'
    #                  ' good or bad helper. Many of you simply read a brief how-to or perhaps watched a video, but doing'
    #                  ' those things does not necessarily prepare you to be a good tierer or filler.\n\n'
    #                  'Some of these tidbits will repeat established rules, but I encourage you to think of this as'
    #                  ' reaffirming how important the rules truly are. The high tierers are spending a lot of time and'
    #                  ' money on these events, and we should always be considering that dedication when we come into a'
    #                  ' server to support or directly help the high tiering players. Every second will count from start'
    #                  ' to end. It is important to be confident and reliable in your ability to help everyone reach'
    #                  ' their goals, including those who are shooting for lower tiers. Being a good helper helps'
    #                  ' everyone, not just the high tierers.'))
    #     embed.set_footer(text=discord.Embed.Empty)
    #     await dest_channel.send(embed=embed)
    #     embed = gen_embed(
    #         title='Importance of Menus',
    #         content=('It may seem negligible in the end, but when it comes down to it, getting in those extra songs'
    #                  ' per hour thanks to fast menu tapping can make a substantial difference in placement if we come'
    #                  ' down to the wire.'))
    #     embed.set_footer(text=discord.Embed.Empty)
    #     await dest_channel.send(embed=embed)
    #     embed = gen_embed(
    #         title='Smooth Swapping',
    #         content=('The swapping of players in rooms can often lead to the biggest of time losses, so it is extremely'
    #                  ' important to judge correctly whether or not you should be joining Room 1 based on how much time'
    #                  ' you can spare. Players who have more time on their hands are generally more favorable in Room 1,'
    #                  ' where the podium players spend most of their time. The less swaps over time, the more efficient'
    #                  ' the room can be.\n\nIf you think you may have obligations (parents, meals, class, etc) that only'
    #                  ' allow you to play for short periods of time, try to actively seek out players who can be ready'
    #                  ' when you leave before you even join a room to play. I find that searching for replacements about'
    #                  ' **30 minutes before you need them** is the best way. If members of the server are present and'
    #                  ' unable to play, join the search to find a substitute! This is a team effort through and'
    #                  ' through.'))
    #     embed.set_footer(text=discord.Embed.Empty)
    #     await dest_channel.send(embed=embed)
    #     embed = gen_embed(
    #         title='Why Should I Remove Pins/Frames/Titles?',
    #         content=('The reason we remove these is to reduce loading times across devices, some of which struggle more'
    #                  ' than others. While it’s an easy mistake to make, do your best to prepare in advance. Go into'
    #                  ' your profile NOW, as you read this, and remove everything. If you accidentally join with them'
    #                  ' on, you can remove them the next time you fill your flames.'))
    #     embed.set_footer(text=discord.Embed.Empty)
    #     await dest_channel.send(embed=embed)
    #     embed = gen_embed(
    #         title='Flames, Rooms and Syncing',
    #         content=('As much as we like to plan this out and pray for full and smooth sets of 90 flames, falling out'
    #                  ' of sync is common and there is no reason to panic!\n\nIf you are helping in Room 1 or 2, where'
    #                  ' our top 10 and podium runners will be, you must prioritize the highest tiering player in the'
    #                  ' room. If T1 is on 30 flames and you, a filler or lower tierer, are on 20 flames, you will refill'
    #                  ' when the T1 is ready. It is important that we all reach our goals, but we must support our top'
    #                  ' players first and foremost, as is the purpose of servers like this one. T1, T2, and T3 ALWAYS'
    #                  ' have highest priority for entering rooms and deciding when flames will be re-synced.'
    #                  ' Please listen to them!'))
    #     embed.set_footer(text=discord.Embed.Empty)
    #     await dest_channel.send(embed=embed)
    #     embed = gen_embed(
    #         title='Starting a Partially Filled Room',
    #         content=('If you happen to be hosting a room with players that are tiering high and need every second to'
    #                  ' count, don’t be afraid to start your room with three or four people if a swap goes wrong. Often'
    #                  ' the length of one song is enough to re-organize. Don’t wait, EP is EP! Just say you’re going'
    #                  ' again and let the players who are swapping in prepare. More songs per hour is always the correct'
    #                  ' choice!'))
    #     embed.set_footer(text=discord.Embed.Empty)
    #     await dest_channel.send(embed=embed)
    #     embed = gen_embed(
    #         title='Being Asked to Play in a Different Room',
    #         content=('Please don’t be personally offended if you are asked to play in a different room. This could'
    #                  ' happen if your device loads slowly, if someone else is available to play longer than you, if'
    #                  ' someone happens to be able to menu faster than you at that current time, if the room needs'
    #                  ' higher band power teams for the extra boost, or even if someone has a better center than you.'
    #                  ' There are a lot of reasons a swap could be requested, and it is never personal. It **never**'
    #                  ' means that we hate you or are purposely ignoring your goals. Efficiency is key above all else,'
    #                  ' and we will try our best to make sure the other room is running smoothly as well!'
    #                  ' Don’t make trouble or argue, just do your best to swap out smoothly.'))
    #     embed.set_footer(text=discord.Embed.Empty)
    #     await dest_channel.send(embed=embed)
    #     embed = gen_embed(
    #         title='Closing Words of Wisdom',
    #         content=('If you are new and not quite sure what you’re doing yet, it might be best not to help in G1'
    #                  ' right away. Hang out in other game rooms and watch others to learn how everything works before'
    #                  ' jumping into the main tiering room, just to help keep up efficiency where we need it most. If'
    #                  ' we need an emergency filler, you’ll know!\n\nUltimately tiering is a game of math and endurance,'
    #                  ' and being realistic and mathematical about it is very beneficial mentally and physically. The'
    #                  ' mental game is just as important as the endurance, so it is important to stay calm and reign in'
    #                  ' those nerves as a first time, or even repeat player. We don’t have to concern ourselves with'
    #                  ' what the competition is doing, or who they are, or what they’re up to. We only have to work'
    #                  ' together to get the highest numbers the most times per hour until the event is over.'
    #                  ' We want **EVERYONE** to achieve their goals, we just need to remember that podium and T10 will'
    #                  ' need extra support. Most of all, remember to have fun doing it!'))
    #     embed.set_footer(text=discord.Embed.Empty)
    #     await dest_channel.send(embed=embed)
    #     await ctx.interaction.followup.send(embed=gen_embed(
    #         title='New Tiering Members Guide',
    #         content=f'New Tiering Members Tips and Tricks guide posted in {dest_channel.mention}'),
    #         ephemeral=True)

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

    # @discord.slash_command(name='giftbox',
    #                        description='Helps you calculate the optimal pulls for getting small boost cans.')
    # async def giftbox(self,
    #                   ctx: discord.ApplicationContext,
    #                   event: Option(str, 'The current event type',
    #                                 choices=[OptionChoice('VS Live', value='1'),
    #                                          OptionChoice('Team Live Festival', value='2')]),
    #                   giftbox: Option(int, 'The number of the giftbox you are currently on',
    #                                   min_value=1,
    #                                   max_value=99999,
    #                                   default=1,
    #                                   required=False)):
    #     class GiftboxMenu(discord.ui.View):
    #         def __init__(self, context, boxnum, event_type):
    #             super().__init__(timeout=900.0)
    #             self.context = context
    #             self.boxnum = boxnum
    #             self.event_type = int(event_type)
    #             self.value = None
    #             self.boxsize = 0
    #             self.cansize = 0
    #             self.can_remaining = 0
    #             self.remaining = 0
    #             self.vs_boxsizes = [30, 50, 70, 120, 170, 180]
    #             self.tl_boxsizes = [40, 65, 90, 160, 220, 230]
    #             self.vs_cansizes = [3, 5, 10, 10, 10, 10]
    #             self.tl_cansizes = [3, 5, 5, 5, 5, 10]
    #             self.vs_base_probabilities = [.1, .1, .1429, .0833, .0588, .0556]
    #             self.tl_base_probabilities = [.075, .0769, .0555, .03125, .0227, .0435]
    #             self.base_probability = 0
    #             self.probability = 0
    #
    #             if self.boxnum == 1:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[0]
    #                     self.can_remaining = self.vs_cansizes[0]
    #                     self.boxsize = self.vs_boxsizes[0]
    #                     self.cansize = self.vs_cansizes[0]
    #                     self.probability = self.vs_base_probabilities[0]
    #                     self.base_probability = self.vs_base_probabilities[1]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[0]
    #                     self.can_remaining = self.tl_cansizes[0]
    #                     self.boxsize = self.tl_boxsizes[0]
    #                     self.cansize = self.tl_cansizes[0]
    #                     self.probability = self.tl_base_probabilities[0]
    #                     self.base_probability = self.tl_base_probabilities[1]
    #             elif self.boxnum == 2:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[1]
    #                     self.can_remaining = self.vs_cansizes[1]
    #                     self.boxsize = self.vs_boxsizes[1]
    #                     self.cansize = self.vs_cansizes[1]
    #                     self.probability = self.vs_base_probabilities[1]
    #                     self.base_probability = self.vs_base_probabilities[2]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[1]
    #                     self.can_remaining = self.tl_cansizes[1]
    #                     self.boxsize = self.tl_boxsizes[1]
    #                     self.cansize = self.tl_cansizes[1]
    #                     self.probability = self.tl_base_probabilities[1]
    #                     self.base_probability = self.tl_base_probabilities[2]
    #             elif self.boxnum == 3:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[2]
    #                     self.can_remaining = self.vs_cansizes[2]
    #                     self.boxsize = self.vs_boxsizes[2]
    #                     self.cansize = self.vs_cansizes[2]
    #                     self.probability = self.vs_base_probabilities[2]
    #                     self.base_probability = self.vs_base_probabilities[3]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[2]
    #                     self.can_remaining = self.tl_cansizes[2]
    #                     self.boxsize = self.tl_boxsizes[2]
    #                     self.cansize = self.tl_cansizes[2]
    #                     self.probability = self.tl_base_probabilities[2]
    #                     self.base_probability = self.tl_base_probabilities[3]
    #             elif self.boxnum == 4:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[3]
    #                     self.can_remaining = self.vs_cansizes[3]
    #                     self.boxsize = self.vs_boxsizes[3]
    #                     self.cansize = self.vs_cansizes[3]
    #                     self.probability = self.vs_base_probabilities[3]
    #                     self.base_probability = self.vs_base_probabilities[4]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[3]
    #                     self.can_remaining = self.tl_cansizes[3]
    #                     self.boxsize = self.tl_boxsizes[3]
    #                     self.cansize = self.tl_cansizes[3]
    #                     self.probability = self.tl_base_probabilities[3]
    #                     self.base_probability = self.tl_base_probabilities[4]
    #             elif self.boxnum == 5:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[4]
    #                     self.can_remaining = self.vs_cansizes[4]
    #                     self.boxsize = self.vs_boxsizes[4]
    #                     self.cansize = self.vs_cansizes[4]
    #                     self.probability = self.vs_base_probabilities[4]
    #                     self.base_probability = self.vs_base_probabilities[5]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[4]
    #                     self.can_remaining = self.tl_cansizes[4]
    #                     self.boxsize = self.tl_boxsizes[4]
    #                     self.cansize = self.tl_cansizes[4]
    #                     self.probability = self.tl_base_probabilities[4]
    #                     self.base_probability = self.tl_base_probabilities[5]
    #             elif self.boxnum > 5:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[5]
    #                     self.can_remaining = self.vs_cansizes[5]
    #                     self.boxsize = self.vs_boxsizes[5]
    #                     self.cansize = self.vs_cansizes[5]
    #                     self.probability = self.vs_base_probabilities[5]
    #                     self.base_probability = self.vs_base_probabilities[5]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[5]
    #                     self.can_remaining = self.tl_cansizes[5]
    #                     self.boxsize = self.tl_boxsizes[5]
    #                     self.cansize = self.tl_cansizes[5]
    #                     self.probability = self.tl_base_probabilities[5]
    #                     self.base_probability = self.tl_base_probabilities[5]
    #
    #         async def interaction_check(self, interaction):
    #             if interaction.user != self.context.author:
    #                 return False
    #             return True
    #
    #         @discord.ui.button(label='-1 Can', style=discord.ButtonStyle.primary)
    #         async def minusonecan(self, button: discord.ui.Button, interaction: discord.Interaction):
    #             self.can_remaining -= 1
    #             if self.can_remaining <= 0:
    #                 self.children[0].disabled = True
    #             else:
    #                 self.children[0].disabled = False
    #             self.value = 1
    #             self.probability = self.can_remaining / self.remaining
    #             if self.probability > self.base_probability:
    #                 g_embed = gen_embed(title=f'Gift Box #{self.boxnum}',
    #                                     content=(f"**{self.remaining}/{self.boxsize} remaining**\n"
    #                                              f"{self.can_remaining}/{self.cansize} cans remaining\n\n"
    #                                              f"Should I pull? **Yes**"
    #                                              f" ({round(self.probability * 100, 2)}% probability)"))
    #             else:
    #                 g_embed = gen_embed(title=f'Gift Box #{self.boxnum}',
    #                                     content=(f"**{self.remaining}/{self.boxsize} remaining**\n"
    #                                              f"{self.can_remaining}/{self.cansize} cans remaining\n\n"
    #                                              f"Should I pull? **No**"
    #                                              f" ({round(self.probability * 100, 2)}% probability)"))
    #             g_embed.set_footer(text='Subtracting one can will not subtract from the total remaining.')
    #             await interaction.response.edit_message(embed=g_embed, view=self)
    #
    #         @discord.ui.button(label='-1', style=discord.ButtonStyle.secondary)
    #         async def minusone(self, button: discord.ui.Button, interaction: discord.Interaction):
    #             self.remaining -= 1
    #             if self.remaining <= 0:
    #                 self.children[0].disabled = True
    #                 self.children[1].disabled = True
    #                 self.children[2].disabled = True
    #             else:
    #                 self.children[1].disabled = False
    #             if self.remaining < 10:
    #                 self.children[2].disabled = True
    #             self.value = 2
    #             if self.remaining != 0:
    #                 self.probability = self.can_remaining / self.remaining
    #             else:
    #                 self.probability = 0
    #             if self.probability > self.base_probability:
    #                 g_embed = gen_embed(title=f'Gift Box #{self.boxnum}',
    #                                     content=(f"**{self.remaining}/{self.boxsize} remaining**\n"
    #                                              f"{self.can_remaining}/{self.cansize} cans remaining\n\n"
    #                                              f"Should I pull? **Yes**"
    #                                              f" ({round(self.probability * 100, 2)}% probability)"))
    #             else:
    #                 g_embed = gen_embed(title=f'Gift Box #{self.boxnum}',
    #                                     content=(f"**{self.remaining}/{self.boxsize} remaining**\n"
    #                                              f"{self.can_remaining}/{self.cansize} cans remaining\n\n"
    #                                              f"Should I pull? **No**"
    #                                              f" ({round(self.probability * 100, 2)}% probability)"))
    #             g_embed.set_footer(text='Subtracting one can will not subtract from the total remaining.')
    #             await interaction.response.edit_message(embed=g_embed, view=self)
    #
    #         @discord.ui.button(label='-10', style=discord.ButtonStyle.secondary)
    #         async def minusten(self, button: discord.ui.Button, interaction: discord.Interaction):
    #             if (self.remaining - 10) < 0:
    #                 raise RuntimeError('Gift box - tried to subtract more items than are available')
    #             self.remaining -= 10
    #             if self.remaining < 10:
    #                 self.children[2].disabled = True
    #             else:
    #                 self.children[2].disabled = False
    #             self.value = 3
    #             if self.remaining != 0:
    #                 self.probability = self.can_remaining / self.remaining
    #             else:
    #                 self.probability = 0
    #                 self.children[1].disabled = True
    #             if self.probability > self.base_probability:
    #                 g_embed = gen_embed(title=f'Gift Box #{self.boxnum}',
    #                                     content=(f"**{self.remaining}/{self.boxsize} remaining**\n"
    #                                              f"{self.can_remaining}/{self.cansize} cans remaining\n\n"
    #                                              f"Should I pull? **Yes**"
    #                                              f" ({round(self.probability * 100, 2)}% probability)"))
    #             else:
    #                 g_embed = gen_embed(title=f'Gift Box #{self.boxnum}',
    #                                     content=(f"**{self.remaining}/{self.boxsize} remaining**\n"
    #                                              f"{self.can_remaining}/{self.cansize} cans remaining\n\n"
    #                                              f"Should I pull? **No**"
    #                                              f" ({round(self.probability * 100, 2)}% probability)"))
    #             g_embed.set_footer(text='Subtracting one can will not subtract from the total remaining.')
    #             await interaction.response.edit_message(embed=g_embed, view=self)
    #
    #         @discord.ui.button(label='Next Box', style=discord.ButtonStyle.green)
    #         async def nextbox(self, button: discord.ui.Button, interaction: discord.Interaction):
    #             self.boxnum += 1
    #             if self.boxnum == 1:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[0]
    #                     self.can_remaining = self.vs_cansizes[0]
    #                     self.boxsize = self.vs_boxsizes[0]
    #                     self.cansize = self.vs_cansizes[0]
    #                     self.probability = self.vs_base_probabilities[0]
    #                     self.base_probability = self.vs_base_probabilities[1]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[0]
    #                     self.can_remaining = self.tl_cansizes[0]
    #                     self.boxsize = self.tl_boxsizes[0]
    #                     self.cansize = self.tl_cansizes[0]
    #                     self.probability = self.tl_base_probabilities[0]
    #                     self.base_probability = self.tl_base_probabilities[1]
    #             elif self.boxnum == 2:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[1]
    #                     self.can_remaining = self.vs_cansizes[1]
    #                     self.boxsize = self.vs_boxsizes[1]
    #                     self.cansize = self.vs_cansizes[1]
    #                     self.probability = self.vs_base_probabilities[1]
    #                     self.base_probability = self.vs_base_probabilities[2]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[1]
    #                     self.can_remaining = self.tl_cansizes[1]
    #                     self.boxsize = self.tl_boxsizes[1]
    #                     self.cansize = self.tl_cansizes[1]
    #                     self.probability = self.tl_base_probabilities[1]
    #                     self.base_probability = self.tl_base_probabilities[2]
    #             elif self.boxnum == 3:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[2]
    #                     self.can_remaining = self.vs_cansizes[2]
    #                     self.boxsize = self.vs_boxsizes[2]
    #                     self.cansize = self.vs_cansizes[2]
    #                     self.probability = self.vs_base_probabilities[2]
    #                     self.base_probability = self.vs_base_probabilities[3]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[2]
    #                     self.can_remaining = self.tl_cansizes[2]
    #                     self.boxsize = self.tl_boxsizes[2]
    #                     self.cansize = self.tl_cansizes[2]
    #                     self.probability = self.tl_base_probabilities[2]
    #                     self.base_probability = self.tl_base_probabilities[3]
    #             elif self.boxnum == 4:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[3]
    #                     self.can_remaining = self.vs_cansizes[3]
    #                     self.boxsize = self.vs_boxsizes[3]
    #                     self.cansize = self.vs_cansizes[3]
    #                     self.probability = self.vs_base_probabilities[3]
    #                     self.base_probability = self.vs_base_probabilities[4]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[3]
    #                     self.can_remaining = self.tl_cansizes[3]
    #                     self.boxsize = self.tl_boxsizes[3]
    #                     self.cansize = self.tl_cansizes[3]
    #                     self.probability = self.tl_base_probabilities[3]
    #                     self.base_probability = self.tl_base_probabilities[4]
    #             elif self.boxnum == 5:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[4]
    #                     self.can_remaining = self.vs_cansizes[4]
    #                     self.boxsize = self.vs_boxsizes[4]
    #                     self.cansize = self.vs_cansizes[4]
    #                     self.probability = self.vs_base_probabilities[4]
    #                     self.base_probability = self.vs_base_probabilities[5]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[4]
    #                     self.can_remaining = self.tl_cansizes[4]
    #                     self.boxsize = self.tl_boxsizes[4]
    #                     self.cansize = self.tl_cansizes[4]
    #                     self.probability = self.tl_base_probabilities[4]
    #                     self.base_probability = self.tl_base_probabilities[5]
    #             elif self.boxnum > 5:
    #                 if self.event_type == 1:
    #                     self.remaining = self.vs_boxsizes[5]
    #                     self.can_remaining = self.vs_cansizes[5]
    #                     self.boxsize = self.vs_boxsizes[5]
    #                     self.cansize = self.vs_cansizes[5]
    #                     self.probability = self.vs_base_probabilities[5]
    #                     self.base_probability = self.vs_base_probabilities[5]
    #                 elif self.event_type == 2:
    #                     self.remaining = self.tl_boxsizes[5]
    #                     self.can_remaining = self.tl_cansizes[5]
    #                     self.boxsize = self.tl_boxsizes[5]
    #                     self.cansize = self.tl_cansizes[5]
    #                     self.probability = self.tl_base_probabilities[5]
    #                     self.base_probability = self.tl_base_probabilities[5]
    #             self.value = 4
    #             for item in self.children:
    #                 item.disabled = False
    #             g_embed = gen_embed(title=f'Gift Box #{self.boxnum}',
    #                                 content=(f"**{self.remaining}/{self.boxsize} remaining**\n"
    #                                          f"{self.can_remaining}/{self.cansize} cans remaining\n\n"
    #                                          f"Should I pull? **Yes**"
    #                                          f" ({round(self.probability * 100, 2)}% probability)"))
    #             g_embed.set_footer(text='Subtracting one can will not subtract from the total remaining.')
    #             await interaction.response.edit_message(embed=g_embed, view=self)
    #
    #         @discord.ui.button(label='Cancel', style=discord.ButtonStyle.danger)
    #         async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
    #             await interaction.response.send_message('Closing gift box calculator.', ephemeral=True)
    #             for item in self.children:
    #                 item.disabled = True
    #             self.value = False
    #             self.stop()
    #
    #         @discord.ui.button(label='Manual Input', style=discord.ButtonStyle.secondary, row=1)
    #         async def manualinput(self, button: discord.ui.Button, interaction: discord.Interaction):
    #             async def remaining_prompt(attempts=1, sent_messages=[]):
    #                 def check(m):
    #                     return m.author == self.context.author and m.channel == self.context.channel
    #
    #                 g_sent_message = await self.context.send(embed=gen_embed(
    #                     title='Items remaining',
    #                     content='How many items are remaining in the box?'))
    #                 sent_messages.append(g_sent_message)
    #                 try:
    #                     mmsg = await self.context.bot.wait_for('message', check=check, timeout=60.0)
    #                 except asyncio.TimeoutError:
    #                     await self.context.send(embed=gen_embed(title='Gift box Cancelled',
    #                                                             content='Gift box calculator cancelled.'))
    #                     return
    #                 if re.match(r'^\d+$', mmsg.clean_content):
    #                     if validators.between(int(mmsg.clean_content), min=0, max=self.boxsize):
    #                         for message in sent_messages:
    #                             await message.delete()
    #                         await mmsg.delete()
    #                         return int(mmsg.clean_content)
    #                     elif attempts > 3:
    #                         raise discord.ext.commands.BadArgument()
    #                     else:
    #                         g_sent_message = await self.context.send(embed=gen_embed(
    #                             title='Items remaining',
    #                             content=(f"Sorry, I didn't catch that or it was an invalid format.\n"
    #                                      f"Please enter a number from 1-{self.boxsize}.")))
    #                         sent_messages.append(g_sent_message)
    #                         attempts += 1
    #                         return await remaining_prompt(attempts, sent_messages)
    #                 elif attempts > 3:
    #                     raise discord.ext.commands.BadArgument()
    #                 else:
    #                     g_sent_message = await self.context.send(embed=gen_embed(
    #                         title='Items remaining',
    #                         content=(f"Sorry, I didn't catch that or it was an invalid format.\n"
    #                                  f"Please enter a number from 1-{self.boxsize}.")))
    #                     sent_messages.append(g_sent_message)
    #                     attempts += 1
    #                     return await remaining_prompt(attempts, sent_messages)
    #
    #             await interaction.response.defer()
    #             self.remaining = await remaining_prompt()
    #             if self.remaining != 0:
    #                 self.probability = self.can_remaining / self.remaining
    #             else:
    #                 self.probability = 0
    #                 self.children[1].disabled = True
    #                 self.children[2].disabled = True
    #             if self.probability > self.base_probability:
    #                 g_embed = gen_embed(title=f'Gift Box #{self.boxnum}',
    #                                     content=(f"**{self.remaining}/{self.boxsize} remaining**\n"
    #                                              f"{self.can_remaining}/{self.cansize} cans remaining\n\n"
    #                                              f"Should I pull? **Yes**"
    #                                              f"({round(self.probability * 100, 2)}% probability)"))
    #             else:
    #                 g_embed = gen_embed(title=f'Gift Box #{self.boxnum}',
    #                                     content=(f"**{self.remaining}/{self.boxsize} remaining**\n"
    #                                              f"{self.can_remaining}/{self.cansize} cans remaining\n\n"
    #                                              f"Should I pull? **No**"
    #                                              f"({round(self.probability * 100, 2)}% probability)"))
    #             g_embed.set_footer(text='Subtracting one can will not subtract from the total remaining.')
    #             await interaction.edit_original_response(embed=g_embed, view=self)
    #
    #     await ctx.interaction.response.defer()
    #     giftbox_view = GiftboxMenu(ctx, giftbox, event)
    #     current_probability = giftbox_view.can_remaining / giftbox_view.remaining
    #     embed = gen_embed(title=f'Gift Box #{giftbox}',
    #                       content=(f"**{giftbox_view.remaining}/{giftbox_view.boxsize} remaining**\n"
    #                                f"{giftbox_view.can_remaining}/{giftbox_view.cansize} cans remaining\n\n"
    #                                f"Should I pull? **Yes** ({round(current_probability * 100, 2)}% probability)"))
    #     embed.set_footer(text='Subtracting one can will not subtract from the total remaining.')
    #     sent_message = await ctx.interaction.followup.send(embed=embed, view=giftbox_view)
    #     await giftbox_view.wait()
    #     await sent_message.edit(view=giftbox_view)

    # refill = SlashCommandGroup('refill', 'Refill related commands')
    #
    # @refill.command(name='counter',
    #                 description='Refill counter to help you keep track of when to refill')
    # async def refillcounter(self,
    #                         ctx: discord.ApplicationContext,
    #                         games: Option(int, '# of games left in the set',
    #                                       min_value=1,
    #                                       max_value=30,
    #                                       default=30,
    #                                       required=False)):
    #     class RefillCounter(discord.ui.View):
    #         def __init__(self, context, game_count):
    #             super().__init__(timeout=900.0)
    #             self.context = context
    #             self.counter = game_count
    #             self.value = False
    #
    #         async def end_interaction(self,
    #                                   interaction: discord.Interaction):
    #             view = discord.ui.View.from_message(interaction.message)
    #             for child in view.children:
    #                 child.disabled = True
    #
    #             self.value = True
    #             await interaction.message.edit(view=view)
    #             self.stop()
    #
    #         @discord.ui.button(emoji='❌', style=discord.ButtonStyle.secondary)
    #         async def exit(self, button: discord.ui.Button, interaction: discord.Interaction):
    #             await interaction.response.defer()
    #             await self.end_interaction(interaction)
    #
    #         @discord.ui.button(emoji='🔄', style=discord.ButtonStyle.secondary)
    #         async def refill(self, button: discord.ui.Button, interaction: discord.Interaction):
    #             await interaction.response.defer()
    #             self.counter = 30
    #             new_embed = gen_embed(title='Refill Counter',
    #                                   content=f'{self.counter} games left in the set')
    #             await interaction.message.edit(embed=new_embed)
    #
    #         @discord.ui.button(emoji='➕', style=discord.ButtonStyle.green)
    #         async def plus(self, button: discord.ui.Button, interaction: discord.Interaction):
    #             await interaction.response.defer()
    #             self.counter += 1
    #             new_embed = gen_embed(title='Refill Counter',
    #                                   content=f'{self.counter} games left in the set')
    #             await interaction.message.edit(embed=new_embed)
    #
    #         @discord.ui.button(emoji='➖', style=discord.ButtonStyle.danger)
    #         async def minus(self, button: discord.ui.Button, interaction: discord.Interaction):
    #             await interaction.response.defer()
    #             self.counter -= 1
    #             new_embed = gen_embed(title='Refill Counter',
    #                                   content=f'{self.counter} games left in the set')
    #             await interaction.message.edit(embed=new_embed)
    #
    #     await ctx.interaction.response.defer()
    #
    #     try:
    #         refill_running = self.refill_running[str(ctx.interaction.channel.id)]
    #     except KeyError:
    #         self.refill_running[str(ctx.interaction.channel.id)] = False
    #
    #     if self.refill_running[str(ctx.interaction.channel.id)]:
    #         embed = gen_embed(title='Refill Counter',
    #                           content=f'A counter is already running in this channel!')
    #         sent_message = await ctx.interaction.followup.send(embed=embed, ephemeral=True)
    #         return
    #     refillcounter_view = RefillCounter(ctx, games)
    #     embed = gen_embed(title='Refill Counter',
    #                       content=f'{games} games left in the set')
    #     sent_message = await ctx.interaction.followup.send(embed=embed, view=refillcounter_view)
    #     self.refill_running[str(ctx.interaction.channel.id)] = True
    #     while refillcounter_view.value is not True:
    #         if ctx.channel.last_message.id != sent_message.id:
    #             await sent_message.delete()
    #             embed = gen_embed(title='Refill Counter',
    #                               content=f'{refillcounter_view.counter} games left in the set')
    #             sent_message = await ctx.channel.send(embed=embed, view=refillcounter_view)
    #         await asyncio.sleep(5)
    #     self.refill_running[str(ctx.interaction.channel.id)] = False
    #
    # trackfiller = SlashCommandGroup('trackfiller', 'Filler tracking for tiering servers',
    #                                 default_member_permissions=discord.Permissions(manage_roles=True))
    #
    # @trackfiller.command(name='enable',
    #                      description='Enable filler tracking for the server')
    # @default_permissions(manage_roles=True)
    # async def trackfiller_enable(self,
    #                              ctx: discord.ApplicationContext):
    #     await ctx.interaction.response.defer(ephemeral=True)
    #     document = await db.fillers.find_one({'server_id': ctx.interaction.guild_id})
    #     if document:
    #         await db.fillers.update_one({'server_id': ctx.interaction.guild_id},
    #                                     {"$set": {"enabled": True}})
    #     else:
    #         post = {'server_id': ctx.interaction.guild_id,
    #                 'fillers': [],
    #                 'roles': [],
    #                 'enabled': True
    #                 }
    #         await db.fillers.insert_one(post)
    #     await ctx.interaction.followup.send(embed=gen_embed(title='trackfiller',
    #                                                         content=f'Enabled trackfiller for {ctx.guild.name}.'),
    #                                         ephemeral=True)
    #     await ctx.interaction.followup.send(content=('How do I set up who can add fillers?\n'
    #                                                  'https://files.s-neon.xyz/share/2022-05-25%2015-18-21.mp4'),
    #                                         ephemeral=True)
    #     await ctx.interaction.followup.send(content=('How do I add a filler?\n'
    #                                                  'https://files.s-neon.xyz/share/DiscordPTB_QkOPfrdP4L.png'),
    #                                         ephemeral=True)
    #
    # @trackfiller.command(name='disable',
    #                      description='Disable filler tracking for the server')
    # @default_permissions(manage_roles=True)
    # async def trackfiller_disable(self,
    #                               ctx: discord.ApplicationContext):
    #     await ctx.interaction.response.defer(ephemeral=True)
    #     document = await db.fillers.find_one({'server_id': ctx.interaction.guild_id})
    #     if document:
    #         await db.fillers.update_one({'server_id': ctx.interaction.guild_id},
    #                                     {"$set": {"enabled": False}})
    #     else:
    #         post = {'server_id': ctx.interaction.guild_id,
    #                 'fillers': [],
    #                 'roles': [],
    #                 'enabled': False
    #                 }
    #         await db.fillers.insert_one(post)
    #     await ctx.interaction.followup.send(embed=gen_embed(title='trackfiller',
    #                                                         content=f'Disabled trackfiller for {ctx.guild.name}.'),
    #                                         ephemeral=True)
    #
    # @trackfiller.command(name='help',
    #                      description='Display help on how to use the filler tracking feature')
    # async def trackfiller_help(self,
    #                            ctx: discord.ApplicationContext):
    #     await ctx.respond(content=('How do I add a filler?\n'
    #                                'https://files.s-neon.xyz/share/DiscordPTB_QkOPfrdP4L.png'),
    #                       ephemeral=True)
    #
    # @trackfiller.command(name='list',
    #                      description='List fillers')
    # async def trackfiller_list(self,
    #                            ctx: discord.ApplicationContext):
    #     await ctx.interaction.response.defer()
    #     fillers = []
    #     document = await db.fillers.find_one({'server_id': ctx.guild.id})
    #     for memberid in document['fillers']:
    #         member = await self.bot.fetch_user(memberid)
    #         fillers.append(member.name)
    #     fillers_str = ", ".join(fillers)
    #     embed = gen_embed(title='List of Fillers',
    #                       content=f'{fillers_str}')
    #     await embed_splitter(embed=embed, destination=ctx.channel, followup=ctx.interaction.followup)
    #
    # @trackfiller.command(name='remove',
    #                      description='Remove a filler from the list')
    # @default_permissions(manage_roles=True)
    # async def trackfiller_remove(self,
    #                              ctx: discord.ApplicationContext,
    #                              user: Option(discord.Member, 'Filler to remove')):
    #     await ctx.interaction.response.defer(ephemeral=True)
    #     document = await db.fillers.find_one({'server_id': ctx.guild.id})
    #     fillers = document['fillers']
    #     fillers.remove(user.id)
    #     await db.fillers.update_one({'server_id': ctx.guild.id}, {"$set": {"fillers": fillers}})
    #     await ctx.interaction.followup.send(embed=
    #                                         gen_embed(title='Remove Filler',
    #                                                   content=f'{user.name}#{user.discriminator} removed.'),
    #                                         ephemeral=True)
    #
    # @trackfiller.command(name='clear',
    #                      description='Clear the filler list')
    # @default_permissions(manage_roles=True)
    # async def trackfiller_clear(self,
    #                             ctx: discord.ApplicationContext):
    #     await ctx.interaction.response.defer(ephemeral=True)
    #     await db.fillers.update_one({'server_id': ctx.guild.id}, {"$set": {"fillers": []}})
    #     await ctx.interaction.followup.send(embed=
    #                                         gen_embed(title='Clear Filler List',
    #                                                   content=f'The filler list has been cleared.'),
    #                                         ephemeral=True)
    #
    # @user_command(name='Add User to Filler List')
    # @default_permissions()
    # async def addfiller(self,
    #                     ctx: discord.ApplicationContext,
    #                     member: discord.Member):
    #     document = await db.fillers.find_one({'server_id': ctx.guild.id})
    #     if document:
    #         fillers = document['fillers']
    #         enabled = document['enabled']
    #     else:
    #         fillers = []
    #         enabled = False
    #     if enabled:
    #         if member.id in fillers:
    #             await ctx.respond(content='User is already in the list of fillers.', ephemeral=True)
    #         else:
    #             fillers.append(member.id)
    #             log.info(f'Appended user to filler list for {ctx.guild.name}')
    #             await db.fillers.update_one({'server_id': ctx.guild.id},
    #                                         {"$set": {"fillers": fillers, "roles": []}}, upsert=True)
    #             await ctx.respond(content=f"Added {member.name} to the list of fillers.", ephemeral=True)
    #     else:
    #         await ctx.respond(content='This is not enabled for this server.', ephemeral=True)


def setup(bot):
    bot.add_cog(Tiering(bot))
