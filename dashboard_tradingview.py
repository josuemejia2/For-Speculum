from dataclasses import asdict
from pathlib import Path
import subprocess
from urllib.parse import quote_plus
import webbrowser

import pandas as pd
import streamlit as st

from domain.analysis import analizar_mercado, calcular_indicadores
from services import save_analysis_to_bitacora

CSV_FILE = Path("datos_ejemplo.csv")
INTERVAL_TO_TF = {
    "1": "1m",
    "5": "5m",
    "15": "15m",
    "30": "30m",
    "60": "1h",
    "240": "4h",
    "D": "1D",
}


def build_tradingview_url(symbol: str, interval: str, theme: str) -> str:
    return (
        "https://s.tradingview.com/widgetembed/"
        f"?symbol={quote_plus(symbol)}"
        f"&interval={quote_plus(interval)}"
        f"&theme={quote_plus(theme)}"
        "&style=1&locale=en&toolbarbg=%231f1f1f"
        "&enable_publishing=false&hide_top_toolbar=false"
        "&hide_side_toolbar=false&allow_symbol_change=true"
    )


def build_gocharting_url(symbol: str) -> str:
    # GoCharting suele cambiar parametros de query; el usuario puede ajustar URL manualmente.
    return f"https://gocharting.com/terminal?ticker={quote_plus(symbol)}"


def abrir_url_externa(url: str, browser_name: str) -> tuple[bool, str]:
    try:
        if browser_name == "Chrome":
            subprocess.Popen(["cmd", "/c", "start", "chrome", url], shell=False)
        elif browser_name == "Opera":
            subprocess.Popen(["cmd", "/c", "start", "opera", url], shell=False)
        else:
            webbrowser.open_new_tab(url)
        return True, ""
    except Exception as e:
        return False, str(e)


def cargar_df_crudo(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"])
    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"])
    return df


def preparar_df_robot(df_crudo: pd.DataFrame) -> pd.DataFrame:
    if df_crudo.empty:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"])

    df = df_crudo.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    for col in ("open", "high", "low", "close"):
        if col not in df.columns:
            df[col] = pd.NA
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "timestamp" not in df.columns:
        df["timestamp"] = pd.Timestamp.now()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)

    if df.empty:
        return df

    df_ind = calcular_indicadores(df)
    df_ind["tipo_vela"] = df_ind.apply(
        lambda r: "Entrada" if r["close"] > r["open"] else "Salida",
        axis=1,
    )
    return df_ind


def registrar_vela(path: Path, df_crudo: pd.DataFrame, open_v: float, high_v: float, low_v: float, close_v: float) -> None:
    nueva_fila = {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "open": float(open_v),
        "high": float(high_v),
        "low": float(low_v),
        "close": float(close_v),
    }

    if df_crudo.empty:
        actualizado = pd.DataFrame([nueva_fila])
    else:
        actualizado = df_crudo.copy()
        for col in actualizado.columns:
            if col not in nueva_fila:
                nueva_fila[col] = pd.NA
        for col in nueva_fila:
            if col not in actualizado.columns:
                actualizado[col] = pd.NA
        actualizado = pd.concat(
            [actualizado, pd.DataFrame([nueva_fila], columns=actualizado.columns)],
            ignore_index=True,
        )

    actualizado.to_csv(path, index=False)


def render_robot_dashboard(page_title: str = "Dashboard Sistema Quero + Robot", show_title: bool = True) -> None:
    if show_title:
        st.title(page_title)

    st.sidebar.header("Configuracion de grafica")
    symbol = st.sidebar.text_input("Simbolo", "BYBIT:BTCUSDT")
    interval = st.sidebar.selectbox("Temporalidad", ["1", "5", "15", "30", "60", "240", "D"])
    theme = st.sidebar.selectbox("Tema", ["dark", "light"])
    provider = st.sidebar.selectbox(
        "Proveedor",
        ["TradingView", "GoCharting", "URL personalizada"],
        index=0,
    )

    tv_url = build_tradingview_url(symbol=symbol, interval=interval, theme=theme)
    go_default = build_gocharting_url(symbol=symbol)

    if provider == "TradingView":
        chart_url = tv_url
    elif provider == "GoCharting":
        chart_url = st.sidebar.text_input("URL GoCharting", go_default)
    else:
        chart_url = st.sidebar.text_input("URL personalizada", go_default)

    st.sidebar.caption("Si el sitio bloquea iframe, abre la URL en navegador externo.")
    browser_choice = st.sidebar.selectbox(
        "Abrir externo con",
        ["Predeterminado", "Chrome", "Opera"],
        index=0,
    )
    if st.sidebar.button("Abrir grafica en navegador externo"):
        ok, msg = abrir_url_externa(chart_url, browser_choice)
        if ok:
            st.sidebar.success("Grafica abierta en navegador externo.")
        else:
            st.sidebar.error(f"No se pudo abrir: {msg}")

    st.sidebar.link_button("Abrir URL en nueva pestana", chart_url, use_container_width=True)

    st.sidebar.header("Entrada rapida de vela")
    open_v = st.sidebar.number_input("Open", value=0.0, step=0.1)
    high_v = st.sidebar.number_input("High", value=0.0, step=0.1)
    low_v = st.sidebar.number_input("Low", value=0.0, step=0.1)
    close_v = st.sidebar.number_input("Close", value=0.0, step=0.1)

    df_crudo = cargar_df_crudo(CSV_FILE)

    if st.sidebar.button("Registrar vela"):
        if high_v < max(open_v, close_v) or low_v > min(open_v, close_v):
            st.sidebar.error("High/Low invalidos para la vela.")
        else:
            registrar_vela(CSV_FILE, df_crudo, open_v, high_v, low_v, close_v)
            st.sidebar.success("Vela registrada en datos_ejemplo.csv")
            st.rerun()

    tf_robot = INTERVAL_TO_TF.get(interval, "5m")

    if st.sidebar.button("Verificar senal robot"):
        try:
            resultado = analizar_mercado(csv_path=CSV_FILE, symbol=symbol, timeframe=tf_robot)
            st.session_state["resultado_robot"] = asdict(resultado)
            st.sidebar.success(f"Senal: {resultado.signal} ({resultado.confidence}%)")
        except Exception as e:
            st.sidebar.error(f"Error al verificar: {e}")

    if st.sidebar.button("Guardar senal robot"):
        try:
            resultado = analizar_mercado(csv_path=CSV_FILE, symbol=symbol, timeframe=tf_robot)
            rutas = save_analysis_to_bitacora(resultado)
            st.session_state["resultado_robot"] = asdict(resultado)
            st.sidebar.success("Senal guardada en bitacora")
            for p in rutas:
                st.sidebar.caption(str(p))
        except Exception as e:
            st.sidebar.error(f"Error al guardar: {e}")

    df_robot = preparar_df_robot(cargar_df_crudo(CSV_FILE))
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Velas del sistema")
        if df_robot.empty:
            st.warning("No hay velas validas para mostrar.")
        else:
            cols = [
                "timestamp",
                "tipo_vela",
                "open",
                "high",
                "low",
                "close",
                "EMA_3",
                "EMA_9",
                "MACD_HIST",
            ]
            disponibles = [c for c in cols if c in df_robot.columns]
            vista = df_robot[disponibles].copy().tail(150)
            if "timestamp" in vista.columns:
                vista["timestamp"] = pd.to_datetime(vista["timestamp"], errors="coerce").dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            st.dataframe(vista, height=600, use_container_width=True)

        st.subheader("Resultado del robot")
        resultado_guardado = st.session_state.get("resultado_robot")

        if resultado_guardado is None:
            try:
                resultado_actual = analizar_mercado(csv_path=CSV_FILE, symbol=symbol, timeframe=tf_robot)
                resultado_guardado = asdict(resultado_actual)
            except Exception as e:
                st.info(f"Robot sin resultado aun: {e}")

        if resultado_guardado is not None:
            st.metric("Senal", resultado_guardado["signal"])
            st.metric("Confianza", f'{resultado_guardado["confidence"]}%')
            st.write(resultado_guardado["reason"])
            with st.expander("Detalle tecnico"):
                st.json(resultado_guardado)

    with col2:
        st.subheader(f"Grafico: {provider}")
        if provider != "TradingView":
            st.info(
                "GoCharting u otros sitios pueden bloquear embebido por seguridad (X-Frame-Options/CSP). "
                "Si no carga, usa 'Abrir grafica en navegador externo'."
            )

        safe_url = chart_url.replace('"', "%22")
        chart_html = f"""
        <iframe
            src="{safe_url}"
            width="100%"
            height="650"
            frameborder="0"
            allowfullscreen>
        </iframe>
        """
        st.components.v1.html(chart_html, height=670)


def main() -> None:
    st.set_page_config(layout="wide")
    render_robot_dashboard()


if __name__ == "__main__":
    main()
