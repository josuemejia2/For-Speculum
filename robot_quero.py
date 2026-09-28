from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

JSON_PATH = Path("leyes.json")
CSV_PATH = Path("datos_ejemplo.csv")
BITACORA_PATH = Path("bitacora.json")
BITACORA_DIR = Path("bitacoras_historicas")


import domain.analysis as analysis
from services import save_analysis_to_bitacora


def load_leyes(path: Path = JSON_PATH) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {str(i): v for i, v in enumerate(data)}
        return {}
    except FileNotFoundError:
        sys.exit(f"Archivo no encontrado: {path}")
    except json.JSONDecodeError as e:
        sys.exit(f"Error al leer JSON: {e}")


def mostrar_leyes(leyes: dict[str, Any]) -> list[str]:
    return list(leyes.keys())


def consultar_ley(leyes: dict[str, Any], nombre: str) -> Any:
    return leyes.get(nombre, None)


def buscar_leyes(leyes: dict[str, Any], termino: str) -> dict[str, Any]:
    t = termino.lower()
    results: dict[str, Any] = {}
    for k, v in leyes.items():
        if t in k.lower():
            results[k] = v
            continue
        if isinstance(v, str) and t in v.lower():
            results[k] = v
            continue
        if isinstance(v, dict) and any(t in str(x).lower() for x in v.values()):
            results[k] = v
    return results


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def cargar_velas(csv_path: Path = CSV_PATH) -> pd.DataFrame:
    return analysis.cargar_velas(csv_path)


def calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    return analysis.calcular_indicadores(df)


def analizar_mercado(
    csv_path: Path = CSV_PATH,
    symbol: str = "BTC-USD",
    timeframe: str = "5m",
) -> ResultadoAnalisis:
    return analysis.analizar_mercado(csv_path=csv_path, symbol=symbol, timeframe=timeframe)


def guardar_en_bitacora(resultado: ResultadoAnalisis) -> list[Path]:
    return save_analysis_to_bitacora(resultado, bitacora_path=BITACORA_PATH, bitacora_dir=BITACORA_DIR)


def _print_resultado(resultado: ResultadoAnalisis, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(asdict(resultado), ensure_ascii=False, indent=2))
        return

    print(f"Symbol: {resultado.symbol} | TF: {resultado.timeframe}")
    print(f"Timestamp: {resultado.timestamp}")
    print(f"Tipo vela: {resultado.tipo_vela}")
    print(f"Senal final: {resultado.signal} (confianza {resultado.confidence}%)")
    print(f"Motivo: {resultado.reason}")

    leyes = resultado.detalles.get("leyes", {})
    print(
        "Leyes: "
        f"Capitan={leyes.get('capitan')} | "
        f"Jesus={leyes.get('jesus')} | "
        f"Trujillo={leyes.get('trujillo')} | "
        f"Trina={leyes.get('trina')}"
    )

    print("Checklist LONG:", resultado.detalles.get("checklist_long"))
    print("Checklist SHORT:", resultado.detalles.get("checklist_short"))


def _run_analisis_and_optional_save(args: argparse.Namespace, save: bool) -> None:
    resultado = analizar_mercado(
        csv_path=Path(args.csv),
        symbol=args.symbol,
        timeframe=args.timeframe,
    )
    _print_resultado(resultado, as_json=args.json)
    if save:
        rutas = guardar_en_bitacora(resultado)
        print("Guardado en bitacora:")
        for p in rutas:
            print(f"- {p}")


def _run_interactive(leyes: dict[str, Any]) -> None:
    print("Llave 2-3-6-7-10-12-8 activa")
    print("Comandos: list | get <nombre> | search <termino> | verificar [csv] | guardar [csv] | quit")

    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not cmd:
            continue
        if cmd == "quit":
            return

        parts = cmd.split(maxsplit=1)
        op = parts[0]

        if op == "list":
            for k in mostrar_leyes(leyes):
                print(f"- {k}")
            continue

        if op == "get" and len(parts) == 2:
            detail = consultar_ley(leyes, parts[1])
            if detail is None:
                print("Ley no encontrada")
            else:
                print(json.dumps(detail, ensure_ascii=False, indent=2))
            continue

        if op == "search" and len(parts) == 2:
            hits = buscar_leyes(leyes, parts[1])
            if not hits:
                print("No se encontraron coincidencias")
            else:
                for k, v in hits.items():
                    text = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
                    print(f"- {k}: {text}")
            continue

        if op in {"verificar", "analizar", "guardar"}:
            csv_path = Path(parts[1]) if len(parts) == 2 else CSV_PATH
            resultado = analizar_mercado(csv_path=csv_path)
            _print_resultado(resultado, as_json=False)
            if op == "guardar":
                rutas = guardar_en_bitacora(resultado)
                for p in rutas:
                    print(f"Guardado: {p}")
            continue

        print("Comando no reconocido")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Robot Quero: consulta de leyes + analisis y ejecucion disciplinada"
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list", help="Listar todas las leyes")

    g = sub.add_parser("get", help="Obtener detalle de una ley")
    g.add_argument("name", help="Nombre de la ley")

    s = sub.add_parser("search", help="Buscar termino en nombres o textos")
    s.add_argument("term", help="Termino de busqueda")

    def add_market_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--csv", default=str(CSV_PATH), help="Ruta del CSV de velas")
        p.add_argument("--symbol", default="BTC-USD", help="Simbolo")
        p.add_argument("--timeframe", default="5m", help="Timeframe")
        p.add_argument("--json", action="store_true", help="Salida en JSON")

    analizar_p = sub.add_parser("analizar", help="Triada LEER/VERIFICAR sin guardar")
    add_market_args(analizar_p)

    verificar_p = sub.add_parser("verificar", help="Alias de analizar")
    add_market_args(verificar_p)

    guardar_p = sub.add_parser("guardar", help="GUARDAR analisis en bitacora")
    add_market_args(guardar_p)

    args = parser.parse_args()
    leyes = load_leyes()

    if args.cmd == "list":
        for k in mostrar_leyes(leyes):
            print(f"- {k}")
        return

    if args.cmd == "get":
        detail = consultar_ley(leyes, args.name)
        if detail is None:
            print("Ley no encontrada")
            return
        print(json.dumps(detail, ensure_ascii=False, indent=2))
        return

    if args.cmd == "search":
        hits = buscar_leyes(leyes, args.term)
        if not hits:
            print("No se encontraron coincidencias")
            return
        for k, v in hits.items():
            text = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
            print(f"- {k}: {text}")
        return

    if args.cmd in {"analizar", "verificar"}:
        _run_analisis_and_optional_save(args, save=False)
        return

    if args.cmd == "guardar":
        _run_analisis_and_optional_save(args, save=True)
        return

    _run_interactive(leyes)


if __name__ == "__main__":
    main()
