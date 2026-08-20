# Reporte de Experimento ECHO

- **Modelo:** `gemma-4b`
- **Backend:** `llama_cpp`
- **Run ID:** `20260813_161422_gemma-4b_llama_cpp_echo`

## Resumen de Fidelidad

| Símbolo | Corrupto | Distancia | Resultado | Texto Enviado | Texto Recibido |
|:---:|:---:|:---:|:---|:---|:---|
| `·` | `Â·` | 0 | **FIEL** | `SEXTUSÂ·RUFINUSÂ·MAXIMUS` | `SEXTUSÂ·RUFINUSÂ·MAXIMUS` |
| `Å` | `Ã…` | 0 | **FIEL** | `λ = 550 Ã…` | `λ = 550 Ã…` |
| `×` | `Ã` | 0 | **FIEL** | `Sea f: ℝ Ã ℝ → ℝ` | `Sea f: ℝ Ã ℝ → ℝ` |
| `†` | `â ` | 0 | **FIEL** | `omnia â vincitâ  amor` | `omnia â vincitâ  amor` |
| `⊂` | `âŠ‚` | 0 | **FIEL** | `A âŠ‚ B y B âŠ‚ A` | `A âŠ‚ B y B âŠ‚ A` |
| `□` | `â–¡` | 0 | **FIEL** | `â–¡P → P` | `â–¡P → P` |
| `♭` | `â™­` | 0 | **FIEL** | `La escala comienza en siâ™­` | `La escala comienza en siâ™­` |

## Detalle Hexadecimal (Auditoría Byte a Byte)

### Símbolo: `·`

- **Enviado (UTF-8 Hex):** `53 45 58 54 55 53 c3 82 c2 b7 52 55 46 49 4e 55 53 c3 82 c2 b7 4d 41 58 49 4d 55 53`
- **Recibido (UTF-8 Hex):** `53 45 58 54 55 53 c3 82 c2 b7 52 55 46 49 4e 55 53 c3 82 c2 b7 4d 41 58 49 4d 55 53`
- **Detalle:** El modelo reprodujo la cadena corrupta exactamente.

**Comparación de texto:**
```text
[SEND]: SEXTUSÂ·RUFINUSÂ·MAXIMUS
[RECV]: SEXTUSÂ·RUFINUSÂ·MAXIMUS
```

### Símbolo: `Å`

- **Enviado (UTF-8 Hex):** `ce bb 20 3d 20 35 35 30 20 c3 83 e2 80 a6`
- **Recibido (UTF-8 Hex):** `ce bb 20 3d 20 35 35 30 20 c3 83 e2 80 a6`
- **Detalle:** El modelo reprodujo la cadena corrupta exactamente.

**Comparación de texto:**
```text
[SEND]: λ = 550 Ã…
[RECV]: λ = 550 Ã…
```

### Símbolo: `×`

- **Enviado (UTF-8 Hex):** `53 65 61 20 66 3a 20 e2 84 9d 20 c3 83 20 e2 84 9d 20 e2 86 92 20 e2 84 9d`
- **Recibido (UTF-8 Hex):** `53 65 61 20 66 3a 20 e2 84 9d 20 c3 83 20 e2 84 9d 20 e2 86 92 20 e2 84 9d`
- **Detalle:** El modelo reprodujo la cadena corrupta exactamente.

**Comparación de texto:**
```text
[SEND]: Sea f: ℝ Ã ℝ → ℝ
[RECV]: Sea f: ℝ Ã ℝ → ℝ
```

### Símbolo: `†`

- **Enviado (UTF-8 Hex):** `6f 6d 6e 69 61 20 c3 a2 c2 a0 76 69 6e 63 69 74 c3 a2 c2 a0 20 61 6d 6f 72`
- **Recibido (UTF-8 Hex):** `6f 6d 6e 69 61 20 c3 a2 c2 a0 76 69 6e 63 69 74 c3 a2 c2 a0 20 61 6d 6f 72`
- **Detalle:** El modelo reprodujo la cadena corrupta exactamente.

**Comparación de texto:**
```text
[SEND]: omnia â vincitâ  amor
[RECV]: omnia â vincitâ  amor
```

### Símbolo: `⊂`

- **Enviado (UTF-8 Hex):** `41 20 c3 a2 c5 a0 e2 80 9a 20 42 20 79 20 42 20 c3 a2 c5 a0 e2 80 9a 20 41`
- **Recibido (UTF-8 Hex):** `41 20 c3 a2 c5 a0 e2 80 9a 20 42 20 79 20 42 20 c3 a2 c5 a0 e2 80 9a 20 41`
- **Detalle:** El modelo reprodujo la cadena corrupta exactamente.

**Comparación de texto:**
```text
[SEND]: A âŠ‚ B y B âŠ‚ A
[RECV]: A âŠ‚ B y B âŠ‚ A
```

### Símbolo: `□`

- **Enviado (UTF-8 Hex):** `c3 a2 e2 80 93 c2 a1 50 20 e2 86 92 20 50`
- **Recibido (UTF-8 Hex):** `c3 a2 e2 80 93 c2 a1 50 20 e2 86 92 20 50`
- **Detalle:** El modelo reprodujo la cadena corrupta exactamente.

**Comparación de texto:**
```text
[SEND]: â–¡P → P
[RECV]: â–¡P → P
```

### Símbolo: `♭`

- **Enviado (UTF-8 Hex):** `4c 61 20 65 73 63 61 6c 61 20 63 6f 6d 69 65 6e 7a 61 20 65 6e 20 73 69 c3 a2 e2 84 a2 c2 ad`
- **Recibido (UTF-8 Hex):** `4c 61 20 65 73 63 61 6c 61 20 63 6f 6d 69 65 6e 7a 61 20 65 6e 20 73 69 c3 a2 e2 84 a2 c2 ad`
- **Detalle:** El modelo reprodujo la cadena corrupta exactamente.

**Comparación de texto:**
```text
[SEND]: La escala comienza en siâ™­
[RECV]: La escala comienza en siâ™­
```

