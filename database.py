import sqlite3
import hashlib
import os

DB_PATH = "lumacta.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nama      TEXT    NOT NULL,
            email     TEXT    NOT NULL UNIQUE,
            username  TEXT    NOT NULL UNIQUE,
            password  TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS riwayat (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            fitur      TEXT    NOT NULL,
            deskripsi  TEXT    NOT NULL,
            hasil      TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(nama: str, email: str, username: str, password: str) -> dict:
    """Daftarkan user baru. Return {'ok': True} atau {'ok': False, 'pesan': '...'}"""
    if len(password) < 6:
        return {"ok": False, "pesan": "Kata sandi minimal 6 karakter."}
    if len(username) < 3:
        return {"ok": False, "pesan": "Username minimal 3 karakter."}
    if "@" not in email:
        return {"ok": False, "pesan": "Format email tidak valid."}

    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (nama, email, username, password) VALUES (?, ?, ?, ?)",
            (nama.strip(), email.strip().lower(), username.strip().lower(), hash_password(password)),
        )
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return {"ok": True, "user_id": user_id, "nama": nama.strip()}
    except sqlite3.IntegrityError as e:
        conn.close()
        if "email" in str(e):
            return {"ok": False, "pesan": "Email sudah digunakan. Coba email lain."}
        if "username" in str(e):
            return {"ok": False, "pesan": "Username sudah dipakai. Coba username lain."}
        return {"ok": False, "pesan": "Terjadi kesalahan. Coba lagi."}


def login_user(email_or_username: str, password: str) -> dict:
    """Login dengan email atau username. Return {'ok': True, 'user': {...}} atau {'ok': False, 'pesan': '...'}"""
    conn = get_connection()
    c = conn.cursor()
    val = email_or_username.strip().lower()
    c.execute(
        "SELECT * FROM users WHERE email = ? OR username = ?", (val, val)
    )
    user = c.fetchone()
    conn.close()

    if user is None:
        return {"ok": False, "pesan": "Akun tidak ditemukan."}
    if user["password"] != hash_password(password):
        return {"ok": False, "pesan": "Kata sandi salah."}

    return {
        "ok": True,
        "user": {
            "id": user["id"],
            "nama": user["nama"],
            "email": user["email"],
            "username": user["username"],
        },
    }


def simpan_riwayat(user_id: int, fitur: str, deskripsi: str, hasil: str):
    """Simpan satu baris riwayat perhitungan."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO riwayat (user_id, fitur, deskripsi, hasil) VALUES (?, ?, ?, ?)",
        (user_id, fitur, deskripsi, hasil),
    )
    conn.commit()
    conn.close()


def ambil_riwayat(user_id: int, limit: int = 10) -> list:
    """Ambil riwayat perhitungan user, terbaru duluan."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM riwayat WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
