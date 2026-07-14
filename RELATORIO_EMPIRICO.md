# Relatório empírico — Grupo 9

## Metodologia

- **Máquina:** AMD Ryzen 5 8500G (12 threads lógicas), 15 GiB RAM.
- **Ambiente:** Docker 28.1.1 (`Dockerfile` na raiz do repo), imagem `ubuntu:24.04`,
  Python 3.12.3 (CPython, sem JIT), container rodando sobre WSL2 no Windows 11.
- **Dataset:** `amzn` (`data/books_200M_uint32`), chaves reais de popularidade de
  vendas de livros da Amazon, `uint32`.
- **Parâmetros fixos do grupo 9 (§9):** `--theta 1.2`, `--mix 35:35:30` (I:D:S),
  `--agg count`, `--insert-order shuffle`, `--seed 9`.
- **Como reproduzir:** `bash run_experiments.sh && python3 plots.py --metrics results/metrics.csv --outdir results`
  (ver [README.md](README.md)). Todas as medições abaixo vêm de
  `results/metrics.csv`, gerado por essa execução — nenhum número foi
  editado manualmente.
- **Métrica de tempo:** nanossegundos por operação, medidos com
  `time.perf_counter_ns()` ao redor de cada chamada individual de
  `insert`/`delete`/`search` (ver `runner.py`). Reportamos média, p50 e p99.
- **`n` (eixo x dos gráficos de escala):** não é `--universe` nem `--ops`, é o
  **tamanho de pico realmente atingido** (`peak_n`), medido em tempo de
  execução — porque sob o mix 35:35:30 inserções e remoções se equilibram e a
  árvore vive em regime de "churn", de modo que o tamanho vivo real é bem
  menor que o universo de chaves.

## 1. Escala (§7.1)

Ver `results/escala.png`.

| n (pico) | insert méd. (ns) | delete méd. (ns) | search méd. (ns) | altura pico |
|---:|---:|---:|---:|---:|
| 89 | 2 259 | 1 775 | 293 | 10 |
| 1 829 | 4 278 | 3 600 | 582 | 30 |
| 15 919 | 6 050 | 4 974 | 848 | 34 |
| 170 787 | 14 250 | 9 419 | 2 388 | 48 |
| 1 745 942 | 32 257 | 19 500 | 6 251 | 56 |

`n` varia de 89 a 1 745 942 — `log₁₀(1745942/89) ≈ 4.3`, cobrindo as **quatro
ordens de grandeza** exigidas pelo enunciado (§7.1).

**Leitura:** o tempo médio de `search` cresce de 293 ns em n≈89 para 6 251 ns
em n≈1,75 milhão — um fator ~21× para um `n` que cresce ~19 600×, fortemente
sublinear e consistente com crescimento logarítmico
(`log₂(1745942/89) ≈ 14.3`, e o tempo por operação tem um piso de custo fixo
— dispatch de função Python, indexação de lista — que não escala com `n`,
então o crescimento *relativo* observado é ainda mais achatado que o `log n`
"puro" nas escalas pequenas, onde esse piso domina). `insert`/`delete` são
sistematicamente mais caros que `search` na mesma escala (ex.: em n≈1,75
milhão, insert é ~5,2× mais caro que search) porque pagam o custo amortizado
das rotações de restauração de heap, enquanto `search` só desce o BST sem
jamais rotacionar.

## 2. Sensibilidade ao enviesamento Zipfiano (§7.2)

Ver `results/theta.png`. `n` fixo em ~170 mil (`--universe` correspondente a
`n_alvo=100000`).

| theta | insert méd. (ns) | delete méd. (ns) | search méd. (ns) | altura pico |
|---:|---:|---:|---:|---:|
| 0.0 | 13 079 | 10 158 | 2 601 | 48 |
| 0.6 | 13 097 | 10 156 | 2 581 | 51 |
| 0.99 | 13 168 | 9 858 | 2 469 | 49 |
| 1.2 (grupo 9) | 12 662 | 8 671 | 2 078 | 48 |

**Leitura:** ao contrário do que a intuição de cache sugere (mais
enviesamento → mais reuso de linhas de cache → mais rápido), o efeito medido
aqui é pequeno e na direção esperada apenas para `delete`/`search`: em
`theta=1.2` (mix mais concentrado em poucas chaves "quentes") o `delete`
médio cai de 10 158 ns (theta=0) para 8 671 ns, e `search` cai de 2 601 ns
para 2 078 ns — uma redução de ~15-20%, plausível como efeito de localidade
(chaves quentes tendem a ficar em posições revisitadas da árvore, com maior
chance de estarem em cache). A altura de pico não varia de forma
significativa entre os thetas (48-51) porque a altura da treap é determinada
pelas prioridades aleatórias na inserção, não pela distribuição de acesso das
buscas/remoções subsequentes — `theta` afeta *quais* chaves são
buscadas/removidas, não a forma estrutural resultante da inserção.

## 3. Caso patológico: shuffle × sorted (§7.3)

Ver `results/patologico.png`. `n` fixo em ~16 mil.

| ordem | insert méd. (ns) | rotações | altura pico | log₂(n) teórico |
|---|---:|---:|---:|---:|
| shuffle | 6 076 | 1 030 738 | 34 | ~14 |
| sorted | 3 382 | 657 961 | 36 | ~14 |

**Leitura — o resultado mais importante deste experimento:** a treap **não
degenera** sob inserção em ordem `sorted`, diferente de uma BST sem
balanceamento (que viraria uma lista encadeada, altura `O(n)`). A altura de
pico é praticamente igual entre as duas ordens (34 vs 36, ambas ≈2.4×
log₂(n)), porque o balanceamento da treap depende das **prioridades
aleatórias** sorteadas a cada inserção, não da ordem de chegada das chaves —
essa é a garantia probabilística central da estrutura. Curiosamente, `sorted`
é ~44% *mais rápido* em inserção média (3 382 ns vs 6 076 ns) e faz ~36%
menos rotações — inserir sempre pela borda direita da árvore é o caso
favorável classicamente descrito para treaps (existe até um algoritmo O(n)
de construção via pilha para entrada já ordenada), então menos comparações
de prioridade são necessárias para restaurar o heap a cada inserção.

## 4. Teoria × prática (§7.4)

Ver `results/escala.png` (curva `O(log n) teórico` sobreposta) e
`results/rotacoes.png` (altura medida vs. `log₂(n)` vs. `1.39·log₂(n)`,
o valor esperado para treaps).

**Leitura:** a altura de pico medida cresce de 10 (n=89) a 56 (n≈1,75 milhão)
— logarítmico, não linear, confirmando que a implementação está de fato no
regime probabilístico esperado, não degenerando. Comparando com o mínimo
teórico `log₂(n)` e a constante esperada para treaps, `1,39·log₂(n)`:

| n (pico) | altura medida | log₂(n) | 1,39·log₂(n) | razão medida/1,39log₂n |
|---:|---:|---:|---:|---:|
| 89 | 10 | 6,5 | 9,0 | 1,11× |
| 1 829 | 30 | 10,8 | 15,0 | 2,00× |
| 15 919 | 34 | 13,9 | 19,4 | 1,75× |
| 170 787 | 48 | 17,4 | 24,2 | 1,98× |
| 1 745 942 | 56 | 20,7 | 28,8 | 1,94× |

A altura medida estabiliza perto de **~1,9-2,0× o valor teórico
`1,39·log₂(n)`** a partir de n≈1800, não em cima da curva teórica. Explicação:
`1,39·log₂(n)` é a altura esperada de uma treap construída *do zero* com `n`
inserções; `peak_height` aqui é o **máximo observado durante todo o regime de
churn** (35% inserção / 35% remoção intercaladas continuamente, `run` de
dezenas de milhões de operações) — remoções em treap fazem uma sequência de
rotações para afundar o nó removido até virar folha, o que pode
transientemente empurrar outra subárvore mais fundo antes do próximo pull. O
pico ao longo de um regime de churn longo tende a exceder a altura esperada
de uma construção única, o que explica o fator ~2× persistente. Ver
`results/rotacoes.png` para a curva completa.

Onde o **tempo** medido diverge da curva `O(log n)` pura: em `n` pequeno, o
custo é dominado por overhead fixo de interpretador (dispatch de método,
indexação de lista Python) que não escala com `n`; em `n` grande, o
crescimento do número de rotações por inserção (amortizado, mas não zero —
103 197 098 rotações registradas ao longo de todo o experimento n≈1,75
milhão, para ~70 milhões de operações estruturais I+D, ou seja, ~1,47
rotação por inserção/remoção em média) e a perda de localidade de cache — os
arrays paralelos ultrapassam o cache L2/L3 nessa escala, então acessos a
`key[i]`, `lft[i]` etc. em índices dispersos custam mais que a extrapolação
puramente logarítmica sugeriria.

## 5. Linha de base: treap × lista ordenada (§7.5)

Ver `results/baseline.png`.

| n (pico) | insert treap (ns) | insert baseline (ns) | search treap (ns) | search baseline (ns) |
|---:|---:|---:|---:|---:|
| 89 | 2 259 | 184 | 293 | 143 |
| 1 829 | 4 278 | 312 | 582 | 213 |
| 15 919 | 6 050 | 873 | 848 | 289 |
| 170 787 | 14 250 | 6 591 | 2 388 | 640 |

**Leitura:** em toda a faixa **efetivamente medida para a baseline** (até
n≈170 mil — o `run_experiments.sh` pula a baseline acima de `n=100000` por
decisão de projeto registrada em §2 desta justificativa: o custo `O(n)` por
escrita torna a execução proibitiva em tempo), a lista ordenada ainda é mais
rápida que a treap, tanto em inserção quanto em busca. Mas a razão
`treap/baseline` para `insert` cai consistentemente com `n` (~12× em n=89,
~13,7× em n=1829, ~6,9× em n=15919, ~2,16× em n≈170 mil) — uma tendência
clara de convergência.

**Estimativa do ponto de cruzamento (extrapolação, não medição direta):**
como o `insert` da baseline aumentou ~7,5× entre n=15919 e n≈170 mil (10,7×
mais chaves) — consistente com o custo `O(n)` de deslocamento de memória
dominando nessa faixa — extrapolamos linearmente para n≈1 745 942
(10,2× mais chaves que 170 787): `6591 ns × 10,2 ≈ 67 300 ns`. O `insert`
da treap **medido** (não extrapolado) nesse mesmo `n` é 32 257 ns — ou seja,
**a treap já seria ~2,1× mais rápida que a baseline extrapolada em
n≈1,75 milhão**, invertendo a vantagem observada em n≈170 mil (onde a
baseline ainda era ~2,16× mais rápida). Isso posiciona o ponto de cruzamento
real **entre n≈170 787 e n≈1 745 942** — plausivelmente na casa de algumas
centenas de milhares de chaves vivas. Uma medição direta da baseline nessa
faixa confirmaria a estimativa, mas não foi executada por ser
computacionalmente proibitiva (inserção `O(n)` sobre >10⁶ elementos, milhões
de vezes).

## Limitações e ameaças à validade

- Todas as medições são de uma única execução (`--seed 9` fixo) — não há
  repetição para estimar variância entre execuções, apenas a distribuição
  intra-execução (p50/p99 sobre as operações individuais).
- O ambiente é uma máquina compartilhada com o host (Docker Desktop sobre
  WSL2), sujeita a ruído de agendamento do SO hospedeiro — não é hardware
  dedicado a benchmark.
- `time.perf_counter_ns()` em Python tem overhead de chamada não-desprezível
  em operações de nanossegundos de duração — parte do "piso" observado em
  `n` pequeno é esse overhead de instrumentação, não custo real da estrutura.
