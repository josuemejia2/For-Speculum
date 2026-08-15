from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from control_plane import MASTER_DOCS
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from domain.analysis import analizar_mercado, calcular_indicadores
from services import (
    add_candle,
    backup_document,
    document_stats,
    layer_text,
    load_market_df,
    prepare_table_df,
    read_document,
    replace_document_layer,
    save_analysis_to_bitacora,
    split_document_layers,
    write_document,
)

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
DEFAULT_PARADIGMA_CANDIDATES = [
    Path("Paradigma.md"),
    Path(r"C:\Users\jonat\iCloudDrive\Paradigma\Paradigma.md"),
]

BACKUP_DIR = Path("document_backups")

POS_COLOR = "#1F7A3A"
NEG_COLOR = "#B23A3A"
MID_COLOR = "#B08A00"
NEUTRAL_BG = "#F5F7FA"
CARD_BG = "#FFFFFF"

@dataclass(frozen=True)
class DocLayer:
    index: int
    title: str
    start: int
    end: int
    level: int
    kind: str


def _read_text(path: Path) -> str:
    return read_document(path)


def _doc_stats(path: Path) -> dict[str, int]:
    return document_stats(path)


def _backup_document(path: Path) -> Path:
    return backup_document(path, BACKUP_DIR)


def _write_text(path: Path, text: str) -> None:
    return write_document(path, text)


def _split_layers(text: str) -> list[DocLayer]:
    repo_layers = split_document_layers(text)
    if repo_layers:
        return [DocLayer(l.index, l.title, l.start, l.end, l.level, l.kind) for l in repo_layers]
    return [DocLayer(0, "Documento completo", 0, len(text.splitlines()), 0, "full")]


def _layer_text(text: str, layer: DocLayer) -> str:
    return layer_text(text, layer)


def _replace_layer(text: str, layer: DocLayer, new_layer_text: str) -> str:
    return replace_document_layer(text, layer, new_layer_text)


def chip_style(state: str) -> str:
    if state == "positive":
        bg = POS_COLOR
    elif state == "negative":
        bg = NEG_COLOR
    else:
        bg = MID_COLOR
    return (
        f"background: {bg}; color: #ffffff; padding: 4px 10px; "
        "border-radius: 8px; font-weight: 700;"
    )


def build_app_stylesheet() -> str:
    return """
    QWidget {
        background: #08101f;
        color: #d9e3f2;
        font-size: 13px;
        font-family: Segoe UI, Arial, sans-serif;
    }
    QMainWindow {
        background: #08101f;
    }
    QFrame#heroCard, QFrame#panelCard, QFrame#statusPanel {
        background: rgba(18, 32, 53, 0.95);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
    }
    QLabel#heroTitle {
        font-size: 28px;
        font-weight: 900;
        color: #f4f7ff;
    }
    QLabel#legendText {
        color: #9ab0d0;
        font-size: 12px;
    }
    QPushButton {
        background: rgba(255,255,255,0.08);
        color: #e9f0fb;
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 14px;
        padding: 10px 16px;
        font-weight: 700;
        min-height: 44px;
    }
    QPushButton:hover {
        background: rgba(45, 143, 93, 0.18);
    }
    QPushButton#btnPositive {
        background: #2d8f5d;
        color: #ffffff;
        border: 1px solid #1f6f44;
    }
    QPushButton#btnPositive:hover {
        background: #3aa473;
    }
    QPushButton#btnNegative {
        background: #bf4335;
        color: #ffffff;
        border: 1px solid #942f27;
    }
    QPushButton#btnNegative:hover {
        background: #d15b4a;
    }
    QPushButton#btnMid {
        background: #a07e00;
        color: #ffffff;
        border: 1px solid #7a6500;
    }
    QPushButton#btnMid:hover {
        background: #b48f0f;
    }
    QLineEdit, QComboBox, QPlainTextEdit, QListWidget, QTableWidget {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 12px;
        color: #eef4fd;
    }
    QComboBox, QLineEdit {
        min-height: 38px;
    }
    QTableWidget::item:selected {
        background: rgba(45, 143, 93, 0.2);
        color: #ffffff;
    }
    QHeaderView::section {
        background: rgba(255,255,255,0.06);
        color: #c8d6e7;
        border: none;
        padding: 8px;
    }
    QListWidget {
        background: rgba(9,16,31,0.95);
        border: none;
    }
    QListWidget::item {
        padding: 14px 10px;
        margin: 4px 0;
    }
    QListWidget::item:selected {
        background: rgba(45, 143, 93, 0.22);
        color: #ffffff;
    }
    """


def build_gocharting_url(symbol: str) -> str:
    return f"https://gocharting.com/terminal?ticker={quote_plus(symbol)}"


def load_raw_df(path: Path = CSV_FILE) -> pd.DataFrame:
    return load_market_df(path)


def append_candle(open_v: float, high_v: float, low_v: float, close_v: float, path: Path = CSV_FILE) -> None:
    return add_candle(open_v, high_v, low_v, close_v, path)


def prepare_df_for_table(path: Path = CSV_FILE) -> pd.DataFrame:
    return prepare_table_df(load_raw_df(path))


def split_markdown_sections(md_text: str) -> list[tuple[str, str]]:
    lines = md_text.splitlines()
    sections: list[tuple[str, str]] = []
    current_title = "Resumen"
    current_lines: list[str] = []

    for line in lines:
        if re.match(r"^\s*#{1,3}\s+", line):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
                current_lines = []
            current_title = re.sub(r"^\s*#{1,3}\s+", "", line).strip()
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return [(t, b) for t, b in sections if t or b]


class HomePage(QWidget):
    def __init__(self, go_robot, go_paradigma, go_documentos, go_editor):
        super().__init__()
        root = QVBoxLayout(self)

        hero = QFrame()
        hero.setObjectName("heroCard")
        hero.setFrameShape(QFrame.StyledPanel)
        hero_layout = QVBoxLayout(hero)
        title = QLabel("Quero Control Plane")
        title.setObjectName("heroTitle")
        subtitle = QLabel(
            "Panel multifunción en estilo consola: selecciona módulos, ejecuta acciones y accede a tu sistema desde un menú rápido."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #9db5d8; font-size: 13px;")
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        root.addWidget(hero)

        menu = QHBoxLayout()
        menu.setSpacing(14)
        for label, callback, role in [
            ("Robot", go_robot, "btnPositive"),
            ("Documentos", go_documentos, "btnMid"),
            ("Editor", go_editor, "btnMid"),
            ("Paradigma", go_paradigma, "btnMid"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName(role)
            btn.setMinimumHeight(46)
            btn.clicked.connect(callback)
            menu.addWidget(btn)
        root.addLayout(menu)

        status = QLabel(
            "Navegación XMB: Sistema > Robot > Documentos > Editor > Paradigma. Usa el menu para abrir cada área con un solo clic."
        )
        status.setWordWrap(True)
        status.setStyleSheet("color: #9ab0cf; margin-top: 10px;")
        root.addWidget(status)

        quick_frame = QFrame()
        quick_frame.setObjectName("panelCard")
        quick_layout = QHBoxLayout(quick_frame)
        for label, subtitle in [
            ("Análisis", "Ver estado actual del robot"),
            ("Editor", "Editar documentos por capas"),
            ("Biblioteca", "Abrir documentos maestros"),
            ("Paradigma", "Consultar marco universal"),
        ]:
            card = QFrame()
            card.setObjectName("panelCard")
            card_layout = QVBoxLayout(card)
            card_title = QLabel(label)
            card_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #f4f7ff;")
            card_desc = QLabel(subtitle)
            card_desc.setWordWrap(True)
            card_desc.setStyleSheet("color: #a6b7d4; font-size: 12px;")
            card_layout.addWidget(card_title)
            card_layout.addWidget(card_desc)
            quick_layout.addWidget(card)
        root.addWidget(quick_frame)

        arch = QPlainTextEdit()
        arch.setReadOnly(True)
        arch.setPlainText(
            "Capa 1 (Core): domain/analysis.py\n"
            "Capa 2 (Flujo): robot_quero.py (persistencia)\n"
            "Capa 3 (UI): control_plane_app.py"
        )
        root.addWidget(arch)


class RobotPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)

        top = QFrame()
        top.setObjectName("panelCard")
        top_layout = QGridLayout(top)

        self.symbol = QLineEdit("BYBIT:BTCUSDT")
        self.interval = QComboBox()
        self.interval.addItems(["1", "5", "15", "30", "60", "240", "D"])

        self.browser_address = QLineEdit("https://www.google.com")
        self.browser_back_btn = QPushButton("<")
        self.browser_fwd_btn = QPushButton(">")
        self.browser_reload_btn = QPushButton("Recargar")
        self.browser_home_btn = QPushButton("Inicio")
        self.browser_go_btn = QPushButton("Ir")
        self.browser_gocharting_btn = QPushButton("GoCharting")
        self.browser_gocharting_btn.setObjectName("btnMid")

        top_layout.addWidget(QLabel("Simbolo (robot)"), 0, 0)
        top_layout.addWidget(self.symbol, 0, 1)
        top_layout.addWidget(QLabel("Temporalidad"), 0, 2)
        top_layout.addWidget(self.interval, 0, 3)

        top_layout.addWidget(self.browser_back_btn, 1, 0)
        top_layout.addWidget(self.browser_fwd_btn, 1, 1)
        top_layout.addWidget(self.browser_reload_btn, 1, 2)
        top_layout.addWidget(self.browser_home_btn, 1, 3)
        top_layout.addWidget(self.browser_address, 1, 4, 1, 3)
        top_layout.addWidget(self.browser_go_btn, 1, 7)
        top_layout.addWidget(self.browser_gocharting_btn, 1, 8)
        root.addWidget(top)

        splitter = QSplitter(Qt.Horizontal)
        left = QWidget()
        left_layout = QVBoxLayout(left)

        status_panel = QFrame()
        status_panel.setObjectName("statusPanel")
        status_layout = QGridLayout(status_panel)

        self.status_state = QLabel("WAIT")
        self.status_conf = QLabel("0%")
        self.status_check = QLabel("INCOMPLETO")
        self.status_reason = QLabel("Sin verificacion")
        self.status_reason.setWordWrap(True)

        status_layout.addWidget(QLabel("Estado final"), 0, 0)
        status_layout.addWidget(self.status_state, 0, 1)
        status_layout.addWidget(QLabel("Confianza"), 0, 2)
        status_layout.addWidget(self.status_conf, 0, 3)
        status_layout.addWidget(QLabel("Checklist"), 1, 0)
        status_layout.addWidget(self.status_check, 1, 1)
        status_layout.addWidget(QLabel("Motivo"), 1, 2)
        status_layout.addWidget(self.status_reason, 1, 3, 1, 1)
        left_layout.addWidget(status_panel)

        candle_form = QFrame()
        candle_form.setObjectName("panelCard")
        candle_layout = QFormLayout(candle_form)
        self.open_in = QLineEdit("0")
        self.high_in = QLineEdit("0")
        self.low_in = QLineEdit("0")
        self.close_in = QLineEdit("0")
        candle_layout.addRow("Open", self.open_in)
        candle_layout.addRow("High", self.high_in)
        candle_layout.addRow("Low", self.low_in)
        candle_layout.addRow("Close", self.close_in)

        self.add_candle_btn = QPushButton("Registrar vela")
        self.add_candle_btn.setObjectName("btnMid")
        self.verify_btn = QPushButton("Verificar senal")
        self.verify_btn.setObjectName("btnPositive")
        self.save_btn = QPushButton("Guardar senal")
        self.save_btn.setObjectName("btnNegative")

        left_layout.addWidget(candle_form)
        left_layout.addWidget(self.add_candle_btn)
        left_layout.addWidget(self.verify_btn)
        left_layout.addWidget(self.save_btn)

        self.result_box = QPlainTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("Resultado del robot...")
        left_layout.addWidget(self.result_box, stretch=1)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(
            ["timestamp", "tipo_vela", "open", "high", "low", "close", "EMA_3", "EMA_9", "MACD_HIST"]
        )
        left_layout.addWidget(self.table, stretch=2)

        self.web = QWebEngineView()
        splitter.addWidget(left)
        splitter.addWidget(self.web)
        splitter.setSizes([550, 900])
        root.addWidget(splitter, stretch=1)

        self.browser_back_btn.clicked.connect(self.web.back)
        self.browser_fwd_btn.clicked.connect(self.web.forward)
        self.browser_reload_btn.clicked.connect(self.web.reload)
        self.browser_home_btn.clicked.connect(self.open_browser_home)
        self.browser_go_btn.clicked.connect(self.open_browser_address)
        self.browser_gocharting_btn.clicked.connect(self.open_browser_gocharting)
        self.browser_address.returnPressed.connect(self.open_browser_address)
        self.web.urlChanged.connect(self.on_browser_url_changed)

        self.add_candle_btn.clicked.connect(self.add_candle)
        self.verify_btn.clicked.connect(lambda: self.run_robot(save=False))
        self.save_btn.clicked.connect(lambda: self.run_robot(save=True))

        self.open_browser_home()
        self.refresh_table()
        self._set_chip(self.status_state, "WAIT", "intermediate")
        self._set_chip(self.status_conf, "0%", "intermediate")
        self._set_chip(self.status_check, "INCOMPLETO", "intermediate")

    def _normalize_browser_target(self, raw: str) -> str:
        text = raw.strip()
        if not text:
            return "https://www.google.com"
        if " " in text:
            return f"https://www.google.com/search?q={quote_plus(text)}"
        if "://" in text:
            return text
        if "." in text:
            return f"https://{text}"
        return f"https://www.google.com/search?q={quote_plus(text)}"

    def open_browser_address(self) -> None:
        target = self._normalize_browser_target(self.browser_address.text())
        self.web.setUrl(QUrl(target))

    def open_browser_home(self) -> None:
        self.web.setUrl(QUrl("https://www.google.com"))

    def open_browser_gocharting(self) -> None:
        symbol = self.symbol.text().strip() or "BYBIT:BTCUSDT"
        self.web.setUrl(QUrl(build_gocharting_url(symbol)))

    def on_browser_url_changed(self, url: QUrl) -> None:
        self.browser_address.setText(url.toString())

    def _set_chip(self, label: QLabel, text: str, state: str) -> None:
        label.setText(text)
        label.setStyleSheet(chip_style(state))

    def _map_signal_to_state(self, signal: str) -> tuple[str, str]:
        if signal == "LONG":
            return "ENTRY", "positive"
        if signal == "SHORT":
            return "EXIT", "negative"
        return "WAIT", "intermediate"

    def _evaluate_checklist_state(self, payload: dict) -> tuple[str, str]:
        details = payload.get("detalles", {})
        check_long = details.get("checklist_long", {})
        check_short = details.get("checklist_short", {})
        signal = payload.get("signal", "NO_TRADE")

        if signal == "LONG":
            invalid = sum(1 for v in check_long.get("invalidaciones", {}).values() if bool(v))
            if invalid == 0 and bool(check_long.get("minimo")):
                return "VALIDO", "positive"
            return "INVALIDO", "negative"

        if signal == "SHORT":
            invalid = sum(1 for v in check_short.get("invalidaciones", {}).values() if bool(v))
            if invalid == 0 and bool(check_short.get("minimo")):
                return "VALIDO", "positive"
            return "INVALIDO", "negative"

        return "INCOMPLETO", "intermediate"

    def _confidence_state(self, confidence: int) -> str:
        if confidence >= 70:
            return "positive"
        if confidence >= 40:
            return "intermediate"
        return "negative"

    def add_candle(self) -> None:
        try:
            open_v = float(self.open_in.text())
            high_v = float(self.high_in.text())
            low_v = float(self.low_in.text())
            close_v = float(self.close_in.text())
        except ValueError:
            QMessageBox.warning(self, "Vela", "Valores numericos invalidos.")
            return

        if high_v < max(open_v, close_v) or low_v > min(open_v, close_v):
            QMessageBox.warning(self, "Vela", "High/Low invalidos para esta vela.")
            return

        append_candle(open_v, high_v, low_v, close_v, CSV_FILE)
        self.refresh_table()
        QMessageBox.information(self, "OK", "Vela registrada en CSV.")

    def refresh_table(self) -> None:
        df = prepare_df_for_table(CSV_FILE).tail(120)
        if df.empty:
            self.table.setRowCount(0)
            return

        cols = ["timestamp", "tipo_vela", "open", "high", "low", "close", "EMA_3", "EMA_9", "MACD_HIST"]
        data = df[cols].copy()
        data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

        self.table.setRowCount(len(data))
        for r, (_, row) in enumerate(data.iterrows()):
            for c, col in enumerate(cols):
                v = row[col]
                if isinstance(v, float):
                    text = f"{v:.6f}" if col == "MACD_HIST" else f"{v:.2f}"
                else:
                    text = str(v)
                self.table.setItem(r, c, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()

    def run_robot(self, save: bool) -> None:
        symbol = self.symbol.text().strip() or "BYBIT:BTCUSDT"
        tf = INTERVAL_TO_TF.get(self.interval.currentText(), "5m")
        try:
            resultado = analizar_mercado(csv_path=CSV_FILE, symbol=symbol, timeframe=tf)
            payload = asdict(resultado)
            state_text, state_color = self._map_signal_to_state(payload.get("signal", "NO_TRADE"))
            check_text, check_color = self._evaluate_checklist_state(payload)
            conf = int(payload.get("confidence", 0))
            conf_state = self._confidence_state(conf)

            self._set_chip(self.status_state, state_text, state_color)
            self._set_chip(self.status_conf, f"{conf}%", conf_state)
            self._set_chip(self.status_check, check_text, check_color)
            self.status_reason.setText(payload.get("reason", "Sin motivo"))
            if state_color == "positive":
                self.status_reason.setStyleSheet(f"color: {POS_COLOR}; font-weight: 700;")
            elif state_color == "negative":
                self.status_reason.setStyleSheet(f"color: {NEG_COLOR}; font-weight: 700;")
            else:
                self.status_reason.setStyleSheet(f"color: {MID_COLOR}; font-weight: 700;")

            out = [
                f"Estado: {state_text}",
                f"Senal cruda: {payload['signal']} ({payload['confidence']}%)",
                f"Motivo: {payload['reason']}",
                "",
                json.dumps(payload, ensure_ascii=False, indent=2),
            ]
            self.result_box.setPlainText("\n".join(out))

            if save:
                rutas = save_analysis_to_bitacora(resultado)
                self.result_box.appendPlainText("\nGuardado en:")
                for p in rutas:
                    self.result_box.appendPlainText(f"- {p}")
                QMessageBox.information(self, "Robot", "Senal guardada en bitacora.")
            else:
                QMessageBox.information(self, "Robot", "Senal verificada.")
        except Exception as e:
            QMessageBox.critical(self, "Robot", f"Error: {e}")
        finally:
            self.refresh_table()


class DocumentosPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)

        header = QLabel("Documentos Maestros")
        header.setStyleSheet("font-size: 22px; font-weight: 800; color: #f4f7ff;")
        root.addWidget(header)

        self.doc_select = QComboBox()
        self.doc_select.addItems([f"{doc.title} ({doc.key})" for doc in MASTER_DOCS])
        self.doc_select.currentIndexChanged.connect(self.load_document)
        root.addWidget(self.doc_select)

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #9fb1cf; margin-bottom: 8px;")
        root.addWidget(self.info_label)

        split = QSplitter(Qt.Horizontal)
        self.section_list = QListWidget()
        self.section_list.setMaximumWidth(280)
        self.section_list.currentRowChanged.connect(self.show_section)
        split.addWidget(self.section_list)

        self.content = QPlainTextEdit()
        self.content.setReadOnly(True)
        split.addWidget(self.content)
        root.addWidget(split, stretch=1)

        self._sections: list[tuple[str, str]] = []
        self.load_document(0)

    def load_document(self, index: int) -> None:
        doc = MASTER_DOCS[index]
        if not doc.path.exists():
            self.info_label.setText(f"Ruta no encontrada: {doc.path}")
            self.section_list.clear()
            self.content.setPlainText("No se encontró el documento.")
            return

        text = _read_text(doc.path)
        stats = _doc_stats(doc.path)
        self.info_label.setText(f"{stats['lines']} líneas · {stats['headings']} títulos · {doc.path}")

        self._sections = split_markdown_sections(text)
        self.section_list.clear()
        for title, _ in self._sections:
            QListWidgetItem(title or "Sección", self.section_list)
        if self._sections:
            self.section_list.setCurrentRow(0)
        else:
            self.content.setPlainText(text)

    def show_section(self, row: int) -> None:
        if row < 0 or row >= len(self._sections):
            return
        title, body = self._sections[row]
        self.content.setPlainText(f"# {title}\n\n{body}" if title else body)


class EditorPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)

        header = QLabel("Editor por Capas")
        header.setStyleSheet("font-size: 22px; font-weight: 800; color: #f4f7ff;")
        root.addWidget(header)

        self.doc_select = QComboBox()
        self.doc_select.addItems([f"{doc.title} ({doc.key})" for doc in MASTER_DOCS])
        self.doc_select.currentIndexChanged.connect(self.on_doc_change)
        root.addWidget(self.doc_select)

        self.layer_select = QComboBox()
        self.layer_select.currentIndexChanged.connect(self.on_layer_change)
        root.addWidget(self.layer_select)

        self.edit_area = QPlainTextEdit()
        root.addWidget(self.edit_area, stretch=1)

        actions = QHBoxLayout()
        self.save_btn = QPushButton("Guardar capa")
        self.save_btn.setObjectName("btnPositive")
        self.save_btn.clicked.connect(self.save_layer)
        actions.addWidget(self.save_btn)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Escribe GUARDAR para confirmar")
        actions.addWidget(self.confirm_input)
        root.addLayout(actions)

        self.feedback = QLabel("")
        self.feedback.setStyleSheet("color: #9fb1cf; margin-top: 8px;")
        root.addWidget(self.feedback)

        self.current_doc_index = 0
        self.current_layers: list[DocLayer] = []
        self.load_document(0)

    def on_doc_change(self, index: int) -> None:
        self.load_document(index)

    def load_document(self, index: int) -> None:
        self.current_doc_index = index
        doc = MASTER_DOCS[index]
        if not doc.path.exists():
            self.layer_select.clear()
            self.edit_area.setPlainText(f"Documento no encontrado: {doc.path}")
            return

        text = _read_text(doc.path)
        self.current_layers = _split_layers(text)
        self.layer_select.clear()
        for layer in self.current_layers:
            self.layer_select.addItem(f"{layer.index + 1}: {layer.title}")
        if self.current_layers:
            self.layer_select.setCurrentIndex(0)
        self.on_layer_change(0)

    def on_layer_change(self, index: int) -> None:
        if index < 0 or index >= len(self.current_layers):
            return
        doc = MASTER_DOCS[self.current_doc_index]
        text = _read_text(doc.path)
        layer = self.current_layers[index]
        self.edit_area.setPlainText(_layer_text(text, layer))

    def save_layer(self) -> None:
        confirm = self.confirm_input.text().strip().upper()
        if confirm != "GUARDAR":
            self.feedback.setText("Escribe GUARDAR para confirmar el guardado.")
            return

        index = self.layer_select.currentIndex()
        if index < 0 or index >= len(self.current_layers):
            self.feedback.setText("Selecciona una capa válida.")
            return

        doc = MASTER_DOCS[self.current_doc_index]
        if not doc.path.exists():
            self.feedback.setText("Documento no encontrado.")
            return

        text = _read_text(doc.path)
        layer = self.current_layers[index]
        new_text = _replace_layer(text, layer, self.edit_area.toPlainText())
        backup_path = _backup_document(doc.path)
        _write_text(doc.path, new_text)
        self.feedback.setText(f"Guardado. Backup creado: {backup_path}")


class ParadigmaPage(QWidget):
    def __init__(self):
        super().__init__()
        self._md_text = ""
        self._sections: list[tuple[str, str]] = []

        root = QVBoxLayout(self)

        top = QHBoxLayout()
        self.path_label = QLabel("Fuente: -")
        self.reload_btn = QPushButton("Recargar")
        self.filter_in = QLineEdit()
        self.filter_in.setPlaceholderText("Filtrar termino...")
        top.addWidget(self.path_label, stretch=1)
        top.addWidget(self.filter_in, stretch=1)
        top.addWidget(self.reload_btn)
        root.addLayout(top)

        split = QSplitter(Qt.Horizontal)
        self.section_list = QListWidget()
        self.content = QPlainTextEdit()
        self.content.setReadOnly(True)
        split.addWidget(self.section_list)
        split.addWidget(self.content)
        split.setSizes([280, 980])
        root.addWidget(split, stretch=1)

        self.reload_btn.clicked.connect(self.reload_paradigma)
        self.filter_in.textChanged.connect(self.apply_filter)
        self.section_list.currentRowChanged.connect(self.show_current_section)

        self.reload_paradigma()

    def _load_paradigma(self) -> tuple[Path | None, str]:
        for p in DEFAULT_PARADIGMA_CANDIDATES:
            if p.exists():
                return p, p.read_text(encoding="utf-8", errors="replace")
        return None, ""

    def reload_paradigma(self) -> None:
        path, text = self._load_paradigma()
        self._md_text = text
        self._sections = split_markdown_sections(text) if text else []
        self.path_label.setText(f"Fuente: {path}" if path else "Fuente: no encontrada")
        self.apply_filter()

    def apply_filter(self) -> None:
        q = self.filter_in.text().strip().lower()
        self.section_list.clear()

        if not self._sections:
            self.content.setPlainText("No se encontro Paradigma.md.")
            return

        filtered = []
        for title, body in self._sections:
            if not q or q in title.lower() or q in body.lower():
                filtered.append((title, body))

        self.section_list.setProperty("sections", filtered)
        for title, _ in filtered:
            QListWidgetItem(title if title else "Seccion", self.section_list)

        if filtered:
            self.section_list.setCurrentRow(0)
        else:
            self.content.setPlainText("Sin resultados para ese filtro.")

    def show_current_section(self, row: int) -> None:
        sections = self.section_list.property("sections") or []
        if row < 0 or row >= len(sections):
            return
        title, body = sections[row]
        self.content.setPlainText(f"# {title}\n\n{body}".strip())


class ControlPlaneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Plane App - Sistema Quero")
        self.resize(1600, 920)
        self.setStyleSheet(build_app_stylesheet())

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        self.nav = QListWidget()
        self.nav.addItems(["Inicio", "Robot", "Documentos", "Editor", "Paradigma"])
        self.nav.setMaximumWidth(240)
        self.nav.setStyleSheet(
            "QListWidget { background: rgba(12,18,31,0.98); border: 1px solid rgba(255,255,255,0.1); }"
        )

        self.stack = QStackedWidget()
        self.home = HomePage(
            go_robot=lambda: self.go_page(1),
            go_paradigma=lambda: self.go_page(4),
            go_documentos=lambda: self.go_page(2),
            go_editor=lambda: self.go_page(3),
        )
        self.robot = RobotPage()
        self.documentos = DocumentosPage()
        self.editor = EditorPage()
        self.paradigma = ParadigmaPage()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.robot)
        self.stack.addWidget(self.documentos)
        self.stack.addWidget(self.editor)
        self.stack.addWidget(self.paradigma)

        layout.addWidget(self.nav)
        layout.addWidget(self.stack, stretch=1)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

        open_chart_action = QAction("Recargar navegador", self)
        open_chart_action.triggered.connect(self.robot.web.reload)
        self.menuBar().addAction(open_chart_action)

    def go_page(self, index: int) -> None:
        self.nav.setCurrentRow(index)


def main() -> None:
    app = QApplication(sys.argv)
    win = ControlPlaneApp()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
