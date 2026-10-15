"""Yeniden kullanılabilir arayüz bileşenleri."""

from contextlib import contextmanager
from typing import Iterator, Literal

import streamlit as st

Tone = Literal["neutral", "info", "success", "warning", "danger"]


def page_head(title: str, subtitle: str = "") -> None:
    """Her sayfanın tepesindeki başlık bloğu."""
    sub = f'<p class="page-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="page-head"><h1>{title}</h1>{sub}</div>',
        unsafe_allow_html=True,
    )


@contextmanager
def card(title: str = "") -> Iterator[None]:
    """Beyaz yüzeyli içerik kartı. `with card("Başlık"):` şeklinde kullanılır."""
    with st.container(border=True):
        if title:
            st.markdown(f'<div class="nt-card-title">{title}</div>', unsafe_allow_html=True)
        yield


def stat(label: str, value: str, hint: str = "") -> None:
    hint_html = f'<div class="nt-stat-hint">{hint}</div>' if hint else ""
    st.markdown(
        f"""
        <div class="nt-stat">
            <div class="nt-stat-label">{label}</div>
            <div class="nt-stat-value">{value}</div>
            {hint_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def note(text: str, tone: Tone = "neutral") -> None:
    """Streamlit'in st.info/st.warning kutularının sakin karşılığı."""
    st.markdown(f'<div class="nt-note {tone}">{text}</div>', unsafe_allow_html=True)


def badge(text: str, tone: Tone = "neutral") -> str:
    return f'<span class="nt-badge {tone}">{text}</span>'


def empty(text: str) -> None:
    st.markdown(f'<div class="nt-empty">{text}</div>', unsafe_allow_html=True)


def message_bubble(author: str, content: str, is_me: bool, timestamp: str = "") -> None:
    side = "me" if is_me else "them"
    meta = f"{author} · {timestamp}" if timestamp else author
    st.markdown(
        f"""
        <div class="nt-msg {side}">
            <div class="nt-msg-meta">{meta}</div>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_tone(risk_level: str) -> Tone:
    """Risk düzeyi etiketini semantik renge eşler."""
    mapping: dict[str, Tone] = {"Yüksek": "danger", "Orta": "warning", "Düşük": "success"}
    return mapping.get(risk_level, "neutral")


def disclaimer() -> None:
    note(
        "Bu ekran ön tarama ve karar destek amaçlıdır. Kesin tanı koymaz ve "
        "uzman değerlendirmesinin yerine geçmez.",
        "info",
    )
