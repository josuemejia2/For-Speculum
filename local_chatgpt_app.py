from flask import Flask, render_template, request, jsonify, session
from pathlib import Path
import json
import os
import re
import unicodedata
from difflib import SequenceMatcher
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from danzariel_quero.core.config import settings
from danzariel_quero.services.files import create_or_update_markdown

app = Flask(__name__)
app.secret_key = os.getenv("ASISTENTE_SESSION_SECRET", "asistente-local-session")

BASE_DIR = Path(__file__).resolve().parent
CONTEXT_DIR = BASE_DIR / "asistente_local"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"


def read_local_context():
    files = []
    if CONTEXT_DIR.exists():
        files.extend(sorted(CONTEXT_DIR.glob("*.md")))
    files.extend(sorted(BASE_DIR.glob("*.md")))

    context = ""
    seen = set()
    for file in files:
        if file.name in seen:
            continue
        seen.add(file.name)
        if file.exists():
            context += f"\n--- {file.name} ---\n{file.read_text(encoding='utf-8')}\n"
    return context.strip()


LOCAL_CONTEXT = read_local_context()


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clear_save_flow() -> None:
    session.pop("save_flow", None)


def safe_note_filename(title: str) -> str:
    filename = re.sub(r"[^A-Za-z0-9_. -]+", "_", title.strip()).strip(" .")
    filename = filename or "nota"
    return filename if filename.lower().endswith(".md") else f"{filename}.md"


def save_flow_reply(message: str) -> str | None:
    normalized = message.strip()
    command = normalized.casefold()
    flow = session.get("save_flow")

    if command == "!aguardar":
        session["save_flow"] = {"stage": "content"}
        return (
            "Vamos a guardar solo lo que tú elijas.\n\n"
            "¿Qué contenido quieres guardar? Escríbelo en tu siguiente mensaje.\n"
            "Escribe CANCELAR para detener el proceso."
        )

    if not flow:
        return None

    if command in {"cancelar", "!cancelar"}:
        clear_save_flow()
        return "Guardado cancelado. No se escribió ningún archivo."

    stage = flow.get("stage")
    if stage == "content":
        if not normalized:
            return "El contenido está vacío. Escribe algo para guardar o CANCELAR."
        flow.update({"stage": "title", "content": normalized})
        session["save_flow"] = flow
        return "¿Qué título quieres ponerle? Escribe solo el título del archivo."

    if stage == "title":
        if not normalized:
            return "Necesito un título para continuar o puedes escribir CANCELAR."
        flow.update({"stage": "area", "title": safe_note_filename(normalized)})
        session["save_flow"] = flow
        areas = ", ".join(settings.areas)
        return f"¿En qué carpeta permitida lo guardo?\n\nOpciones: {areas}"

    if stage == "area":
        area = normalized.casefold()
        if area not in settings.areas:
            return "Esa carpeta no está permitida. Elige una de las opciones mostradas o escribe CANCELAR."
        flow.update({"stage": "confirm", "area": area})
        session["save_flow"] = flow
        relative_path = f"{area}/{flow['title']}"
        return (
            "Vista previa del guardado:\n\n"
            f"Archivo: {relative_path}\n"
            "Contenido:\n"
            f"{flow['content']}\n\n"
            "Escribe CONFIRMAR para guardarlo o CANCELAR para no escribir nada."
        )

    if stage == "confirm":
        if command not in {"confirmar", "!confirmar"}:
            return "No se guardó nada. Escribe CONFIRMAR para aceptar la vista previa o CANCELAR."
        relative_path = create_or_update_markdown(flow["area"], flow["title"], flow["content"])
        clear_save_flow()
        return f"Guardado confirmado: {flow['area']}/{relative_path}"

    clear_save_flow()
    return "Reinicié el flujo de guardado porque su estado era inválido."


FUZZY_INTENTS = {
    "saludo": ["hola", "buenas", "hey", "buenos dias"],
    "organizar": ["organizar", "ordenar", "plan", "proyecto", "pasos"],
    "explicar": ["explicar", "explica", "entender", "concepto", "teoria"],
    "redactar": ["redactar", "escribir", "mejorar texto", "reescribir"],
    "problema": ["problema", "error", "fallo", "bug", "ayuda"],
    "continuar": ["continua", "eso", "hazlo", "lo anterior", "si", "exacto"],
    "emocion": ["cansado", "ansioso", "preocupado", "feliz", "triste", "frustrado"],
}


def fuzzy_normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9\s]", " ", without_accents)


def fuzzy_interpretation(text: str) -> dict[str, object]:
    normalized = fuzzy_normalize(text)
    words = normalized.split()
    scores: dict[str, float] = {}
    for intent, phrases in FUZZY_INTENTS.items():
        best_score = 0.0
        for phrase in phrases:
            target_words = phrase.split()
            if len(target_words) == 1:
                best_score = max(best_score, max((SequenceMatcher(None, word, phrase).ratio() for word in words), default=0.0))
            else:
                best_score = max(best_score, SequenceMatcher(None, normalized, phrase).ratio())
        scores[intent] = best_score

    intent = max(scores, key=scores.get, default="general")
    confidence = round(scores.get(intent, 0.0), 2)
    if confidence < 0.55:
        intent = "general"
    return {"intent": intent, "confidence": confidence}


def ollama_reply(user_message: str, history: list[str]) -> str | None:
    interpretation = fuzzy_interpretation(user_message)
    messages = [
        {
            "role": "system",
            "content": (
                "Eres Asistente Local, un asistente personal cercano, natural y honesto. "
                "Habla principalmente en espanol, con calidez y claridad. Mantén el hilo de la "
                "conversacion, no repitas plantillas y pregunta solo cuando falte informacion. "
                "Puedes ayudar a pensar, redactar, organizar y trabajar con el contexto local. "
                "No inventes que ejecutaste acciones: distingue entre sugerir y hacer.\n\n"
                f"Contexto local disponible:\n{LOCAL_CONTEXT[:8000]}"
                f"\n\nInterpretacion auxiliar de entrada: {interpretation['intent']} "
                f"(confianza {interpretation['confidence']}). Trátala como pista, no como verdad."
            ),
        }
    ]
    pairs = history[-12:]
    for index, item in enumerate(pairs):
        messages.append({"role": "user" if index % 2 == 0 else "assistant", "content": item})
    messages.append({"role": "user", "content": user_message})

    payload = json.dumps({"model": OLLAMA_MODEL, "messages": messages, "stream": False}).encode("utf-8")
    request = Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None

    message = result.get("message", {})
    reply = message.get("content") if isinstance(message, dict) else None
    return reply.strip() if isinstance(reply, str) and reply.strip() else None


def build_reply(user_message: str, history: list[str]) -> str:
    message = clean_text(user_message)
    if not message:
        return "Dime qué quieres hacer y te ayudo con claridad y estilo premium."

    lower = message.lower()
    recent = "\n".join(history[-6:])

    continuity_words = (
        "si", "sí", "no", "eso", "esa", "ese", "lo anterior", "continua",
        "continúa", "hazlo", "exacto", "ok", "vale", "tambien", "también",
    )
    emotional_words = {
        "cansado": "cansancio",
        "cansada": "cansancio",
        "ansioso": "ansiedad",
        "ansiosa": "ansiedad",
        "preocupado": "preocupacion",
        "preocupada": "preocupacion",
        "feliz": "alegria",
        "triste": "tristeza",
        "frustrado": "frustracion",
        "frustrada": "frustracion",
    }

    if recent and (lower in continuity_words or lower.startswith(continuity_words)):
        return (
            "Sí, te sigo. Estoy tomando como referencia lo que veníamos hablando.\n\n"
            f"Lo último que me pediste fue: {history[-2] if len(history) > 1 else 'continuar con el tema actual'}.\n\n"
            "Puedo continuar desde ahí, cambiar el enfoque o detenerme si ya no es lo que necesitas."
        )

    detected_emotion = next((label for word, label in emotional_words.items() if word in lower), None)
    if detected_emotion:
        return (
            f"Te escucho. Suena a {detected_emotion}, y no hace falta resolverlo todo de golpe.\n\n"
            f"Podemos separar lo que sientes de lo que necesitas hacer ahora: {message}. "
            "¿Quieres que te escuche, que ordenemos la situación o que preparemos un siguiente paso concreto?"
        )

    if any(k in lower for k in ["resumen", "resume", "summary", "synopsis"]):
        return (
            "Aquí va un resumen claro y útil:\n\n"
            f"- Tema principal: {message}\n"
            "- Idea central: tienes una necesidad que requiere orden, claridad y enfoque.\n"
            "- Enfoque recomendado: simplifica, identifica lo esencial y responde con un objetivo concreto.\n\n"
            "Si quieres, puedo hacerte un resumen más profesional, técnico o breve."
        )

    if any(k in lower for k in ["redact", "mejora", "mejorar", "rewrite", "text", "escribe", "texto"]):
        return (
            "Te dejo una versión mejorada y más natural:\n\n"
            f"{message}\n\n"
            "Se puede pulir aún más si quieres un tono más profesional, más cercano, más técnico o más persuasivo."
        )

    if any(k in lower for k in ["explica", "explique", "explain", "concepto", "teoria"]):
        return (
            f"Te lo explico de forma clara: {message}.\n\n"
            "La idea clave es descomponer el tema en partes pequeñas, explicar el propósito, y luego mostrar un ejemplo práctico. "
            "Eso ayuda a entender la lógica sin perder claridad."
        )

    if any(k in lower for k in ["plan", "planear", "pasos", "proyecto", "organiza", "organizar"]):
        return (
            "Te propongo este plan práctico:\n\n"
            "1. Define el objetivo final.\n"
            "2. Separa las tareas en bloques pequeños.\n"
            "3. Prioriza lo importante y urgente.\n"
            "4. Ejecuta en ciclos cortos.\n"
            "5. Revisa el resultado y ajusta.\n\n"
            "Si quieres, puedo convertir esto en un plan más detallado para tu caso concreto."
        )

    if any(k in lower for k in ["hola", "buenas", "buenos", "hey", "hi"]):
        return "Hola, soy tu asistente local. Estoy listo para ayudarte con respuestas, redacción, análisis, organización y trabajo basado en tus archivos y tus reglas."

    if any(k in lower for k in ["error", "bug", "problema", "fallo", "debug"]):
        return (
            "Vamos a resolverlo de forma estructurada:\n\n"
            "1. Reproduce el problema.\n"
            "2. Identifica la causa probable.\n"
            "3. Prueba la solución mínima.\n"
            "4. Verifica el resultado.\n\n"
            "Si me pasas el error exacto o el contexto, te ayudo a diagnosticarlo mejor."
        )

    if recent:
        return (
            "Te ayudo con esto con continuidad. "
            f"Tu idea principal parece ser: {message}. "
            "Estoy usando tu contexto local y tu historial reciente para mantener una conversación más coherente y útil. "
            "Lo mejor es enfocarnos en el objetivo, simplificar la lógica, y construir una respuesta práctica con estructura. "
            "Si quieres, puedo convertir esto en un plan, una respuesta mejorada, un resumen o una explicación más profunda."
        )

    return (
        "Te ayudo con esto de forma clara y útil. "
        f"Tu idea principal parece ser: {message}. "
        "Lo mejor es enfocarnos en el objetivo, simplificar la lógica, y construir una respuesta práctica con estructura. "
        "Si quieres, puedo convertir esto en un plan, una respuesta mejorada, un resumen o una explicación más profunda."
    )


@app.route("/")
def index():
    context_files = []
    if CONTEXT_DIR.exists():
        for file in sorted(CONTEXT_DIR.glob("*.md")):
            context_files.append(file.name)
    for file in sorted(BASE_DIR.glob("*.md")):
        if file.name not in context_files:
            context_files.append(file.name)
    return render_template("index.html", context_files=context_files)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    payload = request.get_json(silent=True) or {}
    user_message = str(payload.get("message", "")).strip()
    save_reply = save_flow_reply(user_message)
    if save_reply is not None:
        return jsonify({"reply": save_reply, "context": LOCAL_CONTEXT[:600]})

    history = payload.get("history", [])
    if not isinstance(history, list):
        history = []

    history = [str(item) for item in history if item is not None]
    reply = ollama_reply(user_message, history) or build_reply(user_message, history)

    return jsonify({"reply": reply, "context": LOCAL_CONTEXT[:600]})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
