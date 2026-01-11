
**Aluno:**Caetano Policarpo Luís 

## Descrição Geral

Estes dois projetos consistem em aplicações web interativas desenvolvidas em Python para visualizar e explorar os conceitos fundamentais de campos e forças eletrostáticas:

- **Projeto 1 – Campo Elétrico** (`campo.py`)  
  Visualização 3D do campo elétrico gerado por cargas pontuais, com linhas de campo (integração numérica RK4), vetores de campo, superposição explícita, ponto de teste para E e F = qE, e cálculo aproximado da energia do campo.

- **Projeto 2 – Força Eletrostática** (`forca.py`)  
  Visualização 3D das forças eletrostáticas entre cargas, com superposição de forças individuais e resultante, energia potencial total U, deteção automática de equilíbrio, tabela de componentes vetoriais e ponto de teste.

As aplicações foram concebidas com rigor matemático (lei de Coulomb na forma vetorial completa, unidades SI), design minimalista e interatividade total, permitindo ao utilizador aprender ativamente manipulando as cargas e observando as alterações em tempo real.

## Tecnologia Utilizada

- **Python 3**  
- **Streamlit** – framework que permite criar aplicações web interativas de forma muito simples e rápida. O código roda localmente no teu computador e abre automaticamente no navegador.  
- **Plotly** – biblioteca para gráficos 3D interativos (rotação, zoom).  
- **NumPy** e **SciPy** – cálculos vetoriais e integração numérica precisa das linhas de campo.

## Requisitos e Instalação

Para executar as aplicações é necessário ter o **Anaconda** instalado (recomendado) ou Python com pip.

### Opção recomendada: Anaconda (mais simples e evita problemas de dependências)

1. Descarrega e instala o Anaconda em https://www.anaconda.com/download (escolhe a versão para o teu sistema operativo).

2. Abre o **Anaconda Prompt** (procura no menu Início).

3. Cria um ambiente dedicado (apenas uma vez):
   ```
   conda create -n eletromagnetismo python=3.11
   conda activate eletromagnetismo
   ```

4. Instala as bibliotecas necessárias:
   ```
   conda install numpy scipy pandas
   pip install streamlit plotly
   ```

### Opção alternativa: Python normal (pip)
Se já tens Python instalado:
```
pip install streamlit plotly numpy scipy pandas
```

## Como Executar as Aplicações

1. Coloca os ficheiros `campo.py` e `forca.py` numa pasta (ex: C:\Users\TeuNome\Documents\Eletromagnetismo).

2. Abre o Anaconda Prompt (ou terminal normal).

3. Navega até à pasta:
   ```
   cd C:\Users\TeuNome\Documents\Eletromagnetismo
   ```

4. Executa uma das aplicações:

   - Projeto 1 – Campo Elétrico:
     ```
     streamlit run campo.py
     ```

   - Projeto 2 – Força Eletrostática:
     ```
     streamlit run forca.py
     ```

5. O Streamlit vai abrir automaticamente o navegador em http://localhost:8501 (se não abrir, abre manualmente).

6. Interage livremente:
   - Muda o número de cargas, magnitude, sinal e posição.
   - Ativa as opções de superposição ou ponto de teste.
   - Rota o gráfico com o rato para ver em 3D.

Para parar a aplicação: volta ao Anaconda Prompt e pressiona **Ctrl + C**.

## Exportação de Dados

Ambas as aplicações têm botões para:
- Exportar imagem do gráfico em alta resolução (4K).
- Exportar dados em formato CSV (útil para análise ou inclusão no relatório).

 Campo-e-for-a-el-trica
