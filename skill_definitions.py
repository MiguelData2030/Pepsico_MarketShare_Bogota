class AgentSkills:
    """Manual de Entrenamiento de Agentes - Pepsico Bogotá"""
    
    ANALISTA_MARKET_SHARE = {
        "habilidad": "Detección de Fugas de Share",
        "protocolo": "Si (Share_Margarita < 55%): Alertar al equipo de inteligencia. Objetivo Margarita: 55%."
    }
    
    CENTINELA_LOGISTICO = {
        "habilidad": "Predicción de Quiebre de Stock (OSA)",
        "protocolo": "Si (Retraso_Min > 30): Alertar al tendero y reprogramar prioridad de entrega."
    }
    
    ESTRATEGA_ORQUESTADOR = {
        "habilidad": "Mediación de Prioridades",
        "protocolo": "Priorizar siempre el Share de mercado (ventas) sobre el costo logístico en la resolución de incidentes."
    }