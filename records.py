import flet as ft
import requests

API_URL = "http://192.168.100.38:8000"

PRIMARY = "#8B5E3C"
BG = "#F8F5F2"
CARD = "#FFFFFF"
TEXT = "#2B2B2B"
SUBTEXT = "#7A7A7A"
BORDER = "#EAEAEA"


def records_view(page, go):

    # ---------------- DELETE ----------------
    def confirm_delete(item):
        def do_delete(e):
            try:
                requests.delete(f"{API_URL}/records/{item['records_id']}")
            except:
                pass

            dialog.open = False
            page.update()
            go("/records")  # reload ใหม่

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete this record?"),
            content=ft.Text("This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, "open", False) or page.update()),
                ft.ElevatedButton("Delete", bgcolor="red", color="white", on_click=do_delete),
            ],
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ---------------- EDIT ----------------
    def open_edit_dialog(item):

        diary_field = ft.TextField(
            value=item.get("diary", ""),
            multiline=True,
            min_lines=3
        )

        def save_edit(e):
            try:
                requests.put(
                    f"{API_URL}/records/{item['records_id']}",
                    json={
                        "mood": item["mood"],  # ต้องส่งด้วย
                        "diary": diary_field.value
                    }
                )
            except:
                pass

            dialog.open = False
            page.update()
            go("/records")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Diary"),
            content=diary_field,
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, "open", False) or page.update()),
                ft.ElevatedButton("Save", bgcolor=PRIMARY, color="white", on_click=save_edit),
            ],
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ---------------- COLORS & HELPERS ----------------
    def get_mood_color(mood):
        return {
            1: "#94A3B8",
            2: "#60A5FA",
            3: "#34D399",
            4: "#FBBF24",
            5: "#F87171",
        }.get(mood, "#E5E7EB")

    # ---------------- CARD ----------------
    def record_card(item):
        mood_raw = item.get("mood")
        mood = int(mood_raw) if str(mood_raw).isdigit() else 0
        
        # สีตามมู้ด (ใช้เฉพาะแถบข้างและไอคอน)
        accent_color = get_mood_color(mood)
        
        mood_icon = {
            1: ft.Icons.SENTIMENT_VERY_DISSATISFIED,
            2: ft.Icons.SENTIMENT_DISSATISFIED,
            3: ft.Icons.SENTIMENT_NEUTRAL,
            4: ft.Icons.SENTIMENT_SATISFIED,
            5: ft.Icons.SENTIMENT_VERY_SATISFIED,
        }.get(mood, ft.Icons.HELP_OUTLINE)

        activities_list = item.get("activities", [])
        activity_widgets = []

        if activities_list:
            for a in activities_list:
                activity_widgets.append(
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(a.get("name", ""), size=13),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=8,
                                bgcolor="#F5F5F5", # ใช้สีเทาอ่อนนิ่งๆ
                                content=ft.Text(
                                    str(a.get("score", "-")),
                                    size=12,
                                    weight="bold",
                                    color=TEXT # ใช้สี Text ปกติ ไม่ให้ดึงสายตาเกินไป
                                )
                            )
                        ]
                    )
                )
        else:
            activity_widgets.append(ft.Text("No activities", size=12, color="#AAAAAA"))

        return ft.Container(
            border_radius=20,
            bgcolor=CARD,
            # ✅ ลบ border ออกแล้ว และใช้เงาสีเทาอ่อนมาตรฐาน
            shadow=ft.BoxShadow(
                blur_radius=15,
                color="#0000000D", # เงาสีดำจางมากๆ (ประมาณ 5%) ดูสะอาดตา
                offset=ft.Offset(0, 4)
            ),
            content=ft.Row(
                spacing=0,
                controls=[
                    # 🟩 แถบสีด้านซ้าย (จุดเดียวที่โชว์สีมู้ดชัดเจน)
                    ft.Container(
                        width=10,
                        bgcolor=accent_color,
                        border_radius=ft.border_radius.only(
                            top_left=20,
                            bottom_left=20
                        )
                    ),

                    # 📦 CONTENT
                    ft.Container(
                        expand=True,
                        padding=20,
                        content=ft.Column(
                            spacing=14,
                            controls=[
                                # 📅 DATE & MOOD ICON
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text("Date", size=11, color=SUBTEXT),
                                                ft.Text(item.get("date", "-"), size=14, weight="bold", color=PRIMARY)
                                            ]
                                        ),
                                        # ไอคอนสีตามมู้ด (ช่วยให้การ์ดไม่ดูจืดเกินไป)
                                        ft.Icon(mood_icon, color=accent_color, size=26)
                                    ]
                                ),

                                # 📊 ACTIVITIES
                                ft.Column(
                                    spacing=6,
                                    controls=[
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.BAR_CHART, size=16, color=SUBTEXT),
                                                ft.Text("Activity Scores", size=11, color=SUBTEXT)
                                            ],
                                            spacing=6
                                        ),
                                        *activity_widgets
                                    ]
                                ),

                                # 📝 DIARY
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text("Diary", size=11, color=SUBTEXT),
                                        ft.Text(
                                            item.get("diary", "-"),
                                            size=14,
                                            color=TEXT,
                                            max_lines=3,
                                            overflow=ft.TextOverflow.ELLIPSIS
                                        )
                                    ]
                                ),

                                ft.Divider(height=10, color="#F1F1F1"),

                                # ACTION
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.END,
                                    controls=[
                                        ft.IconButton(
                                            ft.Icons.EDIT_OUTLINED,
                                            icon_color=SUBTEXT,
                                            on_click=lambda e: open_edit_dialog(item)
                                        ),
                                        ft.IconButton(
                                            ft.Icons.DELETE_OUTLINE,
                                            icon_color="#E57373",
                                            on_click=lambda e: confirm_delete(item)
                                        ),
                                    ]
                                )
                            ]
                        )
                    )
                ]
            )
        )

    # ---------------- SORT ----------------
    records_data = []
    try:
        res = requests.get(f"{API_URL}/records")
        records_data = res.json()
    except:
        records_data = []

    sorted_data = sorted(
        records_data,
        key=lambda x: x.get("date", ""),
        reverse=True
    )

    # ---------------- EMPTY ----------------
    if not sorted_data:
        content = ft.Column(
            [
                ft.Icon(ft.Icons.INSERT_DRIVE_FILE_OUTLINED, size=50, color="#CCCCCC"),
                ft.Text("No records yet", size=18, color=SUBTEXT),
                ft.Text("Start tracking your mood today", size=14, color="#AAAAAA")
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
    else:
        content = ft.Column(
            [record_card(item) for item in sorted_data],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    return ft.Container(
        expand=True,
        bgcolor=BG,
        padding=20,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text("My Records", size=26, weight=ft.FontWeight.W_600, color=TEXT),
                content,
            ]
        )
    )