"""@telegraph Utilities
Available Commands:
/telegraph media as reply to a media
/telegraph text as reply to a large text"""
import os
from datetime import datetime

from PIL import Image
from telegraph import Telegraph, exceptions, upload_file
from telethon import events

from DaisyX.services.telethon import tbot as borg

telegraph = Telegraph()
r = telegraph.create_account(short_name="Queer ♕")
auth_url = r["auth_url"]

# Will change later
TMP_DOWNLOAD_DIRECTORY = "./"

BOTLOG = False


@borg.on(events.NewMessage(pattern="/telegraph (media|text) ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    optional_title = event.pattern_match.group(2)
    if event.reply_to_msg_id:
        start = datetime.now()
        r_message = await event.get_reply_message()
        input_str = event.pattern_match.group(1)
        if input_str == "media":
            downloaded_file_name = await borg.download_media(
                r_message, TMP_DOWNLOAD_DIRECTORY
            )
            end = datetime.now()
            ms = (end - start).seconds
            await event.reply(
                "Downloaded to {} in {} seconds.".format(downloaded_file_name, ms)
            )
            if downloaded_file_name.endswith((".webp")):
                resize_image(downloaded_file_name)
            try:
                start = datetime.now()
                media_urls = upload_file(downloaded_file_name)
            except exceptions.TelegraphException as exc:
                await event.edit("ERROR: " + str(exc))
                os.remove(downloaded_file_name)
            else:
                end = datetime.now()
                ms_two = (end - start).seconds
                os.remove(downloaded_file_name)
                await event.reply(
                    "Uploaded to https://telegra.ph{} in {} seconds.".format(
                        media_urls[0], (ms + ms_two)
                    ),
                    link_preview=True,
                )
        elif input_str == "text":
            user_object = await borg.get_entity(r_message.sender_id)
            title_of_page = user_object.first_name  # + " " + user_object.last_name
            # apparently, all Users do not have last_name field
            if optional_title:
                title_of_page = optional_title
            page_content = r_message.message
            if r_message.media:
                if page_content != "":
                    title_of_page = page_content
                downloaded_file_name = await borg.download_media(
                    r_message, TMP_DOWNLOAD_DIRECTORY
                )
                m_list = None
                with open(downloaded_file_name, "rb") as fd:
                    m_list = fd.readlines()
                for m in m_list:
                    page_content += m.decode("UTF-8") + "\n"
                os.remove(downloaded_file_name)
            page_content = page_content.replace("\n", "<br>")
            response = telegraph.create_page(title_of_page, html_content=page_content)
            end = datetime.now()
            ms = (end - start).seconds
            await event.reply(
                "Pasted to https://telegra.ph/{} in {} seconds.".format(
                    response["path"], ms
                ),
                link_preview=True,
            )
    else:
        await event.reply("Reply to a message to get a permanent telegra.ph link. ")


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")


__mod_name__ = """
<b> Telegraph text/video upload plugin </b>
 - /telegraph media <i>reply to image or video<i> : Upload image and video directly to telegraph.
 - /telegraph text <i>reply to text</i> : upload text directly to telegraph .
"""

__mod_name__ = "Telegraph"
