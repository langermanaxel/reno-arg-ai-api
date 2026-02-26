class PromptBuilder:
    def construir_instrucciones(self, datos_entrada: dict) -> tuple:
        # Extract project code from the nested 'proyecto' key if it exists
        proyecto = datos_entrada.get('proyecto', {})
        codigo = proyecto.get('codigo') or datos_entrada.get('proyecto_codigo') or "No especificado"
        
        # The entire dictionary contains the work data
        system = """... (keep your aggressive system prompt) ..."""
        
        user = f"""
        Realiza una auditoría técnica del siguiente snapshot de obra:
        
        --- INICIO DE DATOS ---
        PROYECTO: {codigo}
        DETALLE TÉCNICO: {json.dumps(datos_entrada, indent=2)}
        --- FIN DE DATOS ---
        
        INSTRUCCIONES DE ANÁLISIS:
        1. Evalúa el "resumen": Un párrafo técnico detallado sobre el estado actual.
        2. Calcula el "score_coherencia": Número entero del 0 al 100.
        3. Identifica "riesgos": Lista de objetos con titulo, descripcion y nivel (CRITICO, ATENCION, INFORMATIVO).
        
        RESPONDE SOLO EL JSON:
        """
        return system, user