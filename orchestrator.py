import pandas as pd
from agents.skill_definitions import AgentSkills

# 1. Carga de Realidad (Data que generaste)
df_bogota = pd.read_csv('data/bogota_market_share_history.csv')

def run_weekly_audit(localidad="Kennedy"):
    print(f"--- Iniciando Auditoría Semanal: {localidad} ---")
    
    # Simulación de detección del Agente Analista
    data_local = df_bogota[df_bogota['Localidad'] == localidad].iloc[-1]
    ventas = data_local['Ventas_Valor']
    retraso = data_local['Retraso_Logistico_Min']
    
    # Lógica de Habilidades (Skills)
    print(f"[Agente Analista]: Revisando ventas en {localidad}...")
    if ventas < 900: # Umbral de alerta basado en Nielsen [cite: 9]
        print(f"  ⚠️ ALERTA: Caída detectada. Ventas actuales: {ventas}")
        print(f"  🔍 Consultando RAG: {AgentSkills.ANALISTA_MARKET_SHARE['habilidad']}")
        
        # El Agente Logístico interviene
        print(f"[Agente Centinela]: Verificando tráfico y logística...")
        if retraso > 30: # Protocolo Playbook 
            print(f"  🚨 RETRASO CRÍTICO: {retraso} min. Aplicando Protocolo OTIF.")
            
        # El Estratega decide basado en el Playbook
        print(f"[Agente Estratega]: Consultando Reglas de Oro...")
        # Prioridad Share sobre Costo [cite: 51]
        print(f"  💡 DECISIÓN: Activar NIVEL BETA (Bundle Promocional) en {localidad}. [cite: 40]")
        print(f"  📍 Acción: Asegurar SKU líder a altura de ojos. [cite: 40]")

if __name__ == "__main__":
    run_weekly_audit("Kennedy")