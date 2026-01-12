"""
محرك التحليل الكلاسيكي
Classic Technical Analysis Engine
النماذج الفنية - الدعم والمقاومة - خطوط الاتجاه - القنوات
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class PatternType(Enum):
    # نماذج انعكاسية
    HEAD_SHOULDERS = "رأس وكتفين"
    INVERSE_HEAD_SHOULDERS = "رأس وكتفين مقلوب"
    DOUBLE_TOP = "قمة مزدوجة"
    DOUBLE_BOTTOM = "قاع مزدوج"
    TRIPLE_TOP = "قمة ثلاثية"
    TRIPLE_BOTTOM = "قاع ثلاثي"
    
    # نماذج استمرارية
    ASCENDING_TRIANGLE = "مثلث صاعد"
    DESCENDING_TRIANGLE = "مثلث هابط"
    SYMMETRIC_TRIANGLE = "مثلث متماثل"
    FLAG = "علم"
    PENNANT = "راية"
    WEDGE_UP = "وتد صاعد"
    WEDGE_DOWN = "وتد هابط"
    CHANNEL_UP = "قناة صاعدة"
    CHANNEL_DOWN = "قناة هابطة"
    
    # نماذج أخرى
    RECTANGLE = "مستطيل"
    CUP_HANDLE = "كوب وعروة"

class SignalType(Enum):
    BUY = "شراء"
    SELL = "بيع"
    NEUTRAL = "محايد"

@dataclass
class SupportResistance:
    level: float
    strength: int  # عدد مرات الاختبار
    type: str  # 'support' or 'resistance'
    last_test_idx: int

@dataclass
class TrendLine:
    slope: float
    intercept: float
    start_idx: int
    end_idx: int
    type: str  # 'support' or 'resistance'
    touches: int

@dataclass
class Pattern:
    pattern_type: PatternType
    start_idx: int
    end_idx: int
    confidence: float
    target_price: float
    stop_loss: float
    signal: SignalType
    description: str

@dataclass
class ClassicAnalysisResult:
    supports: List[SupportResistance]
    resistances: List[SupportResistance]
    trend_lines: List[TrendLine]
    patterns: List[Pattern]
    current_trend: str
    key_levels: Dict[str, float]
    signal: SignalType
    analysis_text: str

class ClassicAnalyzer:
    """محلل التحليل الكلاسيكي"""
    
    def __init__(self):
        self.tolerance = 0.02  # 2% tolerance for level matching
    
    def find_support_resistance(self, df: pd.DataFrame, lookback: int = 20) -> Tuple[List[SupportResistance], List[SupportResistance]]:
        """
        تحديد مستويات الدعم والمقاومة
        """
        supports = []
        resistances = []
        
        highs = df['High'].values
        lows = df['Low'].values
        closes = df['Close'].values
        
        # تجميع المستويات المهمة
        levels = {}
        
        for i in range(lookback, len(df)):
            # البحث عن القمم المحلية (مقاومة)
            if highs[i] == max(highs[i-lookback:i+1]):
                level = round(highs[i], 2)
                if level not in levels:
                    levels[level] = {'type': 'resistance', 'count': 0, 'last_idx': i}
                levels[level]['count'] += 1
                levels[level]['last_idx'] = i
            
            # البحث عن القيعان المحلية (دعم)
            if lows[i] == min(lows[i-lookback:i+1]):
                level = round(lows[i], 2)
                if level not in levels:
                    levels[level] = {'type': 'support', 'count': 0, 'last_idx': i}
                levels[level]['count'] += 1
                levels[level]['last_idx'] = i
        
        # تجميع المستويات المتقاربة
        merged_levels = self._merge_close_levels(levels)
        
        current_price = closes[-1]
        
        for level, data in merged_levels.items():
            sr = SupportResistance(
                level=level,
                strength=data['count'],
                type=data['type'],
                last_test_idx=data['last_idx']
            )
            
            # تحديد إذا كان دعم أو مقاومة بناءً على السعر الحالي
            if level < current_price:
                supports.append(sr)
            else:
                resistances.append(sr)
        
        # ترتيب حسب القوة
        supports.sort(key=lambda x: (-x.strength, -x.level))
        resistances.sort(key=lambda x: (-x.strength, x.level))
        
        return supports[:5], resistances[:5]  # أقوى 5 مستويات
    
    def _merge_close_levels(self, levels: Dict) -> Dict:
        """
        دمج المستويات المتقاربة
        """
        if not levels:
            return {}
        
        sorted_levels = sorted(levels.keys())
        merged = {}
        
        current_group = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            if (level - current_group[-1]) / current_group[-1] < self.tolerance:
                current_group.append(level)
            else:
                # حفظ المجموعة السابقة
                avg_level = sum(current_group) / len(current_group)
                total_count = sum(levels[l]['count'] for l in current_group)
                last_idx = max(levels[l]['last_idx'] for l in current_group)
                merged[round(avg_level, 2)] = {
                    'type': levels[current_group[0]]['type'],
                    'count': total_count,
                    'last_idx': last_idx
                }
                current_group = [level]
        
        # حفظ المجموعة الأخيرة
        if current_group:
            avg_level = sum(current_group) / len(current_group)
            total_count = sum(levels[l]['count'] for l in current_group)
            last_idx = max(levels[l]['last_idx'] for l in current_group)
            merged[round(avg_level, 2)] = {
                'type': levels[current_group[0]]['type'],
                'count': total_count,
                'last_idx': last_idx
            }
        
        return merged
    
    def detect_trend(self, df: pd.DataFrame, period: int = 20) -> Tuple[str, float]:
        """
        تحديد الاتجاه العام
        """
        closes = df['Close'].values
        
        if len(closes) < period:
            return "غير محدد", 0
        
        # حساب المتوسط المتحرك
        ma = pd.Series(closes).rolling(window=period).mean().values
        
        # حساب ميل خط الاتجاه
        recent_ma = ma[-period:]
        x = np.arange(len(recent_ma))
        
        # إزالة NaN
        valid_idx = ~np.isnan(recent_ma)
        if sum(valid_idx) < 2:
            return "غير محدد", 0
        
        slope, _ = np.polyfit(x[valid_idx], recent_ma[valid_idx], 1)
        
        # تحديد الاتجاه
        slope_percent = (slope / closes[-1]) * 100
        
        if slope_percent > 0.1:
            trend = "صاعد"
        elif slope_percent < -0.1:
            trend = "هابط"
        else:
            trend = "عرضي"
        
        return trend, slope_percent
    
    def find_trend_lines(self, df: pd.DataFrame, lookback: int = 5) -> List[TrendLine]:
        """
        رسم خطوط الاتجاه
        """
        trend_lines = []
        
        highs = df['High'].values
        lows = df['Low'].values
        
        # إيجاد القمم والقيعان
        high_points = []
        low_points = []
        
        for i in range(lookback, len(df) - lookback):
            if highs[i] == max(highs[i-lookback:i+lookback+1]):
                high_points.append((i, highs[i]))
            if lows[i] == min(lows[i-lookback:i+lookback+1]):
                low_points.append((i, lows[i]))
        
        # رسم خط اتجاه للقمم (مقاومة)
        if len(high_points) >= 2:
            points = high_points[-3:] if len(high_points) >= 3 else high_points
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            if len(set(x)) > 1:
                slope, intercept = np.polyfit(x, y, 1)
                trend_lines.append(TrendLine(
                    slope=slope,
                    intercept=intercept,
                    start_idx=x[0],
                    end_idx=x[-1],
                    type='resistance',
                    touches=len(points)
                ))
        
        # رسم خط اتجاه للقيعان (دعم)
        if len(low_points) >= 2:
            points = low_points[-3:] if len(low_points) >= 3 else low_points
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            if len(set(x)) > 1:
                slope, intercept = np.polyfit(x, y, 1)
                trend_lines.append(TrendLine(
                    slope=slope,
                    intercept=intercept,
                    start_idx=x[0],
                    end_idx=x[-1],
                    type='support',
                    touches=len(points)
                ))
        
        return trend_lines
    
    def detect_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """
        كشف النماذج الفنية
        """
        patterns = []
        
        highs = df['High'].values
        lows = df['Low'].values
        closes = df['Close'].values
        
        # كشف القمة المزدوجة
        pattern = self._detect_double_top(highs, closes)
        if pattern:
            patterns.append(pattern)
        
        # كشف القاع المزدوج
        pattern = self._detect_double_bottom(lows, closes)
        if pattern:
            patterns.append(pattern)
        
        # كشف الرأس والكتفين
        pattern = self._detect_head_shoulders(highs, lows, closes)
        if pattern:
            patterns.append(pattern)
        
        # كشف المثلثات
        pattern = self._detect_triangle(highs, lows, closes)
        if pattern:
            patterns.append(pattern)
        
        return patterns
    
    def _detect_double_top(self, highs: np.ndarray, closes: np.ndarray) -> Optional[Pattern]:
        """
        كشف نموذج القمة المزدوجة
        """
        if len(highs) < 20:
            return None
        
        # البحث عن قمتين متقاربتين
        recent_highs = highs[-30:]
        max_idx1 = np.argmax(recent_highs[:15])
        max_idx2 = np.argmax(recent_highs[15:]) + 15
        
        peak1 = recent_highs[max_idx1]
        peak2 = recent_highs[max_idx2]
        
        # التحقق من تقارب القمتين
        if abs(peak1 - peak2) / peak1 < 0.03:  # فرق أقل من 3%
            # البحث عن القاع بينهما
            valley = min(recent_highs[max_idx1:max_idx2+1])
            
            # حساب الهدف
            pattern_height = ((peak1 + peak2) / 2) - valley
            target = valley - pattern_height
            
            return Pattern(
                pattern_type=PatternType.DOUBLE_TOP,
                start_idx=len(highs) - 30 + max_idx1,
                end_idx=len(highs) - 30 + max_idx2,
                confidence=75,
                target_price=target,
                stop_loss=(peak1 + peak2) / 2 * 1.02,
                signal=SignalType.SELL,
                description=f"🔻 قمة مزدوجة عند ${peak1:.2f} - هدف ${target:.2f}"
            )
        
        return None
    
    def _detect_double_bottom(self, lows: np.ndarray, closes: np.ndarray) -> Optional[Pattern]:
        """
        كشف نموذج القاع المزدوج
        """
        if len(lows) < 20:
            return None
        
        recent_lows = lows[-30:]
        min_idx1 = np.argmin(recent_lows[:15])
        min_idx2 = np.argmin(recent_lows[15:]) + 15
        
        bottom1 = recent_lows[min_idx1]
        bottom2 = recent_lows[min_idx2]
        
        if abs(bottom1 - bottom2) / bottom1 < 0.03:
            peak = max(recent_lows[min_idx1:min_idx2+1])
            
            pattern_height = peak - ((bottom1 + bottom2) / 2)
            target = peak + pattern_height
            
            return Pattern(
                pattern_type=PatternType.DOUBLE_BOTTOM,
                start_idx=len(lows) - 30 + min_idx1,
                end_idx=len(lows) - 30 + min_idx2,
                confidence=75,
                target_price=target,
                stop_loss=(bottom1 + bottom2) / 2 * 0.98,
                signal=SignalType.BUY,
                description=f"🔺 قاع مزدوج عند ${bottom1:.2f} - هدف ${target:.2f}"
            )
        
        return None
    
    def _detect_head_shoulders(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> Optional[Pattern]:
        """
        كشف نموذج الرأس والكتفين
        """
        if len(highs) < 30:
            return None
        
        recent = highs[-40:]
        
        # البحث عن 3 قمم
        third = len(recent) // 3
        
        left_shoulder_idx = np.argmax(recent[:third])
        head_idx = np.argmax(recent[third:2*third]) + third
        right_shoulder_idx = np.argmax(recent[2*third:]) + 2*third
        
        left_shoulder = recent[left_shoulder_idx]
        head = recent[head_idx]
        right_shoulder = recent[right_shoulder_idx]
        
        # التحقق من الشروط
        if head > left_shoulder and head > right_shoulder:
            if abs(left_shoulder - right_shoulder) / left_shoulder < 0.05:
                # خط العنق
                neckline = min(lows[-40:][left_shoulder_idx:right_shoulder_idx+1])
                
                pattern_height = head - neckline
                target = neckline - pattern_height
                
                return Pattern(
                    pattern_type=PatternType.HEAD_SHOULDERS,
                    start_idx=len(highs) - 40 + left_shoulder_idx,
                    end_idx=len(highs) - 40 + right_shoulder_idx,
                    confidence=80,
                    target_price=target,
                    stop_loss=head * 1.02,
                    signal=SignalType.SELL,
                    description=f"👤 رأس وكتفين - خط العنق ${neckline:.2f} - هدف ${target:.2f}"
                )
        
        return None
    
    def _detect_triangle(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> Optional[Pattern]:
        """
        كشف نماذج المثلثات
        """
        if len(highs) < 20:
            return None
        
        recent_highs = highs[-20:]
        recent_lows = lows[-20:]
        
        # حساب ميل القمم والقيعان
        x = np.arange(len(recent_highs))
        
        high_slope, high_intercept = np.polyfit(x, recent_highs, 1)
        low_slope, low_intercept = np.polyfit(x, recent_lows, 1)
        
        # تحديد نوع المثلث
        if high_slope < -0.01 and low_slope > 0.01:
            # مثلث متماثل
            pattern_type = PatternType.SYMMETRIC_TRIANGLE
            signal = SignalType.NEUTRAL
            desc = "📐 مثلث متماثل - انتظار الاختراق"
        elif abs(high_slope) < 0.01 and low_slope > 0.01:
            # مثلث صاعد
            pattern_type = PatternType.ASCENDING_TRIANGLE
            signal = SignalType.BUY
            desc = "📐 مثلث صاعد - توقع اختراق صعودي"
        elif high_slope < -0.01 and abs(low_slope) < 0.01:
            # مثلث هابط
            pattern_type = PatternType.DESCENDING_TRIANGLE
            signal = SignalType.SELL
            desc = "📐 مثلث هابط - توقع اختراق هبوطي"
        else:
            return None
        
        # حساب الهدف
        pattern_height = recent_highs[0] - recent_lows[0]
        current_price = closes[-1]
        
        if signal == SignalType.BUY:
            target = current_price + pattern_height
        elif signal == SignalType.SELL:
            target = current_price - pattern_height
        else:
            target = current_price
        
        return Pattern(
            pattern_type=pattern_type,
            start_idx=len(highs) - 20,
            end_idx=len(highs) - 1,
            confidence=70,
            target_price=target,
            stop_loss=current_price * (0.98 if signal == SignalType.BUY else 1.02),
            signal=signal,
            description=desc
        )
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        حساب المؤشرات الفنية الأساسية
        """
        closes = df['Close']
        
        indicators = {}
        
        # RSI
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['RSI'] = (100 - (100 / (1 + rs))).iloc[-1]
        
        # MACD
        exp1 = closes.ewm(span=12, adjust=False).mean()
        exp2 = closes.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9, adjust=False).mean()
        indicators['MACD'] = macd.iloc[-1]
        indicators['MACD_Signal'] = signal_line.iloc[-1]
        indicators['MACD_Histogram'] = macd.iloc[-1] - signal_line.iloc[-1]
        
        # Moving Averages
        indicators['SMA_20'] = closes.rolling(window=20).mean().iloc[-1]
        indicators['SMA_50'] = closes.rolling(window=50).mean().iloc[-1]
        indicators['EMA_20'] = closes.ewm(span=20, adjust=False).mean().iloc[-1]
        
        # Bollinger Bands
        sma = closes.rolling(window=20).mean()
        std = closes.rolling(window=20).std()
        indicators['BB_Upper'] = (sma + (std * 2)).iloc[-1]
        indicators['BB_Lower'] = (sma - (std * 2)).iloc[-1]
        indicators['BB_Middle'] = sma.iloc[-1]
        
        return indicators
    
    def analyze(self, df: pd.DataFrame) -> ClassicAnalysisResult:
        """
        التحليل الكلاسيكي الكامل
        """
        # الدعم والمقاومة
        supports, resistances = self.find_support_resistance(df)
        
        # الاتجاه
        trend, trend_strength = self.detect_trend(df)
        
        # خطوط الاتجاه
        trend_lines = self.find_trend_lines(df)
        
        # النماذج
        patterns = self.detect_patterns(df)
        
        # المؤشرات
        indicators = self.calculate_indicators(df)
        
        # تحديد الإشارة العامة
        signal = self._determine_signal(trend, patterns, indicators)
        
        # المستويات الرئيسية
        current_price = df['Close'].iloc[-1]
        key_levels = {
            'السعر الحالي': current_price,
            'أقرب دعم': supports[0].level if supports else current_price * 0.95,
            'أقرب مقاومة': resistances[0].level if resistances else current_price * 1.05,
            'RSI': indicators.get('RSI', 50),
            'SMA 20': indicators.get('SMA_20', current_price),
            'SMA 50': indicators.get('SMA_50', current_price),
        }
        
        # بناء نص التحليل
        analysis_text = self._build_analysis_text(
            supports, resistances, trend, patterns, indicators, signal, current_price
        )
        
        return ClassicAnalysisResult(
            supports=supports,
            resistances=resistances,
            trend_lines=trend_lines,
            patterns=patterns,
            current_trend=trend,
            key_levels=key_levels,
            signal=signal,
            analysis_text=analysis_text
        )
    
    def _determine_signal(self, trend: str, patterns: List[Pattern], indicators: Dict) -> SignalType:
        """
        تحديد الإشارة العامة
        """
        buy_score = 0
        sell_score = 0
        
        # الاتجاه
        if trend == "صاعد":
            buy_score += 2
        elif trend == "هابط":
            sell_score += 2
        
        # النماذج
        for pattern in patterns:
            if pattern.signal == SignalType.BUY:
                buy_score += 3
            elif pattern.signal == SignalType.SELL:
                sell_score += 3
        
        # RSI
        rsi = indicators.get('RSI', 50)
        if rsi < 30:
            buy_score += 2
        elif rsi > 70:
            sell_score += 2
        
        # MACD
        macd_hist = indicators.get('MACD_Histogram', 0)
        if macd_hist > 0:
            buy_score += 1
        else:
            sell_score += 1
        
        if buy_score > sell_score + 2:
            return SignalType.BUY
        elif sell_score > buy_score + 2:
            return SignalType.SELL
        else:
            return SignalType.NEUTRAL
    
    def _build_analysis_text(self, supports, resistances, trend, patterns, indicators, signal, current_price) -> str:
        """
        بناء نص التحليل الكلاسيكي
        """
        text = "📊 **التحليل الكلاسيكي**\n\n"
        
        # الاتجاه
        trend_emoji = "📈" if trend == "صاعد" else "📉" if trend == "هابط" else "➡️"
        text += f"{trend_emoji} **الاتجاه**: {trend}\n\n"
        
        # الدعم والمقاومة
        text += "🛡️ **مستويات الدعم:**\n"
        for i, s in enumerate(supports[:3], 1):
            text += f"  {i}. ${s.level:.2f} (قوة: {'⭐' * min(s.strength, 5)})\n"
        
        text += "\n🎯 **مستويات المقاومة:**\n"
        for i, r in enumerate(resistances[:3], 1):
            text += f"  {i}. ${r.level:.2f} (قوة: {'⭐' * min(r.strength, 5)})\n"
        
        # النماذج
        if patterns:
            text += "\n📐 **النماذج المكتشفة:**\n"
            for p in patterns:
                text += f"  • {p.description}\n"
        
        # المؤشرات
        text += "\n📈 **المؤشرات:**\n"
        rsi = indicators.get('RSI', 50)
        rsi_status = "تشبع شرائي 🔴" if rsi > 70 else "تشبع بيعي 🟢" if rsi < 30 else "طبيعي ⚪"
        text += f"  • RSI: {rsi:.1f} ({rsi_status})\n"
        
        macd_hist = indicators.get('MACD_Histogram', 0)
        macd_status = "إيجابي 🟢" if macd_hist > 0 else "سلبي 🔴"
        text += f"  • MACD: {macd_status}\n"
        
        # الإشارة
        signal_emoji = "🟢" if signal == SignalType.BUY else "🔴" if signal == SignalType.SELL else "⚪"
        text += f"\n{signal_emoji} **الإشارة العامة**: {signal.value}\n"
        
        return text
