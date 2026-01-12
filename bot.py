"""
بوت التحليل الفني المتقدم
Advanced Technical Analysis Telegram Bot
موجات إليوت - التحليل الكلاسيكي - التحليل التوافقي - مدرسة ICT
مع نظام طلبات الوصول
"""

import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yfinance as yf
import pandas as pd

# استيراد محركات التحليل
from elliott_waves import ElliottWaveAnalyzer
from classic_analysis import ClassicAnalyzer
from harmonic_patterns import HarmonicAnalyzer
from ict_analysis import ICTAnalyzer

# إعدادات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# إعدادات الصلاحيات
# ============================================

# المشرف الرئيسي (أنت)
ADMIN_ID = 1177923997

# ملف تخزين المستخدمين المعتمدين
APPROVED_USERS_FILE = "approved_users.json"

def load_approved_users():
    """تحميل قائمة المستخدمين المعتمدين"""
    try:
        if os.path.exists(APPROVED_USERS_FILE):
            with open(APPROVED_USERS_FILE, 'r') as f:
                return set(json.load(f))
    except:
        pass
    return {ADMIN_ID}  # المشرف دائماً معتمد

def save_approved_users(users):
    """حفظ قائمة المستخدمين المعتمدين"""
    try:
        with open(APPROVED_USERS_FILE, 'w') as f:
            json.dump(list(users), f)
    except Exception as e:
        logger.error(f"Error saving users: {e}")

# المستخدمين المعتمدين
approved_users = load_approved_users()

# طلبات الوصول المعلقة
pending_requests = {}

# ============================================
# الفريمات الزمنية وأنواع التحليل
# ============================================

TIMEFRAMES = {
    '15m': {'interval': '15m', 'period': '5d', 'name': '15 دقيقة'},
    '30m': {'interval': '30m', 'period': '10d', 'name': '30 دقيقة'},
    '1h': {'interval': '1h', 'period': '1mo', 'name': '1 ساعة'},
    '4h': {'interval': '1h', 'period': '3mo', 'name': '4 ساعات'},
    '1d': {'interval': '1d', 'period': '6mo', 'name': 'يومي'},
}

ANALYSIS_TYPES = {
    'elliott': {'name': '🌊 موجات إليوت', 'analyzer': ElliottWaveAnalyzer},
    'classic': {'name': '📊 التحليل الكلاسيكي', 'analyzer': ClassicAnalyzer},
    'harmonic': {'name': '🔷 التحليل التوافقي', 'analyzer': HarmonicAnalyzer},
    'ict': {'name': '🎯 مدرسة ICT', 'analyzer': ICTAnalyzer},
    'full': {'name': '📋 تحليل شامل', 'analyzer': None},
}

user_states = {}

# ============================================
# دوال التحقق من الصلاحيات
# ============================================

def is_approved(user_id: int) -> bool:
    """التحقق من أن المستخدم معتمد"""
    return user_id in approved_users or user_id == ADMIN_ID

def is_admin(user_id: int) -> bool:
    """التحقق من أن المستخدم مشرف"""
    return user_id == ADMIN_ID

# ============================================
# دوال جلب البيانات
# ============================================

def get_stock_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """جلب بيانات السهم"""
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
        
        return df
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()

def get_stock_info(symbol: str) -> dict:
    """جلب معلومات السهم"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            'name': info.get('shortName', symbol),
            'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'change': info.get('regularMarketChangePercent', 0),
            'volume': info.get('volume', 0),
            'market_cap': info.get('marketCap', 0),
        }
    except:
        return {'name': symbol, 'price': 0, 'change': 0, 'volume': 0, 'market_cap': 0}

# ============================================
# أوامر البوت
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البدء"""
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    username = update.effective_user.username or "بدون يوزر"
    
    # التحقق من الصلاحية
    if not is_approved(user_id):
        # إرسال طلب وصول
        if user_id not in pending_requests:
            pending_requests[user_id] = {
                'name': user_name,
                'username': username,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            
            # إرسال إشعار للمشرف
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
            
            await update.message.reply_text(
                "🔒 **البوت خاص**\n\n"
                "تم إرسال طلب وصول للمشرف.\n"
                "سيتم إعلامك عند الموافقة على طلبك.\n\n"
                "⏳ انتظر الموافقة..."
            )
        else:
            await update.message.reply_text(
                "⏳ **طلبك قيد المراجعة**\n\n"
                "تم إرسال طلبك مسبقاً.\n"
                "انتظر موافقة المشرف."
            )
        return
    
    # المستخدم معتمد - عرض القائمة الرئيسية
    text = (
        "🤖 **بوت التحليل الفني المتقدم**\n\n"
        "أرسل **رمز السهم** للحصول على تحليل شامل\n\n"
        "**أمثلة:**\n"
        "• `AAPL` - Apple\n"
        "• `TSLA` - Tesla\n"
        "• `MSFT` - Microsoft\n"
        "• `NVDA` - NVIDIA\n"
        "• `AMZN` - Amazon\n"
        "• `2222.SR` - أرامكو\n\n"
        "**أنواع التحليل المتاحة:**\n"
        "🌊 موجات إليوت\n"
        "📊 التحليل الكلاسيكي\n"
        "🔷 التحليل التوافقي\n"
        "🎯 مدرسة ICT\n\n"
        "**الفريمات:**\n"
        "15د | 30د | 1س | 4س | يومي\n\n"
        "📝 أرسل رمز السهم للبدء..."
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أوامر المشرف"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ هذا الأمر للمشرف فقط.")
        return
    
    text = (
        "👑 **لوحة تحكم المشرف**\n\n"
        f"👥 المستخدمين المعتمدين: {len(approved_users)}\n"
        f"⏳ الطلبات المعلقة: {len(pending_requests)}\n\n"
        "**الأوامر:**\n"
        "/users - عرض المستخدمين المعتمدين\n"
        "/pending - عرض الطلبات المعلقة\n"
        "/remove [ID] - إزالة مستخدم\n"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المستخدمين المعتمدين"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ هذا الأمر للمشرف فقط.")
        return
    
    if not approved_users:
        await update.message.reply_text("لا يوجد مستخدمين معتمدين.")
        return
    
    text = "👥 **المستخدمين المعتمدين:**\n\n"
    for uid in approved_users:
        admin_mark = " 👑" if uid == ADMIN_ID else ""
        text += f"• `{uid}`{admin_mark}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الطلبات المعلقة"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ هذا الأمر للمشرف فقط.")
        return
    
    if not pending_requests:
        await update.message.reply_text("✅ لا توجد طلبات معلقة.")
        return
    
    text = "⏳ **الطلبات المعلقة:**\n\n"
    for uid, info in pending_requests.items():
        keyboard = [
            [
                InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{uid}"),
                InlineKeyboardButton("❌ رفض", callback_data=f"reject_{uid}")
            ]
        ]
        await update.message.reply_text(
            f"👤 {info['name']}\n"
            f"🆔 @{info['username']}\n"
            f"🔢 `{uid}`\n"
            f"⏰ {info['time']}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إزالة مستخدم"""
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
            await update.message.reply_text(f"✅ تم إزالة المستخدم `{target_id}`", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ المستخدم غير موجود في القائمة.")
    except ValueError:
        await update.message.reply_text("❌ ID غير صحيح.")

async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الموافقة/الرفض"""
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
        
        # إعلام المستخدم
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=(
                    "✅ **تمت الموافقة على طلبك!**\n\n"
                    "يمكنك الآن استخدام البوت.\n"
                    "أرسل /start للبدء."
                )
            )
        except:
            pass
        
        await query.edit_message_text(f"✅ تمت الموافقة على المستخدم `{target_id}`", parse_mode='Markdown')
    
    elif data.startswith('reject_'):
        target_id = int(data.replace('reject_', ''))
        
        if target_id in pending_requests:
            del pending_requests[target_id]
        
        # إعلام المستخدم
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="❌ **تم رفض طلبك.**\n\nللتواصل مع المشرف، راسله مباشرة."
            )
        except:
            pass
        
        await query.edit_message_text(f"❌ تم رفض المستخدم `{target_id}`", parse_mode='Markdown')

# ============================================
# معالجة رموز الأسهم
# ============================================

async def handle_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة رمز السهم المدخل"""
    user_id = update.effective_user.id
    
    # التحقق من الصلاحية
    if not is_approved(user_id):
        await update.message.reply_text(
            "🔒 **غير مصرح**\n\n"
            "أرسل /start لطلب الوصول."
        )
        return
    
    symbol = update.message.text.strip().upper()
    
    await update.message.reply_text(f"⏳ جاري البحث عن {symbol}...")
    
    info = get_stock_info(symbol)
    
    if info['price'] == 0:
        await update.message.reply_text(
            f"❌ لم يتم العثور على السهم: {symbol}\n\n"
            "تأكد من صحة الرمز وحاول مرة أخرى."
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
            InlineKeyboardButton("يومي", callback_data=f"tf_1d_{symbol}")
        ],
        [
            InlineKeyboardButton("📋 تحليل شامل (يومي)", callback_data=f"full_{symbol}")
        ]
    ]
    
    change_emoji = "📈" if info['change'] >= 0 else "📉"
    
    text = (
        f"📊 **{info['name']}** ({symbol})\n\n"
        f"💰 السعر: ${info['price']:.2f}\n"
        f"{change_emoji} التغير: {info['change']:+.2f}%\n\n"
        "اختر الفريم الزمني:"
    )
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_timeframe_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة اختيار الفريم الزمني"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_approved(user_id):
        return
    
    data = query.data
    
    if data.startswith('tf_'):
        parts = data.split('_')
        timeframe = parts[1]
        symbol = parts[2]
        
        user_states[user_id] = user_states.get(user_id, {})
        user_states[user_id]['symbol'] = symbol
        user_states[user_id]['timeframe'] = timeframe
        
        keyboard = [
            [InlineKeyboardButton("🌊 موجات إليوت", callback_data=f"analyze_elliott_{symbol}_{timeframe}")],
            [InlineKeyboardButton("📊 التحليل الكلاسيكي", callback_data=f"analyze_classic_{symbol}_{timeframe}")],
            [InlineKeyboardButton("🔷 التحليل التوافقي", callback_data=f"analyze_harmonic_{symbol}_{timeframe}")],
            [InlineKeyboardButton("🎯 مدرسة ICT", callback_data=f"analyze_ict_{symbol}_{timeframe}")],
            [InlineKeyboardButton("📋 تحليل شامل", callback_data=f"analyze_full_{symbol}_{timeframe}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data=f"back_{symbol}")]
        ]
        
        tf_name = TIMEFRAMES[timeframe]['name']
        
        await query.edit_message_text(
            f"📊 **{symbol}** - فريم {tf_name}\n\n"
            "اختر نوع التحليل:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data.startswith('full_'):
        symbol = data.replace('full_', '')
        await perform_full_analysis(query, symbol, '1d')
    
    elif data.startswith('back_'):
        symbol = data.replace('back_', '')
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
                InlineKeyboardButton("يومي", callback_data=f"tf_1d_{symbol}")
            ]
        ]
        
        await query.edit_message_text(
            f"📊 **{symbol}**\n\nاختر الفريم الزمني:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def handle_analysis_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة اختيار نوع التحليل"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_approved(user_id):
        return
    
    data = query.data
    
    if not data.startswith('analyze_'):
        return
    
    parts = data.split('_')
    analysis_type = parts[1]
    symbol = parts[2]
    timeframe = parts[3]
    
    await query.edit_message_text(f"⏳ جاري تحليل {symbol}...")
    
    df = get_stock_data(symbol, timeframe)
    
    if df.empty or len(df) < 20:
        await query.edit_message_text(
            f"❌ بيانات غير كافية لـ {symbol}\n\n"
            "جرب فريم زمني أطول."
        )
        return
    
    tf_name = TIMEFRAMES[timeframe]['name']
    
    try:
        if analysis_type == 'elliott':
            analyzer = ElliottWaveAnalyzer()
            result = analyzer.analyze(df)
            text = f"📊 **{symbol}** - {tf_name}\n\n{result.analysis_text}"
        
        elif analysis_type == 'classic':
            analyzer = ClassicAnalyzer()
            result = analyzer.analyze(df)
            text = f"📊 **{symbol}** - {tf_name}\n\n{result.analysis_text}"
        
        elif analysis_type == 'harmonic':
            analyzer = HarmonicAnalyzer()
            result = analyzer.analyze(df)
            text = f"📊 **{symbol}** - {tf_name}\n\n{result.analysis_text}"
        
        elif analysis_type == 'ict':
            analyzer = ICTAnalyzer()
            result = analyzer.analyze(df)
            text = f"📊 **{symbol}** - {tf_name}\n\n{result.analysis_text}"
        
        elif analysis_type == 'full':
            await perform_full_analysis(query, symbol, timeframe)
            return
        
        else:
            text = "نوع تحليل غير معروف"
        
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث", callback_data=f"analyze_{analysis_type}_{symbol}_{timeframe}")],
            [InlineKeyboardButton("📋 تحليل شامل", callback_data=f"analyze_full_{symbol}_{timeframe}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data=f"tf_{timeframe}_{symbol}")]
        ]
        
        if len(text) > 4000:
            text = text[:4000] + "\n\n... (تم اختصار النص)"
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        await query.edit_message_text(f"❌ حدث خطأ أثناء التحليل\n\n{str(e)}")

async def perform_full_analysis(query, symbol: str, timeframe: str):
    """تنفيذ التحليل الشامل"""
    await query.edit_message_text(f"⏳ جاري التحليل الشامل لـ {symbol}...")
    
    df = get_stock_data(symbol, timeframe)
    
    if df.empty or len(df) < 20:
        await query.edit_message_text(f"❌ بيانات غير كافية لـ {symbol}")
        return
    
    tf_name = TIMEFRAMES[timeframe]['name']
    info = get_stock_info(symbol)
    
    try:
        elliott = ElliottWaveAnalyzer().analyze(df)
        classic = ClassicAnalyzer().analyze(df)
        harmonic = HarmonicAnalyzer().analyze(df)
        ict = ICTAnalyzer().analyze(df)
        
        change_emoji = "📈" if info['change'] >= 0 else "📉"
        
        text = f"📋 **تقرير شامل: {info['name']}** ({symbol})\n"
        text += f"⏰ الفريم: {tf_name}\n"
        text += f"💰 السعر: ${info['price']:.2f} {change_emoji} {info['change']:+.2f}%\n"
        text += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        text += "═" * 30 + "\n\n"
        
        text += "🌊 **موجات إليوت:**\n"
        text += f"  • الموجة الحالية: {elliott.current_wave}\n"
        text += f"  • الاتجاه: {elliott.trend}\n"
        text += f"  • الثقة: {elliott.confidence:.0f}%\n\n"
        
        text += "📊 **التحليل الكلاسيكي:**\n"
        text += f"  • الاتجاه: {classic.current_trend}\n"
        text += f"  • الإشارة: {classic.signal.value}\n"
        if classic.supports:
            text += f"  • أقرب دعم: ${classic.supports[0].level:.2f}\n"
        if classic.resistances:
            text += f"  • أقرب مقاومة: ${classic.resistances[0].level:.2f}\n"
        text += "\n"
        
        text += "🔷 **التحليل التوافقي:**\n"
        if harmonic.patterns:
            p = harmonic.patterns[0]
            text += f"  • نموذج: {p.pattern_type.value} ({p.direction.value})\n"
            text += f"  • الثقة: {p.confidence:.0f}%\n"
            text += f"  • الهدف: ${p.target_1:.2f}\n"
        else:
            text += "  • لا توجد أنماط مكتملة\n"
        text += "\n"
        
        text += "🎯 **تحليل ICT:**\n"
        text += f"  • هيكل السوق: {ict.market_structure.value}\n"
        text += f"  • المنطقة: {ict.premium_discount}\n"
        if ict.optimal_trade_entry.get('direction'):
            text += f"  • التوصية: {ict.optimal_trade_entry['direction']}\n"
        text += "\n"
        
        text += "═" * 30 + "\n"
        text += "💡 **التوصية النهائية:**\n"
        
        buy_signals = 0
        sell_signals = 0
        
        if elliott.trend == "صاعد":
            buy_signals += 1
        elif elliott.trend == "هابط":
            sell_signals += 1
        
        if classic.signal.value == "شراء":
            buy_signals += 1
        elif classic.signal.value == "بيع":
            sell_signals += 1
        
        if harmonic.patterns and harmonic.patterns[0].direction.value == "صاعد":
            buy_signals += 1
        elif harmonic.patterns and harmonic.patterns[0].direction.value == "هابط":
            sell_signals += 1
        
        if ict.market_structure.value == "هيكل صاعد":
            buy_signals += 1
        elif ict.market_structure.value == "هيكل هابط":
            sell_signals += 1
        
        if buy_signals > sell_signals + 1:
            text += "🟢 **شراء** - أغلب المؤشرات إيجابية\n"
        elif sell_signals > buy_signals + 1:
            text += "🔴 **بيع** - أغلب المؤشرات سلبية\n"
        else:
            text += "⚪ **انتظار** - إشارات متضاربة\n"
        
        text += f"\n📊 إشارات شراء: {buy_signals} | إشارات بيع: {sell_signals}"
        
        keyboard = [
            [
                InlineKeyboardButton("🌊 إليوت", callback_data=f"analyze_elliott_{symbol}_{timeframe}"),
                InlineKeyboardButton("📊 كلاسيكي", callback_data=f"analyze_classic_{symbol}_{timeframe}")
            ],
            [
                InlineKeyboardButton("🔷 توافقي", callback_data=f"analyze_harmonic_{symbol}_{timeframe}"),
                InlineKeyboardButton("🎯 ICT", callback_data=f"analyze_ict_{symbol}_{timeframe}")
            ],
            [InlineKeyboardButton("🔄 تحديث", callback_data=f"analyze_full_{symbol}_{timeframe}")],
            [InlineKeyboardButton("🔙 تغيير الفريم", callback_data=f"back_{symbol}")]
        ]
        
        if len(text) > 4000:
            text = text[:4000] + "\n\n... (تم اختصار النص)"
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Full analysis error: {e}")
        await query.edit_message_text(f"❌ حدث خطأ: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    text = (
        "❓ **دليل الاستخدام**\n\n"
        "**كيفية الاستخدام:**\n"
        "1. أرسل رمز السهم (مثل AAPL)\n"
        "2. اختر الفريم الزمني\n"
        "3. اختر نوع التحليل\n\n"
        "**أنواع التحليل:**\n\n"
        "🌊 **موجات إليوت:**\n"
        "• ترقيم الموجات (1-5, A-B-C)\n"
        "• تحديد القمم والقيعان\n"
        "• مستويات فيبوناتشي\n\n"
        "📊 **التحليل الكلاسيكي:**\n"
        "• الدعم والمقاومة\n"
        "• النماذج الفنية\n"
        "• المؤشرات (RSI, MACD)\n\n"
        "🔷 **التحليل التوافقي:**\n"
        "• نماذج Gartley, Butterfly\n"
        "• نماذج Bat, Crab\n\n"
        "🎯 **مدرسة ICT:**\n"
        "• Order Blocks\n"
        "• Fair Value Gaps\n"
        "• مناطق السيولة\n"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

def main():
    """الدالة الرئيسية"""
    TOKEN = os.environ.get('BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ BOT_TOKEN غير موجود!")
        print("❌ خطأ: BOT_TOKEN غير موجود في Environment Variables")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # أوامر عامة
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # أوامر المشرف
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("pending", pending_command))
    app.add_handler(CommandHandler("remove", remove_command))
    
    # معالجات الأزرار
    app.add_handler(CallbackQueryHandler(handle_approval, pattern=r'^(approve|reject)_'))
    app.add_handler(CallbackQueryHandler(handle_analysis_selection, pattern=r'^analyze_'))
    app.add_handler(CallbackQueryHandler(handle_timeframe_selection))
    
    # معالج الرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol))
    
    logger.info("🚀 بدء تشغيل البوت...")
    print("=" * 50)
    print("🤖 بوت التحليل الفني المتقدم")
    print("🔒 نظام طلبات الوصول مفعّل")
    print(f"👑 المشرف: {ADMIN_ID}")
    print(f"👥 المستخدمين المعتمدين: {len(approved_users)}")
    print("=" * 50)
    
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
