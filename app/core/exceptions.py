from fastapi import HTTPException, status

class AnalisisNotFoundError(HTTPException):
    def __init__(self, analisis_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El análisis con ID {analisis_id} no fue encontrado."
        )

class IAProcessingError(HTTPException):
    def __init__(self, detail: str = "Error interno al procesar con IA"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )