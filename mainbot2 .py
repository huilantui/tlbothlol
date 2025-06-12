
import asyncio
import os
import logging
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

API_TOKEN = '7948363605:AAEN4aHkd4xTBmOcMx-aQqzijInIHTSEEjY'
ADMIN_ID = 7904239408

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Глобальные хранилища данных
user_cart = {}
user_info = {}
user_language = {}
user_payment_method = {}
user_waiting_receipt = {}

# Переводы
translations = {
    'ru': {
        'welcome': "🎉 Добро пожаловать в наш магазин!\n\nВыберите действие из меню ниже:",
        'choose_product': "🛍️ Выбор товара",
        'cart': "🛒 Корзина",
        'info': "ℹ️ Информация",
        'reserve': "📢 Резерв",
        'choose_product_text': "🛍️ <b>Выберите товар:</b>\n\nНажмите на интересующий вас товар для получения подробной информации",
        'back_to_menu': "🔙 Назад в меню",
        'cart_empty': "🛒 Ваша корзина пуста",
        'your_cart': "🛒 <b>Ваша корзина:</b>\n\nТовар: {product_name}\nКоличество: 1 шт.",
        'shop_info': "ℹ️ <b>Информация о магазине:</b>\n\n🏪 Наш интернет-магазин работает 24/7\n💳 Принимаем криптовалюты\n🏆 Мы лучший магазин в своей сфере\n📞 Поддержка: @support\n\n👤 <b>Информация о пользователе:</b>\n👨‍💼 Имя: {full_name}\n📱 Username: @{username}\n📅 Дата регистрации: {start_date}",
        'reserve_info': "📢 <b>Резервный канал:</b>\n\nПереходите на наш резервный канал, чтобы оставаться в курсе новостей!",
        'active_channel': "Активный канал",
        'product_info': "🛍️ <b>{product_name}</b>\n\n📝 {description}\n💰 Цена: {price}\n\n📦 Количество товара ограничено: 1 шт.",
        'payment_methods': "💳 <b>Выберите способ оплаты:</b>\n\n🛍️ Товар: {product_name}\n📦 Количество: {quantity} шт.\n\n💰 Доступные способы оплаты:",
        'payment_address': "💳 <b>Адрес для оплаты {payment_method}:</b>\n\n<code>{address}</code>\n\n📋 <i>Нажмите на адрес, чтобы скопировать его</i>\n\n💰 Сумма к оплате: {price}\n\nПосле отправки средств нажмите кнопку 'Подтвердить оплату'",
        'confirm_payment': "✅ Подтвердить оплату",
        'back_to_payment': "🔙 К способам оплаты",
        'back_to_product': "🔙 Назад к товару",
        'receipt_request': "📸 <b>Отправьте чек об оплате</b>\n\n📷 Пожалуйста, отправьте фотографию чека или скриншот транзакции для более быстрой проверки.\n\n⏰ <i>Проверка может занять до 1 часа</i>\n\n❌ <b>Внимание:</b> Видео не принимаются!",
        'receipt_received': "✅ <b>Чек получен!</b>\n\n⏳ Ваш чек отправлен на проверку администратору.\n\n🔔 Как только оплата будет подтверждена, вы получите товар.\n\n📞 При возникновении вопросов обращайтесь в поддержку: @support",
        'video_not_allowed': "❌ <b>Видео не принимаются!</b>\n\n📸 Пожалуйста, отправьте только фотографию чека или скриншот транзакции.",
        'no_receipt': "❌ <b>Чек не получен!</b>\n\n📸 Пожалуйста, отправьте фотографию чека для подтверждения оплаты.",
        'admin_notification_with_receipt': "🛒 <b>НОВАЯ ПОКУПКА С ЧЕКОМ!</b>\n\n👤 Покупатель:\n🆔 ID: <code>{user_id}</code>\n👨‍💼 Имя: {first_name}\n📱 Username: @{username}\n\n🛍️ Товар: {product_name}\n📦 Количество: {quantity} шт.\n💳 Способ оплаты: {payment_method}\n💰 Сумма: {price}\n\n⏰ Время покупки: {time}\n\n📸 Чек прикреплен ниже ⬇️",
        'product_sent': "🎉 <b>Оплата подтверждена!</b>\n\n✅ Ваш заказ обработан:\n🛍️ Товар: {product_name}\n\n📁 <b>Ссылка для скачивания:</b>\n{product_link}\n\n⚠️ <i>Ссылка действительна в течение 24 часов</i>\n\n🙏 Спасибо за покупку!",
        'payment_cancelled': "❌ <b>Платеж отклонен!</b>\n\n🚫 Ваша оплата была отклонена администратором.\n\n💰 Если вы считаете это ошибкой, обратитесь в поддержку: @support",
        'main_menu': "🏠 В главное меню",
        'quantity': "📦 Количество: 1",
        'pay': "💳 Оплатить",
        'back_to_products': "🔙 К выбору товаров",
        'admin_confirm': "✅ Подтвердить и отправить товар",
        'admin_cancel': "❌ Отклонить платеж (обман)",
        'no_username': "Не указан",
        'no_name': "Не указано",
        'not_defined': "Не определено",
        'russian': "🇷🇺 Русский",
        'english': "🇬🇧 English"
    },
    'en': {
        'welcome': "🎉 Welcome to our shop!\n\nChoose an action from the menu below:",
        'choose_product': "🛍️ Choose Product",
        'cart': "🛒 Cart",
        'info': "ℹ️ Information",
        'reserve': "📢 Reserve",
        'choose_product_text': "🛍️ <b>Choose a product:</b>\n\nClick on the product you're interested in for detailed information",
        'back_to_menu': "🔙 Back to menu",
        'cart_empty': "🛒 Your cart is empty",
        'your_cart': "🛒 <b>Your cart:</b>\n\nProduct: {product_name}\nQuantity: 1 pcs.",
        'shop_info': "ℹ️ <b>Shop Information:</b>\n\n🏪 Our online store works 24/7\n💳 We accept cryptocurrencies\n🏆 We are the best shop in our field\n📞 Support: @support\n\n👤 <b>User Information:</b>\n👨‍💼 Name: {full_name}\n📱 Username: @{username}\n📅 Registration date: {start_date}",
        'reserve_info': "📢 <b>Reserve channel:</b>\n\nGo to our reserve channel to stay updated with news!",
        'active_channel': "Active channel",
        'product_info': "🛍️ <b>{product_name}</b>\n\n📝 {description}\n💰 Price: {price}\n\n📦 Product quantity is limited: 1 pc.",
        'payment_methods': "💳 <b>Choose payment method:</b>\n\n🛍️ Product: {product_name}\n📦 Quantity: {quantity} pcs.\n\n💰 Available payment methods:",
        'payment_address': "💳 <b>Payment address for {payment_method}:</b>\n\n<code>{address}</code>\n\n📋 <i>Click on the address to copy it</i>\n\n💰 Amount to pay: {price}\n\nAfter sending funds, click the 'Confirm payment' button",
        'confirm_payment': "✅ Confirm payment",
        'back_to_payment': "🔙 Back to payment methods",
        'back_to_product': "🔙 Back to product",
        'receipt_request': "📸 <b>Send payment receipt</b>\n\n📷 Please send a photo of the receipt or transaction screenshot for faster verification.\n\n⏰ <i>Verification can take up to 1 hour</i>\n\n❌ <b>Note:</b> Videos are not accepted!",
        'receipt_received': "✅ <b>Receipt received!</b>\n\n⏳ Your receipt has been sent to the administrator for verification.\n\n🔔 Once payment is confirmed, you will receive the product.\n\n📞 If you have any questions, contact support: @support",
        'video_not_allowed': "❌ <b>Videos are not accepted!</b>\n\n📸 Please send only a photo of the receipt or transaction screenshot.",
        'no_receipt': "❌ <b>No receipt received!</b>\n\n📸 Please send a photo of the receipt to confirm payment.",
        'admin_notification_with_receipt': "🛒 <b>NEW PURCHASE WITH RECEIPT!</b>\n\n👤 Buyer:\n🆔 ID: <code>{user_id}</code>\n👨‍💼 Name: {first_name}\n📱 Username: @{username}\n\n🛍️ Product: {product_name}\n📦 Quantity: {quantity} pcs.\n💳 Payment method: {payment_method}\n💰 Amount: {price}\n\n⏰ Purchase time: {time}\n\n📸 Receipt attached below ⬇️",
        'product_sent': "🎉 <b>Payment confirmed!</b>\n\n✅ Your order has been processed:\n🛍️ Product: {product_name}\n\n📁 <b>Download link:</b>\n{product_link}\n\n⚠️ <i>Link is valid for 24 hours</i>\n\n🙏 Thank you for your purchase!",
        'payment_cancelled': "❌ <b>Payment declined!</b>\n\n🚫 Your payment was declined by the administrator.\n\n💰 If you think this is an error, contact support: @support",
        'main_menu': "🏠 Main menu",
        'quantity': "📦 Quantity: 1",
        'pay': "💳 Pay",
        'back_to_products': "🔙 Back to products",
        'admin_confirm': "✅ Confirm and send product",
        'admin_cancel': "❌ Decline payment (fraud)",
        'no_username': "Not specified",
        'no_name': "Not specified",
        'not_defined': "Not defined",
        'russian': "🇷🇺 Русский",
        'english': "🇬🇧 English"
    }
}

# Товары с названиями и описаниями
products = {
    'ru': {
        "1": {
            "name": "📦 L0LEZ PACK 2k",
            "description": "Эксклюзивная коллекция из 2000 элементов. Высокое качество контента для ваших проектов.",
            "price": "500 USDT"
        },
        "2": {
            "name": "🎬 L0LEZ PACK VIDEO 3k",
            "description": "Премиум коллекция видео материалов - 3000 уникальных файлов в высоком разрешении.",
            "price": "1200 USDT"
        },
        "3": {
            "name": "💎 L0LEZ PACK 10k",
            "description": "Мега пак из 10000 элементов - самая полная коллекция для профессионалов.",
            "price": "2000 USDT"
        }
    },
    'en': {
        "1": {
            "name": "📦 L0LEZ PACK 2k",
            "description": "Exclusive collection of 2000 elements. High quality content for your projects.",
            "price": "500 USDT"
        },
        "2": {
            "name": "🎬 L0LEZ PACK VIDEO 3k",
            "description": "Premium video materials collection - 3000 unique files in high resolution.",
            "price": "1200 USDT"
        },
        "3": {
            "name": "💎 L0LEZ PACK 10k",
            "description": "Mega pack of 10000 elements - the most complete collection for professionals.",
            "price": "2000 USDT"
        }
    }
}

# Адреса криптовалют
crypto_addresses = {
    'btc': "17D9zwBVmeP5A6kmrpZyPzktGypntPkZNF",
    'usdt_trc20': "TD5a62op3kQyuq6vT7AXxfRZRtaiUzfYFf",
    'usdt_ton': "UQCQr_qF1BCJeEWAtiasiXjeryJPKOgHIzGWV5gpMine23HU"
}

# Названия способов оплаты
payment_method_names = {
    'btc': '₿ Bitcoin (BTC)',
    'usdt_trc20': '💎 USDT (TRC20)', 
    'usdt_ton': '💙 USDT (TON)'
}

# Ссылки на товары
product_links = {
    "1": "https://drive.google.com/file/d/1example1/view?usp=sharing",
    "2": "https://drive.google.com/file/d/1example2/view?usp=sharing",
    "3": "https://drive.google.com/file/d/1example3/view?usp=sharing"
}

def get_text(user_id, key, **kwargs):
    """Получить переведенный текст для пользователя"""
    lang = user_language.get(user_id, 'ru')
    text = translations[lang].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

def get_main_menu(user_id):
    """Создать главное меню на выбранном языке"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(user_id, 'choose_product'))],
            [KeyboardButton(text=get_text(user_id, 'cart')), KeyboardButton(text=get_text(user_id, 'info'))],
            [KeyboardButton(text=get_text(user_id, 'reserve'))],
            [KeyboardButton(text=get_text(user_id, 'russian')), KeyboardButton(text=get_text(user_id, 'english'))]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard

async def delete_webhook():
    """Удалить webhook если он активен"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook"
            async with session.post(url) as response:
                result = await response.json()
                if result.get('ok'):
                    logging.info("Webhook успешно удален")
                    return True
                else:
                    logging.warning(f"Не удалось удалить webhook: {result}")
                    return False
    except Exception as e:
        logging.error(f"Ошибка при удалении webhook: {e}")
        return False

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    # Сохраняем информацию о пользователе
    username = message.from_user.username or get_text(user_id, 'no_username')
    first_name = message.from_user.first_name or get_text(user_id, 'no_name')
    last_name = message.from_user.last_name or ""
    start_date = datetime.now().strftime("%d.%m.%Y %H:%M")

    user_info[user_id] = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'start_date': start_date,
        'user_id': user_id
    }

    # Проверяем, выбирал ли пользователь язык
    if user_id not in user_language:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ])

        await message.answer(
            "🌐 Выберите язык / Choose language:",
            reply_markup=keyboard
        )
        return

    # Если язык уже выбран, показываем главное меню
    await show_main_menu(message, user_id)

@dp.callback_query(F.data.startswith('lang_'))
async def set_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = callback_query.data.split('_')[1]
    user_language[user_id] = lang

    await callback_query.message.delete()
    await show_main_menu(callback_query.message, user_id)
    await callback_query.answer()

async def show_main_menu(message, user_id):
    """Показать главное меню"""
    await message.answer(
        get_text(user_id, 'welcome'),
        reply_markup=get_main_menu(user_id)
    )

@dp.message(F.text.in_(["🛍️ Выбор товара", "🛍️ Choose Product"]))
async def choose_product_menu(message: types.Message):
    user_id = message.from_user.id
    lang = user_language.get(user_id, 'ru')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=products[lang]["1"]["name"], callback_data="product_1")],
        [InlineKeyboardButton(text=products[lang]["2"]["name"], callback_data="product_2")],
        [InlineKeyboardButton(text=products[lang]["3"]["name"], callback_data="product_3")],
        [InlineKeyboardButton(text=get_text(user_id, 'back_to_menu'), callback_data="back_to_main")]
    ])

    await message.answer(
        get_text(user_id, 'choose_product_text'),
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.message(F.text.in_(["🛒 Корзина", "🛒 Cart"]))
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    lang = user_language.get(user_id, 'ru')
    cart = user_cart.get(user_id)

    if not cart:
        await message.answer(get_text(user_id, 'cart_empty'))
    else:
        product_name = products[lang][cart['product']]["name"]
        await message.answer(
            get_text(user_id, 'your_cart', product_name=product_name),
            parse_mode="HTML"
        )

@dp.message(F.text.in_(["ℹ️ Информация", "ℹ️ Information"]))
async def show_info(message: types.Message):
    user_id = message.from_user.id
    user_data = user_info.get(user_id, {})

    username = user_data.get('username', get_text(user_id, 'no_username'))
    first_name = user_data.get('first_name', get_text(user_id, 'no_name'))
    last_name = user_data.get('last_name', '')
    start_date = user_data.get('start_date', get_text(user_id, 'not_defined'))

    full_name = f"{first_name} {last_name}".strip()

    await message.answer(
        get_text(user_id, 'shop_info', 
                full_name=full_name, 
                username=username, 
                start_date=start_date),
        parse_mode="HTML"
    )

@dp.message(F.text.in_(["📢 Резерв", "📢 Reserve"]))
async def show_reserve(message: types.Message):
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user_id, 'active_channel'), url="https://t.me/yourtelegram")]
    ])
    await message.answer(
        get_text(user_id, 'reserve_info'),
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.message(F.text.in_(["🇷🇺 Русский"]))
async def switch_to_russian(message: types.Message):
    user_id = message.from_user.id
    user_language[user_id] = 'ru'
    await message.answer(
        get_text(user_id, 'welcome'),
        reply_markup=get_main_menu(user_id)
    )

@dp.message(F.text.in_(["🇬🇧 English"]))
async def switch_to_english(message: types.Message):
    user_id = message.from_user.id
    user_language[user_id] = 'en'
    await message.answer(
        get_text(user_id, 'welcome'),
        reply_markup=get_main_menu(user_id)
    )

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_waiting_receipt.pop(user_id, None)
    await callback_query.message.delete()
    await callback_query.message.answer(
        get_text(user_id, 'welcome'),
        reply_markup=get_main_menu(user_id)
    )
    await callback_query.answer()

@dp.callback_query(F.data.startswith('product_'))
async def show_product(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = user_language.get(user_id, 'ru')
    product_id = callback_query.data.split('_')[1]
    user_cart[user_id] = {'product': product_id, 'quantity': 1}

    product = products[lang][product_id]
    product_name = product["name"]
    description = product["description"]
    price = product["price"]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user_id, 'quantity'), callback_data='quantity_display')],
        [InlineKeyboardButton(text=get_text(user_id, 'pay'), callback_data='pay')],
        [
            InlineKeyboardButton(text=get_text(user_id, 'back_to_products'), callback_data='back_to_products'),
            InlineKeyboardButton(text=get_text(user_id, 'main_menu'), callback_data='back_to_main')
        ]
    ])

    new_text = get_text(user_id, 'product_info', 
                        product_name=product_name, 
                        description=description, 
                        price=price)
    
    try:
        await callback_query.message.edit_text(
            new_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        if "message is not modified" not in str(e):
            logging.error(f"Error editing message: {e}")
    
    await callback_query.answer()

@dp.callback_query(F.data == 'back_to_products')
async def back_to_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = user_language.get(user_id, 'ru')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=products[lang]["1"]["name"], callback_data="product_1")],
        [InlineKeyboardButton(text=products[lang]["2"]["name"], callback_data="product_2")],
        [InlineKeyboardButton(text=products[lang]["3"]["name"], callback_data="product_3")],
        [InlineKeyboardButton(text=get_text(user_id, 'back_to_menu'), callback_data="back_to_main")]
    ])

    await callback_query.message.edit_text(
        get_text(user_id, 'choose_product_text'),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback_query.answer()

@dp.callback_query(F.data == 'pay')
async def pay(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = user_language.get(user_id, 'ru')
    cart = user_cart.get(user_id, {'product': '1', 'quantity': 1})

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="₿ Bitcoin", callback_data='payment_btc'),
            InlineKeyboardButton(text="💎 USDT (TRC20)", callback_data='payment_usdt_trc20'),
        ],
        [
            InlineKeyboardButton(text="💙 USDT (TON)", callback_data='payment_usdt_ton'),
        ],
        [
            InlineKeyboardButton(text=get_text(user_id, 'back_to_product'), callback_data=f'product_{cart["product"]}'),
            InlineKeyboardButton(text=get_text(user_id, 'main_menu'), callback_data='back_to_main')
        ]
    ])

    product_name = products[lang][cart['product']]["name"]

    await callback_query.message.edit_text(
        get_text(user_id, 'payment_methods',
                product_name=product_name,
                quantity=cart['quantity']),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback_query.answer()

@dp.callback_query(F.data.startswith('payment_'))
async def show_payment_address(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = user_language.get(user_id, 'ru')
    payment_method = callback_query.data.replace('payment_', '')
    
    user_payment_method[user_id] = payment_method
    cart = user_cart.get(user_id, {'product': '1', 'quantity': 1})
    
    address = crypto_addresses.get(payment_method, "Адрес не найден")
    method_name = payment_method_names.get(payment_method, payment_method)
    price = products[lang][cart['product']]["price"]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user_id, 'confirm_payment'), callback_data='confirm_payment')],
        [
            InlineKeyboardButton(text=get_text(user_id, 'back_to_payment'), callback_data='pay'),
            InlineKeyboardButton(text=get_text(user_id, 'main_menu'), callback_data='back_to_main')
        ]
    ])

    await callback_query.message.edit_text(
        get_text(user_id, 'payment_address',
                payment_method=method_name,
                address=address,
                price=price),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback_query.answer()

@dp.callback_query(F.data == 'confirm_payment')
async def request_receipt(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    user_waiting_receipt[user_id] = True

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user_id, 'main_menu'), callback_data='back_to_main')]
    ])

    await callback_query.message.edit_text(
        get_text(user_id, 'receipt_request'),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback_query.answer()

@dp.message(F.video)
async def handle_video(message: types.Message):
    user_id = message.from_user.id
    
    if user_waiting_receipt.get(user_id):
        await message.answer(
            get_text(user_id, 'video_not_allowed'),
            parse_mode="HTML"
        )

@dp.message(F.photo)
async def handle_receipt_photo(message: types.Message):
    user_id = message.from_user.id
    
    if not user_waiting_receipt.get(user_id):
        return
    
    user_waiting_receipt.pop(user_id, None)
    
    lang = user_language.get(user_id, 'ru')
    cart = user_cart.get(user_id, {'product': '1', 'quantity': 1})
    user_data = user_info.get(user_id, {})
    payment_method = user_payment_method.get(user_id, 'unknown')

    username = message.from_user.username or user_data.get('username', get_text(user_id, 'no_username'))
    first_name = message.from_user.first_name or user_data.get('first_name', get_text(user_id, 'no_name'))
    product_name = products[lang][cart['product']]["name"]
    product_price = products[lang][cart['product']]["price"]
    payment_method_name = payment_method_names.get(payment_method, payment_method)

    try:
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить и отправить товар", callback_data=f'admin_confirm_{user_id}_{cart["product"]}_{payment_method}'),
                InlineKeyboardButton(text="❌ Отклонить платеж (обман)", callback_data=f'admin_cancel_{user_id}_{cart["product"]}_{payment_method}')
            ]
        ])

        await bot.send_message(
            ADMIN_ID,
            f"🛒 <b>НОВАЯ ПОКУПКА С ЧЕКОМ!</b>\n\n"
            f"👤 Покупатель:\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"👨‍💼 Имя: {first_name}\n"
            f"📱 Username: @{username}\n\n"
            f"🛍️ Товар: {product_name}\n"
            f"📦 Количество: {cart['quantity']} шт.\n"
            f"💳 Способ оплаты: {payment_method_name}\n"
            f"💰 Сумма: {product_price}\n\n"
            f"⏰ Время покупки: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
            f"📸 Чек прикреплен ниже ⬇️",
            reply_markup=admin_keyboard,
            parse_mode="HTML"
        )
        
        await bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=user_id,
            message_id=message.message_id
        )
        
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления админу: {e}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user_id, 'main_menu'), callback_data='back_to_main')]
    ])

    await message.answer(
        get_text(user_id, 'receipt_received'),
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith('admin_confirm_'))
async def admin_confirm_purchase(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("❌ У вас нет прав доступа!")
        return

    parts = callback_query.data.split('_')
    if len(parts) >= 4:
        user_id = int(parts[2])
        product_id = parts[3]
        payment_method = parts[4] if len(parts) > 4 else 'unknown'
    else:
        await callback_query.answer("❌ Ошибка данных!")
        return
    
    lang = user_language.get(user_id, 'ru')
    product_name = products[lang][product_id]["name"]
    product_link = product_links.get(product_id, "Ссылка не найдена")

    try:
        await bot.send_message(
            user_id,
            get_text(user_id, 'product_sent',
                    product_name=product_name,
                    product_link=product_link),
            parse_mode="HTML"
        )

        await callback_query.message.edit_text(
            f"✅ <b>ТОВАР ОТПРАВЛЕН!</b>\n\n"
            f"{callback_query.message.text}\n\n"
            f"📤 Товар успешно отправлен покупателю",
            parse_mode="HTML"
        )
        await callback_query.answer("✅ Товар отправлен покупателю!")

        user_cart.pop(user_id, None)
        user_payment_method.pop(user_id, None)

    except Exception as e:
        await callback_query.answer(f"❌ Ошибка отправки: {e}")
        logging.error(f"Ошибка отправки товара: {e}")

@dp.callback_query(F.data.startswith('admin_cancel_'))
async def admin_cancel_purchase(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("❌ У вас нет прав доступа!")
        return

    parts = callback_query.data.split('_')
    if len(parts) >= 4:
        user_id = int(parts[2])
        product_id = parts[3]
        payment_method = parts[4] if len(parts) > 4 else 'unknown'
    else:
        await callback_query.answer("❌ Ошибка данных!")
        return

    try:
        await bot.send_message(
            user_id,
            get_text(user_id, 'payment_cancelled'),
            parse_mode="HTML"
        )

        await callback_query.message.edit_text(
            f"❌ <b>ПЛАТЕЖ ОТКЛОНЕН!</b>\n\n"
            f"{callback_query.message.text}\n\n"
            f"🚫 Платеж отклонен как мошеннический",
            parse_mode="HTML"
        )
        await callback_query.answer("❌ Платеж отклонен!")

        user_cart.pop(user_id, None)
        user_payment_method.pop(user_id, None)

    except Exception as e:
        await callback_query.answer(f"❌ Ошибка отклонения: {e}")
        logging.error(f"Ошибка отклонения платежа: {e}")

@dp.callback_query(F.data.in_(['quantity_display']))
async def noop(callback_query: types.CallbackQuery):
    try:
        await callback_query.answer()
    except Exception as e:
        if "query is too old" not in str(e):
            logging.error(f"Error answering callback: {e}")

@dp.message()
async def handle_other_messages(message: types.Message):
    user_id = message.from_user.id
    
    if user_waiting_receipt.get(user_id):
        await message.answer(
            get_text(user_id, 'no_receipt'),
            parse_mode="HTML"
        )

async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Удаляем webhook перед запуском
    print("🔄 Удаление webhook...")
    await delete_webhook()
    await asyncio.sleep(2)  # Небольшая пауза
    
    # Проверяем среду выполнения
    if os.getenv('REPLIT_DEPLOYMENT'):
        print("🚀 Бот запущен в продакшене (24/7 режим)!")
        logging.info("Bot started in production mode (24/7)")
    else:
        print("🚀 Бот запущен в режиме разработки!")
        logging.info("Bot started in development mode")
    
    # Максимальное количество попыток перезапуска
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"🔄 Попытка запуска бота #{retry_count + 1}")
            await dp.start_polling(bot, skip_updates=True)
            break  # Если успешно запустился, выходим из цикла
            
        except Exception as e:
            retry_count += 1
            logging.error(f"Ошибка запуска #{retry_count}: {e}")
            
            if "Conflict" in str(e) and "webhook" in str(e):
                print("⚠️ Обнаружен конфликт с webhook, пытаемся исправить...")
                await delete_webhook()
                await asyncio.sleep(5)
            elif retry_count >= max_retries:
                print(f"❌ Превышено максимальное количество попыток ({max_retries})")
                logging.error("Maximum retry attempts exceeded")
                break
            else:
                print(f"⏳ Ожидание перед следующей попыткой... ({5 * retry_count} сек)")
                await asyncio.sleep(5 * retry_count)

if __name__ == '__main__':
    asyncio.run(main())
