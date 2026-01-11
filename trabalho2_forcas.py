import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# ========== CONSTANTES FÍSICAS ==========
K_E = 8.9875517923e9  # N·m²/C²

# ========== CONFIGURAÇÃO DO STREAMLIT ==========
st.set_page_config(
    page_title="Forças Eletrostáticas 3D",
    layout="wide",
    page_icon="🔬"
)

# ========== CSS ==========
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1E40AF;
        font-size: 2.2rem;
        margin-bottom: 1rem;
    }
    .test-charge-box {
        background: #FEF3C7;
        border: 2px solid #F59E0B;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .fixed-charge-box {
        background: #F3F4F6;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 4px solid #10B981;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# ========== FUNÇÃO DE CÁLCULO ==========
def calcular_forca_coulomb(q_teste, pos_teste, cargas_fixas):
    """Calcula forças sobre carga de teste."""
    forcas = []
    forca_resultante = np.zeros(3)
    
    for carga in cargas_fixas:
        vetor_r = pos_teste - carga['pos']
        distancia = np.linalg.norm(vetor_r)
        
        if distancia < 0.01:
            distancia = 0.01
        
        vetor_unitario = vetor_r / distancia
        magnitude = K_E * abs(q_teste * carga['q']) / distancia**2
        
        if q_teste * carga['q'] > 0:
            vetor_forca = magnitude * vetor_unitario
        else:
            vetor_forca = -magnitude * vetor_unitario
        
        forcas.append({
            'origem': carga['nome'],
            'vetor': vetor_forca,
            'magnitude': magnitude
        })
        forca_resultante += vetor_forca
    
    return forcas, forca_resultante

# ========== INICIALIZAÇÃO ==========
# Valores padrão
if 'tamanho_marcadores' not in st.session_state:
    st.session_state.tamanho_marcadores = 25
if 'escala' not in st.session_state:
    st.session_state.escala = 0.8
if 'mostrar_componentes' not in st.session_state:
    st.session_state.mostrar_componentes = True
if 'cargas_fixas' not in st.session_state:
    st.session_state.cargas_fixas = []
if 'teste_valor' not in st.session_state:
    st.session_state.teste_valor = 1.0
if 'teste_pos' not in st.session_state:
    st.session_state.teste_pos = [0.0, 2.0, 0.0]

# ========== BARRA LATERAL ==========
with st.sidebar:
    st.markdown("### ⚙️ CONFIGURAÇÃO")
    
    # CARGA DE TESTE
    st.markdown("#### 🎯 Carga de Teste")
    st.markdown('<div class="test-charge-box">', unsafe_allow_html=True)
    
    teste_valor = st.number_input(
        "Valor (µC)",
        value=st.session_state.teste_valor,
        min_value=-20.0,
        max_value=20.0,
        step=0.5,
        key="input_teste_valor"
    )
    st.session_state.teste_valor = teste_valor
    
    st.markdown("**Posição:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        teste_x = st.slider("X", -4.0, 4.0, st.session_state.teste_pos[0], 0.1, key="slider_teste_x")
        st.session_state.teste_pos[0] = teste_x
    with col2:
        teste_y = st.slider("Y", -4.0, 4.0, st.session_state.teste_pos[1], 0.1, key="slider_teste_y")
        st.session_state.teste_pos[1] = teste_y
    with col3:
        teste_z = st.slider("Z", -4.0, 4.0, st.session_state.teste_pos[2], 0.1, key="slider_teste_z")
        st.session_state.teste_pos[2] = teste_z
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CARGAS FIXAS
    st.markdown("#### 🔧 Cargas Fixas")
    
    num_cargas = st.number_input(
        "Número de cargas fixas:",
        min_value=1,
        max_value=6,
        value=2,
        step=1,
        key="num_cargas"
    )
    
    # Criar/atualizar cargas fixas
    cargas_fixas = []
    for i in range(num_cargas):
        st.markdown(f'**Carga Q{i+1}**')
        st.markdown('<div class="fixed-charge-box">', unsafe_allow_html=True)
        
        valor = st.number_input(
            f"Valor (µC)",
            value=5.0 if i == 0 else -5.0,
            key=f"fixa_q_{i}"
        )
        
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            x = st.slider("X", -4.0, 4.0, float(i*2 - 1), 0.1, key=f"fixa_x_{i}")
        with col_y:
            y = st.slider("Y", -4.0, 4.0, 0.0, 0.1, key=f"fixa_y_{i}")
        with col_z:
            z = st.slider("Z", -4.0, 4.0, 0.0, 0.1, key=f"fixa_z_{i}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        cargas_fixas.append({
            'q': valor * 1e-6,
            'pos': np.array([x, y, z]),
            'valor_µC': valor,
            'nome': f"Q{i+1}"
        })
    
    st.session_state.cargas_fixas = cargas_fixas
    
    # OPÇÕES DE VISUALIZAÇÃO
    st.markdown("#### ⚡ Visualização")
    
    mostrar_componentes = st.checkbox(
        "Mostrar forças individuais",
        value=st.session_state.mostrar_componentes,
        key="check_componentes"
    )
    st.session_state.mostrar_componentes = mostrar_componentes
    
    escala = st.slider(
        "Escala dos vetores",
        min_value=0.1,
        max_value=2.0,
        value=st.session_state.escala,
        key="slider_escala"
    )
    st.session_state.escala = escala
    
    tamanho_marcadores = st.slider(
        "Tamanho marcadores",
        min_value=10,
        max_value=40,
        value=st.session_state.tamanho_marcadores,
        key="slider_tamanho"
    )
    st.session_state.tamanho_marcadores = tamanho_marcadores
    
    if st.button("🔄 Resetar Configuração", type="secondary"):
        st.session_state.clear()
        st.rerun()

# ========== CABEÇALHO ==========
st.markdown('<h1 class="main-title">🔬 Trabalho 2: Forças Eletrostáticas 3D</h1>', unsafe_allow_html=True)
st.markdown("**Ano Letivo 2025/2026 - Lei de Coulomb e Superposição Vetorial**")

# ========== CÁLCULOS ==========
q_teste = st.session_state.teste_valor * 1e-6
pos_teste = np.array(st.session_state.teste_pos)
cargas_fixas = st.session_state.cargas_fixas

# Calcular forças
forcas_individuais, forca_resultante = calcular_forca_coulomb(q_teste, pos_teste, cargas_fixas)
magnitude_resultante = np.linalg.norm(forca_resultante)

# ========== MÉTRICAS ==========
st.markdown("---")
st.markdown("### 📊 ANÁLISE NUMÉRICA")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        "Força Resultante",
        f"{magnitude_resultante:.2e} N",
        help="Força total sobre a carga de teste"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    if magnitude_resultante > 1e-10:
        theta = np.degrees(np.arctan2(forca_resultante[1], forca_resultante[0]))
        phi = np.degrees(np.arctan2(forca_resultante[2], np.sqrt(forca_resultante[0]**2 + forca_resultante[1]**2)))
        st.metric("Direção", f"θ={theta:.0f}°, φ={phi:.0f}°")
    else:
        st.metric("Direção", "Indefinida")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    equilibrio = magnitude_resultante < 1e-6
    st.metric(
        "Equilíbrio",
        "✅ SIM" if equilibrio else "⚠️ NÃO",
        delta="Estável" if equilibrio else "Instável"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ========== VISUALIZAÇÃO 3D ==========
st.markdown("---")
st.markdown("### 📈 VISUALIZAÇÃO 3D")

fig = go.Figure()

# Cores
cor_positiva = "#EF4444"
cor_negativa = "#3B82F6"
cor_teste = "#F59E0B"
cor_componente = "#6B7280"
cor_resultante = "#DC2626"

# 1. CARGAS FIXAS
if cargas_fixas:
    for carga in cargas_fixas:
        cor = cor_positiva if carga['q'] > 0 else cor_negativa
        
        fig.add_trace(go.Scatter3d(
            x=[carga['pos'][0]],
            y=[carga['pos'][1]],
            z=[carga['pos'][2]],
            mode='markers+text',
            marker=dict(
                size=st.session_state.tamanho_marcadores,
                color=cor,
                symbol='circle',
                line=dict(color='white', width=2),
                opacity=0.9
            ),
            text=[f"Fixa {carga['nome']}"],
            textposition="top center",
            name=f"{carga['nome']} ({carga['valor_µC']} µC)",
            legendgroup="fixas",
            showlegend=True
        ))

# 2. CARGA DE TESTE
fig.add_trace(go.Scatter3d(
    x=[pos_teste[0]],
    y=[pos_teste[1]],
    z=[pos_teste[2]],
    mode='markers+text',
    marker=dict(
        size=st.session_state.tamanho_marcadores + 10,
        color=cor_teste,
        symbol='diamond',
        line=dict(color='black', width=3),
        opacity=1.0
    ),
    text=["TESTE"],
    textposition="bottom center",
    name=f"🎯 Teste ({st.session_state.teste_valor} µC)",
    legendgroup="teste",
    showlegend=True
))

# 3. FORÇAS COMPONENTES
if st.session_state.mostrar_componentes and forcas_individuais:
    for forca in forcas_individuais:
        if forca['magnitude'] > 1e-12:
            escala_visual = st.session_state.escala * 1e9
            vetor_visual = forca['vetor'] * escala_visual
            ponto_final = pos_teste + vetor_visual
            
            # Linha
            fig.add_trace(go.Scatter3d(
                x=[pos_teste[0], ponto_final[0]],
                y=[pos_teste[1], ponto_final[1]],
                z=[pos_teste[2], ponto_final[2]],
                mode='lines',
                line=dict(
                    color=cor_componente,
                    width=2,
                    dash='dash'
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Cabeça
            fig.add_trace(go.Cone(
                x=[ponto_final[0]],
                y=[ponto_final[1]],
                z=[ponto_final[2]],
                u=[vetor_visual[0]],
                v=[vetor_visual[1]],
                w=[vetor_visual[2]],
                sizemode='absolute',
                sizeref=0.3,
                colorscale=[[0, cor_componente], [1, cor_componente]],
                showscale=False,
                hoverinfo='skip'
            ))

# 4. FORÇA RESULTANTE
if magnitude_resultante > 1e-12:
    escala_resultante = st.session_state.escala * 1e9
    vetor_resultante_visual = forca_resultante * escala_resultante
    ponto_final_resultante = pos_teste + vetor_resultante_visual
    
    # Linha
    fig.add_trace(go.Scatter3d(
        x=[pos_teste[0], ponto_final_resultante[0]],
        y=[pos_teste[1], ponto_final_resultante[1]],
        z=[pos_teste[2], ponto_final_resultante[2]],
        mode='lines',
        line=dict(
            color=cor_resultante,
            width=6
        ),
        name=f"🔴 Resultante: {magnitude_resultante:.2e} N",
        legendgroup="resultante",
        showlegend=True
    ))
    
    # Cabeça
    fig.add_trace(go.Cone(
        x=[ponto_final_resultante[0]],
        y=[ponto_final_resultante[1]],
        z=[ponto_final_resultante[2]],
        u=[vetor_resultante_visual[0]],
        v=[vetor_resultante_visual[1]],
        w=[vetor_resultante_visual[2]],
        sizemode='absolute',
        sizeref=0.5,
        colorscale=[[0, cor_resultante], [1, cor_resultante]],
        showscale=False,
        hoverinfo='skip'
    ))

# Layout do gráfico
fig.update_layout(
    scene=dict(
        xaxis=dict(
            title="Eixo X (m)",
            gridcolor="lightgray",
            showbackground=True,
            backgroundcolor="white",
            range=[-5, 5]
        ),
        yaxis=dict(
            title="Eixo Y (m)",
            gridcolor="lightgray",
            showbackground=True,
            backgroundcolor="white",
            range=[-5, 5]
        ),
        zaxis=dict(
            title="Eixo Z (m)",
            gridcolor="lightgray",
            showbackground=True,
            backgroundcolor="white",
            range=[-5, 5]
        ),
        aspectmode='cube',
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    ),
    margin=dict(l=0, r=0, t=30, b=0),
    height=650,
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(255, 255, 255, 0.9)"
    )
)

st.plotly_chart(fig, use_container_width=True)

# ========== TABELA ==========
st.markdown("---")
st.markdown("### 📋 TABELA DE FORÇAS")

if forcas_individuais:
    dados = []
    for forca in forcas_individuais:
        dados.append({
            'De': forca['origem'],
            'Fx (nN)': forca['vetor'][0] * 1e9,
            'Fy (nN)': forca['vetor'][1] * 1e9,
            'Fz (nN)': forca['vetor'][2] * 1e9,
            '|F| (nN)': forca['magnitude'] * 1e9
        })
    
    dados.append({
        'De': '🔴 RESULTANTE',
        'Fx (nN)': forca_resultante[0] * 1e9,
        'Fy (nN)': forca_resultante[1] * 1e9,
        'Fz (nN)': forca_resultante[2] * 1e9,
        '|F| (nN)': magnitude_resultante * 1e9
    })
    
    df = pd.DataFrame(dados)
    
    def highlight_row(row):
        if row['De'] == '🔴 RESULTANTE':
            return ['background-color: #FEE2E2; font-weight: bold;'] * len(row)
        return [''] * len(row)
    
    st.dataframe(
        df.style.format("{:.2f}").apply(highlight_row, axis=1),
        use_container_width=True,
        height=300
    )
    
    # Exportar
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Exportar CSV",
        csv,
        "forcas_eletrostaticas.csv",
        "text/csv"
    )

# ========== LEGENDA ==========
with st.expander("📖 LEGENDA", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🎯 Elementos:**")
        st.markdown("""
        - 🔴 Círculo vermelho: Carga fixa positiva
        - 🔵 Círculo azul: Carga fixa negativa
        - 🟡 Diamante amarelo: Carga de teste
        - ⚫ Setas cinzentas: Forças individuais
        - 🔴 Seta vermelha: Força resultante
        """)
    with col2:
        st.markdown("**🎮 Controlos:**")
        st.markdown("""
        - Rodar: Arrastar com rato
        - Zoom: Roda do rato
        - Mover: Botão direito
        - Reset: Ícone 🏠
        """)

st.markdown("---")
st.markdown("*Trabalho Prático 2 - Forças Eletrostáticas | Entregue em 07/01/2026*")