import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import solve_ivp
from typing import List, Dict

k_e = 8.99e9
epsilon_0 = 1 / (4 * np.pi * k_e)

st.set_page_config(page_title="Campo Elétrico", layout="centered")

st.title("Campo Elétrico")

st.markdown("""
O campo elétrico é uma presença invisível que dá forma ao espaço à volta das cargas.  
Ele é definido em cada ponto como a força que uma carga-teste positiva unitária sentiria, dada pela lei de Coulomb vetorial:
""")

st.latex(r"\mathbf{E}(\mathbf{r}) = k_e \sum_i \frac{q_i (\mathbf{r} - \mathbf{r}_i)}{|\mathbf{r} - \mathbf{r}_i|^3}")

st.markdown("""
Explore como ele surge da superposição das contribuições individuais.  
Mova as cargas e veja o padrão evoluir — pergunte a si mesmo: o que acontece se aproximar duas cargas opostas?
""")

# Controles intuitivos – sidebar para não poluir a vista
with st.sidebar:
    st.header("Defina as Cargas")
    num_charges = st.slider("Número de cargas", 1, 5, 2, help="Adicione cargas para ver a superposição em ação")
    charges: List[Dict] = []
    for i in range(num_charges):
        with st.expander(f"Carga {i+1}", expanded=i < 2):
            q_mag = st.number_input(f"Magnitude (μC)", min_value=0.1, max_value=10.0, value=1.0, step=0.1, key=f"q_mag_{i}")
            sign = st.radio(f"Sinal", ["+", "-"], horizontal=True, index=0 if i%2==0 else 1, key=f"sign_{i}")
            q = q_mag * 1e-6 if sign == "+" else -q_mag * 1e-6
            x = st.number_input(f"x (m)", min_value=-2.0, max_value=2.0, value=-0.5 if i%2==0 else 0.5, step=0.1, key=f"x_{i}")
            y = st.number_input(f"y (m)", min_value=-2.0, max_value=2.0, value=0.0, step=0.1, key=f"y_{i}")
            z = st.number_input(f"z (m)", min_value=-2.0, max_value=2.0, value=0.0, step=0.1, key=f"z_{i}")
            charges.append({"pos": np.array([x, y, z]), "q": q})

    st.header("Visualização")
    num_lines = st.slider("Densidade de linhas de campo", 10, 50, 25, help="Mais linhas revelam melhor a intensidade |E|")
    show_individual = st.checkbox("Mostrar contribuições individuais (superposição)", value=False, help="Veja como E_total = Σ E_i")
    show_test = st.checkbox("Adicionar ponto de teste para E e F = q E", value=False, help="Teste a força numa carga virtual")

    if show_test:
        st.subheader("Ponto de Teste")
        test_q = st.number_input("q_teste (μC)", min_value=-10.0, max_value=10.0, value=1.0, step=0.1)
        test_q *= 1e-6
        test_x = st.slider("x_teste (m)", -2.0, 2.0, 0.0, 0.1)
        test_y = st.slider("y_teste (m)", -2.0, 2.0, 0.0, 0.1)
        test_z = st.slider("z_teste (m)", -2.0, 2.0, 0.0, 0.1)
        test_pos = np.array([test_x, test_y, test_z])

# Cálculos rigorosos
def e_individual(pos: np.ndarray, charge: Dict) -> np.ndarray:
    r_vec = pos - charge["pos"]
    r = np.linalg.norm(r_vec)
    if r < 1e-8:
        return np.zeros(3)
    return k_e * charge["q"] * r_vec / r**3

def e_total(pos: np.ndarray, charges: List[Dict]) -> np.ndarray:
    return sum(e_individual(pos, c) for c in charges)

def potential(pos: np.ndarray, charges: List[Dict]) -> float:
    V = 0.0
    for c in charges:
        r = np.linalg.norm(pos - c["pos"])
        if r < 1e-8:
            continue
        V += k_e * c["q"] / r
    return V

# Energia U (aproximação numérica)
grid_size_energy = 20
x_range = np.linspace(-2, 2, grid_size_energy)
X, Y, Z = np.meshgrid(x_range, x_range, x_range)
points_energy = np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))
E_values = np.array([e_total(p) for p in points_energy])
dV = ((4) / (grid_size_energy - 1))**3
U = (epsilon_0 / 2) * np.sum(np.linalg.norm(E_values, axis=1)**2) * dV

# Malha para visualização
grid_size = 15
x = np.linspace(-1.5, 1.5, grid_size)
X_v, Y_v, Z_v = np.meshgrid(x, x, x)
points_v = np.column_stack((X_v.ravel(), Y_v.ravel(), Z_v.ravel()))

# Figura 3D
fig = go.Figure()

# Linhas de campo
starts = np.random.uniform(-1.2, 1.2, (num_lines, 3))
for start in starts:
    def ode(t, r):
        E = e_total(r)
        norm = np.linalg.norm(E)
        return E / norm if norm > 1e-8 else np.zeros(3)
    sol = solve_ivp(ode, [0, 5], start, t_eval=np.linspace(0, 5, 100), rtol=1e-5)
    line = sol.y.T
    fig.add_trace(go.Scatter3d(x=line[:,0], y=line[:,1], z=line[:,2], mode='lines', line=dict(color='#007AFF', width=2), showlegend=False))

# Vetores E total
E_grid = np.array([e_total(p) for p in points_v[::4]])
norm_E = np.linalg.norm(E_grid, axis=1)
scale = 0.8 / (norm_E.max() + 1e-8)
fig.add_trace(go.Cone(x=points_v[::4,0], y=points_v[::4,1], z=points_v[::4,2], u=E_grid[:,0]*scale, v=E_grid[:,1]*scale, w=E_grid[:,2]*scale, colorscale='Blues', sizemode='absolute', sizeref=0.2, showscale=False, name="E total"))

# Superposição individual
if show_individual:
    colors = ['#FF3B30', '#34C759', '#FFCC00', '#AF52DE', '#FF9500']
    for i, c in enumerate(charges):
        E_ind = np.array([e_individual(p, c) for p in points_v[::4]])
        fig.add_trace(go.Cone(x=points_v[::4,0], y=points_v[::4,1], z=points_v[::4,2], u=E_ind[:,0]*scale, v=E_ind[:,1]*scale, w=E_ind[:,2]*scale, colorscale=[[0, colors[i]], [1, colors[i]]], sizemode='absolute', sizeref=0.2, name=f"E de q{i+1}", opacity=0.7))

# Cargas
for i, c in enumerate(charges):
    color = '#FF3B30' if c["q"] > 0 else '#007AFF'
    size = 10 + abs(c["q"] * 1e6) * 3
    fig.add_trace(go.Scatter3d(x=[c["pos"][0]], y=[c["pos"][1]], z=[c["pos"][2]], mode='markers+text', marker=dict(size=size, color=color), text=f"q{i+1}", textposition="top center"))

# Ponto de teste
if show_test:
    E_test = e_total(test_pos)
    F_test = test_q * E_test
    V_test = potential(test_pos, charges)
    fig.add_trace(go.Scatter3d(x=[test_pos[0]], y=[test_pos[1]], z=[test_pos[2]], mode='markers', marker=dict(size=10, color='#FFCC00', symbol='diamond'), name='Ponto teste'))
    fig.add_trace(go.Cone(x=[test_pos[0]], y=[test_pos[1]], z=[test_pos[2]], u=[F_test[0]*scale*2], v=[F_test[1]*scale*2], w=[F_test[2]*scale*2], colorscale='Greens', sizemode='absolute', sizeref=0.2, name='F = q E'))

    col1, col2, col3 = st.columns(3)
    col1.metric("Campo |E| no ponto", f"{np.linalg.norm(E_test):.2e} N/C")
    col2.metric("Força |F| = q |E|", f"{np.linalg.norm(F_test):.2e} N")
    col3.metric("Potencial V no ponto", f"{V_test:.2e} V")

# Energia U
col_u1, col_u2 = st.columns(2)
col_u1.metric("Energia do campo U ≈", f"{U:.2e} J")
col_u2.latex(r"U = \frac{\epsilon_0}{2} \int E^2 dV")

fig.update_layout(scene=dict(aspectmode='cube', bgcolor='white', xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), zaxis=dict(showgrid=False, zeroline=False, showticklabels=False)), height=700, margin=dict(l=0, r=0, b=0, t=0))

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
Explore: ative a superposição individual e veja como o campo total é a soma vetorial — como se cada carga contribuísse o seu pedaço ao todo.  
As linhas de campo, tangentes a E, mostram direção; a densidade revela intensidade, proporcional a 1/r² para uma carga isolada.  
Com o ponto de teste, sinta o campo: a força F é q E, e o potencial V é a 'altura' energética, com trabalho W = q ∫ E·dl independente do caminho porque ∇×E = 0.  
Pergunte: o que acontece no centro de um dipolo? Experimente e descubra.
""")

# Exportações
if st.button("Exportar imagem 4K"):
    st.plotly_chart(fig.to_image(format="png", scale=4))

st.download_button("Exportar dados CSV", data=pd.DataFrame([{"x": p[0], "y": p[1], "z": p[2], "Ex": e[0], "Ey": e[1], "Ez": e[2]} for p, e in zip(points_v[::4], E_grid)]).to_csv(), file_name="campos.csv")