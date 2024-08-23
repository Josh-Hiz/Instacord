
### post_data_ND
### functions to get post data without any downloading/deleting
### any image data will only temporarily remain in the post (48-168 hours, 2-7 days)

### to activate this files' post checker version, must replace function call in post_check_task() in main.py


import instaloader
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from datetime import datetime


async def lastpost(ctx, username, channel_id: int, role_id: int, bot, logger, last_post, last_post_author):

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

                role = discord.utils.get(ctx.guild.roles, id=role_id)
                logger.info("Manually sent last post")
                logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                await target_channel.send(f" {role.mention} New post on {fullname}'s Instagram!", embed=e)


                return last_post

        logger.info(f"No unpinned posts found for {username}.")
        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
        await ctx.send(f"No unpinned posts found for {username}.")

        return last_post

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
        await ctx.send(f"An error occurred: {e}")



async def post_check(bot, logger, last_post, last_post_author, global_ctx, global_username, global_channel_id, global_role_id):

        last_post_author = global_username


        target_channel = bot.get_channel(global_channel_id)

        L = instaloader.Instaloader()

        try:
            profile = instaloader.Profile.from_username(L.context, global_username)

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
                        e.set_author(name=global_username, icon_url = profile_pic_url, url="https://www.instagram.com/" + global_username)

                        # get channel next
                        logger.info("New Post Found")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")

                        role2 = discord.utils.get(global_ctx.guild.roles, id=global_role_id)

                        await target_channel.send(f" {role2.mention} New post on {fullname}'s Instagram!", embed=e)
                
                        #role = discord.utils.get(ctx.guild.roles, name='Discord Manager')
                        
                        #await channel.send(embed=e)
                        #await ctx.send(embed=e)

                        return
                    else:
                        logger.info("Most recent post is not new. No new posts found")
                        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
                        return

            await logger.info(f"No unpinned posts found for {global_username}.\n")
        except Exception as e:
            await logger.error(f"An error occurred: {e}\n")