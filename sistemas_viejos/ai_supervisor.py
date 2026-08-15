import openai

openai.api_key = "TU_API_KEY_AQUI"

class AISupervisor:
    def __init__(self):
        pass

    def analizar_codigo(self, codigo, pregunta=""):
        """
        Analiza cualquier bloque de código y responde preguntas o da sugerencias.
        """
        prompt = f"""
        Eres un asistente de desarrollo que conoce el sistema de Josue.
        Analiza este código y responde a la pregunta de la manera más clara posible:
        
        Código:
        {codigo}
        
        Pregunta:
        {pregunta}
        """
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return respuesta.choices[0].message.content