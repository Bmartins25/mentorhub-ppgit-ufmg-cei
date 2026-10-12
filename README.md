# MentorHub — PPGIT/UFMG/CEI — v12

Protótipo acadêmico independente com cinco áreas de concentração, seleção por área sem repetição, ranking explicável e dois motores de similaridade. Os perfis de exemplo são fictícios.

## IA semântica

A opção **IA semântica (embeddings)** utiliza `sentence-transformers` e o modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, baixado automaticamente na primeira execução. Embeddings de textos são armazenados em cache, evitando recomputação. O motor textual permanece disponível sem carregar o modelo.

## Publicação

Envie `app.py`, `matching.py`, `requirements.txt` e `.streamlit/config.toml` juntos ao GitHub. No Streamlit Community Cloud, use **Python 3.11 ou 3.12** ao criar/recriar a aplicação para melhor compatibilidade com PyTorch e Transformers. A versão de Python não é controlada pelo `requirements.txt`; confira as configurações do aplicativo. A primeira execução semântica pode demorar e exigir memória adicional.

## Teste

`python -m pip install -r requirements.txt`
`python test_smoke.py`
`python -m streamlit run app.py`

O teste smoke valida a importação e o algoritmo textual, mas não substitui o teste do download do modelo e do deploy no Streamlit Cloud.


## Versão revisada — motor semântico
- Dois rankings com pesos e sinais diferentes: baseline lexical e embeddings multilíngues.
- Três comparações semânticas: objetivo/biografia, competências e perfil completo.
- Justificativas específicas por motor e carregamento com indicador claro.
- O modelo de embeddings é baixado na primeira execução; requer acesso à internet no servidor.
- Pesos são heurísticos e exigem validação com relevância anotada por avaliadores humanos.

## Versão 3 — comparação controlada
A aba **Comparar motores** executa Textual Leve e IA Semântica sobre o mesmo perfil e conjunto de mentores, apresenta diferenças de posição, componentes do score e justificativas, e exporta CSV com os parâmetros do experimento. O score é heurístico e não representa probabilidade de sucesso. A qualidade da recomendação exige avaliação humana de relevância.
