# Dump de prompts (§10)

Esta pasta reúne o histórico de interações com o assistente de IA (Claude Code)
usado como ferramenta de auxílio para a parte de código do projeto, conforme
permitido pelo enunciado (§2, §11): *"o uso de ferramentas de auxílio (incluindo
modelos de linguagem) é permitido para a parte de código"*, com a avaliação
recaindo sobre o **raciocínio e a iteração demonstrados**, não sobre o volume.

## Arquivos

- [`sessao_2026-07-12.md`](sessao_2026-07-12.md) — sessão que: (1) auditou o
  repositório contra o enunciado; (2) adicionou rastreio de `peak_size`/`peak_height`
  ao `runner.py`; (3) criou `run_experiments.sh` e `plots.py`; (4) resolveu a
  autenticação SSH para push no GitHub; (5) corrigiu o `.gitignore`; (6) revisou
  o enunciado seção a seção e identificou lacunas (escala com menos de 4 ordens
  de grandeza, gráficos não gerados, README com comando Docker quebrado,
  entregáveis §8/§10 ausentes); (7) executou as correções por ordem de urgência.

## Observação importante

O commit inicial do repositório (`983367e "Treap aumentada, runner, gen_workload,
Dockerfile, README e gitignore"`) foi produzido em uma sessão anterior, cujo
histórico de prompts **não está capturado aqui** porque não fez parte desta
conversa. Se essa sessão anterior existir em outra conversa salva, seu dump
precisa ser adicionado a esta pasta antes da entrega — caso contrário, declarar
explicitamente no relatório que o núcleo da treap (`treap.py`) e o gerador de
carga (`gen_workload.py`) foram produzidos com auxílio de IA em uma sessão não
registrada, para cumprir a regra do §11 ("identifique claramente, no relatório,
qualquer parte cuja autoria não seja do grupo").
