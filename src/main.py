import asyncio
import os
from datetime import datetime, timedelta

import discord
import instaloader
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from pretty_help import EmojiMenu, PrettyHelp

import post_data_D
import post_data_ND
import settings

logger = settings.logging.getLogger("bot")

instaloader_logger = settings.logging.getLogger("instaloader")
instaloader_logger.setLevel(settings.logging.WARNING)

# last_post = None
# last_post_author = None

post_checkers = {}


# global_ctx = None
# global_username = None
# global_channel_id = None
# global_role_id = None


start_time = datetime.now()


class RoleNotFound(Exception):
    pass


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="]", intents=intents)
    menu = EmojiMenu(page_left="◀️", page_right="▶️", remove="❌")
    bot.help_command = PrettyHelp(navigation=menu, color=discord.Colour.orange(), no_category="All Commands")

    class PostChecker:
        def __init__(self, bot, ctx, username, channel_id, role_id):
            self.bot = bot
            self.ctx = ctx
            self.username = username
            self.channel_id = channel_id
            self.role_id = role_id
            self.last_post = None
            self.last_post_author = username
            self.check_interval = 120
            self.start_time = "" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)"
            self.start_time_val = datetime.now()
            self.prev_time_val = datetime.now()
            self.task = tasks.loop(minutes=self.check_interval)(self.post_check_task)
            self.task.before_loop(self.before_post_check_task)
            self.task.start()

        async def post_check_task(self):
            logger.info("Beginning post_check call")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
            self.last_post = await post_data_D.post_check_downloadv(
                self.bot,
                logger,
                self.last_post,
                self.last_post_author,
                self.ctx,
                self.username,
                self.channel_id,
                self.role_id,
            )
            self.prev_time_val = datetime.now()

        async def before_post_check_task(self):
            logger.info("Waiting until bot is ready to begin post_check loop")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
            await self.bot.wait_until_ready()

        def cancel(self):
            self.task.cancel()
            logger.info("Canceling post checker task.")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")

        def stop(self):
            self.task.stop()
            logger.info("Stopping post checker task. Task will run for one more iteration before being paused.")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")

        def time_until_next_check(self):
            next_check = self.prev_time_val + timedelta(minutes=self.check_interval)
            return next_check - datetime.now()

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})\n")

        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Mozart 🧐"))
        # await bot.tree.sync()
        # post_check_task.start()

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            missing_param = error.param
            command_name = ctx.command.name
            await ctx.send(
                f"Error: {missing_param} parameter is missing in the function {command_name}! For more information, do ]help {command_name}."
            )
        elif isinstance(error, RoleNotFound):
            await ctx.send(error)
        else:
            await ctx.send(f"Error: {error}")

    # @bot.command(
    #     brief = "Starts post checker"
    # )
    # @has_permissions(ban_members=True)
    # async def start_postchecker(ctx, username, channel_id: int, role_id: int):
    #     if not post_check_task.is_running():

    #         post_check_task.ctx = ctx
    #         post_check_task.username = username
    #         post_check_task.channel_id = channel_id
    #         post_check_task.role_id = role_id
    #         post_check_task.start()

    #         #post_check_task.start()
    #         #asyncio.create_task(post_check_task(ctx, username, channel_id, role_id))
    #         logger.info("Starting post checker task.")
    #         logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
    #     else:
    #         logger.info("Cannot start post checker task. Post checker task is already running.")
    #         logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")

    @bot.command(brief="Starts post checker. Limit of 1 post checker in a channel per author")
    @has_permissions(ban_members=True)
    async def start_postchecker(ctx, username: str, channel_id: int, role_id: int):
        key = (ctx.guild.id, username, channel_id)
        if key not in post_checkers:
            post_checkers[key] = PostChecker(bot, ctx, username, channel_id, role_id)
            logger.info("Starting post checker task.")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
        else:
            logger.info("Cannot start post checker task. Post checker task is already running.")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")

    # @bot.command(
    #     brief = "Immediatedly cancels post checker"
    # )
    # @has_permissions(ban_members=True)
    # async def cancel_postchecker(ctx):
    #     if post_check_task.is_running():
    #         post_check_task.cancel()
    #         logger.info("Canceling post checker task.")
    #         logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
    #     else:
    #         logger.info("Cannot cancel post checker task. Post checker task is not running.")
    #         logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")

    @bot.command(brief="Immediately cancels post checker")
    @has_permissions(ban_members=True)
    async def cancel_postchecker(ctx, username: str, channel_id: int):
        key = (ctx.guild.id, username, channel_id)
        if key in post_checkers:
            post_checkers[key].cancel()
            del post_checkers[key]
        else:
            logger.info("Cannot cancel post checker task. Post checker task is not running.")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")

    # @bot.command(
    #     brief = "Pauses post checker after the next iteration"
    # )
    # @has_permissions(ban_members=True)
    # async def stop_postchecker(ctx):
    #     if post_check_task.is_running():
    #         post_check_task.stop()
    #         logger.info("Stopping post checker task. Task will run for one more iteration before being pasued.")
    #         logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
    #     else:
    #         logger.info("Cannot stop post checker task. Post checker task is not running.")
    #         logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")

    @bot.command(brief="Pauses post checker after the next iteration")
    @has_permissions(ban_members=True)
    async def stop_postchecker(ctx, username: str, channel_id: int):
        key = (ctx.guild.id, username, channel_id)
        if key in post_checkers:
            post_checkers[key].stop()
        else:
            logger.info("Cannot stop post checker task. Post checker task is not running.")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")

    @tasks.loop(minutes=120)
    async def post_check_task():

        # global last_post, last_post_author, global_ctx, global_username, global_channel_id, global_role_id
        global last_post, last_post_author

        ctx = post_check_task.ctx
        username = post_check_task.username
        channel_id = post_check_task.channel_id
        role_id = post_check_task.role_id

        logger.info("Beginning post_check call")
        logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
        # await post_data_D.post_check_downloadv(bot, logger, last_post, last_post_author, global_ctx, global_username, global_channel_id, global_role_id)
        await post_data_D.post_check_downloadv(
            bot, logger, last_post, last_post_author, ctx, username, channel_id, role_id
        )

    @post_check_task.before_loop
    async def before_post_check_task():
        logger.info("Waiting until bot is ready to begin post_check loop")
        logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
        await bot.wait_until_ready()

    @bot.command(
        brief="Prints the current last post of designated account without downloading/deleting. Images within embeds are temporary."
    )
    @has_permissions(ban_members=True)
    async def lastpost_ND(ctx, username, channel_id: int, role_id: int):
        # global last_post_author, last_post

        last_post = await post_data_ND.lastpost(
            ctx, username, channel_id, role_id, bot, logger, last_post, last_post_author
        )

    @bot.command(
        brief="Prints the current last post of designated account with downloading/deleting. Images within embed are permanent. If the channel/author used match a current post checker, it will overwrite that post checker. There will be no double post."
    )
    @has_permissions(ban_members=True)
    async def lastpost_D(ctx, username, channel_id: int, role_id=None):
        # global last_post_author, last_post

        if role_id != None:
            role_id = int(role_id)

        global post_checkers

        post_checkers = await post_data_D.lastpost_downloadv(
            bot, logger, ctx, username, channel_id, role_id, post_checkers
        )

    @bot.command(
        brief="Prints the current last post of designated account with downloading/deleting. Includes pinned messages. Images within embed are permanent. If the channel/author used match a current post checker, it will overwrite that post checker. There will be no double post."
    )
    @has_permissions(ban_members=True)
    async def lastpost_DP(ctx, username, channel_id: int, role_id=None):
        # global last_post_author, last_post

        if role_id != None:
            role_id = int(role_id)

        global post_checkers

        post_checkers = await post_data_D.lastpost_downloadv_pinned(
            bot, logger, ctx, username, channel_id, role_id, post_checkers
        )

    @bot.command(
        brief="Prints the current last post of designated account with downloading/deleting. Images within embed are permanent. If the channel/author used match a current post checker, it will overwrite that post checker. There will be no double post."
    )
    @has_permissions(ban_members=True)
    async def lastpost_DMUL(ctx, username, channel_id: int, role_id: int, num_posts=1):
        # global last_post_author, last_post

        global post_checkers

        post_checkers = await post_data_D.lastpost_downloadv_m(
            bot, logger, ctx, username, channel_id, role_id, post_checkers, num_posts
        )

    @bot.command(brief="Lists all running post checkers")
    @has_permissions(ban_members=True)
    async def list_postcheckers(ctx):
        if post_checkers:
            message = "Current running post checkers:\n"
            for key, checker in post_checkers.items():
                guild_id, username, label = key
                message += f"Guild: {guild_id}, Username: {username}, Channel ID: {checker.channel_id}, Role ID: {checker.role_id}, Label: {label}, Start Time: {checker.start_time}\n"
            await ctx.send(message)
        else:
            await ctx.send("No post checkers are currently running.")

    @bot.command(brief="Prints time until next check for a specific postchecker")
    @has_permissions(ban_members=True)
    async def time_postchecker(ctx, username: str, channel_id: int):
        key = (ctx.guild.id, username, channel_id)
        if key in post_checkers:
            remaining_time = post_checkers[key].time_until_next_check()
            await ctx.send(f"Time remaining until next post check: {remaining_time}")
        else:
            await ctx.send("There is no post checker running under the provided key.")

    @bot.command(brief="Gets uptime of the bot instance")
    @has_permissions(ban_members=True)
    async def uptime_checker(ctx):
        global start_time

        curr_time = datetime.now()

        uptime = curr_time - start_time
        await ctx.send(f"The uptime of the bot is {uptime}.")

    @bot.command(
        aliases=["p"],
        help="This is help",
        description="This is description",
        brief="This is brief",
        enabled=True,
        hidden=True,
    )
    @has_permissions(ban_members=True)
    async def ping(ctx, test: int):
        """Answers with pong

        Arguments:
        test      This is the help message for test.
        """
        await ctx.send("pong")

    @bot.hybrid_command(hidden=True)
    async def testslash(ctx):
        await ctx.send("ping")

    @bot.command(hidden=True)
    @has_permissions(ban_members=True)
    async def test_command(ctx):
        e = discord.Embed(
            title="testing",
            description="test description",
            url="https://www.google.com/",
            color=0x27C4D8,
        )
        role = discord.utils.get(ctx.guild.roles, name="Discord Manager")
        await ctx.send(f" {role.mention} New post on x's instagram", embed=e)

        guild = bot.get_guild

    @bot.command(hidden=True)
    @has_permissions(ban_members=True)
    async def say(ctx, what="Command Needs Input!"):
        name = "Discord Manager"
        role = discord.utils.get(ctx.guild.roles, name=name)
        if role is None:
            raise RoleNotFound(f"The role {name} does not exist in this server")
        await ctx.send(f"what did you say {role.mention}")

    @bot.command(hidden=True)
    @has_permissions(ban_members=True)
    async def say2(ctx, *what):
        if what == None:
            await ctx.send("Missing Arguments")
        else:
            await ctx.send(" ".join(what))

    @bot.command(hidden=True)
    @has_permissions(ban_members=True)
    async def say3(ctx, what="WHAT?", why="WHY?"):
        await ctx.send(what + why)

    @bot.command(hidden=True)
    @has_permissions(ban_members=True)
    async def link(ctx, username):
        await ctx.send(f"https://www.instagram.com/{username}/")

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
