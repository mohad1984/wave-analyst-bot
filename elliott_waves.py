"""
محرك موجات إليوت المتقدم
Elliott Wave Analysis Engine
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class WaveType(Enum):
    IMPULSE = "دافعة"
    CORRECTIVE = "تصحيحية"

class WaveDirection(Enum):
    UP = "صاعدة"
    DOWN = "هابطة"

@dataclass
class Wave:
    number: str  # 1,2,3,4,5 أو A,B,C
    start_idx: int
    end_idx: int
    start_price: float
    end_price: float
    wave_type: WaveType
    direction: WaveDirection
    confidence: float  # نسبة الثقة

@dataclass
class ElliottWaveResult:
    waves: List[Wave]
    current_wave: str
    next_expected: str
    trend: str
    confidence: float
    pivots: List[Dict]
    fibonacci_levels: Dict[str, float]
    analysis_text: str

class ElliottWaveAnalyzer:
    """محلل موجات إليوت"""
    
    def __init__(self):
        # نسب فيبوناتشي لموجات إليوت
        self.fib_ratios = {
            'wave2_retracement': (0.382, 0.618),  # الموجة 2 تصحح 38.2%-61.8% من الموجة 1
            'wave3_extension': (1.618, 2.618),    # الموجة 3 عادة 161.8%-261.8% من الموجة 1
            'wave4_retracement': (0.236, 0.382),  # الموجة 4 تصحح 23.6%-38.2% من الموجة 3
            'wave5_extension': (0.618, 1.0),      # الموجة 5 عادة 61.8%-100% من الموجة 1
            'waveA_retracement': (0.382, 0.618),  # الموجة A
            'waveB_retracement': (0.382, 0.786),  # الموجة B
            'waveC_extension': (0.618, 1.618),    # الموجة C
        }
    
    def find_pivots(self, df: pd.DataFrame, lookback: int = 5) -> Tuple[List[Dict], List[Dict]]:
        """
        تحديد القمم والقيعان (Swing Highs & Lows)
        """
        highs = []
        lows = []
        
        high_col = df['High'].values
        low_col = df['Low'].values
        close_col = df['Close'].values
        
        for i in range(lookback, len(df) - lookback):
            # تحديد القمة
            if high_col[i] == max(high_col[i-lookback:i+lookback+1]):
                highs.append({
                    'index': i,
                    'price': high_col[i],
                    'date': df.index[i] if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'type': 'high'
                })
            
            # تحديد القاع
            if low_col[i] == min(low_col[i-lookback:i+lookback+1]):
                lows.append({
                    'index': i,
                    'price': low_col[i],
                    'date': df.index[i] if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'type': 'low'
                })
        
        return highs, lows
    
    def merge_pivots(self, highs: List[Dict], lows: List[Dict]) -> List[Dict]:
        """
        دمج القمم والقيعان وترتيبها زمنياً
        """
        all_pivots = highs + lows
        all_pivots.sort(key=lambda x: x['index'])
        
        # إزالة النقاط المتتالية من نفس النوع (الاحتفاظ بالأقوى)
        filtered = []
        for pivot in all_pivots:
            if not filtered:
                filtered.append(pivot)
            elif pivot['type'] != filtered[-1]['type']:
                filtered.append(pivot)
            else:
                # نفس النوع - احتفظ بالأقوى
                if pivot['type'] == 'high' and pivot['price'] > filtered[-1]['price']:
                    filtered[-1] = pivot
                elif pivot['type'] == 'low' and pivot['price'] < filtered[-1]['price']:
                    filtered[-1] = pivot
        
        return filtered
    
    def validate_impulse_wave(self, waves: List[Dict]) -> Tuple[bool, float, str]:
        """
        التحقق من صحة الموجة الدافعة (5 موجات)
        قواعد إليوت:
        1. الموجة 2 لا تتجاوز بداية الموجة 1
        2. الموجة 3 ليست الأقصر
        3. الموجة 4 لا تتداخل مع الموجة 1
        """
        if len(waves) < 5:
            return False, 0, "عدد الموجات غير كافٍ"
        
        confidence = 100
        issues = []
        
        # استخراج الموجات
        w1_start, w1_end = waves[0]['price'], waves[1]['price']
        w2_end = waves[2]['price']
        w3_end = waves[3]['price']
        w4_end = waves[4]['price']
        w5_end = waves[5]['price'] if len(waves) > 5 else waves[4]['price']
        
        # حساب أطوال الموجات
        w1_length = abs(w1_end - w1_start)
        w3_length = abs(w3_end - w2_end)
        w5_length = abs(w5_end - w4_end)
        
        # قاعدة 1: الموجة 2 لا تتجاوز بداية الموجة 1
        if (w1_end > w1_start and w2_end < w1_start) or \
           (w1_end < w1_start and w2_end > w1_start):
            confidence -= 40
            issues.append("⚠️ الموجة 2 تجاوزت بداية الموجة 1")
        
        # قاعدة 2: الموجة 3 ليست الأقصر
        if w3_length < w1_length and w3_length < w5_length:
            confidence -= 30
            issues.append("⚠️ الموجة 3 هي الأقصر (مخالفة)")
        
        # قاعدة 3: الموجة 4 لا تتداخل مع الموجة 1
        if (w1_end > w1_start and w4_end < w1_end) or \
           (w1_end < w1_start and w4_end > w1_end):
            confidence -= 20
            issues.append("⚠️ الموجة 4 تتداخل مع الموجة 1")
        
        # التحقق من نسب فيبوناتشي
        if w1_length > 0:
            w2_retracement = abs(w2_end - w1_end) / w1_length
            if 0.382 <= w2_retracement <= 0.618:
                confidence += 5
            
            w3_extension = w3_length / w1_length
            if 1.618 <= w3_extension <= 2.618:
                confidence += 10
        
        confidence = max(0, min(100, confidence))
        
        is_valid = confidence >= 50
        message = "✅ موجة دافعة صحيحة" if is_valid else "❌ موجة دافعة غير مكتملة"
        if issues:
            message += "\n" + "\n".join(issues)
        
        return is_valid, confidence, message
    
    def validate_corrective_wave(self, waves: List[Dict]) -> Tuple[bool, float, str]:
        """
        التحقق من صحة الموجة التصحيحية (A-B-C)
        """
        if len(waves) < 3:
            return False, 0, "عدد الموجات غير كافٍ للتصحيح"
        
        confidence = 80
        
        a_start, a_end = waves[0]['price'], waves[1]['price']
        b_end = waves[2]['price']
        c_end = waves[3]['price'] if len(waves) > 3 else waves[2]['price']
        
        a_length = abs(a_end - a_start)
        c_length = abs(c_end - b_end)
        
        # الموجة B عادة تصحح 38.2%-78.6% من A
        if a_length > 0:
            b_retracement = abs(b_end - a_end) / a_length
            if 0.382 <= b_retracement <= 0.786:
                confidence += 10
        
        # الموجة C عادة تساوي أو تتجاوز A
        if a_length > 0:
            c_ratio = c_length / a_length
            if 0.618 <= c_ratio <= 1.618:
                confidence += 10
        
        confidence = min(100, confidence)
        
        return True, confidence, "✅ موجة تصحيحية (A-B-C)"
    
    def identify_waves(self, pivots: List[Dict], trend: str) -> List[Wave]:
        """
        تحديد وترقيم الموجات
        """
        waves = []
        
        if len(pivots) < 2:
            return waves
        
        # تحديد الاتجاه الرئيسي
        is_uptrend = trend == "صاعد"
        
        wave_labels = ['1', '2', '3', '4', '5', 'A', 'B', 'C']
        current_label_idx = 0
        
        for i in range(len(pivots) - 1):
            start = pivots[i]
            end = pivots[i + 1]
            
            # تحديد اتجاه الموجة
            if end['price'] > start['price']:
                direction = WaveDirection.UP
            else:
                direction = WaveDirection.DOWN
            
            # تحديد نوع الموجة
            if current_label_idx < 5:
                wave_type = WaveType.IMPULSE
                label = wave_labels[current_label_idx]
            else:
                wave_type = WaveType.CORRECTIVE
                label = wave_labels[current_label_idx] if current_label_idx < len(wave_labels) else 'X'
            
            # حساب الثقة
            confidence = 70 + (10 if i < 5 else 0)
            
            wave = Wave(
                number=label,
                start_idx=start['index'],
                end_idx=end['index'],
                start_price=start['price'],
                end_price=end['price'],
                wave_type=wave_type,
                direction=direction,
                confidence=confidence
            )
            waves.append(wave)
            
            current_label_idx += 1
            if current_label_idx >= len(wave_labels):
                current_label_idx = 0  # إعادة الدورة
        
        return waves
    
    def calculate_fibonacci_targets(self, waves: List[Wave]) -> Dict[str, float]:
        """
        حساب مستويات فيبوناتشي المستهدفة
        """
        targets = {}
        
        if len(waves) < 1:
            return targets
        
        # استخدام آخر موجة لحساب الأهداف
        last_wave = waves[-1]
        wave_length = abs(last_wave.end_price - last_wave.start_price)
        
        if last_wave.direction == WaveDirection.UP:
            base = last_wave.end_price
            targets['تصحيح 23.6%'] = base - (wave_length * 0.236)
            targets['تصحيح 38.2%'] = base - (wave_length * 0.382)
            targets['تصحيح 50%'] = base - (wave_length * 0.5)
            targets['تصحيح 61.8%'] = base - (wave_length * 0.618)
            targets['امتداد 161.8%'] = base + (wave_length * 0.618)
        else:
            base = last_wave.end_price
            targets['تصحيح 23.6%'] = base + (wave_length * 0.236)
            targets['تصحيح 38.2%'] = base + (wave_length * 0.382)
            targets['تصحيح 50%'] = base + (wave_length * 0.5)
            targets['تصحيح 61.8%'] = base + (wave_length * 0.618)
            targets['امتداد 161.8%'] = base - (wave_length * 0.618)
        
        return targets
    
    def analyze(self, df: pd.DataFrame, lookback: int = 5) -> ElliottWaveResult:
        """
        التحليل الكامل لموجات إليوت
        """
        # تحديد القمم والقيعان
        highs, lows = self.find_pivots(df, lookback)
        pivots = self.merge_pivots(highs, lows)
        
        if len(pivots) < 3:
            return ElliottWaveResult(
                waves=[],
                current_wave="غير محدد",
                next_expected="غير محدد",
                trend="غير محدد",
                confidence=0,
                pivots=[],
                fibonacci_levels={},
                analysis_text="❌ بيانات غير كافية لتحليل موجات إليوت"
            )
        
        # تحديد الاتجاه العام
        first_price = df['Close'].iloc[0]
        last_price = df['Close'].iloc[-1]
        trend = "صاعد" if last_price > first_price else "هابط"
        
        # تحديد الموجات
        waves = self.identify_waves(pivots, trend)
        
        # التحقق من صحة الموجات
        if len(waves) >= 5:
            is_valid, confidence, validation_msg = self.validate_impulse_wave(pivots)
        elif len(waves) >= 3:
            is_valid, confidence, validation_msg = self.validate_corrective_wave(pivots)
        else:
            is_valid, confidence, validation_msg = False, 50, "موجات قيد التكوين"
        
        # تحديد الموجة الحالية والمتوقعة
        if waves:
            current_wave = waves[-1].number
            wave_sequence = ['1', '2', '3', '4', '5', 'A', 'B', 'C']
            try:
                current_idx = wave_sequence.index(current_wave)
                next_expected = wave_sequence[(current_idx + 1) % len(wave_sequence)]
            except ValueError:
                next_expected = "1"
        else:
            current_wave = "غير محدد"
            next_expected = "1"
        
        # حساب مستويات فيبوناتشي
        fib_levels = self.calculate_fibonacci_targets(waves)
        
        # بناء نص التحليل
        analysis_text = self._build_analysis_text(waves, trend, current_wave, next_expected, confidence, validation_msg, fib_levels)
        
        # تحويل pivots للإخراج
        pivots_output = [{'index': p['index'], 'price': p['price'], 'type': p['type']} for p in pivots]
        
        return ElliottWaveResult(
            waves=waves,
            current_wave=current_wave,
            next_expected=next_expected,
            trend=trend,
            confidence=confidence,
            pivots=pivots_output,
            fibonacci_levels=fib_levels,
            analysis_text=analysis_text
        )
    
    def _build_analysis_text(self, waves: List[Wave], trend: str, current_wave: str, 
                            next_expected: str, confidence: float, validation_msg: str,
                            fib_levels: Dict[str, float]) -> str:
        """
        بناء نص التحليل الكامل
        """
        text = "🌊 **تحليل موجات إليوت**\n\n"
        
        # الاتجاه العام
        trend_emoji = "📈" if trend == "صاعد" else "📉"
        text += f"{trend_emoji} **الاتجاه العام**: {trend}\n"
        text += f"🎯 **الموجة الحالية**: {current_wave}\n"
        text += f"➡️ **الموجة المتوقعة**: {next_expected}\n"
        text += f"📊 **نسبة الثقة**: {confidence:.0f}%\n\n"
        
        # تفاصيل الموجات
        if waves:
            text += "📋 **تفاصيل الموجات:**\n"
            for wave in waves[-5:]:  # آخر 5 موجات
                direction_emoji = "🔼" if wave.direction == WaveDirection.UP else "🔽"
                text += f"  {direction_emoji} موجة {wave.number}: "
                text += f"${wave.start_price:.2f} → ${wave.end_price:.2f}\n"
        
        text += f"\n{validation_msg}\n"
        
        # مستويات فيبوناتشي
        if fib_levels:
            text += "\n📐 **مستويات فيبوناتشي:**\n"
            for level, price in list(fib_levels.items())[:4]:
                text += f"  • {level}: ${price:.2f}\n"
        
        return text
