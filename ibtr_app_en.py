# ibtr_app.py - Full Model with HR-based Calculation, Organized by Section (Corrected lang position)
import streamlit as st
import pandas as pd
import numpy as np

# Language selector must come first
lang = st.selectbox("Language / 言語", ["English", "日本語"])

# Translation dictionary (T) must come after lang is defined
T = {
    "title": {
        "English": "IBTR Risk Prediction Tool Integrating Real-World Data and Evidence from Meta-Analyses",
        "日本語": "実臨床データとメタアナリシスに基づく乳房内再発リスク予測ツール"
    },
    "version": {"English": "Version 1.0", "日本語": "バージョン1.0"},
    "description": {
        "English": "Please enter the patient's clinical and pathological information below.",
        "日本語": "以下に患者の臨床および病理情報を入力してください。"
    },
    "calculate": {"English": "Calculate IBTR Risk", "日本語": "乳房内再発リスクを計算"},
    "estimated_risk": {"English": "Estimated IBTR risk at", "日本語": "推定された乳房内再発リスク（"},
    "ci": {"English": "95% Confidence Interval", "日本語": "95%信頼区間"}
}

# --- Display title and description ---
st.image("logo.png", width=180)
st.markdown(f"## {T['title'][lang]}")
st.markdown(f"### {T['version'][lang]}")
st.markdown(T['description'][lang])

# --- Section: Patient Characteristics ---
st.markdown("### Patient Characteristics")

age = st.radio("Age category", ["Under 40", "40s", "50s", "60s", "70 or older"])
margin = st.radio("Final surgical margin", ["Negative margin", "Close margin", "Positive margin"])
t_stage = st.radio("Pathological T stage", ["pT1", "pT2", "pT3"])
grade = st.radio("Histologic grade", ["Grade 1", "Grade 2", "Grade 3"])
lvi = st.checkbox("Lymphovascular invasion present")
hormone_receptor = st.checkbox("Hormone receptor positive")
her2 = st.checkbox("HER2 positive")

# --- Section: Treatment Information ---
st.markdown("### Treatment")

radiation = st.checkbox("Received radiation therapy")
chemotherapy = st.checkbox("Received chemotherapy")
targeted = st.checkbox("Received targeted therapy") if her2 else False
endocrine = st.checkbox("Received endocrine therapy") if hormone_receptor else False

# --- HR Model Coefficients ---
variables = [
    ("agecategory_<40", "Under 40", 0.925107351, 0.4472657),
    ("agecategory_40s", "40s", 0.0, 0.0),
    ("agecategory_50s", "50s", -0.260198172, 0.1329072),
    ("agecategory_60s", "60s", -0.453197487, 0.1193687),
    ("agecategory_70+", "70 or older", -0.594712977, 0.1222106),
    ("finalmargin_negative", "Negative margin", 0.0, 0.0),
    ("finalmargin_close", "Close margin", 0.533038286, 0.2443688),
    ("finalmargin_positive", "Positive margin", 0.817501467, 0.4696936),
    ("pT_1", "pT1", 0.0, 0.0),
    ("pT_2", "pT2", 0.215485503, 0.195763),
    ("pT_3", "pT3", 0.680535486, 1.414311),
    ("grade_1", "Grade 1", 0.0, 0.0),
    ("grade_2", "Grade 2", 0.135309436, 0.1691389),
    ("grade_3", "Grade 3", 0.396416963, 0.3100963),
    ("lvi", "Lymphovascular invasion (LVI)", 0.445005642, 0.2203228),
    ("hormone_receptor", "Hormone receptor positive", -0.141806451, 0.2086384),
    ("her2", "HER2 positive", 0.407543613, 0.4333971),
    ("radiation", "Received radiation therapy", -1.171182982, 0.04),
    ("chemotherapy", "Received chemotherapy", -0.46203546, 0.08),
    ("endocrine", "Received endocrine therapy", -0.616186139, 0.07),
    ("targeted", "Received targeted therapy", -0.203693927, 0.2783889),
]

baseline_survival = {"5y": 0.94, "10y": 0.86}

# --- Input dictionary ---
input_dict = {var: 0 for var, _, _, _ in variables}
input_dict[f"agecategory_{age.split()[0].replace('<','<').replace('70','70+')}"] = 1
input_dict[f"finalmargin_{'negative' if 'Negative' in margin else 'close' if 'Close' in margin else 'positive'}"] = 1
input_dict[f"pT_{t_stage[2]}"] = 1
input_dict[f"grade_{grade[-1]}"] = 1
input_dict.update({
    "lvi": int(lvi),
    "hormone_receptor": int(hormone_receptor),
    "her2": int(her2),
    "radiation": int(radiation),
    "chemotherapy": int(chemotherapy),
    "endocrine": int(endocrine),
    "targeted": int(targeted)
})

# --- Risk calculation ---
xb = 0.0
se_sum = 0.0
for var, label, loghr, se in variables:
    value = input_dict[var]
    xb += loghr * value
    se_sum += (se * value) ** 2
se_total = np.sqrt(se_sum)

results = {}
for year, S0 in baseline_survival.items():
    risk = 1 - S0 ** np.exp(xb)
    risk_lower = 1 - S0 ** np.exp(xb - 1.96 * se_total)
    risk_upper = 1 - S0 ** np.exp(xb + 1.96 * se_total)
    results[year] = (risk, risk_lower, risk_upper)

# --- Output ---
if st.button(T['calculate'][lang]):
    for year, (r, lower, upper) in results.items():
        st.subheader(f"{T['estimated_risk'][lang]} {year}: {r*100:.1f}%")
        st.write(f"{T['ci'][lang]}: {lower*100:.1f}% - {upper*100:.1f}%")

# --- Footnote ---
st.markdown("""
---
### About this tool
This prediction model was developed and validated through a multi-center retrospective cohort study including women who underwent partial mastectomy for invasive breast cancer between 2008 and 2017. Cases involving conversion to mastectomy, use of neoadjuvant chemotherapy, bilateral/multiple cancers, or missing key data were excluded.

The study was conducted as a collaborative project of the Japanese Breast Cancer Society Collaborative Research Group and involved seven institutions in Japan: Cancer Institute Hospital of JFCR, St. Luke's International Hospital, Kyoto University Hospital, Osaka Metropolitan University Hospital, Mie University Hospital, Okayama University Hospital, and Hakuaikai Sagara Hospital.

Candidate models were developed using Cox proportional hazards regression and validated via bootstrap resampling. Model performance was assessed using Harrell’s C-index, Brier scores, calibration plots, and goodness-of-fit tests. The estimated cumulative incidence of ipsilateral breast tumor recurrence (IBTR), which served as the baseline for the prediction model, was calculated using the Fine and Gray model, treating death as a competing risk.

We used hazard ratios from the multi-institutional cohort study comprising 9,232 patients. Validation was performed by assessing discrimination and calibration of Cox regression models:

- Bootstrap validation (500 iterations)
- Performance assessed using Harrell’s C-index and Brier score
- Calibration plot was made to evaluate concordance between the estimated risk and observed risk

In addition, we incorporated hazard ratios from the EBCTCG meta-analyses (Lancet 2005, 2011) to account for the effects of adjuvant therapies on reducing the risk of isolated local recurrence: chemotherapy (HR 0.63, SE 0.08), endocrine therapy (HR 0.54, SE 0.07), and radiotherapy (HR 0.31, SE 0.04).

This work was presented at the Annual Meeting of the American Society of Clinical Oncology 2025 in Chicago (Abstract number: 575).

### Disclaimer
This tool is intended for academic and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Please consult with a healthcare provider for medical guidance.
""")
