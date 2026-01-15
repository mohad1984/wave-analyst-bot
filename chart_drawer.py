"""
محرك رسم الشارتات مع التحليل الفني
Chart Drawing Engine with Technical Analysis Overlay
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io
import os

# إعدادات الرسم
plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = '#1a1a2e'
plt.rcParams['axes.facecolor'] = '#16213e'
plt.rcParams['axes.edgecolor'] = '#e94560'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'
plt.rcParams['grid.color'] = '#0f3460'
plt.rcParams['text.color'] = 'white'
plt.rcParams['font.size'] = 10


class ChartDrawer:
    """محرك رسم الشارتات"""
    
    def __init__(self):
        self.colors = {
            'bullish': '#00ff88',
            'bearish': '#ff4757',
            'neutral': '#ffa502',
            'support': '#00ff88',
            'resistance': '#ff4757',
            'wave_impulse': '#00d2ff',
            'wave_corrective': '#ffd700',
            'order_block_bull': 'rgba(0, 255, 136, 0.3)',
            'order_block_bear': 'rgba(255, 71, 87, 0.3)',
            'fvg': 'rgba(255, 165, 0, 0.3)',
            'fibonacci': '#9b59b6',
            'trendline': '#3498db',
            'harmonic': '#e74c3c',
        }
    
    def draw_candlesticks(self, ax, df):
        """رسم الشموع اليابانية"""
        for i in range(len(df)):
            row = df.iloc[i]
            color = self.colors['bullish'] if row['Close'] >= row['Open'] else self.colors['bearish']
            
            # جسم الشمعة
            body_bottom = min(row['Open'], row['Close'])
            body_height = abs(row['Close'] - row['Open'])
            
            rect = Rectangle(
                (i - 0.3, body_bottom),
                0.6, body_height,
                facecolor=color,
                edgecolor=color,
                linewidth=1
            )
            ax.add_patch(rect)
            
            # الفتيل العلوي والسفلي
            ax.plot([i, i], [row['Low'], body_bottom], color=color, linewidth=1)
            ax.plot([i, i], [body_bottom + body_height, row['High']], color=color, linewidth=1)
    
    def find_swing_points(self, df, window=5):
        """تحديد القمم والقيعان"""
        highs = df['High'].values
        lows = df['Low'].values
        
        swing_highs = []
        swing_lows = []
        
        for i in range(window, len(df) - window):
            # قمة
            if highs[i] == max(highs[i-window:i+window+1]):
                swing_highs.append((i, highs[i]))
            # قاع
            if lows[i] == min(lows[i-window:i+window+1]):
                swing_lows.append((i, lows[i]))
        
        return swing_highs, swing_lows
    
    def draw_elliott_waves(self, ax, df, swing_highs, swing_lows):
        """رسم موجات إليوت"""
        # دمج القمم والقيعان وترتيبها
        all_points = []
        for idx, price in swing_highs:
            all_points.append((idx, price, 'high'))
        for idx, price in swing_lows:
            all_points.append((idx, price, 'low'))
        
        all_points.sort(key=lambda x: x[0])
        
        if len(all_points) < 5:
            return
        
        # تحديد الموجات (مبسط)
        wave_labels = ['1', '2', '3', '4', '5', 'A', 'B', 'C']
        wave_colors = [self.colors['wave_impulse']] * 5 + [self.colors['wave_corrective']] * 3
        
        # رسم الموجات
        points_to_draw = all_points[-8:] if len(all_points) >= 8 else all_points
        
        for i, (idx, price, point_type) in enumerate(points_to_draw):
            if i < len(wave_labels):
                label = wave_labels[i]
                color = wave_colors[i] if i < len(wave_colors) else self.colors['wave_impulse']
                
                # رسم الدائرة
                ax.scatter(idx, price, color=color, s=100, zorder=5, edgecolors='white', linewidths=1)
                
                # رسم الرقم
                offset = 0.02 * (df['High'].max() - df['Low'].min())
                y_offset = offset if point_type == 'high' else -offset
                ax.annotate(
                    label,
                    (idx, price + y_offset),
                    fontsize=12,
                    fontweight='bold',
                    color=color,
                    ha='center',
                    va='bottom' if point_type == 'high' else 'top'
                )
        
        # رسم خطوط الموجات
        if len(points_to_draw) > 1:
            x_points = [p[0] for p in points_to_draw]
            y_points = [p[1] for p in points_to_draw]
            ax.plot(x_points, y_points, color=self.colors['wave_impulse'], 
                   linewidth=1.5, linestyle='--', alpha=0.7)
    
    def draw_support_resistance(self, ax, df, levels):
        """رسم مستويات الدعم والمقاومة"""
        for level_type, price, strength in levels:
            color = self.colors['support'] if level_type == 'support' else self.colors['resistance']
            alpha = min(0.3 + strength * 0.1, 0.8)
            
            ax.axhline(y=price, color=color, linestyle='-', linewidth=2, alpha=alpha)
            
            label = f"{'S' if level_type == 'support' else 'R'}: ${price:.2f}"
            ax.annotate(
                label,
                (len(df) - 1, price),
                fontsize=9,
                color=color,
                ha='left',
                va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e', edgecolor=color, alpha=0.8)
            )
    
    def draw_order_blocks(self, ax, df, order_blocks):
        """رسم Order Blocks"""
        for ob in order_blocks:
            start_idx = ob['start_idx']
            end_idx = min(ob['end_idx'], len(df) - 1)
            high = ob['high']
            low = ob['low']
            ob_type = ob['type']
            
            color = self.colors['bullish'] if ob_type == 'bullish' else self.colors['bearish']
            
            # رسم المنطقة
            rect = Rectangle(
                (start_idx, low),
                end_idx - start_idx + 5,
                high - low,
                facecolor=color,
                alpha=0.2,
                edgecolor=color,
                linewidth=1
            )
            ax.add_patch(rect)
            
            # التسمية
            label = "OB+" if ob_type == 'bullish' else "OB-"
            ax.annotate(
                label,
                (start_idx + 1, (high + low) / 2),
                fontsize=8,
                color=color,
                fontweight='bold'
            )
    
    def draw_fvg(self, ax, df, fvg_zones):
        """رسم Fair Value Gaps"""
        for fvg in fvg_zones:
            start_idx = fvg['idx']
            high = fvg['high']
            low = fvg['low']
            
            # رسم المنطقة
            rect = Rectangle(
                (start_idx, low),
                len(df) - start_idx,
                high - low,
                facecolor=self.colors['neutral'],
                alpha=0.15,
                edgecolor=self.colors['neutral'],
                linewidth=1,
                linestyle='--'
            )
            ax.add_patch(rect)
            
            ax.annotate(
                "FVG",
                (start_idx + 1, (high + low) / 2),
                fontsize=8,
                color=self.colors['neutral'],
                fontweight='bold'
            )
    
    def draw_harmonic_pattern(self, ax, pattern):
        """رسم النماذج التوافقية"""
        if not pattern or 'points' not in pattern:
            return
        
        points = pattern['points']
        labels = ['X', 'A', 'B', 'C', 'D']
        
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        
        # رسم الخطوط
        ax.plot(x_coords, y_coords, color=self.colors['harmonic'], 
               linewidth=2, linestyle='-', marker='o', markersize=8)
        
        # رسم التسميات
        for i, (x, y) in enumerate(points):
            if i < len(labels):
                offset = 0.02 * (max(y_coords) - min(y_coords))
                ax.annotate(
                    labels[i],
                    (x, y + offset),
                    fontsize=11,
                    fontweight='bold',
                    color=self.colors['harmonic'],
                    ha='center'
                )
        
        # اسم النموذج
        if 'name' in pattern:
            mid_x = sum(x_coords) / len(x_coords)
            mid_y = max(y_coords) + 0.05 * (max(y_coords) - min(y_coords))
            ax.annotate(
                pattern['name'],
                (mid_x, mid_y),
                fontsize=10,
                color=self.colors['harmonic'],
                ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e', 
                         edgecolor=self.colors['harmonic'], alpha=0.8)
            )
    
    def draw_fibonacci(self, ax, df, swing_high, swing_low):
        """رسم مستويات فيبوناتشي"""
        fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
        fib_colors = ['#ff4757', '#ffa502', '#2ed573', '#1e90ff', '#9b59b6', '#e74c3c', '#00ff88']
        
        high_price = swing_high[1]
        low_price = swing_low[1]
        diff = high_price - low_price
        
        for level, color in zip(fib_levels, fib_colors):
            price = low_price + diff * level
            ax.axhline(y=price, color=color, linestyle=':', linewidth=1, alpha=0.6)
            ax.annotate(
                f"{level:.1%}",
                (len(df) + 1, price),
                fontsize=8,
                color=color,
                ha='left',
                va='center'
            )
    
    def draw_trendlines(self, ax, df, swing_highs, swing_lows):
        """رسم خطوط الاتجاه"""
        # خط اتجاه صاعد (من القيعان)
        if len(swing_lows) >= 2:
            lows_sorted = sorted(swing_lows[-5:], key=lambda x: x[0])
            if len(lows_sorted) >= 2:
                x1, y1 = lows_sorted[0]
                x2, y2 = lows_sorted[-1]
                
                if x2 != x1:
                    slope = (y2 - y1) / (x2 - x1)
                    x_extend = len(df) + 5
                    y_extend = y1 + slope * (x_extend - x1)
                    
                    ax.plot([x1, x_extend], [y1, y_extend], 
                           color=self.colors['bullish'], linewidth=1.5, 
                           linestyle='--', alpha=0.7)
        
        # خط اتجاه هابط (من القمم)
        if len(swing_highs) >= 2:
            highs_sorted = sorted(swing_highs[-5:], key=lambda x: x[0])
            if len(highs_sorted) >= 2:
                x1, y1 = highs_sorted[0]
                x2, y2 = highs_sorted[-1]
                
                if x2 != x1:
                    slope = (y2 - y1) / (x2 - x1)
                    x_extend = len(df) + 5
                    y_extend = y1 + slope * (x_extend - x1)
                    
                    ax.plot([x1, x_extend], [y1, y_extend], 
                           color=self.colors['bearish'], linewidth=1.5, 
                           linestyle='--', alpha=0.7)
    
    def calculate_support_resistance(self, df, num_levels=3):
        """حساب مستويات الدعم والمقاومة"""
        swing_highs, swing_lows = self.find_swing_points(df)
        
        current_price = df['Close'].iloc[-1]
        levels = []
        
        # المقاومات (فوق السعر الحالي)
        resistances = [(idx, price) for idx, price in swing_highs if price > current_price]
        resistances.sort(key=lambda x: x[1])
        for i, (idx, price) in enumerate(resistances[:num_levels]):
            levels.append(('resistance', price, num_levels - i))
        
        # الدعوم (تحت السعر الحالي)
        supports = [(idx, price) for idx, price in swing_lows if price < current_price]
        supports.sort(key=lambda x: x[1], reverse=True)
        for i, (idx, price) in enumerate(supports[:num_levels]):
            levels.append(('support', price, num_levels - i))
        
        return levels
    
    def detect_order_blocks(self, df):
        """كشف Order Blocks"""
        order_blocks = []
        
        for i in range(2, len(df) - 1):
            # Bullish Order Block
            if (df['Close'].iloc[i-1] < df['Open'].iloc[i-1] and  # شمعة هابطة
                df['Close'].iloc[i] > df['Open'].iloc[i] and      # شمعة صاعدة
                df['Close'].iloc[i] > df['High'].iloc[i-1]):      # كسر القمة
                
                order_blocks.append({
                    'type': 'bullish',
                    'start_idx': i - 1,
                    'end_idx': i,
                    'high': df['High'].iloc[i-1],
                    'low': df['Low'].iloc[i-1]
                })
            
            # Bearish Order Block
            if (df['Close'].iloc[i-1] > df['Open'].iloc[i-1] and  # شمعة صاعدة
                df['Close'].iloc[i] < df['Open'].iloc[i] and      # شمعة هابطة
                df['Close'].iloc[i] < df['Low'].iloc[i-1]):       # كسر القاع
                
                order_blocks.append({
                    'type': 'bearish',
                    'start_idx': i - 1,
                    'end_idx': i,
                    'high': df['High'].iloc[i-1],
                    'low': df['Low'].iloc[i-1]
                })
        
        return order_blocks[-5:]  # آخر 5 فقط
    
    def detect_fvg(self, df):
        """كشف Fair Value Gaps"""
        fvg_zones = []
        
        for i in range(2, len(df)):
            # Bullish FVG
            if df['Low'].iloc[i] > df['High'].iloc[i-2]:
                fvg_zones.append({
                    'type': 'bullish',
                    'idx': i - 1,
                    'high': df['Low'].iloc[i],
                    'low': df['High'].iloc[i-2]
                })
            
            # Bearish FVG
            if df['High'].iloc[i] < df['Low'].iloc[i-2]:
                fvg_zones.append({
                    'type': 'bearish',
                    'idx': i - 1,
                    'high': df['Low'].iloc[i-2],
                    'low': df['High'].iloc[i]
                })
        
        return fvg_zones[-5:]  # آخر 5 فقط
    
    def detect_harmonic_pattern(self, df, swing_highs, swing_lows):
        """كشف النماذج التوافقية (مبسط)"""
        all_points = []
        for idx, price in swing_highs:
            all_points.append((idx, price, 'high'))
        for idx, price in swing_lows:
            all_points.append((idx, price, 'low'))
        
        all_points.sort(key=lambda x: x[0])
        
        if len(all_points) < 5:
            return None
        
        # أخذ آخر 5 نقاط
        last_5 = all_points[-5:]
        points = [(p[0], p[1]) for p in last_5]
        
        # حساب النسب
        xa = abs(points[1][1] - points[0][1])
        ab = abs(points[2][1] - points[1][1])
        bc = abs(points[3][1] - points[2][1])
        cd = abs(points[4][1] - points[3][1])
        
        if xa == 0:
            return None
        
        ab_xa = ab / xa
        bc_ab = bc / ab if ab != 0 else 0
        cd_bc = cd / bc if bc != 0 else 0
        
        # تحديد النموذج بناءً على النسب
        pattern_name = None
        
        # Gartley
        if 0.55 <= ab_xa <= 0.72:
            pattern_name = "Gartley"
        # Butterfly
        elif 0.72 <= ab_xa <= 0.88:
            pattern_name = "Butterfly"
        # Bat
        elif 0.35 <= ab_xa <= 0.55:
            pattern_name = "Bat"
        # Crab
        elif 0.35 <= ab_xa <= 0.65:
            pattern_name = "Crab"
        
        if pattern_name:
            return {
                'name': pattern_name,
                'points': points,
                'ratios': {
                    'AB/XA': ab_xa,
                    'BC/AB': bc_ab,
                    'CD/BC': cd_bc
                }
            }
        
        return None
    
    def generate_chart(self, df, symbol, timeframe, analysis_types=['all'], 
                       save_path=None):
        """
        توليد الشارت مع التحليل الفني
        
        analysis_types: قائمة بأنواع التحليل المطلوبة
        - 'elliott': موجات إليوت
        - 'classic': الدعم والمقاومة وخطوط الاتجاه
        - 'harmonic': النماذج التوافقية
        - 'ict': Order Blocks و FVG
        - 'all': جميع التحليلات
        """
        
        if 'all' in analysis_types:
            analysis_types = ['elliott', 'classic', 'harmonic', 'ict']
        
        # إنشاء الرسم
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # رسم الشموع
        self.draw_candlesticks(ax, df)
        
        # تحديد القمم والقيعان
        swing_highs, swing_lows = self.find_swing_points(df)
        
        # رسم التحليلات المطلوبة
        if 'elliott' in analysis_types:
            self.draw_elliott_waves(ax, df, swing_highs, swing_lows)
        
        if 'classic' in analysis_types:
            levels = self.calculate_support_resistance(df)
            self.draw_support_resistance(ax, df, levels)
            self.draw_trendlines(ax, df, swing_highs, swing_lows)
            
            # فيبوناتشي
            if swing_highs and swing_lows:
                recent_high = max(swing_highs[-3:], key=lambda x: x[1]) if len(swing_highs) >= 3 else swing_highs[-1]
                recent_low = min(swing_lows[-3:], key=lambda x: x[1]) if len(swing_lows) >= 3 else swing_lows[-1]
                self.draw_fibonacci(ax, df, recent_high, recent_low)
        
        if 'harmonic' in analysis_types:
            pattern = self.detect_harmonic_pattern(df, swing_highs, swing_lows)
            if pattern:
                self.draw_harmonic_pattern(ax, pattern)
        
        if 'ict' in analysis_types:
            order_blocks = self.detect_order_blocks(df)
            self.draw_order_blocks(ax, df, order_blocks)
            
            fvg_zones = self.detect_fvg(df)
            self.draw_fvg(ax, df, fvg_zones)
        
        # إعدادات المحاور
        ax.set_xlim(-1, len(df) + 5)
        ax.set_ylim(df['Low'].min() * 0.98, df['High'].max() * 1.02)
        
        # العنوان
        title = f"📊 {symbol} - {timeframe}"
        analysis_names = {
            'elliott': '🌊 Elliott',
            'classic': '📈 Classic',
            'harmonic': '🔷 Harmonic',
            'ict': '🎯 ICT'
        }
        title += " | " + " • ".join([analysis_names.get(a, a) for a in analysis_types])
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('', fontsize=10)
        ax.set_ylabel('السعر ($)', fontsize=10)
        
        # الشبكة
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        
        # إضافة معلومات
        current_price = df['Close'].iloc[-1]
        info_text = f"السعر الحالي: ${current_price:.2f}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor='#e94560', alpha=0.8))
        
        # التاريخ
        date_text = datetime.now().strftime('%Y-%m-%d %H:%M')
        ax.text(0.98, 0.98, date_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top', horizontalalignment='right',
               color='#888888')
        
        plt.tight_layout()
        
        # حفظ أو إرجاع
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', 
                       facecolor='#1a1a2e', edgecolor='none')
            plt.close()
            return save_path
        else:
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                       facecolor='#1a1a2e', edgecolor='none')
            buf.seek(0)
            plt.close()
            return buf
    
    def generate_multi_timeframe_chart(self, data_dict, symbol):
        """
        توليد شارت متعدد الفريمات
        data_dict: قاموس {timeframe: dataframe}
        """
        num_frames = len(data_dict)
        fig, axes = plt.subplots(1, num_frames, figsize=(6 * num_frames, 6))
        
        if num_frames == 1:
            axes = [axes]
        
        for ax, (tf, df) in zip(axes, data_dict.items()):
            # رسم مبسط لكل فريم
            for i in range(len(df)):
                row = df.iloc[i]
                color = self.colors['bullish'] if row['Close'] >= row['Open'] else self.colors['bearish']
                
                body_bottom = min(row['Open'], row['Close'])
                body_height = abs(row['Close'] - row['Open'])
                
                rect = Rectangle((i - 0.3, body_bottom), 0.6, body_height,
                                facecolor=color, edgecolor=color)
                ax.add_patch(rect)
                ax.plot([i, i], [row['Low'], row['High']], color=color, linewidth=0.5)
            
            ax.set_xlim(-1, len(df) + 1)
            ax.set_ylim(df['Low'].min() * 0.99, df['High'].max() * 1.01)
            ax.set_title(f"{symbol} - {tf}", fontsize=11)
            ax.grid(True, alpha=0.3)
        
        plt.suptitle(f"📊 {symbol} - Multi Timeframe Analysis", fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                   facecolor='#1a1a2e', edgecolor='none')
        buf.seek(0)
        plt.close()
        return buf


# للاختبار
if __name__ == '__main__':
    import yfinance as yf
    
    # جلب بيانات تجريبية
    stock = yf.Ticker("AAPL")
    df = stock.history(period="3mo", interval="1d")
    df = df.reset_index()
    
    # إنشاء الشارت
    drawer = ChartDrawer()
    chart = drawer.generate_chart(df, "AAPL", "Daily", ['all'], "test_chart.png")
    print(f"Chart saved: {chart}")
