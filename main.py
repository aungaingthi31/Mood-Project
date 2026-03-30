import flet as ft

from login import login_view
from home import home_view
from diary import diary_view
from analytics import analytics_view
from records import records_view


def main(page: ft.Page):

    PRIMARY = "#A67C52"

    page.on_resize = lambda e: page.update()

    page.title = "Mood Tracker"
    page.bgcolor = "#F5EFE6"
    page.window_resizable = True

    content_area = ft.Container(expand=True)

    # ---------------- NAV BUTTON ----------------
    def nav_button(icon, route):

        is_active = (page.route == route)

        def handle_click(e):
            go(route)

        return ft.Container(
            padding=10,
            border_radius=15,
            bgcolor="#F1EEE9" if is_active else None,
            on_click=handle_click,
            content=ft.Icon(
                icon,
                size=26,
                color=PRIMARY if is_active else "#9CA3AF"
            )
        )

    # ---------------- BUILD NAV ----------------
    def build_nav():
        return ft.Container(
            bgcolor="#FFFFFF",
            padding=10,
            content=ft.Row(
                [
                    nav_button(ft.Icons.HOME, "/home"),
                    nav_button(ft.Icons.LIST_ALT, "/records"),
                    nav_button(ft.Icons.INSIGHTS, "/analytics"),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND
            )
        )

    # ---------------- ROUTING ----------------
    def go(route):
        page.route = route

        if route == "/":
            content_area.content = login_view(page, go)

        elif route == "/home":
            content_area.content = home_view(page, go)

        elif route == "/diary":
            content_area.content = diary_view(page, go)

        elif route == "/analytics":
            content_area.content = analytics_view(page, go)

        elif route == "/records":
            content_area.content = records_view(page, go)

        # rebuild nav ให้ active ทำงาน
        if route == "/":
            layout.controls[1] = ft.Container()  # ❌ ซ่อน nav
        else:
            layout.controls[1] = build_nav()     # ✅ แสดง nav

        page.update()

    # ---------------- LAYOUT ----------------
    layout = ft.Column(
        [
            content_area,
            build_nav()
        ],
        expand=True
    )

    page.add(layout)

    go("/")


if __name__ == "__main__":
    ft.app(
        target=main,
         view=ft.AppView.WEB_BROWSER,
         port=8500
    )