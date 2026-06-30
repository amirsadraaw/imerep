"""
سرویس برای کار با قراردادها و نمادهای بازار
"""
from database.db import get_market_conn
from datetime import datetime


class ContractService:
    """سرویس مدیریت قراردادها و نمادها"""

    @staticmethod
    def get_contracts_by_market_type(market_type_code):
        """
        دریافت تمام نمادهای یک نوع بازار از دیتابیس
        
        Args:
            market_type_code: کد نوع بازار (cdc، option، future)
            
        Returns:
            لیستی از نمادها به فرمت: [{'code': 'نماد', 'description': 'توضیحات'}, ...]
        """
        conn = get_market_conn()
        cursor = conn.cursor()
        
        try:
            # گرفتن تمام نمادهای یک بازار (بدون تکراری)
            cursor.execute("""
                SELECT DISTINCT contract_code, contract_description
                FROM snapshots
                WHERE market_type = ?
                ORDER BY contract_code
            """, (market_type_code,))
            
            contracts = []
            for row in cursor.fetchall():
                contracts.append({
                    'code': row[0],
                    'description': row[1]
                })
            
            return contracts
        
        except Exception as e:
            print(f"خطا در دریافت نمادها: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_latest_data_by_contract(contract_code, contract_id=None):
        """
        دریافت آخرین داده‌های یک نماد
        
        Args:
            contract_code: کد نماد (مثل: شمش طلا)
            contract_id: شناسه قرارداد (اختیاری)
            
        Returns:
            dict با اطلاعات آخرین قیمت و جزئیات
        """
        conn = get_market_conn()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    contract_code,
                    contract_description,
                    market_type,
                    last_price,
                    volume,
                    volume_delta,
                    open_interest,
                    snapshot_time,
                    trade_date
                FROM snapshots
                WHERE contract_code = ?
                ORDER BY snapshot_time DESC
                LIMIT 1
            """, (contract_code,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'code': row[0],
                'description': row[1],
                'market_type': row[2],
                'last_price': row[3],
                'volume': row[4],
                'volume_delta': row[5],
                'open_interest': row[6],
                'snapshot_time': row[7],
                'trade_date': row[8]
            }
        
        except Exception as e:
            print(f"خطا در دریافت داده نماد: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_today_data(contract_code):
        """
        دریافت تمام داده‌های امروز یک نماد برای ساخت چارت
        
        Args:
            contract_code: کد نماد
            
        Returns:
            لیستی از snapshots امروز مرتب شده براساس زمان
        """
        conn = get_market_conn()
        cursor = conn.cursor()
        
        try:
            from datetime import date
            today = str(date.today())
            
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
            """, (contract_code, today))
            
            data = []
            for row in cursor.fetchall():
                data.append({
                    'code': row[0],
                    'price': row[1],
                    'volume': row[2],
                    'volume_delta': row[3],
                    'oi': row[4],
                    'time': row[5],
                    'date': row[6]
                })
            
            return data
        
        except Exception as e:
            print(f"خطا در دریافت داده‌های امروز: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_formatted_data_message(contract_code):
        """
        ساخت پیام متنی برای نمایش داده‌های نماد
        
        Args:
            contract_code: کد نماد
            
        Returns:
            str: پیام فرمت شده برای ارسال به کاربر
        """
        data = ContractService.get_latest_data_by_contract(contract_code)
        
        if not data:
            return f"❌ داده‌ای برای {contract_code} یافت نشد"
        
        message = f"""
📊 **{data['description']} ({data['code']})**

🏷️ **بازار:** {data['market_type']}
💰 **آخرین قیمت:** {data['last_price']:,} تومان
📈 **حجم:** {data['volume']:,}
📍 **تغییر حجم:** {data['volume_delta']:,}
🔓 **تعداد پوزیشن باز:** {data['open_interest']:,}

⏰ **زمان:** {data['snapshot_time']}
📅 **تاریخ معاملات:** {data['trade_date']}
"""
        return message
