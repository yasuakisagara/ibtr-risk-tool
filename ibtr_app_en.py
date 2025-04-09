import streamlit as st
import pandas as pd
import numpy as np

# Cox model coefficients
# variable name, label, log(HR), SE
variables = [
    ("agecategory_<40", "Under 40", 0.925107, 0.447266),
    ("agecategory_40s", "40s (reference)", 0.0, 0.0),
    ("agecategory_50s", "50s", -0.260198, 0.132907),
    ("agecategory_60s", "60s", -0.537844, 0.169046),
    ("agecategory_70+", "70 or older", -0.642398, 0.188960),

    ("finalmargin_negative", "Negative margin (reference)", 0.0, 0.0),
    ("finalmargin_close", "Close margin", 1.112084, 0.523271),
    ("finalmargin_positive", "Positive margin", 1.481605, 0.416883),

    ("pT_1", "pT1 (reference)", 0.0, 0.0),
    ("pT_2", "pT2", 1.123930, 0.284657),
    ("pT_3", "pT3", 1.789473, 0.350000),

    ("grade_1", "Grade 1 (reference)", 0.0, 0.0),
    ("grade_2", "Grade 2", 0.625418, 0.274052),
    ("grade_3", "Grade 3", 1.213716, 0.273415),

    ("lvi", "Lymphovascular invasion (LVI)", 0.774492, 0.311122),
    ("hormone_receptor", "Hormone receptor positive", -0.756010, 0.377652),
    ("her2", "HER2 positive", -0.030972, 0.295476),
    ("radiation", "Received radiation therapy", -1.010091, 0.284721),
    ("chemotherapy", "Received chemotherapy", -0.368108, 0.299216),
    ("endocrine", "Received endocrine therapy", -0.808540, 0.300993),
    ("targeted", "Received targeted therapy", -0.456789, 0.250000),
]

baseline_survival = {"5y": 0.94, "10y": 0.86}

st.title("IBTR Risk Estimation Tool")

# Radio button selections
age = st.radio("Age category", ["Under 40", "40s (reference)", "50s", "60s", "70 or older"])
margin = st.radio("Final surgical margin", ["Negative margin (reference)", "Close margin", "Positive margin"])
t_stage = st.radio("Pathological T stage", ["pT1 (reference)", "pT2", "pT3"])
grade = st.radio("Histologic grade", ["Grade 1 (reference)", "Grade 2", "Grade 3"])

# Checkboxes
lvi = st.checkbox("Lymphovascular invasion present")
hormone_receptor = st.checkbox("Hormone receptor positive")
her2 = st.checkbox("HER2 positive")
radiation = st.checkbox("Received radiation therapy")
chemotherapy = st.checkbox("Received chemotherapy")
targeted = st.checkbox("Received targeted therapy")

# Endocrine therapy only if hormone receptor is positive
endocrine = False
if hormone_receptor:
    endocrine = st.checkbox("Received endocrine therapy")

# Create input dict
input_dict = {var: 0 for var, _, _, _ in variables}

# Map selections to variable names
input_dict[f"agecategory_{age.split()[0].replace('<','<').replace('70','70+').replace('40s','40s').replace('50s','50s').replace('60s','60s')}"] = 1
input_dict[f"finalmargin_{'negative' if 'Negative' in margin else 'close' if 'Close' in margin else 'positive'}"] = 1
input_dict[f"pT_{t_stage[2]}"] = 1
input_dict[f"grade_{grade[6]}"] = 1

input_dict["lvi"] = int(lvi)
input_dict["hormone_receptor"] = int(hormone_receptor)
input_dict["her2"] = int(her2)
input_dict["radiation"] = int(radiation)
input_dict["chemotherapy"] = int(chemotherapy)
input_dict["endocrine"] = int(endocrine)
input_dict["targeted"] = int(targeted)

# Calculate xb and standard error
xb = 0.0
se_sum = 0.0
for var, label, loghr, se in variables:
    value = input_dict[var]
    xb += loghr * value
    se_sum += (se * value) ** 2
se_total = np.sqrt(se_sum)

# Calculate IBTR risk and 95% CI
results = {}
for year, S0 in baseline_survival.items():
    risk = 1 - S0 ** np.exp(xb)
    risk_lower = 1 - S0 ** np.exp(xb - 1.96 * se_total)
    risk_upper = 1 - S0 ** np.exp(xb + 1.96 * se_total)
    results[year] = (risk, risk_lower, risk_upper)

if st.button("Calculate IBTR Risk"):
    for year, (r, lower, upper) in results.items():
        st.subheader(f"Estimated IBTR risk at {year}: {r*100:.1f}%")
        st.write(f"95% Confidence Interval: {lower*100:.1f}% - {upper*100:.1f}%")

    # Explanation and references
    st.markdown("""
---
### About this tool
This multi-center retrospective cohort study included women who underwent partial mastectomy for invasive breast cancer between 2008 and 2017. Cases involving conversion to mastectomy, use of neoadjuvant chemotherapy, bilateral/multiple cancers, or missing key data were excluded.

Prediction models were developed using Cox proportional hazards regression and validated via bootstrap resampling. Model performance was assessed using Harrell’s C-index, Brier scores, calibration plots, and goodness-of-fit tests. The estimated cumulative incidence of IBTR, which served as the baseline for the prediction model, was calculated using the Fine and Gray model, treating death as a competing risk.

We used Hazard Ratio from the multi-institutional cohort study comprized of 9232 patients. We performed validation by Discrimination and Calibration of Cox Regression Models:
- Bootstrap validation (500 iterations)
- Performance assessed using Harrell’s C-index and Brier score
- Calibration plot was made to evaluate concordance between the estimated risk and observed risk

HRs of chemotherapy, endocrine therapy, radiotherapy, and targeted therapy were used from meta-analysis of EBCTCG (Lancet 2005, 2011).

This model is presented by Yasuaki Sagara et al. in ASCO 2025 Chicago.

### Disclaimer
This tool is intended for academic and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Please consult with a healthcare provider for medical guidance.

""")
