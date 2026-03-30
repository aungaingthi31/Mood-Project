import flet as ft
import requests

PRIMARY = "#A67C52"
CARD = "#FFFFFF"
BG = "#F7F7F7"
BORDER = "#EAEAEA"
TEXT = "#333333"

API_URL = "http://192.168.100.38:8000"


def login_view(page, go):

    page.bgcolor = BG

    username = ft.TextField(
        label="Username",
        border_color=BORDER,
        width=300
    )

    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border_color=BORDER,
        width=300
    )

    message = ft.Text("", color="red")

    # ---------------- LOGIN ----------------
    def login(e):

        if not username.value or not password.value:
            message.value = "Please fill all fields"
            page.update()
            return

        try:
            res = requests.post(
                f"{API_URL}/login",
                json={
                    "username": username.value,
                    "password": password.value
                }
            )

            print("STATUS:", res.status_code)
            print("TEXT:", res.text)

            data = res.json()

            print("DATA:", data)

            if data.get("message") == "success":
                page.user_id = data["user_id"]   # ✅ ถูกทั้งหมด
                page.username = data.get("username", username.value)
                go("/home")
            else:
                message.value = "Username or Password incorrect"

        except Exception as e:
            message.value = str(e)  # 🔥 ให้เห็น error จริง

        page.update()

    # ---------------- CARD ----------------
    def login_card(max_width):

        width = 340 if page.width > 400 else page.width * 0.9

        return ft.Container(
            width=width,
            padding=30,
            bgcolor=CARD,
            border_radius=20,

            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(
                blur_radius=20,
                color="#00000008",
                offset=ft.Offset(0, 6)
            ),

            content=ft.Column(
                [
                    ft.Icon(ft.Icons.PSYCHOLOGY, size=40, color=PRIMARY),

                    ft.Text(
                        "Mood Tracker",
                        size=26,
                        weight="bold",
                        color=TEXT,
                        text_align="center"
                    ),

                    ft.Text(
                        "Welcome back",
                        size=14,
                        color="#888888",
                        text_align="center"
                    ),

                    ft.Container(height=10),

                    username,
                    password,

                    ft.Container(height=5),

                    ft.ElevatedButton(
                        "Login",
                        bgcolor=PRIMARY,
                        color="white",
                        width=width - 40,
                        height=45,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12)
                        ),
                        on_click=login
                    ),

                    message
                ],
                spacing=12,
                horizontal_alignment="center"
            )
        )

    # ---------------- RESPONSIVE ----------------
    return ft.Container(
        expand=True,
       alignment=ft.Alignment.CENTER,  # ✅ แก้ตรงนี้

        content=ft.ResponsiveRow(
            [
                ft.Container(
                    col={"xs": 12, "sm": 8, "md": 6, "lg": 4},
                    content=login_card(page.width)
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
    )