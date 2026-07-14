# Dump de prompts (§10) — Grupo 9

Esta pasta reúne o histórico de interações com assistentes de IA usados como
ferramenta de auxílio para a parte de código do projeto, conforme permitido
pelo enunciado (§2, §11): *"o uso de ferramentas de auxílio (incluindo modelos
de linguagem) é permitido para a parte de código"*, com a avaliação recaindo
sobre o **raciocínio e a iteração demonstrados**, não sobre o volume.

## Membros e ferramentas

| Membro | Ferramenta | Pasta |
|---|---|---|
| Bruno Rocha | Claude Code (Anthropic) | [`bruno-claude/`](bruno-claude/) |
| Andreus Dean Vargas | Claude Code (Anthropic) | [`andreus-claude/`](andreus-claude/) |
| Gabriel Ortiz | GitHub Copilot / Codex | [`gabriel-codex/`](gabriel-codex/) |

---

## Bruno Rocha — Claude Code

### [`sessao_inicial_nao_capturada.md`](bruno-claude/sessao_inicial_nao_capturada.md)
Declaração formal da sessão inicial (anterior a 2026-07-12), na qual foram
produzidos `treap.py`, a versão inicial de `runner.py` e o `README.md`. A
sessão ocorreu antes de o grupo estruturar esta pasta para registro. As
decisões técnicas tomadas nessa sessão estão documentadas em
`JUSTIFICATIVA.md`.

### [`sessao_2026-07-12.md`](bruno-claude/sessao_2026-07-12.md)
Sessão que auditou o repositório contra o enunciado (§1–§11), identificou
lacunas (escala com menos de 4 ordens de grandeza, gráficos não gerados,
entregáveis §8/§10 ausentes), adicionou rastreio de `peak_size`/`peak_height`
ao `runner.py`, criou `run_experiments.sh` e `plots.py`, resolveu autenticação
SSH, e executou as correções por ordem de urgência.

---

## Andreus Dean Vargas — Claude Code

### [`sessao_2026-07-14.md`](andreus-claude/sessao_2026-07-14.md)
Primeira sessão de Andreus. Leitura completa do enunciado, identificação dos
parâmetros do grupo 9, inventário e auditoria técnica do repositório
(corretude dos invariantes da treap, comportamento de `_range`, profundidade
de recursão), identificação do gap nos prompts, e execução da reorganização
desta pasta para estrutura multi-membro.

---

## Gabriel Ortiz — GitHub Copilot / Codex

As sessões de Gabriel serão adicionadas a [`gabriel-codex/`](gabriel-codex/)
conforme ele as exportar ou reconstruir. Ver
[`gabriel-codex/COMO_EXPORTAR.md`](gabriel-codex/COMO_EXPORTAR.md) para
instruções de formato.

---

## Observação sobre a avaliação (§10)

O §10 avalia a **qualidade do raciocínio e da iteração** nas interações com
IA — não o volume de texto. Os arquivos nesta pasta mostram, em cada sessão:
- o que o membro estava tentando resolver (prompt)
- por que aquela abordagem foi escolhida (raciocínio)
- o que foi aceito, modificado ou rejeitado (resultado)

Perguntas do tipo "faça X" sem explicar *por que* têm menos valor avaliativo
do que perguntas que demonstram que o membro entendeu o problema antes de
pedir ajuda.
