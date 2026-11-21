# Estudio STL (rascunho)

Ferramenta do Mimoverso: você pede um bichinho em palavras e recebe um arquivo **STL** que a impressora usa. *Rascunho inicial; a Bia e a IA dela vão continuar daqui.*

## A ideia em uma frase
"Quero um sapinho com chifre, 6 cm" → a IA escreve um programa curto que desenha o bicho com formas arredondadas → sai um `.stl` fechado, com as medidas reais conferidas e três imagens de prévia. "Maior" ou "menor" é trocar **um número** (`SIZE_MM`).

## Como começar (para a Bia, passo a passo)
1. Abra esta pasta no Claude Code e peça: "leia o CLAUDE.md e me explique o plano em 3 linhas".
2. Peça para criar o ambiente Python e instalar `requirements.txt`.
3. Rode o exemplo: `python examples/sapinho.py`, depois `python -m studio.check out/sapinho.stl`.
4. **Abra `out/sapinho.stl` no Bambu Studio.** É o teste que decide: fatia sem aviso? Quanto tempo e quanto filamento?
5. Peça um bicho novo, copiando o exemplo. Um de cada vez.

## Estilos (mesmo bicho, p�blicos diferentes)
`python examples/sapinho.py --style cute --size 60` (fofo) ou `--style edgy` (pontudo, mal-humorado). Um estilo � s� um conjunto de n�meros em `STYLES`; novos estilos s�o novas linhas. `--size 90` muda o tamanho.

## Etapas
| # | O que | Pronto quando |
|---|---|---|
| 1 | **Texto para STL** (começamos aqui) | 3 bichos diferentes, cada um com check "malha fechada" e fatiado no Bambu Studio sem erro |
| 2 | **Abrir um STL existente** e mudar tamanho e partes | o STL de outra pessoa é aberto, medido e ajustado por pedido |
| 3 | Uma tela simples (digitar o pedido, ver o bicho) | a Bia usa sem abrir o terminal |

## O que já está provado e o que não
- Provado: o exemplo gera STL de malha fechada, um corpo só, base reta (saída do `studio.check`, 20/11/2026), e muda de 6 para 9 cm trocando o número.
- **Não provado:** que fatia e imprime bem (nunca foi aberto num fatiador), e que o resultado é fofo o bastante para vender. Isso é com a Bia e o Bruno.

## Estrutura
`studio/` (formas, conferência, prévia) · `examples/` (o sapinho) · `CLAUDE.md` (instruções para a IA da Bia) · `requirements.txt`.
Código e nomes em inglês; textos para a Bia em português.

## Escultura suave (`studio/clay.py`)
`python examples/sapinho_fofo.py --size 60` gera o sapinho em "massinha": um volume único com junções suaves e malha fina (passo de 0,3 mm), sem serrilhado nas emendas. As proporções (cabeça, olhos, chifres, bochechas, sorriso) são números no topo do arquivo.

## Antes de imprimir
`python -m studio.printability out/<arquivo>.stl` mostra a área de saliências (acima de 45° pede suporte), a área de base e uma estimativa de peso. O exemplo já sai com `self_support`, que preenche por baixo do queixo para imprimir sem suporte (`--raw` desliga). É estimativa: o fatiador tem a palavra final.
