import os
import sys
import sqlite3
from datetime import datetime
from bidi.algorithm import get_display
import arabic_reshaper
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
import requests

# --- بيئة التشغيل ودعم اللغة العربية التلقائي ---
# هنا نختبر: إذا كان النظام ليس ويندوز (أي أندرويد)، نفعّل pango
if sys.platform != "win32":
    os.environ["KIVY_TEXT"] = "pango"

def fix_arabic(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# --- رقم IP الكمبيوتر المركزي (تعدله بحسب شبكتك الحالية) ---
SERVER_IP = "127.0.0.1" if sys.platform == "win32" else "192.168.1.50" 
SERVER_PORT = "8000"

# --- تصميم الواجهات بلغة KV ---
KV = """
#:import fix_arabic __main__.fix_arabic

ScreenManager:
    LoginScreen:
    MainScreen:
    ScannerScreen:

<LoginScreen>:
    name: 'login'
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.97, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: fix_arabic("نظام إدارة العدادات الميداني")
            font_name: "cairo.ttf"
            font_size: '28sp'
            color: 0.1, 0.2, 0.3, 1
            size_hint_y: 0.3

        Button:
            text: fix_arabic("الدخول إلى النظام")
            font_name: "cairo.ttf"
            font_size: '20sp'
            size_hint_y: 0.15
            background_color: 0.2, 0.6, 0.4, 1
            on_press: root.manager.current = 'main'

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 15

        BoxLayout:
            size_hint_y: 0.1
            canvas.before:
                Color:
                    rgba: 0.1, 0.2, 0.3, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: fix_arabic("الرئيسية - قائمة التحكم")
                font_name: "cairo.ttf"
                font_size: '18sp'

        BoxLayout:
            orientation: 'vertical'
            spacing: 15
            padding: [10, 20, 10, 20]
            
            Button:
                text: fix_arabic("📷 ابدأ مسح باركود العداد")
                font_name: "cairo.ttf"
                font_size: '22sp'
                background_color: 0.15, 0.45, 0.75, 1
                on_press: root.manager.current = 'scanner'

            Button:
                text: fix_arabic("📥 تحديث بيانات المشتركين")
                font_name: "cairo.ttf"
                font_size: '18sp'
                background_color: 0.4, 0.3, 0.6, 1
                on_press: root.fetch_customers_from_server()

            Button:
                text: fix_arabic("🔄 مزامنة القراءات للمحطة")
                font_name: "cairo.ttf"
                font_size: '18sp'
                background_color: 0.2, 0.6, 0.4, 1
                on_press: root.sync_data_to_server()

        BoxLayout:
            size_hint_y: 0.18
            orientation: 'vertical'
            canvas.before:
                Color:
                    rgba: 0.9, 0.9, 0.9, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                id: status_label
                text: fix_arabic("جاهز للعمل الميداني")
                font_name: "cairo.ttf"
                color: 0.2, 0.2, 0.2, 1
            Label:
                id: count_label
                text: fix_arabic("العدادات غير المتزامنة حالياً: 0")
                font_name: "cairo.ttf"
                color: 0.8, 0.3, 0.1, 1

<ScannerScreen>:
    name: 'scanner'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10

        BoxLayout:
            size_hint_y: 0.08
            Button:
                text: fix_arabic("رجوع")
                font_name: "cairo.ttf"
                size_hint_width: 0.25
                on_press: root.go_back()
            Label:
                text: fix_arabic("إدخال قراءة العداد")
                font_name: "cairo.ttf"
                font_size: '18sp'

        BoxLayout:
            size_hint_y: 0.12
            spacing: 5
            TextInput:
                id: barcode_input
                hint_text: "ادخل رقم الباركود هنا..."
                multiline: False
                font_size: '16sp'
            Button:
                text: fix_arabic("بحث")
                font_name: "cairo.ttf"
                size_hint_width: 0.25
                on_press: root.search_barcode(root.ids.barcode_input.text)

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.5
            padding: 10
            canvas.before:
                Color:
                    rgba: 0.95, 0.95, 0.95, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10]
            
            Label:
                id: cust_name
                text: fix_arabic("اسم المشترك: ---")
                font_name: "cairo.ttf"
                color: 0,0,0,1
            Label:
                id: cust_address
                text: fix_arabic("السكن: ---")
                font_name: "cairo.ttf"
                color: 0,0,0,1
            Label:
                id: cust_phone
                text: fix_arabic("رقم الهاتف: ---")
                font_name: "cairo.ttf"
                color: 0,0,0,1
            Label:
                id: cust_last_reading
                text: fix_arabic("القراءة السابقة: 0")
                font_name: "cairo.ttf"
                color: 0.1, 0.5, 0.2, 1

        BoxLayout:
            size_hint_y: 0.3
            orientation: 'vertical'
            spacing: 10
            
            TextInput:
                id: current_reading_input
                hint_text: "ادخل القراءة الحالية هنا..."
                input_filter: 'float'
                multiline: False
                font_size: '20sp'
                halign: 'center'

            Button:
                text: fix_arabic("💾 حفظ القراءة محلياً")
                font_name: "cairo.ttf"
                font_size: '20sp'
                background_color: 0.2, 0.6, 0.4, 1
                on_press: root.save_reading()
"""

class LoginScreen(Screen):
    pass

class MainScreen(Screen):
    def on_enter(self):
        self.update_counts()

    def update_counts(self):
        conn = sqlite3.connect("field_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM local_readings WHERE is_synced = 0")
        count = cursor.fetchone()[0]
        self.ids.count_label.text = fix_arabic(f"العدادات غير المتزامنة حالياً: {count}")
        conn.close()

    def fetch_customers_from_server(self):
        self.ids.status_label.text = fix_arabic("جاري جلب بيانات المشتركين...")
        url = f"http://{SERVER_IP}:{SERVER_PORT}/api/customers"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                customers = response.json().get("customers", [])
                conn = sqlite3.connect("field_data.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM local_customers")
                for c in customers:
                    cursor.execute("INSERT OR REPLACE INTO local_customers VALUES (?, ?, ?, ?, ?)",
                                   (c["barcode"], c["name"], c["address"], c["phone"], c["last_reading"]))
                conn.commit()
                conn.close()
                self.ids.status_label.text = fix_arabic(f"تم تحديث بيانات {len(customers)} مشترك بنجاح.")
            else:
                self.ids.status_label.text = fix_arabic("خطأ: السيرفر لم يستجب بشكل صحيح.")
        except Exception as e:
            self.ids.status_label.text = fix_arabic("تعذر الاتصال بالسيرفر المركزي.")

    def sync_data_to_server(self):
        self.ids.status_label.text = fix_arabic("جاري إرسال القراءات...")
        conn = sqlite3.connect("field_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, barcode, current_reading, reading_date FROM local_readings WHERE is_synced = 0")
        rows = cursor.fetchall()
        
        if not rows:
            self.ids.status_label.text = fix_arabic("لا توجد قراءات جديدة لإرسالها!")
            conn.close()
            return

        readings_payload = []
        for row in rows:
            readings_payload.append({
                "barcode": row[1],
                "current_reading": row[2],
                "reading_date": row[3],
                "notes": "قراءة ميدانية"
            })

        url = f"http://{SERVER_IP}:{SERVER_PORT}/api/sync"
        try:
            response = requests.post(url, json={"readings": readings_payload}, timeout=5)
            if response.status_code == 200:
                for row in rows:
                    cursor.execute("UPDATE local_readings SET is_synced = 1 WHERE id = ?", (row[0],))
                conn.commit()
                self.ids.status_label.text = fix_arabic(f"نجاح! تم إرسال {len(rows)} قراءة.")
            else:
                self.ids.status_label.text = fix_arabic("فشلت المزامنة من السيرفر.")
        except Exception as e:
            self.ids.status_label.text = fix_arabic("خطأ في الاتصال بالسيرفر.")
        
        conn.close()
        self.update_counts()

class ScannerScreen(Screen):
    current_cust_barcode = None

    def search_barcode(self, barcode):
        if not barcode:
            return
        conn = sqlite3.connect("field_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, address, phone, last_reading FROM local_customers WHERE barcode = ?", (barcode.strip(),))
        row = cursor.fetchone()
        
        if row:
            self.current_cust_barcode = barcode.strip()
            self.ids.cust_name.text = fix_arabic(f"اسم المشترك: {row[0]}")
            self.ids.cust_address.text = fix_arabic(f"السكن: {row[1]}")
            self.ids.cust_phone.text = fix_arabic(f"رقم الهاتف: {row[2]}")
            self.ids.cust_last_reading.text = fix_arabic(f"القراءة السابقة: {row[3]}")
        else:
            self.current_cust_barcode = None
            self.ids.cust_name.text = fix_arabic("❌ الباركود غير مسجل!")
            self.ids.cust_address.text = ""
            self.ids.cust_phone.text = ""
            self.ids.cust_last_reading.text = ""
        conn.close()

    def save_reading(self):
        if not self.current_cust_barcode:
            return
        reading_val = self.ids.current_reading_input.text
        if not reading_val:
            return
        
        conn = sqlite3.connect("field_data.db")
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            "INSERT INTO local_readings (barcode, current_reading, reading_date, is_synced) VALUES (?, ?, ?, 0)",
            (self.current_cust_barcode, float(reading_val), now_str)
        )
        cursor.execute("UPDATE local_customers SET last_reading = ? WHERE barcode = ?", (float(reading_val), self.current_cust_barcode))
        conn.commit()
        conn.close()
        
        self.ids.current_reading_input.text = ""
        self.ids.barcode_input.text = ""
        self.manager.current = 'main'

    def go_back(self):
        self.ids.current_reading_input.text = ""
        self.ids.barcode_input.text = ""
        self.manager.current = 'main'

def init_local_database():
    conn = sqlite3.connect("field_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS local_customers (
            barcode TEXT PRIMARY KEY,
            name TEXT,
            address TEXT,
            phone TEXT,
            last_reading REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS local_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            current_reading REAL,
            reading_date TEXT,
            is_synced INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

class MeterSystemApp(App):
    def build(self):
        init_local_database()
        return Builder.load_string(KV)

if __name__ == '__main__':
    MeterSystemApp().run()