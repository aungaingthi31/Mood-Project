import flet as ft
import requests
import datetime

PRIMARY = "#8B5E3C"
BG = "#F8F5F2"
CARD = "#FFFFFF"
BORDER = "#EAEAEA"
TEXT = "#333333"

API_URL = "http://192.168.100.38:8000"


def diary_view(page, go):

    page.bgcolor = BG

    diary = ft.TextField(
        multiline=True,
        min_lines=8,
        max_lines=15,
        height=200,  # ✅ คงดีไซน์เดิม
        border_radius=12,
        hint_text="How was your day today?",
        border_color=BORDER,
    )

    message = ft.Text("", color="red")

    # ---------------- SAVE ----------------
    def save(e):

        if not diary.value:
            message.value = "Please write something"
            page.update()
            return

        data = {
            "users_id": 1,
            "date": datetime.date.today().isoformat(),
            "mood": 3,
            "diary": diary.value,
            "activities": []
        }

        try:
            requests.post(f"{API_URL}/records", json=data)
            go("/records")
        except:
            message.value = "Error saving data"

        page.update()

    # ---------------- CARD ----------------
    card = ft.Container(
        padding=25,
        bgcolor=CARD,
        border_radius=20,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(
            blur_radius=15,
            color="#00000010",
            offset=ft.Offset(0, 4)
        ),
        content=ft.Column(
            [
                ft.Text(
                    "Diary",
                    size=26,
                    weight="bold",
                    color=PRIMARY
                ),

                diary,

                ft.ElevatedButton(
                    "Save",
                    bgcolor=PRIMARY,
                    color="white",
                    height=45,
                    expand=True,   # ✅ แทน width เดิม
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12)
                    ),
                    on_click=save
                ),

                message
            ],
            spacing=15,
        )
    )

    # ---------------- RESPONSIVE ----------------
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=ft.ResponsiveRow(
            [
                ft.Container(
                    col={
                        "xs": 12,   # 📱 เต็มจอ
                        "sm": 10,
                        "md": 6,
                        "lg": 4
                    },
                    content=card
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )