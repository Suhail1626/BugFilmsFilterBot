from pyrogram.types import Message, ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant, MessageTooLong, FloodWait
from info import AUTH_CHANNEL, ADMINS, CUSTOM_FILE_CAPTION, GRP_LNK, CHNL_LNK, LOG_CHANNEL, BATCH_FILE_CAPTION, PROTECT_CONTENT, IS_VERIFY, HOW_TO_VERIFY
from database.fsub_db import Fsub_DB
from database.ia_filterdb import get_file_details
from utils import temp, get_size, verify_user, check_token, get_shortlink, send_all, check_verification, get_token
from Script import script
import json, asyncio, os, base64
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

INVITE_LINK = None
FSUB_TEMP = {}
BATCH_FILES = {}

@Client.on_chat_join_request(filters.chat(AUTH_CHANNEL))
async def fetch_reqs(bot: Client, request: ChatJoinRequest):
    await Fsub_DB().add_user(
        user_id=request.from_user.id,
        first_name=request.from_user.first_name,
        user_name=request.from_user.username,
        date=request.date
    )
    file_id = FSUB_TEMP.get(request.from_user.id)['file_id'] if FSUB_TEMP.get(request.from_user.id) else None
    ident = FSUB_TEMP.get(request.from_user.id)['ident'] if FSUB_TEMP.get(request.from_user.id) else None
    mode = FSUB_TEMP.get(request.from_user.id)['mode'] if FSUB_TEMP.get(request.from_user.id) else None
    #add these supports later ["BATCH", "DSTORE", "verify", "SHORT", "SELECT", "SENDALL"]
    if file_id and mode == 'files':
        if IS_VERIFY and not await check_verification(bot, request.from_user.id):
            btn = [[
                InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(bot, request.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
            ]]
            return await bot.send_message(
                chat_id=request.from_user.id,
                text=script.VERIFY_TXT,
                protect_content=True if PROTECT_CONTENT else False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
        files_ = await get_file_details(file_id)
        if files_:
            files = files_[0]
            title = files.file_name
            size = get_size(files.file_size)
            f_caption = files.caption
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                        file_size='' if size is None else size,
                                                        file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    f_caption = f_caption
            if f_caption is None:
                f_caption = f"{title}"
            await bot.send_cached_media(
                chat_id=request.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if ident == 'checksubp' else False,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                            InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                        ],
                        [
                            InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/creatorbeatz")
                        ]
                    ]
                )
            )
            FSUB_TEMP[request.from_user.id] = {'file_id': None, 'ident': None, 'mode': None}
    elif file_id and mode == "BATCH":
        if IS_VERIFY and not await check_verification(bot, request.from_user.id):
            btn = [[
                InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(bot, request.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id, mode)),
                InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
            ]]
            return await bot.send_message(
                chat_id=request.from_user.id,
                text=script.VERIFY_TXT,
                protect_content=True if PROTECT_CONTENT else False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
        sts = await bot.send_message(
            chat_id=request.from_user.id,
            text="<b>Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>",
            parse_mode=enums.ParseMode.HTML
        )
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await bot.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("Fᴀɪʟᴇᴅ")
                return await bot.send_message(LOG_CHANNEL, "Uɴᴀʙʟᴇ Tᴏ Oᴘᴇɴ Fɪʟᴇ.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                await bot.send_cached_media(
                    chat_id=request.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(
                        [
                         [
                          InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                          InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                       ],[
                          InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/creatorbeatz")
                         ]
                        ]
                    )
                )
            except FloodWait as e:
                logger.info(f"Floodwait of {e.x} sec.")
                await asyncio.sleep(e.x)
                await bot.send_cached_media(
                    chat_id=request.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(
                        [
                         [
                          InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                          InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                       ],[
                          InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/creatorbeatz")
                         ]
                        ]
                    )
                )
            except Exception as e:
                logger.exception(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        FSUB_TEMP[request.from_user.id] = {'file_id': None, 'ident': None, 'mode': None}
        return
    elif file_id and mode == "DSTORE":
        if IS_VERIFY and not await check_verification(bot, request.from_user.id):
            btn = [[
                InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(bot, request.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id, mode)),
                InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
            ]]
            return await bot.send_message(
                chat_id=request.from_user.id,
                text=script.VERIFY_TXT,
                protect_content=True if PROTECT_CONTENT else False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
        sts = await bot.send_message(
            chat_id=request.from_user.id,
            text="<b>Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>",
            parse_mode=enums.ParseMode.HTML
        )
        b_string = file_id
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in bot.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.error(f"Error: {e}")
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(request.from_user.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(request.from_user.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(request.from_user.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(request.from_user.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    continue
            await asyncio.sleep(1) 
        FSUB_TEMP[request.from_user.id] = {'file_id': None, 'ident': None, 'mode': None}
        return await sts.delete()
    elif file_id and mode == "verify":
        userid = file_id.split("-", 3)[0]
        token = file_id.split("-", 3)[1]
        fileid = file_id.split("-", 3)[2]
        ident = file_id.split("-", 3)[3]
        if str(request.from_user.id) != str(userid):
            return await bot.send_message(
                chat_id=request.from_user.id,
                text="<b>Iɴᴠᴀʟɪᴅ ʟɪɴᴋ ᴏʀ Exᴘɪʀᴇᴅ ʟɪɴᴋ !</b>",
                protect_content=True if PROTECT_CONTENT else False
            )
        is_valid = await check_token(bot, userid, token)
        FSUB_TEMP[request.from_user.id] = {'file_id': None, 'ident': None, 'mode': None}
        if is_valid == True:
            btn = [[
                InlineKeyboardButton("Get File", url=f"https://telegram.me/{temp.U_NAME}?start={ident}_{fileid}" if ident == 'files' else f"https://telegram.me/{temp.U_NAME}?start={ident}-{fileid}")
            ]]
            await bot.send_message(
                chat_id=request.from_user.id,
                text=script.SUCC_VERIFY.format(request.from_user.first_name),
                protect_content=True if PROTECT_CONTENT else False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await verify_user(bot, userid, token)
            return
        else:
            return await bot.send_message(
                chat_id=request.from_user.id,
                text="<b>Iɴᴠᴀʟɪᴅ ʟɪɴᴋ ᴏʀ Exᴘɪʀᴇᴅ ʟɪɴᴋ !</b>",
                protect_content=True if PROTECT_CONTENT else False
            )
    elif file_id and mode == "SHORT":
        msg_id = file_id.split("-", 1)[0]
        chatid = file_id.split("-", 1)[1]
        link = await get_shortlink(chat_id=chatid, link=f"https://telegram.me/{temp.U_NAME}?start=SENDALL-{msg_id}")
        FSUB_TEMP[request.from_user.id] = {'file_id': None, 'ident': None, 'mode': None}
        return await bot.send_message(
            chat_id=int(request.from_user.id),
            text=f"<b>Hᴇʀᴇ Is Yᴏᴜʀ Lɪɴᴋ Tᴏ Gᴇᴛ Tʜᴇ Fɪʟᴇs {link}</b>",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif file_id and mode == "SENDALL":
        if IS_VERIFY and not await check_verification(bot, request.from_user.id):
            btn = [[
                InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(bot, request.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id, mode)),
                InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
            ]]
            return await bot.send_message(
                chat_id=request.from_user.id,
                text=script.VERIFY_TXT,
                protect_content=True if PROTECT_CONTENT else False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
        msg_id = file_id
        files = temp.SEND_ALL_TEMP.get(int(msg_id))['files']
        userid = temp.SEND_ALL_TEMP.get(int(msg_id))['id']
        is_over = await send_all(bot, userid, files, 'file')
        FSUB_TEMP[request.from_user.id] = {'file_id': None, 'ident': None, 'mode': None}
        if is_over == 'done':
            return await bot.send_message(request.from_user.id, f"Hᴇʏ, Aʟʟ ғɪʟᴇs ᴏɴ ᴛʜᴇ sᴇʟᴇᴄᴛᴇᴅ ᴘᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ !")
        else:
            return await bot.send_message(request.from_user.id, f"Eʀʀᴏʀ: {is_over}")
    else:
        logger.debug(f"Something went wrong. Possibly due to missing file ID or unmatched mode value. \n\nMode: {mode}\n\nFile ID: {file_id}")
        return

@Client.on_message(filters.command("total_reqs") & filters.private & filters.user(ADMINS))
async def total_requests(bot: Client, message: Message):
    total = await Fsub_DB().total_users()
    await message.reply_text(
        text=f"<b>The total number of requests is {total}</b>",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("delete_reqs") & filters.private & filters.user(ADMINS))
async def purge_reqs(bot: Client, message: Message):
    total = await Fsub_DB().total_users()
    await Fsub_DB().purge_all()
    await message.reply_text(
        text=f"<b>Successfully deleted all {total} join requests from DB.</b>",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("get_req") & filters.private & filters.user(ADMINS))
async def fetch_request(bot: Client, message: Message):
    try:
        id = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(
            text="<b>Please give me a user ID to search.</b>",
            parse_mode=enums.ParseMode.HTML
        )
    user = await Fsub_DB().get_user(int(id))
    if user:
        return await message.reply_text(
            text=f"<b>ID: {user['id']}\nFirst Name: {user['fname']}\nUserName: {user['uname']}\nDate: {user['date']}</b>",
            parse_mode=enums.ParseMode.HTML
        )
    else:
        return await message.reply_text(
            text="<b>No such user found !</b>",
            parse_mode=enums.ParseMode.HTML
        )
    
@Client.on_message(filters.command("delete_req") & filters.private & filters.user(ADMINS))
async def delete_request(bot: Client, message: Message):
    try:
        id = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(
            text="<b>Please give me a user ID to delete.</b>",
            parse_mode=enums.ParseMode.HTML
        )
    user = await Fsub_DB().get_user(int(id))
    if not user:
        return await message.reply_text(
            text="<b>No such user found !</b>",
            parse_mode=enums.ParseMode.HTML
        )
    await Fsub_DB().delete_user(int(id))
    return await message.reply_text(
        text=f"<b>Successfully deleted {user['fname']} from DB.</b>",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("fetch_reqs") & filters.private & filters.user(ADMINS))
async def fetch_all_reqs(bot: Client, message: Message):
    txt = await message.reply_text("Processing...")
    requests = await Fsub_DB().get_all()
    msg = "These are the Join Requests saved on DB:\n\n"
    for request in requests:
        msg+=f"ID: {request['id']}\nFirst Name: {request['fname']}\nUserName: {request['uname']}\nDate: {request['date']}\n\n"
    try:
        await txt.edit_text(text=msg)
    except MessageTooLong:
        with open("Requests.txt", "w+") as outputFile:
            outputFile.write(msg)
        await message.reply_document(document="Requests.txt", caption="List of all Join Requests saved on DB.")

async def Force_Sub(bot: Client, message: Message, file_id = None, ident = "checksub", mode='files'):
    global INVITE_LINK
    if not AUTH_CHANNEL:
        return True
    try:
        user = await Fsub_DB().get_user(int(message.from_user.id))
        if user:
            return True
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply_text(f"Error: {e}")
        return False
    try:
        await bot.get_chat_member(
            chat_id=AUTH_CHANNEL,
            user_id=message.from_user.id
        )
        return True
    except UserNotParticipant:
        try:
            if INVITE_LINK is None:
                link = await bot.create_chat_invite_link(
                    chat_id=AUTH_CHANNEL, 
                    creates_join_request=True
                )
                INVITE_LINK = link
                logger.info("Invite Link Generated !")
            else:
                link = INVITE_LINK
        except Exception as e:
            logger.error(f"Unable to generate invite link !\nError: {e}")
            return False
        btn = [[
            InlineKeyboardButton("❆ Jᴏɪɴ Oᴜʀ Bᴀᴄᴋ-Uᴘ Cʜᴀɴɴᴇʟ ❆", url=link.invite_link)
        ]]
        FSUB_TEMP[message.from_user.id] = {'file_id': file_id, 'ident': ident, 'mode': mode}
        await message.reply(
            text=script.FSUB_TXT,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.HTML
        )
        return False