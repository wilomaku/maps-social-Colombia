## Abstract

### Introduction and Research question

The municipalities of the Bogotá Metropolitan Area (Colombia) exhibit urban growth dynamics driven by their functional relationship and proximity to the capital city. These dynamics are heterogeneous across the region and have a direct impact on the population's living conditions and habitat. This study aims to address the following research question:

**What can territorial management, urban growth, and habitat conditions reveal about poverty in the Bogotá Metropolitan Area?**

### Methodology

To answer this question, MapBiomas land cover data were used to calculate the urban infrastructure growth rate for the municipalities of the Bogotá Metropolitan Area between 1985 and 2021. In addition, data from the 2021 Multipurpose Survey and the Colombian Geographic Institute (IGAC) were used to construct the variables for a multivariate regression model.

### Results and Conclusions

The results reveal a significant relationship between housing deficit and monetary poverty, as well as differentiated impacts of urban growth across the metropolitan subregions. The study recommends strengthening this analysis through the application of nonparametric models and the development of variables related to land value and economic activities.

## Key Components

### Data Sources
- **Socio-economic data**: Census data from Dane (Colombian National Administrative Department of Statistics) [Census Data](https://www.dane.gov.co/index.php/estadisticas-por-tema/pobreza-y-condiciones-de-vida/encuesta-multiproposito). This survey data is applied every 3 years and the last available to the date of the analysis is 2021.
- **Land cover and land use data**: Annual land cover and land use maps in raster format (30x30 meter pixel). These dataset provide spatial classification of land cover types (e.g. forest, agriculture, water, urban infrastructure, etc.) by state/municipality for Colombia. [MapBiomas Colombia Collection](https://plataforma.colombia.mapbiomas.org).
- **Territorial management data**: Periodic revision of the territorial management plans with last date when the tool was updated. [IGAC Management Territory Platform](https://www.colombiaot.gov.co/)

### Repository Code

maps-social-Colombia/
├── .gitignore
├── README.md
├── requirements.txt
├── doc/
│   └── data_dictionary.md — Data description (full batch)
└── src/
    ├── 00_create_municipality_level_analysis.ipynb — Recreates the municipality-level CSV from the Encuesta Multipropósito survey and soil-cover data.
    ├── 10_analisis_usos_suelo.ipynb — Analyzes soil cover evolution (2009–2024) for selected municipalities in Cundinamarca.
    ├── 11_EDA_socioeconomica.ipynb — Exploratory analysis of socioeconomic conditions for the 20 selected municipalities.
    ├── 12_EDA_usos_suelo_time.ipynb — Explores soil use evolution and the Weighted Environmental Index (WEI) across three time points (2011, 2014, 2021).
    ├── 13_create_indexes.ipynb — Creates BID indicators for soil use and socioeconomic variables.
    ├── 20_read_maps.ipynb — Reads and inspects raster TIFF files for soil coverage maps.
    ├── 30_transicion_pobreza_dispersion_adj.ipynb — Crosses soil cover transition matrices with socioeconomic conditions for municipalities (2018–2021).
    ├── 31_analysis_gral_suelo_social.ipynb — Exploratory analysis of the integrated soil and social indicators.
    ├── 40_model_pobreza.ipynb — Builds the poverty model using the selected factors.
    └── soil_poverty_analysis.py — Utility module with helpers for loading CSVs, normalizing municipality names, computing the Gini coefficient, and building the municipality-level dataset.

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

At the start of the project, it was considered a broad set of variables which is described in /doc/data_dictionary.md . To fit this analysis scope and deadlines, the full set was limited to the following varaibles. However, some notebooks cover more variables and it can be interesting to explore more variables.

| Variable | IND Code | Type | Description | Source |
|---|---|---|---|---|
| `Porc_pobreza_monetaria` | 3.1 | float64 | Percentage of the population below the monetary poverty line, defined by comparing per capita income per expenditure unit against the cost of a food and non-food goods basket. | EM2021 – Variables adicionales – `N_pobre_monetario` |
| `TCMA_URBANO` | 1.2 | float64 | Annual mean growth rate of the urban footprint, calculated as `TCMA = (((area_final / area_initial) ** (1/t)) - 1) * 100`, where *t* is the time in years. | Mapbio |
| `Ind_POT` | 2.1 | float64 | Composite index on the existence and active implementation of a municipal land use plan (POT), including zoning with environmental protection/preservation zones and revision status (every 12 years). | POT municipal / DNP – Mediciones de desempeño territorial – Visor MDM 2021 |
| `Porc_contaminacion_aire` | 4.3 | float64 | Percentage of the population that reports having air pollution problems in the surroundings of their dwelling. | EM2021 – `NVCBP15D` |
| `Porc_deficit_vivienda_cuanti` | 4.2 | float64 | Percentage of households in quantitative housing deficit (lack of sufficient quantity of housing services such as water, sanitation, electricity, etc.). | EM2021 – `N_deficit_cuantitativo` |

**EM2021**: Encuesta Multipropósito DANE 2021 [Census Data](https://www.dane.gov.co/index.php/estadisticas-por-tema/pobreza-y-condiciones-de-vida/encuesta-multiproposito)
**Mapbio**: MapBiomas Data [MapBiomas Colombia Collection](https://plataforma.colombia.mapbiomas.org)

## Important Notes

- The analysis covers 20 municipalities from Bogotá Metropolitan Area (without Bogotá).
- For census data, samples are weighted using survey expansion factors (FEX_C).
- Land cover analysis uses data from the soil coverage workbook.

## Dependencies

Developed in Python. Instructions to use this repository:

1. Create new environment
python -m venv myenv
2. Activate environment
source myenv/bin/activate
3. Clone repository
git clone https://github.com/wilomaku/maps-social-Colombia.git
4. Change to directory
cd maps-social-Colombia
5. Install requirements
pip install -r requirements.txt
6. Create data folder
mkdir data
7. Download data sources to /data folder
- [Socio-economic data](https://microdatos.dane.gov.co/index.php/catalog/743/get-microdata)
- [Land cover and land use data](https://colombia.mapbiomas.org/en/segunda-coleccion-de-mapbiomas-colombia/)


## Credits

Project developed within [Observatorio Socio Territorial Bogotá Sabana](https://www.observatoriosocioterritorial.org/) by Sandra Herrera and William Herrera.