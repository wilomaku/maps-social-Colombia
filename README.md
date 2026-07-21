## Project Overview

This project analyzes the relationship between soil/land cover and socio-economic indicators in Bogotá savanna (Colombia).

## Project Objective

Analyse and understand the relationship between land cover types and use, and their use through time (2014-2021), and socio-economic conditions in Bogotá savanna west region. This region is an important hydric source for the region, rich soil for agriculture, logistic hub and comertial connection between west and center regions, proximity with Bogotá. In recent years, this region has experienced transport changes, urban expansion, demographic and soil use changes. These changes impact both land cover dynamics and socio-economic conditions in the region.

## Definitions

- Bogotá savana west region in this study refers to the following municipalities: Funza, Facatativá, Mosquera, Madrid and Zipacón.

## Key Components

### Data Sources
- **Socio-economic data**: Census data from Dane (Colombian National Administrative Department of Statistics) [Census Data](https://www.dane.gov.co/index.php/estadisticas-por-tema/pobreza-y-condiciones-de-vida/encuesta-multiproposito). This survey data is applied every 3 years and the last available to the date of the analysis is 2021.
- **Land cover and land use data**: Annual land cover and land use maps in raster format (30x30 meter pixel). These dataset provide spatial classification of land cover types (e.g. forest, agriculture, water, urban infrastructure, etc.) by state/municipality for Colombia. [MapBiomas Colombia Collection](https://plataforma.colombia.mapbiomas.org).

### Core Components
1. **`src/`**: 

## Data Processing Workflow

1. **Load Survey Data**: 
   - Start with `Identificación (Capítulo A).csv` as geographic spine
   - Filter for Cundinamarca (DPTO == 25)

2. **Normalize Municipality Names**:
   - Convert to lowercase
   - Remove accents
   - Strip "cabecera" and "resto" suffixes
   - Apply manual mappings for known discrepancies

3. **Load and Process Soil Data**:
   - Filter Excel data for Cundinamarca
   - Normalize municipality names
   - Calculate land cover shares by class level (0, 1, 2)
   - Convert 2021 area column to numeric hectares

4. **Aggregate Survey Data**:
   - Apply survey weights (FEX_C column) which are used to scale individual survey responses to represent the entire target population.
   - Calculate weighted rates for poverty indicators, service access, demographics
   - Aggregate to municipality level using survey weights

5. **Merge Datasets**:
   - Join survey aggregates with soil characteristics on normalized municipality names
   - Output final municipality-level dataset

## Key Variables in Analysis

### Poverty/Dependent Variables
- `poor_subjective_rate`: % reporting subjective poverty (NHCLP11 == 1)
- `income_insufficient_rate`: % reporting insufficient income (NHCLP10 == 1)
- `food_insecurity_any_rate`: % experiencing any food insecurity

### Land Cover Predictors (Shares)
- `share_natural`, `share_anthropic`: Level 0 classification
- `share_forest`, `share_agriculture`, `share_no_vegetation`, `share_water`: Level 1
- `share_urban_infrastructure`, `share_agriculture_pasture_mosaic`, `share_forest_level2`, etc.: Specific Level 2 classes

### Control Variables
- Service access: `water_access_rate`, `sewer_access_rate`, `electricity_access_rate`, `internet_access_rate`
- Demographics: `scholarship_rate`, `online_courses_rate`
- Labor: `pet_rate` (working age), `ocu_rate` (employed), `informal_rate` (informal employment)
- Housing: `tenure_own_rate`, `sanitation_access_rate`, `garbage_access_rate`

## Important Notes

- The analysis covers 21 municipalities (including Bogotá savana west region).
- All rates are weighted using survey expansion factors (FEX_C)
- Land cover analysis uses 2021 data from the soil coverage workbook

## Dependencies

Developed in Python. For details on dependencies, see `requirements.txt`.