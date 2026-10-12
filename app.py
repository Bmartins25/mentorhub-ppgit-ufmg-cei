import csv
import io
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
    mode=st.radio('Similaridade',['Textual leve','IA semântica (opcional)'],help='O modo semântico requer dependências adicionais e download do modelo.')
    available_only=st.checkbox('Somente mentores disponíveis',value=True)
    st.info('Critérios experimentais: competências 40% · similaridade 35% · área 15% · disponibilidade 10%.')
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

def get_semantic():
    if mode=='Textual leve':return None
    try:
        from sentence_transformers import SentenceTransformer,util
        @st.cache_resource(show_spinner='Carregando modelo semântico...')
        def load():return SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        model=load()
        def semantic(a,b):
            emb=model.encode([a['objetivo']+' '+' '.join(a['competencias']),b['bio']+' '+' '.join(b['competencias'])],convert_to_tensor=True)
            return max(0.,min(1.,float(util.cos_sim(emb[0],emb[1]).item())))
        return semantic
    except Exception as exc:
        st.error('Motor semântico indisponível: {}. Use Textual leve ou instale as dependências opcionais.'.format(exc))
        st.stop()

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

find_tab,profiles_tab,lab_tab,method_tab=st.tabs(['🔎 Encontrar mentores','👥 Cadastrar perfis','🧪 Laboratório de testes','📘 Metodologia'])

with find_tab:
    st.subheader('Encontre seu mentor ideal')
    names=[m['nome'] for m in all_mentees]
    selected=st.selectbox('Perfil do mentorado',names)
    profile=next(m for m in all_mentees if m['nome']==selected)
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
            st.bar_chart({r['Perfil']:r['Pontuação (0–100)'] for r in reports},y_label='Pontuação')
            st.caption('Os valores são scores heurísticos. Não representam acurácia nem taxa de sucesso.')
        else:st.warning('Sem candidatos disponíveis para os cenários.')
    else:st.info('Clique em Executar bateria de testes para iniciar.')

with method_tab:
    st.subheader('Como funciona o motor de matching?')
    st.markdown('**Pontuação = 0,40 × competências + 0,35 × similaridade + 0,15 × área + 0,10 × disponibilidade.**')
    st.write('O modo textual compara termos dos objetivos e competências. O modo semântico utiliza embeddings multilíngues, caso o pacote opcional esteja instalado.')
    st.write('Os candidatos são ordenados pela pontuação calculada, e os componentes do score são exibidos para transparência.')
    st.warning('Pesos e métricas são experimentais. A pontuação não é uma probabilidade de êxito, nem foi validada com avaliações humanas.')
    st.markdown('**Áreas de concentração contempladas:**')
    for i, area in enumerate(AREAS_PPGIT, 1):
        st.write(f'{i}. {area}')
    st.markdown('**Próximas etapas:** avaliação com usuários, métricas de ranking, auditoria de vieses, critérios de elegibilidade e conformidade com a LGPD.')

st.divider()
st.markdown('<div class="team-footer"><strong>Equipe MentorHub</strong> · PPGIT/UFMG/CEI<br>Protótipo acadêmico demonstrativo independente · Dados fictícios · Sem integração com sistemas institucionais.</div>',unsafe_allow_html=True)
