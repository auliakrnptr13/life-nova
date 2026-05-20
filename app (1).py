
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import bcrypt
import datetime
import json
import os

st.set_page_config(page_title="Life Nova", page_icon="🌸", layout="wide")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #FFB7B2 0%, #B5E3D5 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #FFD1CD 0%, #D4F0E8 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
    }
    .stButton > button {
        background: linear-gradient(135deg, #FFB7B2 0%, #B5E3D5 100%);
        border: none;
        border-radius: 25px;
    }
</style>
""", unsafe_allow_html=True)

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)

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
        'status': 'active'
    }
    save_users(users)
    return True, "Registrasi berhasil! Silakan login."

def reset_password(email, new_password):
    users = load_users()
    if email in users:
        users[email]['password_hash'] = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        save_users(users)
        return True, "Password berhasil direset!"
    return False, "Email tidak ditemukan!"

def get_all_users():
    return load_users()

def is_admin(email):
    return email == "admin@lifenova.com"

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

def get_qx(usia):
    return MORTALITY_TABLE[MORTALITY_TABLE['usia'] == usia]['qx'].values[0] if usia <= 100 else 1

def get_npx(usia, n):
    if usia + n > 100:
        return 0
    prob = 1
    for t in range(n):
        prob *= (1 - get_qx(usia + t))
    return prob

def get_tpx_qx_t(usia, t):
    if usia + t + 1 > 100:
        return 0
    return get_npx(usia, t) * get_qx(usia + t)

def calculate_whole_life(usia, bunga, benefit):
    premium = 0
    v = 1 / (1 + bunga)
    for t in range(100 - usia):
        premium += (v ** (t + 1)) * get_tpx_qx_t(usia, t)
    return round(premium * benefit, 0)

def calculate_term_life(usia, bunga, term, benefit):
    premium = 0
    v = 1 / (1 + bunga)
    for t in range(term):
        premium += (v ** (t + 1)) * get_tpx_qx_t(usia, t)
    return round(premium * benefit, 0)

def calculate_endowment(usia, bunga, term, benefit):
    term_premium = calculate_term_life(usia, bunga, term, benefit)
    survival = get_npx(usia, term) * (1 / (1 + bunga)) ** term * benefit
    return round(term_premium + survival, 0)

def calculate_annuity(usia, bunga, term, is_lifetime, payment):
    annuity = 1
    v = 1 / (1 + bunga)
    max_term = (100 - usia - 1) if is_lifetime else min(term - 1, 100 - usia - 1)
    for t in range(1, max_term + 1):
        annuity += (v ** t) * get_npx(usia, t)
    return round(annuity * payment, 0)

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

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None

if not st.session_state.logged_in:
    st.markdown("""
    <div class="main-header">
        <h1>🌸 Life Nova</h1>
        <p>Aplikasi Aktuaria | Login dengan Email</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Registrasi", "🔄 Lupa Password"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input("Email", placeholder="contoh@email.com")
            password = st.text_input("Password", type="password")
            if st.button("🌸 Login", use_container_width=True):
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
            if st.button("📝 Daftar", use_container_width=True):
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
            forgot_email = st.text_input("Email Anda")
            new_password = st.text_input("Password Baru", type="password")
            if st.button("🔄 Reset Password", use_container_width=True):
                success, msg = reset_password(forgot_email, new_password)
                st.success(msg) if success else st.error(msg)
    st.stop()

with st.sidebar:
    st.markdown("<h2 style='text-align:center'>🌸 Life Nova</h2>", unsafe_allow_html=True)
    st.markdown(f"👋 Halo, **{st.session_state.user_email}**!")
    st.markdown("---")
    
    menu_options = ["🏠 Dashboard", "💰 Asuransi Jiwa", "📈 Anuitas", "🏦 Dana Pensiun", "ℹ️ Tentang"]
    
    if is_admin(st.session_state.user_email):
        menu_options.append("👥 Data User")
    
    menu = st.selectbox("Menu", menu_options)
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

st.markdown(f"""
<div class="main-header">
    <h1>🌸 Life Nova</h1>
    <p>{menu} | {st.session_state.user_email}</p>
</div>
""", unsafe_allow_html=True)

if menu == "🏠 Dashboard":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h2>{get_qx(60)*100:.1f}%</h2><p>Prob. Kematian (60th)</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h2>{get_npx(30,30)*100:.1f}%</h2><p>Prob. Hidup 30→60th</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h2>8%</h2><p>Return Investasi</p></div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=MORTALITY_TABLE['usia'], y=MORTALITY_TABLE['lx'], 
                              mode='lines', name='Kurva Survival',
                              line=dict(color='#FFB7B2', width=3), fill='tozeroy'))
    fig.update_layout(title="Kurva Survival - Tabel Mortalita", height=450)
    st.plotly_chart(fig, use_container_width=True)

elif menu == "💰 Asuransi Jiwa":
    st.subheader("💰 Kalkulator Premi Asuransi")
    col1, col2 = st.columns(2)
    with col1:
        jenis = st.selectbox("Jenis Asuransi", ["Whole Life", "Term Life", "Endowment"])
        usia = st.number_input("Usia Peserta", 0, 90, 30)
        bunga = st.number_input("Tingkat Bunga (%)", 0.0, 15.0, 5.0) / 100
    with col2:
        benefit = st.number_input("Uang Pertanggungan (Rp)", 1000000, 1000000000, 100000000, step=10000000)
        if jenis != "Whole Life":
            jangka = st.number_input("Jangka Waktu (tahun)", 1, 30, 10)
    if st.button("🌸 Hitung Premi", use_container_width=True):
        if jenis == "Whole Life":
            premi = calculate_whole_life(usia, bunga, benefit)
        elif jenis == "Term Life":
            premi = calculate_term_life(usia, bunga, jangka, benefit)
        else:
            premi = calculate_endowment(usia, bunga, jangka, benefit)
        st.success(f"### ✨ Premi: **Rp {premi:,.0f}**")

elif menu == "📈 Anuitas":
    st.subheader("📈 Kalkulator Anuitas")
    col1, col2 = st.columns(2)
    with col1:
        jenis = st.selectbox("Jenis Anuitas", ["Berjangka", "Seumur Hidup"])
        usia = st.number_input("Usia Peserta", 0, 90, 55)
        bunga = st.number_input("Tingkat Bunga (%)", 0.0, 15.0, 5.0) / 100
    with col2:
        if jenis == "Berjangka":
            jangka = st.number_input("Jangka Waktu (tahun)", 1, 40, 20)
        pembayaran = st.number_input("Pembayaran per Tahun (Rp)", 1000000, 500000000, 50000000, step=5000000)
    if st.button("🌸 Hitung Nilai Sekarang", use_container_width=True):
        is_lifetime = (jenis == "Seumur Hidup")
        jangka_val = jangka if not is_lifetime else 0
        nilai = calculate_annuity(usia, bunga, jangka_val, is_lifetime, pembayaran)
        st.success(f"### ✨ Nilai Sekarang: **Rp {nilai:,.0f}**")

elif menu == "🏦 Dana Pensiun":
    st.subheader("🏦 Perencanaan Dana Pensiun")
    col1, col2 = st.columns(2)
    with col1:
        usia_skrg = st.number_input("Usia Sekarang", 20, 60, 30)
        usia_pensiun = st.number_input("Usia Pensiun", usia_skrg+1, 70, 60)
        gaji = st.number_input("Gaji Bulanan (Rp)", 1000000, 100000000, 10000000, step=1000000)
    with col2:
        iuran = st.number_input("Iuran (%)", 1, 30, 5)
        return_inv = st.number_input("Return Investasi (%)", 1, 20, 8) / 100
    if st.button("🌸 Hitung Dana Pensiun", use_container_width=True):
        dana = calculate_pension(usia_skrg, usia_pensiun, gaji, iuran, return_inv)
        st.metric("💰 Total Dana Terkumpul", f"Rp {dana:,.0f}")

elif menu == "👥 Data User":
    st.subheader("👥 Data Seluruh User")
    st.info("🔒 Halaman ini hanya bisa dilihat oleh ADMIN")
    
    users = get_all_users()
    if users:
        data = []
        for email, info in users.items():
            data.append({
                'Email': email,
                'Nama': info.get('name', '-'),
                'Tanggal Daftar': info.get('created_at', '-'),
                'Terakhir Login': info.get('last_login', '-'),
                'Status': info.get('status', 'active')
            })
        df_users = pd.DataFrame(data)
        st.dataframe(df_users, use_container_width=True)
        
        csv = df_users.to_csv(index=False)
        st.download_button(
            label="📥 Download Data User (CSV)",
            data=csv,
            file_name=f"users_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Belum ada user yang terdaftar")

else:
    st.markdown("""
    ### 🌸 Life Nova - Aplikasi Aktuaria
    
    **✨ Fitur Lengkap:**
    - ✅ Login dengan EMAIL
    - ✅ Registrasi user baru
    - ✅ Reset password
    - ✅ Asuransi Whole Life, Term Life, Endowment
    - ✅ Anuitas Berjangka & Seumur Hidup
    - ✅ Dana Pensiun
    - ✅ Kurva Survival
    
    **👑 Cara Menjadi Admin:**
    - Registrasi dengan email: `admin@lifenova.com`
    - Setelah login, kamu akan melihat menu "Data User"
    
    **🔒 Data User:**
    - Tersimpan di file JSON dalam aplikasi
    - Hanya admin yang bisa melihat data user
    """)
