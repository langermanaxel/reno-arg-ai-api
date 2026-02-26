import json  # <--- ESTA ES LA PIEZA QUE FALTA

class PromptBuilder:
    def construir_instrucciones(self, datos_entrada: dict) -> tuple:
        # Extraer código del proyecto
        proyecto = datos_entrada.get('proyecto', {})
        codigo = proyecto.get('codigo') or datos_entrada.get('proyecto_codigo') or "No especificado"
        
        # Convertimos el dict a JSON string de forma segura
        try:
            datos_json = json.dumps(datos_entrada, indent=2, ensure_ascii=False)
        except Exception:
            datos_json = str(datos_entrada) # Fallback si falla el dump

        system = """... (tu prompt agresivo) ..."""
        
        user = f"""
        Realiza una auditoría técnica del siguiente snapshot de obra:
        
        --- INICIO DE DATOS ---
        PROYECTO: {codigo}
        DETALLE TÉCNICO: {datos_json}
        --- FIN DE DATOS ---
        
        INSTRUCCIONES DE ANÁLISIS:
        1. Evalúa el "resumen": Un párrafo técnico detallado sobre el estado actual.
        2. Calcula el "score_coherencia": Número entero del 0 al 100.
        3. Identifica "riesgos": Lista de objetos con titulo, descripcion y nivel (CRITICO, ATENCION, INFORMATIVO).
        
        RESPONDE SOLO EL JSON:
        """
        return system, user