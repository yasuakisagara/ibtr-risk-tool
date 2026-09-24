"""Model 1.61. UI-independent calculation; coefficients in model.json."""
import json
import math
from pathlib import Path

MODEL = json.loads(Path(__file__).with_name('model.json').read_text(encoding='utf-8'))

def normalize(inputs):
    clean = {}
    for field in MODEL['fields']:
        key = field['id']
        inactive = (key == 'endocrine' and inputs.get('hormone_receptor') == '0') or (key == 'targeted' and inputs.get('her2') == '0')
        value = '0' if inactive else inputs.get(key)
        if value not in [option['value'] for option in field['options']]:
            raise ValueError(key)
        clean[key] = value
    return clean

def calculate(inputs):
    clean = normalize(inputs)
    xb = variance = 0.0
    for field in MODEL['fields']:
        value = clean[field['id']]
        categorical = len(field['options']) > 2
        key, active = (value, 1) if categorical else (field['id'], int(value))
        beta, se = MODEL['coefficients'][key]
        xb += beta * active
        variance += (se * active) ** 2
    se = math.sqrt(variance)
    results = {}
    for year, s0 in MODEL['baseline_survival'].items():
        results[year] = {name: 1 - s0 ** math.exp(z) for name, z in [('risk', xb), ('lower', xb - 1.96 * se), ('upper', xb + 1.96 * se)]}
    return {'input': clean, 'results': results}
