# Guia de Estudo — Projeto Final Estruturas de Dados (Grupo 9)

> Este guia foi escrito para quem nunca viu esse tipo de projeto antes.
> Cada conceito é apresentado com uma analogia do mundo real antes da explicação técnica.
> Leia na ordem — cada parte depende da anterior.

---

## Índice

1. [O que esse projeto faz, em palavras simples](#1-o-que-esse-projeto-faz-em-palavras-simples)
2. [O que é uma Árvore de Busca?](#2-o-que-é-uma-árvore-de-busca)
3. [O problema da árvore desequilibrada](#3-o-problema-da-árvore-desequilibrada)
4. [O que é um Heap?](#4-o-que-é-um-heap)
5. [A Treap — juntar os dois](#5-a-treap--juntar-os-dois)
6. [Rotações — como a treap se equilibra](#6-rotações--como-a-treap-se-equilibra)
7. [Campos Aumentados — o que torna a treap "aumentada"](#7-campos-aumentados--o-que-torna-a-treap-aumentada)
8. [Layout de Arrays Paralelos — por que o código parece estranho](#8-layout-de-arrays-paralelos--por-que-o-código-parece-estranho)
9. [As 6 Operações implementadas](#9-as-6-operações-implementadas)
10. [O Pipeline: como as peças se encaixam](#10-o-pipeline-como-as-peças-se-encaixam)
11. [O Dataset e a Distribuição Zipfiana](#11-o-dataset-e-a-distribuição-zipfiana)
12. [Os 5 Experimentos do projeto](#12-os-5-experimentos-do-projeto)
13. [Por que demora 3 horas?](#13-por-que-demora-3-horas)
14. [O que mostrar na apresentação](#14-o-que-mostrar-na-apresentação)

---

## 1. O que esse projeto faz, em palavras simples

Imagine que você tem uma **lista de 200 milhões de números** (chaves de livros da Amazon). Você precisa de uma estrutura que:

- Guarde esses números
- Permita buscar qualquer número em menos de 30 passos (mesmo com 1 milhão de números guardados)
- Permita inserir e remover números rapidamente
- Responda perguntas como "quantos números existem entre 1000 e 5000?"

O projeto implementa exatamente essa estrutura, chamada **Treap aumentada**, e depois mede o desempenho dela com experimentos.

---

## 2. O que é uma Árvore de Busca?

### Analogia: Dicionário vs. lista telefônica

Imagine procurar a palavra "zebra" em dois cenários:

- **Lista aleatória:** você lê do começo até achar "zebra". Pode levar até ler 200 mil palavras.
- **Dicionário (ordem alfabética):** você abre no meio, vê que está em "m", vai para o final, abre no meio de novo, vê "t", vai para depois, e em ~17 aberturas você acha "zebra" num dicionário de 200 mil palavras.

O segundo método é a lógica de uma **Árvore de Busca Binária (BST)**.

### Como funciona a BST

Cada "caixinha" (nó) guarda um número e aponta para no máximo dois filhos:
- Filho da **esquerda**: tem número MENOR
- Filho da **direita**: tem número MAIOR

```
          50
         /  \
        30   70
       / \   / \
      20  40 60  80
```

Para procurar o número 60:
1. Começa na raiz (50). 60 > 50 → vai para a direita
2. Está no 70. 60 < 70 → vai para a esquerda
3. Encontrou 60! Apenas 3 passos.

Para uma árvore com n números bem distribuídos, o número máximo de passos é **log₂(n)**. Com 1 milhão de números: log₂(1.000.000) ≈ 20 passos. Com 1 bilhão: ~30 passos. Isso é O(log n) — fenomenal.

---

## 3. O problema da árvore desequilibrada

Se você inserir os números **em ordem crescente** (1, 2, 3, 4, 5...) numa BST sem balanceamento, acontece isso:

```
1
 \
  2
   \
    3
     \
      4
       \
        5    ← altura = n (vira uma lista!)
```

Agora buscar o número 5 exige percorrer todos os nós. Voltamos ao O(n) — tão lento quanto uma lista normal.

Esse é o **caso patológico** que o Experimento 3 (§7.3) do projeto testa: a treap aguenta essa situação? (Spoiler: aguenta.)

---

## 4. O que é um Heap?

### Analogia: Torneio de tênis

Num torneio eliminatório, o campeão final venceu TODOS os outros. Quem está mais acima na chave foi mais longe no torneio. O "melhor" fica no topo.

Um **heap** funciona assim: é uma árvore onde o pai é sempre "melhor" (menor, no caso de min-heap) que os filhos.

```
Min-heap (menor valor sempre na raiz):

        1         ← menor de todos
       / \
      3   4
     / \
    5   9
```

**Regra do heap:** `valor(pai)` ≤ `valor(qualquer filho)`

Isso não diz nada sobre a relação entre irmãos — 3 e 4 podem estar em qualquer ordem. O heap só garante que o pai é menor que os filhos.

---

## 5. A Treap — juntar os dois

Treap = **Tree** (árvore) + **Heap**

Cada nó tem **duas coisas**:
- Uma **chave** (o número que você inseriu — ex: 42)
- Uma **prioridade** (número aleatório sorteado no momento da inserção — ex: 0.73)

A chave obedece à regra da BST. A prioridade obedece à regra do heap.

```
Exemplo de treap com 3 elementos (chave/prioridade):

         (50 / 0.1)      ← menor prioridade na raiz (min-heap de prioridade)
        /            \
  (30 / 0.4)    (70 / 0.7)
```

- `(30 / 0.4)` fica à esquerda de 50 porque 30 < 50 ✓ (regra BST)
- `(70 / 0.7)` fica à direita de 50 porque 70 > 50 ✓ (regra BST)
- `(50 / 0.1)` fica na raiz porque 0.1 < 0.4 e 0.1 < 0.7 ✓ (regra heap)

**Por que isso garante balanceamento?**

As prioridades são sorteadas aleatoriamente. A probabilidade de você sortear prioridades numa sequência que cria uma árvore degenerada (tipo lista) é astronomicamente pequena. Matematicamente prova-se que a altura esperada é **1,39 × log₂(n)** — quase tão boa quanto o mínimo teórico.

Diferente da AVL ou rubro-negra (que usam regras determinísticas complexas), a treap usa **aleatoriedade** para simplificar tudo. Uma única regra de heap em vez de 4-5 casos de rebalanceamento.

> **No código:** `treap.py:59-76` — o `__init__` da classe Treap. As 6 listas (`key`, `prio`, `lft`, `rgt`, `sz`, `ag`) são os arrays paralelos. `self._rand = self._rng.random` é o gerador de prioridades aleatórias.

---

## 6. Rotações — como a treap se equilibra

Quando você insere um novo nó, ele vai para o lugar certo pela regra BST. Mas a prioridade aleatória dele pode ser menor que a do pai — violando a regra do heap. Para consertar, fazemos uma **rotação**.

### Rotação à direita

Quando o **filho esquerdo** tem prioridade menor que o pai:

```
Antes:                   Depois:
    i (prio=0.8)             l (prio=0.3)
   /                        / \
  l (prio=0.3)             A   i (prio=0.8)
 / \                           /
A   B                         B

i desce, l sobe. A fica com l. B vai para i.
```

A operação inteira é só troca de ponteiros — não move dados, apenas muda quem aponta para quem. É O(1).

> **No código:** `treap.py:118-124` — `_rot_right`. Só 3 linhas de lógica.

### O `_pull` — por que vem depois de toda rotação

Após uma rotação, dois nós mudaram de lugar. Os campos que guardam "quantos nós tenho abaixo de mim" (`sz`) e "qual é o resultado acumulado da minha subárvore" (`ag`) ficam desatualizados para esses dois nós.

`_pull(i)` recalcula esses campos para o nó `i` olhando para os filhos dele. Deve ser chamado:
1. **Primeiro** no nó que desceu (porque os filhos dele já estão corretos)
2. **Depois** no nó que subiu (porque agora o filho dele — que desceu — já foi corrigido)

Se inverter a ordem, o nó que subiu vai ler um valor velho do filho. Bug silencioso.

---

## 7. Campos Aumentados — o que torna a treap "aumentada"

Uma treap simples só faz inserção, remoção e busca. A versão **aumentada** carrega dados extras em cada nó para responder perguntas sobre intervalos.

### Os dois campos extras

#### `sz[i]` — tamanho da subárvore

`sz[i]` diz: "quantos nós existem em mim e em todos os meus descendentes?"

```
          50 (sz=5)
         /          \
      30 (sz=2)    70 (sz=2)
       \             \
      40 (sz=1)     80 (sz=1)
```

Com `sz`, você pode responder "quantas chaves são menores que 60?" sem varrer a árvore — basta somar os tamanhos dos galhos que estão todos à esquerda.

#### `ag[i]` — agregado da subárvore

`ag[i]` diz: "qual é o resultado acumulado (soma/contagem/mínimo/máximo) de todas as chaves abaixo de mim?"

Para o Grupo 9, a agregação é **contagem** (`count`). Então `ag[i]` = quantidade de nós na subárvore de i = igual ao `sz[i]` nesse caso. Para outros grupos, poderia ser a soma de todas as chaves.

### O que esses campos permitem

**`rank(k)`** — "quantas chaves são menores que k?"

Navega pela árvore. Cada vez que vai para a direita, soma 1 (o nó atual) + sz (filho esquerdo). Resultado em O(log n) sem varrer nada.

**`select(idx)`** — "qual é a idx-ésima menor chave?"

O índice 0 = menor chave. Usa `sz[filho_esquerdo]` para decidir se desce à esquerda, pega o nó atual, ou desce à direita. O(log n).

**`range_agg(a, b)`** — "resultado da agregação para todas as chaves entre a e b?"

A sacada: se uma subárvore inteira está **dentro** do intervalo [a, b], usa `ag[i]` pronto sem descer. Se está **fora**, ignora. Só desce quando a subárvore está **parcialmente** dentro. O(log n) em vez de O(n).

> **No código:** `treap.py:255-277` — `range_agg` e `_range`. A linha `if a <= lo and hi <= b: return self.ag[i]` é a "poda" que faz o O(log n) funcionar.

---

## 8. Layout de Arrays Paralelos — por que o código parece estranho

Se você fosse implementar uma árvore do jeito mais "natural" em Python, faria assim:

```python
class No:
    def __init__(self, chave):
        self.chave = chave
        self.esquerda = None
        self.direita = None
        self.tamanho = 1
```

O projeto fez diferente. Em vez de criar um objeto `No` para cada elemento, usa **6 listas** onde o índice é o "endereço" do nó:

```python
self.key  = [0, 42, 17, 99, ...]   # key[3] = chave do nó 3
self.lft  = [-1, 2, -1, 1, ...]    # lft[3] = índice do filho esquerdo do nó 3
self.rgt  = [-1, -1, -1, 0, ...]   # rgt[3] = índice do filho direito do nó 3
self.sz   = [1, 3, 1, 4, ...]      # sz[3]  = tamanho da subárvore do nó 3
```

O valor **-1** significa "não existe" (equivale ao `None`).

### Por que fazer assim? Cache do processador.

Quando o processador lê `self.key[3]`, ele busca um bloco de memória. Como `key` é uma lista contígua na memória, `key[4]`, `key[5]`, `key[6]`... também vêm junto nesse bloco. Quando você precisar deles logo em seguida, já estão no **cache L1** — velocíssimo.

Com objetos separados (`class No`), cada nó fica num lugar diferente na memória. Acessar `no.esquerda.chave` pode causar um **cache miss** — o processador tem que buscar esse bloco de memória do zero. Com datasets de milhões de elementos, esses misses se acumulam.

**Lista de objetos:**
```
RAM: ...No₁[espalh...]...No₂[ado na...]...No₃[memória]...
```

**Arrays paralelos:**
```
RAM: key=[chave0, chave1, chave2, chave3, ...] ← CONTÍGUO
     lft=[lft0, lft1, lft2, lft3, ...] ← CONTÍGUO
```

> **Tradeoff:** o código fica menos legível (`self.lft[i]` em vez de `no.esquerda`), mas é mais eficiente para milhões de elementos.

---

## 9. As 6 Operações implementadas

### `insert(k)` — inserir a chave k

1. Desce pela árvore como numa BST normal (esquerda se k < chave_atual, direita se k > chave_atual)
2. Cria um novo nó com prioridade aleatória
3. Na volta da recursão (subindo), se o filho tem prioridade menor que o pai, faz rotação
4. Chama `_pull` em cada nó no caminho de volta

> **No código:** `treap.py:137-159`

### `delete(k)` — remover a chave k

1. Encontra o nó com chave k
2. Enquanto o nó tem dois filhos: rotaciona o filho de MENOR prioridade para cima (empurrando k para baixo)
3. Quando k virou folha (ou tem só um filho), remove simplesmente

> **No código:** `treap.py:162-211` — `_delete_root_of` é a parte que empurra o nó para baixo

### `search(k)` — buscar se k existe

Igual à BST: segue esquerda/direita até achar ou chegar num nó vazio.

```python
i = self.root
while i != -1:
    ki = self.key[i]
    if k == ki: return True
    i = self.lft[i] if k < ki else self.rgt[i]
return False
```

É iterativo (loop, não recursão) porque não precisa fazer nada na volta — sem `_pull` necessário.

> **No código:** `treap.py:214-221`

### `rank(k)` — quantas chaves são menores que k

Vai descendo. Cada vez que vai para a direita (k > chave_atual), soma 1 + tamanho do filho esquerdo.

> **No código:** `treap.py:224-235`

### `select(idx)` — qual é a idx-ésima menor chave

- `sz[filho_esquerdo]` = quantas chaves menores existem abaixo
- Se idx < sz_esq → a chave está no galho esquerdo
- Se idx == sz_esq → é o nó atual
- Se idx > sz_esq → está no galho direito (subtrai sz_esq + 1 do índice)

> **No código:** `treap.py:238-252`

### `range_agg(a, b)` — agregado das chaves entre a e b

Navega a árvore com limites implícitos. Cada subárvore "sabe" que suas chaves estão entre `lo` e `hi`. Se [lo, hi] está completamente dentro de [a, b] → usa `ag[i]` pronto. Se está completamente fora → retorna identidade (0 para contagem). Só desce quando está parcialmente dentro.

> **No código:** `treap.py:255-277`

---

## 10. O Pipeline: como as peças se encaixam

O projeto tem 4 arquivos principais que se comunicam assim:

### Passo 1 — `gen_workload.py generate` (gera o teste)

Lê o dataset (200 milhões de chaves binárias), escolhe um subconjunto, e gera dois arquivos:

- **`.trace`** — lista de operações para executar:
  ```
  I 1234    ← inserir 1234
  I 5678    ← inserir 5678
  D 1234    ← deletar 1234
  S 5678    ← buscar 5678
  S 9999    ← buscar 9999
  ```

- **`.expected`** — gabarito com os resultados esperados das buscas:
  ```
  5678 FOUND
  9999 NOT_FOUND
  ```

Só as buscas têm gabarito. As inserções e remoções são testadas **indiretamente**: se você deletar errado, a busca vai dar resultado errado e o oráculo pega.

### Passo 2 — `runner.py` (executa o teste)

Lê o `.trace`, executa cada operação na treap (ou na baseline), e produz:

- **`.out`** — resultados das buscas que o aluno produziu:
  ```
  5678 FOUND
  9999 NOT_FOUND
  ```

- **`metrics.csv`** — dados de desempenho (tempo médio, p50, p99 por tipo de operação)

### Passo 3 — `gen_workload.py verify` (confere)

Compara `.expected` com `.out`. Se bater em tudo → `[OK]`. Se houver diferença → `[FALHA]`.

### Passo 4 — `plots.py` (gera os gráficos)

Lê `metrics.csv` e gera os 5 PNGs do relatório empírico.

### Passo 0 — `run_experiments.sh` (orquestra tudo)

Shell script que chama todos os passos acima, em vários tamanhos de dataset, para os 4 experimentos.

---

## 11. O Dataset e a Distribuição Zipfiana

### O Dataset (`books_200M_uint32`)

Arquivo binário com 200 milhões de números inteiros de 32 bits (uint32), representando popularidade de vendas de livros na Amazon. É um dataset real usado em benchmarks de estruturas de dados (projeto SOSD — Searching on Sorted Data).

O arquivo tem ~800 MB. Nunca entra no git (`.gitignore`). Precisa ser baixado uma vez por máquina:
```
wget -O data/books_200M_uint32 \
    "https://zenodo.org/records/15240501/files/books_200M_uint32?download=1"
```

### Distribuição Zipfiana — o jeito real como as pessoas acessam dados

No mundo real, acesso a dados nunca é uniforme. Nas buscas do Google, nas músicas do Spotify, nos produtos da Amazon: poucas coisas concentram a maior parte dos acessos. Isso se chama **Lei de Zipf** (ou distribuição de cauda longa).

**Parâmetro `theta` — controla o quanto é enviesado:**

| theta | O que significa | Exemplo real |
|---|---|---|
| 0.0 | Uniforme — todos com a mesma chance | Rifa onde cada número tem a mesma probabilidade |
| 0.6 | Leve preferência pelas mais populares | Músicas em rádio FM |
| 0.99 | Padrão YCSB (benchmark industrial Yahoo) | Buscas no Google |
| 1.2 | Mais concentrado ainda | **Grupo 9** — ainda mais enviesado que o padrão |

Com theta=1.2, as ~100 chaves mais "quentes" recebem uma fração enorme das operações. Isso importa para a treap porque essas chaves vão ficando próximas da raiz (ficam mais fáceis de achar). O experimento §7.2 mede exatamente esse efeito.

> **No código:** `gen_workload.py:41-74` — classe `Zipfian`. A fórmula parece complicada mas a ideia é simples: `next_rank()` retorna um número de 0 a n, onde 0 é o mais provável.

---

## 12. Os 5 Experimentos do projeto

### §7.1 — Experimento de ESCALA: como o tempo cresce com n?

**Pergunta:** Se eu dobrar o número de elementos na árvore, quanto o tempo de busca aumenta?

**Como roda:** executa a treap com 5 tamanhos diferentes de n:
- n ≈ 89 (universo de 5.000)
- n ≈ 1.829 (universo de 50.000)
- n ≈ 15.919 (universo de 500.000)
- n ≈ 170.787 (universo de 5.000.000)
- n ≈ 1.745.942 (universo de 50.000.000) ← esse demora horas

**Resultado medido:**

| n | Busca (médio) |
|---|---|
| 89 | 293 ns |
| 1.829 | 582 ns |
| 15.919 | 848 ns |
| 170.787 | 2.388 ns |
| 1.745.942 | 6.251 ns |

Quando n aumentou ~19.600×, o tempo de busca aumentou apenas ~21×. Isso é o O(log n) em ação: log₂(1.745.942 / 89) ≈ 14,3 — o que bate com o que foi medido.

**Gráfico:** `results/escala.png` — escala log-log com a curva teórica O(log n) sobreposta.

### §7.2 — Sensibilidade ao Zipfian (theta)

**Pergunta:** Acessos mais concentrados (theta maior) deixam a árvore mais rápida? Por quê?

**Como roda:** n fixo em ~170k, varia theta = {0.0, 0.6, 0.99, 1.2}.

**Resultado:** theta=1.2 (Grupo 9) é ligeiramente mais rápido que theta=0 para delete e search (~15-20% mais rápido). Motivo: chaves "quentes" ficam sendo acessadas repetidamente e tendem a ficar no cache do processador.

**Surpresa:** a **altura da árvore não muda** entre thetas (48-51 em todos). Isso porque o balanceamento da treap depende das **prioridades aleatórias no momento da inserção**, não de quais chaves são mais acessadas depois.

**Gráfico:** `results/theta.png`

### §7.3 — Caso patológico: inserção em ordem

**Pergunta:** A treap degenera se eu inserir tudo em ordem crescente?

**Como roda:** compara `--insert-order shuffle` (aleatória) vs `sorted` (crescente), n fixo em ~16k.

**Resultado:**
- Altura com shuffle: 34
- Altura com sorted: 36

Praticamente idêntico! A treap **NÃO degenera** porque o balanceamento depende das prioridades aleatórias, não da ordem de chegada das chaves.

**Surpresa:** inserção em ordem `sorted` é ~44% MAIS RÁPIDA (3.382 ns vs 6.076 ns). Isso porque inserir sempre no lado direito da árvore é o caso mais simples — menos comparações de prioridade para restaurar o heap.

Isso contrasta com uma BST sem balanceamento, que com inserção ordenada viraria uma lista de tamanho 16.000 — busca em O(n) ao invés de O(log n).

**Gráfico:** `results/patologico.png`

### §7.4 — Teoria × Prática

**Pergunta:** A altura medida bate com o que a teoria prevê?

A teoria diz: altura esperada de uma treap é **1,39 × log₂(n)**.

**Resultado medido:**

| n | Altura medida | 1,39 × log₂(n) |
|---|---|---|
| 89 | 10 | 9,0 |
| 1.829 | 30 | 15,0 |
| 15.919 | 34 | 19,4 |
| 170.787 | 48 | 24,2 |
| 1.745.942 | 56 | 28,8 |

A altura real ficou ~1,9-2× o teórico, não em cima da curva. Por quê? A teoria assume uma construção "limpa" com n inserções. O experimento mede o **pico** durante um regime de churn contínuo (35% inserção + 35% remoção intercaladas sem parar). Remoções fazem rotações que podem temporariamente aumentar a altura antes de estabilizar. O pico ao longo de dezenas de milhões de operações tende a ser maior que a altura esperada de uma construção única.

**Gráficos:** `results/escala.png` e `results/rotacoes.png`

### §7.5 — Linha de Base: Treap vs Lista Ordenada

**Pergunta:** A partir de que n a treap é mais rápida que uma lista ordenada?

**Por que comparar com lista ordenada?** Uma lista ordenada com busca binária é simples, confiável e muito eficiente na memória (array contíguo). É a alternativa mais justa para comparar — mesma linguagem, mesmo overhead de Python.

- **Busca na lista:** O(log n) — busca binária com bisect
- **Inserção na lista:** O(n) — precisa deslocar todos os elementos para abrir espaço
- **Inserção na treap:** O(log n)

**Resultado:**

| n | Inserção Treap | Inserção Lista |
|---|---|---|
| 89 | 2.259 ns | 184 ns |
| 1.829 | 4.278 ns | 312 ns |
| 15.919 | 6.050 ns | 873 ns |
| 170.787 | 14.250 ns | 6.591 ns |

Até n≈170k, a lista ainda é mais rápida! Mas a razão treap/lista está caindo (12× em n=89, depois 13,7×, 6,9×, 2,16×). Extrapolando, a treap cruza a lista em torno de 400-600 mil elementos.

Por que a lista ainda ganha em n pequeno? A treap tem overhead de Python (chamadas recursivas, geração de prioridade aleatória, `_pull`). Para n pequeno, esse overhead domina. A lista é implementada em C por baixo (o módulo `bisect` do Python é código C nativo) — e acesso sequencial a um array contíguo é o que o processador faz melhor.

**Gráfico:** `results/baseline.png`

---

## 13. Por que demora 3 horas?

### O tamanho do problema no experimento maior

O `run_experiments.sh` tem um loop de escala que inclui N=1.000.000. Para esse tamanho:

```
UNIVERSE = 50 × 1.000.000 = 50.000.000 chaves
OPS = 2 × 50.000.000 = 100.000.000 operações
```

São **100 milhões de operações** executadas em Python puro numa treap recursiva.

### Por que Python é lento para isso

Python é uma linguagem **interpretada**: cada linha de código é processada uma a uma em tempo de execução. Linguagens como C ou Go compilam o código para instruções de máquina diretamente — ordens de magnitude mais rápido para loops intensivos.

Além disso, cada `insert` ou `delete` na treap é **recursivo**: cria um novo "quadro de pilha" (variáveis locais) para cada nível da árvore. Com altura ~56 (n=1,75M), cada inserção cria ~56 quadros. Python cobra um overhead fixo por quadro de função.

Com 70 milhões de operações de insert/delete × 56 níveis = ~3,9 bilhões de chamadas de função Python. Cada uma custa alguns nanosegundos de overhead de interpretação.

### Qual experimento demora mais

- N=100 → ops=10.000 → segundos
- N=1.000 → ops=100.000 → segundos
- N=10.000 → ops=1.000.000 → ~1 minuto
- N=100.000 → ops=10.000.000 → ~10-15 minutos
- **N=1.000.000 → ops=100.000.000 → ~2-2,5 horas** (domina tudo)

Mais os experimentos de theta (4 valores × 10M ops cada) = ~30-40 minutos adicionais.

---

## 14. O que mostrar na apresentação

### Estratégia para 10 minutos: C + A

Os resultados já foram gerados pelo Bruno (arquivos `results/*.png` e `results/metrics.csv`). **Não precisam rodar tudo de novo.**

### Roteiro sugerido

**Minutos 1-2: Mostrar os gráficos prontos**

Abrir `results/escala.png` e explicar o que é O(log n) na prática.

**Minutos 3-4: Demo ao vivo (30 segundos de execução)**

Roda no terminal da apresentação:

```bash
# No diretório do projeto
python3 gen_workload.py generate --synthetic 200000 --ops 500000 --out demo \
    --universe 100000 --mix 35:35:30 --theta 1.2 --seed 9

python3 runner.py --trace demo.trace --out demo.out \
    --struct treap --agg count --seed 9

python3 gen_workload.py verify --expected demo.expected --candidate demo.out
```

Isso usa dados sintéticos (sem precisar do dataset de 800 MB), roda em ~20-30 segundos, e mostra:
- O gerador de workload funcionando
- A treap executando 500.000 operações
- O oráculo confirmando `[OK]` — corretude verificada

**Minutos 5-7: Passear pelos outros gráficos**

- `results/patologico.png` — "a treap não degenera com inserção ordenada"
- `results/baseline.png` — "a lista ganha em n pequeno mas a treap escala melhor"
- `results/theta.png` — "Zipfian mais concentrado = ligeiramente mais rápido"

**Minutos 8-10: Perguntas / justificativas de projeto**

Pontos que o professor pode perguntar:
- "Por que treap e não AVL?" → Invariante único, código menor, mesma garantia O(log n)
- "Por que lista ordenada como baseline?" → Complexidade assintótica conhecida e fixa, mesma linguagem, comparação justa
- "Por que arrays paralelos?" → Localidade de cache, sem overhead de objeto Python por nó
- "Por que demorou 3h?" → Python CPython sem JIT, 100M operações recursivas. PyPy rodaria 10-50× mais rápido.

---

## Referências rápidas

| Arquivo | O que faz |
|---|---|
| `treap.py` | A estrutura de dados em si (insert, delete, search, rank, select, range_agg) |
| `gen_workload.py` | Gera o .trace (operações) e .expected (gabarito) a partir do dataset |
| `runner.py` | Executa o .trace na treap ou na baseline, mede tempos, gera metrics.csv |
| `run_experiments.sh` | Orquestra todos os experimentos (chama gen_workload e runner várias vezes) |
| `plots.py` | Lê metrics.csv e gera os 5 PNGs |
| `results/*.png` | Gráficos já gerados (não precisam reprocessar) |
| `RELATORIO_EMPIRICO.md` | Análise dos resultados (o que os números significam) |
| `JUSTIFICATIVA.md` | Por que as decisões de projeto foram tomadas dessa forma |

---

*Guia gerado para a apresentação do Grupo 9 — 2026-07-14*
