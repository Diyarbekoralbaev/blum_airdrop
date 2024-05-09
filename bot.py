import asyncio
import logging
import sys
from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, WebAppInfo
from aiogram.types import User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.deep_linking import decode_payload, create_start_link
from aiogram.dispatcher.middlewares.base import BaseMiddleware

class CheckUserJoinedToChannel(BaseMiddleware):
    async def on_pre_process_message(self, message: Message, data: dict):
        channel_id = os.getenv("CHANNEL_ID")
        try:
            chat_member = await message.bot.get_chat_member(channel_id, message.from_user.id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                await message.answer("Please join the channel to use the bot!", reply_markup=F.inline_button("Join channel", url=os.getenv("CHANNEL_LINK")))
                return False
        except Exception as e:
            await message.answer("Oops! Something went wrong. Please try again later.")
            return False
from database import Database

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
WEBSITE_URL = os.getenv("WEBSITE_URL")

dp = Dispatcher()

async def check_premium(user: User) -> str:
    if user.is_premium:
        return True
    else:
        return False

def webapp_builder(user_hash) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Let's click!",
        web_app=WebAppInfo(
            url=f"{WEBSITE_URL}/?hash={user_hash}",
            width=600,
            height=800,
        ),
    )
    return builder.as_markup()


@dp.message(CommandStart(deep_link=True))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    db = Database()
    user = db.tg_get_user(message.from_user.id)
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    
    # If the user is new, add them to the database
    if user is None:
        db.tg_add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)

        hash_code = db.tg_get_user_hash(message.from_user.id)[0]
        await message.answer("You have been added to the database!", reply_markup=webapp_builder(hash_code))
        if await check_premium(message.from_user):
            await message.answer("You are a premium user! and you will get 50000 coins as a bonus")
            db.tg_update_balance(message.from_user.id, 50000)
        else:
            await message.answer("You are not a premium user!, you will get 25000 coins as a bonus")
            db.tg_update_balance(message.from_user.id, 25000)
        await message.answer(f"Your hash: <code>{hash_code}</code>", parse_mode=ParseMode.HTML)
        args = str(command.args)
        payload = decode_payload(args)
        referrer_id = int(payload)
        if referrer_id != message.from_user.id:
            db.add_referral(referrer_id, message.from_user.id)
            await message.answer("You were referred by user ID: {}".format(referrer_id))
            await bot.send_message(referrer_id, f"User ID: {message.from_user.id} has been referred by you!, and you will get 25000 coins as a bonus")
            db.tg_update_balance(referrer_id, 25000)
        else:
            await message.answer("You cannot refer yourself!")
            
    else:
        # If the user already exists, optionally regenerate their hash
        regenerate_hash = db.regenerate_hash(message.from_user.id)
        await message.answer("You are already in the database!", reply_markup=webapp_builder(regenerate_hash[0]))
        await message.answer(f"Your hash: <code>{regenerate_hash[0]}</code>", parse_mode=ParseMode.HTML)

    db.close()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    db = Database()
    user = db.tg_get_user(message.from_user.id)
    
    # If the user is new, add them to the database
    if user is None:
        db.tg_add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
        hash_code = db.tg_get_user_hash(message.from_user.id)[0]
        await message.answer("You have been added to the database!", reply_markup=webapp_builder(hash_code))
        if await check_premium(message.from_user):
            await message.answer("You are a premium user! and you will get 50000 coins as a bonus")
            db.tg_update_balance(message.from_user.id, 50000)
        else:
            await message.answer("You are not a premium user!, you will get 25000 coins as a bonus")
            db.tg_update_balance(message.from_user.id, 25000)
        await message.answer(f"Your hash: <code>{hash_code}</code>", parse_mode=ParseMode.HTML)
    else:
        # If the user already exists, optionally regenerate their hash
        regenerate_hash = db.regenerate_hash(message.from_user.id)
        await message.answer("You are already in the database!", reply_markup=webapp_builder(regenerate_hash[0]))
        await message.answer(f"Your hash: <code>{regenerate_hash[0]}</code>", parse_mode=ParseMode.HTML)

    db.close()

    

@dp.message(Command("profile"))
async def command_profile_handler(message: Message) -> None:
    db = Database()
    user = db.tg_get_user(message.from_user.id)
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    if user:
        referal_link = await create_start_link(bot=bot, payload=user[1], encode=True)
        get_all_referrals = db.get_referrals(message.from_user.id)
        response_message = (
            f"Your profile:\n"
            f"Name: {user[2]}\n"
            f"Username: {user[3]}\n"
            f"Balance: {user[4]}\n"
            f"Referal link: {referal_link}\n\n"
            f"Your referrals: {len(get_all_referrals)}"
        )
        await message.answer(response_message, parse_mode=ParseMode.HTML)
    else:
        await message.answer("Something went wrong. Please try again later.")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())