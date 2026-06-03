# Análisis de consistencia: REM ↔ DEIS ↔ FONASA

**Fecha:** 3 de junio 2026
**Objetivo:** Verificar si todos los códigos DEIS del pipeline final calzan con la población inscrita (FONASA).

---

## Fuentes de datos

| Fuente | Archivo | Códigos únicos |
|---|---|---|
| REM | `MS2026_v2.csv` | 314 |
| DEIS | `Establecimientos DEIS MINSAL 30-01-2026.xlsx` | 5,156 |
| FONASA | `data/ms_fonasa.csv` | 303 |

---

## Intersecciones generales

| Cruce | Resultado |
|---|---|
| REM ∩ DEIS | 307 / 314 (97.8%) |
| REM ∩ FONASA | 303 / 314 (96.5%) |
| DEIS ∩ FONASA | 296 / 5,156 (5.7%) |

---

## 7 códigos presentes en REM y FONASA pero AUSENTES en el registro DEIS

Estos 7 códigos fueron localizados en el Excel fuente de FONASA (`T9626 Inscritos APS RM.xlsx`), que contiene columnas `Nombre Centro`, `Comuna` y `Servicio de Salud`. A continuación, el detalle:

### Códigos mapeables (tienen correspondencia en DEIS)

| Código FONASA | Nombre FONASA | Comuna | SS | Inscritos | Código DEIS real |
|---|---|---|---|---|---|
| `109407` | Posta de Salud Rural Juan Pablo II De Lampa | Lampa | Metropolitano Norte | **9,369** | `201212` — CESFAM Juan Pablo II de Lampa |
| `111782` | Centro Comunitario de Salud Familiar El Abrazo | Maipú | Metropolitano Central | **605** | `201674` — CESFAM El Abrazo Dr. Salvador Allende Gossens |
| `113181` | Centro De Referencia De Salud El Pino | San Bernardo | Metropolitano Sur | 17 | `113180` — Hospital El Pino |
| `311001` | Cesfam El Abrazo Dr. Salvador Allende | Maipú | Metropolitano Central | **16,769** | `201674` — CESFAM El Abrazo (ya mapeado en crosswalk) |

### Códigos sin correspondencia clara en DEIS

| Código FONASA | Nombre FONASA | Comuna | SS | Inscritos | Observación |
|---|---|---|---|---|---|
| `110515` | Posta De Salud Rural Santa María | Alhué | Metropolitano Occidente | 12 | No existe en DEIS. Alhué tiene 6 establecimientos; ninguno "Santa María". Posiblemente fue cerrada o absorbida. |
| `114150` | Centro De Referencia De Salud San Rafael | La Florida | Metropolitano Sur Oriente | 15 | No existe en DEIS en La Florida. Existen `114308` (CESFAM San Rafael) y `114808` (SAPU San Rafael), ambos en La Pintana (comuna distinta). |
| `5013502` | Dasalhué | Alhué | Metropolitano Occidente | 3 | Código de 7 dígitos (formato no estándar DEIS). Probablemente código interno del DAS de Alhué. |

---

## 11 códigos REM sin población inscrita (FONASA)

Estos códigos SÍ están en DEIS pero NO en FONASA. Sus datos de metas sanitarias se muestran en el dashboard sin denominador de población.

| Código | Dependencia | MS afectadas |
|---|---|---|
| `109104` | Servicio de Salud | MSI, IIIa, IIIb, VI |
| `200389` | Municipal | IIIa, IIIb |
| `200475` | Municipal | MSI, IIIa, IIIb, VI |
| `201212` | Municipal | MSI, IIIa, IIIb, VI |
| `201353` | Municipal | VI |
| `201379` | Municipal | IIIb |
| `201674` | Municipal | MSI, IIIa, IIIb, VI |
| `202041` | Municipal | IIIa, IIIb, VI |
| `202042` | Municipal | IIIa, IIIb |
| `202205` | Municipal | MSI, IIIa, IIIb, VI |
| `202233` | Municipal | MSI, IIIa, IIIb, VI |

---

## Impacto en el pipeline

En `Calculo MS-2026.py` (línea 454-458) existe un mecanismo de crosswalk que actualmente solo mapea:

```python
codigo_crosswalk = {
    '311001': '201674',  # Cesfam El Abrazo Dr. Salvador Allende Gossens
}
```

Además, en el dashboard (`MS*.py`) la línea `df_ms1.dropna(subset=["servicio_salud", "comuna"])` descarta cualquier establecimiento sin esos datos, lo que significa que **los 7 códigos fantasma actualmente no aparecen en el dashboard**.

### Datos perdidos actualmente

- **~27,790 inscritos** FONASA que están asociados a códigos no presentes en el DEIS
- Los numeradores REM de esos establecimientos (si existen) también se pierden

---

## Recomendaciones

1. **Agregar los 4 mapeos identificados** al `codigo_crosswalk` en `Calculo MS-2026.py`: `109407→201212`, `111782→201674`, `113181→113180`
2. **Investigar los 3 códigos restantes** (`110515`, `114150`, `5013502`) para determinar si son errores de codificación FONASA o establecimientos cerrados (su impacto es mínimo: 30 inscritos entre los 3)
3. **Regenerar `MS2026_v2.csv`** ejecutando `Calculo MS-2026.py` con el crosswalk actualizado
