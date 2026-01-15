

Collaborate

Share
Max
ممتاز! سأجهز لك الكود المحدث بنظام طلبات الوصول الآن.
I discovered the deployment issue was due to incompatible `python-telegram-bot` library with Python 3.13. Updating `requirements.txt` to version 21.7 will fix this, enabling successful deployment.

بس هذا الرقم اعطاني اياه من حسابي الخاص في التلقران عادي استخدمه في البوت؟
Max
نعم، عادي جداً وهذا هو المطلوب بالضبط! ✅
الرقم 1177923997 هو User ID الخاص بحسابك الشخصي في تيليجرام.
هذا الرقم:
آمن للاستخدام (ليس سري مثل التوكن)
ثابت ولا يتغير أبداً
يستخدمه المطورون دائماً لتحديد المشرفين
كيف سيعمل النظام:
الشخص
ماذا يحدث
أنت (1177923997)
تدخل البوت مباشرة بدون طلب
أي شخص آخر
يرسل طلب وصول، وأنت تستلم إشعار للموافقة أو الرفض
سأجهز الكود الآن...
I confirmed the access request system update for the bot, ensuring the owner can access directly while others must request permission. The updated code is now saved.

Max
تم تجهيز الكود المحدث بنظام طلبات الوصول! 🔒
المميزات الجديدة:
الميزة
الوصف
نظام طلبات الوصول
أي شخص جديد يرسل طلب وأنت توافق أو ترفض
أنت المشرف
ID: 1177923997 - تدخل مباشرة بدون طلب
إشعارات فورية
تصلك رسالة عند كل طلب جديد
حفظ المستخدمين
المعتمدين يُحفظون تلقائياً
أوامر المشرف الجديدة:
الأمر
الوظيفة
/admin
لوحة تحكم المشرف
/users
عرض المستخدمين المعتمدين
/pending
عرض الطلبات المعلقة
/remove [ID]
إزالة مستخدم
كيفية التحديث على GitHub:
اذهب إلى Repository على GitHub
اضغط على ملف bot.py
اضغط على أيقونة القلم (Edit) ✏️
امسح كل المحتوى
انسخ محتوى الملف المرفق bot_updated.py والصقه
اضغط Commit changes
بعد التحديث على GitHub:
اذهب إلى Render واضغط:
Manual Deploy > Clear build cache & deploy
كيف يعمل النظام:
شخص جديد يرسل /start للبوت
تصلك رسالة فيها اسمه ويوزره مع زرين (✅ موافقة / ❌ رفض)
إذا وافقت - يقدر يستخدم البوت
إذا رفضت - ما يقدر يدخل
هل تريد أي تعديلات إضافية؟
bot_updated.py
Code · 28.42 KB

View all files in this task
هل استطيع ربطه مع finfiz والحصول على الشارتات منه؟
Max
سؤال ممتاز! نعم، يمكنك الحصول على الشارتات من Finviz، لكن بطريقة محددة:
الوضع الحالي لـ Finviz:
الميزة
متاح؟
الطريقة
صور الشارتات
✅ نعم
روابط مباشرة للصور
API رسمي
❌ لا
لا يوجد API عام
البيانات
⚠️ محدود
Scraping (قد يُحظر)
ما يمكن فعله:
1. جلب صور الشارتات (سهل وقانوني)
Finviz يوفر روابط مباشرة لصور الشارتات:
Plain Text
https://finviz.com/chart.ashx?t=AAPL&ty=c&ta=1&p=d
المعامل
القيم
t
رمز السهم (AAPL, TSLA... )
ty
c = شموع، l = خطي
ta
1 = مع مؤشرات، 0 = بدون
p
d = يومي، w = أسبوعي، m = شهري
هل تريدني أضيف هذه الميزة للبوت؟
سأجعل البوت يرسل لك:
صورة الشارت من Finviz
التحليل الفني (إليوت، ICT، إلخ)
معاً في رسالة واحدة!
ملاحظة: صور Finviz متاحة فقط للأسهم الأمريكية (NYSE, NASDAQ).
هل تريدني أضيف هذه الميزة؟
نعم لوسمحت ولكن هل تستطيع عند ارسال صوره الشارت ان تضع الرسم للتحليل الفني عليها؟
Max
سؤال ممتاز! نعم، أستطيع ذلك! 🎨
سأجعل البوت يرسم على الشارت:
ما سيُرسم على الشارت:
التحليل
الرسم
موجات إليوت
ترقيم الموجات (1,2,3,4,5) و (A,B,C) على القمم والقيعان
الدعم والمقاومة
خطوط أفقية ملونة
النماذج التوافقية
خطوط XABCD مع نسب فيبوناتشي
ICT
مناطق Order Blocks و FVG مظللة
خطوط الاتجاه
خطوط مائلة
كيف سيعمل:
البوت يجلب بيانات السهم
يرسم الشارت بنفسه (باستخدام Python)
يضيف التحليل الفني على الرسم
يرسل لك الصورة مع الشرح
ملاحظة مهمة:
بدلاً من استخدام صور Finviz (لأنها جاهزة ولا نستطيع الرسم عليها)، سأجعل البوت يرسم الشارت بنفسه باستخدام مكتبة matplotlib أو mplfinance.
هذا أفضل لأنه:
✅ نتحكم بالرسم بالكامل
✅ نضيف أي تحليل نريده
✅ جودة عالية
✅ يعمل مع أي سهم (أمريكي أو سعودي)
سأبدأ الآن بتجهيز الكود. هذا سيأخذ وقت لأنه إضافة كبيرة.
هل أبدأ؟
ابدأ 
Max
تم! سأبدأ الآن ببناء نظام رسم الشارتات مع التحليل الفني.
انتظر قليلاً...
I confirmed the access request system update in the code, enabling owners to access directly. Next, I will develop the chart drawing engine with technical analysis for the bot.

I have completed the chart drawing engine with technical analysis. Next, I will integrate it into the main bot to support image sending.

I completed integrating the chart drawing engine with technical analysis into the main bot, enabling it to support image sending with chart analysis.

Max
تم تجهيز البوت مع نظام رسم الشارتات! 🎨📊
الملفات الجديدة:
الملف
الوصف
bot_with_charts.py
البوت الرئيسي (استبدل به bot.py)
chart_drawer.py
محرك رسم الشارتات
requirements_new.txt
المكتبات المطلوبة (استبدل به requirements.txt)
ما يُرسم على الشارت:
التحليل
الرسم
🌊 موجات إليوت
ترقيم (1,2,3,4,5) و (A,B,C) على القمم والقيعان
📊 الكلاسيكي
خطوط الدعم/المقاومة + خطوط الاتجاه + فيبوناتشي
🔷 التوافقي
نماذج XABCD (Gartley, Butterfly, Bat, Crab)
🎯 ICT
Order Blocks + Fair Value Gaps مظللة
خطوات التحديث على GitHub:
1. أضف ملف جديد chart_drawer.py
اضغط Add file > Create new file
الاسم: chart_drawer.py
انسخ محتوى الملف المرفق
2. حدّث bot.py
اضغط على bot.py > أيقونة القلم ✏️
امسح كل المحتوى
انسخ محتوى bot_with_charts.py
3. حدّث requirements.txt
اضغط على requirements.txt > أيقونة القلم ✏️
امسح كل المحتوى واكتب:
Plain Text
python-telegram-bot==21.7
yfinance>=0.2.40
pandas>=2.0.0
numpy>=1.26.0
matplotlib>=3.7.0
4. في Render
اضغط Manual Deploy > Clear build cache & deploy
كيف يعمل البوت الآن:
ترسل رمز السهم (مثل AAPL)
تختار الفريم (15د، 30د، 1س، 4س، يومي)
تختار نوع التحليل
يرسل لك صورة الشارت مع الرسومات التحليلية + ملخص نصي!
هل تريد أي تعديلات إضافية؟
telegram-bot-charts.zip
Archive · 41.54 KB
bot_with_charts.py
Code · 23.54 KB
chart_drawer.py
Code · 22.34 KB
requirements_new.txt
Text · 89 B

View all files in this task
Task completed
How was this result?
Suggested follow-ups
Send message to Manus

bot_with_charts.py
"""
بوت التحليل الفني المتقدم مع الشارتات
Advanced Technical Analysis Telegram Bot with Charts
موجات إليوت - التحليل الكلاسيكي - التحليل التوافقي - مدرسة ICT
مع نظام طلبات الوصول ورسم الشارتات
"""

import os
import json
import logging
import tempfile
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yfinance as yf
import pandas as pd

# استيراد محركات التحليل
from elliott_waves import ElliottWaveAnalyzer
from classic_analysis import ClassicAnalyzer
from harmonic_patterns import HarmonicAnalyzer
from ict_analysis import ICTAnalyzer
from chart_drawer import ChartDrawer

# إعدادات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# إعدادات الصلاحيات
# ============================================

ADMIN_ID = 1177923997
APPROVED_USERS_FILE = "approved_users.json"

def load_approved_users():
    try:
        if os.path.exists(APPROVED_USERS_FILE):
            with open(APPROVED_USERS_FILE, 'r') as f:
                return set(json.load(f))
    except:
        pass
    return {ADMIN_ID}

def save_approved_users(users):
    try:
        with open(APPROVED_USERS_FILE, 'w') as f:
            json.dump(list(users), f)
    except Exception as e:
        logger.error(f"Error saving users: {e}")

approved_users = load_approved_users()
pending_requests = {}

# ============================================
# الإعدادات
# ============================================

TIMEFRAMES = {
    '15m': {'interval': '15m', 'period': '5d', 'name': '15 دقيقة'},
    '30m': {'interval': '30m', 'period': '10d', 'name': '30 دقيقة'},
    '1h': {'interval': '1h', 'period': '1mo', 'name': '1 ساعة'},
    '4h': {'interval': '1h', 'period': '3mo', 'name': '4 ساعات'},
    '1d': {'interval': '1d', 'period': '6mo', 'name': 'يومي'},
}

ANALYSIS_TYPES = {
    'elliott': {'name': '🌊 موجات إليوت', 'code': 'elliott'},
    'classic': {'name': '📊 كلاسيكي', 'code': 'classic'},
    'harmonic': {'name': '🔷 توافقي', 'code': 'harmonic'},
    'ict': {'name': '🎯 ICT', 'code': 'ict'},
    'full': {'name': '📋 شامل', 'code': 'all'},
}

user_states = {}
chart_drawer = ChartDrawer()

# ============================================
# دوال مساعدة
# ============================================

def is_approved(user_id: int) -> bool:
    return user_id in approved_users or user_id == ADMIN_ID

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def get_stock_data(symbol: str, timeframe: str) -> pd.DataFrame:
    try:
        tf_config = TIMEFRAMES.get(timeframe, TIMEFRAMES['1d'])
        stock = yf.Ticker(symbol)
        
        if timeframe == '4h':
            df = stock.history(period='3mo', interval='1h')
            if not df.empty:
                df = df.resample('4h').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
        else:
            df = stock.history(period=tf_config['period'], interval=tf_config['interval'])
        
        df = df.reset_index()
        return df
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()

def get_stock_info(symbol: str) -> dict:
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            'name': info.get('shortName', symbol),
            'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'change': info.get('regularMarketChangePercent', 0),
            'volume': info.get('volume', 0),
        }
    except:
        return {'name': symbol, 'price': 0, 'change': 0, 'volume': 0}

# ============================================
# أوامر البوت
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    username = update.effective_user.username or "بدون يوزر"
    
    if not is_approved(user_id):
        if user_id not in pending_requests:
            pending_requests[user_id] = {
                'name': user_name,
                'username': username,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{user_id}"),
                    InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")
                ]
            ]
            
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=(
                        "🔔 **طلب وصول جديد**\n\n"
                        f"👤 الاسم: {user_name}\n"
                        f"🆔 اليوزر: @{username}\n"
                        f"🔢 ID: `{user_id}`\n"
                        f"⏰ الوقت: {pending_requests[user_id]['time']}"
                    ),
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending to admin: {e}")
            
            if update.message:
                await update.message.reply_text(
                    "🔒 **البوت خاص**\n\n"
                    "تم إرسال طلب وصول للمشرف.\n"
                    "سيتم إعلامك عند الموافقة على طلبك.\n\n"
                    "⏳ انتظر الموافقة..."
                )
        else:
            if update.message:
                await update.message.reply_text(
                    "⏳ **طلبك قيد المراجعة**\n\n"
                    "تم إرسال طلبك مسبقاً.\n"
                    "انتظر موافقة المشرف."
                )
        return
    
    text = (
        "🤖 **بوت التحليل الفني المتقدم**\n\n"
        "📊 أرسل **رمز السهم** للحصول على تحليل مع شارت\n\n"
        "**أمثلة:**\n"
        "• `AAPL` - Apple\n"
        "• `TSLA` - Tesla\n"
        "• `MSFT` - Microsoft\n"
        "• `NVDA` - NVIDIA\n"
        "• `2222.SR` - أرامكو\n\n"
        "**أنواع التحليل:**\n"
        "🌊 موجات إليوت (مع الترقيم)\n"
        "📊 التحليل الكلاسيكي (دعم/مقاومة)\n"
        "🔷 التحليل التوافقي (النماذج)\n"
        "🎯 مدرسة ICT (OB/FVG)\n\n"
        "**الفريمات:** 15د | 30د | 1س | 4س | يومي\n\n"
        "📝 أرسل رمز السهم للبدء..."
    )
    
    if update.message:
        await update.message.reply_text(text, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown')

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ هذا الأمر للمشرف فقط.")
        return
    
    text = (
        "👑 **لوحة تحكم المشرف**\n\n"
        f"👥 المستخدمين المعتمدين: {len(approved_users)}\n"
        f"⏳ الطلبات المعلقة: {len(pending_requests)}\n\n"
        "**الأوامر:**\n"
        "/users - عرض المستخدمين\n"
        "/pending - عرض الطلبات\n"
        "/remove [ID] - إزالة مستخدم\n"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ هذا الأمر للمشرف فقط.")
        return
    
    text = "👥 **المستخدمين المعتمدين:**\n\n"
    for uid in approved_users:
        admin_mark = " 👑" if uid == ADMIN_ID else ""
        text += f"• `{uid}`{admin_mark}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ هذا الأمر للمشرف فقط.")
        return
    
    if not pending_requests:
        await update.message.reply_text("✅ لا توجد طلبات معلقة.")
        return
    
    for uid, info in pending_requests.items():
        keyboard = [
            [
                InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{uid}"),
                InlineKeyboardButton("❌ رفض", callback_data=f"reject_{uid}")
            ]
        ]
        await update.message.reply_text(
            f"👤 {info['name']}\n🆔 @{info['username']}\n🔢 `{uid}`",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ هذا الأمر للمشرف فقط.")
        return
    
    if not context.args:
        await update.message.reply_text("استخدم: /remove [User ID]")
        return
    
    try:
        target_id = int(context.args[0])
        if target_id == ADMIN_ID:
            await update.message.reply_text("❌ لا يمكن إزالة المشرف!")
            return
        
        if target_id in approved_users:
            approved_users.discard(target_id)
            save_approved_users(approved_users)
            await update.message.reply_text(f"✅ تم إزالة `{target_id}`", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ المستخدم غير موجود.")
    except ValueError:
        await update.message.reply_text("❌ ID غير صحيح.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❓ **دليل الاستخدام**\n\n"
        "1️⃣ أرسل رمز السهم\n"
        "2️⃣ اختر الفريم الزمني\n"
        "3️⃣ اختر نوع التحليل\n"
        "4️⃣ استلم الشارت مع التحليل!\n\n"
        "**الشارت يتضمن:**\n"
        "• رسم الشموع اليابانية\n"
        "• ترقيم موجات إليوت\n"
        "• خطوط الدعم والمقاومة\n"
        "• النماذج التوافقية\n"
        "• Order Blocks و FVG\n"
        "• خطوط الاتجاه\n"
        "• مستويات فيبوناتشي\n"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

# ============================================
# معالجات الأزرار
# ============================================

async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    data = query.data
    
    if data.startswith('approve_'):
        target_id = int(data.replace('approve_', ''))
        approved_users.add(target_id)
        save_approved_users(approved_users)
        
        if target_id in pending_requests:
            del pending_requests[target_id]
        
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="✅ **تمت الموافقة!**\n\nأرسل /start للبدء."
            )
        except:
            pass
        
        await query.edit_message_text(f"✅ تمت الموافقة على `{target_id}`", parse_mode='Markdown')
    
    elif data.startswith('reject_'):
        target_id = int(data.replace('reject_', ''))
        
        if target_id in pending_requests:
            del pending_requests[target_id]
        
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="❌ **تم رفض طلبك.**"
            )
        except:
            pass
        
        await query.edit_message_text(f"❌ تم رفض `{target_id}`", parse_mode='Markdown')

async def handle_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_approved(user_id):
        await update.message.reply_text("🔒 أرسل /start لطلب الوصول.")
        return
    
    symbol = update.message.text.strip().upper()
    
    # تجاهل الأوامر
    if symbol.startswith('/'):
        return
    
    msg = await update.message.reply_text(f"⏳ جاري البحث عن {symbol}...")
    
    info = get_stock_info(symbol)
    
    if info['price'] == 0:
        await msg.edit_text(
            f"❌ لم يتم العثور على: {symbol}\n\n"
            "تأكد من صحة الرمز."
        )
        return
    
    user_states[user_id] = {'symbol': symbol, 'info': info}
    
    keyboard = [
        [
            InlineKeyboardButton("15 دقيقة", callback_data=f"tf_15m_{symbol}"),
            InlineKeyboardButton("30 دقيقة", callback_data=f"tf_30m_{symbol}")
        ],
        [
            InlineKeyboardButton("1 ساعة", callback_data=f"tf_1h_{symbol}"),
            InlineKeyboardButton("4 ساعات", callback_data=f"tf_4h_{symbol}")
        ],
        [
            InlineKeyboardButton("📊 يومي", callback_data=f"tf_1d_{symbol}")
        ],
        [
            InlineKeyboardButton("📋 تحليل شامل سريع", callback_data=f"quick_{symbol}")
        ]
    ]
    
    change_emoji = "📈" if info['change'] >= 0 else "📉"
    
    text = (
        f"📊 **{info['name']}** ({symbol})\n\n"
        f"💰 السعر: ${info['price']:.2f}\n"
        f"{change_emoji} التغير: {info['change']:+.2f}%\n\n"
        "اختر الفريم الزمني:"
    )
    
    await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_approved(user_id):
        return
    
    data = query.data
    
    # تحليل سريع
    if data.startswith('quick_'):
        symbol = data.replace('quick_', '')
        await generate_and_send_chart(query, context, symbol, '1d', ['all'])
        return
    
    # اختيار الفريم
    if data.startswith('tf_'):
        parts = data.split('_')
        timeframe = parts[1]
        symbol = parts[2]
        
        user_states[user_id] = user_states.get(user_id, {})
        user_states[user_id]['symbol'] = symbol
        user_states[user_id]['timeframe'] = timeframe
        
        keyboard = [
            [
                InlineKeyboardButton("🌊 إليوت", callback_data=f"chart_elliott_{symbol}_{timeframe}"),
                InlineKeyboardButton("📊 كلاسيكي", callback_data=f"chart_classic_{symbol}_{timeframe}")
            ],
            [
                InlineKeyboardButton("🔷 توافقي", callback_data=f"chart_harmonic_{symbol}_{timeframe}"),
                InlineKeyboardButton("🎯 ICT", callback_data=f"chart_ict_{symbol}_{timeframe}")
            ],
            [
                InlineKeyboardButton("📋 تحليل شامل (الكل)", callback_data=f"chart_all_{symbol}_{timeframe}")
            ],
            [
                InlineKeyboardButton("🔙 رجوع", callback_data=f"back_{symbol}")
            ]
        ]
        
        tf_name = TIMEFRAMES[timeframe]['name']
        
        await query.edit_message_text(
            f"📊 **{symbol}** - فريم {tf_name}\n\n"
            "اختر نوع التحليل للشارت:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # رجوع
    elif data.startswith('back_'):
        symbol = data.replace('back_', '')
        info = get_stock_info(symbol)
        
        keyboard = [
            [
                InlineKeyboardButton("15 دقيقة", callback_data=f"tf_15m_{symbol}"),
                InlineKeyboardButton("30 دقيقة", callback_data=f"tf_30m_{symbol}")
            ],
            [
                InlineKeyboardButton("1 ساعة", callback_data=f"tf_1h_{symbol}"),
                InlineKeyboardButton("4 ساعات", callback_data=f"tf_4h_{symbol}")
            ],
            [
                InlineKeyboardButton("📊 يومي", callback_data=f"tf_1d_{symbol}")
            ]
        ]
        
        await query.edit_message_text(
            f"📊 **{symbol}**\n\nاختر الفريم الزمني:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def handle_chart_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_approved(user_id):
        return
    
    data = query.data
    
    if not data.startswith('chart_'):
        return
    
    parts = data.split('_')
    analysis_type = parts[1]
    symbol = parts[2]
    timeframe = parts[3]
    
    if analysis_type == 'all':
        analysis_types = ['elliott', 'classic', 'harmonic', 'ict']
    else:
        analysis_types = [analysis_type]
    
    await generate_and_send_chart(query, context, symbol, timeframe, analysis_types)

async def generate_and_send_chart(query, context, symbol: str, timeframe: str, analysis_types: list):
    """توليد وإرسال الشارت"""
    
    await query.edit_message_text(f"⏳ جاري إنشاء الشارت لـ {symbol}...")
    
    # جلب البيانات
    df = get_stock_data(symbol, timeframe)
    
    if df.empty or len(df) < 20:
        await query.edit_message_text(
            f"❌ بيانات غير كافية لـ {symbol}\n\n"
            "جرب فريم زمني أطول."
        )
        return
    
    tf_name = TIMEFRAMES[timeframe]['name']
    info = get_stock_info(symbol)
    
    try:
        # إنشاء الشارت
        chart_buffer = chart_drawer.generate_chart(
            df, symbol, tf_name, analysis_types
        )
        
        # إنشاء التحليل النصي
        analysis_text = await generate_analysis_text(df, symbol, timeframe, analysis_types, info)
        
        # إرسال الصورة
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=chart_buffer,
            caption=analysis_text[:1024],  # حد تيليجرام
            parse_mode='Markdown'
        )
        
        # أزرار المتابعة
        keyboard = [
            [
                InlineKeyboardButton("🔄 تحديث", callback_data=f"chart_{'_'.join(analysis_types)}_{symbol}_{timeframe}"),
                InlineKeyboardButton("📋 شامل", callback_data=f"chart_all_{symbol}_{timeframe}")
            ],
            [
                InlineKeyboardButton("🔙 تغيير الفريم", callback_data=f"back_{symbol}"),
                InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")
            ]
        ]
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر الإجراء التالي:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        # حذف رسالة الانتظار
        try:
            await query.message.delete()
        except:
            pass
        
    except Exception as e:
        logger.error(f"Chart error: {e}")
        await query.edit_message_text(f"❌ حدث خطأ: {str(e)}")

async def generate_analysis_text(df, symbol: str, timeframe: str, analysis_types: list, info: dict) -> str:
    """توليد النص التحليلي"""
    
    tf_name = TIMEFRAMES[timeframe]['name']
    change_emoji = "📈" if info['change'] >= 0 else "📉"
    
    text = f"📊 **{info['name']}** ({symbol})\n"
    text += f"⏰ {tf_name} | 💰 ${info['price']:.2f} {change_emoji} {info['change']:+.2f}%\n"
    text += "─" * 20 + "\n\n"
    
    try:
        if 'elliott' in analysis_types or 'all' in analysis_types:
            elliott = ElliottWaveAnalyzer().analyze(df)
            text += f"🌊 **إليوت:** {elliott.current_wave} ({elliott.trend})\n"
        
        if 'classic' in analysis_types or 'all' in analysis_types:
            classic = ClassicAnalyzer().analyze(df)
            text += f"📊 **كلاسيكي:** {classic.current_trend} - {classic.signal.value}\n"
        
        if 'harmonic' in analysis_types or 'all' in analysis_types:
            harmonic = HarmonicAnalyzer().analyze(df)
            if harmonic.patterns:
                p = harmonic.patterns[0]
                text += f"🔷 **توافقي:** {p.pattern_type.value}\n"
            else:
                text += "🔷 **توافقي:** لا نماذج\n"
        
        if 'ict' in analysis_types or 'all' in analysis_types:
            ict = ICTAnalyzer().analyze(df)
            text += f"🎯 **ICT:** {ict.market_structure.value}\n"
        
    except Exception as e:
        logger.error(f"Analysis text error: {e}")
        text += "\n⚠️ بعض التحليلات غير متاحة"
    
    text += f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    return text

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "main_menu":
        await start_command(update, context)

# ============================================
# الدالة الرئيسية
# ============================================

def main():
    TOKEN = os.environ.get('BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ BOT_TOKEN غير موجود!")
        print("❌ خطأ: BOT_TOKEN غير موجود")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # الأوامر
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("pending", pending_command))
    app.add_handler(CommandHandler("remove", remove_command))
    
    # معالجات الأزرار
    app.add_handler(CallbackQueryHandler(handle_approval, pattern=r'^(approve|reject)_'))
    app.add_handler(CallbackQueryHandler(handle_chart_request, pattern=r'^chart_'))
    app.add_handler(CallbackQueryHandler(handle_main_menu, pattern=r'^main_menu$'))
    app.add_handler(CallbackQueryHandler(handle_timeframe))
    
    # الرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol))
    
    logger.info("🚀 بدء تشغيل البوت...")
    print("=" * 50)
    print("🤖 بوت التحليل الفني المتقدم")
    print("📊 مع رسم الشارتات")
    print("🔒 نظام طلبات الوصول مفعّل")
    print(f"👑 المشرف: {ADMIN_ID}")
    print("=" * 50)
    
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
هل الكود يحتوي على مشكلة؟ - Manus
