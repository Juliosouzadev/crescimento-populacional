"""
Dashboard: População e Crescimento Demográfico (Censo 2010 x 2022)
Persona: prefeitos de Curitiba, Porto Alegre, Belo Horizonte, Salvador e Florianópolis
Fonte principal: IBGE - Censo Demográfico 2022 (População 2010 compatibilizada)
"""
import json
import re
import urllib.request
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

st.set_page_config(page_title="CP Analytics | Crescimento Populacional",
                   page_icon="✦", layout="wide")

# ------------------------------------------------------------------ IDENTIDADE VISUAL
OURO, OURO_ESC, OURO_CLARO, GRAFITE = "#C9A227", "#8A6D12", "#F7F0DC", "#1F2430"
PALETA = ["#C9A227", "#1F2430", "#8A6D12", "#6B7280", "#E3C565", "#A16207"]
ESCALA_OURO = [[0, "#FBF7EC"], [0.5, "#D4AF37"], [1, "#5C4510"]]

pio.templates["cp"] = go.layout.Template(layout=dict(
    font=dict(family="Inter, sans-serif", color=GRAFITE, size=13),
    colorway=PALETA, paper_bgcolor="white", plot_bgcolor="white",
    title=dict(font=dict(size=16, color=GRAFITE)),
    xaxis=dict(gridcolor="#F1EBDA", zerolinecolor="#E5DCC3"),
    yaxis=dict(gridcolor="#F1EBDA", zerolinecolor="#E5DCC3"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="white", bordercolor=OURO, font_color=GRAFITE),
))
pio.templates.default = "plotly_white+cp"
px.defaults.template = "plotly_white+cp"
px.defaults.color_discrete_sequence = PALETA

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');
html, body, [class*="css"], [data-testid="stAppViewContainer"] {{ font-family: 'Inter', sans-serif; }}
[data-testid="stAppViewContainer"], [data-testid="stHeader"] {{ background: #FFFFFF; }}
[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #FFFDF7 0%, {OURO_CLARO} 100%);
    border-right: 1px solid #EADFBF; }}
[data-testid="stSidebar"] * {{ color: {GRAFITE}; }}
.block-container {{ padding-top: 1.5rem; max-width: 1300px; }}
h1, h2, h3 {{ color: {GRAFITE}; letter-spacing: -0.01em; }}
h2, h3 {{ border-left: 4px solid {OURO}; padding-left: .6rem; }}

.cp-hero {{ background: linear-gradient(120deg, #FFFFFF 0%, #FBF6E6 55%, #F3E6BC 100%);
    border: 1px solid #EADFBF; border-radius: 20px; padding: 28px 34px; margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(201,162,39,.12); }}
.cp-marca {{ display:flex; align-items:center; gap:12px; margin-bottom:10px; }}
.cp-logo {{ width:46px; height:46px; border-radius:12px; display:flex; align-items:center;
    justify-content:center; font-weight:800; color:white; font-size:18px;
    background: linear-gradient(135deg, {OURO} 0%, {OURO_ESC} 100%);
    box-shadow: 0 6px 16px rgba(138,109,18,.35); }}
.cp-nome {{ font-family:'Playfair Display', serif; font-size:26px; font-weight:700; color:{GRAFITE}; }}
.cp-nome span {{ color:{OURO}; }}
.cp-tag {{ font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:{OURO_ESC}; font-weight:600; }}
.cp-titulo {{ font-size:34px; font-weight:800; color:{GRAFITE}; line-height:1.15; margin:6px 0 8px; }}
.cp-titulo b {{ background: linear-gradient(90deg, {OURO} 0%, {OURO_ESC} 100%);
    -webkit-background-clip:text; background-clip:text; color:transparent; }}
.cp-sub {{ color:#4B5563; font-size:15px; }}

[data-testid="stMetric"] {{ background:#FFFFFF; border:1px solid #EFE6CB; border-top:4px solid {OURO};
    border-radius:16px; padding:16px 18px; box-shadow:0 4px 14px rgba(31,36,48,.06); }}
[data-testid="stMetricLabel"] p {{ color:#6B7280; font-weight:600; text-transform:uppercase;
    font-size:12px; letter-spacing:.06em; }}
[data-testid="stMetricValue"] {{ color:{GRAFITE}; font-weight:800; }}

.stTabs [data-baseweb="tab-list"] {{ gap:6px; border-bottom:1px solid #EFE6CB; }}
.stTabs [data-baseweb="tab"] {{ border-radius:12px 12px 0 0; padding:10px 18px; font-weight:600; color:#6B7280; }}
.stTabs [aria-selected="true"] {{ background:{OURO_CLARO}; color:{OURO_ESC} !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color:{OURO} !important; }}

[data-testid="stPlotlyChart"] {{ background:white; border:1px solid #F1EBDA; border-radius:16px;
    padding:8px; box-shadow:0 2px 10px rgba(31,36,48,.04); }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-color:#EFE6CB !important; border-radius:14px !important; }}
a {{ color:{OURO_ESC} !important; font-weight:600; }}
/* força o tema claro mesmo se o navegador estiver em modo escuro */
[data-testid="stAppViewContainer"] *, [data-testid="stSidebar"] * {{ color:{GRAFITE}; }}
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="popover"] *,
[data-testid="stFileUploaderDropzone"], [data-testid="stExpander"] details {{
    background-color:#FFFFFF !important; color:{GRAFITE} !important; border-color:#E5DCC3 !important; }}
[data-baseweb="tag"] {{ background-color:{OURO} !important; }}
[data-baseweb="tag"] * {{ color:white !important; }}
[data-testid="stMetricDelta"] svg {{ fill:currentColor; }}
.cp-rodape {{ text-align:center; color:#9CA3AF; font-size:12px; padding:18px 0 4px; }}
.cp-rodape b {{ color:{OURO_ESC}; }}
</style>
""", unsafe_allow_html=True)

PASTA = Path(__file__).parent
ARQ_DADOS = PASTA / "dados" / "censo_municipios_2010_2022.csv"
PASTA_IMG = PASTA / "imagens"

REGIOES = {1: "Norte", 2: "Nordeste", 3: "Sudeste", 4: "Sul", 5: "Centro-Oeste"}
CAPITAIS_PERSONA = {
    "Curitiba": "PR", "Porto Alegre": "RS", "Belo Horizonte": "MG",
    "Salvador": "BA", "Florianópolis": "SC",
}
ANOS_INTERVALO = 12  # 01/08/2010 -> 01/08/2022

# Série histórica oficial dos Censos (população residente - Brasil)
SERIE_BRASIL = pd.DataFrame({
    "Ano": [1970, 1980, 1991, 2000, 2010, 2022],
    "População": [93_134_846, 119_011_052, 146_825_475, 169_799_170,
                  190_755_799, 203_080_756],
})
# Proporção por grandes grupos de idade - Brasil (IBGE, Censo 1980-2022)
GRANDES_GRUPOS = pd.DataFrame({
    "Ano": [1980, 1991, 2000, 2010, 2022],
    "0 a 14 anos": [38.2, 34.7, 29.6, 24.1, 19.8],
    "15 a 64 anos": [57.7, 60.4, 64.5, 68.5, 69.3],
    "65 anos ou mais": [4.0, 4.8, 5.9, 7.4, 10.9],
})

COR_H, COR_M = GRAFITE, OURO
CORES_REGIAO = {"Norte": "#C9A227", "Nordeste": "#8A6D12", "Sudeste": "#1F2430",
                "Sul": "#6B7280", "Centro-Oeste": "#E3C565"}


def mostrar(fig):
    """Exibe gráfico Plotly ocupando a largura toda (compatível com versões do Streamlit)."""
    try:
        st.plotly_chart(fig, width="stretch", theme=None)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, theme=None)


def tabela(df):
    try:
        st.dataframe(df, width="stretch", hide_index=True)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ------------------------------------------------------------------ DADOS
def preparar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["regiao"] = (df["cod_ibge"] // 1_000_000).map(REGIOES)
    df["cod_uf"] = df["cod_ibge"] // 100_000
    df["variacao_abs"] = df["pop_2022"] - df["pop_2010_comp"]
    df["variacao_pct"] = (df["pop_2022"] / df["pop_2010_comp"] - 1) * 100
    # Taxa de crescimento geométrico anual (mesma fórmula do IBGE)
    df["taxa_anual"] = ((df["pop_2022"] / df["pop_2010_comp"]) ** (1 / ANOS_INTERVALO) - 1) * 100
    return df


@st.cache_data
def carregar_dados(arquivo=None) -> pd.DataFrame:
    if arquivo is not None:
        if arquivo.name.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(arquivo, engine="calamine")
        else:
            df = pd.read_csv(arquivo)
    else:
        df = pd.read_csv(ARQ_DADOS)
    return preparar(df)


@st.cache_data(show_spinner=False)
def carregar_geojson():
    urls = [
        "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        "https://raw.githubusercontent.com/giuliano-oliveira/geodata-br-states/main/geojson/br_states.json",
    ]
    ufs = {"AC", "SP", "RJ", "MG", "BA", "RS"}
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                gj = json.loads(r.read().decode("utf-8"))
            props = gj["features"][0]["properties"]
            # descobre qual propriedade guarda a sigla da UF
            for chave in props:
                valores = {str(f["properties"].get(chave)).upper() for f in gj["features"]}
                if ufs <= valores:
                    for f in gj["features"]:
                        f["properties"][chave] = str(f["properties"][chave]).upper()
                    return gj, f"properties.{chave}"
        except Exception:
            continue
    return None, None


@st.cache_data(show_spinner=False)
def carregar_piramide(cod_local: int, nivel: str) -> pd.DataFrame:
    """Busca população por sexo e idade (Censo 2022, Tabela 9514) na API do SIDRA/IBGE."""
    url = (f"https://apisidra.ibge.gov.br/values/t/9514/{nivel}/{cod_local}"
           f"/v/93/p/2022/c2/4,5/c287/all/c286/113635")
    with urllib.request.urlopen(url, timeout=30) as r:
        dados = json.loads(r.read().decode("utf-8"))
    cab, linhas = dados[0], dados[1:]
    k_sexo = next(k for k, v in cab.items() if v == "Sexo")
    k_idade = next(k for k, v in cab.items() if v == "Idade")
    out = []
    for ln in linhas:
        idade = ln[k_idade]
        m = re.match(r"^(\d+) a (\d+) anos$", idade)
        if (m and int(m.group(2)) - int(m.group(1)) == 4) or idade == "100 anos ou mais":
            ini = int(m.group(1)) if m else 100
            val = ln["V"]
            out.append({"Faixa": idade, "inicio": ini, "Sexo": ln[k_sexo],
                        "Pessoas": int(val) if str(val).isdigit() else 0})
    df = pd.DataFrame(out).sort_values("inicio")
    if df.empty:
        raise ValueError("SIDRA não retornou faixas etárias")
    return df


# ------------------------------------------------------------------ SIDEBAR
st.sidebar.markdown(
    '<div class="cp-marca"><div class="cp-logo">CP</div>'
    '<div class="cp-nome">CP <span>Analytics</span></div></div>', unsafe_allow_html=True)
st.sidebar.markdown("### Filtros")
st.sidebar.caption("Censo Demográfico IBGE · 2010 x 2022")

with st.sidebar.expander("📤 Upload de dados (opcional)"):
    st.write("Envie um CSV/XLSX com as colunas: `UF, cod_ibge, municipio, "
             "pop_2010, pop_2010_comp, pop_2022`.")
    up = st.file_uploader("Arquivo", type=["csv", "xlsx"])

try:
    df = carregar_dados(up)
except Exception as e:
    st.sidebar.error(f"Não consegui ler o arquivo enviado ({e}). Usando a base padrão.")
    df = carregar_dados()

regioes_sel = st.sidebar.multiselect("Região", list(REGIOES.values()),
                                     default=list(REGIOES.values()))
ufs_disp = sorted(df[df["regiao"].isin(regioes_sel)]["UF"].unique())
ufs_sel = st.sidebar.multiselect("Unidade da Federação", ufs_disp, default=ufs_disp)

ano_sel = st.sidebar.radio("Ano do Censo (mapa e ranking)",
                           ["2022", "2010", "Crescimento 2010→2022"], index=2)

faixas = ["0 a 4", "5 a 9", "10 a 14", "15 a 19", "20 a 24", "25 a 29", "30 a 34",
          "35 a 39", "40 a 44", "45 a 49", "50 a 54", "55 a 59", "60 a 64",
          "65 a 69", "70 a 74", "75 a 79", "80 a 84", "85 a 89", "90 a 94",
          "95 a 99", "100+"]
faixa_ini, faixa_fim = st.sidebar.select_slider("Faixa etária (pirâmide)",
                                                options=faixas, value=("0 a 4", "100+"))
ano_proj = st.sidebar.slider("Projetar população até", 2025, 2050, 2040, step=5)

base = df[df["UF"].isin(ufs_sel)]
if base.empty:
    st.warning("Selecione ao menos uma região e uma UF na barra lateral.")
    st.stop()

# ------------------------------------------------------------------ CABEÇALHO
st.markdown("""
<div class="cp-hero">
  <div class="cp-marca"><div class="cp-logo">CP</div>
    <div><div class="cp-nome">CP <span>Analytics</span></div>
    <div class="cp-tag">Inteligência em dados demográficos</div></div></div>
  <div class="cp-titulo">Crescimento Populacional e <b>Envelhecimento</b></div>
  <div class="cp-sub">Relatório para Carlos (Curitiba), Eduardo (Porto Alegre), Elisa (Belo Horizonte),
  Jorge (Salvador) e Roberto (Florianópolis) · revisão dos Planos Diretores e do orçamento
  de saúde e infraestrutura urbana · Censo IBGE 2010 x 2022</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ KPIs
p10, p22 = base["pop_2010_comp"].sum(), base["pop_2022"].sum()
taxa = ((p22 / p10) ** (1 / ANOS_INTERVALO) - 1) * 100
encolheram = (base["variacao_abs"] < 0).sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("População 2022", f"{p22:,.0f}".replace(",", "."),
          f"{p22 - p10:+,.0f} desde 2010".replace(",", "."))
c2.metric("Taxa geométrica anual", f"{taxa:.2f}% a.a.".replace(".", ","),
          f"{taxa - 0.52:+.2f} p.p. vs Brasil".replace(".", ","))
c3.metric("Taxa média por município", f"{base['taxa_anual'].mean():.2f}% a.a.".replace(".", ","),
          f"mediana {base['taxa_anual'].median():.2f}%".replace(".", ","), delta_color="off")
c4.metric("Municípios que encolheram", f"{encolheram:,}".replace(",", "."),
          f"{encolheram / len(base) * 100:.1f}% do total".replace(".", ","),
          delta_color="inverse")

aba1, aba2, aba3, aba4, aba5 = st.tabs(
    ["🗺️ Mapa", "👥 Pirâmide etária", "📉 Projeção", "🎯 Outliers", "📰 Notícias"])

# ------------------------------------------------------------------ ABA 1 - MAPA
with aba1:
    uf = base.groupby(["UF", "regiao"], as_index=False)[["pop_2010_comp", "pop_2022"]].sum()
    uf["taxa_anual"] = ((uf["pop_2022"] / uf["pop_2010_comp"]) ** (1 / ANOS_INTERVALO) - 1) * 100
    col_val = {"2022": "pop_2022", "2010": "pop_2010_comp",
               "Crescimento 2010→2022": "taxa_anual"}[ano_sel]
    rotulo = {"pop_2022": "População 2022", "pop_2010_comp": "População 2010",
              "taxa_anual": "Taxa anual (%)"}[col_val]

    st.subheader(f"Mapa de calor por UF: {rotulo}")
    gj, chave = carregar_geojson()
    if gj:
        fig = px.choropleth(uf, geojson=gj, locations="UF", featureidkey=chave,
                            color=col_val, hover_name="UF",
                            hover_data={"pop_2010_comp": ":,", "pop_2022": ":,",
                                        "taxa_anual": ":.2f"},
                            color_continuous_scale=ESCALA_OURO,
                            labels={col_val: rotulo, "pop_2010_comp": "Pop. 2010",
                                    "pop_2022": "Pop. 2022", "taxa_anual": "Taxa a.a. (%)"})
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=560, margin=dict(l=0, r=0, t=10, b=0))
        mostrar(fig)
    else:
        st.info("Não foi possível baixar o contorno dos estados. Exibindo ranking.")
    fig = px.bar(uf.sort_values(col_val), x=col_val, y="UF", color="regiao",
                 orientation="h", labels={col_val: rotulo, "regiao": "Região"},
                 color_discrete_map=CORES_REGIAO)
    fig.add_vline(x=0.52, line_dash="dash", annotation_text="Brasil 0,52%") \
        if col_val == "taxa_anual" else None
    fig.update_layout(height=max(350, 22 * len(uf)))
    mostrar(fig)

# ------------------------------------------------------------------ ABA 2 - PIRÂMIDE
with aba2:
    st.subheader("Pirâmide etária interativa (Censo 2022)")
    local = st.selectbox("Local", ["Brasil"] + ufs_sel)
    try:
        if local == "Brasil":
            pir = carregar_piramide(1, "n1")
        else:
            cod = int(df.loc[df["UF"] == local, "cod_uf"].iloc[0])
            pir = carregar_piramide(cod, "n3")
        i0 = faixas.index(faixa_ini) * 5
        i1 = faixas.index(faixa_fim) * 5
        pir = pir[(pir["inicio"] >= i0) & (pir["inicio"] <= i1)].copy()
        total = pir["Pessoas"].sum()
        pir["%"] = pir["Pessoas"] / total * 100
        h = pir[pir["Sexo"] == "Homens"]
        m = pir[pir["Sexo"] == "Mulheres"]
        fig = go.Figure()
        fig.add_bar(y=h["Faixa"], x=-h["%"], name="Homens", orientation="h",
                    marker_color=COR_H, customdata=h["Pessoas"],
                    hovertemplate="%{y}<br>%{customdata:,} homens<extra></extra>")
        fig.add_bar(y=m["Faixa"], x=m["%"], name="Mulheres", orientation="h",
                    marker_color=COR_M, customdata=m["Pessoas"],
                    hovertemplate="%{y}<br>%{customdata:,} mulheres<extra></extra>")
        lim = pir["%"].max() * 1.15
        fig.update_layout(barmode="relative", bargap=0.05, height=600,
                          xaxis=dict(range=[-lim, lim], title="% da população",
                                     tickvals=[-lim * .66, -lim * .33, 0, lim * .33, lim * .66],
                                     ticktext=[f"{lim*.66:.1f}", f"{lim*.33:.1f}", "0",
                                               f"{lim*.33:.1f}", f"{lim*.66:.1f}"]))
        mostrar(fig)
        idosos = pir[pir["inicio"] >= 65]["Pessoas"].sum()
        criancas = pir[pir["inicio"] < 15]["Pessoas"].sum()
        k1, k2 = st.columns(2)
        k1.metric("Pessoas no recorte", f"{total:,}".replace(",", "."))
        if criancas:
            k2.metric("Índice de envelhecimento (65+ por 100 de 0-14)",
                      f"{idosos / criancas * 100:.1f}".replace(".", ","))
    except Exception:
        st.info("A API do IBGE (SIDRA) não respondeu agora. Mostrando a evolução da "
                "estrutura etária do Brasil por grandes grupos (IBGE, Censos 1980-2022).")
    st.markdown("**Transição demográfica no Brasil (1980 → 2022)**")
    gg = GRANDES_GRUPOS.melt(id_vars="Ano", var_name="Grupo", value_name="%")
    fig = px.bar(gg, x="Ano", y="%", color="Grupo", barmode="stack", text="%",
                 color_discrete_sequence=["#E3C565", "#D1D5DB", GRAFITE])
    fig.update_xaxes(type="category")
    mostrar(fig)

# ------------------------------------------------------------------ ABA 3 - PROJEÇÃO
with aba3:
    st.subheader("Evolução e projeção populacional")
    st.caption("Projeção simples: mantém constante a taxa geométrica anual observada "
               "entre 2010 e 2022. Serve como cenário, não como previsão oficial.")
    escolha = st.selectbox("Comparar", ["Capitais da persona", "UFs selecionadas"])
    anos_fut = list(range(2022, ano_proj + 1, 1))
    if escolha == "Capitais da persona":
        sel = df[df.apply(lambda r: CAPITAIS_PERSONA.get(r["municipio"]) == r["UF"], axis=1)]
        nomes = sel["municipio"]
    else:
        sel = base.groupby("UF", as_index=False)[["pop_2010_comp", "pop_2022"]].sum()
        sel["taxa_anual"] = ((sel["pop_2022"] / sel["pop_2010_comp"]) ** (1 / 12) - 1) * 100
        nomes = sel["UF"]
    linhas = []
    for nome, (_, r) in zip(nomes, sel.iterrows()):
        linhas.append({"Local": nome, "Ano": 2010, "População": r["pop_2010_comp"], "Tipo": "Censo"})
        for a in anos_fut:
            linhas.append({"Local": nome, "Ano": a, "Tipo": "Censo" if a == 2022 else "Projeção",
                           "População": r["pop_2022"] * (1 + r["taxa_anual"] / 100) ** (a - 2022)})
    proj = pd.DataFrame(linhas)
    fig = px.line(proj, x="Ano", y="População", color="Local", markers=False)
    fig.add_vrect(x0=2022, x1=ano_proj, fillcolor=OURO, opacity=0.08,
                  annotation_text="projeção", line_width=0)
    fig.update_layout(height=480)
    mostrar(fig)

    st.markdown("**Brasil: série histórica dos Censos e projeção**")
    tx_br = ((203_080_756 / 190_755_799) ** (1 / 12) - 1)
    fut = pd.DataFrame({"Ano": list(range(2030, ano_proj + 1, 10)) or [ano_proj]})
    fut["População"] = 203_080_756 * (1 + tx_br) ** (fut["Ano"] - 2022)
    fig = go.Figure()
    fig.add_scatter(x=SERIE_BRASIL["Ano"], y=SERIE_BRASIL["População"], mode="lines+markers",
                    name="Censos", line=dict(color=OURO, width=3), marker=dict(size=9))
    fig.add_scatter(x=[2022] + fut["Ano"].tolist(), y=[203_080_756] + fut["População"].tolist(),
                    mode="lines+markers", name="Projeção (0,52% a.a.)",
                    line=dict(color=OURO_ESC, dash="dash"))
    fig.update_layout(height=380, yaxis_title="População")
    mostrar(fig)

# ------------------------------------------------------------------ ABA 4 - OUTLIERS
with aba4:
    st.subheader("Onde estão os outliers de crescimento?")
    q1, q3 = base["taxa_anual"].quantile([.25, .75])
    iqr = q3 - q1
    lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    st.caption(f"Critério de Tukey (IQR): outliers são municípios com taxa anual abaixo de "
               f"{lim_inf:.2f}% ou acima de {lim_sup:.2f}%.".replace(".", ","))
    fig = px.box(base, x="regiao", y="taxa_anual", color="regiao", points="outliers",
                 color_discrete_map=CORES_REGIAO,
                 hover_name="municipio", hover_data={"UF": True, "pop_2022": ":,"},
                 labels={"taxa_anual": "Taxa anual (%)", "regiao": "Região"})
    fig.add_hline(y=0, line_color="gray")
    fig.update_layout(height=480, showlegend=False)
    mostrar(fig)

    fig = px.scatter(base, x="pop_2010_comp", y="taxa_anual", color="regiao", log_x=True,
                     color_discrete_map=CORES_REGIAO,
                     hover_name="municipio", hover_data={"UF": True},
                     labels={"pop_2010_comp": "População 2010 (escala log)",
                             "taxa_anual": "Taxa anual (%)", "regiao": "Região"}, opacity=0.6)
    caps = base[base.apply(lambda r: CAPITAIS_PERSONA.get(r["municipio"]) == r["UF"], axis=1)]
    fig.add_scatter(x=caps["pop_2010_comp"], y=caps["taxa_anual"], mode="markers+text",
                    text=caps["municipio"], textposition="top center", name="Capitais da persona",
                    marker=dict(size=16, color=OURO, symbol="star", line=dict(color=GRAFITE, width=1.5)))
    fig.update_layout(height=520)
    mostrar(fig)

    cols = ["UF", "municipio", "pop_2010_comp", "pop_2022", "variacao_pct", "taxa_anual"]
    nomes_cols = {"municipio": "Município", "pop_2010_comp": "Pop. 2010", "pop_2022": "Pop. 2022",
                  "variacao_pct": "Variação (%)", "taxa_anual": "Taxa a.a. (%)"}
    a, b = st.columns(2)
    with a:
        st.markdown("🚀 **Cresceram exageradamente** (top 10)")
        tabela(base.nlargest(10, "taxa_anual")[cols].rename(columns=nomes_cols).round(2))
    with b:
        st.markdown("📉 **Mais encolheram** (top 10)")
        tabela(base.nsmallest(10, "taxa_anual")[cols].rename(columns=nomes_cols).round(2))

    st.markdown("**Busque um município**")
    mun = st.selectbox("Município", sorted(base["municipio"] + " - " + base["UF"]))
    r = base[(base["municipio"] + " - " + base["UF"]) == mun].iloc[0]
    m1, m2, m3 = st.columns(3)
    m1.metric("População 2022", f"{r['pop_2022']:,}".replace(",", "."),
              f"{r['variacao_abs']:+,}".replace(",", "."))
    m2.metric("Variação 2010→2022", f"{r['variacao_pct']:.1f}%".replace(".", ","))
    m3.metric("Taxa anual", f"{r['taxa_anual']:.2f}% a.a.".replace(".", ","))

# ------------------------------------------------------------------ ABA 5 - NOTÍCIAS
with aba5:
    st.subheader("Transição demográfica, envelhecimento e expansão urbana")
    imgs = sorted(PASTA_IMG.glob("*.jp*g")) + sorted(PASTA_IMG.glob("*.png")) \
        if PASTA_IMG.exists() else []
    if imgs:
        cols_img = st.columns(min(3, len(imgs)))
        for c, img in zip(cols_img, imgs[:3]):
            c.image(str(img), caption=img.stem.replace("_", " "))
    noticias = [
        ("Censo 2022: número de pessoas com 65 anos ou mais cresceu 57,4% em 12 anos",
         "Agência de Notícias IBGE",
         "https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-denoticias/noticias/38186-",
         "Idosos passaram de 7,4% para 10,9% da população; no RS e no RJ já há mais "
         "pessoas de 60+ do que crianças de 0 a 14 anos."),
        ("Censo 2022: idade mediana da população brasileira é de 35 anos",
         "CNN Brasil",
         "https://www.cnnbrasil.com.br/nacional/censo-2022-idade-mediana-da-populacao-brasileira-e-de-35-anos/",
         "A idade mediana subiu de 29 para 35 anos entre 2010 e 2022."),
        ("Somos 203 milhões de pessoas no Brasil", "Revista Pesquisa FAPESP",
         "https://revistapesquisa.fapesp.br/somos-203-milhoes-de-pessoas-no-brasil/",
         "Crescimento médio de 0,52% ao ano é o menor desde o primeiro Censo, de 1872."),
        ("O futuro e a transição demográfica", "Congresso em Foco",
         "https://congressoemfoco.com.br/coluna/8025/o-futuro-e-a-transicao-demografica",
         "Envelhecimento rápido pressiona SUS e previdência."),
        ("O Brasil está mais idoso e as mulheres são maioria da população", "Extra Classe",
         "https://www.extraclasse.org.br/?p=98163",
         "Rio Grande do Sul tem a maior proporção de idosos do país."),
    ]
    for titulo, fonte, link, resumo in noticias:
        with st.container(border=True):
            st.markdown(f"**[{titulo}]({link})**  \n*{fonte}*  \n{resumo}")

st.markdown('<div class="cp-rodape">Desenvolvido por <b>CP Analytics</b> · Arthur Bernard · Júlio Souza · Moisés Caldeira · Pedro Henrique</div>', unsafe_allow_html=True)
st.caption("Fonte: IBGE, Censo Demográfico 2022: População e Domicílios, Primeiros Resultados "
           "(população 2010 compatibilizada com a malha de 2022); IBGE/SIDRA Tabela 9514. "
           "Taxa de crescimento geométrico: ((P2022/P2010)^(1/12) − 1) × 100.")
