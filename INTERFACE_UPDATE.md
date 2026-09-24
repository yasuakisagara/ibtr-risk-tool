# IBTR interface refresh

The bilingual `ibtr_app_en.py` now presents inputs and results side by side, with explicit unanswered options, common-scale risk/interval plots and same-background treatment comparison. Canonical values survive language changes, while clinical input changes clear stale results. Dependent therapy inputs clear when receptor positivity is removed.

Model 1.61 is unchanged. `model.json` records coefficients, standard errors, baseline survival and source commit. `ibtr_model.py` separates calculation from the UI. The older `ibtr_app.py` remains untouched because it uses a different model.

The privacy copy now describes Streamlit server-side processing. The original approximate interval calculation is retained and its covariance/baseline uncertainty limitations are disclosed.

Validation: 9,720 valid scenarios agreed with the original implementation; the accompanying Sites JavaScript calculator agreed within 1e-12 absolute probability. The regression fixtures are frozen reference results sampled across that complete set. Streamlit 1.33 AppTest passed language preservation, completeness, stale-result clearing, treatment comparison, dependency clearing and reset.

Run `python tests/check_model.py` and `python tests/check_interface.py` with existing requirements installed. Start with `streamlit run ibtr_app_en.py`. Dependencies are unchanged. Browser visual QA was not performed.
