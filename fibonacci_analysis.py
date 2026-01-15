"""
Fibonacci Analysis Engine
Separate module for Fibonacci retracement and extension analysis
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum


class FibLevel(Enum):
    """Fibonacci levels"""
    LEVEL_0 = 0.0
    LEVEL_236 = 0.236
    LEVEL_382 = 0.382
    LEVEL_5 = 0.5
    LEVEL_618 = 0.618
    LEVEL_786 = 0.786
    LEVEL_100 = 1.0
    LEVEL_1272 = 1.272
    LEVEL_1618 = 1.618
    LEVEL_2618 = 2.618


@dataclass
class FibonacciResult:
    """Fibonacci analysis result"""
    trend: str  # 'bullish' or 'bearish'
    swing_high: float
    swing_low: float
    current_price: float
    retracement_levels: dict
    extension_levels: dict
    current_zone: str
    key_levels: List[dict]
    recommendation: str
    targets: List[float]
    stop_loss: float


class FibonacciAnalyzer:
    """Fibonacci Retracement and Extension Analyzer"""
    
    def __init__(self):
        self.retracement_ratios = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        self.extension_ratios = [1.0, 1.272, 1.618, 2.0, 2.618, 3.618]
    
    def analyze(self, df: pd.DataFrame) -> FibonacciResult:
        """Perform Fibonacci analysis"""
        
        # Find swing high and low
        swing_high, swing_low, trend = self._find_swing_points(df)
        current_price = df['Close'].iloc[-1]
        
        # Calculate retracement levels
        retracement_levels = self._calculate_retracement(swing_high, swing_low, trend)
        
        # Calculate extension levels
        extension_levels = self._calculate_extension(swing_high, swing_low, trend)
        
        # Determine current zone
        current_zone = self._get_current_zone(current_price, retracement_levels, trend)
        
        # Get key levels
        key_levels = self._get_key_levels(retracement_levels, extension_levels, current_price)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(current_price, retracement_levels, trend)
        
        # Calculate targets and stop loss
        targets, stop_loss = self._calculate_targets_sl(current_price, retracement_levels, 
                                                         extension_levels, trend)
        
        return FibonacciResult(
            trend=trend,
            swing_high=swing_high,
            swing_low=swing_low,
            current_price=current_price,
            retracement_levels=retracement_levels,
            extension_levels=extension_levels,
            current_zone=current_zone,
            key_levels=key_levels,
            recommendation=recommendation,
            targets=targets,
            stop_loss=stop_loss
        )
    
    def _find_swing_points(self, df: pd.DataFrame) -> Tuple[float, float, str]:
        """Find major swing high and low"""
        
        # Use last N candles to find swing points
        lookback = min(len(df), 50)
        recent_df = df.tail(lookback)
        
        swing_high = recent_df['High'].max()
        swing_low = recent_df['Low'].min()
        
        # Determine trend based on price position
        current_price = df['Close'].iloc[-1]
        mid_point = (swing_high + swing_low) / 2
        
        # Also check recent momentum
        sma_10 = df['Close'].rolling(10).mean().iloc[-1]
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        
        if current_price > mid_point and sma_10 > sma_20:
            trend = 'bullish'
        elif current_price < mid_point and sma_10 < sma_20:
            trend = 'bearish'
        else:
            # Use recent price action
            trend = 'bullish' if df['Close'].iloc[-1] > df['Close'].iloc[-5] else 'bearish'
        
        return swing_high, swing_low, trend
    
    def _calculate_retracement(self, high: float, low: float, trend: str) -> dict:
        """Calculate Fibonacci retracement levels"""
        
        diff = high - low
        levels = {}
        
        if trend == 'bullish':
            # Retracement from high to low (pullback in uptrend)
            for ratio in self.retracement_ratios:
                price = high - (diff * ratio)
                levels[f'{ratio}'] = round(price, 4)
        else:
            # Retracement from low to high (pullback in downtrend)
            for ratio in self.retracement_ratios:
                price = low + (diff * ratio)
                levels[f'{ratio}'] = round(price, 4)
        
        return levels
    
    def _calculate_extension(self, high: float, low: float, trend: str) -> dict:
        """Calculate Fibonacci extension levels"""
        
        diff = high - low
        levels = {}
        
        if trend == 'bullish':
            # Extensions above swing high
            for ratio in self.extension_ratios:
                price = low + (diff * ratio)
                levels[f'{ratio}'] = round(price, 4)
        else:
            # Extensions below swing low
            for ratio in self.extension_ratios:
                price = high - (diff * ratio)
                levels[f'{ratio}'] = round(price, 4)
        
        return levels
    
    def _get_current_zone(self, price: float, levels: dict, trend: str) -> str:
        """Determine which Fibonacci zone the price is in"""
        
        sorted_levels = sorted(levels.items(), key=lambda x: float(x[1]))
        
        for i in range(len(sorted_levels) - 1):
            lower_level = float(sorted_levels[i][1])
            upper_level = float(sorted_levels[i + 1][1])
            
            if lower_level <= price <= upper_level:
                lower_name = sorted_levels[i][0]
                upper_name = sorted_levels[i + 1][0]
                return f"Between {lower_name} and {upper_name}"
        
        if price > float(sorted_levels[-1][1]):
            return "Above 100% (Extended)"
        else:
            return "Below 0% (Oversold)"
    
    def _get_key_levels(self, retracement: dict, extension: dict, current_price: float) -> List[dict]:
        """Get key Fibonacci levels near current price"""
        
        all_levels = []
        
        for name, price in retracement.items():
            distance = abs(current_price - price)
            pct_distance = (distance / current_price) * 100
            all_levels.append({
                'level': name,
                'price': price,
                'type': 'Retracement',
                'distance_pct': round(pct_distance, 2)
            })
        
        for name, price in extension.items():
            distance = abs(current_price - price)
            pct_distance = (distance / current_price) * 100
            all_levels.append({
                'level': name,
                'price': price,
                'type': 'Extension',
                'distance_pct': round(pct_distance, 2)
            })
        
        # Sort by distance and return closest 5
        all_levels.sort(key=lambda x: x['distance_pct'])
        return all_levels[:5]
    
    def _generate_recommendation(self, price: float, levels: dict, trend: str) -> str:
        """Generate trading recommendation based on Fibonacci"""
        
        # Check if price is in golden zone (0.618 - 0.382)
        level_382 = float(levels.get('0.382', 0))
        level_618 = float(levels.get('0.618', 0))
        level_5 = float(levels.get('0.5', 0))
        
        if trend == 'bullish':
            if level_618 <= price <= level_382:
                return "STRONG BUY - Price in Golden Zone (0.382-0.618)"
            elif level_5 <= price <= level_382:
                return "BUY - Price near 50% retracement"
            elif price < level_618:
                return "WAIT - Deep retracement, wait for reversal signal"
            else:
                return "HOLD - Price above key retracement levels"
        else:
            if level_382 <= price <= level_618:
                return "STRONG SELL - Price in Golden Zone (0.382-0.618)"
            elif level_382 <= price <= level_5:
                return "SELL - Price near 50% retracement"
            elif price > level_618:
                return "WAIT - Deep retracement, wait for reversal signal"
            else:
                return "HOLD - Price below key retracement levels"
    
    def _calculate_targets_sl(self, price: float, retracement: dict, 
                              extension: dict, trend: str) -> Tuple[List[float], float]:
        """Calculate targets and stop loss based on Fibonacci"""
        
        targets = []
        
        if trend == 'bullish':
            # Targets are extension levels
            targets = [
                float(extension.get('1.272', price * 1.05)),
                float(extension.get('1.618', price * 1.08)),
                float(extension.get('2.618', price * 1.15)),
            ]
            # Stop loss below 0.786 or swing low
            stop_loss = float(retracement.get('0.786', price * 0.95))
        else:
            # Targets are extension levels (lower)
            targets = [
                float(extension.get('1.272', price * 0.95)),
                float(extension.get('1.618', price * 0.92)),
                float(extension.get('2.618', price * 0.85)),
            ]
            # Stop loss above 0.786 or swing high
            stop_loss = float(retracement.get('0.786', price * 1.05))
        
        return targets, stop_loss
    
    def get_analysis_text(self, result: FibonacciResult) -> str:
        """Generate text summary of Fibonacci analysis"""
        
        text = f"📐 **FIBONACCI ANALYSIS**\n\n"
        text += f"**Trend:** {result.trend.upper()}\n"
        text += f"**Current Price:** ${result.current_price:.2f}\n"
        text += f"**Swing High:** ${result.swing_high:.2f}\n"
        text += f"**Swing Low:** ${result.swing_low:.2f}\n\n"
        
        text += f"**Current Zone:** {result.current_zone}\n\n"
        
        text += "**Key Retracement Levels:**\n"
        for level, price in list(result.retracement_levels.items())[:5]:
            text += f"  • {level}: ${price:.2f}\n"
        
        text += f"\n**Recommendation:** {result.recommendation}\n\n"
        
        text += "**Targets:**\n"
        for i, target in enumerate(result.targets, 1):
            text += f"  TP{i}: ${target:.2f}\n"
        
        text += f"\n**Stop Loss:** ${result.stop_loss:.2f}\n"
        
        return text
