"""
بوت التحليل الفني المتقدم
Advanced Technical Analysis Telegram Bot
موجات إليوت - التحليل الكلاسيكي - التحليل التوافقي - مدرسة ICT
"""

import os
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

# الفريمات الزمنية
TIMEFRAMES = {
    '15m': {'interval': '15m', 'period': '5d', 'name': '15 دقيقة'},
    '30m': {'interval': '30m', 'period': '10d', 'name': '30 دقيقة'},
    '1h': {'interval': '1h', 'period': '1mo', 'name': '1 ساعة'},
    '4h': {'interval': '1h', 'period': '3mo', 'name': '4 ساعات'},  # سنجمع البيانات
    '1d': {'interval': '1d', 'period': '6mo', 'name': 'يومي'},
}

# أنواع التحليل
ANALYSIS_TYPES = {
    'elliott': {'name': '🌊 موجات إليوت', 'analyzer': ElliottWaveAnalyzer},
    'classic': {'name': '📊 التحليل الكلاسيكي', 'analyzer': ClassicAnalyzer},
    'harmonic': {'name': '🔷 التحليل التوافقي', 'analyzer': HarmonicAnalyzer},
    'ict': {'name': '🎯 مدرسة ICT', 'analyzer': ICTAnalyzer},
    'full': {'name': '📋 تحليل شامل', 'analyzer': None},
}

# تخزين حالة المستخدم
user_states = {}

def get_stock_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """
    جلب بيانات السهم
    """
    try:
        tf_config = TIMEFRAMES.get(timeframe, TIMEFRAMES['1d'])
        
        stock = yf.Ticker(symbol)
        
        if timeframe == '4h':
            # جلب بيانات الساعة وتجميعها لـ 4 ساعات
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
    """
    جلب معلومات السهم
    """
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    أمر البدء
    """
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

async def handle_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    معالجة رمز السهم المدخل
    """
    symbol = update.message.text.strip().upper()
    user_id = update.effective_user.id
    
    # التحقق من صحة الرمز
    await update.message.reply_text(f"⏳ جاري البحث عن {symbol}...")
    
    # جلب معلومات السهم
    info = get_stock_info(symbol)
    
    if info['price'] == 0:
        await update.message.reply_text(
            f"❌ لم يتم العثور على السهم: {symbol}\n\n"
            "تأكد من صحة الرمز وحاول مرة أخرى."
        )
        return
    
    # حفظ الرمز في حالة المستخدم
    user_states[user_id] = {'symbol': symbol, 'info': info}
    
    # عرض قائمة الفريمات
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
    """
    معالجة اختيار الفريم الزمني
    """
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith('tf_'):
        parts = data.split('_')
        timeframe = parts[1]
        symbol = parts[2]
        
        user_id = update.effective_user.id
        user_states[user_id] = user_states.get(user_id, {})
        user_states[user_id]['symbol'] = symbol
        user_states[user_id]['timeframe'] = timeframe
        
        # عرض قائمة أنواع التحليل
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
        # إعادة عرض قائمة الفريمات
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
    """
    معالجة اختيار نوع التحليل
    """
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if not data.startswith('analyze_'):
        return
    
    parts = data.split('_')
    analysis_type = parts[1]
    symbol = parts[2]
    timeframe = parts[3]
    
    await query.edit_message_text(f"⏳ جاري تحليل {symbol}...")
    
    # جلب البيانات
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
        
        # أزرار التنقل
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث", callback_data=f"analyze_{analysis_type}_{symbol}_{timeframe}")],
            [InlineKeyboardButton("📋 تحليل شامل", callback_data=f"analyze_full_{symbol}_{timeframe}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data=f"tf_{timeframe}_{symbol}")]
        ]
        
        # تقسيم الرسالة إذا كانت طويلة
        if len(text) > 4000:
            text = text[:4000] + "\n\n... (تم اختصار النص)"
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        await query.edit_message_text(
            f"❌ حدث خطأ أثناء التحليل\n\n{str(e)}"
        )

async def perform_full_analysis(query, symbol: str, timeframe: str):
    """
    تنفيذ التحليل الشامل
    """
    await query.edit_message_text(f"⏳ جاري التحليل الشامل لـ {symbol}...")
    
    df = get_stock_data(symbol, timeframe)
    
    if df.empty or len(df) < 20:
        await query.edit_message_text(f"❌ بيانات غير كافية لـ {symbol}")
        return
    
    tf_name = TIMEFRAMES[timeframe]['name']
    info = get_stock_info(symbol)
    
    # تنفيذ جميع التحليلات
    try:
        elliott = ElliottWaveAnalyzer().analyze(df)
        classic = ClassicAnalyzer().analyze(df)
        harmonic = HarmonicAnalyzer().analyze(df)
        ict = ICTAnalyzer().analyze(df)
        
        # بناء التقرير الشامل
        change_emoji = "📈" if info['change'] >= 0 else "📉"
        
        text = f"📋 **تقرير شامل: {info['name']}** ({symbol})\n"
        text += f"⏰ الفريم: {tf_name}\n"
        text += f"💰 السعر: ${info['price']:.2f} {change_emoji} {info['change']:+.2f}%\n"
        text += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        text += "═" * 30 + "\n\n"
        
        # ملخص موجات إليوت
        text += "🌊 **موجات إليوت:**\n"
        text += f"  • الموجة الحالية: {elliott.current_wave}\n"
        text += f"  • الاتجاه: {elliott.trend}\n"
        text += f"  • الثقة: {elliott.confidence:.0f}%\n\n"
        
        # ملخص التحليل الكلاسيكي
        text += "📊 **التحليل الكلاسيكي:**\n"
        text += f"  • الاتجاه: {classic.current_trend}\n"
        text += f"  • الإشارة: {classic.signal.value}\n"
        if classic.supports:
            text += f"  • أقرب دعم: ${classic.supports[0].level:.2f}\n"
        if classic.resistances:
            text += f"  • أقرب مقاومة: ${classic.resistances[0].level:.2f}\n"
        text += "\n"
        
        # ملخص التحليل التوافقي
        text += "🔷 **التحليل التوافقي:**\n"
        if harmonic.patterns:
            p = harmonic.patterns[0]
            text += f"  • نموذج: {p.pattern_type.value} ({p.direction.value})\n"
            text += f"  • الثقة: {p.confidence:.0f}%\n"
            text += f"  • الهدف: ${p.target_1:.2f}\n"
        else:
            text += "  • لا توجد أنماط مكتملة\n"
        text += "\n"
        
        # ملخص ICT
        text += "🎯 **تحليل ICT:**\n"
        text += f"  • هيكل السوق: {ict.market_structure.value}\n"
        text += f"  • المنطقة: {ict.premium_discount}\n"
        if ict.optimal_trade_entry.get('direction'):
            text += f"  • التوصية: {ict.optimal_trade_entry['direction']}\n"
        text += "\n"
        
        # التوصية النهائية
        text += "═" * 30 + "\n"
        text += "💡 **التوصية النهائية:**\n"
        
        # حساب التوصية بناءً على جميع التحليلات
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
    """
    أمر المساعدة
    """
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
        "• مستويات فيبوناتشي\n"
        "• نسبة الثقة في الترقيم\n\n"
        "📊 **التحليل الكلاسيكي:**\n"
        "• الدعم والمقاومة\n"
        "• خطوط الاتجاه\n"
        "• النماذج الفنية\n"
        "• المؤشرات (RSI, MACD)\n\n"
        "🔷 **التحليل التوافقي:**\n"
        "• نماذج Gartley, Butterfly\n"
        "• نماذج Bat, Crab\n"
        "• نموذج ABCD\n"
        "• مناطق الانعكاس\n\n"
        "🎯 **مدرسة ICT:**\n"
        "• هيكل السوق (BOS, CHoCH)\n"
        "• Order Blocks\n"
        "• Fair Value Gaps\n"
        "• مناطق السيولة\n"
        "• Premium/Discount\n\n"
        "**الفريمات المتاحة:**\n"
        "15د | 30د | 1س | 4س | يومي\n\n"
        "⚠️ **تنبيه:**\n"
        "التحليلات للمعلومات فقط.\n"
        "استشر مختصاً قبل الاستثمار."
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

def main():
    """
    الدالة الرئيسية
    """
    TOKEN = os.environ.get('BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ BOT_TOKEN غير موجود!")
        print("❌ خطأ: BOT_TOKEN غير موجود في Environment Variables")
        return
    
    # إنشاء التطبيق
    app = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # معالج الأزرار
    app.add_handler(CallbackQueryHandler(handle_analysis_selection, pattern=r'^analyze_'))
    app.add_handler(CallbackQueryHandler(handle_timeframe_selection))
    
    # معالج الرسائل النصية (رموز الأسهم)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol))
    
    # بدء التشغيل
    logger.info("🚀 بدء تشغيل البوت...")
    print("=" * 50)
    print("🤖 بوت التحليل الفني المتقدم")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 التحليلات المتاحة:")
    print("   • موجات إليوت")
    print("   • التحليل الكلاسيكي")
    print("   • التحليل التوافقي")
    print("   • مدرسة ICT")
    print("⏰ الفريمات: 15د | 30د | 1س | 4س | يومي")
    print("=" * 50)
    
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
