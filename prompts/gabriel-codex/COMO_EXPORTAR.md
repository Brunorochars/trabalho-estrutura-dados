# Dump de prompts — Gabriel Ortiz (Codex)

Esta pasta reúne as sessões de Gabriel com o GitHub Copilot / Codex usadas
como auxílio no projeto. O §10 do enunciado exige um dump de TODOS os chats,
"de maneira organizada", com avaliação focada no "raciocínio e na iteração
demonstrados, não no volume".

---

## Como exportar do Copilot/Codex

### Opção A — Você tem acesso ao histórico (recomendado)

No GitHub Copilot Chat (VS Code ou github.com):
1. Abra o painel de chat
2. Localize as conversas relacionadas ao projeto
3. Copie o conteúdo (Ctrl+A no painel) ou use "Export" se disponível
4. Cole em um arquivo `.md` aqui, seguindo o formato abaixo

### Opção B — Reconstrução de memória

Se não tiver o histórico salvo, preencha um arquivo por sessão respondendo
às perguntas do template abaixo. O professor avalia o raciocínio, não a
transcrição literal.

---

## Formato esperado para cada sessão

Crie um arquivo por sessão: `sessao_YYYY-MM-DD.md`

```markdown
# Sessão YYYY-MM-DD — Copilot/Codex — Gabriel Ortiz

## Objetivo
O que você estava tentando resolver nesta sessão?

## Interações principais

### 1. [Título do que foi feito]

**Prompt:** "transcrição ou resumo do que você pediu"

**Raciocínio:** por que você pediu isso? que problema estava tentando
resolver? que alternativas considerou antes de pedir?

**Resultado:** o que o Codex fez/sugeriu? você aceitou, modificou ou
rejeitou? por quê?

---

### 2. [Próxima interação]
...
```

---

## Sessões a documentar (referência)

Documente todas as sessões em que o Codex ajudou com qualquer parte do
projeto. Exemplos do que pode ter ocorrido:

- Implementação ou revisão de partes da estrutura de dados
- Depuração de erros de execução
- Geração ou ajuste de scripts de experimentos
- Redação ou revisão de documentação
- Pesquisa de APIs, bibliotecas ou comandos

Cada sessão deve ser um arquivo separado nesta pasta.
