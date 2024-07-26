import os
import aiohttp
import instaloader
import settings
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from datetime import datetime
#from instagrapi import Client


logger = settings.logging.getLogger("bot")

instaloader_logger = settings.logging.getLogger('instaloader')
instaloader_logger.setLevel(settings.logging.WARNING)

last_post = None
last_post_author = None

private_server_id = 385825313323483146
private_server_target_role_id = 385826570377625601


global_ctx = None
global_username = None
global_channel_id = None
global_role_id = None


class RoleNotFound(Exception):
    pass


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="]", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})\n")

        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Mozart 🧐'))
        #await bot.tree.sync()
        #post_check_task.start()

    
    @bot.event
    async def on_command_error(ctx, error): 
        if isinstance(error, commands.MissingRequiredArgument):
            missing_param = error.param 
            command_name = ctx.command.name
            await ctx.send(f"Error: {missing_param} parameter is missing in the function {command_name}! For more information, do ]help {command_name}.")
        elif isinstance(error, RoleNotFound):
            await ctx.send(error)
        else:
            await ctx.send(f"Error: {error}")


    @bot.command(
        brief = "Starts post checker"
    )
    @has_permissions(ban_members=True)
    async def start_postchecker(ctx, username, channel_id: int, role_id: int):
        if not post_check_task.is_running():

            ### FIX
            ### MAKE GLOBALS
            global global_ctx 
            global global_username 
            global global_channel_id 
            global global_role_id

            global_ctx = ctx
            global_username = username
            global_channel_id = channel_id
            global_role_id = role_id

            post_check_task.start()
            logger.info("Starting post checker task.")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
        else:
            logger.info("Cannot start post checker task. Post checker task is already running.")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")


    @bot.command(
        brief = "Immediatedly cancels post checker"
    )
    @has_permissions(ban_members=True)
    async def cancel_postchecker(ctx):
        if post_check_task.is_running():
            post_check_task.cancel()
            logger.info("Canceling post checker task.")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
        else:
            logger.info("Cannot cancel post checker task. Post checker task is not running.")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")


    @bot.command(
        brief = "Pauses post checker after the next iteration"
    )
    @has_permissions(ban_members=True)
    async def stop_postchecker(ctx):
        if post_check_task.is_running():
            post_check_task.stop()
            logger.info("Stopping post checker task. Task will run for one more iteration before being pasued.")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
        else:
            logger.info("Cannot stop post checker task. Post checker task is not running.")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")



    @bot.command(
        aliases=['p'],
        help="This is help",
        description="This is description",
        brief = "This is brief",
        enabled=True,
        hidden=True
    )
    @has_permissions(ban_members=True)
    async def ping(ctx, test: int):
        """ Answers with pong 
        
        Arguments:
        test      This is the help message for test.
        """
        await ctx.send("pong")



    @bot.hybrid_command(
        hidden = True
    )
    async def testslash(ctx):
        await ctx.send("ping")



    @bot.command(
        hidden=True
    )
    @has_permissions(ban_members=True)
    async def test_command(ctx):
        e = discord.Embed(
            title="testing",
            description="test description",
            url="https://www.google.com/",
            color=0x27C4D8,)
        role = discord.utils.get(ctx.guild.roles, name='Discord Manager')
        await ctx.send(f" {role.mention} New post on x's instagram", embed=e)

        guild = bot.get_guild



    @bot.command(
        hidden=True
    )
    @has_permissions(ban_members=True)
    async def say(ctx, what = "Command Needs Input!"):
        name = 'Discord Manager'
        role = discord.utils.get(ctx.guild.roles, name = name)
        if role is None:
            raise RoleNotFound(f"The role {name} does not exist in this server")
        await ctx.send(f"what did you say {role.mention}")



    @bot.command(
        hidden=True
    )
    @has_permissions(ban_members=True)
    async def say2(ctx, *what):
        if what == None:
            await ctx.send("Missing Arguments")
        else:
            await ctx.send(" ".join(what))



    @bot.command(
        hidden=True
    )
    @has_permissions(ban_members=True)
    async def say3(ctx, what = "WHAT?", why = "WHY?"):
        await ctx.send(what + why)



    @bot.command(
        hidden=True
    )
    @has_permissions(ban_members=True)
    async def link(ctx, username):
        await ctx.send(f"https://www.instagram.com/{username}/")



    # if the post checker is running, stops it, prints the last post at the current moment (regardless if it has been previously posted).
    # finally, if the post checker was stopped in the function, it will restart it at the end
    @bot.command(
        brief = "Prints the current last post of designated account"
    )
    @has_permissions(ban_members=True)
    async def lastpost(ctx, username, channel_id: int, role_id: int):
        # user = InstagramUser(username)
        # print(user.data)
        # latest_post = user.posts[0]
        # last_post_id = latest_post['shortcode']
        # post_url = f"https://www.instagram.com/p/{last_post_id}/"
        # await ctx.send(f"New post from {username}: {post_url}")

        # headers = {
        #     "Host": "www.instagram.com",
        #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 "
        #     "Safari/537.11 ",
        # }

        # async with aiohttp.ClientSession() as session:
        #     async with session.get(
        #         "https://www.instagram.com/" + username + "/feed/?__a=1",
        #         headers=headers,
        #     ) as r:
        #         response = await r.json()
        
        # last_post = response["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]

        # post_url = "https://www.instagram.com/" + "p/" + last_post["shortcode"]

        # await ctx.send(f"New post from {username}: {post_url}")
        global last_post
        global last_post_author

    

        # task_stopped = False

        # if post_check_task.is_running():
        #     task_stopped = True
        #     last_post = None
        #     logger.info("Stopping post checker task")
        #     logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
        #     post_check_task.stop()  

        target_channel = bot.get_channel(channel_id)


        L = instaloader.Instaloader()

        try:
            profile = instaloader.Profile.from_username(L.context, username)

            profile_pic_url = profile.profile_pic_url
            fullname = profile.full_name
            
            for post in profile.get_posts():
                if not post.is_pinned:
                    post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                    caption = post.caption
                    comments = post.comments
                    likes = post.likes
                    date = post.date


                    if username == last_post_author:
                        last_post = date
                        logger.info("lastpost called on same author as post checker, adjusting last_post value")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")


                    if post.typename == "GraphSidecar":
                        sidecar_nodes = list(post.get_sidecar_nodes())
                        if sidecar_nodes:
                            top_image_url = sidecar_nodes[0].display_url
                        else:
                            top_image_url = None
                    else:
                        top_image_url = post.url

                    
                    e = discord.Embed(
                        title = f"New Instagram post published on {date}",
                        description=caption,
                        url=post_url,
                        color=0x40E0D0,
                    )

                    e.set_image(url=top_image_url)
                    e.set_footer(text=f"❤️ {likes} | 💬 {comments}")
                    e.set_author(name=username, icon_url = profile_pic_url, url="https://www.instagram.com/" + username)

                    #await ctx.send(embed=e)
                    role = discord.utils.get(ctx.guild.roles, id=role_id)
                    logger.info("Manually sent last post")
                    logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                    await target_channel.send(f" {role.mention} New post on {fullname}'s Instagram!", embed=e)

                    # if task_stopped:
                    #     task_stopped = False
                    #     logger.info("lastpost: Restarting post checker task")
                    #     logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                    #     post_check_task.start()
                        

                    return

            logger.info(f"No unpinned posts found for {username}.")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
            await ctx.send(f"No unpinned posts found for {username}.")

            # if task_stopped:
            #     task_stopped = False
            #     logger.info("lastpost: Restarting post checker task")
            #     logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
            #     post_check_task.start()
            return

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
            await ctx.send(f"An error occurred: {e}")

            # if task_stopped:
            #     task_stopped = False
            #     logger.info("lastpost: Restarting post checker task")
            #     logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
            #     post_check_task.start()


    async def post_check(username):

        global last_post
        global last_post_author

        last_post_author = username

        private_server_target_channel = bot.get_channel(385829067225825282)

        L = instaloader.Instaloader()

        try:
            profile = instaloader.Profile.from_username(L.context, username)

            profile_pic_url = profile.profile_pic_url
            fullname = profile.full_name
            
            for post in profile.get_posts():
                if not post.is_pinned:

                    # first iteration
                    if last_post == None:                   
                        last_post = post.date
                        logger.info("No new post found (first iteration)")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                        return
                    # new post
                    elif last_post != post.date:
                        last_post = post.date

                        post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                        caption = post.caption
                        comments = post.comments
                        likes = post.likes
                        date = post.date

                        if post.typename == "GraphSidecar":
                            sidecar_nodes = list(post.get_sidecar_nodes())
                            if sidecar_nodes:
                                top_image_url = sidecar_nodes[0].display_url
                            else:
                                top_image_url = None
                        else:
                            top_image_url = post.url

                        
                        e = discord.Embed(
                            title = f"New Instagram post published on {date}",
                            description=caption,
                            url=post_url,
                            color=0x40E0D0,
                        )

                        e.set_image(url=top_image_url)
                        e.set_footer(text=f"❤️ {likes} | 💬 {comments}")
                        e.set_author(name=username, icon_url = profile_pic_url, url="https://www.instagram.com/" + username)

                        # get channel next
                        logger.info("New Post Found")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                        guild = bot.get_guild(private_server_id)
                        if guild:
                            role = guild.get_role(private_server_target_role_id)
                            await private_server_target_channel.send(f" {role.mention} New post on {fullname}'s Instagram!", embed=e)
                        #role = discord.utils.get(ctx.guild.roles, name='Discord Manager')
                        
                        #await channel.send(embed=e)
                        #await ctx.send(embed=e)

                        return
                    else:
                        logger.info("Most recent post is not new. No new posts found")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                        return

            #await private_server_target_channel.send(f"No unpinned posts found for {username}.")
            await logger.info(f"No unpinned posts found for {username}.\n")
        except Exception as e:
            #await private_server_target_channel.send(f"An error occurred: {e}")
            await logger.error(f"An error occurred: {e}\n")

    @tasks.loop(minutes=20)
    async def post_check_task():
        logger.info("Beginning post_check call")
        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
        await post_check_downloadv() 

    @post_check_task.before_loop
    async def before_post_check_task():
        logger.info("Waiting until bot is ready to begin post_check loop")
        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
        await bot.wait_until_ready()

    # @tree.command(name="testslash", description="A simple ping command")
    # async def slash_ping(interaction: discord.Interaction):
    #     """ Answers with pong. """
    #     await interaction.response.send_message("pong")
            



    # if the post checker is running, stops it, prints the last post at the current moment (regardless if it has been previously posted).
    # finally, if the post checker was stopped in the function, it will restart it at the end
    #
    # downloads the image in post (if there is any) and profile picture locally, and uses that instead of url
    # this is b/c url will expire after few days and images will not load
    @bot.command(
        brief = "Prints the current last post of designated account"
    )
    @has_permissions(ban_members=True)
    async def lastpost_downloadv(ctx, username, channel_id: int, role_id: int):

        global last_post
        global last_post_author

        target_channel = bot.get_channel(channel_id)


        L = instaloader.Instaloader()

        try:
            profile = instaloader.Profile.from_username(L.context, username)

            profile_pic_path = f"{username}_profile_pic"
            file_extension = "jpg"
            profile_pic_url = profile.profile_pic_url
            fullname = profile.full_name

            picDownload = L.download_pic(profile_pic_path, profile_pic_url, datetime.now())
            if picDownload == False:
                print("\n")
                logger.error("lastpost: profile picture not downloaded")
                logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                return
            else:
                print("\n")
                logger.info("lastpost: profile picture successfully downloaded")
                logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")


            for file in os.listdir():
                if file.startswith(profile_pic_path):
                    profile_pic_path = file
                    break

            
            for post in profile.get_posts():
                if not post.is_pinned:
                    post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                    caption = post.caption
                    comments = post.comments
                    likes = post.likes
                    date = post.date


                    if username == last_post_author:
                        last_post = date
                        logger.info("lastpost called on same author as post checker, adjusting last_post value")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")


                    if post.typename == "GraphSidecar":
                        sidecar_nodes = list(post.get_sidecar_nodes())
                        if sidecar_nodes:
                            top_image_url = sidecar_nodes[0].display_url
                        else:
                            top_image_url = None
                    else:
                        top_image_url = post.url


                    post_image_path = f"{username}_post_image"
                    picDownload2 = L.download_pic(post_image_path, top_image_url, datetime.now())
                    if picDownload2 == False:
                        print("\n")
                        logger.error("lastpost: post image not downloaded")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                        return
                    else:
                        print("\n")
                        logger.info("lastpost: post image successfully downloaded")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")

                    for file in os.listdir():
                        if file.startswith(post_image_path):
                            post_image_path = file
                            break

                    
                    e = discord.Embed(
                        title = f"New Instagram post published on {date}",
                        description=caption,
                        url=post_url,
                        color=0x40E0D0,
                    )

                    print(f"Profile pic file: {profile_pic_path}")
                    print(f"Post image file: {post_image_path} \n")

                    #post_image_path = post_image_path+"."+file_extension
                    #profile_pic_path = profile_pic_path+"."+file_extension

                    e.set_image(url="attachment://" + post_image_path)
                    e.set_footer(text=f"❤️ {likes} | 💬 {comments}")
                    e.set_author(name=username, icon_url = "attachment://" + profile_pic_path, url="https://www.instagram.com/" + username)


                    role = discord.utils.get(ctx.guild.roles, id=role_id)
                    logger.info("Manually sent last post")
                    logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                    await target_channel.send(f" {role.mention} New post on {fullname}'s Instagram!", embed=e, files=[discord.File(profile_pic_path), discord.File(post_image_path)])
                        
                    files = os.listdir()
                    if profile_pic_path in files:
                        os.remove(profile_pic_path)
                    if post_image_path in files:
                        os.remove(post_image_path)

                    return


            files = os.listdir()
            if profile_pic_path in files:
                os.remove(profile_pic_path)
            if post_image_path in files:
                os.remove(post_image_path)

            logger.info(f"No unpinned posts found for {username}.")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
            await ctx.send(f"No unpinned posts found for {username}.")

            return

        except Exception as e:
            files = os.listdir()
            if profile_pic_path in files:
                os.remove(profile_pic_path)
            if post_image_path in files:
                os.remove(post_image_path)

            logger.error(f"An error occurred: {e}")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
            await ctx.send(f"An error occurred: {e}")




    


    async def post_check_downloadv():

        global global_ctx 
        global global_username 
        global global_channel_id 
        global global_role_id

        picDownload, picDownload2 = False, False

        #profile_pic_path 
        #post_image_path

        global last_post
        global last_post_author

        last_post_author = global_username

        private_server_target_channel = bot.get_channel(385829067225825282)

        target_channel = bot.get_channel(global_channel_id)

        L = instaloader.Instaloader()

        try:
            profile = instaloader.Profile.from_username(L.context, global_username)

            profile_pic_url = profile.profile_pic_url
            fullname = profile.full_name
            profile_pic_path = f"{global_username}_profile_pic_loop"


            picDownload = L.download_pic(profile_pic_path, profile_pic_url, datetime.now())
            print("\n")
            if picDownload == False:
                logger.error("post_check: profile picture not downloaded")
                logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                return
            else:
                logger.info("post_check: profile picture successfully downloaded")
                logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")


            for file in os.listdir():
                if file.startswith(profile_pic_path):
                    profile_pic_path = file
                    break


            
            for post in profile.get_posts():
                if not post.is_pinned:

                    # first iteration
                    if last_post == None:                   
                        last_post = post.date
                        logger.info("No new post found (first iteration)")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")

                        files = os.listdir()
                        if profile_pic_path and profile_pic_path in files:
                            os.remove(profile_pic_path)
                        # if post_image_path and post_image_path in files:
                        #     os.remove(post_image_path)
                        picDownload = False

                        return
                    # new post
                    elif last_post != post.date:
                        last_post = post.date

                        post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                        caption = post.caption
                        comments = post.comments
                        likes = post.likes
                        date = post.date

                        if post.typename == "GraphSidecar":
                            sidecar_nodes = list(post.get_sidecar_nodes())
                            if sidecar_nodes:
                                top_image_url = sidecar_nodes[0].display_url
                            else:
                                top_image_url = None
                        else:
                            top_image_url = post.url

                        
                        post_image_path = f"{global_username}_post_image_loop"
                        picDownload2 = L.download_pic(post_image_path, top_image_url, datetime.now())
                        print("\n")
                        if picDownload2 == False:
                            logger.error("post_check: post image not downloaded")
                            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                            return
                        else:
                            logger.info("post_check: post image successfully downloaded")
                            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")

                        for file in os.listdir():
                            if file.startswith(post_image_path):
                                post_image_path = file
                                break

                        
                        e = discord.Embed(
                            title = f"New Instagram post published on {date}",
                            description=caption,
                            url=post_url,
                            color=0x40E0D0,
                        )

                        print(f"Profile pic file: {profile_pic_path}")
                        print(f"Post image file: {post_image_path} \n")

                        e.set_image(url="attachment://" + post_image_path)
                        e.set_footer(text=f"❤️ {likes} | 💬 {comments}")
                        e.set_author(name=global_username, icon_url = "attachment://" + profile_pic_path, url="https://www.instagram.com/" + global_username)


                        # get channel next
                        logger.info("New Post Found")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                        guild = bot.get_guild(private_server_id)
                        if guild:
                            role = guild.get_role(private_server_target_role_id)
                            await private_server_target_channel.send(f" {role.mention} New post on {fullname}'s Instagram!", embed=e, files=[discord.File(profile_pic_path), discord.File(post_image_path)])
                        #role = discord.utils.get(ctx.guild.roles, name='Discord Manager')

                        role2 = discord.utils.get(global_ctx.guild.roles, id=global_role_id)

                        await target_channel.send(f" {role2.mention} New post on {fullname}'s Instagram!", embed=e, files=[discord.File(profile_pic_path), discord.File(post_image_path)])
                        
                        #await channel.send(embed=e)
                        #await ctx.send(embed=e)

                        files = os.listdir()
                        if profile_pic_path and profile_pic_path in files:
                            os.remove(profile_pic_path)
                        if post_image_path and post_image_path in files:
                            os.remove(post_image_path)
                        picDownload, picDownload2 = False, False

                        return
                    else:
                        logger.info("Most recent post is not new. No new posts found")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")

                        files = os.listdir()
                        if profile_pic_path and profile_pic_path in files:
                            os.remove(profile_pic_path)
                        # if post_image_path and post_image_path in files:
                        #     os.remove(post_image_path)
                        picDownload = False
                        return

            files = os.listdir()
            if picDownload and profile_pic_path in files:
                os.remove(profile_pic_path)
            if picDownload2 and post_image_path in files:
                os.remove(post_image_path)

            logger.info(f"No unpinned posts found for {global_username}.")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
            await global_ctx.send(f"No unpinned posts found for {global_username}.")
        except Exception as e:
            files = os.listdir()
            if picDownload and profile_pic_path in files:
                os.remove(profile_pic_path)
            if picDownload2 and post_image_path in files:
                os.remove(post_image_path)

            logger.error(f"An error occurred: {e}")
            logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
            await global_ctx.send(f"An error occurred: {e}")







    bot.run(settings.DISCORD_API_SECRET, root_logger=True)

if __name__ == "__main__":
    run()