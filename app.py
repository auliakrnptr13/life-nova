import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import bcrypt
import datetime
import json
import os

# Konfigurasi halaman
st.set_page_config(page_title="Life Nova", page_icon="🌸", layout="wide")

# Custom CSS (Pink & Hijau Pastel seperti VitaPilot)
st.markdown("""
<style>
    /* Global */
    .stApp {
        background: linear-gradient(135deg, #FFF5F0 0%, #F0F7F4 100%);
    }
    
    /* Header utama */
    .main-header {
        background: linear-gradient(135deg, #FFB7B2 0%, #B5E3D5 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    
    .main-header h1 {
        color: #5A6E6A;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: #6B8580;
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
        border-left: 4px solid #FFB7B2;
    }
    
    .learn-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    .learn-card .title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #5A6E6A;
        margin-bottom: 0.3rem;
    }
    
    .learn-card .desc {
        font-size: 0.85rem;
        color: #888;
        margin-bottom: 0.8rem;
    }
    
    .learn-card .tag {
        background: #FFD1CD;
        color: #D47B6A;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        display: inline-block;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFF5F0 0%, #F0F7F4 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #5A6E6A !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: #FFB7B2 !important;
    }
    
    /* Tombol */
    .stButton > button {
        background: linear-gradient(135deg, #FFB7B2 0%, #D4A5A0 100%);
        color: #5A6E6A !important;
        border: none !important;
        border-radius: 25px !important;
        font-weight: 600 !important;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(255,183,178,0.4);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #FFD1CD 0%, #D4F0E8 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: #5A6E6A;
        margin: 0;
    }
    
    /* Success message */
    .stSuccess {
        background-color: #D4F0E8;
        color: #2C5F4F;
        border-left-color: #B5E3D5;
    }
    
    /* Progress section */
    .progress-section {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid #FFD1CD;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #C4A4A4;
        font-size: 0.8rem;
        margin-top: 2rem;
    }
    
    /* Welcome banner */
    .welcome-banner {
        background: linear-gradient(135deg, #FFD1CD 0%, #D4F0E8 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
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
    "🌱 Dasar Aktuaria": [
        {"title": "Pengertian Aktuaria", "desc": "Memahami dasar-dasar ilmu aktuaria", "tag": "Pemula"},
        {"title": "Tabel Mortalita", "desc": "Cara membaca dan menggunakan tabel mortalita", "tag": "Pemula"},
        {"title": "Bunga dan Diskonto", "desc": "Konsep nilai waktu uang", "tag": "Pemula"},
    ],
    "📈 Asuransi & Anuitas": [
        {"title": "Asuransi Jiwa", "desc": "Perhitungan premi asuransi jiwa", "tag": "Menengah"},
        {"title": "Anuitas Hidup", "desc": "Menghitung nilai sekarang anuitas", "tag": "Menengah"},
        {"title": "Cadangan Premi", "desc": "Perhitungan cadangan premi", "tag": "Menengah"},
    ],
    "🚀 Lanjutan": [
        {"title": "Model Mortalita", "desc": "Gompertz, Makeham, dan lainnya", "tag": "Lanjutan"},
        {"title": "Dana Pensiun", "desc": "Perencanaan dan perhitungan dana pensiun", "tag": "Lanjutan"},
        {"title": "Manajemen Risiko", "desc": "Enterprise Risk Management", "tag": "Lanjutan"},
    ]
}

# ========== FUNGSI AKTUARIA ==========
@st.cache_data
def generate_mortality_table():
    ages = list(range(101))
    lx = [100000]
    for x in range(1, 101):
        mu = 0.0001 * np.exp(0.08 * (x - 1))
        lx.append(int(lx[-1] * np.exp(-mu)))
    df = pd.DataFrame({'usia': ages, 'lx': lx})
    df['dx'] = df['lx'].diff().fillna(0).abs().astype(int)
    df['qx'] = (df['dx'] / df['lx']).fillna(0).round(6)
    return df

MORTALITY_TABLE = generate_mortality_table()

def calculate_whole_life(usia, bunga, benefit):
    premium = 0
    v = 1 / (1 + bunga)
    for t in range(100 - usia):
        prob_mati = MORTALITY_TABLE[MORTALITY_TABLE['usia'] == usia + t]['qx'].values[0] if usia + t <= 100 else 1
        prob_hidup = 1
        for y in range(t):
            prob_hidup *= (1 - MORTALITY_TABLE[MORTALITY_TABLE['usia'] == usia + y]['qx'].values[0])
        premium += (v ** (t + 1)) * prob_hidup * prob_mati
    return round(premium * benefit, 0)

def calculate_annuity_due(usia, bunga, years, is_lifetime):
    annuity = 1
    v = 1 / (1 + bunga)
    max_term = (100 - usia - 1) if is_lifetime else min(years - 1, 100 - usia - 1)
    for t in range(1, max_term + 1):
        prob_hidup = 1
        for y in range(t):
            prob_hidup *= (1 - MORTALITY_TABLE[MORTALITY_TABLE['usia'] == usia + y]['qx'].values[0])
        annuity += (v ** t) * prob_hidup
    return annuity

def calculate_pension(usia, usia_pensiun, gaji, iuran, return_inv):
    tahun = usia_pensiun - usia
    if tahun <= 0:
        return 0
    iuran_bulanan = gaji * (iuran / 100)
    bunga_bulanan = (1 + return_inv) ** (1/12) - 1
    dana = 0
    for _ in range(tahun * 12):
        dana = dana * (1 + bunga_bulanan) + iuran_bulanan
    return int(dana)

# ========== HALAMAN LOGIN ==========
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None

if not st.session_state.logged_in:
    st.markdown("""
    <div class="main-header">
        <h1>🌸 Life Nova</h1>
        <p>Platform Belajar Aktuaria | Pink & Hijau Pastel</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Registrasi", "🔄 Lupa Password"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input("Email", placeholder="contoh@email.com")
            password = st.text_input("Password", type="password")
            if st.button("🌸 Login Sekarang", use_container_width=True):
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
            st.info("🔧 Hubungi admin untuk reset password.")
    st.stop()

# ========== HALAMAN UTAMA ==========
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3rem;">🌸</div>
        <h3 style="color: #FFB7B2;">Life Nova</h3>
        <p style="font-size: 0.8rem;">Learn Actuary</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"👋 **{st.session_state.user_email}**")
    st.markdown("---")
    
    menu = st.selectbox("📚 Menu", [
        "🏠 Dashboard", "📖 Materi Belajar", "📊 Kalkulator Aktuaria", 
        "📈 Progress Saya", "ℹ️ Tentang"
    ])
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🌸 Life Nova</h1>
    <p>Platform Belajar Aktuaria | {menu}</p>
</div>
""", unsafe_allow_html=True)

# DASHBOARD
if menu == "🏠 Dashboard":
    user_progress = get_user_progress(st.session_state.user_email)
    
    st.markdown(f"""
    <div class="welcome-banner">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0;">Selamat Belajar, {st.session_state.user_email.split('@')[0]}! 👋</h2>
                <p style="margin: 5px 0 0;">Terus semangat untuk jadi aktuaria handal</p>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: bold;">{user_progress}%</div>
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
            <div class="title">🌱 Dasar Aktuaria</div>
            <div class="desc">Dasar-dasar ilmu aktuaria untuk pemula</div>
            <div class="tag">3 Materi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Mulai Dasar →", key="basic"):
            st.session_state.menu = "📖 Materi Belajar"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="learn-card">
            <div class="title">📈 Asuransi & Anuitas</div>
            <div class="desc">Perhitungan asuransi jiwa dan anuitas</div>
            <div class="tag">3 Materi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Mulai Menengah →", key="inter"):
            st.session_state.menu = "📖 Materi Belajar"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="learn-card">
            <div class="title">🚀 Lanjutan</div>
            <div class="desc">Model mortalita dan manajemen risiko</div>
            <div class="tag">3 Materi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Mulai Lanjutan →", key="adv"):
            st.session_state.menu = "📖 Materi Belajar"
            st.rerun()
    
    # Kurva Survival
    st.markdown("---")
    st.markdown("## 📊 Kurva Survival")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=MORTALITY_TABLE['usia'],
        y=MORTALITY_TABLE['lx'],
        mode='lines',
        name='Jumlah Hidup (lx)',
        line=dict(color='#FFB7B2', width=3),
        fill='tozeroy',
        fillcolor='rgba(255,183,178,0.2)'
    ))
    fig.update_layout(
        title="Kurva Survival - Tabel Mortalita",
        height=400,
        plot_bgcolor='rgba(255,245,240,0.5)',
        paper_bgcolor='rgba(255,245,240,0.3)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistik
    st.markdown("## 📊 Statistik Belajar")
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("📚 Total Materi", "9")
    with col_b:
        st.metric("✅ Telah Dipelajari", f"{user_progress // 11}")
    with col_c:
        st.metric("👥 Siswa Aktif", "456")
    with col_d:
        st.metric("⭐ Rating", "4.9/5")

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
                    update_progress(st.session_state.user_email, 
                                  get_user_progress(st.session_state.user_email) + 11)
        st.markdown("---")

# KALKULATOR AKTUARIA
elif menu == "📊 Kalkulator Aktuaria":
    st.subheader("📊 Kalkulator Aktuaria")
    
    tab1, tab2, tab3 = st.tabs(["💰 Asuransi Jiwa", "📈 Anuitas", "🏦 Dana Pensiun"])
    
    with tab1:
        st.markdown("### 💰 Kalkulator Premi Asuransi Jiwa")
        col1, col2 = st.columns(2)
        with col1:
            usia = st.number_input("Usia Peserta", 20, 70, 30)
            bunga = st.number_input("Tingkat Bunga (%)", 1, 15, 5) / 100
        with col2:
            up = st.number_input("Uang Pertanggungan (Rp)", 10_000_000, 1_000_000_000, 100_000_000, step=10_000_000)
            jenis = st.selectbox("Jenis Asuransi", ["Whole Life", "Term Life 10 Tahun"])
        
        if st.button("🌸 Hitung Premi", use_container_width=True):
            if jenis == "Whole Life":
                premi = calculate_whole_life(usia, bunga, up)
            else:
                premi = calculate_whole_life(usia, bunga, up) * 0.7
            st.success(f"✨ Premi: **Rp {premi:,.0f}**")
            st.caption("Perhitungan menggunakan tabel mortalita dan prinsip aktuaria")
    
    with tab2:
        st.markdown("### 📈 Kalkulator Anuitas")
        col1, col2 = st.columns(2)
        with col1:
            usia_an = st.number_input("Usia Peserta", 20, 70, 55)
            bunga_an = st.number_input("Tingkat Bunga (%)", 1, 15, 5) / 100
        with col2:
            jenis_an = st.selectbox("Jenis Anuitas", ["Seumur Hidup", "Berjangka 20 Tahun"])
            pembayaran = st.number_input("Pembayaran per Tahun (Rp)", 10_000_000, 500_000_000, 50_000_000, step=10_000_000)
        
        if st.button("🌸 Hitung Nilai Sekarang", use_container_width=True):
            is_lifetime = (jenis_an == "Seumur Hidup")
            faktor = calculate_annuity_due(usia_an, bunga_an, 20, is_lifetime)
            nilai = faktor * pembayaran
            st.success(f"✨ Nilai Sekarang Anuitas: **Rp {nilai:,.0f}**")
            st.caption(f"Faktor Anuitas: {faktor:.4f}")
    
    with tab3:
        st.markdown("### 🏦 Kalkulator Dana Pensiun")
        col1, col2 = st.columns(2)
        with col1:
            usia_skrg = st.number_input("Usia Sekarang", 20, 50, 30)
            usia_pensiun = st.number_input("Usia Pensiun", 50, 65, 60)
            gaji = st.number_input("Gaji Bulanan (Rp)", 5_000_000, 100_000_000, 10_000_000, step=5_000_000)
        with col2:
            iuran = st.number_input("Persentase Iuran (%)", 1, 20, 5)
            return_inv = st.number_input("Return Investasi (%)", 1, 15, 8) / 100
        
        if st.button("🌸 Hitung Dana Pensiun", use_container_width=True):
            dana = calculate_pension(usia_skrg, usia_pensiun, gaji, iuran, return_inv)
            st.success(f"✨ Dana Pensiun Terkumpul: **Rp {dana:,.0f}**")
            st.caption(f"Periode menabung: {usia_pensiun - usia_skrg} tahun")

# PROGRESS SAYA
elif menu == "📈 Progress Saya":
    st.subheader("📈 Progress Belajar")
    
    progress = get_user_progress(st.session_state.user_email)
    
    st.markdown(f"""
    <div class="progress-section">
        <h4>Total Progress Belajar</h4>
        <div style="background: #FFD1CD; border-radius: 10px; height: 25px;">
            <div style="background: linear-gradient(90deg, #FFB7B2, #B5E3D5); 
                        width: {progress}%; border-radius: 10px; height: 25px;
                        display: flex; align-items: center; justify-content: center;
                        color: #5A6E6A; font-size: 12px; font-weight: bold;">
                {progress}%
            </div>
        </div>
        <p style="margin-top: 10px;"><strong>{progress}%</strong> dari total materi telah selesai</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## ✅ Materi yang Telah Dipelajari")
    
    completed_materials = []
    if progress >= 11:
        completed_materials.append("Pengertian Aktuaria")
    if progress >= 22:
        completed_materials.append("Tabel Mortalita")
    if progress >= 33:
        completed_materials.append("Bunga dan Diskonto")
    
    if completed_materials:
        for item in completed_materials:
            st.markdown(f"- ✅ {item}")
    else:
        st.info("Belum ada materi yang selesai. Mulai belajar dari menu 'Materi Belajar'!")
    
    if st.button("🎯 Update Progress Belajar", use_container_width=True):
        new_progress = min(progress + 11, 100)
        update_progress(st.session_state.user_email, new_progress)
        st.success(f"Progress berhasil diupdate menjadi {new_progress}%!")
        st.rerun()

# TENTANG
else:
    st.subheader("ℹ️ Tentang Life Nova")
    st.markdown("""
    ### 🌸 Life Nova
    
    **Life Nova** adalah platform belajar aktuaria dan asuransi dengan tema **pink dan hijau pastel** yang dirancang untuk membantu kamu memahami konsep-konsep aktuaria dengan mudah dan menyenangkan.
    
    ### ✨ Fitur Lengkap:
    - ✅ **Materi Belajar** - Terstruktur dari dasar hingga lanjutan
    - ✅ **Kalkulator Aktuaria** - Hitung premi asuransi, anuitas, dana pensiun
    - ✅ **Kurva Survival** - Visualisasi tabel mortalita
    - ✅ **Tracking Progress** - Pantau perkembangan belajarmu
    - ✅ **Login & Registrasi** - Simpan progress per user
    
    ### 🎯 Untuk Siapa?
    - Mahasiswa aktuaria
    - Calon aktuaris
    - Praktisi asuransi
    - Siapa pun yang ingin belajar aktuaria
    
    ### 🎨 Tema
    - Pink Pastel (#FFB7B2) - Kehangatan dan perhatian
    - Hijau Pastel (#B5E3D5) - Pertumbuhan dan keseimbangan
    
    ### 📧 Kontak
    - Email: support@lifenova.com
    - GitHub: github.com/lifenova
    
    ---
    **Dibuat dengan 🌸 untuk para pembelajar aktuaria**
    """)

# Footer
st.markdown("""
<div class="footer">
    <p>🌸 Life Nova | Platform Belajar Aktuaria Pink & Hijau Pastel 🌿</p>
    <p>© 2024 Life Nova - Belajar Jadi Aktuaris Handal</p>
</div>
""", unsafe_allow_html=True)
