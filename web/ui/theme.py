"""Tasarım sistemi: renk/tipografi/boşluk token'ları ve global stil."""

import streamlit as st

APP_NAME = "NeuroTrack AI"
APP_SUBTITLE = "Otizm Takip ve Karar Destek Sistemi"

CSS = """
<style>
:root {
    --canvas: #F6F8FA;
    --surface: #FFFFFF;
    --surface-sunken: #F1F5F9;
    --ink: #0F172A;
    --ink-muted: #64748B;
    --ink-subtle: #94A3B8;
    --line: #E2E8F0;
    --line-strong: #CBD5E1;

    --primary: #0F766E;
    --primary-hover: #0B5F58;
    --primary-soft: #ECFDF5;
    --primary-line: #99F6E4;

    --info: #0369A1;
    --info-soft: #EFF6FF;
    --success: #15803D;
    --success-soft: #F0FDF4;
    --warning: #B45309;
    --warning-soft: #FFFBEB;
    --danger: #B91C1C;
    --danger-soft: #FEF2F2;

    --radius-sm: 8px;
    --radius: 12px;
    --radius-lg: 16px;

    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 24px;
    --space-6: 32px;

    --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
    --shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 8px 24px -12px rgba(15, 23, 42, 0.12);

    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif;
}

html, body, [class*="css"], .stApp { font-family: var(--font); }

.stApp { background: var(--canvas); color: var(--ink); }

.block-container {
    padding-top: var(--space-6);
    padding-bottom: var(--space-6);
    max-width: 1180px;
}

/* --- Tipografi ölçeği --- */
h1, h2, h3, h4 { color: var(--ink); letter-spacing: -0.02em; }
h1 { font-size: 1.75rem; font-weight: 650; }
h2 { font-size: 1.35rem; font-weight: 650; }
h3 { font-size: 1.05rem; font-weight: 620; }
p, li, label, .stMarkdown { color: var(--ink); }

/* --- Sayfa başlığı --- */
.page-head { margin-bottom: var(--space-5); }
.page-head h1 { margin: 0 0 6px 0; }
.page-head .page-sub {
    color: var(--ink-muted);
    font-size: 0.95rem;
    line-height: 1.55;
    max-width: 68ch;
    margin: 0;
}

/* --- Kart --- */
.nt-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);
    padding: var(--space-5);
    box-shadow: var(--shadow-sm);
    margin-bottom: var(--space-4);
}
.nt-card-title {
    font-size: 0.78rem;
    font-weight: 650;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--ink-subtle);
    margin-bottom: var(--space-3);
}

/* --- İstatistik kutusu --- */
.nt-stat {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: var(--space-4);
    box-shadow: var(--shadow-sm);
    height: 100%;
}
.nt-stat-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--ink-subtle);
    margin-bottom: 6px;
}
.nt-stat-value {
    font-size: 1.65rem;
    font-weight: 660;
    line-height: 1.15;
    letter-spacing: -0.02em;
    color: var(--ink);
    font-variant-numeric: tabular-nums;
}
.nt-stat-hint { font-size: 0.8rem; color: var(--ink-muted); margin-top: 6px; }

/* --- Rozet --- */
.nt-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 620;
    border: 1px solid transparent;
}
.nt-badge.neutral { background: var(--surface-sunken); color: var(--ink-muted); border-color: var(--line); }
.nt-badge.success { background: var(--success-soft); color: var(--success); border-color: #BBF7D0; }
.nt-badge.warning { background: var(--warning-soft); color: var(--warning); border-color: #FDE68A; }
.nt-badge.danger  { background: var(--danger-soft);  color: var(--danger);  border-color: #FECACA; }
.nt-badge.info    { background: var(--info-soft);    color: var(--info);    border-color: #BFDBFE; }

/* --- Uyarı şeridi --- */
.nt-note {
    border-left: 3px solid var(--line-strong);
    background: var(--surface-sunken);
    padding: var(--space-3) var(--space-4);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    font-size: 0.875rem;
    line-height: 1.6;
    color: var(--ink-muted);
    margin-bottom: var(--space-4);
}
.nt-note.info    { border-color: var(--info);    background: var(--info-soft);    color: #1E3A5F; }
.nt-note.warning { border-color: var(--warning); background: var(--warning-soft); color: #78350F; }
.nt-note.danger  { border-color: var(--danger);  background: var(--danger-soft);  color: #7F1D1D; }
.nt-note.success { border-color: var(--success); background: var(--success-soft); color: #14532D; }

/* --- Boş durum --- */
.nt-empty {
    border: 1px dashed var(--line-strong);
    border-radius: var(--radius);
    padding: var(--space-6) var(--space-5);
    text-align: center;
    color: var(--ink-muted);
    font-size: 0.9rem;
    background: var(--surface);
}

/* --- Sohbet balonu --- */
.nt-msg { max-width: 78%; padding: 10px 14px; border-radius: 14px; margin-bottom: 10px; font-size: 0.9rem; line-height: 1.55; }
.nt-msg .nt-msg-meta { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.03em; text-transform: uppercase; opacity: 0.65; margin-bottom: 4px; }
.nt-msg.them { background: var(--surface); border: 1px solid var(--line); color: var(--ink); border-bottom-left-radius: 4px; }
.nt-msg.me { background: var(--primary); color: #FFFFFF; margin-left: auto; border-bottom-right-radius: 4px; }
.nt-msg.me .nt-msg-meta { opacity: 0.8; }

/* --- Sidebar --- */
section[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] .block-container { padding-top: var(--space-5); }
.nt-brand { display: flex; align-items: center; gap: 10px; margin-bottom: 2px; }
.nt-brand-mark {
    width: 30px; height: 30px; border-radius: 8px; flex: 0 0 30px;
    background: var(--primary); color: #FFF;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem; letter-spacing: -0.03em;
}
.nt-brand-name { font-size: 1rem; font-weight: 660; letter-spacing: -0.02em; color: var(--ink); }
.nt-brand-sub { font-size: 0.72rem; color: var(--ink-subtle); margin: 0 0 var(--space-5) 40px; line-height: 1.4; }

.nt-user { border-top: 1px solid var(--line); padding-top: var(--space-4); margin-top: var(--space-2); }
.nt-user-name { font-size: 0.875rem; font-weight: 620; color: var(--ink); }
.nt-user-role { font-size: 0.75rem; color: var(--ink-muted); margin-top: 2px; }

.nt-navlabel {
    font-size: 0.7rem; font-weight: 650; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--ink-subtle); margin: var(--space-4) 0 var(--space-2) 2px;
}

/* Navigasyon öğeleri arasındaki dikey ritmi sıkılaştır (varsayılan 1rem çok havalı) */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] { gap: 0.25rem; }

/* Sidebar navigasyon butonları: sol hizalı, sade, aktif olan vurgulu */
section[data-testid="stSidebar"] div.stButton > button {
    width: 100%;
    justify-content: flex-start;
    text-align: left;
    background: transparent;
    border: 1px solid transparent;
    color: var(--ink-muted);
    font-weight: 550;
    font-size: 0.875rem;
    padding: 7px 10px;
    min-height: 0;
    border-radius: var(--radius-sm);
    box-shadow: none;
    transition: background 120ms ease, color 120ms ease;
}
/* Etiket, buton içinde div > span > markdown zincirinde durur. Sola yaslamak için
   butona hizalama vermek yetmez; ara sarmalayıcıların da tam genişlik alması gerekir. */
section[data-testid="stSidebar"] div.stButton > button > div,
section[data-testid="stSidebar"] div.stButton > button span,
section[data-testid="stSidebar"] div.stButton > button div[data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] div.stButton > button p {
    width: 100%;
    justify-content: flex-start;
    text-align: left;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: var(--surface-sunken);
    color: var(--ink);
    border-color: transparent;
}
section[data-testid="stSidebar"] div.stButton > button[kind^="primary"] {
    background: var(--primary-soft);
    color: var(--primary);
    font-weight: 640;
    box-shadow: inset 2px 0 0 var(--primary);
}

/* --- Ana içerik butonları: gerçek hiyerarşi ---
   kind^= kullanılır: form submit butonları kind="primaryFormSubmit" alır. */
div.stButton > button[kind^="primary"], div.stFormSubmitButton > button[kind^="primary"] {
    background: var(--primary);
    color: #FFFFFF;
    border: 1px solid var(--primary);
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 0.875rem;
    padding: 0.5rem 1.1rem;
    box-shadow: var(--shadow-sm);
    transition: background 120ms ease;
}
div.stButton > button[kind^="primary"]:hover, div.stFormSubmitButton > button[kind^="primary"]:hover {
    background: var(--primary-hover);
    border-color: var(--primary-hover);
    color: #FFFFFF;
}
div.stButton > button[kind^="secondary"], div.stFormSubmitButton > button[kind^="secondary"] {
    background: var(--surface);
    color: var(--ink);
    border: 1px solid var(--line-strong);
    border-radius: var(--radius-sm);
    font-weight: 550;
    font-size: 0.875rem;
    padding: 0.5rem 1.1rem;
    box-shadow: none;
}
div.stButton > button[kind^="secondary"]:hover, div.stFormSubmitButton > button[kind^="secondary"]:hover {
    background: var(--surface-sunken);
    color: var(--ink);
    border-color: var(--ink-subtle);
}
div.stButton > button:focus-visible, div.stFormSubmitButton > button:focus-visible {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
}

/* --- Form alanları --- */
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input {
    border-radius: var(--radius-sm) !important;
    border-color: var(--line-strong) !important;
    font-size: 0.9rem;
}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.12) !important;
}
div[data-testid="stWidgetLabel"] label, .stRadio label, .stSelectbox label {
    font-size: 0.875rem !important;
    font-weight: 550 !important;
    color: var(--ink) !important;
}
div[data-baseweb="select"] > div { border-radius: var(--radius-sm); border-color: var(--line-strong); }

/* --- Sağ altta yüzen Deva sohbet balonu ---
   st.container(key="x") DOM'a .st-key-x sınıfını basar; sabitleme buna dayanır. */
.st-key-deva_fab {
    position: fixed;
    right: 24px;
    bottom: 24px;
    z-index: 1000;
    width: auto !important;
}
.st-key-deva_fab button {
    border-radius: 999px !important;
    padding: 0.7rem 1.25rem !important;
    box-shadow: 0 8px 24px rgba(15, 118, 110, 0.35) !important;
}

.st-key-deva_panel {
    position: fixed;
    right: 24px;
    bottom: 24px;
    z-index: 1000;
    width: 370px !important;
    max-height: 72vh;
    overflow-y: auto;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);
    box-shadow: 0 16px 48px rgba(15, 23, 42, 0.18);
    padding: var(--space-4);
}
.deva-widget-title {
    font-size: 0.95rem;
    font-weight: 660;
    color: var(--ink);
    padding-top: 6px;
}
.st-key-deva_close_btn button { padding: 0.25rem 0.5rem !important; min-height: 0 !important; }

/* Sohbet geçmişi panel içinde kendi içinde kaydırılır */
.st-key-deva_log {
    max-height: 300px;
    overflow-y: auto;
    padding: var(--space-2) 2px;
    margin-bottom: var(--space-2);
}
.st-key-deva_panel .nt-msg { max-width: 92%; font-size: 0.85rem; }

/* Dar ekranda panel taşmasın */
@media (max-width: 640px) {
    .st-key-deva_panel {
        width: calc(100vw - 32px) !important;
        right: 16px;
        bottom: 16px;
        max-height: 70vh;
    }
    .st-key-deva_fab { right: 16px; bottom: 16px; }
}

/* --- Tablo / sekme --- */
div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }
button[data-baseweb="tab"] { font-weight: 580; font-size: 0.9rem; }
div[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); }
hr { border-color: var(--line); }
</style>
"""


def page_config() -> None:
    st.set_page_config(
        page_title=f"{APP_NAME} — {APP_SUBTITLE}",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hide_sidebar() -> None:
    """Giriş/kayıt ekranlarında navigasyon yoktur; boş sidebar gösterilmez."""
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"], div[data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
