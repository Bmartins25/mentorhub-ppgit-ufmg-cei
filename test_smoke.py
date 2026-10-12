from pathlib import Path
import ast
from matching import MENTORES, MENTORADOS, AREAS_PPGIT, score
assert len(AREAS_PPGIT)==5
assert len(MENTORES)==8 and len(MENTORADOS)==6
for p in MENTORADOS:
    for m in MENTORES:
        r=score(p,m)
        assert 0<=r['total']<=100
        assert m['area'] in AREAS_PPGIT
        assert 'lattes' in m
source=Path(__file__).with_name('app.py').read_text(encoding='utf-8')
ast.parse(source)
assert 'from matching import MENTORES, MENTORADOS, AREAS_PPGIT, score' in source
assert 'Equipe MentorHub' in source
assert 'valid_lattes' in source
print('OK: importações, 5 áreas, 8 mentores, 6 mentorados, scores, Lattes, rodapé e sintaxe')
