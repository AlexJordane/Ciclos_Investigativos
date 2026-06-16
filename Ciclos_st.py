import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Laboratório de Sistemas Dinâmicos", layout="wide")

st.title("🔬 Laboratório de Investigação de Sistemas Dinâmicos Discretos")
st.write("Trabalho compartilhado para exploração de cadeias numéricas, bacias de atração e ciclos periódicos.")
st.markdown("---")

# --- FUNÇÕES MATEMÁTICAS ---
def aplicar_regra(n, divisor_par, expressao_impar):
    if n % 2 == 0:
        return n // divisor_par
    else:
        # O escopo restrito garante uma execução limpa do eval
        return eval(expressao_impar, {"x": n, "abs": abs})

def normalizar_ciclo(ciclo):
    menor_valor = min(ciclo)
    idx_menor = ciclo.index(menor_valor)
    return tuple(ciclo[idx_menor:] + ciclo[:idx_menor])

# --- BARRA LATERAL: ENTRADA DE DADOS ---
st.sidebar.header("⚙️ Configuração das Regras")

divisor = st.sidebar.selectbox("1. Divisor para números pares:", [2, -2])

st.sidebar.markdown("**2. Operação para números ímpares:**")
st.sidebar.caption("Use a variável 'x'. Exemplos: `x + 11`, `x - 11`, `3*x + 1`, `3*x - 1`")
operacao = st.sidebar.text_input("Digite a expressão:", value="x + 11")

st.sidebar.markdown("---")
st.sidebar.header("🎯 Escopo da Investigação")
opcao = st.sidebar.radio("3. Tipo de teste:", ["Testar número único", "Mapear faixa (intervalo)"])

# --- FLUXO 1: NÚMERO ÚNICO ---
if opcao == "Testar número único":
    num = st.sidebar.number_input("4. Escolha o número inicial:", value=100, step=1)
    
    st.subheader(f"📊 Órbita e Atrator para o Número Inicial: {num}")
    
    G = nx.DiGraph()
    caminho = []
    atual = num
    divergiu = False
    
    while atual not in caminho:
        caminho.append(atual)
        try:
            proximo = aplicar_regra(atual, divisor, operacao)
        except Exception as e:
            st.error(f"Erro ao avaliar a expressão no valor {atual}: {e}")
            divergiu = True
            break
        G.add_edge(atual, proximo)
        atual = proximo
        
        if abs(atual) > 50000:
            st.warning(f"A sequência foi interrompida pois ultrapassou o limite de magnitude (Último valor: {atual}).")
            divergiu = True
            break
            
    if not divergiu:
        # Exibe a sequência em formato textual fluido
        st.markdown("**Caminho percorrido:**")
        st.write(" → ".join(map(str, caminho)) + f" → ({atual}...)")
        
        # Identifica o ciclo final
        indice_ciclo = caminho.index(atual)
        elementos_ciclo = set(caminho[indice_ciclo:])
        
        # Lógica de cores
        cores = []
        for no in G.nodes():
            if no == num:
                cores.append('tab:blue')       # Início
            elif no in elementos_ciclo:
                cores.append('tab:orange')     # Ciclo final
            else:
                cores.append('lightgray')      # Percurso
                
        # Construção do gráfico do Matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))
        pos = nx.spring_layout(G, k=0.3, seed=42)
        nx.draw_networkx_nodes(G, pos, node_color=cores, node_size=600, alpha=0.9, ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=15, width=1.5, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
        ax.axis('off')
        
        # Renderiza no Streamlit
        st.pyplot(fig)

# --- FLUXO 2: FAIXA DE NÚMEROS ---
else:
    col_inf, col_sup = st.sidebar.columns(2)
    inf = col_inf.number_input("Mínimo:", value=-30, step=1)
    sup = col_sup.number_input("Máximo:", value=30, step=1)
    
    st.subheader(f"🕸️ Bacias de Atração no Intervalo [{inf}, {sup}]")
    
    if inf >= sup:
        st.error("O limite mínimo deve ser menor que o máximo.")
    else:
        G = nx.DiGraph()
        ciclos_encontrados = set()
        
        # Processamento da faixa
        for i in range(int(inf), int(sup) + 1):
            caminho_local = []
            atual = i
            while atual not in caminho_local:
                caminho_local.append(atual)
                try:
                    proximo = aplicar_regra(atual, divisor, operacao)
                except:
                    break
                G.add_edge(atual, proximo)
                atual = proximo
                if abs(atual) > max(abs(inf), abs(sup)) * 3:
                    break
            else:
                idx_rep = caminho_local.index(atual)
                ciclo = caminho_local[idx_rep:]
                ciclos_encontrados.add(normalizar_ciclo(ciclo))
                
        lista_ciclos = list(ciclos_encontrados)
        
        # Exibe os dados textuais em colunas organizadas
        st.markdown(f"**Foram encontrados {len(lista_ciclos)} ciclo(s) estável(eis):**")
        for idx, ciclo in enumerate(lista_ciclos, 1):
            st.info(f"**Ciclo {idx}** (comprimento {len(ciclo)}): {list(ciclo)}")
            
        # Lógica de cores usando colormap dinâmico
        cmap = plt.get_cmap('tab10')
        cores = []
        for no in G.nodes():
            cor_no = 'lightgray'
            for idx_ciclo, ciclo in enumerate(lista_ciclos):
                if no in ciclo:
                    cor_no = cmap(idx_ciclo % 10)
                    break
            cores.append(cor_no)
            
        # Construção do gráfico de rede completo
        fig, ax = plt.subplots(figsize=(12, 8))
        pos = nx.spring_layout(G, k=0.25, iterations=50, seed=42)
        nx.draw_networkx_nodes(G, pos, node_color=cores, node_size=350, alpha=0.8, ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.4, arrows=True, arrowsize=10, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
        ax.axis('off')
        
        # Renderiza no Streamlit
        st.pyplot(fig)