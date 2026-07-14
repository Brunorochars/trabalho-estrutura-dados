# Justificativa de projeto — Grupo 9

## 1. Por que treap (e não AVL ou rubro-negra)

O enunciado (§3) deixa o balanceamento a critério do grupo, desde que os campos
aumentados (`size`, `agg`) permaneçam corretos sob rotação. Escolhemos **treap**
por três razões, comparadas às alternativas descartadas:

- **AVL** — rebalanceamento por altura exige recalcular fatores de balanceamento
  em cada nó do caminho de rotação e, em `delete`, potencialmente uma cadeia de
  rotações até a raiz. Corretude é mais fácil de auditar por invariante único
  (fator ∈ {−1,0,1}), mas o custo de manter esse invariante é maior em código e
  em rotações por remoção.
- **Rubro-negra** — invariantes de cor com 4–5 casos distintos por rebalanceamento
  de remoção (nó duplamente-negro). Mais rotações no pior caso são evitadas (é
  a estrutura com menos rotações amortizadas por operação), mas à custa de uma
  máquina de casos bem mais complexa — mais superfície para um bug silencioso
  no campo aumentado, exatamente o risco que o enunciado destaca como "o ponto
  difícil, e o mais avaliado".
- **Treap** — o invariante de balanceamento (min-heap de prioridades aleatórias)
  é probabilístico, não determinístico: `insert`/`delete` viram, respectivamente,
  "desce até achar o lugar do BST e sobe via rotações até restaurar o heap" e
  "desce a chave removida via rotações até virar folha e desconecta". Isso
  reduz o balanceamento a **um único invariante** (heap de prioridades) e a
  **um único ponto de recomputação de campo aumentado** (`_pull`, chamado a
  cada rotação) — mais fácil de argumentar corretude, ao custo de altura
  esperada `O(log n)` (não garantida no pior caso, mas 1.39·log₂(n) em
  expectativa — ver `rotacoes.png` no relatório empírico).

Custo medido dessa escolha: nenhuma rotação de rebalanceamento "extra" é feita
fora do caminho de inserção/remoção — `rotations` (instrumentado em
[`treap.py`](treap.py)) conta exatamente as rotações de restauração de heap,
sem passe adicional.

## 2. Alternativas descartadas para a linha de base (§7.5)

O enunciado pede uma "estrutura ingênua deliberada (lista ordenada, ou BST sem
balanceamento)". Escolhemos **lista ordenada com busca binária** (`bisect`),
implementada em [`runner.py`](runner.py) (`SortedListBaseline`), em vez de uma
BST sem balanceamento, por dois motivos:

1. Uma BST sem balanceamento degenera de formas diferentes dependendo da ordem
   de inserção — o que confundiria o "ponto de cruzamento" (§7.5) com o efeito
   já medido separadamente em `--insert-order sorted` (§7.3, caso patológico).
   A lista ordenada tem complexidade **assintótica fixa e conhecida**
   (busca `O(log n)`, inserção/remoção `O(n)` por deslocamento de memória),
   isolando melhor a variável que queremos observar: a partir de que `n` o
   custo `O(n)` do deslocamento supera o `O(log n)` da treap.
2. Mesma linguagem/overhead de interpretador que a treap (ambas em Python puro
   sobre a mesma VM), o que o próprio código já documenta como decisão de
   projeto — um ponto de cruzamento justo não pode ser contaminado por uma
   comparação C vs. Python.

Custo aceito: a baseline só roda até `n=100000` (`run_experiments.sh`) porque
acima disso o custo `O(n)` por escrita torna a execução proibitiva em tempo —
essa é também uma decisão registrada e mensurável (ver comentário em
`run_experiments.sh`, "acima disso o O(n) fica proibitivo").

## 3. Layout de arrays paralelos (em vez de nós-objeto)

`treap.py` representa cada nó como um **índice inteiro** em seis arrays
paralelos (`key`, `prio`, `lft`, `rgt`, `sz`, `ag`) em vez de instâncias de uma
classe `Node`. Trade-off explícito:

- **Ganho:** localidade de cache (arrays contíguos), sem overhead de
  alocação/coleta de objeto por inserção, e um índice `-1` sentinela substitui
  checagem de `None` em todo lugar.
- **Custo:** perde-se a legibilidade de `no.esquerda`/`no.direita`; todo acesso
  passa por indexação (`self.lft[i]`), o que exige mais disciplina para não
  inverter argumentos por engano (`self.lft[i] = self._insert(self.lft[i], k)`
  — o índice sempre precisa ser o filho correto, não o pai).
- Reuso de nós liberados (`self._free`) evita realocar o array inteiro a cada
  remoção; crescimento é amortizado (dobra de tamanho, como uma lista
  dinâmica).

Essa decisão é a que mais distancia a implementação de uma "treap de livro-texto"
genérica — não é meramente estilística, é o que possibilita medir efeitos de
localidade de cache no estudo empírico (§7.4).

## 4. Invariantes formais e argumento de corretude sob rotação

Enunciados exatamente como aparecem no docstring de [`treap.py`](treap.py):

```
(BST)  key[lft[i]] < key[i] < key[rgt[i]]         (chaves distintas)
(HEAP) prio[i] <= prio[filho]                      (min-heap nas prioridades)
(AUG)  sz[i] = 1 + sz[lft[i]] + sz[rgt[i]]
       ag[i] = combine(val(key[i]), ag[lft[i]], ag[rgt[i]])
       onde ag[-1] = identidade da operação (0 para soma/contagem, +inf para
       mínimo, -inf para máximo)
```

**Argumento informal de que (AUG) se mantém sob rotação.** Uma rotação
(`_rot_left`/`_rot_right`) troca dois ponteiros (`lft[i]`/`rgt[l]` ou
`rgt[i]`/`lft[r]`) e devolve o novo topo da subárvore. Isso viola (AUG)
**temporariamente** para os dois nós cujos filhos mudaram — o nó que desce
(`i`) e o nó que sobe (`l` ou `r`). A correção é restaurar (AUG) chamando
`_pull` **nessa ordem exata**: primeiro no nó que desceu (seus filhos já
estão corretos, então `_pull(i)` recomputa `sz[i]`/`ag[i]` a partir de dados
válidos), depois no nó que subiu (agora um dos filhos dele — o que desceu —
já tem campo aumentado correto, então `_pull(l)`/`_pull(r)` também recomputa
a partir de dados válidos). Inverter essa ordem propagaria um valor stale.
Cada uma das duas funções de rotação faz exatamente essa sequência.

Em `_delete_root_of`, quando o nó a remover tem dois filhos, a estratégia
"desce a chave via rotação até virar folha" reaplica essa mesma garantia a
cada rotação intermediária — não há atalho que pule `_pull`.

**Por que uma rotação que "esquece" de chamar `_pull` quebra tudo
silenciosamente** (o risco citado em §3): `range_agg`/`rank`/`select` decidem
se descem para um filho, ou se usam o campo `ag[i]`/`sz[i]` pronto, **sem
jamais revalidar contra os filhos**. Um `ag[i]` desatualizado é indistinguível
de um `ag[i]` correto do ponto de vista dessas consultas — o oráculo do
`gen_workload.py` só verifica `search`, então esse tipo de bug **não seria
detectado pelo oráculo**; só apareceria em `range_agg`/`rank`/`select`, que não
são exercitadas pelo trace. É por isso que a disciplina "sempre `_pull` após
qualquer mutação de `lft`/`rgt`" é tratada como invariante de código, não como
otimização opcional.

## 5. Agregação plugável (`range_agg`, §9: `count` para o grupo 9)

`make_agg(kind)` devolve uma tripla `(identidade, val, combine)` — por
exemplo, para `count`: identidade `0`, `val(k) = 1`, `combine = soma`. Isso
permite que `_pull` e `_range` sejam **agnósticos à agregação escolhida**: a
mesma árvore aumentada serve para soma, contagem, mínimo ou máximo trocando
apenas essa tripla, sem duplicar a lógica de rotação/pull. Para o grupo 9,
`--agg count` conta quantas chaves caem no intervalo `[a,b]` — a poda de
`_range` usa `ag[i]` diretamente quando a subárvore inteira está contida no
intervalo, dando custo `O(log n)` amortizado por consulta em vez de `O(n)`
por varredura.

## 6. `search`/`rank` iterativos vs. `insert`/`delete` recursivos

`insert` e `delete` são recursivos porque precisam **recompor** o campo
aumentado na volta da recursão (cada chamada retorna o novo índice de raiz da
subárvore, e o chamador religa esse índice e roda `_pull`). `search` e `rank`
são iterativos porque seguem um único caminho raiz→folha sem nunca precisar
"desfazer" nada na volta — não há estado para recompor, então uma pilha de
recursão só adicionaria overhead de chamada de função sem benefício. Essa
diferença é intencional, não inconsistência de estilo.
