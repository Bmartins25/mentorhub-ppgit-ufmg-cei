import csv
import io
import streamlit as st
from matching import MENTORES, MENTORADOS, score

st.set_page_config(page_title='MentorHub | PPGIT/UFMG/CEI', page_icon='🎓', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#f6f9fd;color:#182b45}
[data-testid="stSidebar"],[data-testid="stSidebar"]>div{background:#fff!important}
.block-container{max-width:1240px;padding-top:1.6rem;padding-bottom:3rem}
h1,h2,h3{color:#103b72!important;letter-spacing:-.025em}
p,label,[data-testid="stMarkdownContainer"]{color:#273b53}
[data-testid="stButton"] button[kind="primary"]{background:#1264d6;color:white;border-radius:9px;border:0;font-weight:700}
[data-testid="stButton"] button[kind="primary"] p{color:white!important}
[data-testid="stMetric"]{background:#eaf3ff;padding:16px;border-radius:12px;border:1px solid #d7e7fa}
[data-testid="stMetricValue"]{color:#075bb5}
[data-testid="stVerticalBlockBorderWrapper"]>div{border-color:#dae5f3!important;border-radius:14px}
[data-baseweb="select"]>div,[data-baseweb="input"]>div,textarea{background:white!important;color:#182b45!important}
.hero{background:linear-gradient(115deg,#103b72,#1264d6);color:#fff;padding:24px 28px;border-radius:17px;margin-bottom:20px}
.hero h1{color:white!important;margin:0;font-size:2rem}.hero p{color:#eaf3ff!important;margin:7px 0 0}
.eyebrow{font-size:.78rem;font-weight:800;letter-spacing:.11em;color:#1971bd}
.small-note{font-size:.85rem;color:#5a6d85}
</style>''',unsafe_allow_html=True)

with st.sidebar:
    st.markdown('### 🎓 MentorHub')
    st.caption('PPGIT / UFMG / CEI')
    st.divider()
    mode=st.radio('Motor de similaridade',['Textual leve','IA semântica (opcional)'],help='O motor leve não faz downloads de modelos.')
    only=st.checkbox('Somente mentores disponíveis',value=True)
    st.info('Pesos experimentais: competências 40% · similaridade 35% · área 15% · disponibilidade 10%.')
    st.caption('Resultados ilustrativos, não validados cientificamente. Todos os perfis são fictícios.')

st.markdown('<div class="hero"><div style="font-size:12px;font-weight:700;letter-spacing:2px">PROTÓTIPO ACADÊMICO · PPGIT/UFMG/CEI</div><h1>🎓 MentorHub — Matching Inteligente</h1><p>Encontre mentores compatíveis, compare resultados e entenda cada recomendação.</p></div>',unsafe_allow_html=True)

tab1,tab2,tab3=st.tabs(['🔎 Encontrar mentores','🧪 Laboratório de testes','ℹ️ Metodologia'])

def similarity_function():
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
        st.error('IA semântica indisponível: {}. Selecione Textual leve ou instale requirements-ia-opcional.txt.'.format(exc))
        st.stop()

def rank(profile,semantic=None,available_only=True):
    rows=[]
    for m in MENTORES:
        if available_only and not m['disponivel']:continue
        result=score(profile,m,semantic(profile,m) if semantic else None)
        rows.append((m,result))
    return sorted(rows,key=lambda x:x[1]['total'],reverse=True)

def export_csv(rows):
    stream=io.StringIO()
    writer=csv.writer(stream)
    writer.writerow(['mentor','area','pontuacao','competencias','similaridade','area_score','disponibilidade','justificativa'])
    for m,s in rows:writer.writerow([m['nome'],m['area'],s['total'],s['competencias'],s['semantica'],s['area'],s['disponibilidade'],s['justificativa']])
    return stream.getvalue().encode('utf-8-sig')

with tab1:
    st.subheader('1. Perfil do mentorado')
    choice=st.selectbox('Selecione um perfil de teste',[m['nome'] for m in MENTORADOS]+['Criar perfil personalizado'])
    if choice=='Criar perfil personalizado':
        left,right=st.columns(2)
        with left:
            name=st.text_input('Nome fictício','Meu perfil')
            area=st.selectbox('Área',['Dados e IA','Desenvolvimento de Software','Gestão e Produto','Outra'])
        with right:
            skills=st.text_input('Competências desejadas','Python, Machine Learning')
            goal=st.text_area('Objetivo da mentoria','Quero desenvolver competências em inteligência artificial.')
        profile={'nome':name,'area':area,'competencias':[x.strip() for x in skills.split(',') if x.strip()],'objetivo':goal}
    else:
        profile=next(m for m in MENTORADOS if m['nome']==choice)
        st.markdown('**Área:** {}  |  **Competências:** {}'.format(profile['area'],', '.join(profile['competencias'])))
        st.caption('Objetivo: '+profile['objetivo'])
    st.subheader('2. Recomendações')
    signature=(str(profile),mode,only)
    if st.button('🔎 Executar matching',type='primary',use_container_width=True):
        st.session_state['ranking']=rank(profile,similarity_function(),only)
        st.session_state['signature']=signature
    if 'ranking' in st.session_state and st.session_state.get('signature')==signature:
        rows=st.session_state['ranking']
        if rows:
            c1,c2,c3=st.columns(3)
            c1.metric('Mentores encontrados',len(rows))
            c2.metric('Melhor compatibilidade','{}%'.format(rows[0][1]['total']))
            c3.metric('Motor','Semântico' if mode!='Textual leve' else 'Textual')
            for pos,(m,s) in enumerate(rows,1):
                with st.container(border=True):
                    a,b=st.columns([4,1])
                    with a:
                        st.markdown('#### {}º · {}'.format(pos,m['nome']))
                        st.caption('{} · {}'.format(m['area'],'Disponível' if m['disponivel'] else 'Indisponível'))
                        st.write(m['bio'])
                        st.caption('Competências: '+', '.join(m['competencias']))
                    with b:st.metric('Compatibilidade','{}%'.format(s['total']))
                    st.progress(s['total']/100)
                    with st.expander('Por que este mentor foi recomendado?'):
                        st.write(s['justificativa'])
                        st.write('Competências: {}% | Similaridade: {}% | Área: {}% | Disponibilidade: {}%'.format(s['competencias'],s['semantica'],s['area'],s['disponibilidade']))
            st.download_button('⬇️ Exportar ranking CSV',export_csv(rows),'ranking_mentorhub.csv','text/csv')
        else:st.warning('Nenhum mentor atende aos filtros.')
    else:st.info('Execute o matching para visualizar recomendações atualizadas para este perfil.')

with tab2:
    st.subheader('Laboratório de testes')
    st.write('Compare os três perfis fictícios e verifique se as recomendações mudam de acordo com o objetivo da mentoria.')
    if st.button('🧪 Executar bateria de testes',use_container_width=True):
        semantic=similarity_function()
        reports=[]
        for p in MENTORADOS:
            rows=rank(p,semantic,only)
            if rows:
                m,s=rows[0]
                reports.append({'Perfil':p['nome'],'Mentor recomendado':m['nome'],'Compatibilidade (%)':s['total'],'Quantidade de candidatos':len(rows)})
        st.session_state['test_reports']=reports
        st.session_state['test_mode']=(mode,only)
    if st.session_state.get('test_mode')==(mode,only) and 'test_reports' in st.session_state:
        st.dataframe(st.session_state['test_reports'],use_container_width=True,hide_index=True)
        st.success('Bateria de testes executada. Compare os resultados e avalie a coerência das recomendações.')
    else:st.info('Clique no botão para executar os cenários de teste.')
    st.caption('Este é um teste funcional ilustrativo, não uma validação estatística da qualidade do algoritmo.')

with tab3:
    st.subheader('Como a pontuação é calculada')
    st.markdown('**Pontuação = 40% competências + 35% similaridade + 15% área + 10% disponibilidade.**')
    st.write('O modo textual usa sobreposição de palavras; o modo semântico usa embeddings multilíngues, quando instalado. O ranking é ordenado pela pontuação calculada.')
    st.warning('Os pesos e percentuais são hipóteses de prototipação. Compatibilidade não representa probabilidade de sucesso de uma mentoria.')
    st.markdown('**Próximas validações:** qualidade do ranking com avaliações humanas, vieses, critérios de elegibilidade, proteção de dados e testes com usuários.')

st.divider()
st.caption('MentorHub · PPGIT/UFMG/CEI · Demonstração independente, com dados fictícios. Sem integração com sistemas institucionais.')
