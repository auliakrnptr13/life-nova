import streamlit as st
from database import init_db, register_user, login_user, simpan_riwayat, ambil_riwayat
from styles import LUMACTA_CSS

# ── Konfigurasi halaman ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lumacta",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Inisialisasi database ─────────────────────────────────────────────────────
init_db()

# ── Inject CSS ────────────────────────────────────────────────────────────────
st.markdown(LUMACTA_CSS, unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None          # None = belum login
if "halaman_auth" not in st.session_state:
    st.session_state.halaman_auth = "login"  # "login" atau "register"


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER UI
# ═══════════════════════════════════════════════════════════════════════════════

def navbar():
    user = st.session_state.user
    st.markdown(f"""
    <div class="lumacta-nav">
        <div class="brand">🌿 Lumacta</div>
        <div class="user-info">Halo, <strong>{user['nama']}</strong> &nbsp;·&nbsp; {user['email']}</div>
    </div>
    """, unsafe_allow_html=True)


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
