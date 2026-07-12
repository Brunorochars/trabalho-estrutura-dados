#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
runner.py -- Le um .trace do gen_workload.py, executa as operacoes na
estrutura escolhida (treap aumentada ou baseline ingenua) e:

  1) emite <chave> <FOUND|NOT_FOUND> por operacao S (para o oraculo verify);
  2) coleta metricas por tipo de operacao (I/D/S): media, p50, p99, alem de
     altura final e numero de rotacoes -- material do estudo empirico (§7).

Uso:
  python3 runner.py --trace g.trace --out g.out \
      --struct treap --agg min --seed 3 [--metrics g_metrics.csv]

O parametro --agg deve casar com o range_agg do grupo (§9). Para a corretude
do oraculo (que so verifica S), a agregacao e irrelevante; ela existe para os
experimentos de range_agg e para manter o campo aumentado exercitado.
"""

import argparse
import sys
import time
import bisect

from treap import Treap


# ---------------------------------------------------------------------------
# Baseline ingenua (§7 item 5): BST sem balanceamento OU lista ordenada.
# Aqui: lista ordenada com bisect -> busca O(log n), insert/delete O(n).
# Mesma interface do runner para o ponto de cruzamento ser justo (mesma
# linguagem, mesmo overhead de interpretador).
# ---------------------------------------------------------------------------
class SortedListBaseline:
    def __init__(self, **_):
        self.a = []
        self.rotations = 0
    def insert(self, k):
        i = bisect.bisect_left(self.a, k)
        if i == len(self.a) or self.a[i] != k:
            self.a.insert(i, k)
    def delete(self, k):
        i = bisect.bisect_left(self.a, k)
        if i < len(self.a) and self.a[i] == k:
            self.a.pop(i)
    def search(self, k):
        i = bisect.bisect_left(self.a, k)
        return i < len(self.a) and self.a[i] == k
    def height(self):
        return len(self.a)   # "profundidade" degenerada, so para logging
    def __len__(self):
        return len(self.a)


def percentile(sorted_ns, q):
    if not sorted_ns:
        return 0.0
    idx = int(q * (len(sorted_ns) - 1))
    return sorted_ns[idx]


def run(args):
    if args.struct == "treap":
        ds = Treap(agg=args.agg, seed=args.seed)
    elif args.struct == "baseline":
        ds = SortedListBaseline()
    else:
        sys.exit(f"struct desconhecida: {args.struct}")

    t_ins, t_del, t_srch = [], [], []
    n_i = n_d = n_s = 0
    peak_size = 0          # maior n atingido (eixo x real dos graficos de escala)
    peak_height = 0        # maior altura atingida (evidencia do balanceamento)
    sample_every = 1000    # amostra altura periodicamente (height() e O(n))

    out = open(args.out, "w")
    perf = time.perf_counter_ns

    with open(args.trace) as ft:
        for line in ft:
            if not line or line[0] == "#":
                continue
            op = line[0]
            k = int(line[2:])
            if op == "I":
                t0 = perf(); ds.insert(k); t_ins.append(perf() - t0); n_i += 1
                cur = len(ds)
                if cur > peak_size:
                    peak_size = cur
                if args.struct == "treap" and n_i % sample_every == 0:
                    h = ds.height()
                    if h > peak_height:
                        peak_height = h
            elif op == "D":
                t0 = perf(); ds.delete(k); t_del.append(perf() - t0); n_d += 1
            elif op == "S":
                t0 = perf(); found = ds.search(k); dt = perf() - t0
                t_srch.append(dt); n_s += 1
                out.write(f"{k} {'FOUND' if found else 'NOT_FOUND'}\n")
    out.close()

    height_final = ds.height() if args.struct == "treap" else -1

    def stats(name, ts):
        if not ts:
            return f"{name}: (nenhuma)"
        s = sorted(ts)
        mean = sum(ts) / len(ts)
        return (f"{name}: n={len(ts)} mean={mean:.1f}ns "
                f"p50={percentile(s,0.50):.1f}ns p99={percentile(s,0.99):.1f}ns")

    sys.stderr.write("[runner] " + stats("I", t_ins) + "\n")
    sys.stderr.write("[runner] " + stats("D", t_del) + "\n")
    sys.stderr.write("[runner] " + stats("S", t_srch) + "\n")
    sys.stderr.write(f"[runner] estrutura={args.struct} agg={args.agg} "
                     f"pico_n={peak_size} pico_altura={peak_height} "
                     f"altura_final={height_final} rotacoes={getattr(ds,'rotations',0)} "
                     f"tamanho_final={len(ds)}\n")

    if args.metrics:
        # uma linha por tipo de operacao, formato longo para o plots.py
        import os
        header = not os.path.exists(args.metrics)
        with open(args.metrics, "a") as fm:
            if header:
                fm.write("struct,agg,seed,trace,op,n_ops,mean_ns,p50_ns,p99_ns,"
                         "peak_n,peak_height,height_final,rotations,size_final\n")
            for name, ts in (("I", t_ins), ("D", t_del), ("S", t_srch)):
                if not ts:
                    continue
                s = sorted(ts)
                fm.write(f"{args.struct},{args.agg},{args.seed},{args.trace},"
                         f"{name},{len(ts)},{sum(ts)/len(ts):.3f},"
                         f"{percentile(s,0.50):.3f},{percentile(s,0.99):.3f},"
                         f"{peak_size},{peak_height},{height_final},"
                         f"{getattr(ds,'rotations',0)},{len(ds)}\n")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--struct", choices=["treap", "baseline"], default="treap")
    p.add_argument("--agg", choices=["sum", "count", "min", "max"], default="sum")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--metrics", help="arquivo CSV para acumular metricas (opcional)")
    run(p.parse_args())


if __name__ == "__main__":
    main()
