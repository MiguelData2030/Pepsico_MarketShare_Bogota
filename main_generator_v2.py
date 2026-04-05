import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_robust_market_data():
    # Configuración de Bogotá
    localidades = {
        'Kennedy': {'estrato': 2, 'base_vol': 1.2},
        'Bosa': {'estrato': 2, 'base_vol': 1.1},
        'Suba': {'estrato': 3, 'base_vol': 1.3},
        'Engativá': {'estrato': 3, 'base_vol': 1.0},
        'Usaquén': {'estrato': 5, 'base_vol': 0.9},
        'Chapinero': {'estrato': 4, 'base_vol': 0.8}
    }
    competidores = ['Margarita', 'Super Ricas', 'D1_MarcaPropia', 'Pringles']
    canales = ['Tradicional', 'Moderno']
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(1185): # 3+ años
        current_date = start_date + timedelta(days=i)
        is_quincena = current_date.day in [15, 30]
        
        for loc, info in localidades.items():
            for canal in canales:
                # 1. Factor Logístico (Retrasos en Bogotá)
                delay_min = np.random.randint(0, 80) if np.random.random() < 0.3 else np.random.randint(0, 20)
                osa_status = 1.0 if delay_min < 30 else 0.82 # Quiebre de stock si delay > 30min [cite: 46]
                
                for comp in competidores:
                    # 2. Configuración de Precio y Umbral (Threshold)
                    # Precio base de $2.500 COP para snacks de 30g [cite: 19]
                    precio_pvp = 2400 if comp != 'Pringles' else 4500
                    if comp == 'Margarita' and np.random.random() < 0.05:
                        precio_pvp = 2650 # Superamos el umbral para probar al agente [cite: 20]
                    
                    # 3. Lógica de Volumen y Market Share
                    volumen_base = 500 * info['base_vol']
                    if is_quincena: volumen_base *= 1.25
                    
                    # Impacto de Ejecución (POP e Inversión) 
                    inversion_pop = np.random.choice([0, 50000, 150000], p=[0.7, 0.2, 0.1])
                    efecto_pop = 1.15 if inversion_pop > 0 else 1.0
                    
                    # 4. Determinación de Causa de No Venta
                    causa = "Venta Normal"
                    v_final = volumen_base * osa_status * efecto_pop
                    
                    if osa_status < 1.0: 
                        causa = "Logística (Retraso)"
                    elif precio_pvp > 2500 and comp == 'Margarita':
                        v_final *= 0.82 # Caída del 18% por umbral de precio [cite: 20]
                        causa = "Precio (Umbral Excedido)"
                    elif (comp == 'Super Ricas' and np.random.random() < 0.1):
                        v_final *= 1.3
                        causa = "Ataque Competencia (Promo)"
                    
                    data.append([
                        current_date, loc, info['estrato'], canal, comp, 
                        round(v_final, 2), precio_pvp, delay_min, 
                        inversion_pop, causa
                    ])

    df = pd.DataFrame(data, columns=[
        'Fecha', 'Localidad', 'Estrato', 'Canal', 'Competidor', 
        'Ventas_Valor', 'Precio_PVP', 'Retraso_Min', 'Inversion_POP', 'Causa_Principal'
    ])
    
    df.to_csv('data/bogota_market_share_history_v2.csv', index=False)
    print("✅ Base de Datos 'Ejecutiva' v2 generada con éxito.")

if __name__ == "__main__":
    generate_robust_market_data()