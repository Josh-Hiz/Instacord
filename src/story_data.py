import os
from datetime import datetime

import discord
import instaloader

###
###
### NEEDS LOGIN INFO TO WORK
###
###


#
# Print all current stories for a user
#
async def allstory(ctx, bot, logger, username: str, channel_id: int, role_id: int):

    L = instaloader.Instaloader()

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        full_name = profile.full_name
        user_id = profile.userid

        # Getting profile picture
        profile_pic_path = f"{username}_{channel_id}_profile_pic"
        profile_pic_url = profile.profile_pic_url
        picDownload = L.download_pic(profile_pic_path, profile_pic_url, datetime.now())
        if picDownload == False:
            print("\n")
            logger.error("allstory: profile picture not downloaded")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
            return
        else:
            print("\n")
            logger.info("allstory: profile picture successfully downloaded")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
        for file in os.listdir():
            if file.startswith(profile_pic_path):
                profile_pic_path = file
                break

        has_stories = False

        for story in L.get_stories(userids=[user_id]):
            for item in story.get_items():
                has_stories = True

                ### Story is a video
                if item.is_video:
                    image_path = f"{username}_{channel_id}_story"
                    picDownload2 = L.download_pic(image_path, item.url, item.date_local)
                    if picDownload2 == False:
                        print("\n")
                        logger.error("allstory: video thumbnail not downloaded")
                        logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
                        return
                    else:
                        print("\n")
                        logger.info("allstory: video thumbnail successfully downloaded")
                        logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
                    for file in os.listdir():
                        if file.startswith(image_path):
                            image_path = file
                            break
                ### Story is an image
                else:
                    image_path = f"{username}_{channel_id}_story"
                    picDownload2 = L.download_storyitem(item, target=f"{username}_{channel_id}_story")
                    if picDownload2 == False:
                        print("\n")
                        logger.error("allstory: story image not downloaded")
                        logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
                        return
                    else:
                        print("\n")
                        logger.info("allstory: story image successfully downloaded")
                        logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
                    for file in os.listdir():
                        if file.startswith(image_path):
                            image_path = file
                            break

                ### Print the story

                e = discord.Embed(
                    title=f"New Instagram story published on {item.date}",
                    url=f"https://www.instagram.com/stories/{username}",
                    color=0xEF04D9,
                    description=f"Story will expire at {item.expiring_utc} (UTC)",
                )

                e.set_image(url=f"attachment://{image_path}")
                e.set_author(
                    name=username,
                    icon_url=f"attachment://{profile_pic_path}",
                    url=f"https://www.instagram.com/{username}",
                )

                target_channel = await bot.get_channel(channel_id)
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                await target_channel.send(
                    f"{role.mention} New story on {full_name}'s Instagram!",
                    embed=e,
                    files=[discord.File(profile_pic_path), discord.File(image_path)],
                )
                logger.info(f"Manually sent story from {username}")
                logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")

                files = os.listdir()
                if picDownload2 and image_path in files:
                    os.remove(image_path)

        if not has_stories:
            target_channel = bot.get_channel(channel_id)
            await target_channel.send(f"There are no current stories on {full_name}'s account.")
            logger.info(f"{username} has no current stories.")
            logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")

        files = os.listdir()
        if picDownload and profile_pic_path in files:
            os.remove(profile_pic_path)

    except Exception as e:
        files = os.listdir()
        if picDownload and profile_pic_path in files:
            os.remove(profile_pic_path)
        if picDownload2 and image_path in files:
            os.remove(image_path)
        logger.error(f"An error occurred: {e}")
        logger.info("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (EST)\n")
        await ctx.send(f"An error occurred: {e}")
