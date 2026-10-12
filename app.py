import csv
import io
import html
import pandas as pd
import altair as alt
from urllib.parse import urlparse
import streamlit as st
from matching import MENTORES, MENTORADOS, AREAS_PPGIT, score

def valid_lattes(url):
    """Accept only HTTPS links to the official Lattes platform."""
    if not url.strip():
        return True
    parsed = urlparse(url.strip())
    return parsed.scheme == 'https' and parsed.hostname in {'lattes.cnpq.br', 'buscatextual.cnpq.br'} and bool(parsed.path.strip('/'))

st.set_page_config(page_title='MentorHub | PPGIT/UFMG/CEI', page_icon='🎓', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#f6f9fd;color:#20314a}
[data-testid="stSidebar"],[data-testid="stSidebar"]>div{background:#ffffff!important}
.block-container{max-width:1320px;padding-top:1.3rem;padding-bottom:3rem}
h1,h2,h3,h4{color:#123c70!important}p,label,[data-testid="stMarkdownContainer"]{color:#253b58}
[data-testid="stButton"] button[kind="primary"]{background:#1265d6!important;color:white!important;border:0;border-radius:10px;font-weight:700}
[data-testid="stButton"] button[kind="primary"] p{color:white!important}
[data-testid="stMetric"]{background:#fff;padding:16px;border-radius:14px;border:1px solid #dae5f2;box-shadow:0 2px 10px #1c4b780a}
[data-testid="stMetricValue"]{color:#1056a7}
[data-testid="stVerticalBlockBorderWrapper"]>div{border-color:#dae5f2!important;border-radius:15px}
[data-baseweb="select"]>div,[data-baseweb="input"]>div,textarea{background:white!important;color:#1d3454!important}
.hero{background:linear-gradient(110deg,#123c70,#1566d6);padding:27px 31px;border-radius:18px;margin-bottom:15px}
.hero h1{color:white!important;margin:3px 0;font-size:2.05rem}.hero p{color:#edf5ff!important;margin:6px 0 0}
.eyebrow{color:#dceeff!important;font-size:.78rem;font-weight:800;letter-spacing:.12em}
.small{color:#61748e;font-size:.9rem}.section-label{font-size:.82rem;font-weight:750;color:#1463ba;letter-spacing:.07em;text-transform:uppercase}

/* Dropdown, menu e controles: tema claro consistente */
[data-baseweb="popover"], [data-baseweb="popover"] > div, [data-baseweb="popover"] ul,
[data-baseweb="menu"], [role="listbox"], [role="option"],
[data-baseweb="select"] [role="listbox"], [data-baseweb="menu"] > div {background-color:#ffffff!important;color:#17365d!important;}
[data-baseweb="popover"] li, [data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"], [role="option"] span,
[data-baseweb="popover"] span {color:#17365d!important;}
[data-baseweb="menu"] [aria-selected="true"], [role="option"][aria-selected="true"] {background:#e8f2ff!important;}
[data-baseweb="menu"] [role="option"]:hover, [role="option"]:hover {background:#eef5ff!important;}
[data-baseweb="select"] input, [data-baseweb="select"] span {color:#17365d!important;}
/* Botões secundários e download */
[data-testid="stDownloadButton"] button, [data-testid="stButton"] button[kind="secondary"] {
 background:#eaf3ff!important;border:1px solid #b8d6fa!important;color:#1155a0!important;
 border-radius:10px!important;font-weight:650!important;
}
[data-testid="stDownloadButton"] button p, [data-testid="stButton"] button[kind="secondary"] p {color:#1155a0!important;}
[data-testid="stDownloadButton"] button:hover, [data-testid="stButton"] button[kind="secondary"]:hover {background:#d7eaff!important;}
[data-testid="stExpander"] {background:#fff!important;border-radius:10px;}
[data-testid="stExpander"] summary, [data-testid="stExpander"] p {color:#17365d!important;}
.team-footer {padding:15px 10px 8px;text-align:center;color:#58708d;font-size:.9rem;}
.team-footer strong{color:#155aaf;}

/* V8: corrigir componentes BaseWeb com estilos nativos escuros */
html, body, [data-testid="stApp"], .stApp {color-scheme:light!important;}
[data-testid="stHeader"], header[data-testid="stHeader"],
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stAppToolbar"], [data-testid="stStatusWidget"] {
  background-color:#f6f9fd!important;color:#17365d!important;
}
[data-testid="stHeader"] * {color:#17365d!important;}
/* Campo select: o div externo deve ser branco, não só os descendentes. */
.stApp [data-baseweb="select"],
.stApp [data-baseweb="select"] > div,
.stApp [data-baseweb="select"] > div > div,
.stApp [data-baseweb="select"] [role="combobox"],
.stApp [data-baseweb="select"] [aria-haspopup="listbox"],
.stApp [data-baseweb="input"],
.stApp [data-baseweb="input"] > div,
.stApp [data-baseweb="textarea"],
.stApp [data-baseweb="textarea"] > div {
  background-color:#ffffff!important;color:#17365d!important;
  border-color:#c7d9ed!important;
}
.stApp [data-baseweb="select"] *,
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea {
  color:#17365d!important;
  -webkit-text-fill-color:#17365d!important;
}
.stApp [data-baseweb="select"] svg {fill:#31618f!important;color:#31618f!important;}
/* Dropdown é renderizado em portal fora do corpo principal do Streamlit. */
body [data-baseweb="popover"], body [data-baseweb="popover"] > div,
body [data-baseweb="menu"], body [data-baseweb="menu"] > div,
body [role="listbox"], body [role="listbox"] > div,
body [role="option"], body [role="option"] > div,
body [data-baseweb="menu"] li {
  background:#ffffff!important;color:#17365d!important;
}
body [role="option"] *,body [role="listbox"] *,body [data-baseweb="menu"] * {
  color:#17365d!important;-webkit-text-fill-color:#17365d!important;
}
body [role="option"]:hover,body [role="option"][aria-selected="true"],
body [data-baseweb="menu"] li:hover {background:#e9f3ff!important;}
/* Expansor das áreas: fundo e textos legíveis mesmo aberto. */
[data-testid="stSidebar"] [data-testid="stExpander"],
[data-testid="stSidebar"] [data-testid="stExpander"] details,
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
  background:#ffffff!important;color:#17365d!important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary *,
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] * {
  color:#17365d!important;-webkit-text-fill-color:#17365d!important;
}
/* Todos os botões de download e secundários seguem a paleta clara. */
[data-testid="stDownloadButton"] button,
[data-testid="stBaseButton-secondary"],
[data-testid="stFormSubmitButton"] button:not([kind="primary"]) {
  background:#eaf3ff!important;color:#1155a0!important;border:1px solid #b8d6fa!important;
}
[data-testid="stDownloadButton"] button *,[data-testid="stBaseButton-secondary"] * {
  color:#1155a0!important;-webkit-text-fill-color:#1155a0!important;
}

/* V10: dropdown com paleta clara e área oficial visível. */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [role="combobox"] {
  background-color:#ffffff!important;color:#17365d!important;border-color:#b8d6fa!important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] * {
  color:#17365d!important;-webkit-text-fill-color:#17365d!important;
}
body [data-baseweb="popover"] [role="listbox"],
body [data-baseweb="popover"] [role="option"] {
  background-color:#ffffff!important;color:#17365d!important;
}

/* Indicador de carregamento claro, acessível e alinhado à marca */
[data-testid="stSpinner"], [data-testid="stStatusWidget"] {background:#eaf3ff!important;color:#17365d!important;border:1px solid #b8d6fa!important;border-radius:12px!important;padding:10px 14px!important;}
[data-testid="stSpinner"] *,[data-testid="stStatusWidget"] * {color:#17365d!important;}

/* V5: tabela comparativa independente do tema do navegador e do Streamlit */
.mentor-table-scroll{overflow-x:auto;width:100%;background:#fff;border:1px solid #d9e5f2;border-radius:12px;box-shadow:0 2px 12px rgba(17,59,107,.06)}
.mentor-table{border-collapse:collapse;width:100%;min-width:1050px;background:#fff;color:#193758;font-size:.98rem}
.mentor-table thead th{background:#e8f2ff!important;color:#123c70!important;font-weight:750;text-align:left;padding:15px 13px;border-bottom:2px solid #b7d3f2;white-space:nowrap}
.mentor-table tbody td{background:#fff!important;color:#193758!important;padding:14px 13px;border-bottom:1px solid #e6edf6;vertical-align:middle}
.mentor-table tbody tr:nth-child(even) td{background:#f5f9ff!important}
.mentor-table tbody tr:hover td{background:#eaf3ff!important}
.mentor-table td:first-child{font-weight:700;white-space:nowrap}
.mentor-table td:nth-child(n+3){font-variant-numeric:tabular-nums}
.mentor-table .rank-up{color:#167347!important;font-weight:800;white-space:nowrap}
.mentor-table .rank-down{color:#c33e47!important;font-weight:800;white-space:nowrap}
@media(max-width:700px){.mentor-table{font-size:.88rem}.mentor-table td,.mentor-table th{padding:9px!important}}

/* V7 — superfícies claras em todos os campos e tabelas de laboratório */
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stTextArea"] [data-baseweb="textarea"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div {
  background:#ffffff!important;color:#17365d!important;-webkit-text-fill-color:#17365d!important;
}
[data-testid="stDataFrame"], [data-testid="stDataFrame"] > div,
[data-testid="stVegaLiteChart"], [data-testid="stVegaLiteChart"] > div,
[data-testid="stArrowVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] > div {
 background:#ffffff!important;color:#17365d!important;border-radius:12px;
}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{color:#7a8ca4!important;-webkit-text-fill-color:#7a8ca4!important}
</style>''',unsafe_allow_html=True)

if 'custom_mentors' not in st.session_state: st.session_state.custom_mentors=[]
if 'custom_mentees' not in st.session_state: st.session_state.custom_mentees=[]

with st.sidebar:
    st.markdown('## 🎓 MentorHub')
    st.caption('PPGIT / UFMG / CEI')
    with st.expander('Áreas de concentração do PPGIT'):
        for n, area in enumerate(AREAS_PPGIT, 1):
            st.caption(f'{n}. {area}')
    st.divider()
    st.markdown('**Configuração do motor**')
    mode=st.radio('Como deseja encontrar seu mentor?', ['Textual leve','IA semântica (embeddings)'], help='Escolha como o sistema compara as descrições dos perfis.')
    if mode=='Textual leve':
        st.info('🔎 **Busca por palavras**\n\nCompara termos presentes nos perfis. Exemplo: quem procura Python tende a encontrar mentores que também mencionam Python.')
    else:
        st.info('🧠 **Busca inteligente com IA**\n\nCompara o significado dos textos, mesmo com palavras diferentes. Exemplo: “prever riscos clínicos” pode estar relacionado a “análise preditiva”.')
    st.caption('Os dois modos também consideram competências, área e disponibilidade. O score é experimental.')
    available_only=st.checkbox('Somente mentores disponíveis',value=True)
    st.info('Pesos — Textual: competências 40%, contexto 35%, área 15%, disponibilidade 10%. IA semântica: competências 30%, contexto 50%, área 10%, disponibilidade 10%.')
    st.caption('Dados fictícios e perfis inseridos nesta sessão. Pontuações não validadas cientificamente.')
    st.divider()
    st.caption('Protótipo acadêmico independente • PPGIT/UFMG/CEI')

st.markdown('<div class="hero"><div class="eyebrow">PROTÓTIPO ACADÊMICO · PPGIT/UFMG/CEI</div><h1>🎓 MentorHub — Matching Inteligente</h1><p>Conectando objetivos, competências e experiências com recomendações explicáveis.</p></div>',unsafe_allow_html=True)
all_mentors=MENTORES+st.session_state.custom_mentors
all_mentees=MENTORADOS+st.session_state.custom_mentees
c1,c2,c3,c4=st.columns(4)
c1.metric('Mentores cadastrados',len(all_mentors))
c2.metric('Mentorados cadastrados',len(all_mentees))
c3.metric('Mentores disponíveis',sum(m['disponivel'] for m in all_mentors))
c4.metric('Áreas de concentração',len(AREAS_PPGIT))
st.caption('Motor selecionado: ' + ('IA semântica' if mode.startswith('IA') else 'Textual leve'))

@st.cache_resource(show_spinner=False)
def load_semantic_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', device='cpu')

@st.cache_data(show_spinner=False, max_entries=3000)
def semantic_embedding(text):
    model=load_semantic_model()
    return model.encode(text, normalize_embeddings=True, convert_to_numpy=True).tolist()

def get_semantic():
    if mode=='Textual leve':
        return None
    try:
        with st.spinner('Preparando o modelo de IA semântica...'):
            model=load_semantic_model()
    except Exception as exc:
        st.error('Não foi possível iniciar a IA semântica. Confira a instalação de sentence-transformers e a versão do Python nos logs do Streamlit.')
        st.caption(f'Detalhe técnico: {type(exc).__name__}: {exc}')
        st.stop()
    def sim(left,right):
        v1=semantic_embedding(left.strip() or 'sem informação')
        v2=semantic_embedding(right.strip() or 'sem informação')
        return max(0.0,min(1.0,sum(x*y for x,y in zip(v1,v2))))
    def semantic(a,b):
        objective=a['objetivo']
        bio=b['bio']
        skills_a='; '.join(a['competencias'])
        skills_b='; '.join(b['competencias'])
        return (sim(objective,bio),sim(skills_a,skills_b),sim(objective+'; '+skills_a,bio+'; '+skills_b))
    return semantic

def rank(profile,semantic=None):
    rows=[]
    for mentor in all_mentors:
        if available_only and not mentor['disponivel']:continue
        result=score(profile,mentor,semantic(profile,mentor) if semantic else None)
        rows.append((mentor,result))
    return sorted(rows,key=lambda x:x[1]['total'],reverse=True)

def csv_bytes(rows):
    out=io.StringIO(); w=csv.writer(out)
    w.writerow(['mentor','area','lattes','pontuacao','competencias','similaridade','area_score','disponibilidade','justificativa'])
    for m,s in rows:w.writerow([m['nome'],m['area'],m.get('lattes',''),s['total'],s['competencias'],s['semantica'],s['area'],s['disponibilidade'],s['justificativa']])
    return out.getvalue().encode('utf-8-sig')

find_tab,profiles_tab,lab_tab,compare_tab,method_tab=st.tabs(['🔎 Encontrar mentores','👥 Cadastrar perfis','🧪 Laboratório de testes','⚖️ Comparar motores','📘 Metodologia'])

with find_tab:
    st.subheader('Encontre seu mentor ideal')
    # Cada área aparece uma única vez. Os perfis são selecionados separadamente.
    areas_disponiveis=[a for a in AREAS_PPGIT if any(p['area']==a for p in all_mentees)]
    areas_disponiveis += sorted({p['area'] for p in all_mentees} - set(areas_disponiveis))
    area_escolhida=st.selectbox('Área de concentração do PPGIT', areas_disponiveis, key='area_mentorado_v11')
    perfis_da_area=[p for p in all_mentees if p['area']==area_escolhida]
    if len(perfis_da_area)>1:
        indice_perfil=st.selectbox('Perfil do mentorado', range(len(perfis_da_area)),
                                  format_func=lambda i: perfis_da_area[i]['nome'], key='perfil_mentorado_v11')
        profile=perfis_da_area[indice_perfil]
    else:
        profile=perfis_da_area[0]
        st.caption('Perfil do mentorado: '+profile['nome'])
    with st.container(border=True):
        left,right=st.columns([2,1])
        with left:
            st.markdown('**Objetivo da mentoria**')
            st.write(profile['objetivo'])
        with right:
            st.markdown('**Área de interesse**')
            st.write(profile['area'])
            st.caption('Competências: '+', '.join(profile['competencias']))
    signature=(repr(profile),mode,available_only,repr(all_mentors))
    if st.button('🔎 Encontrar mentores compatíveis',type='primary',use_container_width=True):
        st.session_state.ranking=rank(profile,get_semantic())
        st.session_state.ranking_signature=signature
    if st.session_state.get('ranking_signature')==signature:
        rows=st.session_state.ranking
        if rows:
            st.markdown('### Ranking de compatibilidade')
            st.caption('Pontuação heurística ilustrativa, não probabilidade de sucesso.')
            for i,(mentor,result) in enumerate(rows,1):
                with st.container(border=True):
                    left,right=st.columns([4,1])
                    with left:
                        st.markdown('#### {}º · {}'.format(i,mentor['nome']))
                        st.caption('{} · {}'.format(mentor['area'],'Disponível' if mentor['disponivel'] else 'Indisponível'))
                        st.write(mentor['bio'])
                        st.caption('Competências: '+', '.join(mentor['competencias']))
                        lattes_url = mentor.get('lattes', '').strip()
                        if lattes_url:
                            st.link_button('📚 Currículo Lattes', lattes_url, help='Abrir currículo Lattes em nova aba')
                        else:
                            st.caption('Currículo Lattes: não informado (perfil fictício)')
                    with right:st.metric('Compatibilidade','{:.1f}/100'.format(result['total']))
                    st.progress(max(0.,min(1.,result['total']/100)))
                    with st.expander('Entenda esta recomendação'):
                        st.write(result['justificativa'])
                        a,b,c,d=st.columns(4)
                        a.metric('Competências','{}%'.format(result['competencias']))
                        b.metric('Similaridade','{}%'.format(result['semantica']))
                        c.metric('Área','{}%'.format(result['area']))
                        d.metric('Disponibilidade','{}%'.format(result['disponibilidade']))
            st.download_button('⬇️ Exportar ranking (CSV)',csv_bytes(rows),'mentorhub_ranking.csv','text/csv')
        else:st.warning('Nenhum mentor encontrado com os filtros atuais.')
    else:st.info('Selecione um perfil e execute o matching para visualizar as recomendações.')

with profiles_tab:
    st.subheader('Cadastrar perfis para simulação')
    st.caption('Os perfis ficam somente na memória da sessão e não são salvos em banco de dados. Use dados fictícios.')
    ptab,mtab=st.tabs(['Novo mentorado','Novo mentor'])
    areas=AREAS_PPGIT
    with ptab:
        with st.form('form_mentorado',clear_on_submit=True):
            a,b=st.columns(2)
            name=a.text_input('Nome fictício do mentorado')
            area=b.selectbox('Área desejada',areas)
            skills=st.text_input('Competências desejadas (separadas por vírgula)','Python, Machine Learning')
            goal=st.text_area('Objetivo da mentoria')
            submit=st.form_submit_button('Adicionar mentorado',type='primary')
            if submit:
                if not name.strip() or not goal.strip() or not skills.strip():st.error('Preencha nome, competências e objetivo.')
                elif any(p['nome'].casefold()==name.strip().casefold() for p in all_mentees):st.warning('Já existe um perfil com esse nome.')
                else:
                    st.session_state.custom_mentees.append({'nome':name.strip(),'area':area,'competencias':[s.strip() for s in skills.split(',') if s.strip()],'objetivo':goal.strip()})
                    st.success('Mentorado adicionado à sessão. Acesse Encontrar mentores para testar.')
    with mtab:
        with st.form('form_mentor',clear_on_submit=True):
            a,b=st.columns(2)
            name=a.text_input('Nome fictício do mentor')
            area=b.selectbox('Área de atuação',areas)
            skills=st.text_input('Competências oferecidas (separadas por vírgula)','Python, SQL')
            bio=st.text_area('Experiência e descrição profissional')
            lattes=st.text_input('Currículo Lattes (URL HTTPS, opcional)',placeholder='https://lattes.cnpq.br/0000000000000000',help='Use apenas links oficiais do CNPq. Para perfis fictícios, deixe vazio.')
            available=st.checkbox('Disponível para mentoria',value=True)
            submit=st.form_submit_button('Adicionar mentor',type='primary')
            if submit:
                if not name.strip() or not bio.strip() or not skills.strip():st.error('Preencha nome, competências e experiência.')
                elif not valid_lattes(lattes):st.error('Informe um endereço HTTPS válido do Currículo Lattes (lattes.cnpq.br) ou deixe o campo vazio.')
                elif any(p['nome'].casefold()==name.strip().casefold() for p in all_mentors):st.warning('Já existe um mentor com esse nome.')
                else:
                    st.session_state.custom_mentors.append({'nome':name.strip(),'area':area,'competencias':[s.strip() for s in skills.split(',') if s.strip()],'bio':bio.strip(),'disponivel':available,'lattes':lattes.strip()})
                    st.success('Mentor adicionado à sessão. Ele participará do próximo ranking.')
    if st.session_state.custom_mentors or st.session_state.custom_mentees:
        st.divider()
        if st.button('Limpar perfis adicionados nesta sessão'):
            st.session_state.custom_mentors=[];st.session_state.custom_mentees=[]
            st.session_state.pop('ranking_signature',None)
            st.rerun()

with lab_tab:
    st.subheader('Laboratório de testes do matching')
    st.write('Execute cenários distintos e compare a coerência dos primeiros colocados.')
    if st.button('🧪 Executar bateria de testes',type='primary',use_container_width=True):
        sem=get_semantic(); reports=[]
        for p in all_mentees:
            rows=rank(p,sem)
            if rows:
                m,s=rows[0]
                reports.append({'Perfil':p['nome'],'Mentor recomendado':m['nome'],'Pontuação (0–100)':s['total'],'Candidatos':len(rows)})
        st.session_state.test_reports=reports
        st.session_state.test_signature=(mode,available_only,repr(all_mentees),repr(all_mentors))
    if st.session_state.get('test_signature')==(mode,available_only,repr(all_mentees),repr(all_mentors)):
        reports=st.session_state.test_reports
        if reports:
            st.dataframe(reports,use_container_width=True,hide_index=True)
            chart_df=pd.DataFrame(reports)
            chart=alt.Chart(chart_df).mark_bar(color='#2474d2',cornerRadiusTopLeft=4,cornerRadiusTopRight=4).encode(
                x=alt.X('Perfil:N',sort=None,title='Perfil de mentorado',axis=alt.Axis(labelAngle=-25,labelLimit=200)),
                y=alt.Y('Pontuação (0–100):Q',scale=alt.Scale(domain=[0,100]),title='Pontuação (0–100)'),
                tooltip=['Perfil:N','Mentor recomendado:N',alt.Tooltip('Pontuação (0–100):Q',format='.1f')]
            ).properties(height=330,background='white').configure_view(stroke=None).configure_axis(labelColor='#24466a',titleColor='#24466a',gridColor='#e4edf7').configure_legend(labelColor='#24466a',titleColor='#24466a')
            st.altair_chart(chart,use_container_width=True)
            st.caption('Os valores são scores heurísticos. Não representam acurácia nem taxa de sucesso.')
        else:st.warning('Sem candidatos disponíveis para os cenários.')
    else:st.info('Clique em Executar bateria de testes para iniciar.')


with compare_tab:
    st.subheader('Comparação controlada: Textual Leve × IA Semântica')
    st.write('Os dois motores usam o mesmo mentorado e o mesmo conjunto de candidatos. Scores não são probabilidades e não devem ser interpretados como equivalentes.')
    chosen=st.selectbox('Perfil para comparação',range(len(all_mentees)),format_func=lambda i: f"{all_mentees[i]['nome']} — {all_mentees[i]['area']}",key='compare_profile')
    profile=all_mentees[chosen]
    st.caption(f"Objetivo: {profile['objetivo']}")
    st.caption('Competências: '+', '.join(profile['competencias']))
    if st.button('⚖️ Executar comparação com os mesmos dados',type='primary',use_container_width=True):
        semantic_fn=get_semantic() if mode.startswith('IA') else None
        # A comparação sempre carrega o motor semântico, independentemente da escolha lateral.
        if semantic_fn is None:
            try:
                with st.spinner('Preparando o modelo de IA semântica...'):
                    load_semantic_model()
                def sim(a,b):
                    x=semantic_embedding(a.strip() or 'sem informação'); y=semantic_embedding(b.strip() or 'sem informação')
                    return max(0.,min(1.,sum(v*w for v,w in zip(x,y))))
                def semantic_fn(a,b):
                    sa='; '.join(a['competencias']); sb='; '.join(b['competencias'])
                    return (sim(a['objetivo'],b['bio']),sim(sa,sb),sim(a['objetivo']+'; '+sa,b['bio']+'; '+sb))
            except Exception as exc:
                st.error(f'Não foi possível carregar o modelo semântico: {type(exc).__name__}: {exc}')
                st.stop()
        mentors=[m for m in all_mentors if m['disponivel'] or not available_only]
        textual=sorted([(m,score(profile,m)) for m in mentors],key=lambda t:t[1]['total'],reverse=True)
        semantic=sorted([(m,score(profile,m,semantic_fn(profile,m))) for m in mentors],key=lambda t:t[1]['total'],reverse=True)
        t_index={m['nome']:(i+1,s) for i,(m,s) in enumerate(textual)}
        s_index={m['nome']:(i+1,s) for i,(m,s) in enumerate(semantic)}
        rows=[]
        for m,_ in textual:
            rt,t=t_index[m['nome']]; rs,a=s_index[m['nome']]
            rows.append({'Mentor':m['nome'],'Área do mentor':m['area'],'Posição textual':rt,'Score textual':t['total'],'Posição semântica':rs,'Score semântico':a['total'],'Mudança de posição':rt-rs,'Similaridade lexical (%)':t['semantica'],'Similaridade semântica (%)':a['semantica'],'Competências textual (%)':t['competencias'],'Competências semântica (%)':a['competencias'],'Área (%)':a['area'],'Disponibilidade (%)':a['disponibilidade'],'Justificativa textual':t['justificativa'],'Justificativa semântica':a['justificativa']})
        st.session_state.comparison={'signature':(chosen,available_only,repr(all_mentors),repr(all_mentees)),'rows':rows,'profile':dict(profile)}
    comparison=st.session_state.get('comparison')
    if comparison and comparison['signature']==(chosen,available_only,repr(all_mentors),repr(all_mentees)):
        rows=comparison['rows']
        if rows:
            st.markdown('#### Ranking comparativo dos mentores')
            # Tabela HTML própria: evita o tema escuro do grid nativo do Streamlit.
            visible_cols=['Mentor','Área do mentor','Posição textual','Score textual','Posição semântica','Score semântico','Mudança de posição','Similaridade semântica (%)']
            def table_cell(value, column):
                if column in ('Score textual','Score semântico','Similaridade semântica (%)'):
                    return f'{float(value):.1f}' + ('%' if column.startswith('Similaridade') else '')
                if column=='Mudança de posição':
                    value=int(value)
                    if value>0:return f'<span class="rank-up">↑ +{value}</span>'
                    if value<0:return f'<span class="rank-down">↓ −{abs(value)}</span>'
                return html.escape(str(value))
            head=''.join(f'<th>{html.escape(c)}</th>' for c in visible_cols)
            body=''.join('<tr>'+''.join(f'<td>{table_cell(r[c],c)}</td>' for c in visible_cols)+'</tr>' for r in rows)
            st.markdown(f'<div class="mentor-table-scroll"><table class="mentor-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>',unsafe_allow_html=True)
            st.caption('Mudança de posição positiva: o mentor subiu no ranking semântico. As pontuações usam pesos diferentes; a diferença entre scores não mede ganho de qualidade.')
            st.markdown('#### Comparação de scores por mentor')
            st.caption('Barras agrupadas: cada mentor tem uma barra por algoritmo. Os valores são scores heurísticos, não probabilidades.')
            chart_df=pd.DataFrame([
                {'Mentor':r['Mentor'],'Motor':'Textual Leve','Score':r['Score textual']} for r in rows
            ]+[
                {'Mentor':r['Mentor'],'Motor':'IA Semântica','Score':r['Score semântico']} for r in rows
            ])
            mentor_order=[r['Mentor'] for r in rows]
            chart=alt.Chart(chart_df,background='#ffffff').mark_bar(cornerRadiusTopLeft=3,cornerRadiusTopRight=3).encode(
                x=alt.X('Mentor:N',sort=mentor_order,title=None,axis=alt.Axis(labelAngle=-25,labelColor='#203b5e',titleColor='#203b5e')),
                xOffset=alt.XOffset('Motor:N',sort=['Textual Leve','IA Semântica']),
                y=alt.Y('Score:Q',scale=alt.Scale(domain=[0,100]),title='Pontuação (0–100)',axis=alt.Axis(labelColor='#203b5e',titleColor='#203b5e',gridColor='#e3ebf5')),
                color=alt.Color('Motor:N',scale=alt.Scale(domain=['Textual Leve','IA Semântica'],range=['#8ab6e8','#1265d6']),legend=alt.Legend(orient='top',title=None,labelColor='#203b5e')),
                tooltip=[alt.Tooltip('Mentor:N'),alt.Tooltip('Motor:N'),alt.Tooltip('Score:Q',format='.1f')]
            ).properties(height=350,padding={'left':10,'top':15,'right':15,'bottom':5}).configure_view(stroke=None).configure(background='#ffffff')
            st.altair_chart(chart,use_container_width=True,theme=None)

            out=io.StringIO(); writer=csv.writer(out)
            writer.writerow(['perfil_mentorado','area_mentorado','objetivo_mentoria','competencias_mentorado','modelo_embeddings','versao_algoritmo']+list(rows[0].keys()))
            for r in rows:
                writer.writerow([profile['nome'],profile['area'],profile['objetivo'],'; '.join(profile['competencias']),'paraphrase-multilingual-MiniLM-L12-v2','v6-conclusao-explicativa']+list(r.values()))
            st.download_button('⬇️ Exportar comparação (CSV)',out.getvalue().encode('utf-8-sig'),'mentorhub_comparacao_motores.csv','text/csv')
            st.markdown('#### Conclusão da comparação')
            top_t=min(rows,key=lambda r:r['Posição textual'])
            top_s=min(rows,key=lambda r:r['Posição semântica'])
            climbed=sorted((r for r in rows if r['Mudança de posição']>0),key=lambda r:r['Mudança de posição'],reverse=True)
            fell=sorted((r for r in rows if r['Mudança de posição']<0),key=lambda r:r['Mudança de posição'])
            st.markdown('<div class="comparison-summary">',unsafe_allow_html=True)
            if top_t['Mentor']==top_s['Mentor']:
                st.success(f"**Concordância no primeiro lugar:** os dois motores recomendaram **{top_t['Mentor']}** como primeira opção para o perfil selecionado.")
            else:
                st.info(f"**Recomendações principais diferentes:** o Textual Leve indicou **{top_t['Mentor']}** e a IA Semântica indicou **{top_s['Mentor']}** em primeiro lugar.")
            if climbed:
                up=climbed[0]
                st.write(f"**Maior subida no ranking semântico:** {up['Mentor']} passou da posição {up['Posição textual']} para {up['Posição semântica']} (↑ {up['Mudança de posição']} posições). Isso sugere que o modelo identificou relações de significado além da correspondência literal de palavras.")
            if fell:
                down=fell[0]
                st.write(f"**Maior queda no ranking semântico:** {down['Mentor']} passou da posição {down['Posição textual']} para {down['Posição semântica']} (↓ {abs(down['Mudança de posição'])} posições).")
            st.write('**Como interpretar:** o Textual Leve prioriza termos coincidentes; a IA Semântica utiliza embeddings para reconhecer proximidade de significado. Pontuações dos dois motores têm pesos distintos e **não são probabilidades nem devem ser comparadas como medidas equivalentes de qualidade**.')
            st.caption('Esta análise descreve os resultados deste perfil demonstrativo. Para afirmar que um motor recomenda melhor, é necessário avaliar a relevância dos mentores com especialistas e métricas como Precision@K ou NDCG@K.')
            st.markdown('</div>',unsafe_allow_html=True)
            st.info('Validação de qualidade requer avaliações humanas de relevância. Diferenças de ranking, isoladamente, não comprovam superioridade do motor semântico.')
        else: st.warning('Nenhum mentor atende ao filtro de disponibilidade.')
    else:
        st.info('Selecione o perfil e execute a comparação. A primeira execução pode demorar enquanto o modelo é carregado.')

with method_tab:
    st.subheader('Metodologia do MentorHub')
    st.write('Esta seção explica como os perfis são comparados, o que significa cada pontuação e quais são os limites dos resultados. O protótipo utiliza dados demonstrativos e pesos experimentais.')
    st.info('**Em resumo:** o Textual Leve procura correspondências de palavras. A IA Semântica compara também a proximidade de significado. Ambos produzem recomendações exploratórias, não decisões automáticas.')

    st.markdown('### 1. Etapas da recomendação')
    st.markdown('**Perfil do mentorado → perfis de mentores → cálculo dos critérios → ranking → justificativas e comparação.**')
    st.write('O perfil inclui área de interesse, competências desejadas e objetivo da mentoria. Cada mentor apresenta área de atuação, competências, experiência e disponibilidade. A classificação considera as informações disponíveis no momento do teste.')

    st.markdown('### 2. Diferenças entre os motores')
    col_texto, col_ia = st.columns(2)
    with col_texto:
        with st.container(border=True):
            st.markdown('#### 🔎 Textual Leve')
            st.write('Compara palavras e expressões dos perfis. Identifica correspondências literais, mas pode deixar de reconhecer termos equivalentes.')
            st.caption('Exemplo: “Python” no objetivo e “Python” nas competências do mentor.')
    with col_ia:
        with st.container(border=True):
            st.markdown('#### 🧠 IA Semântica')
            st.write('Utiliza embeddings multilíngues para representar textos numericamente e estimar proximidade de significado, inclusive entre expressões diferentes.')
            st.caption('Exemplo: “prever riscos clínicos” e “modelagem preditiva em saúde”.')

    st.markdown('### 3. Como a pontuação é calculada')
    pesos=pd.DataFrame([
        {'Critério':'Competências','Textual Leve':40,'IA Semântica':30},
        {'Critério':'Similaridade textual / contexto semântico','Textual Leve':35,'IA Semântica':50},
        {'Critério':'Área de concentração','Textual Leve':15,'IA Semântica':10},
        {'Critério':'Disponibilidade','Textual Leve':10,'IA Semântica':10},
    ])
    st.dataframe(pesos,hide_index=True,use_container_width=True,column_config={
        'Textual Leve':st.column_config.NumberColumn('Textual Leve (%)',format='%d%%'),
        'IA Semântica':st.column_config.NumberColumn('IA Semântica (%)',format='%d%%')})
    st.caption('Pesos heurísticos do protótipo, não calibrados empiricamente. A IA semântica combina comparações entre objetivo e biografia, competências e perfis completos.')

    st.markdown('### 4. Como interpretar os resultados')
    with st.expander('Pontuação, similaridade e mudança de posição',expanded=True):
        st.write('**Pontuação (0–100):** índice heurístico de ordenação dentro de cada motor. Não é probabilidade de sucesso.')
        st.write('**Similaridade:** medida calculada pelo algoritmo; não equivale automaticamente à qualidade de uma mentoria.')
        st.write('**Mudança de posição:** indica subida ou queda no ranking semântico em relação ao textual. A diferença entre os scores não mede ganho de qualidade.')
        st.write('**Disponibilidade:** critério operacional que não substitui a avaliação da aderência acadêmica.')
    with st.expander('Por que os motores podem recomendar mentores diferentes?'):
        st.write('Uma expressão pode ter pouca coincidência literal com outra, mas proximidade de significado. Por isso, os rankings podem mudar. A relevância da recomendação ainda deve ser julgada por pessoas que conheçam a área de pesquisa.')

    st.markdown('### 5. Limitações e validação científica')
    st.warning('O MentorHub é um protótipo acadêmico. Os scores não são probabilidades, e não há evidência suficiente para afirmar superioridade de um motor sem avaliação humana independente.')
    st.write('A validação futura deve incluir julgamentos de relevância por especialistas, cenários reproduzíveis, métricas como Precision@K e NDCG@K, análise de vieses e verificação dos critérios de elegibilidade.')
    st.write('O motor semântico depende do carregamento do modelo multilíngue no servidor. Caso ele não esteja disponível, o modo textual pode ser usado separadamente.')

    with st.expander('Áreas de concentração contempladas'):
        for i, area in enumerate(AREAS_PPGIT, 1):
            st.write(f'{i}. {area}')
    with st.expander('Privacidade e escopo do protótipo'):
        st.write('Os perfis criados nesta demonstração ficam na memória da sessão, sem persistência em banco de dados. Utilize dados fictícios. A plataforma não está integrada a sistemas institucionais e exige avaliação de conformidade com a LGPD antes de uso com dados pessoais reais.')

st.divider()
st.markdown('<div class="team-footer"><strong>Equipe MentorHub</strong> · PPGIT/UFMG/CEI<br>Protótipo acadêmico demonstrativo independente · Dados fictícios · Sem integração com sistemas institucionais.</div>',unsafe_allow_html=True)
