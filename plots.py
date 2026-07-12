#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plots.py -- Gera os graficos do estudo empirico (§7) a partir do metrics.csv
produzido por run_experiments.sh.

Graficos gerados:
  1. escala.png          -- tempo/op (mean, p50, p99) x n, em escala log-log,
                            com a curva teorica O(log n) sobreposta (§7.1, §7.4)
  2. baseline.png        -- treap x lista ordenada, com o ponto de cruzamento (§7.5)
  3. theta.png           -- sensibilidade ao enviesamento Zipfiano (§7.2)
  4. patologico.png      -- shuffle x sorted: tempo e altura (§7.3)
  5. rotacoes.png        -- rotacoes por operacao x n (custo amortizado)

Uso:
  python3 plots.py --metrics results/metrics.csv --outdir results
"""

import argparse
import os
import csv
import math
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")          # backend sem display (roda no container)
import matplotlib.pyplot as plt


def load(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            for k in ("n_ops", "peak_n", "peak_height", "height_final",
                      "rotations", "size_final", "seed"):
                r[k] = int(r[k])
            for k in ("mean_ns", "p50_ns", "p99_ns"):
                r[k] = float(r[k])
            rows.append(r)
    return rows


def sel(rows, **kw):
    out = rows
    for k, v in kw.items():
        out = [r for r in out if r[k] == v]
    return out


def tag_of(trace):
    return os.path.basename(trace).replace(".trace", "")


# ---------------------------------------------------------------------------
# 1. ESCALA + TEORIA x PRATICA  (§7.1, §7.4)
# ---------------------------------------------------------------------------
def plot_escala(rows, outdir):
    esc = [r for r in rows if tag_of(r["trace"]).startswith("scale_")
           and r["struct"] == "treap"]
    if not esc:
        print("  [skip] escala: sem dados")
        return

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, op, titulo in zip(axes, ["I", "D", "S"],
                              ["insert(k)", "delete(k)", "search(k)"]):
        d = sorted(sel(esc, op=op), key=lambda r: r["peak_n"])
        if not d:
            continue
        ns = [r["peak_n"] for r in d]
        ax.plot(ns, [r["mean_ns"] for r in d], "o-", label="media", lw=2)
        ax.plot(ns, [r["p50_ns"] for r in d], "s--", label="p50", lw=1.5)
        ax.plot(ns, [r["p99_ns"] for r in d], "^:", label="p99", lw=1.5)

        # curva teorica O(log n), ancorada no primeiro ponto medido
        if len(ns) >= 2:
            n0, t0 = ns[0], d[0]["mean_ns"]
            teo = [t0 * (math.log2(max(n, 2)) / math.log2(max(n0, 2))) for n in ns]
            ax.plot(ns, teo, "k-.", alpha=0.6, lw=1.5, label="O(log n) teorico")

        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("n (chaves vivas, pico)")
        ax.set_ylabel("tempo por operacao (ns)")
        ax.set_title(titulo)
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)

    fig.suptitle("Escala: tempo por operacao x n  |  Grupo 9 (amzn, theta=1.2, "
                 "mix 35:35:30)", fontsize=12)
    fig.tight_layout()
    p = os.path.join(outdir, "escala.png")
    fig.savefig(p, dpi=130); plt.close(fig)
    print(f"  [ok] {p}")


# ---------------------------------------------------------------------------
# 2. LINHA DE BASE + PONTO DE CRUZAMENTO  (§7.5)
# ---------------------------------------------------------------------------
def plot_baseline(rows, outdir):
    esc = [r for r in rows if tag_of(r["trace"]).startswith("scale_")]
    if not esc:
        print("  [skip] baseline: sem dados")
        return

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, op, titulo in zip(axes, ["I", "D", "S"],
                              ["insert(k)", "delete(k)", "search(k)"]):
        for struct, marker, cor in (("treap", "o-", "tab:blue"),
                                    ("baseline", "s--", "tab:red")):
            d = sorted(sel(esc, op=op, struct=struct), key=lambda r: r["peak_n"])
            if not d:
                continue
            ax.plot([r["peak_n"] for r in d], [r["mean_ns"] for r in d],
                    marker, color=cor, lw=2,
                    label="treap" if struct == "treap" else "lista ordenada")

        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("n (chaves vivas, pico)")
        ax.set_ylabel("tempo medio por operacao (ns)")
        ax.set_title(titulo)
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=9)

    fig.suptitle("Linha de base: treap aumentada x lista ordenada  "
                 "(procure o ponto de cruzamento)", fontsize=12)
    fig.tight_layout()
    p = os.path.join(outdir, "baseline.png")
    fig.savefig(p, dpi=130); plt.close(fig)
    print(f"  [ok] {p}")


# ---------------------------------------------------------------------------
# 3. SENSIBILIDADE AO THETA  (§7.2)
# ---------------------------------------------------------------------------
def plot_theta(rows, outdir):
    th = [r for r in rows if tag_of(r["trace"]).startswith("theta_")
          and r["struct"] == "treap"]
    if not th:
        print("  [skip] theta: sem dados")
        return

    def theta_val(r):
        return float(tag_of(r["trace"]).split("_", 1)[1])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    for op, marker, titulo in (("I", "o-", "insert"), ("D", "s-", "delete"),
                               ("S", "^-", "search")):
        d = sorted(sel(th, op=op), key=theta_val)
        if not d:
            continue
        xs = [theta_val(r) for r in d]
        ax1.plot(xs, [r["mean_ns"] for r in d], marker, lw=2, label=f"{titulo} (media)")
        ax2.plot(xs, [r["p99_ns"] for r in d], marker, lw=2, label=f"{titulo} (p99)")

    for ax, t in ((ax1, "Tempo medio por operacao"), (ax2, "Cauda: p99")):
        ax.set_xlabel("theta (enviesamento Zipfiano)")
        ax.set_ylabel("tempo (ns)")
        ax.set_title(t)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
        ax.axvline(1.2, color="tab:red", ls=":", alpha=0.7)
        ax.text(1.2, ax.get_ylim()[1] * 0.95, " grupo 9", color="tab:red",
                fontsize=8, va="top")

    fig.suptitle("Sensibilidade ao enviesamento Zipfiano (theta) | n fixo = 1e5 alvo",
                 fontsize=12)
    fig.tight_layout()
    p = os.path.join(outdir, "theta.png")
    fig.savefig(p, dpi=130); plt.close(fig)
    print(f"  [ok] {p}")


# ---------------------------------------------------------------------------
# 4. CASO PATOLOGICO: shuffle x sorted  (§7.3)
# ---------------------------------------------------------------------------
def plot_patologico(rows, outdir):
    pat = [r for r in rows if tag_of(r["trace"]).startswith("order_")
           and r["struct"] == "treap"]
    if not pat:
        print("  [skip] patologico: sem dados")
        return

    ordens = ["shuffle", "sorted"]
    ops = ["I", "D", "S"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    largura = 0.35
    xs = range(len(ops))
    for i, ordem in enumerate(ordens):
        d = {r["op"]: r for r in pat if tag_of(r["trace"]) == f"order_{ordem}"}
        if not d:
            continue
        vals = [d[o]["mean_ns"] if o in d else 0 for o in ops]
        ax1.bar([x + i * largura for x in xs], vals, largura, label=ordem)

    ax1.set_xticks([x + largura / 2 for x in xs])
    ax1.set_xticklabels(["insert", "delete", "search"])
    ax1.set_ylabel("tempo medio por operacao (ns)")
    ax1.set_title("Tempo: shuffle x sorted")
    ax1.legend(); ax1.grid(True, axis="y", alpha=0.3)

    # altura: a evidencia direta do balanceamento
    alturas, rots, labels = [], [], []
    for ordem in ordens:
        d = [r for r in pat if tag_of(r["trace"]) == f"order_{ordem}"]
        if d:
            alturas.append(d[0]["peak_height"])
            rots.append(d[0]["rotations"])
            labels.append(ordem)
    if alturas:
        n_ref = pat[0]["peak_n"]
        ax2.bar(labels, alturas, color=["tab:blue", "tab:orange"])
        lim = math.log2(max(n_ref, 2))
        ax2.axhline(lim, color="k", ls="--", alpha=0.7,
                    label=f"log2(n) = {lim:.1f} (minimo teorico)")
        ax2.set_ylabel("altura de pico da arvore")
        ax2.set_title(f"Balanceamento: altura de pico (n_pico = {n_ref})")
        ax2.legend(fontsize=9); ax2.grid(True, axis="y", alpha=0.3)
        for i, (a, rr) in enumerate(zip(alturas, rots)):
            ax2.text(i, a, f"  h={a}\n  {rr} rot.", va="bottom", fontsize=8)

    fig.suptitle("Caso patologico: ordem de insercao shuffle x sorted", fontsize=12)
    fig.tight_layout()
    p = os.path.join(outdir, "patologico.png")
    fig.savefig(p, dpi=130); plt.close(fig)
    print(f"  [ok] {p}")


# ---------------------------------------------------------------------------
# 5. ROTACOES POR OPERACAO (custo amortizado do rebalanceamento)
# ---------------------------------------------------------------------------
def plot_rotacoes(rows, outdir):
    esc = [r for r in rows if tag_of(r["trace"]).startswith("scale_")
           and r["struct"] == "treap" and r["op"] == "I"]
    if not esc:
        print("  [skip] rotacoes: sem dados")
        return

    d = sorted(esc, key=lambda r: r["peak_n"])
    ns = [r["peak_n"] for r in d]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # rotacoes totais / (I + D) -> rotacoes por operacao estrutural
    by_trace = defaultdict(dict)
    for r in rows:
        if r["struct"] == "treap":
            by_trace[r["trace"]][r["op"]] = r

    rpo, alturas = [], []
    for r in d:
        t = by_trace[r["trace"]]
        estruturais = t.get("I", {}).get("n_ops", 0) + t.get("D", {}).get("n_ops", 0)
        rpo.append(r["rotations"] / estruturais if estruturais else 0)
        alturas.append(r["peak_height"])

    ax1.plot(ns, rpo, "o-", lw=2, color="tab:purple")
    ax1.set_xscale("log")
    ax1.set_xlabel("n (chaves vivas, pico)")
    ax1.set_ylabel("rotacoes por operacao (I+D)")
    ax1.set_title("Custo amortizado do rebalanceamento")
    ax1.grid(True, which="both", alpha=0.3)

    ax2.plot(ns, alturas, "o-", lw=2, color="tab:green", label="altura medida (pico)")
    ax2.plot(ns, [math.log2(max(n, 2)) for n in ns], "k--", alpha=0.7,
             label="log2(n) (minimo teorico)")
    ax2.plot(ns, [1.39 * math.log2(max(n, 2)) for n in ns], "r:", alpha=0.7,
             label="1.39*log2(n) (esperado p/ treap)")
    ax2.set_xscale("log")
    ax2.set_xlabel("n (chaves vivas, pico)")
    ax2.set_ylabel("altura")
    ax2.set_title("Altura da arvore x limite teorico")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=9)

    fig.suptitle("Rebalanceamento e altura", fontsize=12)
    fig.tight_layout()
    p = os.path.join(outdir, "rotacoes.png")
    fig.savefig(p, dpi=130); plt.close(fig)
    print(f"  [ok] {p}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--metrics", default="results/metrics.csv")
    ap.add_argument("--outdir", default="results")
    a = ap.parse_args()

    if not os.path.exists(a.metrics):
        raise SystemExit(f"metrics nao encontrado: {a.metrics}\n"
                         f"Rode antes:  bash run_experiments.sh")

    os.makedirs(a.outdir, exist_ok=True)
    rows = load(a.metrics)
    print(f"[plots] {len(rows)} linhas lidas de {a.metrics}")

    plot_escala(rows, a.outdir)
    plot_baseline(rows, a.outdir)
    plot_theta(rows, a.outdir)
    plot_patologico(rows, a.outdir)
    plot_rotacoes(rows, a.outdir)

    print("\n[plots] concluido. Lembre-se: identifique no relatorio a MAQUINA, "
          "o ambiente (Docker/WSL) e a metodologia (§7).")


if __name__ == "__main__":
    main()
