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
    wants=normset(mentorado['competencias']); offers=normset(mentor['competencias']); skill=len(wants & offers)/len(wants) if wants else 0
    semantic_score=cosine(mentorado['objetivo']+' '+' '.join(mentorado['competencias']),mentor['bio']+' '+' '.join(mentor['competencias'])) if semantic is None else semantic
    area=1.0 if mentorado['area']==mentor['area'] else 0.0
    available=1.0 if mentor['disponivel'] else 0.0
    total=round(100*(.40*skill+.35*semantic_score+.15*area+.10*available),1)
    common=sorted(wants & offers)
    reasons=[]
    if common: reasons.append('Competências em comum: '+', '.join(common[:6]))
    if area: reasons.append('Mesma área de interesse')
    if not mentor['disponivel']: reasons.append('Mentor indisponível no momento')
    reasons.append('Afinidade textual estimada: {:.0f}%'.format(semantic_score*100))
    return {'total':total,'competencias':round(skill*100,1),'semantica':round(semantic_score*100,1),'area':round(area*100),'disponibilidade':round(available*100),'justificativa':'; '.join(reasons)}
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
