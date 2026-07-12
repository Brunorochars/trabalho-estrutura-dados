#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# run_experiments.sh -- Orquestra TODAS as execucoes exigidas pelo §7 do
# projeto final, para o GRUPO 9.
#
# Parametros fixos do grupo 9 (§9):
#   conjunto = amzn (books_200M_uint32, uint32 -> --key-bytes 4)
#   theta    = 1.2
#   mix      = 35:35:30 (I:D:S)
#   range_agg= contagem (count)
#   ordem    = shuffle
#   seed     = 9
#
# CALIBRACAO DE ESCALA (descoberta empirica, ver relatorio):
#   Com o mix 35:35:30, insercoes e remocoes se equilibram e a arvore vive em
#   "churn" permanente. O tamanho de pico em regime estacionario e ~2% do
#   --universe. Logo, para um n-alvo de chaves vivas usamos:
#
#       --universe ~= 50 * n_alvo
#
#   Isso limita o n maximo: n=1e6 exige universe=5e7 (cabe nos 200M do amzn),
#   mas n=1e7 exigiria universe=5e8 > dataset inteiro. O teto e n ~= 1e6.
#
# Uso:  bash run_experiments.sh
# Saida: results/metrics.csv  (consumido por plots.py)
# ---------------------------------------------------------------------------
set -euo pipefail

KEYS="data/books_200M_uint32"
KEYBYTES=4
SEED=9
THETA=1.2
MIX="35:35:30"
AGG="count"
ORDER="shuffle"

OUTDIR="results"
TRACEDIR="traces"
METRICS="$OUTDIR/metrics.csv"

mkdir -p "$OUTDIR" "$TRACEDIR"
rm -f "$METRICS"

if [ ! -f "$KEYS" ]; then
    echo "ERRO: dataset nao encontrado em $KEYS"
    echo "Baixe com: wget -O $KEYS 'https://zenodo.org/records/15240501/files/books_200M_uint32?download=1'"
    exit 1
fi

# fator empirico: universe necessario para atingir n chaves vivas de pico
FATOR=50

echo "############################################################"
echo "# GRUPO 9 | amzn | theta=$THETA | mix=$MIX | agg=$AGG | $ORDER | seed=$SEED"
echo "############################################################"
echo ""

# ---------------------------------------------------------------------------
# EXPERIMENTO 1 (§7.1) -- ESCALA: n em 5 ordens de grandeza
#   Tambem roda a LINHA DE BASE (§7.5) em cada escala, para achar o ponto
#   de cruzamento treap x lista ordenada.
# ---------------------------------------------------------------------------
echo "=== [1/4] ESCALA (§7.1) + LINHA DE BASE (§7.5) ==="
for N in 100 1000 10000 100000 1000000; do
    UNIVERSE=$(( N * FATOR ))
    OPS=$(( UNIVERSE * 2 ))
    MAXLOAD=$(( UNIVERSE * 2 ))
    TAG="scale_n${N}"

    echo ""
    echo "--- n_alvo=$N  (universe=$UNIVERSE, ops=$OPS) ---"

    python3 gen_workload.py generate \
        --keys "$KEYS" --format sosd --key-bytes $KEYBYTES \
        --max-load $MAXLOAD \
        --out "$TRACEDIR/$TAG" --ops $OPS \
        --universe $UNIVERSE --mix "$MIX" --theta $THETA --seed $SEED \
        --insert-order $ORDER

    # treap
    python3 runner.py --trace "$TRACEDIR/$TAG.trace" --out "$TRACEDIR/$TAG.treap.out" \
        --struct treap --agg $AGG --seed $SEED --metrics "$METRICS"
    python3 gen_workload.py verify \
        --expected "$TRACEDIR/$TAG.expected" --candidate "$TRACEDIR/$TAG.treap.out"

    # baseline (lista ordenada) -- so ate 1e5; acima disso o O(n) fica proibitivo
    if [ "$N" -le 100000 ]; then
        python3 runner.py --trace "$TRACEDIR/$TAG.trace" --out "$TRACEDIR/$TAG.base.out" \
            --struct baseline --agg $AGG --seed $SEED --metrics "$METRICS"
        python3 gen_workload.py verify \
            --expected "$TRACEDIR/$TAG.expected" --candidate "$TRACEDIR/$TAG.base.out"
    else
        echo "    (baseline pulada em n=$N: O(n) por operacao inviabiliza)"
    fi

    rm -f "$TRACEDIR/$TAG.trace" "$TRACEDIR/$TAG.expected" \
          "$TRACEDIR/$TAG.treap.out" "$TRACEDIR/$TAG.base.out"
done

# ---------------------------------------------------------------------------
# EXPERIMENTO 2 (§7.2) -- SENSIBILIDADE AO ENVIESAMENTO ZIPFIANO
#   theta em {0.0, 0.6, 0.99, 1.2}; n fixo para isolar o efeito do theta.
# ---------------------------------------------------------------------------
echo ""
echo "=== [2/4] SENSIBILIDADE AO THETA (§7.2) ==="
N=100000
UNIVERSE=$(( N * FATOR ))
OPS=$(( UNIVERSE * 2 ))
for TH in 0.0 0.6 0.99 1.2; do
    TAG="theta_${TH}"
    echo ""
    echo "--- theta=$TH  (n_alvo=$N) ---"

    python3 gen_workload.py generate \
        --keys "$KEYS" --format sosd --key-bytes $KEYBYTES \
        --max-load $(( UNIVERSE * 2 )) \
        --out "$TRACEDIR/$TAG" --ops $OPS \
        --universe $UNIVERSE --mix "$MIX" --theta $TH --seed $SEED \
        --insert-order $ORDER

    python3 runner.py --trace "$TRACEDIR/$TAG.trace" --out "$TRACEDIR/$TAG.out" \
        --struct treap --agg $AGG --seed $SEED --metrics "$METRICS"
    python3 gen_workload.py verify \
        --expected "$TRACEDIR/$TAG.expected" --candidate "$TRACEDIR/$TAG.out"

    rm -f "$TRACEDIR/$TAG.trace" "$TRACEDIR/$TAG.expected" "$TRACEDIR/$TAG.out"
done

# ---------------------------------------------------------------------------
# EXPERIMENTO 3 (§7.3) -- CASO PATOLOGICO: shuffle x sorted
#   Roda a TREAP e tambem uma BST SEM BALANCEAMENTO, para evidenciar a
#   degeneracao que o balanceamento evita.
# ---------------------------------------------------------------------------
echo ""
echo "=== [3/4] CASO PATOLOGICO: shuffle x sorted (§7.3) ==="
N=10000
UNIVERSE=$(( N * FATOR ))
OPS=$(( UNIVERSE * 2 ))
for ORD in shuffle sorted; do
    TAG="order_${ORD}"
    echo ""
    echo "--- insert-order=$ORD  (n_alvo=$N) ---"

    python3 gen_workload.py generate \
        --keys "$KEYS" --format sosd --key-bytes $KEYBYTES \
        --max-load $(( UNIVERSE * 2 )) \
        --out "$TRACEDIR/$TAG" --ops $OPS \
        --universe $UNIVERSE --mix "$MIX" --theta $THETA --seed $SEED \
        --insert-order $ORD

    python3 runner.py --trace "$TRACEDIR/$TAG.trace" --out "$TRACEDIR/$TAG.out" \
        --struct treap --agg $AGG --seed $SEED --metrics "$METRICS"
    python3 gen_workload.py verify \
        --expected "$TRACEDIR/$TAG.expected" --candidate "$TRACEDIR/$TAG.out"

    rm -f "$TRACEDIR/$TAG.trace" "$TRACEDIR/$TAG.expected" "$TRACEDIR/$TAG.out"
done

echo ""
echo "=== [4/4] CONCLUIDO ==="
echo "Metricas acumuladas em: $METRICS"
echo ""
echo "Proximo passo:  python3 plots.py --metrics $METRICS --outdir $OUTDIR"
