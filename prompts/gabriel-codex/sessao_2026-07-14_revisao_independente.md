# Sessão 2026-07-14 — Codex — Gabriel Camargo Ortiz

Contexto: primeira revisão independente de Gabriel no projeto usando Codex. O
repositório já continha a implementação principal, scripts de execução,
experimentos, relatório e organização inicial dos prompts. O objetivo foi
entender e auditar a solução existente sem alterar arquivos.

---

## 1. Revisão independente da implementação e do pipeline

**Prompt:** solicitei ao Codex uma revisão independente da treap, do pipeline do
oráculo e dos experimentos do grupo 9, sem alterar arquivos. O foco foi verificar
se a implementação atendia ao enunciado, especialmente as operações obrigatórias
da árvore aumentada e a configuração específica do grupo 9.

**Arquivos lidos pelo Codex:**

- `treap.py`
- `runner.py`
- `run_experiments.sh`
- `plots.py`
- `RELATORIO_EMPIRICO.md`
- `prompts/README.md`
- `gen_workload.py`
- `README.md`
- `JUSTIFICATIVA.md`

**Raciocínio:** a revisão foi feita primeiro por leitura estática, sem alterar o
código. A intenção foi evitar mudanças desnecessárias em uma implementação que
já havia sido produzida por outro integrante e verificar se a arquitetura estava
coerente com o projeto final.

---

## 2. Arquitetura identificada

O Codex identificou o seguinte fluxo:

- `gen_workload.py` gera o trace de operações e o gabarito esperado;
- `runner.py` executa a treap ou a baseline e emite as respostas das buscas;
- `run_experiments.sh` orquestra os cenários experimentais do grupo 9;
- `plots.py` transforma o CSV de métricas em gráficos;
- `RELATORIO_EMPIRICO.md` e `JUSTIFICATIVA.md` documentam decisões, resultados e interpretação.

A implementação da treap usa arrays paralelos:

- `key`
- `prio`
- `lft`
- `rgt`
- `sz`
- `ag`

Os nós são representados por índices, e `-1` representa filho vazio.

---

## 3. Achados de corretude

**BST:** a propriedade de árvore binária de busca foi considerada correta. A
inserção coloca chaves menores à esquerda e maiores à direita; duplicatas são
tratadas como no-op. As rotações preservam a ordem em-ordem, e a exclusão
rearranja a árvore por rotações válidas.

**HEAP:** a propriedade de heap da treap foi considerada correta. A estrutura usa
min-heap de prioridades. Na inserção, o filho de menor prioridade é promovido
quando necessário. Na exclusão, entre os dois filhos, é promovido o de menor
prioridade antes de continuar a remoção.

**AUG:** os campos aumentados `sz` e `ag` foram considerados corretos pela leitura
estática. A função `_pull()` recompõe os campos a partir dos filhos. Nas rotações,
o nó que desce é atualizado primeiro e o nó que sobe é atualizado depois. Isso
mantém os campos aumentados consistentes após mudanças estruturais.

**`range_agg` para `count`:** para o grupo 9, o agregado é contagem. O Codex
verificou que `identity = 0`, cada chave contribui com valor `1`, e a combinação
usa soma. Portanto, `range_agg(a, b)` conta corretamente as chaves presentes no
intervalo fechado `[a, b]`.

**`rank` e `select`:** ambos foram considerados corretos. `rank(k)` usa `sz` para
contar nós estritamente menores que `k`, enquanto `select(i)` usa índice 0-based
e valida limites.

**Saída para o oráculo:** o `runner.py` foi considerado compatível com o oráculo,
pois para cada operação `S` escreve exatamente `<chave> FOUND` ou
`<chave> NOT_FOUND`, e não escreve linhas para operações `I` ou `D`.