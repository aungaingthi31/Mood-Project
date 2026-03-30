import flet as ft
import requests
from datetime import datetime, timedelta

PRIMARY = "#8B5E3C"
BG = "#F8F5F2"
CARD = "#FFFFFF"
SUBTEXT = "#7A7A7A"

API_URL = "http://192.168.100.38:8000"


def get_mood_color(mood):
    return {
        1: "#94A3B8",
        2: "#60A5FA",
        3: "#34D399",
        4: "#FBBF24",
        5: "#F87171",
    }.get(int(mood), "#E5E7EB")


def analytics_view(page, go):

    # ---------------- FETCH ----------------
    try:
        res = requests.get(f"{API_URL}/records")
        all_data = res.json()

        user_id = getattr(page, "user_id", None)
        if user_id:
            records = [r for r in all_data if r.get("users_id") == user_id]
        else:
            records = all_data

    except:
        records = []

    # ---------------- PROCESS ----------------
    moods = []
    activity_scores = {}
    activity_effect = {}

    for r in records:
        mood = r.get("mood", 0)

        if isinstance(mood, int) and mood > 0:
            moods.append(mood)

        for a in r.get("activities", []):
            name = a["name"]
            score = a["score"]

            activity_scores.setdefault(name, []).append(score)

            # 🔥 ใช้ score + mood
            impact = score * mood

            activity_effect.setdefault(name, []).append(impact)

    # ---------------- CALCULATE ----------------
    total_days = len(records)
    avg_mood = round(sum(moods)/len(moods), 1) if moods else 0

    activity_avg = {
        k: round(sum(v)/len(v), 1)
        for k, v in activity_scores.items()
    }

    activity_effect_avg = {
    k: round(sum(v)/len(v), 2)
    for k, v in activity_effect.items()
}

    if activity_effect_avg:
        best_activity = max(activity_effect_avg, key=activity_effect_avg.get)
        worst_activity = min(activity_effect_avg, key=activity_effect_avg.get)
    else:
        best_activity = "None"
        worst_activity = "None"

    # ---------------- GRAPH (Mon–Sun) ----------------
    date_mood = {r["date"]: r["mood"] for r in records}

    if records:
        last_date = max(datetime.strptime(r["date"], "%Y-%m-%d") for r in records)
    else:
        last_date = datetime.today()

    start_week = last_date - timedelta(days=last_date.weekday())

    graph = []

    MAX_HEIGHT = 120

    for i in range(7):
        day = start_week + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        mood = date_mood.get(day_str)

        if mood:
            bar_height = (mood / 5) * MAX_HEIGHT
            bar = ft.Column(
                [
                    ft.Container(
                        width=18,
                        height=bar_height,
                        bgcolor=get_mood_color(mood),
                        border_radius=10
                    ),
                    ft.Text(day.strftime("%a"), size=10)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END  # 🔥 สำคัญมาก
            )
        else:
            bar = ft.Column(
                [
                    ft.Container(
                        width=18,
                        height=5,
                        bgcolor="#E5E7EB"
                    ),
                    ft.Text(day.strftime("%a"), size=10)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END
            )

        graph.append(bar)

    # ---------------- UI BLOCKS ----------------

    summary = ft.Row(
        [
            ft.Container(
                expand=True,
                bgcolor=CARD,
                padding=20,
                border_radius=20,
                content=ft.Column([
                    ft.Text("Avg Mood", color=SUBTEXT),
                    ft.Text(str(avg_mood), size=22, weight="bold")
                ])
            ),
            ft.Container(
                expand=True,
                bgcolor=CARD,
                padding=20,
                border_radius=20,
                content=ft.Column([
                    ft.Text("Logged Days", color=SUBTEXT),
                    ft.Text(str(total_days), size=22, weight="bold")
                ])
            ),
        ],
        spacing=15
    )

    graph_box = ft.Container(
    bgcolor=CARD,
    padding=20,
    border_radius=20,
    content=ft.Column([
        ft.Text("Mood Trend (Mon–Sun)"),
        
        ft.Container(   # 🔥 ตัวนี้สำคัญ
            height=150,  # กำหนดความสูงกราฟ
            content=ft.Row(
                graph,
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                vertical_alignment=ft.CrossAxisAlignment.END  # 🔥 ดันลงล่าง
            )
        )
    ])
)

    activity_box = ft.Container(
        bgcolor=CARD,
        padding=20,
        border_radius=20,
        content=ft.Column(
            [ft.Text("Activity Scores", weight="bold")] +
            [
                ft.Row(
                    [
                        ft.Text(name),
                        ft.Text(str(score), weight="bold")
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
                for name, score in activity_avg.items()
            ] if activity_avg else [ft.Text("No data")]
        )
    )

    best_box = ft.Container(
        bgcolor="#E8F8F5",
        padding=20,
        border_radius=20,
        content=ft.Column([
            ft.Row(
    [
        ft.Icon(ft.Icons.EMOJI_EVENTS, size=18, color="#10B981"),
        ft.Text("Best Activity", weight="bold")
    ],
    spacing=6
),
            ft.Text(best_activity, size=18, weight="bold"),
        ])
    )

    worst_box = ft.Container(
        bgcolor="#FEE2E2",
        padding=20,
        border_radius=20,
        content=ft.Column([
            ft.Row(
    [
        ft.Icon(ft.Icons.WARNING, size=18, color="#EF4444"),
        ft.Text("Worst Activity", weight="bold")
    ],
    spacing=6
),
            ft.Text(worst_activity, size=18, weight="bold"),
        ])
    )

    # ---------------- MAIN ----------------
    best_worst_row = ft.Row(
    [
        ft.Container(expand=True, content=best_box),
        ft.Container(expand=True, content=worst_box),
        
    ],
    spacing=15
)
    # ---------------- RESPONSIVE CHECK ----------------
    is_mobile = page.width < 600
    is_tablet = page.width < 1000
    # ---------------- RESPONSIVE SECTION ----------------
    if is_mobile:
        responsive_section = ft.Column(
            [
                activity_box,
                ft.Container(expand=True, content=best_box),
                ft.Container(expand=True, content=worst_box)
            ],
            spacing=20
        )

    elif is_tablet:
        responsive_section = ft.Column(
            [
                ft.Container(expand=2, content=activity_box),
                ft.Container(
                    expand=1,
                    content=ft.Row(
                        [
                        ft.Container(expand=True, content=best_box),
                        ft.Container(expand=True, content=worst_box)
                        ],
                        spacing=15
                    )
                )
            ],
            spacing=20
        )

    else:
        responsive_section = ft.Column(
            [
                ft.Container(expand=2, content=activity_box),
                ft.Container(
                    expand=1,
                    content=ft.Row(
                        [
                        ft.Container(expand=True, content=best_box),
                        ft.Container(expand=True, content=worst_box)
                        ],
                        spacing=15
                    )
                )
            ],
            spacing=20
        )

    return ft.Container(
        expand=True,
        bgcolor=BG,
        padding=25,
        content=ft.Column(
            [
                ft.Text("Analytics", size=26, weight="bold"),
                summary,
                graph_box,
                responsive_section
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO
        )
    )