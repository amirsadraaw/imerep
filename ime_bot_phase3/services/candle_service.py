"""
سرویس برای تولید چارت‌های شمعی
"""
import io
from datetime import datetime, timedelta
from database.db import get_market_conn
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np


class CandleService:
    """سرویس ساخت چارت‌های شمعی"""

    @staticmethod
    def group_by_timeframe(snapshots, timeframe_minutes=5):
        """
        گروپ‌بندی snapshots به بازه‌های زمانی
        
        Args:
            snapshots: لیستی از snapshots
            timeframe_minutes: طول هر شمع به دقیقه
            
        Returns:
            لیستی از شمع‌ها با اطلاعات open, high, low, close
        """
        if not snapshots:
            return []
        
        candles = []
        current_candle = None
        current_timeframe = None
        
        for snapshot in snapshots:
            try:
                # تبدیل زمان snapshot به datetime
                snap_time = datetime.strptime(
                    snapshot['time'], 
                    "%Y-%m-%d %H:%M:%S"
                )
                
                # تحدید بازه زمانی
                timeframe_start = snap_time.replace(
                    minute=(snap_time.minute // timeframe_minutes) * timeframe_minutes,
                    second=0,
                    microsecond=0
                )
                
                price = snapshot['price']
                
                # اگر بازه زمانی تغیر کرد، شمع قبلی را ذخیره کن
                if current_timeframe != timeframe_start:
                    if current_candle:
                        candles.append(current_candle)
                    
                    current_timeframe = timeframe_start
                    current_candle = {
                        'time': timeframe_start,
                        'open': price,
                        'high': price,
                        'low': price,
                        'close': price,
                        'volume': snapshot.get('volume', 0)
                    }
                else:
                    # بروزرسانی شمع فعلی
                    current_candle['high'] = max(current_candle['high'], price)
                    current_candle['low'] = min(current_candle['low'], price)
                    current_candle['close'] = price
                    current_candle['volume'] += snapshot.get('volume', 0)
            
            except Exception as e:
                print(f"خطا در پردازش snapshot: {e}")
                continue
        
        # اضافه کردن آخرین شمع
        if current_candle:
            candles.append(current_candle)
        
        return candles

    @staticmethod
    def create_candlestick_chart(contract_code, snapshots, timeframe_minutes=5):
        """
        ساخت چارت شمعی
        
        Args:
            contract_code: کد نماد
            snapshots: لیستی از snapshots امروز
            timeframe_minutes: طول هر شمع
            
        Returns:
            bytes: تصویر چارت
        """
        if not snapshots:
            return None
        
        try:
            # گروپ‌بندی داده‌ها
            candles = CandleService.group_by_timeframe(snapshots, timeframe_minutes)
            
            if not candles:
                return None
            
            # استخراج داده‌ها
            times = [c['time'] for c in candles]
            opens = [c['open'] for c in candles]
            highs = [c['high'] for c in candles]
            lows = [c['low'] for c in candles]
            closes = [c['close'] for c in candles]
            volumes = [c['volume'] for c in candles]
            
            # ساخت شکل
            fig, (ax1, ax2) = plt.subplots(
                2, 1,
                figsize=(14, 8),
                gridspec_kw={'height_ratios': [3, 1]}
            )
            
            # تنظیمات فارسی
            plt.rcParams['font.family'] = 'DejaVu Sans'
            
            # رسم شمع‌ها
            width = 0.6
            for i, (t, o, h, l, c, v) in enumerate(zip(
                times, opens, highs, lows, closes, volumes
            )):
                # رنگ: سبز اگر close > open، قرمز اگر close < open
                color = 'green' if c >= o else 'red'
                
                # خط بالا و پایین (Wick)
                ax1.plot([i, i], [l, h], color=color, linewidth=1)
                
                # بدنه شمع
                body_height = abs(c - o)
                body_bottom = min(o, c)
                
                rect = Rectangle(
                    (i - width/2, body_bottom),
                    width,
                    body_height,
                    facecolor=color,
                    edgecolor=color,
                    linewidth=1
                )
                ax1.add_patch(rect)
            
            # تنظیمات چارت قیمت
            ax1.set_xlabel('Time', fontsize=10)
            ax1.set_ylabel('Price', fontsize=10)
            ax1.set_title(f'{contract_code} - {timeframe_minutes}min Candlestick Chart', 
                          fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.set_xlim(-1, len(candles))
            
            # تعیین نقاط X axis
            step = max(1, len(candles) // 10)
            ax1.set_xticks(range(0, len(candles), step))
            ax1.set_xticklabels(
                [t.strftime('%H:%M') for t in times[::step]],
                rotation=45
            )
            
            # رسم حجم
            colors_vol = ['green' if closes[i] >= opens[i] else 'red' 
                          for i in range(len(candles))]
            ax2.bar(range(len(volumes)), volumes, color=colors_vol, alpha=0.6)
            ax2.set_ylabel('Volume', fontsize=10)
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(-1, len(candles))
            ax2.set_xticks(range(0, len(candles), step))
            ax2.set_xticklabels(
                [t.strftime('%H:%M') for t in times[::step]],
                rotation=45
            )
            
            plt.tight_layout()
            
            # تبدیل به bytes
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        
        except Exception as e:
            print(f"خطا در ساخت چارت: {e}")
            return None

    @staticmethod
    def get_latest_snapshots(contract_code):
        """
        دریافت تمام snapshots آخرین روز موجود برای یک نماد
        
        Args:
            contract_code: کد نماد
            
        Returns:
            لیستی از snapshots
        """
        conn = get_market_conn()
        cursor = conn.cursor()
        
        try:
            # ابتدا آخرین تاریخ موجود برای این نماد را بگیر
            cursor.execute("""
                SELECT MAX(trade_date)
                FROM snapshots
                WHERE contract_code = ?
            """, (contract_code,))
            
            result = cursor.fetchone()
            latest_date = result[0] if result and result[0] else None
            
            if not latest_date:
                return []
            
            # اکنون تمام snapshots آن روز را بگیر
            cursor.execute("""
                SELECT 
                    contract_code,
                    last_price,
                    volume,
                    volume_delta,
                    open_interest,
                    snapshot_time,
                    trade_date
                FROM snapshots
                WHERE contract_code = ? AND trade_date = ?
                ORDER BY snapshot_time ASC
            """, (contract_code, latest_date))
            
            snapshots = []
            for row in cursor.fetchall():
                snapshots.append({
                    'code': row[0],
                    'price': row[1],
                    'volume': row[2],
                    'volume_delta': row[3],
                    'oi': row[4],
                    'time': row[5],
                    'date': row[6]
                })
            
            return snapshots
        
        except Exception as e:
            print(f"خطا در دریافت snapshots: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def create_chart_image(contract_code, timeframe_minutes=5):
        """
        ساخت و بازگشت تصویر چارت برای یک نماد
        
        Args:
            contract_code: کد نماد
            timeframe_minutes: طول هر شمع
            
        Returns:
            tuple: (bytes, str) - تصویر و متن توضیح
        """
        # دریافت snapshots آخرین روز
        snapshots = CandleService.get_latest_snapshots(contract_code)
        
        if not snapshots:
            return None, f"❌ داده‌ای برای {contract_code} یافت نشد"
        
        # ساخت چارت
        image = CandleService.create_candlestick_chart(
            contract_code,
            snapshots,
            timeframe_minutes
        )
        
        if not image:
            return None, f"❌ خطا در ساخت چارت برای {contract_code}"
        
        # متن توضیح - استفاده از آخرین snapshot
        last_snap = snapshots[-1]
        first_snap = snapshots[0]
        
        caption = f"""
📊 **{contract_code}**
⏱️ **{timeframe_minutes} دقیقه‌ای**

📈 **اولین قیمت:** {first_snap['price']:,}
💰 **آخرین قیمت:** {last_snap['price']:,}
🔝 **بالاترین:** {max(s['price'] for s in snapshots):,}
🔻 **پایین‌ترین:** {min(s['price'] for s in snapshots):,}

📈 **حجم:** {int(last_snap['volume']) if last_snap['volume'] else 0:,}
📍 **تغییر حجم:** {int(last_snap['volume_delta']) if last_snap['volume_delta'] else 0:,}
🔓 **پوزیشن باز:** {int(last_snap['oi']) if last_snap['oi'] else 0:,}

📅 **تاریخ:** {last_snap['date']}
⏰ **آخرین بروزرسانی:** {last_snap['time']}
"""
        
        return image, caption
