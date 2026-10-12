import math, re, unicodedata
from collections import Counter
STOP={'de','da','do','dos','das','em','e','a','o','para','com','um','uma','na','no','por','que','the','and','of'}
def tokens(text):
    s=unicodedata.normalize('NFKD',str(text).lower()); s=''.join(c for c in s if not unicodedata.combining(c))
    return [x for x in re.findall(r'[a-z0-9]+',s) if x not in STOP and len(x)>1]
def cosine(a,b):
    a,b=Counter(tokens(a)),Counter(tokens(b)); dot=sum(v*b.get(k,0) for k,v in a.items()); den=math.sqrt(sum(v*v for v in a.values())*sum(v*v for v in b.values()))
    return dot/den if den else 0.
def normset(items): return set(tokens(' '.join(items)))
def score(mentorado,mentor,semantic=None):
    wants=normset(mentorado['competencias']); offers=normset(mentor['competencias'])
    lexical_skill=len(wants & offers)/len(wants) if wants else 0
    lexical_context=cosine(mentorado['objetivo']+' '+' '.join(mentorado['competencias']),mentor['bio']+' '+' '.join(mentor['competencias']))
    area=float(mentorado['area']==mentor['area'])
    available=float(bool(mentor['disponivel']))
    if semantic is None:
        similarity=lexical_context
        skill=lexical_skill
        weights=(.40,.35,.15,.10)
        method='Textual leve'
    else:
        # semantic: contexto (objetivo/bio), competências (listas), perfil integral
        context,semantic_skills,full=semantic
        similarity=max(0.,min(1., .65*context+.35*full))
        skill=max(0.,min(1., .80*semantic_skills+.20*lexical_skill))
        weights=(.30,.50,.10,.10)
        method='IA semântica'
    total=round(100*sum(w*x for w,x in zip(weights,(skill,similarity,area,available))),1)
    common=sorted(wants & offers)
    reasons=[]
    if common: reasons.append('Termos de competências coincidentes: '+', '.join(common[:6]))
    if area: reasons.append('Mesma área de interesse')
    if not mentor['disponivel']: reasons.append('Mentor indisponível no momento')
    reasons.append(('Afinidade semântica por embeddings' if semantic is not None else 'Afinidade lexical')+': {:.0f}%'.format(similarity*100))
    if semantic is not None: reasons.append('Competências comparadas também por significado: {:.0f}%'.format(skill*100))
    return {'total':total,'competencias':round(skill*100,1),'semantica':round(similarity*100,1),'area':round(area*100),'disponibilidade':round(available*100),'justificativa':'; '.join(reasons),'metodo':method}
AREAS_PPGIT = [
    'Biotecnologia e Inovação Biofarmacêutica',
    'Gestão da Inovação, Propriedade Intelectual e Empreendedorismo',
    'Novos Materiais, Nanotecnologia e Química',
    'Transformação Digital e Inteligência Artificial',
    'Sustentabilidade',
]
MENTORES = [
 {'nome':'Ana Costa','area':AREAS_PPGIT[3],'competencias':['Python','Machine Learning','SQL','Power BI'],'bio':'Cientista de dados, orienta projetos de machine learning, análise de dados e carreira em inteligência artificial.','disponivel':True,'lattes':''},
 {'nome':'Carlos Lima','area':AREAS_PPGIT[3],'competencias':['Python','APIs','Docker','Git'],'bio':'Engenheiro de software com experiência em backend, arquitetura de APIs e implantação de aplicações.','disponivel':True,'lattes':''},
 {'nome':'Mariana Rocha','area':AREAS_PPGIT[3],'competencias':['Python','NLP','Machine Learning','Ética em IA'],'bio':'Pesquisadora em processamento de linguagem natural, inteligência artificial responsável e modelos de linguagem.','disponivel':True,'lattes':''},
 {'nome':'João Pereira','area':AREAS_PPGIT[1],'competencias':['Scrum','Produto','Liderança','Gestão de projetos','Empreendedorismo'],'bio':'Mentor de inovação, empreendedorismo, gestão de produtos digitais e liderança de equipes.','disponivel':True,'lattes':''},
 {'nome':'Fernanda Alves','area':AREAS_PPGIT[3],'competencias':['SQL','Power BI','Engenharia de Dados'],'bio':'Especialista em inteligência de negócios, visualização e pipelines de dados.','disponivel':False,'lattes':''},
 {'nome':'Beatriz Nogueira','area':AREAS_PPGIT[0],'competencias':['Biotecnologia','Biofármacos','Pesquisa clínica','Desenvolvimento farmacêutico'],'bio':'Pesquisadora de biotecnologia e inovação biofarmacêutica, com experiência em desenvolvimento de biofármacos.','disponivel':True,'lattes':''},
 {'nome':'Ricardo Mendes','area':AREAS_PPGIT[2],'competencias':['Nanotecnologia','Novos materiais','Química','Caracterização de materiais'],'bio':'Pesquisador de novos materiais e nanotecnologia, com foco em caracterização química e aplicações tecnológicas.','disponivel':True,'lattes':''},
 {'nome':'Luísa Carvalho','area':AREAS_PPGIT[4],'competencias':['Sustentabilidade','Economia circular','ESG','Gestão ambiental'],'bio':'Pesquisadora de sustentabilidade, economia circular e inovação para gestão ambiental.','disponivel':True,'lattes':''},
]
MENTORADOS = [
 {'nome':'Estudante de IA','area':AREAS_PPGIT[3],'competencias':['Python','Machine Learning','NLP'],'objetivo':'Quero aprender inteligência artificial, processamento de linguagem natural e desenvolver um projeto de machine learning.'},
 {'nome':'Estudante de BI','area':AREAS_PPGIT[3],'competencias':['SQL','Power BI'],'objetivo':'Busco orientação para atuar com análise de dados, dashboards e business intelligence.'},
 {'nome':'Estudante de Inovação','area':AREAS_PPGIT[1],'competencias':['Scrum','Empreendedorismo','Gestão de projetos'],'objetivo':'Desejo desenvolver um negócio inovador e aprender gestão de projetos e empreendedorismo.'},
 {'nome':'Estudante de Biotecnologia','area':AREAS_PPGIT[0],'competencias':['Biotecnologia','Biofármacos'],'objetivo':'Busco orientação em pesquisa e desenvolvimento de produtos biofarmacêuticos.'},
 {'nome':'Estudante de Nanotecnologia','area':AREAS_PPGIT[2],'competencias':['Nanotecnologia','Novos materiais'],'objetivo':'Quero desenvolver pesquisa aplicada em nanotecnologia e caracterização de novos materiais.'},
 {'nome':'Estudante de Sustentabilidade','area':AREAS_PPGIT[4],'competencias':['Sustentabilidade','Economia circular'],'objetivo':'Desejo pesquisar soluções de economia circular e gestão ambiental sustentável.'},
]
