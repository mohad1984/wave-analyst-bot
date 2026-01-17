"""
Advanced Chart Drawer with Technical Analysis
Includes: Moving Averages, Volume Profile, Targets, Stop Loss
All text in English
"""

import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from datetime import datetime

class ChartDrawer:
    """Advanced chart drawer with technical analysis visualization"""
    
    def __init__(self):
        self.colors = {
            'background': '#1a1a2e',
            'grid': '#2d2d44',
            'text': '#ffffff',
            'bullish': '#00ff88',
            'bearish': '#ff4757',
            'neutral': '#ffa502',
            'ma10': '#ff6b6b',
            'ma20': '#ffd93d',
            'ma50': '#6bcb77',
            'ma200': '#4d96ff',
            'volume_high': '#ff6b6b',
            'volume_low': '#4d96ff',
            'target': '#00ff88',
            'stop_loss': '#ff4757',
            'entry': '#ffffff',
            'support': '#00ff88',
            'resistance': '#ff4757',
            'elliott': '#ffd93d',
            'fib': '#bb86fc',
            'order_block_bull': 'rgba(0, 255, 136, 0.3)',
            'order_block_bear': 'rgba(255, 71, 87, 0.3)',
            'fvg': 'rgba(255, 165, 2, 0.3)',
        }
        
        plt.style.use('dark_background')
    
    def calculate_moving_averages(self, df: pd.DataFrame) -> dict:
        """Calculate moving averages"""
        mas = {}
        close = df['Close'].values
        
        for period in [10, 20, 50, 200]:
            if len(close) >= period:
                ma = pd.Series(close).rolling(window=period).mean().values
                mas[f'MA{period}'] = ma
            else:
                mas[f'MA{period}'] = None
        
        return mas
    
    def calculate_volume_profile(self, df: pd.DataFrame, bins: int = 20) -> dict:
        """Calculate Volume Profile"""
        if len(df) < 10:
            return None
        
        price_min = df['Low'].min()
        price_max = df['High'].max()
        price_range = price_max - price_min
        
        if price_range == 0:
            return None
        
        bin_size = price_range / bins
        volume_profile = []
        
        for i in range(bins):
            bin_low = price_min + (i * bin_size)
            bin_high = bin_low + bin_size
            bin_mid = (bin_low + bin_high) / 2
            
            # Calculate volume in this price range
            mask = ((df['Low'] <= bin_high) & (df['High'] >= bin_low))
            volume = df.loc[mask, 'Volume'].sum()
            
            volume_profile.append({
                'price_low': bin_low,
                'price_high': bin_high,
                'price_mid': bin_mid,
                'volume': volume
            })
        
        # Find POC (Point of Control) - highest volume level
        max_vol = max(vp['volume'] for vp in volume_profile)
        poc = next((vp for vp in volume_profile if vp['volume'] == max_vol), None)
        
        # Find Value Area (70% of volume)
        total_volume = sum(vp['volume'] for vp in volume_profile)
        sorted_vp = sorted(volume_profile, key=lambda x: x['volume'], reverse=True)
        
        cumulative = 0
        value_area = []
        for vp in sorted_vp:
            cumulative += vp['volume']
            value_area.append(vp)
            if cumulative >= total_volume * 0.7:
                break
        
        va_high = max(vp['price_high'] for vp in value_area)
        va_low = min(vp['price_low'] for vp in value_area)
        
        return {
            'profile': volume_profile,
            'poc': poc['price_mid'] if poc else None,
            'va_high': va_high,
            'va_low': va_low,
            'max_volume': max_vol
        }
    
    def get_targets_text(self, df: pd.DataFrame) -> dict:
        """Calculate entry, targets and stop loss"""
        if len(df) < 20:
            return {
                'entry': 0, 'target_1': 0, 'target_2': 0, 'target_3': 0,
                'stop_loss': 0, 'is_bullish': True
            }
        
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        
        current_price = close[-1]
        
        # Calculate ATR for stop loss
        tr = np.maximum(high[1:] - low[1:], 
                       np.abs(high[1:] - close[:-1]),
                       np.abs(low[1:] - close[:-1]))
        atr = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
        
        # Determine trend
        ma20 = np.mean(close[-20:])
        ma50 = np.mean(close[-50:]) if len(close) >= 50 else ma20
        is_bullish = current_price > ma20 and ma20 > ma50
        
        if is_bullish:
            entry = current_price
            stop_loss = current_price - (atr * 1.5)
            target_1 = current_price + (atr * 1.5)
            target_2 = current_price + (atr * 2.5)
            target_3 = current_price + (atr * 4.0)
        else:
            entry = current_price
            stop_loss = current_price + (atr * 1.5)
            target_1 = current_price - (atr * 1.5)
            target_2 = current_price - (atr * 2.5)
            target_3 = current_price - (atr * 4.0)
        
        return {
            'entry': entry,
            'target_1': target_1,
            'target_2': target_2,
            'target_3': target_3,
            'stop_loss': stop_loss,
            'is_bullish': is_bullish,
            'atr': atr
        }
    
    def find_peaks_valleys(self, df: pd.DataFrame, order: int = 5) -> tuple:
        """Find peaks and valleys for Elliott Waves"""
        high = df['High'].values
        low = df['Low'].values
        
        peaks = []
        valleys = []
        
        for i in range(order, len(high) - order):
            if all(high[i] >= high[i-j] for j in range(1, order+1)) and \
               all(high[i] >= high[i+j] for j in range(1, order+1)):
                peaks.append((i, high[i]))
            
            if all(low[i] <= low[i-j] for j in range(1, order+1)) and \
               all(low[i] <= low[i+j] for j in range(1, order+1)):
                valleys.append((i, low[i]))
        
        return peaks, valleys
    
    def draw_candlesticks(self, ax, df: pd.DataFrame):
        """Draw candlestick chart"""
        for i in range(len(df)):
            open_price = df['Open'].iloc[i]
            close_price = df['Close'].iloc[i]
            high_price = df['High'].iloc[i]
            low_price = df['Low'].iloc[i]
            
            color = self.colors['bullish'] if close_price >= open_price else self.colors['bearish']
            
            # Wick
            ax.plot([i, i], [low_price, high_price], color=color, linewidth=0.8)
            
            # Body
            body_bottom = min(open_price, close_price)
            body_height = abs(close_price - open_price)
            
            if body_height == 0:
                body_height = 0.001
            
            rect = Rectangle((i - 0.3, body_bottom), 0.6, body_height,
                            facecolor=color, edgecolor=color, alpha=0.9)
            ax.add_patch(rect)
    
    def draw_moving_averages(self, ax, df: pd.DataFrame, mas: dict):
        """Draw moving averages on chart"""
        x = range(len(df))
        
        ma_colors = {
            'MA10': self.colors['ma10'],
            'MA20': self.colors['ma20'],
            'MA50': self.colors['ma50'],
            'MA200': self.colors['ma200']
        }
        
        for ma_name, ma_values in mas.items():
            if ma_values is not None:
                ax.plot(x, ma_values, color=ma_colors[ma_name], 
                       linewidth=1.2, label=ma_name, alpha=0.8)
    
    def draw_volume_profile(self, ax, df: pd.DataFrame, vp_data: dict):
        """Draw Volume Profile on the right side of chart"""
        if vp_data is None:
            return
        
        profile = vp_data['profile']
        max_vol = vp_data['max_volume']
        
        if max_vol == 0:
            return
        
        chart_width = len(df)
        vp_width = chart_width * 0.15  # Volume profile takes 15% of chart width
        
        for vp in profile:
            # Normalize volume to chart width
            bar_width = (vp['volume'] / max_vol) * vp_width
            
            # Color based on price relative to POC
            if vp['price_mid'] >= vp_data['poc']:
                color = self.colors['volume_high']
            else:
                color = self.colors['volume_low']
            
            # Draw horizontal bar
            rect = Rectangle((chart_width + 1, vp['price_low']), 
                            bar_width, 
                            vp['price_high'] - vp['price_low'],
                            facecolor=color, edgecolor='none', alpha=0.5)
            ax.add_patch(rect)
        
        # Draw POC line
        if vp_data['poc']:
            ax.axhline(y=vp_data['poc'], color='#ffd93d', linestyle='--', 
                      linewidth=1.5, alpha=0.8, label=f"POC: {vp_data['poc']:.2f}")
        
        # Draw Value Area
        ax.axhline(y=vp_data['va_high'], color='#bb86fc', linestyle=':', 
                  linewidth=1, alpha=0.6)
        ax.axhline(y=vp_data['va_low'], color='#bb86fc', linestyle=':', 
                  linewidth=1, alpha=0.6)
    
    def draw_targets_stoploss(self, ax, df: pd.DataFrame, targets: dict):
        """Draw entry, targets and stop loss lines"""
        chart_len = len(df)
        
        # Entry line
        ax.axhline(y=targets['entry'], color=self.colors['entry'], 
                  linestyle='-', linewidth=1.5, alpha=0.9)
        ax.text(chart_len * 0.02, targets['entry'], f"Entry: {targets['entry']:.2f}", 
               color=self.colors['entry'], fontsize=8, va='bottom')
        
        # Target lines
        if targets['is_bullish']:
            for i, (key, label) in enumerate([('target_1', 'TP1'), ('target_2', 'TP2'), ('target_3', 'TP3')]):
                ax.axhline(y=targets[key], color=self.colors['target'], 
                          linestyle='--', linewidth=1, alpha=0.7 - i*0.15)
                ax.text(chart_len * 0.02, targets[key], f"{label}: {targets[key]:.2f}", 
                       color=self.colors['target'], fontsize=8, va='bottom')
        else:
            for i, (key, label) in enumerate([('target_1', 'TP1'), ('target_2', 'TP2'), ('target_3', 'TP3')]):
                ax.axhline(y=targets[key], color=self.colors['target'], 
                          linestyle='--', linewidth=1, alpha=0.7 - i*0.15)
                ax.text(chart_len * 0.02, targets[key], f"{label}: {targets[key]:.2f}", 
                       color=self.colors['target'], fontsize=8, va='top')
        
        # Stop loss line
        ax.axhline(y=targets['stop_loss'], color=self.colors['stop_loss'], 
                  linestyle='-', linewidth=2, alpha=0.9)
        ax.text(chart_len * 0.02, targets['stop_loss'], f"SL: {targets['stop_loss']:.2f}", 
               color=self.colors['stop_loss'], fontsize=8, 
               va='top' if targets['is_bullish'] else 'bottom')
    
    def draw_elliott_waves(self, ax, df: pd.DataFrame, peaks: list, valleys: list):
        """Draw Elliott Wave labels"""
        all_points = [(p[0], p[1], 'peak') for p in peaks] + [(v[0], v[1], 'valley') for v in valleys]
        all_points.sort(key=lambda x: x[0])
        
        if len(all_points) < 5:
            return
        
        # Label last 8 points as waves
        wave_labels = ['1', '2', '3', '4', '5', 'A', 'B', 'C']
        
        for i, point in enumerate(all_points[-8:]):
            idx, price, ptype = point
            label = wave_labels[i] if i < len(wave_labels) else ''
            
            offset = 0.02 * (df['High'].max() - df['Low'].min())
            y_pos = price + offset if ptype == 'peak' else price - offset
            
            ax.annotate(label, xy=(idx, price), xytext=(idx, y_pos),
                       fontsize=10, fontweight='bold', color=self.colors['elliott'],
                       ha='center', va='center',
                       bbox=dict(boxstyle='circle', facecolor=self.colors['background'], 
                                edgecolor=self.colors['elliott'], alpha=0.8))
    
    def draw_support_resistance(self, ax, df: pd.DataFrame):
        """Draw support and resistance levels"""
        high = df['High'].values
        low = df['Low'].values
        
        # Find key levels
        resistance = np.max(high[-20:])
        support = np.min(low[-20:])
        
        ax.axhline(y=resistance, color=self.colors['resistance'], 
                  linestyle='-.', linewidth=1.5, alpha=0.7)
        ax.axhline(y=support, color=self.colors['support'], 
                  linestyle='-.', linewidth=1.5, alpha=0.7)
        
        ax.text(len(df) - 1, resistance, f"R: {resistance:.2f}", 
               color=self.colors['resistance'], fontsize=8, va='bottom', ha='right')
        ax.text(len(df) - 1, support, f"S: {support:.2f}", 
               color=self.colors['support'], fontsize=8, va='top', ha='right')
    
    def draw_fibonacci(self, ax, df: pd.DataFrame):
        """Draw Fibonacci retracement levels"""
        high = df['High'].max()
        low = df['Low'].min()
        diff = high - low
        
        fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
        fib_colors = ['#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff', '#bb86fc', '#ff9ff3', '#00ff88']
        
        for level, color in zip(fib_levels, fib_colors):
            price = high - (diff * level)
            ax.axhline(y=price, color=color, linestyle=':', linewidth=1, alpha=0.6)
            ax.text(len(df) + 2, price, f"{level:.1%}: {price:.2f}", 
                   color=color, fontsize=7, va='center')
    
    def draw_order_blocks(self, ax, df: pd.DataFrame):
        """Draw ICT Order Blocks"""
        if len(df) < 10:
            return
        
        # Find potential order blocks (simplified)
        for i in range(3, len(df) - 1):
            # Bullish OB: bearish candle followed by strong bullish move
            if df['Close'].iloc[i-1] < df['Open'].iloc[i-1]:  # Bearish candle
                if df['Close'].iloc[i] > df['High'].iloc[i-1]:  # Break above
                    rect = Rectangle((i-1, df['Low'].iloc[i-1]), 
                                    2, df['High'].iloc[i-1] - df['Low'].iloc[i-1],
                                    facecolor=self.colors['bullish'], 
                                    edgecolor='none', alpha=0.2)
                    ax.add_patch(rect)
            
            # Bearish OB: bullish candle followed by strong bearish move
            if df['Close'].iloc[i-1] > df['Open'].iloc[i-1]:  # Bullish candle
                if df['Close'].iloc[i] < df['Low'].iloc[i-1]:  # Break below
                    rect = Rectangle((i-1, df['Low'].iloc[i-1]), 
                                    2, df['High'].iloc[i-1] - df['Low'].iloc[i-1],
                                    facecolor=self.colors['bearish'], 
                                    edgecolor='none', alpha=0.2)
                    ax.add_patch(rect)
    
    def draw_fvg(self, ax, df: pd.DataFrame):
        """Draw Fair Value Gaps"""
        if len(df) < 3:
            return
        
        for i in range(2, len(df)):
            # Bullish FVG
            if df['Low'].iloc[i] > df['High'].iloc[i-2]:
                gap_low = df['High'].iloc[i-2]
                gap_high = df['Low'].iloc[i]
                rect = Rectangle((i-1, gap_low), 1, gap_high - gap_low,
                                facecolor=self.colors['bullish'], 
                                edgecolor='none', alpha=0.15)
                ax.add_patch(rect)
            
            # Bearish FVG
            if df['High'].iloc[i] < df['Low'].iloc[i-2]:
                gap_low = df['High'].iloc[i]
                gap_high = df['Low'].iloc[i-2]
                rect = Rectangle((i-1, gap_low), 1, gap_high - gap_low,
                                facecolor=self.colors['bearish'], 
                                edgecolor='none', alpha=0.15)
                ax.add_patch(rect)
    
    def generate_chart(self, df: pd.DataFrame, symbol: str, timeframe: str, 
                      analysis_types: list, show_ma: bool = True, 
                      show_volume_profile: bool = True) -> io.BytesIO:
        """Generate complete chart with all analysis"""
        
        # Create figure with subplots
        fig = plt.figure(figsize=(14, 10), facecolor=self.colors['background'])
        
        # Main chart area
        ax_main = fig.add_axes([0.08, 0.25, 0.75, 0.65])
        ax_main.set_facecolor(self.colors['background'])
        
        # Volume area
        ax_vol = fig.add_axes([0.08, 0.08, 0.75, 0.15])
        ax_vol.set_facecolor(self.colors['background'])
        
        # Draw candlesticks
        self.draw_candlesticks(ax_main, df)
        
        # Calculate and draw moving averages
        if show_ma:
            mas = self.calculate_moving_averages(df)
            self.draw_moving_averages(ax_main, df, mas)
        
        # Calculate and draw volume profile
        if show_volume_profile:
            vp_data = self.calculate_volume_profile(df)
            self.draw_volume_profile(ax_main, df, vp_data)
        
        # Calculate targets
        targets = self.get_targets_text(df)
        
        # Draw analysis based on type
        peaks, valleys = self.find_peaks_valleys(df)
        
        if 'elliott' in analysis_types or 'all' in analysis_types:
            self.draw_elliott_waves(ax_main, df, peaks, valleys)
        
        if 'classic' in analysis_types or 'all' in analysis_types:
            self.draw_support_resistance(ax_main, df)
        
        if 'fibonacci' in analysis_types or 'all' in analysis_types:
            self.draw_fibonacci(ax_main, df)
        
        if 'ict' in analysis_types or 'all' in analysis_types:
            self.draw_order_blocks(ax_main, df)
            self.draw_fvg(ax_main, df)
        
        # Draw targets and stop loss
        self.draw_targets_stoploss(ax_main, df, targets)
        
        # Draw volume bars
        for i in range(len(df)):
            color = self.colors['bullish'] if df['Close'].iloc[i] >= df['Open'].iloc[i] else self.colors['bearish']
            ax_vol.bar(i, df['Volume'].iloc[i], color=color, alpha=0.7, width=0.8)
        
        # Styling
        ax_main.set_xlim(-1, len(df) + len(df) * 0.2)
        ax_main.set_ylim(df['Low'].min() * 0.995, df['High'].max() * 1.005)
        ax_main.grid(True, color=self.colors['grid'], alpha=0.3, linestyle='--')
        ax_main.tick_params(colors=self.colors['text'])
        ax_main.set_ylabel('Price', color=self.colors['text'])
        
        ax_vol.set_xlim(-1, len(df) + len(df) * 0.2)
        ax_vol.grid(True, color=self.colors['grid'], alpha=0.3, linestyle='--')
        ax_vol.tick_params(colors=self.colors['text'])
        ax_vol.set_ylabel('Volume', color=self.colors['text'])
        
        # Title
        direction = "🟢 LONG" if targets['is_bullish'] else "🔴 SHORT"
        title = f"{symbol} | {timeframe} | {direction}"
        ax_main.set_title(title, color=self.colors['text'], fontsize=14, fontweight='bold', pad=10)
        
        # Legend for MAs
        if show_ma:
            ax_main.legend(loc='upper left', fontsize=8, facecolor=self.colors['background'],
                          edgecolor=self.colors['grid'], labelcolor=self.colors['text'])
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        fig.text(0.99, 0.01, f"Generated: {timestamp}", ha='right', va='bottom',
                fontsize=8, color=self.colors['text'], alpha=0.7)
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, facecolor=self.colors['background'],
                   edgecolor='none', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
