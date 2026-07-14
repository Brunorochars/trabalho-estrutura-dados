# Projeto Final - Estruturas de Dados (Treap aumentada)

Núcleo: treap com arrays paralelos, campos aumentados `size` e `agg`
(soma/contagem/mínimo/máximo, plugável via `--agg`). Passa no oráculo
transitivo do `gen_workload.py` para todas as agregações e para o caso
patológico `sorted`.

## Arquivos
- `treap.py`   -- estrutura balanceada aumentada (insert/delete/search/rank/select/range_agg)
- `runner.py`  -- lê .trace, executa, emite .out, coleta métricas (mean/p50/p99, altura, rotações)
- `Dockerfile` -- ambiente Ubuntu 24.04 com numpy/scipy/matplotlib/pandas/zstd/valgrind

## Baixar o dataset (grupo 9: `amzn` / `books_200M_uint32`)
    mkdir -p data
    wget -O data/books_200M_uint32 \
        "https://zenodo.org/records/15240501/files/books_200M_uint32?download=1"
    echo "55845580be1554d82be1c0dda416005c  data/books_200M_uint32" | md5sum -c

O arquivo (~800 MB) nunca é versionado no git (`data/` está no `.gitignore`) —
precisa ser baixado uma vez por máquina. Repositório/instruções completas:
github.com/learnedsystems/SOSD.

## Ambiente (Docker)
    docker build -t ed-projeto .
    docker run -it --rm -v "$PWD/data":/work/data -v "$PWD":/work/src ed-projeto bash
    cd /work/src

Monte `data/` como volume do host (datasets SOSD têm dezenas de GB; nunca na imagem). Os
scripts (`treap.py`, `runner.py`, `gen_workload.py`, `run_experiments.sh`, `plots.py`) ficam
na raiz do repositório, por isso ela é montada inteira em `/work/src`.

## Estudo empírico completo (grupo 9)
    bash run_experiments.sh                                   # gera results/metrics.csv
    python3 plots.py --metrics results/metrics.csv --outdir results   # gera os .png

## Pipeline (substituir PARAMS pelos do seu grupo, §9; --seed = nº do grupo)
    # 1. gerar trace + gabarito a partir das chaves reais
    python3 gen_workload.py generate --keys data/<DATASET> --format sosd --key-bytes 8 \
        --max-load 20000000 --out g --ops 50000000 \
        --universe 10000000 --mix <MIX> --theta <THETA> --seed <GRUPO> --insert-order <ORDEM>

    # 2. executar na treap
    python3 runner.py --trace g.trace --out g.out --struct treap --agg <AGG> --seed <GRUPO> --metrics g_metrics.csv

    # 3. conferir com o oráculo
    python3 gen_workload.py verify --expected g.expected --candidate g.out

    # baseline (ponto de cruzamento, §7 item 5)
    python3 runner.py --trace g.trace --out g_base.out --struct baseline --metrics g_metrics.csv

## Validação rápida (sem dataset)
    python3 gen_workload.py generate --synthetic 200000 --ops 500000 --out t \
        --universe 100000 --mix 40:30:30 --theta 0.99 --seed 3
    python3 runner.py --trace t.trace --out t.out --struct treap --agg min --seed 3
    python3 gen_workload.py verify --expected t.expected --candidate t.out
