import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from dashboard_tradingview import render_robot_dashboard
from domain.analysis import analizar_mercado
from services import (
    backup_document,
    document_stats,
    layer_text,
    read_document,
    replace_document_layer,
    split_document_sections,
    split_document_layers,
)


ROOT = Path(__file__).resolve().parent
CSV_FILE = ROOT / "datos_ejemplo.csv"
BITACORA_FILE = ROOT / "bitacora.json"
BACKUP_DIR = ROOT / "document_backups"


@dataclass(frozen=True)
class MasterDoc:
    key: str
    title: str
    role: str
    path: Path
    state: str
    locked: bool = False


@dataclass(frozen=True)
class DocLayer:
    index: int
    title: str
    start: int
    end: int
    level: int
    kind: str


MASTER_DOCS = [
    MasterDoc(
        key="acta",
        title="Acta de Origen y Fe",
        role="Raiz sellada",
        path=Path(r"C:\Users\jonat\iCloudDrive\ACTA DE ORIGEN Y FE\ACTA DE ORIGEN Y FE.md"),
        state="Inmutable",
        locked=True,
    ),
    MasterDoc(
        key="paradigma",
        title="Paradigma",
        role="Marco universal",
        path=Path(os.getenv("PARADIGMA_MD_PATH", r"C:\Users\jonat\iCloudDrive\Paradigma\Paradigma.md")),
        state="Maestro",
    ),
    MasterDoc(
        key="root",
        title="Root Architecture",
        role="Mapa raiz del ecosistema",
        path=Path(r"C:\Users\jonat\iCloudDrive\Nuevas ideas_\Historial\Root Architecture.txt"),
        state="Arquitectura",
    ),
    MasterDoc(
        key="protocolo",
        title="Protocolo",
        role="Core Engine documental",
        path=Path(r"C:\Users\jonat\iCloudDrive\Protocolo\Protocolo.md"),
        state="Motor",
    ),
    MasterDoc(
        key="manual",
        title="Manual Quero",
        role="Mercado y reglas tecnicas",
        path=Path(r"C:\Users\jonat\iCloudDrive\Manual\Manual.md"),
        state="Operativo",
    ),
    MasterDoc(
        key="legacy",
        title="Legacy",
        role="Sistema de juego",
        path=Path(r"C:\Users\jonat\iCloudDrive\Legacy\Legacy.md"),
        state="Sistema",
    ),
    MasterDoc(
        key="botones",
        title="Botones iOS",
        role="Custodia movil",
        path=Path(r"C:\Users\jonat\iCloudDrive\Nuevas ideas_\Historial\Flujo de Botones del sistema quero(1).txt"),
        state="Flujo",
    ),
]


XMB_CATEGORIES = ["Sistema", "Motor", "Documentos", "Editor", "Custodia"]


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
        }
        body {
            background: radial-gradient(circle at top, #1a2538, #080a11 55%);
            color: #eceff4;
        }
        .main .block-container {
            padding-top: 1.2rem;
            max-width: 1480px;
        }
        [data-testid="stSidebar"] {
            background: #0f1521;
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        .stSidebar .stMarkdown p, .stSidebar .stMarkdown span {
            color: #c8d1e0;
        }
        h1, h2, h3, h4 {
            font-family: Inter, sans-serif;
            letter-spacing: 0.01em;
        }
        .cp-topbar {
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(16, 23, 35, 0.92);
            padding: 20px 24px;
            border-radius: 16px;
            margin-bottom: 18px;
            box-shadow: 0 18px 50px rgba(0,0,0,0.24);
        }
        .cp-eyebrow {
            color: #8ea3bf;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .cp-title {
            color: #f6f8fb;
            font-size: 36px;
            font-weight: 800;
            margin: 0;
            line-height: 1.05;
        }
        .cp-subtitle {
            color: #9ab1cc;
            font-size: 14px;
            margin: 10px 0 0 0;
        }
        .cp-card {
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(18, 28, 45, 0.78);
            border-radius: 16px;
            padding: 18px 20px;
            min-height: 144px;
            margin-bottom: 14px;
        }
        .cp-card h3 {
            margin: 4px 0 8px 0;
            font-size: 18px;
            color: #eef3fb;
        }
        .cp-card p {
            margin: 0;
            color: #a5b3d1;
            font-size: 13px;
            line-height: 1.5;
        }
        .cp-pill {
            display: inline-block;
            border-radius: 999px;
            padding: 4px 11px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .cp-pill-ok {
            color: #ffffff;
            background: #2d8f5d;
        }
        .cp-pill-warn {
            color: #ffffff;
            background: #b58b1c;
        }
        .cp-pill-red {
            color: #ffffff;
            background: #bf4335;
        }
        .cp-path {
            color: #8c9eba;
            font-size: 12px;
            margin-top: 10px;
            word-break: break-word;
        }
        .cp-section-title {
            color: #f4f7ff;
            font-size: 20px;
            font-weight: 800;
            margin: 22px 0 12px 0;
        }
        .cp-signal {
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(10, 18, 31, 0.92);
            border-radius: 16px;
            padding: 18px 20px;
            margin-bottom: 18px;
        }
        .cp-signal strong {
            color: #f4f7ff;
        }
        .xmb-stage {
            background: linear-gradient(180deg, rgba(14,26,44,0.95), rgba(5,10,18,0.8));
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 24px 80px rgba(0,0,0,0.25);
        }
        .xmb-kicker {
            color: #82a1d4;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .xmb-title {
            color: #ffffff;
            font-size: 34px;
            font-weight: 900;
            margin: 0 0 8px 0;
        }
        .xmb-copy {
            color: #9fb1cf;
            font-size: 14px;
            margin: 0;
            line-height: 1.7;
        }
        .xmb-menu {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 18px 0 20px 0;
        }
        .xmb-button {
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.05);
            padding: 14px 18px;
            min-width: 130px;
            text-align: center;
            color: #dfe7f3;
            font-weight: 700;
            letter-spacing: 0.02em;
        }
        .xmb-button.selected {
            background: rgba(45, 143, 93, 0.22);
            border-color: rgba(45, 143, 93, 0.75);
            color: #ffffff;
        }
        .xmb-card {
            border: 1px solid rgba(255,255,255,0.07);
            background: rgba(17, 28, 42, 0.88);
            border-radius: 16px;
            padding: 18px;
            min-height: 150px;
            margin-bottom: 16px;
        }
        .xmb-card h3 {
            color: #f7fbff;
            font-size: 18px;
            margin: 0 0 10px 0;
        }
        .xmb-card p {
            color: #a4b1ce;
            font-size: 13px;
            margin: 0;
            line-height: 1.6;
        }
        .xmb-tag {
            display: inline-block;
            color: #ffffff;
            background: rgba(45, 143, 93, 0.9);
            border-radius: 999px;
            padding: 4px 11px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .stButton > button {
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.07);
            color: #e9eef6;
            font-weight: 700;
            min-height: 46px;
            padding: 0 18px;
        }
        .stButton > button:hover {
            border-color: rgba(45, 143, 93, 0.65);
            color: #ffffff;
            background: rgba(45, 143, 93, 0.16);
        }
        .stTextInput>div>div>input, .stSelectbox>div>div>div>select, .stTextArea>div>div>textarea {
            background: rgba(255,255,255,0.06);
            color: #f4f7ff;
            border: 1px solid rgba(255,255,255,0.12);
        }
        """,
        unsafe_allow_html=True,
    )




    if layers:
        return layers

    return [DocLayer(0, "Documento completo", 0, len(lines), 0, "full")]


def _layer_text(text: str, layer: DocLayer) -> str:
    return layer_text(text, layer)


def _replace_layer(text: str, layer: DocLayer, new_layer_text: str) -> str:
    return replace_document_layer(text, layer, new_layer_text)


def _safe_name(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return clean.strip("_") or "documento"


def _backup_document(doc: MasterDoc) -> Path:
    return backup_document(doc.path, BACKUP_DIR / doc.key)


def _doc_stats(path: Path) -> dict[str, Any]:
    return document_stats(path)


def _format_mtime(path: Path) -> str:
    if not path.exists():
        return "No encontrado"
    return pd.Timestamp.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _csv_health(path: Path) -> tuple[int, str]:
    if not path.exists():
        return 0, "Falta datos_ejemplo.csv"

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        return 0, f"CSV invalido: {exc}"

    if df.empty:
        return 0, "CSV vacio"

    df.columns = [c.strip().lower() for c in df.columns]
    if "close" not in df.columns:
        return len(df), "Falta columna close"

    closes = pd.to_numeric(df["close"], errors="coerce").dropna()
    if closes.empty:
        return len(df), "Sin cierres validos"

    min_close = float(closes.min())
    max_close = float(closes.max())
    if min_close > 0 and max_close / min_close > 100:
        return len(df), "Escalas mezcladas"

    return len(df), "Datos coherentes"


def _status_pill(label: str, state: str = "ok") -> str:
    css = "cp-pill-ok" if state == "ok" else "cp-pill-red" if state == "red" else "cp-pill-warn"
    return f'<span class="cp-pill {css}">{label}</span>'


def _header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="cp-topbar">
            <div class="cp-eyebrow">{kicker}</div>
            <h1 class="cp-title">{title}</h1>
            <p class="cp-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _doc_card(doc: MasterDoc) -> None:
    stats = _doc_stats(doc.path)
    if stats["exists"]:
        pill = _status_pill(doc.state, "warn" if doc.locked else "ok")
        meta = f"{stats['lines']} lineas - actualizado {_format_mtime(doc.path)}"
    else:
        pill = _status_pill("Falta", "red")
        meta = "Documento no encontrado"

    lock_text = "Solo lectura" if doc.locked else "Editable por capas"
    st.markdown(
        f"""
        <div class="cp-card">
            {pill}
            <h3>{doc.title}</h3>
            <p>{doc.role}</p>
            <div class="cp-path">{meta}</div>
            <div class="cp-path">{lock_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _xmb_category_button(category: str) -> None:
    selected = st.session_state.get("xmb_category", "Sistema") == category
    label = f"[{category}]" if selected else category
    if st.button(label, width="stretch", key=f"xmb_{category}"):
        st.session_state["xmb_category"] = category
        st.rerun()


def _chunks(items: list[Any], size: int) -> list[list[Any]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def _xmb_option(title: str, subtitle: str, tag: str) -> None:
    st.markdown(
        f"""
        <div class="xmb-card">
            <span class="xmb-tag">{tag}</span>
            <h3>{title}</h3>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_xmb() -> None:
    if "xmb_category" not in st.session_state:
        st.session_state["xmb_category"] = "Sistema"

    st.markdown(
        """
        <div class="xmb-stage">
            <div class="xmb-kicker">Quero Control Panel</div>
            <div class="xmb-title">Interfaz tipo XMB / PS3</div>
            <p class="xmb-copy">Panel multifunción: navega, ejecuta acciones y abre cada módulo desde un solo lugar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(len(XMB_CATEGORIES))
    for col, category in zip(cols, XMB_CATEGORIES):
        with col:
            _xmb_category_button(category)

    current = st.session_state.get("xmb_category", "Sistema")
    st.markdown(f'<div class="cp-section-title">{current}</div>', unsafe_allow_html=True)

    if current == "Sistema":
        found_docs = sum(1 for doc in MASTER_DOCS if doc.path.exists())
        candle_count, csv_state = _csv_health(CSV_FILE)
        bitacora_count = len(_load_json_list(BITACORA_FILE))

        metric_cols = st.columns(4)
        metric_cols[0].metric("Documentos", f"{found_docs}/{len(MASTER_DOCS)}")
        metric_cols[1].metric("Velas CSV", candle_count)
        metric_cols[2].metric("Bitacora", bitacora_count)
        metric_cols[3].metric("Salud CSV", csv_state)

        action_cols = st.columns(5)
        actions = [
            ("Robot", "Resumen de señal y tablero rápido.", "Robot"),
            ("Documentos", "Biblioteca maestra y lectura estructurada.", "Documentos"),
            ("Editor", "Edición por capas con backup automático.", "Editor"),
            ("Paradigma", "Marco universal para el sistema.", "Paradigma"),
            ("Custodia", "Backups, bitácoras y estado de seguridad.", "Custodia"),
        ]
        for col, (title, subtitle, page) in zip(action_cols, actions):
            with col:
                _xmb_option(title, subtitle, "ACCIÓN")
                if st.button(f"Abrir {title}", key=f"xmb_open_{page}"):
                    st.session_state["cp_page"] = page
                    st.rerun()

    elif current == "Motor":
        try:
            resultado = analizar_mercado(csv_path=CSV_FILE)
            st.markdown(
                f"""
                <div class="cp-signal">
                    {_status_pill(resultado.signal, "ok" if resultado.signal != "NO_TRADE" else "warn")}
                    <strong> Confianza {resultado.confidence}%</strong>
                    <div class="cp-path">{resultado.reason}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except Exception as exc:
            st.warning(f"Robot sin resultado: {exc}")

        button_cols = st.columns(3)
        with button_cols[0]:
            if st.button("Verificar señal"):
                st.session_state["cp_page"] = "Robot"
                st.rerun()
        with button_cols[1]:
            if st.button("Abrir robot"):
                st.session_state["cp_page"] = "Robot"
                st.rerun()
        with button_cols[2]:
            if st.button("Actualizar datos"):
                st.experimental_rerun()

    elif current == "Documentos":
        for row_docs in _chunks(MASTER_DOCS, 3):
            cols = st.columns(len(row_docs))
            for col, doc in zip(cols, row_docs):
                with col:
                    _doc_card(doc)
        if st.button("Abrir biblioteca", key="open_library"):
            st.session_state["cp_page"] = "Documentos"
            st.rerun()

    elif current == "Editor":
        st.info("El editor crea una copia de seguridad antes de cada guardado. El Acta está bloqueada.")
        if st.button("Ir al editor por capas", key="open_editor"):
            st.session_state["cp_page"] = "Editor"
            st.rerun()

    elif current == "Custodia":
        backup_count = len(list(BACKUP_DIR.rglob("*"))) if BACKUP_DIR.exists() else 0
        col1, col2 = st.columns(2)
        col1.metric("Backups locales", backup_count)
        col2.metric("Carpeta", "document_backups")
        st.code(
            "AGREGAR -> contenido nuevo\n"
            "EDITAR -> cambio local\n"
            "RECONFIGURAR -> cambio de arquitectura\n"
            "ENVIAR -> reconstruccion completa",
            language="text",
        )


def render_documentos(selected_key: str | None = None) -> None:
    _header(
        "Biblioteca",
        "Documentos Maestros",
        "Lectura estructurada de las fuentes principales del ecosistema Quero.",
    )

    keys = [doc.key for doc in MASTER_DOCS]
    labels = {doc.key: doc.title for doc in MASTER_DOCS}
    default_key = selected_key if selected_key in keys else keys[0]
    current_key = st.selectbox(
        "Documento",
        options=keys,
        index=keys.index(default_key),
        format_func=lambda key: labels[key],
    )
    doc = next(item for item in MASTER_DOCS if item.key == current_key)

    if not doc.path.exists():
        st.error(f"No se encontro: {doc.path}")
        return

    text = read_document(doc.path)
    stats = document_stats(doc.path)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lineas", stats["lines"])
    col2.metric("Caracteres", stats["chars"])
    col3.metric("Titulos", stats["headings"])
    col4.metric("Estado", doc.state)

    st.caption(str(doc.path))

    query = st.text_input("Filtrar", "")
    sections = split_document_sections(text)

    if query.strip():
        q = query.lower()
        sections = [(title, body) for title, body in sections if q in title.lower() or q in body.lower()]

    if sections:
        for title, body in sections:
            with st.expander(title if title else "Seccion", expanded=False):
                st.markdown(body if body else "_Sin contenido_")
    else:
        st.text_area("Contenido", text, height=620)

    with st.expander("Markdown completo", expanded=False):
        st.markdown(text)


def render_editor() -> None:
    _header(
        "Editor",
        "Edicion por capas",
        "Selecciona un documento, edita una capa y guarda con backup automatico.",
    )

    keys = [doc.key for doc in MASTER_DOCS]
    labels = {doc.key: doc.title for doc in MASTER_DOCS}
    current_key = st.selectbox("Documento", options=keys, format_func=lambda key: labels[key])
    doc = next(item for item in MASTER_DOCS if item.key == current_key)

    if not doc.path.exists():
        st.error(f"No se encontro: {doc.path}")
        return

    text = read_document(doc.path)
    layers = split_document_layers(text)
    stats = document_stats(doc.path)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lineas", stats["lines"])
    col2.metric("Capas", len(layers))
    col3.metric("Estado", "Bloqueado" if doc.locked else "Editable")
    col4.metric("Actualizado", _format_mtime(doc.path))

    if doc.locked:
        st.warning("Este documento esta marcado como inmutable. Puedes leerlo por capas, pero no guardarlo.")
    else:
        st.info("Al guardar, se crea una copia en document_backups antes de escribir sobre el archivo original.")

    layer_index = st.selectbox(
        "Capa",
        options=[layer.index for layer in layers],
        format_func=lambda index: f"{index + 1}. {layers[index].title}",
    )
    layer = layers[layer_index]
    original_layer_text = _layer_text(text, layer)

    st.caption(f"{doc.path} | lineas {layer.start + 1}-{layer.end} | tipo {layer.kind}")

    with st.form(key=f"edit_{doc.key}_{layer.index}"):
        edited = st.text_area("Contenido de la capa", value=original_layer_text, height=460)
        confirm = st.text_input("Para guardar escribe GUARDAR", value="")
        submitted = st.form_submit_button("Guardar capa con backup", disabled=doc.locked)

    if submitted:
        if confirm.strip().upper() != "GUARDAR":
            st.error("Guardado cancelado. Escribe GUARDAR para confirmar.")
            return
        if edited == original_layer_text:
            st.info("No hay cambios que guardar.")
            return

        backup_path = _backup_document(doc)
        new_text = _replace_layer(text, layer, edited)
        _write_text(doc.path, new_text)
        st.success(f"Capa guardada. Backup creado en: {backup_path}")

    with st.expander("Vista previa de la capa", expanded=False):
        st.markdown(edited if "edited" in locals() else original_layer_text)


def render_paradigma() -> None:
    render_documentos(selected_key="paradigma")


def main() -> None:
    st.set_page_config(layout="wide", page_title="Quero Control Panel")
    _inject_styles()

    pages = ["Control", "Robot", "Documentos", "Editor", "Paradigma"]
    if "cp_page" not in st.session_state:
        st.session_state["cp_page"] = "Control"

    current = st.sidebar.radio(
        "Navegacion",
        options=pages,
        index=pages.index(st.session_state["cp_page"]) if st.session_state["cp_page"] in pages else 0,
    )
    st.session_state["cp_page"] = current

    st.sidebar.markdown("---")
    st.sidebar.caption("Llave Sagrada / Sistema Quero")
    st.sidebar.caption(str(ROOT))

    if current == "Control":
        render_xmb()
        return
    if current == "Robot":
        render_robot_dashboard(page_title="Robot", show_title=True)
        return
    if current == "Documentos":
        render_documentos()
        return
    if current == "Editor":
        render_editor()
        return
    if current == "Paradigma":
        render_paradigma()
        return


if __name__ == "__main__":
    main()
