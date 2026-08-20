import json
from typing import Any

from ollama import AsyncClient


SYSTEM_PROMPT = """
Eres ANNIE, la asistente virtual de un hospital.

Tu función es ayudar exclusivamente con temas relacionados con la atención
y los servicios del hospital.

Reglas:
- Responde siempre en español.
- Sé clara, amable y breve.
- No inventes médicos, horarios, precios ni disponibilidad.
- No confirmes citas que el sistema no haya registrado.
- No realices diagnósticos.
- No prescribas medicamentos.
- No hables de temas ajenos al hospital.
"""


INTENT_PROMPT = """
Tu tarea NO es responder directamente al paciente.

Debes analizar el mensaje del paciente y devolver SOLO un objeto JSON.

Los valores permitidos para "intent" son:

- book_appointment
- cancel_appointment
- reschedule_appointment
- ask_service
- greeting
- other

Reglas:

1. Si quiere sacar, reservar, pedir o agendar una cita:
   intent = "book_appointment"

2. Si quiere cancelar una cita:
   intent = "cancel_appointment"

3. Si quiere cambiar fecha u hora de una cita:
   intent = "reschedule_appointment"

4. Si pregunta por servicios o atención:
   intent = "ask_service"

5. Si solamente saluda:
   intent = "greeting"

6. En cualquier otro caso:
   intent = "other"

Recibirás también el catálogo REAL de servicios del hospital.

Para service_id y service_name:
- SOLO puedes elegir un servicio incluido en el catálogo proporcionado.
- Nunca inventes un servicio.
- Si el paciente menciona claramente un servicio del catálogo,
  selecciónalo.
- Si hay varias opciones razonables, usa null y
  needs_clarification = true.
- Si no hay suficiente información para elegir, usa null.
- No diagnostiques al paciente basándote únicamente en síntomas.

Para requested_date:
- Conserva la fecha solicitada por el paciente.
- Ejemplos: "mañana", "viernes", "20 de agosto".
- Si no indicó fecha, usa null.

Para needs_clarification:
- true si se necesita preguntar al paciente qué servicio desea.
- false si el servicio está claramente indicado.

Para needs_human:
- true si pide explícitamente hablar con una persona.
- true si el caso no puede manejarse de forma segura.
- false en los demás casos.

Formato obligatorio:

{
  "intent": "book_appointment",
  "service_id": 23,
  "service_name": "Traumatología",
  "requested_date": "mañana",
  "needs_clarification": false,
  "needs_human": false
}
"""


class AIAgentService:
    def __init__(
        self,
        model: str = "llama3.2:1b",
        host: str = "http://localhost:11434",
    ) -> None:
        self.model = model
        self.client = AsyncClient(host=host)

    async def chat(
        self,
        message: str,
    ) -> str:
        response = await self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
        )

        return response.message.content

    async def analyze_message(
        self,
        message: str,
        services: list[dict[str, Any]],
    ) -> dict[str, Any]:
        catalog = "\n".join(
            f"- ID {service['id']}: {service['name']}"
            for service in services
        )

        user_content = (
            f"CATÁLOGO REAL DE SERVICIOS:\n"
            f"{catalog}\n\n"
            f"MENSAJE DEL PACIENTE:\n"
            f"{message}"
        )

        response = await self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": INTENT_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
            format="json",
            options={
                "temperature": 0,
            },
        )

        result = json.loads(response.message.content)

        normalized_message = message.lower().strip()

        reschedule_phrases = (
            "reprogramar cita",
            "reprogramar mi cita",
            "cambiar mi cita",
            "cambiar la cita",
            "cambiar fecha",
            "cambiar hora",
            "mover mi cita",
        )

        cancel_phrases = (
            "cancelar cita",
            "cancelar mi cita",
            "anular cita",
            "anular mi cita",
            "no podré asistir",
        )

        booking_phrases = (
            "quiero sacar una cita",
            "quiero una cita",
            "quiero cita",
            "sacar una cita",
            "sacar cita",
            "agendar una cita",
            "agendar cita",
            "reservar una cita",
            "reservar cita",
            "pedir una cita",
            "pedir cita",
            "necesito una cita",
        )

        if any(
            phrase in normalized_message
            for phrase in reschedule_phrases
        ):
            result["intent"] = "reschedule_appointment"

        elif any(
            phrase in normalized_message
            for phrase in cancel_phrases
        ):
            result["intent"] = "cancel_appointment"

        elif any(
            phrase in normalized_message
            for phrase in booking_phrases
        ):
            result["intent"] = "book_appointment"

        # Corrige fechas evidentes sin depender de Llama.
        date_keywords = (
            "hoy",
            "mañana",
            "manana",
            "lunes",
            "martes",
            "miércoles",
            "miercoles",
            "jueves",
            "viernes",
            "sábado",
            "sabado",
            "domingo",
        )

        for date_keyword in date_keywords:
            if date_keyword in normalized_message:
                if date_keyword == "manana":
                    result["requested_date"] = "mañana"

                elif date_keyword == "miercoles":
                    result["requested_date"] = "miércoles"

                elif date_keyword == "sabado":
                    result["requested_date"] = "sábado"

                else:
                    result["requested_date"] = date_keyword

                break

        valid_services = {
            service["id"]: service["name"]
            for service in services
        }

        service_id = result.get("service_id")

        if service_id not in valid_services:
            result["service_id"] = None
            result["service_name"] = None

        elif service_id is not None:
            result["service_name"] = valid_services[service_id]

        if (
            result.get("intent") == "book_appointment"
            and result.get("service_id") is None
        ):
            result["needs_clarification"] = True

        return result

    async def build_patient_response(
        self,
        message: str,
        analysis: dict[str, Any],
        services: list[dict[str, Any]],
    ) -> str:
        if analysis.get("needs_human"):
            return (
                "Voy a derivar tu consulta a un operador humano "
                "para que pueda ayudarte."
            )

        if (
            analysis.get("intent") == "book_appointment"
            and analysis.get("needs_clarification")
        ):
            related_services = [
                service["name"]
                for service in services
                if any(
                    word in service["name"].lower()
                    for word in message.lower().split()
                    if len(word) >= 4
                )
            ]

            if related_services:
                options = ", ".join(
                    related_services[:4]
                )

                return (
                    "Encontré más de una opción relacionada "
                    "con tu solicitud. "
                    f"Tenemos: {options}. "
                    "¿Con cuál deseas agendar tu cita?"
                )

            return (
                "Para ayudarte a agendar la cita necesito saber "
                "qué servicio o especialidad deseas."
            )

        if (
            analysis.get("intent") == "book_appointment"
            and analysis.get("service_id") is not None
        ):
            service_name = analysis.get(
                "service_name"
            )

            return (
                f"Entendido. Deseas agendar una cita para "
                f"{service_name}. "
                "Ahora consultaré la disponibilidad."
            )

        if analysis.get("intent") == "greeting":
            return (
                "Hola, soy ANNIE, asistente virtual del hospital. "
                "Puedo ayudarte con servicios y gestión de citas. "
                "¿En qué puedo ayudarte?"
            )

        return (
            "Puedo ayudarte con información sobre servicios "
            "y gestión de citas del hospital."
        )