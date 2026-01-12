"""
محرك التحليل التوافقي
Harmonic Patterns Analysis Engine
Gartley, Butterfly, Bat, Crab, Shark, Cypher
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class HarmonicType(Enum):
    GARTLEY = "جارتلي"
    BUTTERFLY = "الفراشة"
    BAT = "الخفاش"
    CRAB = "السلطعون"
    SHARK = "القرش"
    CYPHER = "سايفر"
    ABCD = "ABCD"
    THREE_DRIVES = "ثلاث دفعات"

class PatternDirection(Enum):
    BULLISH = "صاعد"
    BEARISH = "هابط"

@dataclass
class HarmonicPattern:
    pattern_type: HarmonicType
    direction: PatternDirection
    points: Dict[str, Tuple[int, float]]  # X, A, B, C, D points
    ratios: Dict[str, float]  # Fibonacci ratios
    confidence: float
    prz_low: float  # Potential Reversal Zone
    prz_high: float
    target_1: float
    target_2: float
    stop_loss: float
    description: str

@dataclass
class HarmonicAnalysisResult:
    patterns: List[HarmonicPattern]
    potential_patterns: List[Dict]  # أنماط قيد التكوين
    fibonacci_levels: Dict[str, float]
    analysis_text: str

class HarmonicAnalyzer:
    """محلل الأنماط التوافقية"""
    
    def __init__(self):
        # نسب فيبوناتشي لكل نموذج
        self.pattern_ratios = {
            HarmonicType.GARTLEY: {
                'XAB': (0.618, 0.618),      # B = 61.8% of XA
                'ABC': (0.382, 0.886),      # C = 38.2%-88.6% of AB
                'BCD': (1.27, 1.618),       # D = 127%-161.8% of BC
                'XAD': (0.786, 0.786),      # D = 78.6% of XA
            },
            HarmonicType.BUTTERFLY: {
                'XAB': (0.786, 0.786),
                'ABC': (0.382, 0.886),
                'BCD': (1.618, 2.618),
                'XAD': (1.27, 1.618),
            },
            HarmonicType.BAT: {
                'XAB': (0.382, 0.50),
                'ABC': (0.382, 0.886),
                'BCD': (1.618, 2.618),
                'XAD': (0.886, 0.886),
            },
            HarmonicType.CRAB: {
                'XAB': (0.382, 0.618),
                'ABC': (0.382, 0.886),
                'BCD': (2.24, 3.618),
                'XAD': (1.618, 1.618),
            },
            HarmonicType.SHARK: {
                'XAB': (0.446, 0.618),
                'ABC': (1.13, 1.618),
                'BCD': (1.618, 2.24),
                'XAD': (0.886, 1.13),
            },
            HarmonicType.CYPHER: {
                'XAB': (0.382, 0.618),
                'ABC': (1.13, 1.414),
                'BCD': (1.272, 2.0),
                'XAD': (0.786, 0.786),
            },
        }
        
        self.tolerance = 0.05  # 5% tolerance
    
    def find_swing_points(self, df: pd.DataFrame, lookback: int = 5) -> List[Tuple[int, float, str]]:
        """
        إيجاد نقاط التأرجح (القمم والقيعان)
        """
        points = []
        highs = df['High'].values
        lows = df['Low'].values
        
        for i in range(lookback, len(df) - lookback):
            # قمة
            if highs[i] == max(highs[i-lookback:i+lookback+1]):
                points.append((i, highs[i], 'high'))
            # قاع
            if lows[i] == min(lows[i-lookback:i+lookback+1]):
                points.append((i, lows[i], 'low'))
        
        # ترتيب وتنظيف
        points.sort(key=lambda x: x[0])
        
        # إزالة النقاط المتتالية من نفس النوع
        cleaned = []
        for point in points:
            if not cleaned or point[2] != cleaned[-1][2]:
                cleaned.append(point)
            else:
                # الاحتفاظ بالأقوى
                if point[2] == 'high' and point[1] > cleaned[-1][1]:
                    cleaned[-1] = point
                elif point[2] == 'low' and point[1] < cleaned[-1][1]:
                    cleaned[-1] = point
        
        return cleaned
    
    def calculate_ratio(self, p1: float, p2: float, p3: float) -> float:
        """
        حساب نسبة فيبوناتشي
        """
        if abs(p2 - p1) < 0.0001:
            return 0
        return abs(p3 - p2) / abs(p2 - p1)
    
    def check_ratio_match(self, actual: float, expected: Tuple[float, float]) -> bool:
        """
        التحقق من تطابق النسبة
        """
        min_val, max_val = expected
        return (min_val - self.tolerance) <= actual <= (max_val + self.tolerance)
    
    def detect_abcd(self, points: List[Tuple[int, float, str]]) -> List[HarmonicPattern]:
        """
        كشف نموذج ABCD
        """
        patterns = []
        
        if len(points) < 4:
            return patterns
        
        for i in range(len(points) - 3):
            A = points[i]
            B = points[i + 1]
            C = points[i + 2]
            D = points[i + 3]
            
            # التحقق من التناوب
            if A[2] == B[2] or B[2] == C[2] or C[2] == D[2]:
                continue
            
            # حساب النسب
            AB = abs(B[1] - A[1])
            BC = abs(C[1] - B[1])
            CD = abs(D[1] - C[1])
            
            if AB == 0:
                continue
            
            BC_ratio = BC / AB
            CD_ratio = CD / BC if BC > 0 else 0
            
            # التحقق من نسب ABCD
            # BC = 61.8%-78.6% of AB
            # CD = 127%-161.8% of BC
            if 0.55 <= BC_ratio <= 0.85 and 1.2 <= CD_ratio <= 1.7:
                direction = PatternDirection.BULLISH if D[2] == 'low' else PatternDirection.BEARISH
                
                # حساب الأهداف
                if direction == PatternDirection.BULLISH:
                    target_1 = D[1] + (AB * 0.618)
                    target_2 = D[1] + AB
                    stop_loss = D[1] - (AB * 0.236)
                else:
                    target_1 = D[1] - (AB * 0.618)
                    target_2 = D[1] - AB
                    stop_loss = D[1] + (AB * 0.236)
                
                confidence = 70 + (10 if 0.6 <= BC_ratio <= 0.8 else 0) + (10 if 1.27 <= CD_ratio <= 1.618 else 0)
                
                patterns.append(HarmonicPattern(
                    pattern_type=HarmonicType.ABCD,
                    direction=direction,
                    points={'A': (A[0], A[1]), 'B': (B[0], B[1]), 'C': (C[0], C[1]), 'D': (D[0], D[1])},
                    ratios={'BC/AB': BC_ratio, 'CD/BC': CD_ratio},
                    confidence=min(confidence, 95),
                    prz_low=D[1] * 0.99,
                    prz_high=D[1] * 1.01,
                    target_1=target_1,
                    target_2=target_2,
                    stop_loss=stop_loss,
                    description=f"📐 ABCD {direction.value} - BC={BC_ratio:.3f} CD={CD_ratio:.3f}"
                ))
        
        return patterns
    
    def detect_gartley(self, points: List[Tuple[int, float, str]]) -> List[HarmonicPattern]:
        """
        كشف نموذج جارتلي
        """
        patterns = []
        
        if len(points) < 5:
            return patterns
        
        for i in range(len(points) - 4):
            X = points[i]
            A = points[i + 1]
            B = points[i + 2]
            C = points[i + 3]
            D = points[i + 4]
            
            # التحقق من التناوب
            types = [X[2], A[2], B[2], C[2], D[2]]
            if any(types[j] == types[j+1] for j in range(4)):
                continue
            
            # حساب النسب
            XA = abs(A[1] - X[1])
            AB = abs(B[1] - A[1])
            BC = abs(C[1] - B[1])
            CD = abs(D[1] - C[1])
            XD = abs(D[1] - X[1])
            
            if XA == 0 or AB == 0 or BC == 0:
                continue
            
            XAB = AB / XA  # B retracement of XA
            ABC = BC / AB  # C retracement of AB
            BCD = CD / BC  # D extension of BC
            XAD = XD / XA  # D retracement of XA
            
            # التحقق من نسب جارتلي
            ratios = self.pattern_ratios[HarmonicType.GARTLEY]
            
            if (self.check_ratio_match(XAB, ratios['XAB']) and
                self.check_ratio_match(ABC, ratios['ABC']) and
                self.check_ratio_match(XAD, ratios['XAD'])):
                
                direction = PatternDirection.BULLISH if D[2] == 'low' else PatternDirection.BEARISH
                
                # منطقة الانعكاس المحتملة
                prz_center = X[1] + (A[1] - X[1]) * 0.786 if direction == PatternDirection.BULLISH else X[1] - (X[1] - A[1]) * 0.786
                
                # الأهداف
                if direction == PatternDirection.BULLISH:
                    target_1 = D[1] + (XA * 0.382)
                    target_2 = D[1] + (XA * 0.618)
                    stop_loss = D[1] - (XA * 0.118)
                else:
                    target_1 = D[1] - (XA * 0.382)
                    target_2 = D[1] - (XA * 0.618)
                    stop_loss = D[1] + (XA * 0.118)
                
                confidence = 75 + (5 if abs(XAB - 0.618) < 0.02 else 0) + (10 if abs(XAD - 0.786) < 0.02 else 0)
                
                patterns.append(HarmonicPattern(
                    pattern_type=HarmonicType.GARTLEY,
                    direction=direction,
                    points={'X': (X[0], X[1]), 'A': (A[0], A[1]), 'B': (B[0], B[1]), 'C': (C[0], C[1]), 'D': (D[0], D[1])},
                    ratios={'XAB': XAB, 'ABC': ABC, 'BCD': BCD, 'XAD': XAD},
                    confidence=min(confidence, 95),
                    prz_low=prz_center * 0.99,
                    prz_high=prz_center * 1.01,
                    target_1=target_1,
                    target_2=target_2,
                    stop_loss=stop_loss,
                    description=f"🦋 جارتلي {direction.value} - XAD={XAD:.3f}"
                ))
        
        return patterns
    
    def detect_butterfly(self, points: List[Tuple[int, float, str]]) -> List[HarmonicPattern]:
        """
        كشف نموذج الفراشة
        """
        patterns = []
        
        if len(points) < 5:
            return patterns
        
        for i in range(len(points) - 4):
            X, A, B, C, D = points[i:i+5]
            
            types = [X[2], A[2], B[2], C[2], D[2]]
            if any(types[j] == types[j+1] for j in range(4)):
                continue
            
            XA = abs(A[1] - X[1])
            AB = abs(B[1] - A[1])
            BC = abs(C[1] - B[1])
            CD = abs(D[1] - C[1])
            XD = abs(D[1] - X[1])
            
            if XA == 0 or AB == 0 or BC == 0:
                continue
            
            XAB = AB / XA
            ABC = BC / AB
            XAD = XD / XA
            
            ratios = self.pattern_ratios[HarmonicType.BUTTERFLY]
            
            if (self.check_ratio_match(XAB, ratios['XAB']) and
                self.check_ratio_match(ABC, ratios['ABC']) and
                self.check_ratio_match(XAD, ratios['XAD'])):
                
                direction = PatternDirection.BULLISH if D[2] == 'low' else PatternDirection.BEARISH
                
                if direction == PatternDirection.BULLISH:
                    target_1 = D[1] + (XA * 0.382)
                    target_2 = D[1] + (XA * 0.618)
                    stop_loss = D[1] - (XA * 0.118)
                else:
                    target_1 = D[1] - (XA * 0.382)
                    target_2 = D[1] - (XA * 0.618)
                    stop_loss = D[1] + (XA * 0.118)
                
                confidence = 75
                
                patterns.append(HarmonicPattern(
                    pattern_type=HarmonicType.BUTTERFLY,
                    direction=direction,
                    points={'X': (X[0], X[1]), 'A': (A[0], A[1]), 'B': (B[0], B[1]), 'C': (C[0], C[1]), 'D': (D[0], D[1])},
                    ratios={'XAB': XAB, 'ABC': ABC, 'XAD': XAD},
                    confidence=confidence,
                    prz_low=D[1] * 0.99,
                    prz_high=D[1] * 1.01,
                    target_1=target_1,
                    target_2=target_2,
                    stop_loss=stop_loss,
                    description=f"🦋 الفراشة {direction.value} - XAD={XAD:.3f}"
                ))
        
        return patterns
    
    def detect_bat(self, points: List[Tuple[int, float, str]]) -> List[HarmonicPattern]:
        """
        كشف نموذج الخفاش
        """
        patterns = []
        
        if len(points) < 5:
            return patterns
        
        for i in range(len(points) - 4):
            X, A, B, C, D = points[i:i+5]
            
            types = [X[2], A[2], B[2], C[2], D[2]]
            if any(types[j] == types[j+1] for j in range(4)):
                continue
            
            XA = abs(A[1] - X[1])
            AB = abs(B[1] - A[1])
            BC = abs(C[1] - B[1])
            XD = abs(D[1] - X[1])
            
            if XA == 0 or AB == 0 or BC == 0:
                continue
            
            XAB = AB / XA
            ABC = BC / AB
            XAD = XD / XA
            
            ratios = self.pattern_ratios[HarmonicType.BAT]
            
            if (self.check_ratio_match(XAB, ratios['XAB']) and
                self.check_ratio_match(ABC, ratios['ABC']) and
                self.check_ratio_match(XAD, ratios['XAD'])):
                
                direction = PatternDirection.BULLISH if D[2] == 'low' else PatternDirection.BEARISH
                
                if direction == PatternDirection.BULLISH:
                    target_1 = D[1] + (XA * 0.382)
                    target_2 = D[1] + (XA * 0.618)
                    stop_loss = D[1] - (XA * 0.118)
                else:
                    target_1 = D[1] - (XA * 0.382)
                    target_2 = D[1] - (XA * 0.618)
                    stop_loss = D[1] + (XA * 0.118)
                
                patterns.append(HarmonicPattern(
                    pattern_type=HarmonicType.BAT,
                    direction=direction,
                    points={'X': (X[0], X[1]), 'A': (A[0], A[1]), 'B': (B[0], B[1]), 'C': (C[0], C[1]), 'D': (D[0], D[1])},
                    ratios={'XAB': XAB, 'ABC': ABC, 'XAD': XAD},
                    confidence=75,
                    prz_low=D[1] * 0.99,
                    prz_high=D[1] * 1.01,
                    target_1=target_1,
                    target_2=target_2,
                    stop_loss=stop_loss,
                    description=f"🦇 الخفاش {direction.value} - XAD={XAD:.3f}"
                ))
        
        return patterns
    
    def detect_crab(self, points: List[Tuple[int, float, str]]) -> List[HarmonicPattern]:
        """
        كشف نموذج السلطعون
        """
        patterns = []
        
        if len(points) < 5:
            return patterns
        
        for i in range(len(points) - 4):
            X, A, B, C, D = points[i:i+5]
            
            types = [X[2], A[2], B[2], C[2], D[2]]
            if any(types[j] == types[j+1] for j in range(4)):
                continue
            
            XA = abs(A[1] - X[1])
            AB = abs(B[1] - A[1])
            BC = abs(C[1] - B[1])
            XD = abs(D[1] - X[1])
            
            if XA == 0 or AB == 0 or BC == 0:
                continue
            
            XAB = AB / XA
            ABC = BC / AB
            XAD = XD / XA
            
            ratios = self.pattern_ratios[HarmonicType.CRAB]
            
            if (self.check_ratio_match(XAB, ratios['XAB']) and
                self.check_ratio_match(ABC, ratios['ABC']) and
                self.check_ratio_match(XAD, ratios['XAD'])):
                
                direction = PatternDirection.BULLISH if D[2] == 'low' else PatternDirection.BEARISH
                
                if direction == PatternDirection.BULLISH:
                    target_1 = D[1] + (XA * 0.382)
                    target_2 = D[1] + (XA * 0.618)
                    stop_loss = D[1] - (XA * 0.118)
                else:
                    target_1 = D[1] - (XA * 0.382)
                    target_2 = D[1] - (XA * 0.618)
                    stop_loss = D[1] + (XA * 0.118)
                
                patterns.append(HarmonicPattern(
                    pattern_type=HarmonicType.CRAB,
                    direction=direction,
                    points={'X': (X[0], X[1]), 'A': (A[0], A[1]), 'B': (B[0], B[1]), 'C': (C[0], C[1]), 'D': (D[0], D[1])},
                    ratios={'XAB': XAB, 'ABC': ABC, 'XAD': XAD},
                    confidence=75,
                    prz_low=D[1] * 0.99,
                    prz_high=D[1] * 1.01,
                    target_1=target_1,
                    target_2=target_2,
                    stop_loss=stop_loss,
                    description=f"🦀 السلطعون {direction.value} - XAD={XAD:.3f}"
                ))
        
        return patterns
    
    def calculate_fibonacci_retracements(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        حساب مستويات فيبوناتشي
        """
        high = df['High'].max()
        low = df['Low'].min()
        diff = high - low
        
        levels = {
            '0%': high,
            '23.6%': high - (diff * 0.236),
            '38.2%': high - (diff * 0.382),
            '50%': high - (diff * 0.5),
            '61.8%': high - (diff * 0.618),
            '78.6%': high - (diff * 0.786),
            '100%': low,
            '127.2%': low - (diff * 0.272),
            '161.8%': low - (diff * 0.618),
        }
        
        return levels
    
    def analyze(self, df: pd.DataFrame) -> HarmonicAnalysisResult:
        """
        التحليل التوافقي الكامل
        """
        # إيجاد نقاط التأرجح
        points = self.find_swing_points(df)
        
        # كشف الأنماط
        all_patterns = []
        all_patterns.extend(self.detect_abcd(points))
        all_patterns.extend(self.detect_gartley(points))
        all_patterns.extend(self.detect_butterfly(points))
        all_patterns.extend(self.detect_bat(points))
        all_patterns.extend(self.detect_crab(points))
        
        # ترتيب حسب الثقة
        all_patterns.sort(key=lambda x: x.confidence, reverse=True)
        
        # مستويات فيبوناتشي
        fib_levels = self.calculate_fibonacci_retracements(df)
        
        # بناء نص التحليل
        analysis_text = self._build_analysis_text(all_patterns, fib_levels, df['Close'].iloc[-1])
        
        return HarmonicAnalysisResult(
            patterns=all_patterns[:5],  # أفضل 5 أنماط
            potential_patterns=[],
            fibonacci_levels=fib_levels,
            analysis_text=analysis_text
        )
    
    def _build_analysis_text(self, patterns: List[HarmonicPattern], fib_levels: Dict, current_price: float) -> str:
        """
        بناء نص التحليل التوافقي
        """
        text = "🔷 **التحليل التوافقي**\n\n"
        
        if patterns:
            text += "📐 **الأنماط المكتشفة:**\n"
            for p in patterns[:3]:
                direction_emoji = "🟢" if p.direction == PatternDirection.BULLISH else "🔴"
                text += f"\n{direction_emoji} **{p.pattern_type.value}** ({p.direction.value})\n"
                text += f"  • الثقة: {p.confidence:.0f}%\n"
                text += f"  • منطقة الانعكاس: ${p.prz_low:.2f} - ${p.prz_high:.2f}\n"
                text += f"  • الهدف 1: ${p.target_1:.2f}\n"
                text += f"  • الهدف 2: ${p.target_2:.2f}\n"
                text += f"  • وقف الخسارة: ${p.stop_loss:.2f}\n"
        else:
            text += "❌ لا توجد أنماط توافقية مكتملة حالياً\n"
        
        # مستويات فيبوناتشي
        text += "\n📐 **مستويات فيبوناتشي:**\n"
        for level, price in list(fib_levels.items())[:6]:
            marker = "👈" if abs(price - current_price) / current_price < 0.02 else ""
            text += f"  • {level}: ${price:.2f} {marker}\n"
        
        return text
