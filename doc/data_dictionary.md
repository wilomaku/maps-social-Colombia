# Data Dictionary

## Overview

This document describes all variables in the `municipality_level_analysis.csv` dataset used across the project. Variables are grouped by dimension and mapped to their BID IND code where applicable.

---

## 1. Geographic Identifiers

| Variable | Type | Description |
|---|---|---|
| `SUBREGIÓN` | string | Subregion name (e.g., Sabana noroccidente, Sabana suroccidente, Sabana Centro, Sabana Norte, Guavio, Soacha - Sibaté) |
| `MUNICIPIO` | string | Municipality name |

---

## 2. Area and Population

| Variable | Type | Description |
|---|---|---|
| `AREA KM2` | float64 | Total municipal area in square kilometers |
| `AREA KM2 URBANA` | float64 | Urban area of the municipality in km² |
| `POBLACION ESTIMADA 2021/RURAL` | float64 | Estimated rural population in 2021 |
| `POBLACION ESTIMADA 2021/URBANA` | float64 | Estimated urban population in 2021 |
| `TOTAL POBLACIÓN` | float64 | Total estimated population in 2021 |

---

## 3. Soil and Land Use Indicators (IND 1)

| Variable | IND Code | Type | Description | Source |
|---|---|---|---|---|
| `WEI` | 1.1 | float64 | Weighted Environmental Index — composite index assigning weights to each land cover type according to its ecological importance (`bosque: 0.3`, `natural_no_bosque: 0.25`, `agricultura: 0.15`, `no_vegetación: 0.0`, `agua: 0.3`) | Mapbio |
| `TCMA_URBANO` | 1.2 | float64 | Annual mean growth rate of the urban footprint: `TCMA = (((area_final / area_initial) ** (1/t)) - 1) * 100`, where *t* is the time in years | Mapbio |
| `Porc_poblacion_en_urbana` | 1.3 | float64 | Percentage of the population living in the urban cabecera | DNP – Visor MDM 2021 |
| `Densidad_urbana` | 1.4 | float64 | Net population density of the urban area: persons per km² of urbanized land | DANE population projections / POT municipal |
| `TCMA_AGRICULTURA` | — | float64 | CAGR of agriculture and pasture mosaic area (2011–2021) | Computed from Mapbio land cover data |
| `TCMA_BOSQUE` | — | float64 | CAGR of forest area (2011–2021) | Computed from Mapbio land cover data |
| `TCMA_AGUA` | — | float64 | CAGR of water body area (2011–2021) | Computed from Mapbio land cover data |

---

## 4. Institutional Indicators (IND 2)

| Variable | IND Code | Type | Description | Source |
|---|---|---|---|---|
| `IND 2.1 TIPO` | 2.1 | string | Type of land use plan: `EOT` (Equipo de Trabajo), `POT` (Plan de Ordenamiento Territorial), `PBOT` (Plan Básico de Ordenamiento Territorial) | POT municipal |
| `Ind_POT` | 2.1 | float64 | Composite index on the existence and active implementation of a municipal POT, including zoning with environmental protection/preservation zones and revision status (every 12 years) | POT municipal / DNP – Visor MDM 2021 |
| `AÑOS REVISION` | 2.1 | float64 | Number of years since the last POT revision | POT municipal |
| `AÑO ULTIMA REVISION` | 2.1 | float64 | Year of the last POT revision | POT municipal |
| `IND 2.1 REVISION` | 2.1 | float64 | Revision status indicator (1 = revised, 0 = not revised) | POT municipal |
| `IND 2.1 ZONAS AMB` | 2.1 | string | Environmental protection zoning status | POT municipal |
| `Ind_eficiencia_recaudo` | 2.2 | float64 | Composite index of predial tax collection efficiency, comparing the municipal value to the initial capacity group (CI) average | DNP – Visor MDM 2021 |
| `Ingresos_tributarios_percap` | 2.3 | float64 | Per capita tributary income (total collection divided by absolute population), comparable to the CI group average | DNP – Visor MDM 2021 |
| `Percepcion_corrupcion` | 2.4 | float64 | Percentage of the population that believes the municipality has worsened in the fight against corruption between 2017 and the survey date | EM2021 – NHCLPA8P |
| `Percepcion_verde` | 2.5 | float64 | Percentage of the population that believes the municipality has worsened in green spaces and parks between 2017 and the survey date | EM2021 – NHCLPA7E |

---

## 5. Social Indicators (IND 3)

| Variable | IND Code | Type | Description | Source |
|---|---|---|---|---|
| `Porc_pobreza_monetaria` | 3.1 | float64 | Percentage of the population below the monetary poverty line (per capita income per expenditure unit vs. cost of a food and non-food goods basket) | EM2021 – `N_pobre_monetario` |
| `Porc_pobreza_extrema` | 3.2 | float64 | Percentage of the population below the extreme poverty line (per capita income vs. cost of a basic food basket) | EM2021 – `N_pobre_extremo` |
| `Porc_pobreza_multi` | 3.3 | float64 | Percentage of households with multidimensional poverty | EM2021 – `N_pobre_ipm` |
| `GINI` | 3.4 | float64 | Gini coefficient of income inequality (Deaton / Sen-Shorrocks-Thon formula based on covariance of incomes) | EM2021 – `N_ingpc` |
| `Porc_informal` | 3.5 | float64 | Percentage of informal employment (non-public-employment workers in businesses ≤5 employees, independent workers, or own-account workers outside the 195 formal DANE occupations) | EM2021 – `N_informal` |

---

## 6. Housing and Environment Indicators (IND 4)

| Variable | IND Code | Type | Description | Source |
|---|---|---|---|---|
| `Porc_deficit_vivienda_cuali` | 4.1 | float64 | Percentage of housing units in conditions below habitability standards defined by the country | EM2021 – `N_deficit_cualitativo` |
| `Porc_deficit_vivienda_cuanti` | 4.2 | float64 | Percentage of households in quantitative housing deficit (insufficient quantity of housing services such as water, sanitation, electricity) | EM2021 – `N_deficit_cuantitativo` |
| `Porc_contaminacion_aire` | 4.3 | float64 | Percentage of the population reporting air pollution problems in the surroundings of their dwelling | EM2021 – `NVCBP15D` |
| `Porc_contaminacion_agua` | 4.4 | float64 | Percentage of the population reporting water body contamination problems (rivers, streams, wetlands, lagoons) in the surroundings of their dwelling | EM2021 – `NVCBP15I` |

---

## Notes

- All percentage variables are expressed as values in the range 0–100 (e.g., `29.97` means 29.97%).
- `TCMA_URBANO`, `TCMA_AGRICULTURA`, `TCMA_BOSQUE`, and `TCMA_AGUA` are expressed as percentage growth rates per year (e.g., `1.7158` means 1.72% annual growth).
- `Ind_POT` is a composite index where higher values indicate better POT implementation; typical range is 0–1, with `1` indicating full compliance.
- `GINI` ranges from 0 (perfect equality) to 1 (maximum inequality).
- `WEI` is a weighted composite index; higher values indicate greater environmental weight from natural/protected land cover.
- Missing values are represented as `NaN` in the dataset.