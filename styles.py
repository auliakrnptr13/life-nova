LUMACTA_CSS = """
<style>
/* ── Brand colors ── */
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

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

/* ── Navbar ── */
.lumacta-nav {
    background: var(--green-dark);
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 12px;
    margin-bottom: 20px;
}
.lumacta-nav .brand {
    font-size: 20px;
    font-weight: 600;
    color: #EAF3DE;
    display: flex;
    align-items: center;
    gap: 8px;
}
.lumacta-nav .user-info {
    font-size: 13px;
    color: #C0DD97;
}

/* ── Auth card ── */
.auth-card {
    max-width: 420px;
    margin: 40px auto;
    background: white;
    border: 0.5px solid #e0e0e0;
    border-radius: 16px;
    padding: 32px;
}
.auth-logo {
    text-align: center;
    margin-bottom: 24px;
}
.auth-logo .logo-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: var(--green-dark);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    margin-bottom: 8px;
}
.auth-logo h2 {
    font-size: 22px;
    font-weight: 700;
    color: var(--green-dark);
    margin: 0;
}
.auth-logo p {
    font-size: 12px;
    color: #888;
    margin: 2px 0 0;
}

/* ── Tombol utama ── */
.stButton > button {
    background: var(--pink-dark) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    width: 100% !important;
    transition: opacity .15s;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── Tombol sekunder (outline hijau) ── */
.btn-green > button {
    background: var(--green-light) !important;
    color: var(--green-dark) !important;
    border: 1px solid var(--green-border) !important;
    border-radius: 8px !important;
}

/* ── Stat card ── */
.stat-card {
    background: white;
    border: 0.5px solid #e8e8e8;
    border-radius: 12px;
    padding: 14px 16px;
}
.stat-card .label {
    font-size: 11px;
    color: #888;
    margin-bottom: 4px;
}
.stat-card .value {
    font-size: 22px;
    font-weight: 600;
    color: #1a1a1a;
}
.stat-card .delta-green { font-size: 11px; color: var(--green-dark); margin-top: 2px; }
.stat-card .delta-pink  { font-size: 11px; color: var(--pink-dark);  margin-top: 2px; }

/* ── Fitur card ── */
.fitur-card {
    background: white;
    border: 0.5px solid #e8e8e8;
    border-radius: 12px;
    padding: 16px;
    height: 100%;
}
.fitur-card .fc-icon {
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    margin-bottom: 10px;
}
.fitur-card .fc-icon-p { background: var(--pink-light); }
.fitur-card .fc-icon-g { background: var(--green-light); }
.fitur-card h4 { font-size: 14px; font-weight: 600; margin: 0 0 6px; color: #1a1a1a; }
.fitur-card p  { font-size: 12px; color: #666; line-height: 1.55; margin: 0; }

/* ── Riwayat item ── */
.rw-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    background: #f9f9f9;
    border-radius: 8px;
    margin-bottom: 6px;
}
.rw-item .rw-icon {
    width: 28px; height: 28px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0;
}
.rw-item .rw-icon-p { background: var(--pink-light); }
.rw-item .rw-icon-g { background: var(--green-light); }
.rw-item .rw-info   { flex: 1; }
.rw-item .rw-name   { font-size: 12px; font-weight: 500; color: #1a1a1a; }
.rw-item .rw-date   { font-size: 10px; color: #aaa; }
.rw-item .rw-val    { font-size: 12px; font-weight: 600; color: var(--pink-dark); }

/* ── Welcome banner ── */
.welcome-banner {
    background: var(--pink-dark);
    border-radius: 12px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    color: white;
}
.welcome-banner .wb-name { font-size: 16px; font-weight: 600; }
.welcome-banner .wb-sub  { font-size: 11px; color: #F4C0D1; margin-top: 2px; }

/* ── Alert kustom ── */
.alert-success {
    background: var(--green-light);
    border-left: 3px solid var(--green-mid);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: var(--green-dark);
    margin: 8px 0;
}
.alert-error {
    background: #fff0f0;
    border-left: 3px solid #e24b4a;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #a32d2d;
    margin: 8px 0;
}
</style>
"""
