# MentorHub — PPGIT/UFMG/CEI — v7

Protótipo demonstrativo independente de matching acadêmico. Os perfis são fictícios e não há integração com sistemas institucionais.

## Melhorias
- Cinco áreas de concentração do PPGIT; oito mentores e seis mentorados fictícios.
- Campo opcional de Currículo Lattes para novos mentores e link no ranking quando preenchido.
- Interface clara, inclusive menus suspensos e botão de exportação CSV.
- Rodapé «Equipe MentorHub».
- Ranking explicável e laboratório de testes.

## Publicação no GitHub / Streamlit Cloud
**Envie `app.py`, `matching.py`, `requirements.txt`, `.streamlit/config.toml` juntos.** Não renomeie `matching.py`: o import do `app.py` depende desse nome. Oculte/exclua `__pycache__` (já ignorado por `.gitignore`).

O Streamlit deve apontar para `app.py` na branch `main`. Se houver opção de Python no painel de deploy, prefira Python 3.12 ou 3.13.

### Teste antes de publicar
Execute `python test_smoke.py` para verificar importações, dados e pontuações sem instalar Streamlit. Para executar o aplicativo localmente: `pip install -r requirements.txt` e `streamlit run app.py`.

O modo de IA semântica é opcional e exige `sentence-transformers` instalado separadamente. O modo textual funciona apenas com Streamlit.
