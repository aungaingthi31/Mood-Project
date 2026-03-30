import flet as ft
import datetime

import datetime
import calendar
import requests

API_URL = "http://192.168.100.38:8000"

hour = datetime.datetime.now().hour

if hour < 12:
    greeting = "Good Morning"
elif hour < 18:
    greeting = "Good Afternoon"
else:
    greeting = "Good Evening"

PRIMARY = "#A67C52"
BG = "#F7F7F7"
CARD = "#FFFFFF"
BORDER = "#EAEAEA"
TEXT = "#333333"



def home_view(page, go):
 
    username = "babe"
    # สร้างคลาสย่อยเพื่อเก็บอ้างอิงของ Row ป้องกันความสับสน
    class ActivityRowRef:
        def __init__(self, name):
            self.name = name
            self.row = None  # จะถูกกำหนดค่าเมื่อสร้าง UI เสร็จ

    selected_mood = {"level": None}
    selected_activities = []  # รูปแบบ: [{"name": "Study", "score": 3}, ...]
    activity_refs = []  # เก็บอ้างอิงเพื่อใช้อัปเดต UI ทีละอัน

    content_area = ft.Container(expand=True)

    # ---------------- DIARY ----------------
    diary = ft.TextField(
        hint_text="How was your day today?",
        multiline=True,
        min_lines=8,
        max_lines=15,
        height=50,
        width=1000,
        border_radius=15,
        filled=True,
        bgcolor="#FAFAFA",
        expand=False
    )

    # ---------------- MOOD ----------------
    mood_colors = [
    ("#6A0DAD", "#E6D6F2"),  # ม่วง (เข้ม, อ่อน)
    ("#3498DB", "#D6EAF8"),  # ฟ้า
    ("#2ECC71", "#D5F5E3"),  # เขียว
    ("#F1C40F", "#FCF3CF"),  # เหลือง
    ("#FF69B4", "#FADADD")   # ชมพู
    ]

    def select_mood(box, value):
        selected_mood["level"] = value
        for c in mood_row.controls:
            c.border = None
        box.border = ft.border.all(3, "#000")
        page.update()

    def mood_circle(color_pair, value):

        strong, soft = color_pair  # แยกสีเข้ม/อ่อน

        def handle_click(e):
            selected_mood["level"] = value

            for c in mood_row.controls:
                is_selected = (c.data["value"] == value)

                c.bgcolor = c.data["strong"] if is_selected else c.data["soft"]

                c.border = ft.border.all(3, "#000") if is_selected else None

            page.update()

        return ft.Container(
            data={
                "value": value,
                "strong": strong,
                "soft": soft
            },

            width=50,
            height=50,
            border_radius=25,

            bgcolor=soft,  # เริ่ม = สีอ่อน (สวยกว่า opacity มาก)

           alignment=ft.Alignment.CENTER,
            content=ft.Text(str(value), color="white"),

            on_click=handle_click
        )

    mood_row = ft.Row(
    [mood_circle(c, i+1) for i, c in enumerate(mood_colors)],
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
)

    # ---------------- ACTIVITY ----------------
    # ✨ ฟังก์ชันใหม่สำหรับสร้างปุ่มคะแนนแบบมีสถานะ
    def create_score_buttons(activity_name, current_score, ref_object):
        
        def set_score(val, act_name, ref_obj):
            # 1. ค้นหาว่ามีกิจกรรมนี้ในรายการที่เลือกหรือยัง
            found = next((a for a in selected_activities if a["name"] == act_name), None)
            if found:
                found["score"] = val  # ถ้ามีแล้ว อัปเดตคะแนนใหม่
            else:
                selected_activities.append({"name": act_name, "score": val})  # ถ้ายังไม่มี เพิ่มใหม่

            # 2. ✨ อัปเดต UI เฉพาะ Row ของกิจกรรมนี้ (ไม่ต้อง page.update() ทั้งหน้า)
            if ref_obj.row:
                ref_obj.row.controls = create_score_buttons(act_name, val, ref_obj)
                ref_obj.row.update()

        buttons = []
        for i in range(1, 6):
            is_selected = (current_score == i)
            
            # ✨ ปรับหน้าตาปุ่มตามสถานะการเลือก
            buttons.append(
                ft.Container(
                    width=40,
                    height=40,
                    border_radius=20,
                    # ถ้าเลือก ใช้สี PRIMARY ถ้าไม่เลือก ใช้สีอ่อน
                    bgcolor=PRIMARY if is_selected else "#EDE0D4", 
                    alignment=ft.Alignment.CENTER,
                    # ถ้าเลือก ใช้ตัวหนังสือสีขาว ถ้าไม่เลือก ใช้สี PRIMARY
                    content=ft.Text(str(i), color="white" if is_selected else PRIMARY, weight="bold"),
                    on_click=lambda e, val=i: set_score(val, activity_name, ref_object)
                )
            )
        return buttons

    # ฟังก์ชันหลักสำหรับสร้างบล็อกกิจกรรม
    def activity_with_score(label, icon):

        current_data = next((a for a in selected_activities if a["name"] == label), None)
        initial_score = current_data["score"] if current_data else None

        ref_obj = ActivityRowRef(label)

        score_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[]
        )
        ref_obj.row = score_row
        activity_refs.append(ref_obj)

        score_row.controls = create_score_buttons(label, initial_score, ref_obj)

        return ft.Container(
            bgcolor="#FAF7F3",
            border_radius=15,
            padding=12,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,   # ✅ เลื่อนได้
                expand=True,
                controls=[
                    ft.Row(
                        [
                            ft.Icon(icon, color=PRIMARY, size=18),
                            ft.Text(label, weight="bold", color=TEXT),
                        ],
                        spacing=10
                    ),
                    score_row
                ]
            )
        )
    activities_ui = ft.Column(
        [
        activity_with_score("Study", ft.Icons.MENU_BOOK_OUTLINED),
        activity_with_score("Exercise", ft.Icons.FITNESS_CENTER),
        activity_with_score("Game", ft.Icons.SPORTS_ESPORTS),
        activity_with_score("Rest", ft.Icons.HOTEL),
        ],
        spacing=10
    )

    # ---------------- SAVE ----------------
    def save(e):
        if selected_mood["level"] is None:
            page.snack_bar = ft.SnackBar(ft.Text("Select mood first"))
            page.snack_bar.open = True
            page.update()
            return

        today = datetime.date.today().isoformat()

        # 🔥 แปลง activities ให้ตรงกับ API
        activities_payload = []
        for a in selected_activities:
            # map name → id
            activity_map = {
                "Study": 1,
                "Exercise": 2,
                "Game": 3,
                "Rest": 4
            }

            activities_payload.append({
                "activity_id": activity_map.get(a["name"]),
                "score": a["score"]
            })

        data = {
            "users_id": page.user_id,
            "date": today,
            "mood": selected_mood["level"],
            "diary": diary.value,
            "activities": activities_payload
        }

        # 🔥 เรียก API
        res = requests.post(f"{API_URL}/records", json=data)
        result = res.json()

        # 🔥 ถ้าซ้ำ
        if "error" in result:
            page.dialog = ft.AlertDialog(
                title=ft.Text("แจ้งเตือน"),
                content=ft.Text("วันนี้คุณบันทึกแล้ว"),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: close_dialog(e))
                ]
            )
            page.dialog.open = True
            page.update()
            return

        # ✅ ถ้าปกติ
        page.snack_bar = ft.SnackBar(ft.Text("Saved to DB ✅"))
        page.snack_bar.open = True
        page.update()

        go("/records")

    def close_dialog(dialog):
        dialog.open = False
        page.update()
    # ---------------- FORM ----------------
    form = ft.Container(
        bgcolor=CARD,
        border_radius=25,
        padding=20,
        content=ft.Column(
            [
                ft.Text("How was your day?", size=22, weight="bold"),
                ft.Text("Overall mood"),
                mood_row,
                ft.Text("Activities & impact"),
                activities_ui,
                ft.Text("Diary"),
                diary,
                ft.ElevatedButton(
                    "Save",
                    bgcolor=PRIMARY,
                    color="white",
                    height=50,
                    on_click=save
                )
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO
        ),
        height=500
    )

# ---------------- WELCOME ----------------
    def show_form(e):
        today = datetime.date.today().isoformat()

        try:
            res = requests.get(f"{API_URL}/records")
            data = res.json()

            # 🔥 เช็คว่ามีของวันนี้แล้วไหม
            already = any(
                r.get("date") == today
                for r in data
            )

            if already:
                dialog = ft.AlertDialog(
                title=ft.Text("Ohhh No!"),
                content=ft.Text("You already logged your mood today. Try again tomorrow!"),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: close_dialog(dialog))
                ]
            )

                page.overlay.append(dialog)   # 🔥 สำคัญมาก
                dialog.open = True
                page.update()
                return

        except:
            pass

        # ✅ ถ้ายังไม่เคยบันทึก
        content_area.content = form
        page.update()
    
    today = datetime.date.today()
    year = today.year
    month = today.month

    mood_by_date = {}
    try:
        res = requests.get(f"{API_URL}/records")
        data = res.json()

        for item in data:
            mood_by_date[item.get("date")] = int(item.get("mood", 0))

    except:
        mood_by_date = {}

    def get_mood_color(mood):
        return {
            1: "#94A3B8",
            2: "#60A5FA",
            3: "#34D399",
            4: "#FBBF24",
            5: "#F87171",
        }.get(mood, "#E5E7EB")

    cal = calendar.monthcalendar(year, month)

    calendar_ui = ft.Container(
        bgcolor="#FFFFFF",
        border_radius=20,
        padding=15,
        content=ft.Column(
            [
                ft.Text(f"{calendar.month_name[month]} {year}", weight="bold"),

                *[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        spacing=2,
                        controls=[
                            ft.Container(
                                width=35,
                                height=35,
                                border_radius=8,
                                alignment=ft.Alignment.CENTER,
                                

                                bgcolor=get_mood_color(
                                    mood_by_date.get(f"{year}-{month:02d}-{day:02d}", 0)
                                ) if day != 0 else None,

                                content=ft.Text(str(day)) if day != 0 else None
                            )
                            for day in week
                        ]
                    )
                    for week in cal
                ]
            ],
            spacing=5
        )
    )
    welcome = ft.Container(
        expand=True,
        padding=20,
        content=ft.Container(
            bgcolor=CARD,
            border_radius=30,
            padding=35,
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.AUTO_GRAPH, size=40, color=PRIMARY),
                    ft.Text(
                    f"{greeting}, {username}",
                    size=26,
                    weight=ft.FontWeight.W_600,
                    color=TEXT
                ),
                    
                    # ใช้ \n เพื่อขึ้นบรรทัดใหม่แทนการใช้ line_height
                    ft.Text(
                        "Recording your feelings every day \nwill help you know yourself better.", 
                        size=15, 
                        color="#555555"
                    ),
                    
                    calendar_ui,

                    ft.Text(
                        "Time to log your feelings for today!", 
                        size=15, 
                        weight="w500", 
                        color=PRIMARY 
                    ),

                    ft.Divider(height=20, color="#EEEEEE"),

                    ft.Container(height=20),

                    ft.ElevatedButton(
                        "Start",
                        width=280,
                        height=55,
                        bgcolor=PRIMARY,
                        color="white",
                        on_click=show_form,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=15),
                        )
                    )
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,  # ✅ สำคัญมาก
                expand=True  
            )
        )
    )
    

    content_area.content = welcome

    return ft.Container(
        expand=True,
        bgcolor=BG,
        padding=20,
        content=content_area
    )