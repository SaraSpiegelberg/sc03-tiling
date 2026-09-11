# sc03-tiling

Impressão tileada (mosaico) para a térmica portátil **SC03h-12BC**.

A impressora SC03 imprime tiras de ~5cm (48mm impressíveis) de largura. Este projeto divide qualquer imagem em tiras que cabem na impressora, gera o **layout (mapa mental)** e o **plano de consumo de papel**, e opcionalmente imprime as tiras via wrapper `print-sc03.ps1` (com contador de rolo, corte e bip automáticos).

Depois é só colar as tiras lado a lado com cola fria/bastão — usando a régua pra alinhar.

## Instalação

```bash
cd sc03-tiling
pip install -e .
```

## Uso rápido

```bash
# Dry-run (gera tiras + plano sem imprimir nada)
sc03-tile foto.png --width-cm 10 --height-cm 15 --dry-run

# Gera as tiras e imprime cada uma
sc03-tile foto.png --width-cm 10 --height-cm 15 --print --preset forte

# Imprime também o plano.txt (lista de tiras + consumo)
sc03-tile foto.png --width-cm 10 --height-cm 15 --print --print-plan
```

### Parâmetros

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--width-cm` | obrigatório | Largura desejada da imagem final em cm |
| `--height-cm` | obrigatório | Altura desejada da imagem final em cm |
| `--printable-mm` | 48 | Largura impressível por tira em mm |
| `--overlap-mm` | 2 | Sobreposição entre tiras (facilita colar sem buraco) |
| `--out` | `out` | Pasta de saída das tiras e layouts |
| `--preset` | `forte` | Preset de energia (fraco/medio/forte/max) |
| `--darkness` | 5 | Escurecimento (1–5) |
| `--dry-run` | - | Só gera tiras + plano, não imprime |
| `--print` | - | Imprime as tiras (chama o wrapper) |
| `--print-plan` | - | Imprime o plano.txt como referência |
| `--wrapper` | `print-sc03.ps1` | Caminho do wrapper (ajuste se necessário) |

## Exemplo: foto 10×15cm

```bash
sc03-tile foto.jpg --width-cm 10 --height-cm 15 --out tiles --dry-run
```

Resultado:

```
=== Plano de impressão tileada ===
Imagem: 10.0 x 15.0 cm
Tiras: 3 x ~48.0mm de largura
Cada tira: 15.0cm de comprimento + 1.2cm de corte = 16.2cm
Total estimado de papel: 48.6cm (~0.5m)
```

3 tiras de ~48mm × 15cm, lado a lado → 10×15cm, usando ~50cm de papel.

> **Dica:** pra minimizar consumo, escolha a orientação que coloca o **menor lado** como largura do output (ex.: 10cm de largura × 15cm de altura usa ~50cm; 15cm de largura × 10cm de altura usaria ~42cm mas com 4 tiras).

## Rolo de 3m (30 impressões de 10cm)

Se você tem um rolo grande de papel térmico e quer preparar **rolos de 3m** pra uso diário, faça assim:

### Passo 1: Imprimir a régua de 30cm

```bash
python "C:\Users\Pichau\Desktop\.opencode\tools\timiniprint\gen_ruler.py" "C:\Users\Pichau\Desktop\ruler_30cm.png" 30
```

Imprima pela impressora (com a régua de 30cm no preset medio/max), rasgue e guarde — ela serve como gabarito permanente pra medir.

### Passo 2: Medir e cortar 3m do rolo grande

Com a régua de 30cm na mão:

1. Desenrole o papel térmico do rolo grande.
2. Meça **10 vezes** a régua (10 × 30cm = 300cm = 3m) ao longo da fita, marcando com lápis.
3. Corte na marca com tesoura.
4. Enrole o pedaço de 3m num rolo novo (o furo do rolo precisa caber no eixo da impressora — núcleo ~11-12mm).

Cada rolo de 3m dá **~30 impressões** de 10cm (ou ~27 com a área de corte de 1.2cm, dependendo do conteúdo).

### Passo 3: Registrar no contador

```bash
# Opção A: sabe o tamanho exato
& "C:\Users\Pichau\Desktop\.opencode\tools\timiniprint\print-sc03.ps1" -ResetRoll -RollMeters 3

# Opção B: mediu o diâmetro externo do rolo novo
& "C:\Users\Pichau\Desktop\.opencode\tools\timiniprint\print-sc03.ps1" -ResetRoll -DiameterMM 35 -CoreMM 12 -ThicknessMM 0.06
```

Daqui pra frente, cada impressão desconta automaticamente e o `print.md` mostra quantos impressões restam.

## Saída gerada

| Arquivo | Descrição |
|---------|-----------|
| `tile_01_of_03.png`, `tile_02_of_03.png`, ... | Tiras individuais prontas pra impressão |
| `layout_preview.png` | Preview do mosaico (mapa mental com numeração das tiras) |
| `plano.txt` | Lista de tiras + consumo estimado de papel |

## Integração com o contador de rolo

O wrapper `print-sc03.ps1` gerencia o estado do rolo (`sc03_roll_state.json`) e atualiza o `print.md` automaticamente. Quando o papel acaba, rode `-PaperOut` pra ver o relatório e depois `-ResetRoll` com o novo rolo de 3m.

## Limitações

- **Resolução:** 8 dots/mm (203 dpi) — a imagem é rasterizada nessa resolução; fontes pequenas podem ficar ilegíveis.
- **Sem corte automático:** as tiras são cortadas manualmente na borda serrilhada.
- **Impressora comum:** este projeto só faz sentido com térmicas de ~5cm de largura; pra impressão maior, use outra impressora.

## Licença

MIT — © 2026 **Sara Spiegelberg**. Uso livre, com atribuição.