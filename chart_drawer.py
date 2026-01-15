"""
Chart Drawing Engine with Targets and Stop Loss
Draws technical analysis on candlestick charts
"""

import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch
from datetime import datetime

class ChartDrawer:
    """Advanced Chart Drawing with Technical Analysis"""
    
    def __init__(self):
        self.colors = {
            'bg': '#1a1a2e',
            'grid': '#2d2d44',
            'text': '#ffffff',
            'bullish': '#00ff88',
            'bearish': '#ff4757',
            'elliott': '#ffd700',
            'support': '#00bcd4',
            'resistance': '#ff5722',
            'fib': '#9c27b0',
            'ob_bull': 'rgba(0, 255, 136, 0.3)',
            'ob_bear': 'rgba(255, 71, 87, 0.3)',
            'fvg': 'rgba(255, 193, 7, 0.3)',
            'target': '#00ff88',
            'stoploss': '#ff4757',
            'harmonic': '#e91e63',
        }
        
        plt.style.use('dark_background')
    
    def generate_chart(self, df: pd.DataFrame, symbol: str, timeframe: str, 
                       analysis_types: list, targets: dict = None) -> io.BytesIO:
        """Generate chart with analysis drawings"""
        
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.colors['bg'])
        ax.set_facecolor(self.colors['bg'])
        
        # Draw candlesticks
        self._draw_candlesticks(ax, df)
        
        # Draw analysis based on type
        if 'elliott' in analysis_types or 'all' in analysis_types:
            self._draw_elliott_waves(ax, df)
        
        if 'classic' in analysis_types or 'all' in analysis_types:
            self._draw_classic_analysis(ax, df)
        
        if 'harmonic' in analysis_types or 'all' in analysis_types:
            self._draw_harmonic_patterns(ax, df)
        
        if 'ict' in analysis_types or 'all' in analysis_types:
            self._draw_ict_analysis(ax, df)
        
        if 'fibonacci' in analysis_types:
            self._draw_fibonacci_only(ax, df)
        
        # Draw targets and stop loss
        if targets:
            self._draw_targets_stoploss(ax, df, targets)
        else:
            # Auto calculate targets and stop loss
            auto_targets = self._calculate_targets_stoploss(df)
            self._draw_targets_stoploss(ax, df, auto_targets)
        
        # Styling
        self._style_chart(ax, symbol, timeframe, analysis_types)
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                    facecolor=self.colors['bg'], edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    def _draw_candlesticks(self, ax, df: pd.DataFrame):
        """Draw candlestick chart"""
        
        for i in range(len(df)):
            open_price = df['Open'].iloc[i]
            close_price = df['Close'].iloc[i]
            high_price = df['High'].iloc[i]
            low_price = df['Low'].iloc[i]
            
            color = self.colors['bullish'] if close_price >= open_price else self.colors['bearish']
            
            # Wick
            ax.plot([i, i], [low_price, high_price], color=color, linewidth=1)
            
            # Body
            body_bottom = min(open_price, close_price)
            body_height = abs(close_price - open_price)
            
            rect = Rectangle((i - 0.3, body_bottom), 0.6, body_height,
                            facecolor=color, edgecolor=color, linewidth=1)
            ax.add_patch(rect)
    
    def _find_swing_points(self, df: pd.DataFrame, window: int = 5) -> tuple:
        """Find swing highs and lows"""
        
        highs = []
        lows = []
        
        for i in range(window, len(df) - window):
            # Swing High
            if df['High'].iloc[i] == df['High'].iloc[i-window:i+window+1].max():
                highs.append((i, df['High'].iloc[i]))
            
            # Swing Low
            if df['Low'].iloc[i] == df['Low'].iloc[i-window:i+window+1].min():
                lows.append((i, df['Low'].iloc[i]))
        
        return highs, lows
    
    def _draw_elliott_waves(self, ax, df: pd.DataFrame):
        """Draw Elliott Wave labels"""
        
        highs, lows = self._find_swing_points(df, window=5)
        
        all_points = [(i, p, 'H') for i, p in highs] + [(i, p, 'L') for i, p in lows]
        all_points.sort(key=lambda x: x[0])
        
        if len(all_points) < 5:
            return
        
        # Label waves
        wave_labels = ['1', '2', '3', '4', '5', 'A', 'B', 'C']
        
        for idx, (i, price, point_type) in enumerate(all_points[:8]):
            label = wave_labels[idx] if idx < len(wave_labels) else ''
            
            offset = 0.02 * (df['High'].max() - df['Low'].min())
            y_pos = price + offset if point_type == 'H' else price - offset
            
            ax.annotate(label, xy=(i, price), xytext=(i, y_pos),
                       fontsize=12, fontweight='bold', color=self.colors['elliott'],
                       ha='center', va='center',
                       bbox=dict(boxstyle='circle,pad=0.3', facecolor=self.colors['bg'],
                                edgecolor=self.colors['elliott'], linewidth=2))
        
        # Connect waves with lines
        if len(all_points) >= 2:
            wave_x = [p[0] for p in all_points[:8]]
            wave_y = [p[1] for p in all_points[:8]]
            ax.plot(wave_x, wave_y, color=self.colors['elliott'], 
                   linewidth=1.5, linestyle='--', alpha=0.7)
    
    def _draw_classic_analysis(self, ax, df: pd.DataFrame):
        """Draw support, resistance, and trend lines"""
        
        highs, lows = self._find_swing_points(df, window=5)
        
        # Support levels
        if lows:
            support_levels = sorted(set([l[1] for l in lows]))[:3]
            for level in support_levels:
                ax.axhline(y=level, color=self.colors['support'], 
                          linestyle='-', linewidth=1.5, alpha=0.7)
                ax.text(len(df) - 1, level, f' S: {level:.2f}', 
                       color=self.colors['support'], fontsize=9, va='center')
        
        # Resistance levels
        if highs:
            resistance_levels = sorted(set([h[1] for h in highs]), reverse=True)[:3]
            for level in resistance_levels:
                ax.axhline(y=level, color=self.colors['resistance'], 
                          linestyle='-', linewidth=1.5, alpha=0.7)
                ax.text(len(df) - 1, level, f' R: {level:.2f}', 
                       color=self.colors['resistance'], fontsize=9, va='center')
        
        # Trend line
        if len(lows) >= 2:
            x_vals = [lows[0][0], lows[-1][0]]
            y_vals = [lows[0][1], lows[-1][1]]
            ax.plot(x_vals, y_vals, color='#ffeb3b', linewidth=2, 
                   linestyle='--', alpha=0.8, label='Trend Line')
    
    def _draw_fibonacci_only(self, ax, df: pd.DataFrame):
        """Draw Fibonacci retracement levels only"""
        
        high = df['High'].max()
        low = df['Low'].min()
        diff = high - low
        
        fib_levels = {
            '0.0': high,
            '0.236': high - 0.236 * diff,
            '0.382': high - 0.382 * diff,
            '0.5': high - 0.5 * diff,
            '0.618': high - 0.618 * diff,
            '0.786': high - 0.786 * diff,
            '1.0': low,
            '1.272': low - 0.272 * diff,
            '1.618': low - 0.618 * diff,
        }
        
        fib_colors = ['#ff0000', '#ff6600', '#ffcc00', '#00ff00', 
                      '#00ffff', '#0066ff', '#6600ff', '#ff00ff', '#ff0099']
        
        for idx, (level, price) in enumerate(fib_levels.items()):
            color = fib_colors[idx % len(fib_colors)]
            ax.axhline(y=price, color=color, linestyle='-', linewidth=1.5, alpha=0.8)
            ax.text(len(df) + 1, price, f' {level} ({price:.2f})', 
                   color=color, fontsize=9, va='center', fontweight='bold')
        
        # Draw Fibonacci zones
        ax.fill_between([0, len(df)], fib_levels['0.382'], fib_levels['0.618'],
                        color='#9c27b0', alpha=0.1, label='Golden Zone')
    
    def _draw_harmonic_patterns(self, ax, df: pd.DataFrame):
        """Draw harmonic pattern if detected"""
        
        highs, lows = self._find_swing_points(df, window=5)
        
        all_points = [(i, p, 'H') for i, p in highs] + [(i, p, 'L') for i, p in lows]
        all_points.sort(key=lambda x: x[0])
        
        if len(all_points) < 5:
            return
        
        # Take last 5 points for XABCD pattern
        pattern_points = all_points[-5:]
        
        labels = ['X', 'A', 'B', 'C', 'D']
        
        for idx, (i, price, _) in enumerate(pattern_points):
            ax.annotate(labels[idx], xy=(i, price),
                       fontsize=11, fontweight='bold', color=self.colors['harmonic'],
                       ha='center', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor=self.colors['bg'],
                                edgecolor=self.colors['harmonic'], linewidth=1.5))
        
        # Connect pattern points
        x_vals = [p[0] for p in pattern_points]
        y_vals = [p[1] for p in pattern_points]
        ax.plot(x_vals, y_vals, color=self.colors['harmonic'], 
               linewidth=2, linestyle='-', alpha=0.8)
        
        # Draw Fibonacci ratios between points
        if len(pattern_points) >= 4:
            xa = abs(pattern_points[1][1] - pattern_points[0][1])
            ab = abs(pattern_points[2][1] - pattern_points[1][1])
            if xa > 0:
                ratio = ab / xa
                mid_x = (pattern_points[1][0] + pattern_points[2][0]) / 2
                mid_y = (pattern_points[1][1] + pattern_points[2][1]) / 2
                ax.text(mid_x, mid_y, f'{ratio:.3f}', color=self.colors['harmonic'],
                       fontsize=8, ha='center')
    
    def _draw_ict_analysis(self, ax, df: pd.DataFrame):
        """Draw ICT concepts: Order Blocks, FVG"""
        
        # Find Order Blocks
        for i in range(2, len(df) - 1):
            # Bullish Order Block
            if (df['Close'].iloc[i-1] < df['Open'].iloc[i-1] and  # Bearish candle
                df['Close'].iloc[i] > df['Open'].iloc[i] and      # Bullish candle
                df['Close'].iloc[i] > df['High'].iloc[i-1]):      # Break above
                
                rect = Rectangle((i-1 - 0.4, df['Low'].iloc[i-1]), 0.8,
                                df['High'].iloc[i-1] - df['Low'].iloc[i-1],
                                facecolor='#00ff88', alpha=0.2, edgecolor='#00ff88',
                                linewidth=1, linestyle='--')
                ax.add_patch(rect)
                ax.text(i-1, df['High'].iloc[i-1], 'OB+', color='#00ff88', 
                       fontsize=8, fontweight='bold')
            
            # Bearish Order Block
            if (df['Close'].iloc[i-1] > df['Open'].iloc[i-1] and  # Bullish candle
                df['Close'].iloc[i] < df['Open'].iloc[i] and      # Bearish candle
                df['Close'].iloc[i] < df['Low'].iloc[i-1]):       # Break below
                
                rect = Rectangle((i-1 - 0.4, df['Low'].iloc[i-1]), 0.8,
                                df['High'].iloc[i-1] - df['Low'].iloc[i-1],
                                facecolor='#ff4757', alpha=0.2, edgecolor='#ff4757',
                                linewidth=1, linestyle='--')
                ax.add_patch(rect)
                ax.text(i-1, df['Low'].iloc[i-1], 'OB-', color='#ff4757', 
                       fontsize=8, fontweight='bold')
        
        # Find Fair Value Gaps
        for i in range(2, len(df)):
            # Bullish FVG
            if df['Low'].iloc[i] > df['High'].iloc[i-2]:
                gap_low = df['High'].iloc[i-2]
                gap_high = df['Low'].iloc[i]
                rect = Rectangle((i-1 - 0.4, gap_low), 0.8, gap_high - gap_low,
                                facecolor='#ffc107', alpha=0.3, edgecolor='#ffc107',
                                linewidth=1)
                ax.add_patch(rect)
                ax.text(i-1, gap_high, 'FVG', color='#ffc107', fontsize=7)
            
            # Bearish FVG
            if df['High'].iloc[i] < df['Low'].iloc[i-2]:
                gap_low = df['High'].iloc[i]
                gap_high = df['Low'].iloc[i-2]
                rect = Rectangle((i-1 - 0.4, gap_low), 0.8, gap_high - gap_low,
                                facecolor='#ffc107', alpha=0.3, edgecolor='#ffc107',
                                linewidth=1)
                ax.add_patch(rect)
                ax.text(i-1, gap_low, 'FVG', color='#ffc107', fontsize=7)
    
    def _calculate_targets_stoploss(self, df: pd.DataFrame) -> dict:
        """Auto calculate targets and stop loss"""
        
        current_price = df['Close'].iloc[-1]
        high = df['High'].max()
        low = df['Low'].min()
        atr = self._calculate_atr(df)
        
        # Determine trend
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        is_bullish = current_price > sma_20
        
        if is_bullish:
            stop_loss = current_price - (2 * atr)
            target_1 = current_price + (1.5 * atr)
            target_2 = current_price + (3 * atr)
            target_3 = current_price + (5 * atr)
        else:
            stop_loss = current_price + (2 * atr)
            target_1 = current_price - (1.5 * atr)
            target_2 = current_price - (3 * atr)
            target_3 = current_price - (5 * atr)
        
        return {
            'entry': current_price,
            'stop_loss': stop_loss,
            'target_1': target_1,
            'target_2': target_2,
            'target_3': target_3,
            'is_bullish': is_bullish
        }
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        
        high = df['High']
        low = df['Low']
        close = df['Close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean().iloc[-1]
        
        return atr if not pd.isna(atr) else (df['High'].max() - df['Low'].min()) * 0.05
    
    def _draw_targets_stoploss(self, ax, df: pd.DataFrame, targets: dict):
        """Draw entry, targets and stop loss on chart"""
        
        entry = targets['entry']
        stop_loss = targets['stop_loss']
        target_1 = targets['target_1']
        target_2 = targets['target_2']
        target_3 = targets['target_3']
        
        # Entry line
        ax.axhline(y=entry, color='#ffffff', linestyle='-', linewidth=2, alpha=0.9)
        ax.text(len(df) + 1, entry, f' ENTRY: {entry:.2f}', 
               color='#ffffff', fontsize=10, va='center', fontweight='bold')
        
        # Stop Loss
        ax.axhline(y=stop_loss, color=self.colors['stoploss'], 
                  linestyle='--', linewidth=2, alpha=0.9)
        ax.text(len(df) + 1, stop_loss, f' SL: {stop_loss:.2f}', 
               color=self.colors['stoploss'], fontsize=10, va='center', fontweight='bold')
        
        # Targets
        ax.axhline(y=target_1, color=self.colors['target'], 
                  linestyle='--', linewidth=1.5, alpha=0.8)
        ax.text(len(df) + 1, target_1, f' TP1: {target_1:.2f}', 
               color=self.colors['target'], fontsize=9, va='center', fontweight='bold')
        
        ax.axhline(y=target_2, color=self.colors['target'], 
                  linestyle='--', linewidth=1.5, alpha=0.7)
        ax.text(len(df) + 1, target_2, f' TP2: {target_2:.2f}', 
               color=self.colors['target'], fontsize=9, va='center', fontweight='bold')
        
        ax.axhline(y=target_3, color=self.colors['target'], 
                  linestyle='--', linewidth=1.5, alpha=0.6)
        ax.text(len(df) + 1, target_3, f' TP3: {target_3:.2f}', 
               color=self.colors['target'], fontsize=9, va='center', fontweight='bold')
        
        # Risk/Reward box
        risk = abs(entry - stop_loss)
        reward = abs(target_2 - entry)
        rr_ratio = reward / risk if risk > 0 else 0
        
        direction = "LONG" if targets.get('is_bullish', True) else "SHORT"
        
        info_text = f"Direction: {direction}\nR:R = 1:{rr_ratio:.1f}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               fontsize=10, color='#ffffff', va='top', ha='left',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=self.colors['bg'],
                        edgecolor='#ffffff', alpha=0.8))
    
    def _style_chart(self, ax, symbol: str, timeframe: str, analysis_types: list):
        """Apply chart styling"""
        
        # Title
        analysis_names = {
            'elliott': 'Elliott Waves',
            'classic': 'Classic',
            'harmonic': 'Harmonic',
            'ict': 'ICT',
            'fibonacci': 'Fibonacci',
            'all': 'Full Analysis'
        }
        
        analysis_str = ' + '.join([analysis_names.get(a, a) for a in analysis_types])
        
        ax.set_title(f'{symbol} | {timeframe} | {analysis_str}', 
                    fontsize=14, fontweight='bold', color=self.colors['text'], pad=15)
        
        # Grid
        ax.grid(True, alpha=0.2, color=self.colors['grid'])
        ax.set_axisbelow(True)
        
        # Labels
        ax.set_xlabel('', fontsize=10, color=self.colors['text'])
        ax.set_ylabel('Price', fontsize=10, color=self.colors['text'])
        
        # Tick colors
        ax.tick_params(colors=self.colors['text'])
        
        # Spine colors
        for spine in ax.spines.values():
            spine.set_color(self.colors['grid'])
        
        # Timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
        ax.text(0.99, 0.01, timestamp, transform=ax.transAxes,
               fontsize=8, color='#888888', ha='right', va='bottom')
    
    def get_targets_text(self, df: pd.DataFrame) -> dict:
        """Get targets and stop loss as text for message"""
        
        return self._calculate_targets_stoploss(df)
