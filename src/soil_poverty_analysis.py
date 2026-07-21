import os
import re
import unicodedata
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd


def find_repo_root(start: Optional[Path] = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / 'data').exists() and (candidate / 'src').exists():
            return candidate
    return current


def parse_weight_series(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.str.replace('.', '', regex=False)
    s = s.str.replace(',', '.', regex=False)
    return pd.to_numeric(s, errors='coerce')


def normalize_municipality(value) -> str:
    if pd.isna(value):
        return ''
    text = str(value).lower()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r'\b(cabecera|resto)\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_semicolon_csv(path: Path, columns: Optional[Iterable[str]] = None, encodings: Iterable[str] = ('utf-8', 'latin1')):
    last_error = None
    for encoding in encodings:
        try:
            if columns is None:
                return pd.read_csv(path, sep=';', encoding=encoding)
            return pd.read_csv(path, sep=';', encoding=encoding, usecols=list(columns))
        except Exception as exc:
            last_error = exc
    raise last_error


def build_municipality_dataset(output_path: Optional[Path] = None):
    root = find_repo_root()
    data_dir = root / 'data'
    multi_dir = data_dir / 'multiproposito'
    soil_path = data_dir / 'Statistics-for-Website-MB-Cobertura-col3.xlsx'
    out_path = output_path or data_dir / 'processed' / 'municipality_level_analysis.csv'
    out_path.parent.mkdir(parents=True, exist_ok=True)

    manual_mapping = {
        'bojaca': 'Bojacá',
        'cajica': 'Cajicá',
        'chia': 'Chía',
        'facatativa': 'Facatativá',
        'fusagasuga': 'Fusagasugá',
        'gachancipa': 'Gachancipá',
        'sibate': 'Sibaté',
        'sopo': 'Sopó',
        'tocancipa': 'Tocancipá',
        'zipacon': 'Zipacón',
        'zipaquira': 'Zipaquirá',
    }

    ident = load_semicolon_csv(
        multi_dir / 'Identificación (Capítulo A).csv',
        columns=['DIRECTORIO', 'DPTO', 'MPIO', 'NOMBRE_ESTRATO', 'FEX_C'],
        encodings=('latin1', 'utf-8'),
    )
    ident['weight'] = parse_weight_series(ident['FEX_C'])
    ident_cund = ident[ident['DPTO'] == 25].copy()

    ident_unique = ident_cund[['NOMBRE_ESTRATO']].drop_duplicates().copy()
    ident_unique['municipio_base'] = ident_unique['NOMBRE_ESTRATO'].apply(normalize_municipality)
    ident_unique['municipio_base'] = ident_unique['municipio_base'].map(lambda x: manual_mapping.get(x, x))
    ident_unique['municipio_base_key'] = ident_unique['municipio_base'].apply(normalize_municipality)

    soil = pd.read_excel(soil_path, sheet_name='COBERTURA_MUNICIPIO')
    soil = soil[soil['departamento'].astype(str).str.strip().str.lower() == 'cundinamarca'].copy()
    soil['municipio_clean'] = soil['municipio'].astype(str).apply(normalize_municipality)
    soil_lookup = soil[['municipio_clean', 'municipio']].drop_duplicates().set_index('municipio_clean')['municipio'].to_dict()
    ident_unique['soil_municipio'] = ident_unique['municipio_base_key'].apply(lambda x: soil_lookup.get(x, np.nan))
    ident_unique['match_method'] = np.where(
        ident_unique['municipio_base_key'].isin(soil_lookup.keys()),
        'deterministic',
        'manual',
    )

    soil_long = soil[['municipio', 'departamento', 'class_level_0', 'class_level_1', 'class_level_2', 2021]].copy()
    soil_long.columns = ['municipio', 'departamento', 'class_level_0', 'class_level_1', 'class_level_2', 'area_ha_2021']
    soil_long['area_ha_2021'] = pd.to_numeric(soil_long['area_ha_2021'], errors='coerce').fillna(0)
    soil_long['municipio_clean'] = soil_long['municipio'].astype(str).apply(normalize_municipality)
    soil_long['municipio_clean'] = soil_long['municipio_clean'].map(lambda x: manual_mapping.get(x, x))

    level0 = soil_long.groupby(['municipio_clean', 'class_level_0'])['area_ha_2021'].sum().reset_index()
    level0['share'] = level0.groupby('municipio_clean')['area_ha_2021'].transform(lambda s: s / s.sum())
    level0_wide = level0.pivot(index='municipio_clean', columns='class_level_0', values='share').reset_index()
    level0_wide = level0_wide.rename(columns={'Antrópico': 'share_anthropic', 'Natural': 'share_natural'})

    level1 = soil_long.groupby(['municipio_clean', 'class_level_1'])['area_ha_2021'].sum().reset_index()
    level1['share'] = level1.groupby('municipio_clean')['area_ha_2021'].transform(lambda s: s / s.sum())
    level1_wide = level1.pivot(index='municipio_clean', columns='class_level_1', values='share').reset_index()
    level1_wide = level1_wide.rename(columns={
        '1. Formacion Boscosa': 'share_forest',
        '2. Formación natural no boscosa': 'share_natural_non_forest',
        '3. Área  agropecuaria': 'share_agriculture',
        '4. Área sin vegetación': 'share_no_vegetation',
        '5. Cuerpo de agua': 'share_water',
    })

    selected_classes = {
        'share_urban_infrastructure': '4.2. Infraestructura urbana',
        'share_agriculture_pasture_mosaic': '3.4. Mosaico de agricultura o pasto',
        'share_forest_level2': '1.1. Bosque',
        'share_mining': '4.3. Minería',
        'share_other_no_vegetation': '4.5. Otra área sin vegetación',
        'share_herbazales_arbustales': '2.7. Herbazales o arbustales andinos',
    }
    level2 = soil_long.groupby(['municipio_clean', 'class_level_2'])['area_ha_2021'].sum().reset_index()
    level2['share'] = level2.groupby('municipio_clean')['area_ha_2021'].transform(lambda s: s / s.sum())
    level2_wide = level2.pivot(index='municipio_clean', columns='class_level_2', values='share').reset_index()
    level2_features = {feat: level2_wide[cls].fillna(0) for feat, cls in selected_classes.items()}
    level2_feature_df = pd.DataFrame(level2_features, index=level2_wide['municipio_clean'])
    level2_feature_df = level2_feature_df.reset_index().rename(columns={'index': 'municipio_clean'})

    soil_features = level0_wide.merge(level1_wide, on='municipio_clean', how='outer').merge(level2_feature_df, on='municipio_clean', how='outer')
    soil_features['area_total_ha_2021'] = soil_long.groupby('municipio_clean')['area_ha_2021'].sum().reindex(soil_features['municipio_clean']).values
    soil_features = soil_features.fillna(0).copy()

    def weighted_mean(series, weights):
        s = pd.to_numeric(series, errors='coerce')
        w = pd.to_numeric(weights, errors='coerce').fillna(0)
        total_w = w.sum()
        return np.average(s, weights=w) if total_w > 0 else np.nan

    def get_household_data():
        chap_c = load_semicolon_csv(
            multi_dir / 'Condiciones habitacionales del hogar (Capítulo C).csv',
            columns=['DIRECTORIO', 'DIRECTORIO_HOG', 'NHCCP1', 'NHCCP31', 'NHCCP37', 'FEX_C'],
        )
        chap_d = load_semicolon_csv(
            multi_dir / 'Servicios públicos domiciliarios y de TIC (Capítulo D).csv',
            columns=['DIRECTORIO', 'DIRECTORIO_HOG', 'NHCDP1', 'NHCDP3', 'NHCDP9', 'NHCDP15', 'NHCDP28', 'FEX_C'],
        )
        chap_l = load_semicolon_csv(
            multi_dir / 'Percepción sobre las condiciones de vida y el desempeño institucional (Capítulo L).csv',
            columns=['DIRECTORIO', 'DIRECTORIO_HOG', 'NHCLP10', 'NHCLP11', 'NHCLP14', 'NHCLP16', 'NHCLP17', 'NHCLP18', 'NHCLP19', 'FEX_C'],
        )
        for df in [chap_c, chap_d, chap_l]:
            df['weight'] = parse_weight_series(df['FEX_C'])

        base_households = ident_cund[['DIRECTORIO', 'NOMBRE_ESTRATO']].copy()
        chap_c = chap_c.merge(base_households, on='DIRECTORIO', how='inner')
        chap_d = chap_d.merge(base_households, on='DIRECTORIO', how='inner')
        chap_l = chap_l.merge(base_households, on='DIRECTORIO', how='inner')

        chap_d = chap_d.rename(columns={'weight': 'weight_d'})
        chap_l = chap_l.rename(columns={'weight': 'weight_l'})

        households = chap_c.merge(
            chap_d[['DIRECTORIO', 'DIRECTORIO_HOG', 'NHCDP1', 'NHCDP3', 'NHCDP9', 'NHCDP15', 'NHCDP28', 'NOMBRE_ESTRATO', 'weight_d']],
            on=['DIRECTORIO', 'DIRECTORIO_HOG', 'NOMBRE_ESTRATO'],
            how='left',
        )
        households = households.merge(
            chap_l[['DIRECTORIO', 'DIRECTORIO_HOG', 'NHCLP10', 'NHCLP11', 'NHCLP14', 'NHCLP16', 'NHCLP17', 'NHCLP18', 'NHCLP19', 'NOMBRE_ESTRATO', 'weight_l']],
            on=['DIRECTORIO', 'DIRECTORIO_HOG', 'NOMBRE_ESTRATO'],
            how='left',
        )
        households['weight'] = households['weight'].fillna(households['weight_d']).fillna(households['weight_l'])
        households = households.drop(columns=['weight_d', 'weight_l'])
        return households

    households = get_household_data()
    households['poor_subjective'] = (households['NHCLP11'] == 1).astype(float)
    households['income_insufficient'] = (households['NHCLP10'] == 1).astype(float)
    households['food_insecurity_any'] = households[['NHCLP16', 'NHCLP17', 'NHCLP18', 'NHCLP19']].eq(1).any(axis=1).astype(float)
    households['tenure_own'] = (households['NHCCP1'] == 1).astype(float)
    households['sanitation_access'] = (households['NHCCP31'] == 1).astype(float)
    households['garbage_access'] = (households['NHCCP37'] == 1).astype(float)
    households['water_access'] = (households['NHCDP1'] == 1).astype(float)
    households['sewer_access'] = (households['NHCDP3'] == 1).astype(float)
    households['electricity_access'] = (households['NHCDP9'] == 1).astype(float)
    households['internet_access'] = (households['NHCDP28'] == 1).astype(float)

    household_summary = []
    for municipality, group in households.groupby('NOMBRE_ESTRATO'):
        row = {
            'NOMBRE_ESTRATO': municipality,
            'n_households': group['DIRECTORIO_HOG'].nunique(),
            'weighted_households': group['weight'].sum(),
        }
        for col in ['poor_subjective', 'income_insufficient', 'food_insecurity_any', 'tenure_own', 'sanitation_access', 'garbage_access', 'water_access', 'sewer_access', 'electricity_access', 'internet_access']:
            row[col + '_rate'] = weighted_mean(group[col], group['weight'])
        household_summary.append(row)
    household_summary = pd.DataFrame(household_summary)
    household_summary['municipio_base'] = household_summary['NOMBRE_ESTRATO'].apply(normalize_municipality)
    household_summary['municipio_base'] = household_summary['municipio_base'].map(lambda x: manual_mapping.get(x, x))

    chap_e = load_semicolon_csv(
        multi_dir / 'Composición del hogar y demografía (Capítulo E).csv',
        columns=['DIRECTORIO', 'DIRECTORIO_HOG', 'DIRECTORIO_PER', 'SEXO', 'FEX_C'],
    )
    chap_h = load_semicolon_csv(
        multi_dir / 'Educaciвn (Capitulo H).csv',
        columns=['DIRECTORIO', 'DIRECTORIO_HOG', 'DIRECTORIO_PER', 'NPCHP24', 'NPCHP36', 'FEX_C'],
    )
    chap_k = load_semicolon_csv(
        multi_dir / 'Fuerza de trabajo (Capítulo K).csv',
        columns=['DIRECTORIO', 'DIRECTORIO_HOG', 'DIRECTORIO_PER', 'PET', 'OCU', 'DES', 'FL', 'OINFORMAL', 'FEX_C'],
    )
    for df in [chap_e, chap_h, chap_k]:
        df['weight'] = parse_weight_series(df['FEX_C'])

    chap_e = chap_e.merge(ident_cund[['DIRECTORIO', 'NOMBRE_ESTRATO']], on='DIRECTORIO', how='inner')
    chap_h = chap_h.merge(ident_cund[['DIRECTORIO', 'NOMBRE_ESTRATO']], on='DIRECTORIO', how='inner')
    chap_k = chap_k.merge(ident_cund[['DIRECTORIO', 'NOMBRE_ESTRATO']], on='DIRECTORIO', how='inner')

    chap_e['female'] = (chap_e['SEXO'] == 2).astype(float)
    chap_h['scholarship'] = (chap_h['NPCHP24'] == 1).astype(float)
    chap_h['online_courses'] = (chap_h['NPCHP36'] == 1).astype(float)
    chap_k['pet'] = (chap_k['PET'] == 1).astype(float)
    chap_k['ocu'] = (chap_k['OCU'] == 1).astype(float)
    chap_k['des'] = (chap_k['DES'] == 1).astype(float)
    chap_k['fl'] = (chap_k['FL'] == 1).astype(float)
    chap_k['informal'] = (chap_k['OINFORMAL'] == 1).astype(float)

    person_summary = []
    for name, df, indicator in [
        ('female', chap_e, 'female'),
        ('scholarship', chap_h, 'scholarship'),
        ('online_courses', chap_h, 'online_courses'),
        ('pet', chap_k, 'pet'),
        ('ocu', chap_k, 'ocu'),
        ('des', chap_k, 'des'),
        ('fl', chap_k, 'fl'),
        ('informal', chap_k, 'informal'),
    ]:
        rows = []
        for municipality, group in df.groupby('NOMBRE_ESTRATO'):
            rows.append({
                'NOMBRE_ESTRATO': municipality,
                'n_people': group['DIRECTORIO_PER'].nunique(),
                'weighted_people': group['weight'].sum(),
                f'{name}_rate': weighted_mean(group[indicator], group['weight']),
            })
        person_summary.append(pd.DataFrame(rows))

    person_summary_df = person_summary[0]
    for frame in person_summary[1:]:
        person_summary_df = person_summary_df.merge(frame, on=['NOMBRE_ESTRATO', 'n_people', 'weighted_people'], how='outer')

    household_summary = household_summary.rename(columns={'municipio_base': 'municipio_base_hh'})
    municipality_df = ident_unique[['NOMBRE_ESTRATO', 'municipio_base', 'soil_municipio', 'match_method']].merge(household_summary, on='NOMBRE_ESTRATO', how='left')
    municipality_df = municipality_df.merge(person_summary_df, on='NOMBRE_ESTRATO', how='left')
    soil_features_renamed = soil_features.rename(columns={'municipio_clean': 'municipio_base'})
    municipality_df = municipality_df.merge(soil_features_renamed, on='municipio_base', how='left')
    municipality_df = municipality_df[municipality_df['municipio_base'].notna()].copy()

    def aggregate_by_municipality(df):
        group_cols = ['municipio_base']
        count_cols = ['n_households', 'weighted_households', 'n_people', 'weighted_people']
        rate_cols = [c for c in df.columns if c.endswith('_rate') and c not in count_cols]
        constant_cols = [c for c in df.columns if c not in group_cols + count_cols + rate_cols + ['NOMBRE_ESTRATO', 'soil_municipio', 'match_method', 'municipio_base_key']]
        # Use weights where available to aggregate rates.
        out = []
        for municipality, group in df.groupby(group_cols, dropna=False):
            municipality_value = municipality[0] if isinstance(municipality, tuple) else municipality
            row = {'municipio_base': municipality_value}
            for c in count_cols:
                row[c] = group[c].sum() if c in group.columns else np.nan
            for c in rate_cols:
                if 'weighted_households' in group.columns and c.startswith(('poor_', 'income_', 'food_', 'tenure_', 'sanitation_', 'garbage_', 'water_', 'sewer_', 'electricity_', 'internet_')):
                    weights = group['weighted_households']
                elif 'weighted_people' in group.columns and c.endswith('_rate'):
                    weights = group['weighted_people']
                else:
                    weights = pd.Series(1, index=group.index)
                row[c] = weighted_mean(group[c], weights)
            for c in constant_cols:
                row[c] = group[c].iloc[0] if c in group.columns else np.nan
            out.append(row)
        return pd.DataFrame(out)

    municipality_df = aggregate_by_municipality(municipality_df)
    municipality_df = municipality_df.sort_values('municipio_base').reset_index(drop=True)
    municipality_df.to_csv(out_path, index=False)
    return municipality_df, ident_unique


if __name__ == '__main__':
    df, match = build_municipality_dataset()
    print(df[['municipio_base', 'poor_subjective_rate', 'income_insufficient_rate', 'share_urban_infrastructure', 'share_agriculture_pasture_mosaic', 'share_forest_level2']].head())
    print('Rows:', len(df))
