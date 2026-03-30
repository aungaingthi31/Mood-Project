from fastapi import FastAPI
import pymysql

from pydantic import BaseModel
from typing import List

app = FastAPI()

# =========================
# 🔌 DB CONNECTION (แก้ให้เสถียร + debug ได้)
# =========================

def get_connection():
    try:
        return pymysql.connect(
            host="127.0.0.1",   # 🔥 แก้จาก 192.168 → localhost (ถ้า DB อยู่เครื่องเดียวกัน)
            user="root",
            password="P@ssword",
            database="mood",
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print("DB CONNECTION ERROR:", e)
        raise e


# =========================
# 🧠 MODELS
# =========================

class Activity(BaseModel):
    activity_id: int
    score: int

class Record(BaseModel):
    users_id: int
    date: str
    mood: int
    diary: str
    activities: List[Activity]

class LoginData(BaseModel):
    username: str
    password: str

class UpdateRecord(BaseModel):
    mood: int
    diary: str


# =========================
# 🔐 LOGIN (เพิ่ม try-except)
# =========================

@app.post("/login")
def login(data: LoginData):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (data.username, data.password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            return {
                "message": "success",
                "user_id": user["users_id"]
            }
        else:
            return {"error": "invalid"}

    except Exception as e:
        print("LOGIN ERROR:", e)
        return {"error": str(e)}


# =========================
# 📦 RECORDS
# =========================

@app.get("/records")
def get_records():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                r.records_id,
                r.users_id,
                r.date,
                r.mood,
                r.diary,
                a.activity_name,
                ra.score
            FROM records r
            LEFT JOIN record_activity ra ON r.records_id = ra.records_id
            LEFT JOIN activity a ON ra.activity_id = a.activity_id
            ORDER BY r.date DESC
        """)

        rows = cursor.fetchall()

        records_dict = {}

        for row in rows:
            rid = row["records_id"]

            if rid not in records_dict:
                records_dict[rid] = {
                    "records_id": rid,
                    "users_id": row["users_id"],
                    "date": row["date"],
                    "mood": row["mood"],
                    "diary": row["diary"],
                    "activities": []
                }

            if row["activity_name"]:
                records_dict[rid]["activities"].append({
                    "name": row["activity_name"],
                    "score": row["score"]
                })

        conn.close()
        return list(records_dict.values())

    except Exception as e:
        print("GET RECORDS ERROR:", e)
        return {"error": str(e)}


@app.get("/records/{records_id}")
def get_record(records_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM records WHERE records_id=%s", (records_id,))
        data = cursor.fetchone()

        conn.close()
        return data

    except Exception as e:
        print("GET ONE ERROR:", e)
        return {"error": str(e)}


@app.post("/records")
def create_record(data: Record):
    try:
        data = data.dict()

        conn = get_connection()
        cursor = conn.cursor()

        # 🔥 CHECK DUPLICATE
        cursor.execute(
            "SELECT records_id FROM records WHERE users_id=%s AND date=%s",
            (data["users_id"], data["date"])
        )
        existing = cursor.fetchone()

        if existing:
            return {"error": "You already recorded today"}

        # INSERT
        cursor.execute(
            "INSERT INTO records (users_id, date, mood, diary) VALUES (%s, %s, %s, %s)",
            (data["users_id"], data["date"], data["mood"], data["diary"])
        )
        records_id = cursor.lastrowid

        # insert activities
        for a in data["activities"]:
            cursor.execute(
                "INSERT INTO record_activity (records_id, activity_id, score) VALUES (%s, %s, %s)",
                (records_id, a["activity_id"], a["score"])
            )

        conn.commit()
        conn.close()

        return {"message": "created", "records_id": records_id}

    except Exception as e:
        print("CREATE ERROR:", e)
        return {"error": str(e)}


@app.put("/records/{records_id}")
def update_record(records_id: int, data: UpdateRecord):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE records SET mood=%s, diary=%s WHERE records_id=%s",
            (data.mood, data.diary, records_id)
        )

        conn.commit()
        conn.close()

        return {"message": "updated"}

    except Exception as e:
        print("UPDATE ERROR:", e)
        return {"error": str(e)}


@app.delete("/records/{records_id}")
def delete_record(records_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM record_activity WHERE records_id=%s", (records_id,))
        cursor.execute("DELETE FROM records WHERE records_id=%s", (records_id,))

        conn.commit()
        conn.close()

        return {"message": "deleted"}

    except Exception as e:
        print("DELETE ERROR:", e)
        return {"error": str(e)}


# =========================
# 🎯 ACTIVITIES
# =========================

@app.get("/activities")
def get_activities():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM activity")
        data = cursor.fetchall()

        conn.close()
        return data

    except Exception as e:
        print("ACTIVITY ERROR:", e)
        return {"error": str(e)}


# =========================
# 📊 ANALYTICS
# =========================

@app.get("/analytics")
def analytics():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT ROUND(AVG(mood),1) as avg_mood FROM records")
        avg = cursor.fetchone()["avg_mood"]

        cursor.execute("""
            SELECT a.activity_name, COUNT(*) as total
            FROM record_activity ra
            JOIN activity a ON ra.activity_id = a.activity_id
            GROUP BY a.activity_name
            ORDER BY total DESC
            LIMIT 1
        """)
        best = cursor.fetchone()

        conn.close()

        return {
            "avg_mood": avg,
            "best_activity": best
        }

    except Exception as e:
        print("ANALYTICS ERROR:", e)
        return {"error": str(e)}