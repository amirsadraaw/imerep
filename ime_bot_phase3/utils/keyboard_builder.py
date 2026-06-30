"""
ابزارهایی برای ساخت کیبوردهای دینامیک
"""


def build_dynamic_keyboard(items, items_per_row=2):
    """
    ساخت کیبورد دینامیک از لیست آیتم‌ها
    
    Args:
        items: لیستی از dict‌ها با کلیدهای 'code' و 'description'
        items_per_row: تعداد آیتم‌ها در هر ردیف
        
    Returns:
        dict: کیبورد فرمت شده برای Telegram/Bale
    """
    keyboard = []
    row = []
    
    for item in items:
        # استفاده از code به عنوان متن دکمه
        button = {"text": item['code']}
        row.append(button)
        
        if len(row) == items_per_row:
            keyboard.append(row)
            row = []
    
    # اضافه کردن دکمه‌های باقی‌مانده
    if row:
        keyboard.append(row)
    
    # اضافه کردن دکمه بازگشت
    keyboard.append([{"text": "بازگشت"}])
    
    return {
        "keyboard": keyboard,
        "resize_keyboard": True
    }


def build_custom_keyboard(buttons_list):
    """
    ساخت کیبورد سفارشی از لیست دکمه‌ها
    
    Args:
        buttons_list: لیستی از لیست‌های دکمه‌ها
                     مثال: [['دکمه 1', 'دکمه 2'], ['دکمه 3']]
        
    Returns:
        dict: کیبورد فرمت شده
    """
    keyboard = []
    
    for row_buttons in buttons_list:
        row = [{"text": btn} for btn in row_buttons]
        keyboard.append(row)
    
    return {
        "keyboard": keyboard,
        "resize_keyboard": True
    }
