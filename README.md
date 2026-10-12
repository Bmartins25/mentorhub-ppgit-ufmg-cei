# MentorHub — PPGIT/UFMG/CEI — v4

MVP demonstrativo em Streamlit, com interface clara, ranking explicável, cadastro de perfis fictícios em sessão e laboratório de testes.

## Publicar no Streamlit Community Cloud

1. Envie **os arquivos do conteúdo desta pasta** para a raiz do repositório `mentorhub-ppgit-ufmg-cei` no GitHub (inclua `.streamlit/config.toml`).
2. O app existente deverá reconstruir automaticamente após o commit. O arquivo principal é `app.py`.
3. Abra https://mentor-ppgit-ufmg-cei.streamlit.app/ e atualize a página.

## Execução local

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## IA semântica (opcional)

Para habilitar o modo semântico, instale `sentence-transformers` no ambiente ou adicione uma versão compatível ao `requirements.txt`. O primeiro uso baixa o modelo, o que pode aumentar tempo e memória de inicialização. O modo textual funciona sem essa dependência.

**Nota:** perfis cadastrados são temporários, mantidos apenas na sessão Streamlit. Não há persistência, autenticação ou vínculo com sistemas institucionais. Não inserir dados pessoais reais.
