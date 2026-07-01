#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
treap.py -- Arvore de busca balanceada aumentada (Treap) com layout de
arrays paralelos, para o projeto final de Estruturas de Dados.

Motivacao do layout (decisao de projeto, defensavel oralmente):
  Em vez de um no ser um objeto Python com atributos, cada no e um indice
  inteiro. Todos os campos vivem em listas Python paralelas indexadas por
  esse inteiro:

      key[i]   chave
      prio[i]  prioridade aleatoria (heap invariant -> balanceamento)
      lft[i]   indice do filho esquerdo   (-1 = vazio)
      rgt[i]   indice do filho direito    (-1 = vazio)
      sz[i]    tamanho da subarvore enraizada em i   (campo aumentado)
      ag[i]    agregado da subarvore enraizada em i   (campo aumentado)

  Isso da localidade muito melhor (listas contiguas) e evita criar/destruir
  objetos por operacao. A rotacao vira troca de indices.

Invariantes:
  (BST)  key[lft[i]] < key[i] < key[rgt[i]]  (chaves distintas)
  (HEAP) prio[i] <= prio[filho]              (min-heap nas prioridades)
  (AUG)  para todo no i:
             sz[i] = 1 + sz[lft[i]] + sz[rgt[i]]
             ag[i] = combine(val(key[i]), ag[lft[i]], ag[rgt[i]])
         onde ag[-1] = identidade da operacao.

  A rotacao viola (AUG) temporariamente para os dois nos envolvidos; _pull(i)
  recomputa sz[i] e ag[i] a partir dos filhos e e chamada, na ordem certa
  (primeiro o no que desce, depois o que sobe), antes de qualquer consulta.
  Esse e o argumento informal de corretude sob rotacao.

Operacoes exigidas (§3): insert, delete, search, rank, select, range_agg.
"""

import random

INF = float("inf")


# ---------------------------------------------------------------------------
# Agregacoes plugaveis (§9 -- varia por grupo: soma, contagem, minimo, maximo)
# ---------------------------------------------------------------------------
def make_agg(kind):
    """Retorna (identity, val_fn, combine_fn) para a operacao pedida."""
    if kind == "sum":
        return 0, (lambda k: k), (lambda a, b: a + b)
    if kind == "count":
        return 0, (lambda k: 1), (lambda a, b: a + b)
    if kind == "min":
        return INF, (lambda k: k), (lambda a, b: a if a < b else b)
    if kind == "max":
        return -INF, (lambda k: k), (lambda a, b: a if a > b else b)
    raise ValueError(f"agg desconhecida: {kind!r} (use sum|count|min|max)")


class Treap:
    def __init__(self, agg="sum", seed=42, capacity_hint=1024):
        self.identity, self._val, self._combine = make_agg(agg)
        self.agg_kind = agg

        self.key = [0] * capacity_hint
        self.prio = [0.0] * capacity_hint
        self.lft = [-1] * capacity_hint
        self.rgt = [-1] * capacity_hint
        self.sz = [0] * capacity_hint
        self.ag = [self.identity] * capacity_hint

        self.root = -1
        self.n_nodes = 0
        self._next = 0
        self._free = []
        self._rng = random.Random(seed)
        self._rand = self._rng.random     # metodo ligado, evita lookup por no

        self.rotations = 0   # instrumentacao (§7)

    # -- alocacao ------------------------------------------------------------
    def _new_node(self, k):
        if self._free:
            i = self._free.pop()
        else:
            i = self._next
            self._next += 1
            if i >= len(self.key):
                grow = len(self.key)
                self.key.extend([0] * grow)
                self.prio.extend([0.0] * grow)
                self.lft.extend([-1] * grow)
                self.rgt.extend([-1] * grow)
                self.sz.extend([0] * grow)
                self.ag.extend([self.identity] * grow)
        self.key[i] = k
        self.prio[i] = self._rand()
        self.lft[i] = -1
        self.rgt[i] = -1
        self.sz[i] = 1
        self.ag[i] = self._val(k)
        return i

    # -- campo aumentado -----------------------------------------------------
    def _pull(self, i):
        l, r = self.lft[i], self.rgt[i]
        s = 1
        a = self._val(self.key[i])
        if l != -1:
            s += self.sz[l]
            a = self._combine(a, self.ag[l])
        if r != -1:
            s += self.sz[r]
            a = self._combine(a, self.ag[r])
        self.sz[i] = s
        self.ag[i] = a

    # -- rotacoes ------------------------------------------------------------
    def _rot_right(self, i):
        l = self.lft[i]
        self.lft[i] = self.rgt[l]
        self.rgt[l] = i
        self._pull(i)      # i desceu: recomputa primeiro
        self._pull(l)      # l subiu: recomputa depois
        self.rotations += 1
        return l

    def _rot_left(self, i):
        r = self.rgt[i]
        self.rgt[i] = self.lft[r]
        self.lft[r] = i
        self._pull(i)
        self._pull(r)
        self.rotations += 1
        return r

    # -- insert --------------------------------------------------------------
    def insert(self, k):
        self.root = self._insert(self.root, k)

    def _insert(self, i, k):
        if i == -1:
            self.n_nodes += 1
            return self._new_node(k)
        ki = self.key[i]
        if k == ki:
            return i                       # ja presente: no-op
        if k < ki:
            self.lft[i] = self._insert(self.lft[i], k)
            if self.prio[self.lft[i]] < self.prio[i]:
                i = self._rot_right(i)
            else:
                self._pull(i)
        else:
            self.rgt[i] = self._insert(self.rgt[i], k)
            if self.prio[self.rgt[i]] < self.prio[i]:
                i = self._rot_left(i)
            else:
                self._pull(i)
        return i

    # -- delete --------------------------------------------------------------
    def delete(self, k):
        self.root = self._delete(self.root, k)

    def _delete(self, i, k):
        if i == -1:
            return -1                      # ausente: no-op
        ki = self.key[i]
        if k < ki:
            self.lft[i] = self._delete(self.lft[i], k)
            self._pull(i)
        elif k > ki:
            self.rgt[i] = self._delete(self.rgt[i], k)
            self._pull(i)
        else:
            i = self._delete_root_of(i)
        return i

    def _delete_root_of(self, i):
        """Remove o no i (raiz da subarvore atual) e devolve a nova raiz.
        Estrategia treap: enquanto i tiver dois filhos, rotaciona o filho de
        menor prioridade para cima (empurrando i para baixo) ate i virar folha
        ou ter um so filho; ai desconecta em O(1)."""
        while True:
            l, r = self.lft[i], self.rgt[i]
            if l == -1 and r == -1:
                self._free.append(i)
                self.n_nodes -= 1
                return -1
            if l == -1:
                self._free.append(i)
                self.n_nodes -= 1
                return r
            if r == -1:
                self._free.append(i)
                self.n_nodes -= 1
                return l
            # dois filhos: sobe o de menor prioridade
            if self.prio[l] < self.prio[r]:
                # rotaciona a direita: l sobe, i desce para rgt[l].
                # depois continuamos deletando i, agora filho direito de l.
                new_sub = self._rot_right(i)          # new_sub == l (ja com _pull)
                # i agora e rgt[new_sub]; recorre nesse lado e reancora
                self.rgt[new_sub] = self._delete_root_of(self.rgt[new_sub])
                self._pull(new_sub)
                return new_sub
            else:
                new_sub = self._rot_left(i)           # new_sub == r
                self.lft[new_sub] = self._delete_root_of(self.lft[new_sub])
                self._pull(new_sub)
                return new_sub

    # -- search --------------------------------------------------------------
    def search(self, k):
        i = self.root
        while i != -1:
            ki = self.key[i]
            if k == ki:
                return True
            i = self.lft[i] if k < ki else self.rgt[i]
        return False

    # -- rank(k): numero de chaves < k ---------------------------------------
    def rank(self, k):
        i = self.root
        r = 0
        while i != -1:
            ki = self.key[i]
            if k <= ki:
                i = self.lft[i]
            else:
                lft = self.lft[i]
                r += 1 + (self.sz[lft] if lft != -1 else 0)
                i = self.rgt[i]
        return r

    # -- select(idx): a idx-esima menor chave (0-based) ----------------------
    def select(self, idx):
        n = self.sz[self.root] if self.root != -1 else 0
        if idx < 0 or idx >= n:
            raise IndexError("select fora do intervalo")
        i = self.root
        while True:
            lft = self.lft[i]
            lsize = self.sz[lft] if lft != -1 else 0
            if idx < lsize:
                i = lft
            elif idx == lsize:
                return self.key[i]
            else:
                idx -= lsize + 1
                i = self.rgt[i]

    # -- range_agg(a, b): agregado das chaves em [a, b] ----------------------
    def range_agg(self, a, b):
        if a > b:
            return self.identity
        return self._range(self.root, a, b, -INF, INF)

    def _range(self, i, a, b, lo, hi):
        """lo/hi = limites da subarvore i (implicitos pela posicao na BST).
        Se [lo,hi] esta contido em [a,b], usa ag[i] pronto -> O(log n) total."""
        if i == -1:
            return self.identity
        if b < lo or hi < a:
            return self.identity           # subarvore fora do intervalo
        if a <= lo and hi <= b:
            return self.ag[i]              # subarvore totalmente contida
        ki = self.key[i]
        res = self.identity
        left = self._range(self.lft[i], a, b, lo, ki - 1)
        res = self._combine(res, left) if left != self.identity else res
        if a <= ki <= b:
            res = self._combine(res, self._val(ki))
        right = self._range(self.rgt[i], a, b, ki + 1, hi)
        res = self._combine(res, right) if right != self.identity else res
        return res

    # -- medicao -------------------------------------------------------------
    def height(self):
        if self.root == -1:
            return 0
        stack = [(self.root, 1)]
        h = 0
        while stack:
            i, d = stack.pop()
            if d > h:
                h = d
            l, r = self.lft[i], self.rgt[i]
            if l != -1:
                stack.append((l, d + 1))
            if r != -1:
                stack.append((r, d + 1))
        return h

    def __len__(self):
        return self.n_nodes
