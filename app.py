# LIFE NOVA - VERSI LENGKAP (SUDAH DIKOREKSI)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import bcrypt
import datetime
import json
import os

# ========== KONFIGURASI HALAMAN ==========
st.set_page_config(page_title="Life Nova", page_icon="🌿", layout="wide")

# ========== WARNA (seperti Lumacta) ==========
st.markdown("""
<style>
    /* Brand colors dari Lumacta */
    :root {
        --pink-dark:   #993556;
        --pink-mid:    #D4537E;
        --pink-light:  #FBEAF0;
        --pink-border: #ED93B1;
        --green-dark:  #3B6D11;
        --green-mid:   #639922;
        --green-light: #EAF3DE;
        --green-border:#97C459;
    }
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, var(--pink-dark) 0%, var(--green-dark) 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: var(--green-light);
        margin-top: 0.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, var(--pink-light) 0%, var(--green-light) 100%);
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid var(--green-border);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .metric-card h2 {
        color: var(--pink-dark);
        margin: 0;
        font-size: 1.8rem;
    }
    .metric-card p {
        color: var(--green-dark);
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    .metric-card small {
        color: #888;
        font-size: 0.7rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--pink-dark) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background: var(--pink-mid) !important;
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--green-light) 0%, white 100%);
    }
    [data-testid="stSidebar"] h2 {
        color: var(--green-dark);
    }
    
    /* Success/Info/Warning */
    .stSuccess {
        background-color: var(--green-light);
        color: var(--green-dark);
        border-left-color: var(--green-mid);
    }
    .stInfo {
        background-color: var(--pink-light);
        color: var(--pink-dark);
        border-left-color: var(--pink-mid);
    }
    .stError {
        background-color: #FFE4E4;
        color: #c0392b;
        border-left-color: #e74c3c;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--green-light);
        border-radius: 10px;
        color: var(--green-dark);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--pink-dark);
        font-size: 0.8rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--pink-dark);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ========== DATABASE USER (file JSON) ==========
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

# ========== TABEL MORTALITA ==========
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
    df['px'] = (1 - df['qx']).round(6)
    return df

MORTALITY_TABLE = generate_mortality_table()

def get_qx(usia):
    if 0 <= usia <= 100:
        return MORTALITY_TABLE[MORTALITY_TABLE['usia'] == usia]['qx'].values[0]
    return 1

def get_px(usia):
    return 1 - get_qx(usia)

def get_npx(usia, n):
    if usia + n > 100:
        return 0
    prob = 1
    for t in range(n):
        prob *= get_px(usia + t)
    return prob

def get_tpx_qx_t(usia, t):
    if usia + t + 1 > 100:
        return 0
    return get_npx(usia, t) * get_qx(usia + t)

# ========== FUNGSI AKTUARIA ==========
def calculate_annuity_due(usia, bunga, n, is_lifetime=False):
    max_age = 100
    annuity = 1
    v = 1 / (1 + bunga)
    max_term = (max_age - usia - 1) if is_lifetime else min(n - 1, max_age - usia - 1)
    for t in range(1, max_term + 1):
        prob_hidup = get_npx(usia, t)
        annuity += (v ** t) * prob_hidup
    return round(annuity, 6)

def calculate_whole_life(usia, bunga, benefit=1):
    premium = 0
    v = 1 / (1 + bunga)
    for t in range(100 - usia):
        premium += (v ** (t + 1)) * get_tpx_qx_t(usia, t)
    return round(premium * benefit, 0)

def calculate_term_life(usia, bunga, term, benefit=1):
    premium = 0
    v = 1 / (1 + bunga)
    for t in range(term):
        premium += (v ** (t + 1)) * get_tpx_qx_t(usia, t)
    return round(premium * benefit, 0)

def calculate_endowment(usia, bunga, term, benefit=1):
    term_premium = calculate_term_life(usia, bunga, term, benefit)
    survival = get_npx(usia, term) * (1 / (1 + bunga)) ** term * benefit
    return round(term_premium + survival, 0)

def calculate_annuity_value(usia, bunga, term, is_lifetime, payment):
    ann_factor = calculate_annuity_due(usia, bunga, term if not is_lifetime else 0, is_lifetime)
    return round(ann_factor * payment, 0)

def calculate_pension_fund(usia, usia_pensiun, gaji, iuran, return_inv):
    tahun = usia_pensiun - usia
    if tahun <= 0:
        return 0
    iuran_bulanan = gaji * (iuran / 100)
    bunga_bulanan = (1 + return_inv) ** (1/12) - 1
    dana = 0
    for _ in range(tahun * 12):
        dana = dana * (1 + bunga_bulanan) + iuran_bulanan
    return int(dana)

def calculate_probability_survival(usia, tahun):
    return get_npx(usia, tahun)

def calculate_probability_death(usia, tahun):
    if tahun == 1:
        return get_qx(usia)
    return get_npx(usia, tahun - 1) * get_qx(usia + tahun - 1)

# ========== HALAMAN LOGIN ==========
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None

if not st.session_state.logged_in:
    st.markdown("""
    <div class="main-header">
        <h1>🌿 Life Nova</h1>
        <p>Aplikasi Aktuaria Profesional | Tema Pink & Hijau Elegan</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Registrasi", "🔄 Lupa Password"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input("Email", placeholder="contoh@email.com")
            password = st.text_input("Password", type="password")
            if st.button("🌿 Login", use_container_width=True):
                if login_user(email, password):
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("Email atau password salah!")
            st.caption("Demo: admin@lifenova.com (registrasi dulu ya!)")
    
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
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
    
    with tab3:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            forgot_email = st.text_input("Email Anda")
            new_password = st.text_input("Password Baru", type="password")
            if st.button("🔄 Reset Password", use_container_width=True):
                success, msg = reset_password(forgot_email, new_password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    st.stop()

# ========== HALAMAN UTAMA ==========
with st.sidebar:
    st.markdown("<h2 style='text-align:center'>🌿 Life Nova</h2>", unsafe_allow_html=True)
    st.markdown(f"👋 Halo, **{st.session_state.user_email}**!")
    st.markdown("---")
    
    menu_options = ["🏠 Dashboard", "📊 Tabel Mortalita", "💰 Asuransi Jiwa", "📈 Anuitas", "🏦 Dana Pensiun", "🎲 Probabilitas", "ℹ️ Tentang"]
    
    if is_admin(st.session_state.user_email):
        menu_options.append("👥 Data User")
    
    menu = st.selectbox("Menu", menu_options)
    st.markdown("---")
    if st.button("🌿 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

st.markdown(f"""
<div class="main-header">
    <h1>🌿 Life Nova</h1>
    <p>{menu} | {st.session_state.user_email}</p>
</div>
""", unsafe_allow_html=True)

# ========== DASHBOARD ==========
if menu == "🏠 Dashboard":
    st.subheader("📊 Ringkasan Aktuaria")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        prob_mati_60 = get_qx(60) * 100
        st.markdown(f"""
        <div class="metric-card">
            <h2>{prob_mati_60:.1f}%</h2>
            <p>Probabilitas Kematian</p>
            <small>Usia 60 tahun</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        prob_hidup_30_60 = get_npx(30, 30) * 100
        st.markdown(f"""
        <div class="metric-card">
            <h2>{prob_hidup_30_60:.1f}%</h2>
            <p>Probabilitas Hidup</p>
            <small>Usia 30 → 60 tahun</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        harapan_hidup = sum([get_npx(30, t) for t in range(1, 71)]) / 1
        st.markdown(f"""
        <div class="metric-card">
            <h2>{harapan_hidup:.1f}</h2>
            <p>Harapan Hidup</p>
            <small>Dari usia 30 tahun</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h2>8%</h2>
            <p>Return Investasi</p>
            <small>Untuk Dana Pensiun</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grafik Kurva Survival
    st.subheader("📈 Kurva Survival")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=MORTALITY_TABLE['usia'], 
        y=MORTALITY_TABLE['lx'], 
        mode='lines', 
        name='Jumlah Hidup (lx)',
        line=dict(color='#993556', width=3),
        fill='tozeroy',
        fillcolor='rgba(153,53,86,0.2)'
    ))
    fig.update_layout(
        title="Kurva Survival - Tabel Mortalita Gompertz",
        xaxis_title="Usia (tahun)",
        yaxis_title="Jumlah Orang Hidup (lx)",
        height=450,
        plot_bgcolor='rgba(234,243,222,0.3)',
        paper_bgcolor='rgba(234,243,222,0.1)'
    )
    fig.update_xaxis(showgrid=True, gridcolor='#97C459')
    fig.update_yaxis(showgrid=True, gridcolor='#97C459')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Dashboard Life Nova - Aplikasi aktuaria dengan tema pink dan hijau elegan. Gunakan menu di samping untuk menghitung asuransi, anuitas, dan dana pensiun.")

# ========== TABEL MORTALITA ==========
elif menu == "📊 Tabel Mortalita":
    st.subheader("📊 Tabel Mortalita")
    st.caption("Model Gompertz dengan parameter a=0.0001, b=0.08")
    
    usia_range = st.slider("Filter Rentang Usia", 0, 100, (0, 80))
    
    df_filtered = MORTALITY_TABLE[(MORTALITY_TABLE['usia'] >= usia_range[0]) & (MORTALITY_TABLE['usia'] <= usia_range[1])]
    
    st.dataframe(
        df_filtered,
        column_config={
            "usia": "Usia",
            "lx": "Jumlah Hidup",
            "dx": "Jumlah Meninggal",
            "qx": "Prob. Kematian",
            "px": "Prob. Hidup"
        },
        use_container_width=True,
        height=400
    )
    
    st.caption("Tabel mortalita digunakan untuk menghitung probabilitas hidup dan mati dalam perhitungan aktuaria.")

# ========== ASURANSI JIWA ==========
elif menu == "💰 Asuransi Jiwa":
    st.subheader("💰 Kalkulator Premi Asuransi Jiwa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        jenis = st.selectbox("Jenis Asuransi", ["Whole Life (Seumur Hidup)", "Term Life (Berjangka)", "Endowment"])
        usia = st.number_input("Usia Peserta", 0, 90, 30)
        bunga = st.number_input("Tingkat Bunga (%)", 0.0, 15.0, 5.0) / 100
    
    with col2:
        benefit = st.number_input("Uang Pertanggungan (Rp)", 1_000_000, 1_000_000_000, 100_000_000, step=10_000_000)
        if jenis != "Whole Life (Seumur Hidup)":
            jangka = st.number_input("Jangka Waktu (tahun)", 1, 30, 10)
    
    if st.button("🌿 Hitung Premi", use_container_width=True):
        if jenis == "Whole Life (Seumur Hidup)":
            premi = calculate_whole_life(usia, bunga, benefit)
            st.success(f"### ✨ Premi Asuransi Whole Life: **Rp {premi:,.0f}**")
            st.caption("Premi dibayarkan sekaligus (single premium)")
        
        elif jenis == "Term Life (Berjangka)":
            premi = calculate_term_life(usia, bunga, jangka, benefit)
            st.success(f"### ✨ Premi Asuransi Term Life {jangka} tahun: **Rp {premi:,.0f}**")
            st.caption("Premi dibayarkan sekaligus (single premium)")
        
        else:
            premi = calculate_endowment(usia, bunga, jangka, benefit)
            st.success(f"### ✨ Premi Asuransi Endowment {jangka} tahun: **Rp {premi:,.0f}**")
            st.caption("Premi dibayarkan sekaligus (single premium)")
        
        with st.expander("📖 Detail Perhitungan"):
            st.write(f"**Usia:** {usia} tahun")
            st.write(f"**Tingkat Bunga:** {bunga*100}% per tahun")
            st.write(f"**Uang Pertanggungan:** Rp {benefit:,.0f}")
            st.write("Metode: Prinsip aktuaria dengan tabel mortalita Gompertz")

# ========== ANUITAS ==========
elif menu == "📈 Anuitas":
    st.subheader("📈 Kalkulator Anuitas Hidup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        jenis = st.selectbox("Jenis Anuitas", ["Anuitas Berjangka", "Anuitas Seumur Hidup"])
        usia = st.number_input("Usia Peserta", 0, 90, 55)
        bunga = st.number_input("Tingkat Bunga (%)", 0.0, 15.0, 5.0) / 100
    
    with col2:
        if jenis == "Anuitas Berjangka":
            jangka = st.number_input("Jangka Waktu (tahun)", 1, 40, 20)
        pembayaran = st.number_input("Pembayaran per Tahun (Rp)", 1_000_000, 500_000_000, 50_000_000, step=5_000_000)
    
    if st.button("🌿 Hitung Nilai Sekarang", use_container_width=True):
        is_lifetime = (jenis == "Anuitas Seumur Hidup")
        jangka_val = jangka if not is_lifetime else 0
        nilai = calculate_annuity_value(usia, bunga, jangka_val, is_lifetime, pembayaran)
        
        st.success(f"### ✨ Nilai Sekarang Anuitas: **Rp {nilai:,.0f}**")
        
        with st.expander("📖 Detail Perhitungan"):
            st.write(f"**Usia:** {usia} tahun")
            st.write(f"**Jenis:** {jenis}")
            st.write(f"**Pembayaran per tahun:** Rp {pembayaran:,.0f}")
            st.write(f"**Tingkat bunga:** {bunga*100}% per tahun")

# ========== DANA PENSIUN ==========
elif menu == "🏦 Dana Pensiun":
    st.subheader("🏦 Perencanaan Dana Pensiun")
    
    col1, col2 = st.columns(2)
    
    with col1:
        usia_skrg = st.number_input("Usia Sekarang", 20, 60, 30)
        usia_pensiun = st.number_input("Usia Pensiun", usia_skrg+1, 70, 60)
        gaji = st.number_input("Gaji Bulanan (Rp)", 1_000_000, 100_000_000, 10_000_000, step=1_000_000)
    
    with col2:
        iuran = st.number_input("Persentase Iuran dari Gaji (%)", 1, 30, 5)
        return_inv = st.number_input("Return Investasi per Tahun (%)", 1, 20, 8) / 100
    
    if st.button("🌿 Hitung Dana Pensiun", use_container_width=True):
        dana = calculate_pension_fund(usia_skrg, usia_pensiun, gaji, iuran, return_inv)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("💰 Total Dana Terkumpul", f"Rp {dana:,.0f}")
        with col_b:
            estimasi_manfaat = int(dana * 0.05 / 12)
            st.metric("📆 Estimasi Manfaat per Bulan", f"Rp {estimasi_manfaat:,.0f}")
        
        # Grafik pertumbuhan
        tahun_menabung = usia_pensiun - usia_skrg
        iuran_bulanan = gaji * (iuran / 100)
        bunga_bulanan = (1 + return_inv) ** (1/12) - 1
        
        dana_per_tahun = []
        dana_berjalan = 0
        for bulan in range(tahun_menabung * 12):
            dana_berjalan = dana_berjalan * (1 + bunga_bulanan) + iuran_bulanan
            if (bulan + 1) % 12 == 0:
                dana_per_tahun.append(dana_berjalan)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, tahun_menabung + 1)),
            y=dana_per_tahun,
            mode='lines+markers',
            name='Dana Pensiun',
            line=dict(color='#993556', width=3),
            marker=dict(color='#3B6D11', size=6)
        ))
        fig.update_layout(
            title="📈 Pertumbuhan Dana Pensiun",
            xaxis_title="Tahun",
            yaxis_title="Dana Terkumpul (Rp)",
            height=400,
            plot_bgcolor='rgba(234,243,222,0.3)'
        )
        st.plotly_chart(fig, use_container_width=True)

# ========== PROBABILITAS ==========
elif menu == "🎲 Probabilitas":
    st.subheader("🎲 Kalkulator Probabilitas Aktuaria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        usia = st.number_input("Usia", 0, 100, 40)
        tahun = st.number_input("Jangka Waktu (tahun)", 1, 60, 10)
    
    if st.button("🌿 Hitung Probabilitas", use_container_width=True):
        prob_hidup = calculate_probability_survival(usia, tahun)
        prob_mati = calculate_probability_death(usia, tahun)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{prob_hidup*100:.2f}%</h2>
                <p>Probabilitas Hidup</p>
                <small>sampai {tahun} tahun ke depan</small>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{prob_mati*100:.4f}%</h2>
                <p>Probabilitas Meninggal</p>
                <small>pada tahun ke-{tahun}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Grafik survival
        ages = list(range(usia, min(usia + 50, 101)))
        survival_probs = [calculate_probability_survival(usia, a - usia) for a in ages]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ages,
            y=survival_probs,
            mode='lines',
            name='Probabilitas Survival',
            line=dict(color='#3B6D11', width=3),
            fill='tozeroy',
            fillcolor='rgba(59,109,17,0.2)'
        ))
        fig.update_layout(
            title=f"Kurva Survival dari Usia {usia}",
            xaxis_title="Usia",
            yaxis_title="Probabilitas Hidup",
            height=400,
            plot_bgcolor='rgba(234,243,222,0.3)'
        )
        st.plotly_chart(fig, use_container_width=True)

# ========== DATA USER (khusus admin) ==========
elif menu == "👥 Data User":
    st.subheader("👥 Data Seluruh Pengguna")
    st.warning("🔒 Halaman ini hanya bisa diakses oleh ADMIN")
    
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
            file_name=f"life_nova_users_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.info(f"📊 Total user terdaftar: **{len(users)}** orang")
    else:
        st.info("Belum ada user yang terdaftar")

# ========== TENTANG ==========
elif menu == "ℹ️ Tentang":
    st.markdown("""
    ### 🌿 Life Nova - Aplikasi Aktuaria Profesional
    
    **✨ Fitur Lengkap:**
    - Dashboard dengan grafik kurva survival
    - Tabel Mortalita (Model Gompertz)
    - Asuransi Whole Life, Term Life, Endowment
    - Anuitas Berjangka & Seumur Hidup
    - Perencanaan Dana Pensiun
    - Kalkulator Probabilitas Hidup & Meninggal
    - Manajemen User (Registrasi, Login, Reset Password)
    - Admin dapat melihat semua data user
    
    **🎨 Tema:**
    - Pink Elegan: `#993556`
    - Hijau Elegan: `#3B6D11`
    
    **👑 Cara Menjadi Admin:**
    - Registrasi dengan email: `admin@lifenova.com`
    
    **🔒 Keamanan:**
    - Password dienkripsi dengan bcrypt
    - Data user tersimpan di file JSON
    """)

# ========== FOOTER ==========
st.markdown("""
<div class="footer">
    <p>🌿 Life Nova • Aplikasi Aktuaria dengan Tema Pink & Hijau Elegan</p>
    <p>Dibuat untuk para aktuaria dan perencana keuangan</p>
</div>
""", unsafe_allow_html=True)    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: var(--green-light);
        margin-top: 0.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, var(--pink-light) 0%, var(--green-light) 100%);
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid var(--green-border);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .metric-card h2 {
        color: var(--pink-dark);
        margin: 0;
        font-size: 1.8rem;
    }
    .metric-card p {
        color: var(--green-dark);
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    .metric-card small {
        color: #888;
        font-size: 0.7rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--pink-dark) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background: var(--pink-mid) !important;
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--green-light) 0%, white 100%);
    }
    [data-testid="stSidebar"] h2 {
        color: var(--green-dark);
    }
    
    /* Success/Info/Warning */
    .stSuccess {
        background-color: var(--green-light);
        color: var(--green-dark);
        border-left-color: var(--green-mid);
    }
    .stInfo {
        background-color: var(--pink-light);
        color: var(--pink-dark);
        border-left-color: var(--pink-mid);
    }
    .stError {
        background-color: #FFE4E4;
        color: #c0392b;
        border-left-color: #e74c3c;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--green-light);
        border-radius: 10px;
        color: var(--green-dark);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--pink-dark);
        font-size: 0.8rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--pink-dark);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ========== DATABASE USER (file JSON) ==========
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

# ========== TABEL MORTALITA ==========
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
    df['px'] = (1 - df['qx']).round(6)
    return df

MORTALITY_TABLE = generate_mortality_table()

def get_qx(usia):
    if 0 <= usia <= 100:
        return MORTALITY_TABLE[MORTALITY_TABLE['usia'] == usia]['qx'].values[0]
    return 1

def get_px(usia):
    return 1 - get_qx(usia)

def get_npx(usia, n):
    if usia + n > 100:
        return 0
    prob = 1
    for t in range(n):
        prob *= get_px(usia + t)
    return prob

def get_tpx_qx_t(usia, t):
    if usia + t + 1 > 100:
        return 0
    return get_npx(usia, t) * get_qx(usia + t)

# ========== FUNGSI AKTUARIA ==========
def calculate_annuity_due(usia, bunga, n, is_lifetime=False):
    max_age = 100
    annuity = 1
    v = 1 / (1 + bunga)
    max_term = (max_age - usia - 1) if is_lifetime else min(n - 1, max_age - usia - 1)
    for t in range(1, max_term + 1):
        prob_hidup = get_npx(usia, t)
        annuity += (v ** t) * prob_hidup
    return round(annuity, 6)

def calculate_whole_life(usia, bunga, benefit=1):
    premium = 0
    v = 1 / (1 + bunga)
    for t in range(100 - usia):
        premium += (v ** (t + 1)) * get_tpx_qx_t(usia, t)
    return round(premium * benefit, 0)

def calculate_term_life(usia, bunga, term, benefit=1):
    premium = 0
    v = 1 / (1 + bunga)
    for t in range(term):
        premium += (v ** (t + 1)) * get_tpx_qx_t(usia, t)
    return round(premium * benefit, 0)

def calculate_endowment(usia, bunga, term, benefit=1):
    term_premium = calculate_term_life(usia, bunga, term, benefit)
    survival = get_npx(usia, term) * (1 / (1 + bunga)) ** term * benefit
    return round(term_premium + survival, 0)

def calculate_annuity_value(usia, bunga, term, is_lifetime, payment):
    ann_factor = calculate_annuity_due(usia, bunga, term if not is_lifetime else 0, is_lifetime)
    return round(ann_factor * payment, 0)

def calculate_pension_fund(usia, usia_pensiun, gaji, iuran, return_inv):
    tahun = usia_pensiun - usia
    if tahun <= 0:
        return 0
    iuran_bulanan = gaji * (iuran / 100)
    bunga_bulanan = (1 + return_inv) ** (1/12) - 1
    dana = 0
    for _ in range(tahun * 12):
        dana = dana * (1 + bunga_bulanan) + iuran_bulanan
    return int(dana)

def calculate_probability_survival(usia, tahun):
    return get_npx(usia, tahun)

def calculate_probability_death(usia, tahun):
    if tahun == 1:
        return get_qx(usia)
    return get_npx(usia, tahun - 1) * get_qx(usia + tahun - 1)

# ========== HALAMAN LOGIN ==========
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None

if not st.session_state.logged_in:
    st.markdown("""
    <div class="main-header">
        <h1>🌿 Life Nova</h1>
        <p>Aplikasi Aktuaria Profesional | Tema Pink & Hijau Elegan</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Registrasi", "🔄 Lupa Password"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input("Email", placeholder="contoh@email.com")
            password = st.text_input("Password", type="password")
            if st.button("🌿 Login", use_container_width=True):
                if login_user(email, password):
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("❌ Email atau password salah!")
            st.caption("💡 Demo: admin@lifenova.com (registrasi dulu ya!)")
    
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

# ========== HALAMAN UTAMA ==========
with st.sidebar:
    st.markdown("<h2 style='text-align:center'>🌿 Life Nova</h2>", unsafe_allow_html=True)
    st.markdown(f"👋 Halo, **{st.session_state.user_email}**!")
    st.markdown("---")
    
    menu_options = ["🏠 Dashboard", "📊 Tabel Mortalita", "💰 Asuransi Jiwa", "📈 Anuitas", "🏦 Dana Pensiun", "🎲 Probabilitas", "ℹ️ Tentang"]
    
    if is_admin(st.session_state.user_email):
        menu_options.append("👥 Data User")
    
    menu = st.selectbox("Menu", menu_options)
    st.markdown("---")
    if st.button("🌿 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

st.markdown(f"""
<div class="main-header">
    <h1>🌿 Life Nova</h1>
    <p>{menu} | {st.session_state.user_email}</p>
</div>
""", unsafe_allow_html=True)

# ========== DASHBOARD ==========
if menu == "🏠 Dashboard":
    st.subheader("📊 Ringkasan Aktuaria")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        prob_mati_60 = get_qx(60) * 100
        st.markdown(f"""
        <div class="metric-card">
            <h2>{prob_mati_60:.1f}%</h2>
            <p>Probabilitas Kematian</p>
            <small>Usia 60 tahun</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        prob_hidup_30_60 = get_npx(30, 30) * 100
        st.markdown(f"""
        <div class="metric-card">
            <h2>{prob_hidup_30_60:.1f}%</h2>
            <p>Probabilitas Hidup</p>
            <small>Usia 30 → 60 tahun</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        harapan_hidup = sum([get_npx(30, t) for t in range(1, 71)]) / 1
        st.markdown(f"""
        <div class="metric-card">
            <h2>{harapan_hidup:.1f}</h2>
            <p>Harapan Hidup</p>
            <small>Dari usia 30 tahun</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h2>8%</h2>
            <p>Return Investasi</p>
            <small>Untuk Dana Pensiun</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grafik Kurva Survival
    st.subheader("📈 Kurva Survival")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=MORTALITY_TABLE['usia'], 
        y=MORTALITY_TABLE['lx'], 
        mode='lines', 
        name='Jumlah Hidup (lx)',
        line=dict(color='#993556', width=3),
        fill='tozeroy',
        fillcolor='rgba(153,53,86,0.2)'
    ))
    fig.update_layout(
        title="Kurva Survival - Tabel Mortalita Gompertz",
        xaxis_title="Usia (tahun)",
        yaxis_title="Jumlah Orang Hidup (lx)",
        height=450,
        plot_bgcolor='rgba(234,243,222,0.3)',
        paper_bgcolor='rgba(234,243,222,0.1)'
    )
    fig.update_xaxis(showgrid=True, gridcolor='#97C459')
    fig.update_yaxis(showgrid=True, gridcolor='#97C459')
    st.plotly_chart(fig, use_container_width=True)
    
    # Informasi Tambahan
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **Dashboard Life Nova** - Aplikasi aktuaria dengan tema pink dan hijau elegan. Gunakan menu di samping untuk menghitung asuransi, anuitas, dan dana pensiun.")

# ========== TABEL MORTALITA ==========
elif menu == "📊 Tabel Mortalita":
    st.subheader("📊 Tabel Mortalita")
    st.caption("Model Gompertz dengan parameter a=0.0001, b=0.08")
    
    usia_range = st.slider("Filter Rentang Usia", 0, 100, (0, 80))
    
    df_filtered = MORTALITY_TABLE[(MORTALITY_TABLE['usia'] >= usia_range[0]) & 
                                   (MORTALITY_TABLE['usia'] <= usia_range[1])]
    
    st.dataframe(
        df_filtered,
        column_config={
            "usia": "🎂 Usia",
            "lx": "👥 Jumlah Hidup",
            "dx": "💔 Jumlah Meninggal",
            "qx": "📊 Prob. Kematian",
            "px": "✨ Prob. Hidup"
        },
        use_container_width=True,
        height=400
    )
    
    st.caption("Tabel mortalita digunakan untuk menghitung probabilitas hidup dan mati dalam perhitungan aktuaria.")

# ========== ASURANSI JIWA ==========
elif menu == "💰 Asuransi Jiwa":
    st.subheader("💰 Kalkulator Premi Asuransi Jiwa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        jenis = st.selectbox("Jenis Asuransi", ["Whole Life (Seumur Hidup)", "Term Life (Berjangka)", "Endowment"])
        usia = st.number_input("Usia Peserta", 0, 90, 30)
        bunga = st.number_input("Tingkat Bunga (%)", 0.0, 15.0, 5.0) / 100
    
    with col2:
        benefit = st.number_input("Uang Pertanggungan (Rp)", 1_000_000, 1_000_000_000, 100_000_000, step=10_000_000, format="%d")
        if jenis != "Whole Life (Seumur Hidup)":
            jangka = st.number_input("Jangka Waktu (tahun)", 1, 30, 10)
    
    if st.button("🌿 Hitung Premi", use_container_width=True):
        if jenis == "Whole Life (Seumur Hidup)":
            premi = calculate_whole_life(usia, bunga, benefit)
            st.success(f"### ✨ Premi Asuransi Whole Life: **Rp {premi:,.0f}**")
            st.caption("Premi dibayarkan sekaligus (single premium)")
        
        elif jenis == "Term Life (Berjangka)":
            premi = calculate_term_life(usia, bunga, jangka, benefit)
            st.success(f"### ✨ Premi Asuransi Term Life {jangka} tahun: **Rp {premi:,.0f}**")
            st.caption("Premi dibayarkan sekaligus (single premium)")
        
        else:
            premi = calculate_endowment(usia, bunga, jangka, benefit)
            st.success(f"### ✨ Premi Asuransi Endowment {jangka} tahun: **Rp {premi:,.0f}**")
            st.caption("Premi dibayarkan sekaligus (single premium)")
        
        with st.expander("📖 Detail Perhitungan"):
            st.write(f"**Usia:** {usia} tahun")
            st.write(f"**Tingkat Bunga:** {bunga*100}% per tahun")
            st.write(f"**Uang Pertanggungan:** Rp {benefit:,.0f}")
            st.write("**Metode:** Prinsip aktuaria dengan tabel mortalita Gompertz")

# ========== ANUITAS ==========
elif menu == "📈 Anuitas":
    st.subheader("📈 Kalkulator Anuitas Hidup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        jenis = st.selectbox("Jenis Anuitas", ["Anuitas Berjangka", "Anuitas Seumur Hidup"])
        usia = st.number_input("Usia Peserta", 0, 90, 55)
        bunga = st.number_input("Tingkat Bunga (%)", 0.0, 15.0, 5.0) / 100
    
    with col2:
        if jenis == "Anuitas Berjangka":
            jangka = st.number_input("Jangka Waktu (tahun)", 1, 40, 20)
        pembayaran = st.number_input("Pembayaran per Tahun (Rp)", 1_000_000, 500_000_000, 50_000_000, step=5_000_000, format="%d")
    
    if st.button("🌿 Hitung Nilai Sekarang", use_container_width=True):
        is_lifetime = (jenis == "Anuitas Seumur Hidup")
        jangka_val = jangka if not is_lifetime else 0
        nilai = calculate_annuity_value(usia, bunga, jangka_val, is_lifetime, pembayaran)
        
        st.success(f"### ✨ Nilai Sekarang Anuitas: **Rp {nilai:,.0f}**")
        
        with st.expander("📖 Detail Perhitungan"):
            st.write(f"**Usia:** {usia} tahun")
            st.write(f"**Jenis:** {jenis}")
            st.write(f"**Pembayaran per tahun:** Rp {pembayaran:,.0f}")
            st.write(f"**Tingkat bunga:** {bunga*100}% per tahun")

# ========== DANA PENSIUN ==========
elif menu == "🏦 Dana Pensiun":
    st.subheader("🏦 Perencanaan Dana Pensiun")
    
    col1, col2 = st.columns(2)
    
    with col1:
        usia_skrg = st.number_input("Usia Sekarang", 20, 60, 30)
        usia_pensiun = st.number_input("Usia Pensiun", usia_skrg+1, 70, 60)
        gaji = st.number_input("Gaji Bulanan (Rp)", 1_000_000, 100_000_000, 10_000_000, step=1_000_000, format="%d")
    
    with col2:
        iuran = st.number_input("Persentase Iuran dari Gaji (%)", 1, 30, 5)
        return_inv = st.number_input("Return Investasi per Tahun (%)", 1, 20, 8) / 100
    
    if st.button("🌿 Hitung Dana Pensiun", use_container_width=True):
        dana = calculate_pension_fund(usia_skrg, usia_pensiun, gaji, iuran, return_inv)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("💰 Total Dana Terkumpul", f"Rp {dana:,.0f}")
        with col_b:
            # Estimasi manfaat bulanan (asumsi anuitas 5%)
            estimasi_manfaat = int(dana * 0.05 / 12)
            st.metric("📆 Estimasi Manfaat per Bulan", f"Rp {estimasi_manfaat:,.0f}")
        
        # Grafik pertumbuhan
        tahun_menabung = usia_pensiun - usia_skrg
        iuran_bulanan = gaji * (iuran / 100)
        bunga_bulanan = (1 + return_inv) ** (1/12) - 1
        
        dana_per_tahun = []
        dana_berjalan = 0
        for bulan in range(tahun_menabung * 12):
            dana_berjalan = dana_berjalan * (1 + bunga_bulanan) + iuran_bulanan
            if (bulan + 1) % 12 == 0:
                dana_per_tahun.append(dana_berjalan)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, tahun_menabung + 1)),
            y=dana_per_tahun,
            mode='lines+markers',
            name='Dana Pensiun',
            line=dict(color='#993556', width=3),
            marker=dict(color='#3B6D11', size=6)
        ))
        fig.update_layout(
            title="📈 Pertumbuhan Dana Pensiun",
            xaxis_title="Tahun",
            yaxis_title="Dana Terkumpul (Rp)",
            height=400,
            plot_bgcolor='rgba(234,243,222,0.3)'
        )
        st.plotly_chart(fig, use_container_width=True)

# ========== PROBABILITAS ==========
elif menu == "🎲 Probabilitas":
    st.subheader("🎲 Kalkulator Probabilitas Aktuaria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        usia = st.number_input("Usia", 0, 100, 40)
        tahun = st.number_input("Jangka Waktu (tahun)", 1, 60, 10)
    
    if st.button("🌿 Hitung Probabilitas", use_container_width=True):
        prob_hidup = calculate_probability_survival(usia, tahun)
        prob_mati = calculate_probability_death(usia, tahun)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{prob_hidup*100:.2f}%</h2>
                <p>Probabilitas Hidup</p>
                <small>sampai {tahun} tahun ke depan</small>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{prob_mati*100:.4f}%</h2>
                <p>Probabilitas Meninggal</p>
                <small>pada tahun ke-{tahun}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Grafik survival dari usia sekarang
        ages = list(range(usia, min(usia + 50, 101)))
        survival_probs = [calculate_probability_survival(usia, a - usia) for a in ages]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ages,
            y=survival_probs,
            mode='lines',
            name='Probabilitas Survival',
            line=dict(color='#3B6D11', width=3),
            fill='tozeroy',
            fillcolor='rgba(59,109,17,0.2)'
        ))
        fig.update_layout(
            title=f"Kurva Survival dari Usia {usia}",
            xaxis_title="Usia",
            yaxis_title="Probabilitas Hidup",
            height=400,
            plot_bgcolor='rgba(234,243,222,0.3)'
        )
        st.plotly_chart(fig, use_container_width=True)

# ========== DATA USER (khusus admin) ==========
elif menu == "👥 Data User":
    st.subheader("👥 Data Seluruh Pengguna")
    st.warning("🔒 Halaman ini hanya bisa diakses oleh ADMIN")
    
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
            file_name=f"life_nova_users_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.info(f"📊 Total user terdaftar: **{len(users)}** orang")
    else:
        st.info("Belum ada user yang terdaftar")

# ========== TENTANG ==========
else:
    st.markdown("""
    ### 🌿 Life Nova - Aplikasi Aktuaria Profesional
    
    **✨ Fitur Lengkap:**
    - ✅ Dashboard dengan grafik kurva survival
    - ✅ Tabel Mortalita (Model Gompertz)
    - ✅ Asuransi Whole Life, Term Life, Endowment
    - ✅ Anuitas Berjangka & Seumur Hidup
    - ✅ Perencanaan Dana Pensiun
    - ✅ Kalkulator Probabilitas Hidup & Meninggal
    - ✅ Manajemen User (Registrasi, Login, Reset Password)
    - ✅ Admin dapat melihat semua data user
    
    **🎨 Tema:**
    - Pink Elegan: `#993556`
    - Hijau Elegan: `#3B6D11`
    
    **👑 Cara Menjadi Admin:**
    - Registrasi dengan email: `admin@lifenova.com`
    
    **🔒 Keamanan:**
    - Password dienkripsi dengan bcrypt
    - Data user tersimpan di file JSON
    
    **📚 Dasar Teori:**
    - Premi Asuransi: \( A_x = \sum v^{t+1} \cdot {}_{t|}q_x \)
    - Anuitas Hidup: \( \ddot{a}_x = \sum_{t=0}^{\infty} v^t \cdot {}_tp_x \)
    - Cadangan Prospektif: \( {}_kV_x = A_{x+k} - P \cdot \ddot{a}_{x+k} \)
    """)

# ========== FOOTER ==========
st.markdown("""
<div class="footer">
    <p>🌿 Life Nova • Aplikasi Aktuaria dengan Tema Pink & Hijau Elegan</p>
    <p>Dibuat dengan 💕 untuk para aktuaria dan perencana keuangan</p>
</div>
""", unsafe_allow_html=True)    """, unsafe_allow_html=True)


def alert_sukses(pesan: str):
    st.markdown(f'<div class="alert-success">✓ &nbsp;{pesan}</div>', unsafe_allow_html=True)


def alert_error(pesan: str):
    st.markdown(f'<div class="alert-error">✕ &nbsp;{pesan}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN LOGIN
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_login():
    # Logo & judul tengah
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("""
        <div style="text-align:center; margin-bottom:8px">
            <div style="width:56px;height:56px;border-radius:14px;background:#3B6D11;
                        display:inline-flex;align-items:center;justify-content:center;
                        font-size:28px;margin-bottom:8px">🌿</div>
            <h2 style="margin:0;color:#3B6D11;font-size:24px">Lumacta</h2>
            <p style="margin:2px 0 0;color:#888;font-size:12px">
                Hitung premi asuransi lebih cerdas & mudah
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Masuk ke akunmu")

        email_atau_username = st.text_input(
            "Email atau username",
            placeholder="contoh@email.com atau username",
            key="login_ident",
        )
        password = st.text_input(
            "Kata sandi",
            type="password",
            placeholder="Minimal 6 karakter",
            key="login_pass",
        )

        if st.button("Masuk sekarang", key="btn_login"):
            if not email_atau_username or not password:
                alert_error("Isi email/username dan kata sandi terlebih dahulu.")
            else:
                hasil = login_user(email_atau_username, password)
                if hasil["ok"]:
                    st.session_state.user = hasil["user"]
                    st.rerun()
                else:
                    alert_error(hasil["pesan"])

        st.markdown("<div style='text-align:center;margin-top:14px;font-size:13px'>", unsafe_allow_html=True)
        st.markdown("Belum punya akun?")
        if st.button("Daftar gratis →", key="ke_register"):
            st.session_state.halaman_auth = "register"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN REGISTER
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_register():
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("""
        <div style="text-align:center; margin-bottom:8px">
            <div style="width:56px;height:56px;border-radius:14px;background:#3B6D11;
                        display:inline-flex;align-items:center;justify-content:center;
                        font-size:28px;margin-bottom:8px">🌿</div>
            <h2 style="margin:0;color:#3B6D11;font-size:24px">Lumacta</h2>
            <p style="margin:2px 0 0;color:#888;font-size:12px">
                Buat akun gratis — tidak perlu kartu kredit
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Buat akun baru")

        nama = st.text_input("Nama lengkap", placeholder="Siti Aminah", key="reg_nama")
        email = st.text_input("Alamat email", placeholder="contoh@email.com", key="reg_email")
        username = st.text_input(
            "Username",
            placeholder="sitiaminah  (tanpa spasi)",
            key="reg_username",
        )
        password = st.text_input(
            "Kata sandi",
            type="password",
            placeholder="Minimal 6 karakter",
            key="reg_pass",
        )
        konfirmasi = st.text_input(
            "Ulangi kata sandi",
            type="password",
            placeholder="Sama seperti kata sandi di atas",
            key="reg_konfirmasi",
        )

        if st.button("Buat akun sekarang", key="btn_register"):
            if not all([nama, email, username, password, konfirmasi]):
                alert_error("Semua kolom wajib diisi.")
            elif password != konfirmasi:
                alert_error("Kata sandi dan konfirmasi tidak cocok.")
            else:
                hasil = register_user(nama, email, username, password)
                if hasil["ok"]:
                    alert_sukses(f"Akun berhasil dibuat! Silakan masuk, {hasil['nama']}.")
                    st.session_state.halaman_auth = "login"
                    st.rerun()
                else:
                    alert_error(hasil["pesan"])

        st.markdown("<div style='text-align:center;margin-top:14px;font-size:13px'>", unsafe_allow_html=True)
        st.markdown("Sudah punya akun?")
        if st.button("← Masuk di sini", key="ke_login"):
            st.session_state.halaman_auth = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_dashboard():
    user = st.session_state.user
    navbar()

    # Welcome banner
    st.markdown(f"""
    <div class="welcome-banner">
        <div>
            <div class="wb-name">Selamat datang, {user['nama']} 👋</div>
            <div class="wb-sub">{user['email']} &nbsp;·&nbsp; @{user['username']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tombol keluar di atas kanan
    col_space, col_logout = st.columns([5, 1])
    with col_logout:
        if st.button("Keluar", key="btn_logout"):
            st.session_state.user = None
            st.session_state.halaman_auth = "login"
            st.rerun()

    # ── Statistik ringkas ────────────────────────────────────────────────────
    riwayat = ambil_riwayat(user["id"], limit=50)
    total   = len(riwayat)
    premi   = sum(1 for r in riwayat if r["fitur"] == "Simulasi Premi")
    bandin  = sum(1 for r in riwayat if r["fitur"] == "Bandingkan")
    peluang = sum(1 for r in riwayat if r["fitur"] == "Peluang Hidup")

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, delta, warna in [
        (c1, "Total perhitungan", total,   "Semua fitur",       "delta-green"),
        (c2, "Simulasi premi",   premi,   "Tabungan berjangka", "delta-pink"),
        (c3, "Perbandingan",     bandin,  "Fitur unggulan",     "delta-green"),
        (c4, "Peluang hidup",    peluang, "Analisis survival",  "delta-green"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="label">{label}</div>
                <div class="value">{val}</div>
                <div class="{warna}">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Fitur utama ──────────────────────────────────────────────────────────
    st.markdown("#### Pilih fitur")
    fc1, fc2, fc3, fc4 = st.columns(4)

    fitur_list = [
        (fc1, "fc-icon-p", "🪙", "Simulasi premi tabungan",
         "Hitung berapa premi sekali bayar untuk dapat uang pertanggungan — baik meninggal maupun hidup sampai akhir kontrak.",
         "btn_fitur_premi"),
        (fc2, "fc-icon-g", "⚖️", "Bandingkan dua jenis asuransi",
         "Lihat perbedaan biaya antara asuransi per tahun vs terus-menerus dalam grafik yang mudah dibaca.",
         "btn_fitur_bandin"),
        (fc3, "fc-icon-p", "💓", "Peluang hidup",
         "Ketahui berapa besar kemungkinan seseorang masih hidup di usia tertentu berdasarkan data mortalitas.",
         "btn_fitur_peluang"),
        (fc4, "fc-icon-g", "📋", "Unduh laporan PDF",
         "Ekspor semua hasil perhitungan menjadi laporan PDF lengkap dengan identitas dan rumus yang digunakan.",
         "btn_fitur_pdf"),
    ]

    for col, icon_cls, icon, judul, deskripsi, key in fitur_list:
        with col:
            st.markdown(f"""
            <div class="fitur-card">
                <div class="fc-icon {icon_cls}">{icon}</div>
                <h4>{judul}</h4>
                <p>{deskripsi}</p>
            </div>
            """, unsafe_allow_html=True)
            st.button("Buka fitur →", key=key)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Riwayat perhitungan ──────────────────────────────────────────────────
    st.markdown("#### Riwayat perhitungan terakhir")

    riwayat_tampil = ambil_riwayat(user["id"], limit=5)

    if not riwayat_tampil:
        st.markdown("""
        <div style="text-align:center;padding:24px;color:#aaa;font-size:13px;
                    background:#f9f9f9;border-radius:12px">
            Belum ada perhitungan. Mulai dari salah satu fitur di atas!
        </div>
        """, unsafe_allow_html=True)
    else:
        icon_map = {
            "Simulasi Premi": ("🪙", "rw-icon-p"),
            "Bandingkan":     ("⚖️", "rw-icon-g"),
            "Peluang Hidup":  ("💓", "rw-icon-p"),
        }
        for r in riwayat_tampil:
            ikon, ikon_cls = icon_map.get(r["fitur"], ("📌", "rw-icon-g"))
            tanggal = r["created_at"][:16].replace("T", "  ")
            st.markdown(f"""
            <div class="rw-item">
                <div class="rw-icon {ikon_cls}">{ikon}</div>
                <div class="rw-info">
                    <div class="rw-name">{r['deskripsi']}</div>
                    <div class="rw-date">{tanggal}</div>
                </div>
                <div class="rw-val">{r['hasil']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Demo: tombol tambah riwayat contoh ───────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🧪 Demo — tambah data riwayat contoh"):
        st.caption("Ini hanya untuk demo. Nanti riwayat otomatis terisi dari hasil perhitungan.")
        if st.button("Tambah contoh riwayat"):
            simpan_riwayat(user["id"], "Simulasi Premi",
                           "Premi tabungan 15 tahun · usia 30 · bunga 6%",
                           "Rp 39.156.000")
            simpan_riwayat(user["id"], "Bandingkan",
                           "Perbandingan asuransi 10 tahun · usia 35",
                           "Selisih 4.1%")
            simpan_riwayat(user["id"], "Peluang Hidup",
                           "Peluang hidup sampai usia 75 · dari usia 40",
                           "72.3%")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER UTAMA
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.user is None:
    if st.session_state.halaman_auth == "register":
        halaman_register()
    else:
        halaman_login()
else:
    halaman_dashboard()
