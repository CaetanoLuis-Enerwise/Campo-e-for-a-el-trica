import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import solve_ivp
import pandas as pd

# ========== CONSTANTES FÍSICAS ==========
K_E = 8.9875517923e9  # N·m²/C²
EPSILON_0 = 8.8541878128e-12  # F/m

# ========== CONFIGURAÇÃO DO STREAMLIT ==========
st.set_page_config(
    page_title="Simulação de Campo Elétrico 3D",
    layout="wide",
    page_icon="⚡"
)

# ========== CSS PERSONALIZADO ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .theory-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# ========== CABEÇALHO ==========
st.markdown('<h1 class="main-header">⚡ Simulação 3D de Campo Elétrico</h1>', unsafe_allow_html=True)
st.markdown("**Trabalho Prático 1 - Visualização de Linhas de Campo Elétrico**")

# ========== TEORIA ==========
with st.expander("📚 Fundamentos Teóricos", expanded=False):
    st.markdown("""
    ### Campo Elétrico de Cargas Pontuais
    
    O campo elétrico num ponto do espaço devido a uma carga pontual é dado por:
    
    $$
    \\vec{E} = \\frac{1}{4\\pi\\epsilon_0} \\frac{q}{r^2} \\hat{r}
    $$
    
    Para múltiplas cargas, aplica-se o **princípio da superposição**:
    
    $$
    \\vec{E}_{\\text{total}} = \\sum_{i=1}^{n} \\vec{E}_i
    $$
    
    As linhas de campo:
    1. Saem de cargas positivas e entram em cargas negativas
    2. A densidade é proporcional à intensidade do campo
    3. Nunca se cruzam
    """)

# ========== FUNÇÃO DE CÁLCULO DO CAMPO ==========
def calcular_campo_eletrico(posicao, cargas):
    """
    Calcula o campo elétrico num ponto do espaço.
    
    Args:
        posicao: array [x, y, z] com coordenadas do ponto
        cargas: lista de dicionários com 'q' e 'pos'
    
    Returns:
        Vetor campo elétrico [Ex, Ey, Ez]
    """
    E = np.zeros(3)
    
    for carga in cargas:
        vetor_r = posicao - carga['pos']
        distancia = np.linalg.norm(vetor_r)
        
        if distancia < 0.05:  # Evita singularidade
            continue
            
        E += (K_E * carga['q'] / distancia**3) * vetor_r
    
    return E

# ========== BARRA LATERAL ==========
with st.sidebar:
    st.header("⚙️ Configuração das Cargas")
    
    # Controle do número de cargas
    numero_cargas = st.slider(
        "Número de cargas",
        min_value=1,
        max_value=6,
        value=2,
        help="Quantas cargas pontuais deseja colocar no espaço?"
    )
    
    cargas = []
    
    # Configuração individual de cada carga
    for i in range(numero_cargas):
        with st.expander(f"Carga Q{i+1}", expanded=(i < 2)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                valor = st.number_input(
                    f"Valor (µC)",
                    value=2.0 if i % 2 == 0 else -2.0,
                    format="%.2f",
                    key=f"valor_{i}"
                )
            
            with col2:
                sinal = "Positiva (+)" if valor > 0 else "Negativa (-)"
                st.markdown(f"**Sinal:** {sinal}")
            
            # Posição 3D
            col_x, col_y, col_z = st.columns(3)
            with col_x:
                x = st.slider(f"X", -3.0, 3.0, 
                             float(i * 1.5 - 1.5) if i < 4 else 0.0,
                             key=f"x_{i}")
            with col_y:
                y = st.slider(f"Y", -3.0, 3.0, 0.0, key=f"y_{i}")
            with col_z:
                z = st.slider(f"Z", -3.0, 3.0, 0.0, key=f"z_{i}")
            
            # Converter para Coulombs e armazenar
            q_coulomb = valor * 1e-6
            cargas.append({
                'q': q_coulomb,
                'pos': np.array([x, y, z]),
                'valor_µC': valor,
                'id': i+1
            })
    
    st.divider()
    
    # Configurações da visualização
    st.header("🎨 Visualização")
    
    mostrar_linhas = st.checkbox(
        "Mostrar linhas de campo",
        value=True,
        help="Mostra as linhas de campo que partem das cargas positivas"
    )
    
    mostrar_vetores = st.checkbox(
        "Mostrar vetores do campo",
        value=True,
        help="Mostra cones representando a direção e intensidade do campo"
    )
    
    densidade_grid = st.slider(
        "Densidade do grid",
        min_value=4,
        max_value=10,
        value=6,
        help="Número de pontos em cada eixo para cálculo do campo"
    )
    
    escala_vetores = st.slider(
        "Escala dos vetores",
        min_value=0.1,
        max_value=1.0,
        value=0.3,
        help="Tamanho visual dos cones do campo"
    )
    
    if st.button("🔄 Resetar Visualização"):
        st.rerun()

# ========== CÁLCULOS E MÉTRICAS ==========
# Calcular carga total
carga_total = sum(c['q'] for c in cargas) * 1e6  # Convert to µC

# Calcular energia aproximada do campo
pontos_amostra = np.linspace(-2, 2, 8)
energia_total = 0

for x in pontos_amostra:
    for y in pontos_amostra:
        for z in pontos_amostra:
            E = calcular_campo_eletrico(np.array([x, y, z]), cargas)
            energia_total += np.dot(E, E)

energia_total *= 0.5 * EPSILON_0 * (4/7)**3  # Fator de volume aproximado

# Mostrar métricas
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Carga Total", f"{carga_total:.2f} µC")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Energia do Campo", f"{energia_total:.2e} J")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Número de Cargas", numero_cargas)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== VISUALIZAÇÃO 3D ==========
fig = go.Figure()

# Criar grid para vetores do campo
grid_valores = np.linspace(-3, 3, densidade_grid)
X, Y, Z = np.meshgrid(grid_valores, grid_valores, grid_valores)
pontos_grid = np.vstack([X.ravel(), Y.ravel(), Z.ravel()]).T

# Calcular campo em todos os pontos do grid
vetores_campo = []
intensidades = []
posicoes_validas = []

for ponto in pontos_grid:
    E = calcular_campo_eletrico(ponto, cargas)
    intensidade = np.linalg.norm(E)
    
    if intensidade > 1e-3 and intensidade < 1e8:  # Filtrar valores extremos
        vetores_campo.append(E / intensidade)  # Vetor unitário
        intensidades.append(intensidade)
        posicoes_validas.append(ponto)

if posicoes_validas and mostrar_vetores:
    posicoes_validas = np.array(posicoes_validas)
    vetores_campo = np.array(vetores_campo)
    intensidades = np.array(intensidades)
    
    # Adicionar cones representando o campo
    fig.add_trace(go.Cone(
        x=posicoes_validas[:, 0],
        y=posicoes_validas[:, 1],
        z=posicoes_validas[:, 2],
        u=vetores_campo[:, 0],
        v=vetores_campo[:, 1],
        w=vetores_campo[:, 2],
        colorscale='Viridis',
        sizemode='scaled',
        sizeref=2.0 * escala_vetores,
        colorbar=dict(title="Intensidade |E|"),
        showscale=True,
        opacity=0.7
    ))

# Adicionar linhas de campo (RK4)
if mostrar_linhas:
    for carga in cargas:
        if carga['q'] > 0:  # Linhas saem de cargas positivas
            # Gerar pontos iniciais em uma pequena esfera
            n_linhas = 12
            for _ in range(n_linhas):
                # Ponto inicial aleatório perto da carga
                direcao = np.random.randn(3)
                direcao /= np.linalg.norm(direcao)
                ponto_inicial = carga['pos'] + 0.2 * direcao
                
                # Integrar trajetória
                def equacao_diferencial(t, pos):
                    E = calcular_campo_eletrico(pos, cargas)
                    norma = np.linalg.norm(E)
                    return E / norma if norma > 1e-6 else [0, 0, 0]
                
                try:
                    solucao = solve_ivp(
                        equacao_diferencial,
                        [0, 8],
                        ponto_inicial,
                        t_eval=np.linspace(0, 8, 50),
                        method='RK45'
                    )
                    
                    fig.add_trace(go.Scatter3d(
                        x=solucao.y[0],
                        y=solucao.y[1],
                        z=solucao.y[2],
                        mode='lines',
                        line=dict(color='#666666', width=2),
                        opacity=0.4,
                        showlegend=False
                    ))
                except:
                    pass

# Adicionar as cargas (esferas coloridas)
for carga in cargas:
    cor = "#EF4444" if carga['q'] > 0 else "#3B82F6"  # Vermelho/Azul
    tamanho = 15 + abs(carga['valor_µC']) * 3
    
    fig.add_trace(go.Scatter3d(
        x=[carga['pos'][0]],
        y=[carga['pos'][1]],
        z=[carga['pos'][2]],
        mode='markers+text',
        marker=dict(
            size=tamanho,
            color=cor,
            line=dict(color='white', width=2)
        ),
        text=[f"Q{carga['id']}"],
        textposition="top center",
        name=f"Carga {carga['id']} ({carga['valor_µC']} µC)"
    ))

# Configurar layout da cena 3D
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='cube',
        bgcolor='white',
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    ),
    margin=dict(l=0, r=0, t=30, b=0),
    height=700,
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

# Mostrar o gráfico
st.plotly_chart(fig, use_container_width=True)

# ========== TABELA DE DADOS ==========
st.subheader("📊 Dados das Cargas")
dados_cargas = pd.DataFrame([{
    'Carga': f"Q{c['id']}",
    'Valor (µC)': c['valor_µC'],
    'Posição X': f"{c['pos'][0]:.2f} m",
    'Posição Y': f"{c['pos'][1]:.2f} m",
    'Posição Z': f"{c['pos'][2]:.2f} m",
    'Sinal': 'Positiva' if c['q'] > 0 else 'Negativa'
} for c in cargas])

st.dataframe(dados_cargas, use_container_width=True)

# ========== EXPORTAÇÃO ==========
col_export1, col_export2 = st.columns(2)

with col_export1:
    # Exportar dados como CSV
    csv = dados_cargas.to_csv(index=False)
    st.download_button(
        label="📥 Exportar Dados (CSV)",
        data=csv,
        file_name="cargas_eletricas.csv",
        mime="text/csv"
    )

with col_export2:
    # Instruções
    with st.expander("💡 Como usar"):
        st.markdown("""
        1. **Rodar**: Use o mouse para rodar a visualização 3D
        2. **Zoom**: Use a roda do mouse para zoom in/out
        3. **Cargas**: Clique nas cargas na legenda para mostrar/esconder
        4. **Reset**: Use o botão na barra lateral para resetar
        """)

st.divider()
st.caption("Trabalho Prático 1 - Eletromagnetismo 2025/2026 | Desenvolvido com Python e Plotly")