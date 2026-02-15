class PromptBuilder:
    def construir_instrucciones(self, datos_entrada: dict) -> tuple:
        """
        Transforma los datos del dominio en instrucciones de lenguaje natural 
        para el LLM, asegurando una respuesta técnica y estructurada.
        """
        
        # El System Prompt: Ahora con instrucciones de formato "agresivas"
        system = """
        Eres un Ingeniero Civil Senior y Auditor de Proyectos con 20 años de experiencia. 
        Tu objetivo es detectar riesgos financieros, operativos y de seguridad en datos de obra.
        
        REGLAS DE FORMATO INQUEBRANTABLES:
        1. TU RESPUESTA DEBE SER ÚNICAMENTE UN OBJETO JSON VÁLIDO.
        2. NO incluyas introducciones, ni comentarios, ni bloques de código markdown (```json ... ```).
        3. No escribas nada antes ni después del objeto JSON.
        4. Asegúrate de que todas las comillas sean dobles y el JSON sea parseable.

        ESTRUCTURA OBLIGATORIA:
        {
          "resumen": "...",
          "score_coherencia": 0,
          "riesgos": [{"titulo": "...", "descripcion": "...", "nivel": "..."}]
        }
        """
        
        # El User Prompt: Organiza los datos y refuerza el contrato técnico
        user = f"""
        Realiza una auditoría técnica del siguiente snapshot de obra:
        
        --- INICIO DE DATOS ---
        PROYECTO: {datos_entrada.get('proyecto_codigo')}
        DATOS DE OBRA: {datos_entrada.get('datos')}
        --- FIN DE DATOS ---
        
        INSTRUCCIONES DE ANÁLISIS:
        1. Evalúa el "resumen": Un párrafo técnico detallado sobre el estado actual.
        2. Calcula el "score_coherencia": Número entero del 0 al 100.
        3. Identifica "riesgos": Lista de objetos con titulo, descripcion y nivel (CRITICO, ATENCION, INFORMATIVO).
        
        RESPONDE SOLO EL JSON:
        """
        
        return system, user