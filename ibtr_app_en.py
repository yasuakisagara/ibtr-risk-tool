# ibtr_app.py - Streamlit App for IBTR Prediction (Multilingual + PDF Export)
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from io import BytesIO
from fpdf import FPDF
import os
import urllib.request

# Language selector
lang = st.selectbox("Language / 言語", ["English", "日本語"])

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
    "download": {"English": "Download Results as PDF", "日本語": "PDFとして結果をダウンロード"}
}

label_map = {
    "English": {
        "agecategory_<40": "Age category: Under 40",
        "agecategory_40s": "Age category: 40s",
        "agecategory_50s": "Age category: 50s",
        "agecategory_60s": "Age category: 60s",
        "agecategory_70+": "Age category: 70 or older",
        "finalmargin_negative": "Final margin: Negative",
        "finalmargin_close": "Final margin: Close",
        "finalmargin_positive": "Final margin: Positive",
        "pT_1": "Tumor size: pT1",
        "pT_2": "Tumor size: pT2",
        "pT_3": "Tumor size: pT3",
        "grade_1": "Grade: 1",
        "grade_2": "Grade: 2",
        "grade_3": "Grade: 3",
        "lvi": "Lymphovascular invasion",
        "hormone_receptor": "Hormone receptor positive",
        "her2": "HER2 positive",
        "radiation": "Radiation therapy",
        "chemotherapy": "Chemotherapy",
        "endocrine": "Endocrine therapy",
        "targeted": "Targeted therapy"
    },
    "日本語": {
        "agecategory_<40": "年齢: 40歳未満",
        "agecategory_40s": "年齢: 40代",
        "agecategory_50s": "年齢: 50代",
        "agecategory_60s": "年齢: 60代",
        "agecategory_70+": "年齢: 70歳以上",
        "finalmargin_negative": "断端: 陰性",
        "finalmargin_close": "断端: 近接",
        "finalmargin_positive": "断端: 陽性",
        "pT_1": "腫瘍サイズ: pT1",
        "pT_2": "腫瘍サイズ: pT2",
        "pT_3": "腫瘍サイズ: pT3",
        "grade_1": "グレード: 1",
        "grade_2": "グレード: 2",
        "grade_3": "グレード: 3",
        "lvi": "脈管侵襲あり",
        "hormone_receptor": "ホルモン受容体陽性",
        "her2": "HER2陽性",
        "radiation": "放射線治療あり",
        "chemotherapy": "化学療法あり",
        "endocrine": "内分泌療法あり",
        "targeted": "分子標的治療あり"
    }
}

st.image("logo.png", width=180)
st.markdown(f"## {T['title'][lang]}")
st.markdown(f"### {T['version'][lang]}")
st.markdown(T['description'][lang])

age = st.radio("Age category", ["Under 40", "40s", "50s", "60s", "70 or older"])
margin = st.radio("Final surgical margin", ["Negative margin", "Close margin", "Positive margin"])
t_stage = st.radio("Pathological T stage", ["pT1", "pT2", "pT3"])
grade = st.radio("Histologic grade", ["Grade 1", "Grade 2", "Grade 3"])

lvi = st.checkbox("Lymphovascular invasion present")
hormone_receptor = st.checkbox("Hormone receptor positive")
her2 = st.checkbox("HER2 positive")
radiation = st.checkbox("Received radiation therapy")
chemotherapy = st.checkbox("Received chemotherapy")
targeted = st.checkbox("Received targeted therapy") if her2 else False
endocrine = st.checkbox("Received endocrine therapy") if hormone_receptor else False

variables = [
    ("agecategory_<40", 0.925107351, 0.4472657),
    ("agecategory_40s", 0.0, 0.0),
    ("agecategory_50s", -0.260198172, 0.1329072),
    ("agecategory_60s", -0.453197487, 0.1193687),
    ("agecategory_70+", -0.594712977, 0.1222106),
    ("finalmargin_negative", 0.0, 0.0),
    ("finalmargin_close", 0.533038286, 0.2443688),
    ("finalmargin_positive", 0.817501467, 0.4696936),
    ("pT_1", 0.0, 0.0),
    ("pT_2", 0.215485503, 0.195763),
    ("pT_3", 0.680535486, 1.414311),
    ("grade_1", 0.0, 0.0),
    ("grade_2", 0.135309436, 0.1691389),
    ("grade_3", 0.396416963, 0.3100963),
    ("lvi", 0.445005642, 0.2203228),
    ("hormone_receptor", -0.141806451, 0.2086384),
    ("her2", 0.407543613, 0.4333971),
    ("radiation", -1.171182982, 0.04),
    ("chemotherapy", -0.46203546, 0.08),
    ("endocrine", -0.616186139, 0.07),
    ("targeted", -0.203693927, 0.2783889),
]

input_dict = {key: 0 for key, _, _ in variables}
input_dict[f"agecategory_{age.split()[0].replace('<','<').replace('70','70+')}"] = 1
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

baseline_survival = {"5y": 0.94, "10y": 0.86}
xb, se_sum = 0.0, 0.0
for var, loghr, se in variables:
    value = input_dict[var]
    xb += loghr * value
    se_sum += (se * value) ** 2
se_total = np.sqrt(se_sum)

results = {}
for year, S0 in baseline_survival.items():
    risk = 1 - S0 ** np.exp(xb)
    lower = 1 - S0 ** np.exp(xb - 1.96 * se_total)
    upper = 1 - S0 ** np.exp(xb + 1.96 * se_total)
    results[year] = (risk, lower, upper)

if st.button(T["calculate"][lang]):
    for year, (r, l, u) in results.items():
        st.write(f"{year} IBTR Risk: {r*100:.1f}% (95% CI: {l*100:.1f}% - {u*100:.1f}%)")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="IBTR Risk Prediction Report", ln=True, align='C')
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 10, txt=f"Date: {date.today()}", ln=True)
    pdf.ln(5)
    for key, val in input_dict.items():
        if val == 1 and key in label_map[lang]:
            pdf.cell(200, 8, txt=label_map[lang][key], ln=True)
    for year, (r, l, u) in results.items():
        pdf.cell(200, 10, txt=f"{year} IBTR Risk: {r*100:.1f}% (95% CI: {l*100:.1f}% - {u*100:.1f}%)", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    st.download_button(
        label=T["download"][lang],
        data=buffer.getvalue(),
        file_name="ibtr_risk_report.pdf",
        mime="application/pdf"
    )
    
 # PDF 出力処理
    font_path = "ipaexg.ttf"
    if not os.path.exists(font_path):
        urllib.request.urlretrieve(
            "https://moji.or.jp/wp-content/ipafont/IPAexfont/ipaexg00401/ipaexg.ttf",
            font_path
        )

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("IPAexGothic", fname=font_path, uni=True)
    pdf.set_font("IPAexGothic", size=12)
    pdf.cell(200, 10, txt="IBTR Risk Prediction Report", ln=True, align='C')
    pdf.set_font("IPAexGothic", size=11)
    pdf.cell(200, 10, txt=f"Date: {date.today()}", ln=True)
    pdf.ln(5)
    for key, val in input_dict.items():
        if val == 1 and key in label_map[lang]:
            pdf.cell(200, 8, txt=label_map[lang][key], ln=True)
    for year, (r, l, u) in results.items():
        pdf.cell(200, 10, txt=f"{year} IBTR Risk: {r*100:.1f}% (95% CI: {l*100:.1f}% - {u*100:.1f}%)", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    st.download_button(
        label=T["download"][lang],
        data=buffer.getvalue(),
        file_name="ibtr_risk_report.pdf",
        mime="application/pdf"
    )
