"""
محرك تحليل مدرسة ICT
ICT (Inner Circle Trader) Analysis Engine
Order Blocks, Fair Value Gaps, Liquidity, Market Structure
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class OrderBlockType(Enum):
    BULLISH = "صاعد"
    BEARISH = "هابط"

class LiquidityType(Enum):
    BUY_SIDE = "سيولة شرائية (قمم)"
    SELL_SIDE = "سيولة بيعية (قيعان)"

class MarketStructure(Enum):
    BULLISH = "هيكل صاعد"
    BEARISH = "هيكل هابط"
    RANGING = "هيكل عرضي"

class BreakType(Enum):
    BOS = "كسر هيكل (BOS)"
    CHOCH = "تغير الشخصية (CHoCH)"

@dataclass
class OrderBlock:
    ob_type: OrderBlockType
    high: float
    low: float
    start_idx: int
    end_idx: int
    strength: float  # قوة الأوردر بلوك
    mitigated: bool  # هل تم اختباره
    description: str

@dataclass
class FairValueGap:
    fvg_type: str  # 'bullish' or 'bearish'
    high: float
    low: float
    idx: int
    filled: bool
    fill_percentage: float
    description: str

@dataclass
class LiquidityZone:
    liq_type: LiquidityType
    level: float
    strength: int  # عدد القمم/القيعان
    swept: bool  # هل تم اصطيادها
    idx: int

@dataclass
class StructurePoint:
    point_type: str  # 'HH', 'HL', 'LH', 'LL'
    price: float
    idx: int

@dataclass
class ICTAnalysisResult:
    market_structure: MarketStructure
    structure_points: List[StructurePoint]
    order_blocks: List[OrderBlock]
    fair_value_gaps: List[FairValueGap]
    liquidity_zones: List[LiquidityZone]
    premium_discount: str  # premium, discount, equilibrium
    optimal_trade_entry: Dict
    analysis_text: str

class ICTAnalyzer:
    """محلل مدرسة ICT"""
    
    def __init__(self):
        pass
    
    def identify_swing_points(self, df: pd.DataFrame, lookback: int = 3) -> List[Dict]:
        """
        تحديد نقاط التأرجح (Swing Highs & Lows)
        """
        swings = []
        highs = df['High'].values
        lows = df['Low'].values
        
        for i in range(lookback, len(df) - lookback):
            # Swing High
            if highs[i] == max(highs[i-lookback:i+lookback+1]):
                swings.append({
                    'type': 'high',
                    'price': highs[i],
                    'idx': i
                })
            
            # Swing Low
            if lows[i] == min(lows[i-lookback:i+lookback+1]):
                swings.append({
                    'type': 'low',
                    'price': lows[i],
                    'idx': i
                })
        
        swings.sort(key=lambda x: x['idx'])
        return swings
    
    def analyze_market_structure(self, swings: List[Dict]) -> Tuple[MarketStructure, List[StructurePoint], List[Dict]]:
        """
        تحليل هيكل السوق (Market Structure)
        HH = Higher High, HL = Higher Low
        LH = Lower High, LL = Lower Low
        """
        structure_points = []
        breaks = []
        
        if len(swings) < 4:
            return MarketStructure.RANGING, [], []
        
        # تصنيف النقاط
        highs = [s for s in swings if s['type'] == 'high']
        lows = [s for s in swings if s['type'] == 'low']
        
        # تحليل القمم
        for i in range(1, len(highs)):
            if highs[i]['price'] > highs[i-1]['price']:
                structure_points.append(StructurePoint('HH', highs[i]['price'], highs[i]['idx']))
            else:
                structure_points.append(StructurePoint('LH', highs[i]['price'], highs[i]['idx']))
        
        # تحليل القيعان
        for i in range(1, len(lows)):
            if lows[i]['price'] > lows[i-1]['price']:
                structure_points.append(StructurePoint('HL', lows[i]['price'], lows[i]['idx']))
            else:
                structure_points.append(StructurePoint('LL', lows[i]['price'], lows[i]['idx']))
        
        structure_points.sort(key=lambda x: x.idx)
        
        # تحديد الهيكل العام
        recent_points = structure_points[-6:] if len(structure_points) >= 6 else structure_points
        
        hh_count = sum(1 for p in recent_points if p.point_type == 'HH')
        hl_count = sum(1 for p in recent_points if p.point_type == 'HL')
        lh_count = sum(1 for p in recent_points if p.point_type == 'LH')
        ll_count = sum(1 for p in recent_points if p.point_type == 'LL')
        
        bullish_score = hh_count + hl_count
        bearish_score = lh_count + ll_count
        
        if bullish_score > bearish_score + 1:
            structure = MarketStructure.BULLISH
        elif bearish_score > bullish_score + 1:
            structure = MarketStructure.BEARISH
        else:
            structure = MarketStructure.RANGING
        
        # كشف كسر الهيكل (BOS) وتغير الشخصية (CHoCH)
        for i in range(1, len(structure_points)):
            prev = structure_points[i-1]
            curr = structure_points[i]
            
            # BOS صاعد: كسر قمة سابقة في اتجاه صاعد
            if prev.point_type in ['HH', 'LH'] and curr.point_type == 'HH':
                breaks.append({
                    'type': BreakType.BOS,
                    'direction': 'bullish',
                    'price': curr.price,
                    'idx': curr.idx
                })
            
            # CHoCH: تغير من هابط لصاعد
            if prev.point_type == 'LL' and curr.point_type == 'HL':
                breaks.append({
                    'type': BreakType.CHOCH,
                    'direction': 'bullish',
                    'price': curr.price,
                    'idx': curr.idx
                })
            
            # CHoCH: تغير من صاعد لهابط
            if prev.point_type == 'HH' and curr.point_type == 'LH':
                breaks.append({
                    'type': BreakType.CHOCH,
                    'direction': 'bearish',
                    'price': curr.price,
                    'idx': curr.idx
                })
        
        return structure, structure_points, breaks
    
    def find_order_blocks(self, df: pd.DataFrame, swings: List[Dict]) -> List[OrderBlock]:
        """
        إيجاد Order Blocks
        Bullish OB: آخر شمعة هابطة قبل حركة صعودية قوية
        Bearish OB: آخر شمعة صاعدة قبل حركة هبوطية قوية
        """
        order_blocks = []
        
        opens = df['Open'].values
        closes = df['Close'].values
        highs = df['High'].values
        lows = df['Low'].values
        
        # البحث عن Bullish Order Blocks
        for swing in swings:
            if swing['type'] == 'low':
                idx = swing['idx']
                
                # البحث عن آخر شمعة هابطة قبل القاع
                for i in range(idx - 1, max(0, idx - 5), -1):
                    if closes[i] < opens[i]:  # شمعة هابطة
                        # التحقق من قوة الحركة بعدها
                        if idx + 3 < len(df):
                            move_up = highs[idx:idx+3].max() - lows[idx]
                            candle_range = highs[i] - lows[i]
                            
                            if move_up > candle_range * 2:  # حركة قوية
                                # التحقق من عدم الاختبار
                                mitigated = any(lows[idx+1:] < lows[i]) if idx + 1 < len(df) else False
                                
                                order_blocks.append(OrderBlock(
                                    ob_type=OrderBlockType.BULLISH,
                                    high=highs[i],
                                    low=lows[i],
                                    start_idx=i,
                                    end_idx=idx,
                                    strength=min(move_up / candle_range, 5),
                                    mitigated=mitigated,
                                    description=f"🟢 OB صاعد: ${lows[i]:.2f} - ${highs[i]:.2f}"
                                ))
                        break
        
        # البحث عن Bearish Order Blocks
        for swing in swings:
            if swing['type'] == 'high':
                idx = swing['idx']
                
                for i in range(idx - 1, max(0, idx - 5), -1):
                    if closes[i] > opens[i]:  # شمعة صاعدة
                        if idx + 3 < len(df):
                            move_down = highs[idx] - lows[idx:idx+3].min()
                            candle_range = highs[i] - lows[i]
                            
                            if move_down > candle_range * 2:
                                mitigated = any(highs[idx+1:] > highs[i]) if idx + 1 < len(df) else False
                                
                                order_blocks.append(OrderBlock(
                                    ob_type=OrderBlockType.BEARISH,
                                    high=highs[i],
                                    low=lows[i],
                                    start_idx=i,
                                    end_idx=idx,
                                    strength=min(move_down / candle_range, 5),
                                    mitigated=mitigated,
                                    description=f"🔴 OB هابط: ${lows[i]:.2f} - ${highs[i]:.2f}"
                                ))
                        break
        
        # ترتيب حسب القوة
        order_blocks.sort(key=lambda x: x.strength, reverse=True)
        
        return order_blocks[:10]  # أقوى 10
    
    def find_fair_value_gaps(self, df: pd.DataFrame) -> List[FairValueGap]:
        """
        إيجاد Fair Value Gaps (FVG)
        Bullish FVG: فجوة بين low الشمعة الثالثة و high الشمعة الأولى
        Bearish FVG: فجوة بين high الشمعة الثالثة و low الشمعة الأولى
        """
        fvgs = []
        
        highs = df['High'].values
        lows = df['Low'].values
        
        for i in range(2, len(df)):
            # Bullish FVG
            if lows[i] > highs[i-2]:
                gap_high = lows[i]
                gap_low = highs[i-2]
                
                # التحقق من الملء
                filled = False
                fill_pct = 0
                if i + 1 < len(df):
                    lowest_after = lows[i+1:].min() if len(lows[i+1:]) > 0 else gap_high
                    if lowest_after <= gap_low:
                        filled = True
                        fill_pct = 100
                    elif lowest_after < gap_high:
                        fill_pct = ((gap_high - lowest_after) / (gap_high - gap_low)) * 100
                
                fvgs.append(FairValueGap(
                    fvg_type='bullish',
                    high=gap_high,
                    low=gap_low,
                    idx=i,
                    filled=filled,
                    fill_percentage=fill_pct,
                    description=f"🟢 FVG صاعد: ${gap_low:.2f} - ${gap_high:.2f}"
                ))
            
            # Bearish FVG
            if highs[i] < lows[i-2]:
                gap_high = lows[i-2]
                gap_low = highs[i]
                
                filled = False
                fill_pct = 0
                if i + 1 < len(df):
                    highest_after = highs[i+1:].max() if len(highs[i+1:]) > 0 else gap_low
                    if highest_after >= gap_high:
                        filled = True
                        fill_pct = 100
                    elif highest_after > gap_low:
                        fill_pct = ((highest_after - gap_low) / (gap_high - gap_low)) * 100
                
                fvgs.append(FairValueGap(
                    fvg_type='bearish',
                    high=gap_high,
                    low=gap_low,
                    idx=i,
                    filled=filled,
                    fill_percentage=fill_pct,
                    description=f"🔴 FVG هابط: ${gap_low:.2f} - ${gap_high:.2f}"
                ))
        
        # الاحتفاظ بالفجوات غير المملوءة أولاً
        fvgs.sort(key=lambda x: (x.filled, -x.idx))
        
        return fvgs[:10]
    
    def find_liquidity_zones(self, df: pd.DataFrame, swings: List[Dict]) -> List[LiquidityZone]:
        """
        إيجاد مناطق السيولة (Liquidity)
        Buy-side liquidity: فوق القمم (stop losses للبائعين)
        Sell-side liquidity: تحت القيعان (stop losses للمشترين)
        """
        liquidity_zones = []
        
        current_price = df['Close'].iloc[-1]
        
        # تجميع القمم المتقاربة (Buy-side liquidity)
        highs = [s for s in swings if s['type'] == 'high']
        high_levels = {}
        
        for h in highs:
            level = round(h['price'], 1)
            if level not in high_levels:
                high_levels[level] = {'count': 0, 'idx': h['idx']}
            high_levels[level]['count'] += 1
            high_levels[level]['idx'] = max(high_levels[level]['idx'], h['idx'])
        
        for level, data in high_levels.items():
            if data['count'] >= 2:  # على الأقل قمتين
                swept = current_price > level
                liquidity_zones.append(LiquidityZone(
                    liq_type=LiquidityType.BUY_SIDE,
                    level=level,
                    strength=data['count'],
                    swept=swept,
                    idx=data['idx']
                ))
        
        # تجميع القيعان المتقاربة (Sell-side liquidity)
        lows = [s for s in swings if s['type'] == 'low']
        low_levels = {}
        
        for l in lows:
            level = round(l['price'], 1)
            if level not in low_levels:
                low_levels[level] = {'count': 0, 'idx': l['idx']}
            low_levels[level]['count'] += 1
            low_levels[level]['idx'] = max(low_levels[level]['idx'], l['idx'])
        
        for level, data in low_levels.items():
            if data['count'] >= 2:
                swept = current_price < level
                liquidity_zones.append(LiquidityZone(
                    liq_type=LiquidityType.SELL_SIDE,
                    level=level,
                    strength=data['count'],
                    swept=swept,
                    idx=data['idx']
                ))
        
        # ترتيب حسب القوة
        liquidity_zones.sort(key=lambda x: x.strength, reverse=True)
        
        return liquidity_zones[:10]
    
    def calculate_premium_discount(self, df: pd.DataFrame) -> Tuple[str, Dict]:
        """
        حساب منطقة Premium/Discount
        """
        high = df['High'].max()
        low = df['Low'].min()
        current = df['Close'].iloc[-1]
        
        range_size = high - low
        equilibrium = low + (range_size * 0.5)
        
        premium_zone = low + (range_size * 0.75)  # 75% وأعلى
        discount_zone = low + (range_size * 0.25)  # 25% وأقل
        
        if current >= premium_zone:
            zone = "Premium (منطقة البيع)"
        elif current <= discount_zone:
            zone = "Discount (منطقة الشراء)"
        else:
            zone = "Equilibrium (منطقة التوازن)"
        
        levels = {
            'premium': premium_zone,
            'equilibrium': equilibrium,
            'discount': discount_zone,
            'current': current,
            'high': high,
            'low': low
        }
        
        return zone, levels
    
    def find_optimal_trade_entry(self, df: pd.DataFrame, structure: MarketStructure, 
                                  order_blocks: List[OrderBlock], fvgs: List[FairValueGap]) -> Dict:
        """
        إيجاد نقطة الدخول المثلى (OTE - Optimal Trade Entry)
        """
        current_price = df['Close'].iloc[-1]
        
        ote = {
            'direction': None,
            'entry_zone': None,
            'stop_loss': None,
            'targets': [],
            'confluence': []
        }
        
        if structure == MarketStructure.BULLISH:
            ote['direction'] = 'شراء'
            
            # البحث عن OB صاعد غير مختبر
            bullish_obs = [ob for ob in order_blocks if ob.ob_type == OrderBlockType.BULLISH and not ob.mitigated]
            if bullish_obs:
                best_ob = bullish_obs[0]
                ote['entry_zone'] = (best_ob.low, best_ob.high)
                ote['stop_loss'] = best_ob.low * 0.99
                ote['confluence'].append(f"OB صاعد عند ${best_ob.low:.2f}")
            
            # البحث عن FVG صاعد
            bullish_fvgs = [fvg for fvg in fvgs if fvg.fvg_type == 'bullish' and not fvg.filled]
            if bullish_fvgs:
                ote['confluence'].append(f"FVG صاعد عند ${bullish_fvgs[0].low:.2f}")
            
            # الأهداف
            recent_high = df['High'].tail(20).max()
            ote['targets'] = [
                current_price + (current_price - df['Low'].tail(20).min()) * 0.5,
                recent_high,
                recent_high * 1.02
            ]
            
        elif structure == MarketStructure.BEARISH:
            ote['direction'] = 'بيع'
            
            bearish_obs = [ob for ob in order_blocks if ob.ob_type == OrderBlockType.BEARISH and not ob.mitigated]
            if bearish_obs:
                best_ob = bearish_obs[0]
                ote['entry_zone'] = (best_ob.low, best_ob.high)
                ote['stop_loss'] = best_ob.high * 1.01
                ote['confluence'].append(f"OB هابط عند ${best_ob.high:.2f}")
            
            bearish_fvgs = [fvg for fvg in fvgs if fvg.fvg_type == 'bearish' and not fvg.filled]
            if bearish_fvgs:
                ote['confluence'].append(f"FVG هابط عند ${bearish_fvgs[0].high:.2f}")
            
            recent_low = df['Low'].tail(20).min()
            ote['targets'] = [
                current_price - (df['High'].tail(20).max() - current_price) * 0.5,
                recent_low,
                recent_low * 0.98
            ]
        
        return ote
    
    def analyze(self, df: pd.DataFrame) -> ICTAnalysisResult:
        """
        التحليل الكامل بمدرسة ICT
        """
        # نقاط التأرجح
        swings = self.identify_swing_points(df)
        
        # هيكل السوق
        structure, structure_points, breaks = self.analyze_market_structure(swings)
        
        # Order Blocks
        order_blocks = self.find_order_blocks(df, swings)
        
        # Fair Value Gaps
        fvgs = self.find_fair_value_gaps(df)
        
        # Liquidity Zones
        liquidity = self.find_liquidity_zones(df, swings)
        
        # Premium/Discount
        pd_zone, pd_levels = self.calculate_premium_discount(df)
        
        # Optimal Trade Entry
        ote = self.find_optimal_trade_entry(df, structure, order_blocks, fvgs)
        
        # بناء نص التحليل
        analysis_text = self._build_analysis_text(
            structure, structure_points, breaks, order_blocks, 
            fvgs, liquidity, pd_zone, pd_levels, ote, df['Close'].iloc[-1]
        )
        
        return ICTAnalysisResult(
            market_structure=structure,
            structure_points=structure_points,
            order_blocks=order_blocks,
            fair_value_gaps=fvgs,
            liquidity_zones=liquidity,
            premium_discount=pd_zone,
            optimal_trade_entry=ote,
            analysis_text=analysis_text
        )
    
    def _build_analysis_text(self, structure, structure_points, breaks, order_blocks, 
                            fvgs, liquidity, pd_zone, pd_levels, ote, current_price) -> str:
        """
        بناء نص تحليل ICT
        """
        text = "🎯 **تحليل ICT**\n\n"
        
        # هيكل السوق
        structure_emoji = "📈" if structure == MarketStructure.BULLISH else "📉" if structure == MarketStructure.BEARISH else "➡️"
        text += f"{structure_emoji} **هيكل السوق**: {structure.value}\n"
        
        # آخر نقاط الهيكل
        if structure_points:
            recent = structure_points[-3:]
            text += "📊 **آخر نقاط الهيكل**: "
            text += " → ".join([f"{p.point_type}(${p.price:.2f})" for p in recent])
            text += "\n"
        
        # كسر الهيكل
        if breaks:
            last_break = breaks[-1]
            text += f"⚡ **آخر كسر**: {last_break['type'].value} ({last_break['direction']})\n"
        
        text += "\n"
        
        # Premium/Discount
        text += f"📍 **المنطقة الحالية**: {pd_zone}\n"
        text += f"  • Premium: ${pd_levels['premium']:.2f}\n"
        text += f"  • Equilibrium: ${pd_levels['equilibrium']:.2f}\n"
        text += f"  • Discount: ${pd_levels['discount']:.2f}\n\n"
        
        # Order Blocks
        text += "🧱 **Order Blocks:**\n"
        active_obs = [ob for ob in order_blocks if not ob.mitigated][:3]
        if active_obs:
            for ob in active_obs:
                emoji = "🟢" if ob.ob_type == OrderBlockType.BULLISH else "🔴"
                text += f"  {emoji} {ob.ob_type.value}: ${ob.low:.2f} - ${ob.high:.2f}\n"
        else:
            text += "  لا توجد OBs نشطة\n"
        
        # Fair Value Gaps
        text += "\n📊 **Fair Value Gaps:**\n"
        active_fvgs = [fvg for fvg in fvgs if not fvg.filled][:3]
        if active_fvgs:
            for fvg in active_fvgs:
                emoji = "🟢" if fvg.fvg_type == 'bullish' else "🔴"
                text += f"  {emoji} {fvg.fvg_type}: ${fvg.low:.2f} - ${fvg.high:.2f}\n"
        else:
            text += "  لا توجد FVGs مفتوحة\n"
        
        # Liquidity
        text += "\n💧 **مناطق السيولة:**\n"
        unswept = [liq for liq in liquidity if not liq.swept][:4]
        for liq in unswept:
            emoji = "🔺" if liq.liq_type == LiquidityType.BUY_SIDE else "🔻"
            text += f"  {emoji} {liq.liq_type.value}: ${liq.level:.2f}\n"
        
        # التوصية
        if ote['direction']:
            text += f"\n💡 **التوصية**: {ote['direction']}\n"
            if ote['entry_zone']:
                text += f"  • منطقة الدخول: ${ote['entry_zone'][0]:.2f} - ${ote['entry_zone'][1]:.2f}\n"
            if ote['stop_loss']:
                text += f"  • وقف الخسارة: ${ote['stop_loss']:.2f}\n"
            if ote['targets']:
                text += f"  • الهدف 1: ${ote['targets'][0]:.2f}\n"
            if ote['confluence']:
                text += f"  • التقاء: {', '.join(ote['confluence'])}\n"
        
        return text
