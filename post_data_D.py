### post_data_D
### functions to get post data with downloading/deleting
### any image data will remain permanently in the post


import os
import instaloader
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from datetime import datetime

private_server_id = 385825313323483146
private_server_target_role_id = 385826570377625601


async def lastpost_downloadv(bot, logger, last_post, last_post_author, ctx, username, channel_id: int, role_id: int):

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

                return last_post


        files = os.listdir()
        if profile_pic_path in files:
            os.remove(profile_pic_path)
        if post_image_path in files:
            os.remove(post_image_path)

        logger.info(f"No unpinned posts found for {username}.")
        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
        await ctx.send(f"No unpinned posts found for {username}.")

        return last_post

    except Exception as e:
        files = os.listdir()
        if profile_pic_path in files:
            os.remove(profile_pic_path)
        if post_image_path in files:
            os.remove(post_image_path)

        logger.error(f"An error occurred: {e}")
        logger.info("Time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " (EST)\n")
        await ctx.send(f"An error occurred: {e}")










async def post_check_downloadv(bot, logger, last_post, last_post_author, global_ctx, global_username, global_channel_id, global_role_id):


        picDownload, picDownload2 = False, False

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

                        role2 = discord.utils.get(global_ctx.guild.roles, id=global_role_id)

                        await target_channel.send(f" {role2.mention} New post on {fullname}'s Instagram!", embed=e, files=[discord.File(profile_pic_path), discord.File(post_image_path)])

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