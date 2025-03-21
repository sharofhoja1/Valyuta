import logging
import httpx
from aiogram import types, Bot, Dispatcher
from aiogram.utils import executor
from api import CURRENCIES, URL, text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7706086807:AAEzbDH0P_YVf6Wso0ATC6k_RzBDOSivC6s'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_selected_currency = {}

@dp.message_handler(commands='start')
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kalkulyator", callback_data="calc"),
         InlineKeyboardButton(text="Yangilash", callback_data="refresh")]
    ])
    await message.answer(text, reply_markup=keyboard)


async def get_currency_rates():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(URL)
            data = response.json()
            return {item['Ccy']: float(item['Rate']) for item in data}
    except Exception as e:
        logging.error(f"API xatosi: {e}")
        return None

@dp.callback_query_handler(lambda query: query.data == 'calc')
async def calc_callback(query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(f"{CURRENCIES[c]} {c}", callback_data=f"currency_{c}") for c in CURRENCIES]
    keyboard.add(*buttons)
    await query.message.edit_text("Qaysi valyutani hisoblashni xohlaysiz?", reply_markup=keyboard)

@dp.callback_query_handler(lambda query: query.data.startswith("currency_"))
async def currency_selected(query: types.CallbackQuery):
    currency = query.data.split("_")[1]
    user_selected_currency[query.from_user.id] = currency
    await query.message.answer(f"✅ Siz {currency} valyutasini tanladingiz. Miqdorni kiriting:")

@dp.message_handler()
async def calculate(message: types.Message):
    try:
        amount = float(message.text)
        user_id = message.from_user.id

        if user_id not in user_selected_currency:
            await message.answer("❌ Avval valyutani tanlang!")
            return

        currency = user_selected_currency[user_id]
        rates = await get_currency_rates()

        if rates and currency in rates:
            total = amount * rates[currency]
            await message.answer(f"{amount} {currency} = {total:.2f} so‘m")
        else:
            await message.answer("❌ Kurslarni olib bo‘lmadi, keyinroq urinib ko‘ring.")
    except ValueError:
        await message.answer("⚠ Iltimos, faqat son kiriting!")

@dp.callback_query_handler(lambda query: query.data == 'refresh')
async def refresh_rates(query: types.CallbackQuery):
    rates = await get_currency_rates()
    
    if rates:
        await query.answer("✅ Valyuta kurslari yangilandi!", show_alert=True)
    else:
        await query.answer("❌ Kurslarni yangilab bo‘lmadi, keyinroq urinib ko‘ring!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)