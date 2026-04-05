import streamlit as st
import pandas as pd
import numpy as np
import time
import json
import re
import pydeck as pdk
import plotly.express as px
from rag_engine import PepsicoRAG

st.set_page_config(page_title="Pepsico Strategy Room - Ultra Plus", layout="wide")

@st.cache_resource
def load_rag_v7(): return PepsicoRAG()

@st.cache_data
def load_data_v7():
    try:
        df = pd.read_csv('data/bogota_market_share_history_v2.csv')
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        return df.sort_values(by='Fecha').reset_index(drop=True)
    except: return pd.DataFrame()

rag = load_rag_v7()
df = load_data_v7()

if "memory_log" not in st.session_state: st.session_state.memory_log = []
if "current_week_idx" not in st.session_state: st.session_state.current_week_idx = 0
if "max_weeks_to_sim" not in st.session_state: st.session_state.max_weeks_to_sim = 4
if "messages" not in st.session_state: st.session_state.messages = []

# Extraer semanas a partir de 2026 para el Autonomous Loop
def extraer_semanas(dataframe):
    if dataframe.empty: return []
    df_2026 = dataframe[dataframe['Fecha'].dt.year >= 2026] if not dataframe[dataframe['Fecha'].dt.year >= 2026].empty else dataframe
    return df_2026.groupby(pd.Grouper(key='Fecha', freq='W-MON')).apply(lambda x: x).reset_index(drop=True).groupby('Fecha').mean(numeric_only=True).reset_index().to_dict('records')

semanas_data = extraer_semanas(df)

COORDS_20 = {
    'Usaquén': [4.7100, -74.0300], 'Chapinero': [4.6300, -74.0600], 'Santa Fe': [4.6000, -74.0600],
    'San Cristóbal': [4.5500, -74.0700], 'Usme': [4.4500, -74.1100], 'Tunjuelito': [4.5800, -74.1300],
    'Bosa': [4.6100, -74.1900], 'Kennedy': [4.6300, -74.1500], 'Fontibón': [4.6700, -74.1400],
    'Engativá': [4.6900, -74.1100], 'Suba': [4.7400, -74.0800], 'Barrios Unidos': [4.6600, -74.0700],
    'Teusaquillo': [4.6300, -74.0800], 'Los Mártires': [4.6000, -74.0800], 'Antonio Nariño': [4.5800, -74.0900],
    'Puente Aranda': [4.6100, -74.1100], 'La Candelaria': [4.5900, -74.0700], 'Rafael Uribe Uribe': [4.5600, -74.1100],
    'Ciudad Bolívar': [4.5600, -74.1500], 'Sumapaz': [4.1500, -74.3100]
}

st.title("🧃 Pepsico System - Full Autonomous V4")

col_izq, col_der = st.columns([1.3, 1.1])

with col_izq:
    st.subheader("📊 Cuadro de Mando Integral")
    
    if len(semanas_data) > 0:
        data_actual = semanas_data[st.session_state.current_week_idx] if st.session_state.current_week_idx < len(semanas_data) else semanas_data[-1]
        fecha_str = data_actual.get('Fecha', pd.NaT).strftime("%Y-%m-%d") if pd.notnull(data_actual.get('Fecha')) else "Actual"
        st.markdown(f"**Semana Operativa:** {fecha_str}")
        
        caida_vol = np.random.normal(-5, 3) if np.random.random() < 0.5 else np.random.normal(2, 1)
        riesgo = abs(caida_vol) / 10.0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Market Share Margarita", "56.2%", f"{caida_vol:.1f}% vs Promedio")
        c2.metric("OSA Promedio", max(70, min(100, int(100-(data_actual.get('Retraso_Min',0)/10)))), "-2%")
        c3.metric("Sentimiento Cruzado (Voice)", "Deterioro 🔴" if caida_vol < -4 else "Estable 🟢")
        
        st.divider()
        cx1, cx2 = st.columns(2)
        with cx1:
            st.markdown("### Risk Heatmap (20 Zonas)")
            map_data = []
            for loc, crd in COORDS_20.items():
                peso_riesgo = np.random.uniform(0.1, riesgo + 0.3)
                map_data.append({"lon": crd[1], "lat": crd[0], "peso": peso_riesgo, "color": [255, int((1-peso_riesgo)*255), 0]})
            df_map = pd.DataFrame(map_data)
            layer = pdk.Layer("HeatmapLayer", df_map, get_position=["lon", "lat"], get_weight="peso", radiusPixels=50)
            st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=pdk.ViewState(latitude=4.65, longitude=-74.1, zoom=9, pitch=0), height=350))

        with cx2:
            st.markdown("### Causa-Raíz (Drill-down)")
            if not df.empty:
                df_fallas = df[(df['Competidor'] == 'Margarita') & (df['Causa_Principal'] != 'Venta Normal')].copy()
                if not df_fallas.empty:
                    fig = px.treemap(df_fallas, path=['Localidad', 'Estrato', 'Causa_Principal'], values='Ventas_Valor',
                                     color='Inversion_POP', color_continuous_scale='RdBu_r')
                    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=350)
                    st.plotly_chart(fig, use_container_width=True)

with col_der:
    st.subheader("⚡ Trace Autonomous Engine")
    
    cb1, cb2 = st.columns(2)
    with cb1:
        start_btn = st.button("▶️ Start Autonomous Loop")
    with cb2:
        if st.session_state.current_week_idx >= st.session_state.max_weeks_to_sim:
            if st.button("⏭️ Approve & Continue (4 Weeks)"):
                st.session_state.max_weeks_to_sim += 4
                st.rerun()

    feed_placeholder = st.container()
    
    if start_btn or (st.session_state.current_week_idx < st.session_state.max_weeks_to_sim and st.session_state.current_week_idx > 0):
        with feed_placeholder:
            for w_idx in range(st.session_state.current_week_idx, min(st.session_state.max_weeks_to_sim, len(semanas_data))):
                st.session_state.current_week_idx = w_idx
                week_info = semanas_data[w_idx]
                fecha_str = week_info.get('Fecha').strftime("%w-%m-%Y") if pd.notnull(week_info.get('Fecha')) else f"W{w_idx}"
                
                with st.expander(f"Semana {fecha_str} - Verbose Chain", expanded=True):
                    # Analyst
                    with st.chat_message("analyst", avatar="🧑‍💻"):
                        val = week_info.get('Ventas_Valor', 0)
                        pvp = week_info.get('Precio_PVP', 2400)
                        umbral = "⚠️ SE SUPERÓ $2.500 COP" if pvp > 2500 else "✔️ Precio competitivo."
                        ventas_caida = np.random.randint(-15, 2)
                        st.markdown(f"**Market Analyst:** Escaneo completado. \n- **Ventas_Valor**: {val:.1f} COP (Delta: {ventas_caida}%).\n- **Precio_PVP**: {pvp:.1f} COP. {umbral}\n- **Sentimiento VOC**: Deteriorándose por sensibilidad de precio. Posible fuga de demanda hacia competidor.")
                        st.session_state.memory_log.append(f"W{w_idx} Analista: Ventas {val:.1f}, Precio {pvp:.1f} ({umbral}). Sentimiento malo.")
                    
                    # Sentinel
                    with st.chat_message("human", avatar="🚚"):
                        retraso = int(week_info.get('Retraso_Min', 0))
                        osa = max(50, 100 - (retraso/10))
                        st.markdown(f"**Logistics Sentinel:** Evaluando red de suministro.\n- **Retraso_Min**: {retraso} minutos detectados en las troncales principales.\n- **Estado OSA**: {osa:.1f}%. Riesgo logístico inminente para reposición.")
                        st.session_state.memory_log.append(f"W{w_idx} Logística: Retraso {retraso} min, OSA {osa:.1f}%.")
                    
                    # Orchestrator
                    with st.chat_message("assistant", avatar="🧠"):
                        with st.spinner("Sintetizando y cruzando con RAG Playbook..."):
                            time.sleep(0.5)
                            decision = rag.orquestar_debate(st.session_state.memory_log[-2:])
                            st.info(f"**Strategic Orchestrator:** {decision}")
                            st.session_state.memory_log.append(f"W{w_idx} Orchestrator: {decision}")
                time.sleep(1.0)
            
            if st.session_state.current_week_idx >= st.session_state.max_weeks_to_sim - 1:
                st.warning("⚠️ **PAUSA AUTÓNOMA POR FEEDBACK:** El loop ha recorrido 4 iteraciones. Analiza las métricas y oprime 'Approve & Continue' para reanudar.")

    st.divider()
    st.subheader("💡 RAG Sandbox Chat")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "has_chart" in message and message["has_chart"]:
                try:
                    df_sim = message["chart_data"]
                    st.line_chart(df_sim, y=["Real Trend", "Projected Trend"])
                except Exception as e: pass

    if prompt := st.chat_input("Escribe 'Qué pasa si...' para iniciar Sandbox Mode."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("Ejecutando Forecasting Engine..."):
                resp = rag.responder_consulta(st.session_state.memory_log, st.session_state.messages, prompt)
                
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', resp, re.DOTALL)
                chat_data = None
                
                if json_match:
                    try:
                        sandbox_json = json.loads(json_match.group(1))
                        if sandbox_json.get("is_simulation"):
                            obj = sandbox_json.get("objetivo_alcanzado_estimado", 55.0)
                            if obj is None: obj = 55.0
                            resp_clean = resp.replace(json_match.group(0), '').strip()
                            st.markdown(resp_clean)
                            
                            # Synthetic Line Chart
                            historico_share = [54.0, 52.1, 51.5, 52.0]
                            trend_real = historico_share + [52.0, 51.8, 51.4, 51.4]
                            
                            step = (obj - historico_share[-1]) / 4
                            trend_proj = historico_share + [historico_share[-1] + step*1, historico_share[-1] + step*2, historico_share[-1] + step*3, obj]
                            
                            df_sim = pd.DataFrame({
                                "Semana": ["1_W-3", "2_W-2", "3_W-1", "4_Base", "5_Sim+1", "6_Sim+2", "7_Sim+3", "8_Sim+4"],
                                "Real Trend": trend_real,
                                "Projected Trend": trend_proj
                            }).set_index("Semana")
                            
                            st.line_chart(df_sim, y=["Real Trend", "Projected Trend"])
                            chat_data = df_sim
                        else:
                            resp_clean = resp.replace(json_match.group(0), '').strip()
                            st.markdown(resp_clean)
                    except:
                        st.markdown(resp)
                        resp_clean = resp
                else:
                    st.markdown(resp)
                    resp_clean = resp
                    
        message_to_save = {"role": "assistant", "content": resp_clean}
        if chat_data is not None:
            message_to_save["has_chart"] = True
            message_to_save["chart_data"] = chat_data
            
        st.session_state.messages.append(message_to_save)
