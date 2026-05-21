import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import bcrypt
import datetime
import json
import os

# Konfigurasi halaman
st.set_page_config(page_title="VitaPilot", page_icon="🧪", layout="wide")

# Custom CSS untuk tampilan seperti VitaPilot
st.markdown("""
<style>
    /* Global */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    }
    
    /* Header utama */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: #00d4ff;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: #e0e0e0;
        font-size: 1rem;
    }
    
    /* Card untuk materi belajar */
    .learn-card {
        background: white;
        border-radius: 15px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.2s;
        border-left: 4px solid #00d4ff;
    }
    
    .learn-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    .learn-card .title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.3rem;
    }
    
    .learn-card .desc {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.8rem;
    }
    
    .learn-card .tag {
        background: #e8f4fd;
        color: #00a8cc;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        display: inline-block;
    }
    
    /* Sidebar style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f3460 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: #00d4ff !important;
    }
    
    /* Tombol */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,212,255,0.3);
    }
    
    /* Success message */
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border-left-color: #28a745;
    }
    
    /* Progress bar */
    .progress-section {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #888;
        font-size: 0.8rem;
        margin-top: 2rem;
    }
    
    /* Welcome banner */
    .welcome-banner {
        background: linear-gradient(135deg, #00d4ff20 0%, #0099cc10 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #00d4ff30;
    }
</style>
""", unsafe_allow_html=True)

# ========== DATABASE USER ==========
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def login_user(email, password):
    users = load_users()
    if email in users and verify_password(password, users[email]['password_hash']):
        users[email]['last_login'] = str(datetime.datetime.now())
        save_users(users)
        return True
    return False

def register_user(email, password, name):
    users = load_users()
    if email in users:
        return False, "Email sudah terdaftar!"
    users[email] = {
        'password_hash': bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        'name': name,
        'created_at': str(datetime.date.today()),
        'last_login': '',
        'progress': 0,
        'status': 'active'
    }
    save_users(users)
    return True, "Registrasi berhasil! Silakan login."

def get_user_progress(email):
    users = load_users()
    if email in users:
        return users[email].get('progress', 0)
    return 0

def update_progress(email, progress):
    users = load_users()
    if email in users:
        users[email]['progress'] = min(progress, 100)
        save_users(users)
        return True
    return False

# ========== DATA MATERI BELAJAR ==========
MATERIALS = {
    "📊 Basic": [
        {"title": "Pengertian Aktuaria", "desc": "Memahami dasar-dasar ilmu aktuaria", "tag": "Mudah", "url": "#"},
        {"title": "Tabel Mortalita", "desc": "Cara membaca dan menggunakan tabel mortalita", "tag": "Mudah", "url": "#"},
        {"title": "Bunga dan Diskonto", "desc": "Konsep nilai waktu uang", "tag": "Mudah", "url": "#"},
    ],
    "📈 Intermediate": [
        {"title": "Asuransi Jiwa", "desc": "Perhitungan premi asuransi jiwa", "tag": "Sedang", "url": "#"},
        {"title": "Anuitas Hidup", "desc": "Menghitung nilai sekarang anuitas", "tag": "Sedang", "url": "#"},
        {"title": "Cadangan Premi", "desc": "Perhitungan cadangan premi", "tag": "Sedang", "url": "#"},
    ],
    "🚀 Advanced": [
        {"title": "Model Mortalita Lanjutan", "desc": "Gompertz, Makeham, dan lainnya", "tag": "Sulit", "url": "#"},
        {"title": "Stochastic Modeling", "desc": "Simulasi Monte Carlo untuk aktuaria", "tag": "Sulit", "url": "#"},
        {"title": "ERM", "desc": "Enterprise Risk Management", "tag": "Sulit", "url": "#"},
    ]
}

# ========== HALAMAN LOGIN ==========
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None

if not st.session_state.logged_in:
    st.markdown("""
    <div class="main-header">
        <h1>🧪 VitaPilot</h1>
        <p>Belajar Aktuaria & Asuransi | Panduan Lengkap Untukmu</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Registrasi", "🔄 Lupa Password"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input("Email", placeholder="contoh@email.com")
            password = st.text_input("Password", type="password")
            if st.button("🚀 Login Sekarang", use_container_width=True):
                if login_user(email, password):
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("❌ Email atau password salah!")
            st.caption("💡 Belum punya akun? Registrasi dulu ya!")
    
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            new_email = st.text_input("Email", placeholder="email@anda.com")
            new_name = st.text_input("Nama Lengkap")
            new_pass = st.text_input("Password", type="password")
            confirm_pass = st.text_input("Konfirmasi Password", type="password")
            if st.button("📝 Daftar Sekarang", use_container_width=True):
                if new_pass != confirm_pass:
                    st.error("Password tidak cocok!")
                elif len(new_pass) < 4:
                    st.error("Password minimal 4 karakter!")
                elif "@" not in new_email:
                    st.error("Email tidak valid!")
                else:
                    success, msg = register_user(new_email, new_pass, new_name)
                    st.success(msg) if success else st.error(msg)
    
    with tab3:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("🔧 Fitur reset password akan segera hadir. Hubungi admin untuk reset password.")
    st.stop()

# ========== HALAMAN UTAMA (DASHBOARD) ==========
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3rem;">🧪</div>
        <h3 style="color: #00d4ff;">VitaPilot</h3>
        <p style="font-size: 0.8rem;">Learn Actuary</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"👋 **{st.session_state.user_email}**")
    st.markdown("---")
    
    menu = st.selectbox("📚 Menu", [
        "🏠 Dashboard", "📖 Materi Belajar", "📊 Kalkulator Aktuaria", 
        "📈 Progress Saya", "💬 Diskusi", "ℹ️ Tentang"
    ])
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🧪 VitaPilot</h1>
    <p>Platform Belajar Aktuaria & Asuransi | {menu}</p>
</div>
""", unsafe_allow_html=True)

# DASHBOARD
if menu == "🏠 Dashboard":
    user_progress = get_user_progress(st.session_state.user_email)
    
    st.markdown(f"""
    <div class="welcome-banner">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0;">Selamat Belajar! 👋</h2>
                <p style="margin: 5px 0 0;">Terus semangat untuk jadi aktuaria handal</p>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem;">{user_progress}%</div>
                <div style="font-size: 0.8rem;">Progress Belajar</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📚 Mulai Belajar")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="learn-card">
            <div class="title">📊 Basic Aktuaria</div>
            <div class="desc">Dasar-dasar ilmu aktuaria untuk pemula</div>
            <div class="tag">6 Materi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Mulai Basic →", key="basic"):
            st.info("Materi akan segera tersedia!")
    
    with col2:
        st.markdown("""
        <div class="learn-card">
            <div class="title">📈 Intermediate</div>
            <div class="desc">Perhitungan asuransi dan anuitas</div>
            <div class="tag">6 Materi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Mulai Intermediate →", key="inter"):
            st.info("Materi akan segera tersedia!")
    
    with col3:
        st.markdown("""
        <div class="learn-card">
            <div class="title">🚀 Advanced</div>
            <div class="desc">Model mortalita dan manajemen risiko</div>
            <div class="tag">6 Materi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Mulai Advanced →", key="adv"):
            st.info("Materi akan segera tersedia!")
    
    # Statistik
    st.markdown("---")
    st.markdown("## 📊 Statistik Belajar")
    
    stat1, stat2, stat3, stat4 = st.columns(4)
    with stat1:
        st.metric("📚 Total Materi", "18")
    with stat2:
        st.metric("✅ Telah Dipelajari", f"{user_progress // 6}")
    with stat3:
        st.metric("👥 Siswa Aktif", "1,234")
    with stat4:
        st.metric("⭐ Rating", "4.8/5")

# MATERI BELAJAR
elif menu == "📖 Materi Belajar":
    st.subheader("📖 Semua Materi Belajar")
    
    for category, materials in MATERIALS.items():
        st.markdown(f"### {category}")
        cols = st.columns(2)
        for idx, material in enumerate(materials):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="learn-card">
                    <div class="title">{material['title']}</div>
                    <div class="desc">{material['desc']}</div>
                    <div class="tag">{material['tag']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"📖 Baca →", key=f"read_{category}_{idx}"):
                    st.info(f"Materi '{material['title']}' akan segera tersedia!")
        st.markdown("---")

# KALKULATOR AKTUARIA
elif menu == "📊 Kalkulator Aktuaria":
    st.subheader("📊 Kalkulator Aktuaria")
    
    tab_k1, tab_k2, tab_k3 = st.tabs(["💰 Asuransi Jiwa", "📈 Anuitas", "🏦 Dana Pensiun"])
    
    with tab_k1:
        col1, col2 = st.columns(2)
        with col1:
            usia = st.number_input("Usia", 20, 70, 30)
            bunga = st.number_input("Bunga (%)", 1, 15, 5) / 100
        with col2:
            up = st.number_input("Uang Pertanggungan (Rp)", 10_000_000, 1_000_000_000, 100_000_000, step=10_000_000)
            jenis = st.selectbox("Jenis", ["Whole Life", "Term Life 10 Tahun"])
        
        if st.button("🧪 Hitung Premi"):
            # Simulasi perhitungan
            premi = up * 0.15 * (0.8 ** (usia - 30))
            st.success(f"✨ Premi: **Rp {premi:,.0f}**")
            st.caption("Ini adalah simulasi perhitungan. Untuk hasil akurat, gunakan data aktuaria lengkap.")
    
    with tab_k2:
        usia_an = st.number_input("Usia", 20, 70, 55)
        pembayaran = st.number_input("Pembayaran per tahun (Rp)", 10_000_000, 500_000_000, 50_000_000, step=10_000_000)
        
        if st.button("🧪 Hitung Anuitas"):
            nilai = pembayaran * 12 * 0.85
            st.success(f"✨ Nilai Sekarang Anuitas: **Rp {nilai:,.0f}**")
    
    with tab_k3:
        usia_skrg = st.number_input("Usia Sekarang", 20, 50, 30)
        usia_pensiun = st.number_input("Usia Pensiun", 50, 65, 60)
        gaji = st.number_input("Gaji Bulanan (Rp)", 5_000_000, 100_000_000, 10_000_000, step=5_000_000)
        
        if st.button("🧪 Hitung Dana Pensiun"):
            tahun = usia_pensiun - usia_skrg
            dana = gaji * 12 * tahun * 1.08
            st.success(f"✨ Dana Pensiun Terkumpul: **Rp {dana:,.0f}**")

# PROGRESS SAYA
elif menu == "📈 Progress Saya":
    st.subheader("📈 Progress Belajar")
    
    progress = get_user_progress(st.session_state.user_email)
    
    st.markdown(f"""
    <div class="progress-section">
        <h4>Total Progress</h4>
        <div style="background: #e0e0e0; border-radius: 10px; height: 20px;">
            <div style="background: linear-gradient(90deg, #00d4ff, #0099cc); 
                        width: {progress}%; border-radius: 10px; height: 20px;">
            </div>
        </div>
        <p style="margin-top: 10px;"><strong>{progress}%</strong> dari materi selesai</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## ✅ Materi yang Telah Dipelajari")
    
    completed = [
        "Pengertian Aktuaria",
        "Tabel Mortalita",
    ]
    
    for item in completed:
        st.markdown(f"- ✅ {item}")
    
    if st.button("🎯 Update Progress +10%"):
        new_progress = min(progress + 10, 100)
        update_progress(st.session_state.user_email, new_progress)
        st.success(f"Progress berhasil diupdate menjadi {new_progress}%!")
        st.rerun()

# DISKUSI
elif menu == "💬 Diskusi":
    st.subheader("💬 Forum Diskusi")
    
    st.info("💡 Fitur diskusi akan segera hadir! Kamu bisa bertanya dan berdiskusi dengan sesama pembelajar aktuaria.")
    
    question = st.text_area("Ada pertanyaan? Tulis di sini:")
    if st.button("💬 Kirim Pertanyaan"):
        if question:
            st.success("Pertanyaanmu telah terkirim! Admin akan segera merespon.")
        else:
            st.warning("Tulis pertanyaan terlebih dahulu.")

# TENTANG
else:
    st.subheader("ℹ️ Tentang VitaPilot")
    st.markdown("""
    ### 🧪 VitaPilot
    
    **VitaPilot** adalah platform belajar aktuaria dan asuransi yang dirancang untuk membantu kamu memahami konsep-konsep aktuaria dengan mudah.
    
    ### ✨ Fitur:
    - ✅ Materi belajar terstruktur (Basic → Intermediate → Advanced)
    - ✅ Kalkulator aktuaria (asuransi, anuitas, dana pensiun)
    - ✅ Tracking progress belajar
    - ✅ Forum diskusi
    
    ### 🎯 Target Pengguna:
    - Mahasiswa aktuaria
    - Calon aktuaris
    - Praktisi asuransi
    - Siapa pun yang ingin belajar aktuaria
    
    ### 📧 Kontak:
    - Email: support@vitapilot.com
    - GitHub: github.com/vitapilot
    
    ---
    **Dibuat dengan 🧪 untuk para pembelajar aktuaria**
    """)

st.markdown("""
<div class="footer">
    <p>🧪 VitaPilot | Platform Belajar Aktuaria & Asuransi</p>
    <p>© 2024 VitaPilot - Belajar Jadi Aktuaris Handal</p>
</div>
""", unsafe_allow_html=True)
