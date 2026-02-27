import json


class PromptBuilder:
    def construir_instrucciones(
        self,
        datos_entrada: dict,
        system_prompt: str | None = None,
        instrucciones_extra: str | None = None,
    ) -> tuple:
        """
        Construye el par (system, user) para el LLM.

        Args:
            datos_entrada:      El snapshot de obra como dict.
            system_prompt:      Reemplaza completamente el system prompt por defecto.
                                Si no se pasa, se usa el default definido aquí.
            instrucciones_extra: Texto adicional que se agrega al final del user prompt.
                                Útil para variar el tipo de análisis sin tocar el core.
        """

        # --- Extracción de metadata básica ---
        proyecto = datos_entrada.get("proyecto", {})
        codigo = (
            proyecto.get("codigo")
            or datos_entrada.get("proyecto_codigo")
            or "No especificado"
        )

        try:
            datos_json = json.dumps(datos_entrada, indent=2, ensure_ascii=False)
        except Exception:
            datos_json = str(datos_entrada)

        # --- System prompt: configurable desde afuera ---
        system = system_prompt or (
            "Sos analista técnico de obras. "
            "Respondé ÚNICAMENTE con un JSON válido, sin texto adicional, sin markdown, sin backticks. "
            "Estructura obligatoria exacta:\n"
            "{\n"
            '  "resumen_general": "Informe narrativo completo en tono formal. Incluir: estado general, ejecución y planificación, seguridad y cumplimiento, validaciones técnicas, observación final.",\n'
            '  "score_coherencia": <número entre 0 y 100 que refleja coherencia y completitud de los datos>,\n'
            '  "detecta_riesgos": <true o false>,\n'
            '  "riesgos": [\n'
            '    {"titulo": "...", "descripcion": "...", "nivel": "informativo|atencion|critico"}\n'
            '  ]\n'
            "}\n"
            "Usá exclusivamente los datos del JSON recibido. "
            "No inventes información. Si falta un dato, indicarlo como 'no informado' dentro del resumen_general. "
            "Si no hay riesgos, devolver riesgos como array vacío []."
        )

        # --- User prompt: estructura fija, contenido dinámico ---
        user = f"""
Realizá un informe técnico del siguiente snapshot de obra:

--- INICIO DE DATOS ---
PROYECTO: {codigo}
DETALLE TÉCNICO:
{datos_json}
--- FIN DE DATOS ---
"""

        # Permite agregar instrucciones específicas por request sin romper el core
        if instrucciones_extra:
            user += f"\nINSTRUCCIONES ADICIONALES:\n{instrucciones_extra}\n"

        return system, user