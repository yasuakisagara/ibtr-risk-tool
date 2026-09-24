import json, sys, pathlib, math
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ibtr_model import calculate
cases = json.loads(pathlib.Path(__file__).with_name('model_v1_61_cases.json').read_text())
for case in cases:
    result = calculate(case['input'])
    for year in case['results']:
        for key in case['results'][year]:
            assert math.isclose(result['results'][year][key], case['results'][year][key], abs_tol=1e-12)
for invalid in [{}, dict(cases[0]['input'], age='invalid')]:
    try: calculate(invalid)
    except ValueError: pass
    else: raise AssertionError('Invalid inputs accepted')
print(f'{len(cases)} frozen original-model cases and invalid-input checks passed')
