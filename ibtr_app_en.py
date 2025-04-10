# Multilingual IBTR Prediction Tool with PDF Export
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from io import BytesIO
from fpdf import FPDF

# Sidebar language selector
lang = st.sidebar.selectbox("Language / 言語", ["English", "日本語"])

# Translations dictionary
T = {
    "title": {
        "English": "IBTR Risk Prediction Tool Integrating Real-World Data and Evidence from Meta-Analyses",
        "日本語": "実臨床データとメタアナリシスに基づく乳房内再発リスク予測ツール"
    },
    "version": {"English": "Version 1.0", "日本語": "バージョン1.0"},
    "description": {
        "English": "Please enter the patient's clinical and pathological information below. The tool will estimate the 5-year and 10-year risk of ipsilateral breast tumor recurrence (IBTR) based on a validated prediction model.",
        "日本語": "以下に患者の臨床および病理情報を入力してください。このツールは検証済みの予測モデルに基づいて5年および10年の乳房内再発リスクを推定します。"
    },
    "calculate": {"English": "Calculate IBTR Risk", "日本語": "乳房内再発リスクを計算"},
    "download": {"English": "Download Results as PDF", "日本語": "PDFとして結果をダウンロード"}
}

# Display logo and title
st.image("logo.png", width=180)
st.markdown(f"## {T['title'][lang]}")
st.markdown(f"### {T['version'][lang]}")
st.markdown(T['description'][lang])

# Radio buttons
age = st.radio("Age category", ["Under 40", "40s", "50s", "60s", "70 or older"])
margin = st.radio("Final surgical margin", ["Negative margin", "Close margin", "Positive margin"])
t_stage = st.radio("Pathological T stage", ["pT1", "pT2", "pT3"])
grade = st.radio("Histologic grade", ["Grade 1", "Grade 2", "Grade 3"])

# Checkboxes
lvi = st.checkbox("Lymphovascular invasion present")
hormone_receptor = st.checkbox("Hormone receptor positive")
her2 = st.checkbox("HER2 positive")
radiation = st.checkbox("Received radiation therapy")
chemotherapy = st.checkbox("Received chemotherapy")

# Conditional therapy checkboxes
targeted = st.checkbox("Received targeted therapy") if her2 else False
endocrine = st.checkbox("Received endocrine therapy") if hormone_receptor else False

# Input dictionary setup
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

input_dict = {var: 0 for var, _, _, _ in variables}
input_dict[f"agecategory_{age.split()[0].replace('<','<').replace('70','70+').replace('40s','40s').replace('50s','50s').replace('60s','60s')}"] = 1
input_dict[f"finalmargin_{'negative' if 'Negative' in margin else 'close' if 'Close' in margin else 'positive'}"] = 1
input_dict[f"pT_{t_stage[2]}"] = 1
input_dict[f"grade_{grade[6]}"] = 1
input_dict.update({
    "lvi": int(lvi),
    "hormone_receptor": int(hormone_receptor),
    "her2": int(her2),
    "radiation": int(radiation),
    "chemotherapy": int(chemotherapy),
    "endocrine": int(endocrine),
    "targeted": int(targeted)
})

# Risk calculation
baseline_survival = {"5y": 0.94, "10y": 0.86}
xb, se_sum = 0.0, 0.0
for var, _, loghr, se in variables:
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

# Display results
if st.button(T['calculate'][lang]):
    for year, (r, lower, upper) in results.items():
        st.subheader(f"{year} IBTR Risk: {r*100:.1f}%")
        st.write(f"95% CI: {lower*100:.1f}% - {upper*100:.1f}%")

    # PDF generation
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="IBTR Risk Prediction Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Date: {date.today()}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    for key, value in input_dict.items():
        if value == 1:
            pdf.cell(200, 8, txt=f"{key.replace('_', ' ').title()} : Yes", ln=True)
    for year, (r, lower, upper) in results.items():
        pdf.ln(2)
        pdf.cell(200, 10, txt=f"{year} IBTR Risk: {r*100:.1f}% (95% CI: {lower*100:.1f}% - {upper*100:.1f}%)", ln=True)

    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    st.download_button(
        label=T['download'][lang],
        data=pdf_buffer.getvalue(),
        file_name="ibtr_risk_report.pdf",
        mime="application/pdf"
    )
