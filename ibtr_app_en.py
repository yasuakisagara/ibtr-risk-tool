# Multilingual IBTR Prediction Tool with PDF Export
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from io import BytesIO
from fpdf import FPDF

# Top-level language selector
lang = st.selectbox("Language / 言語", ["English", "日本語"])

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

label_map = {
    "English": {
        "agecategory_<40": "Age category: Under 40",
        "agecategory_40s": "Age category: 40s",
        "agecategory_50s": "Age category: 50s",
        "agecategory_60s": "Age category: 60s",
        "agecategory_70+": "Age category: 70 or older",
        "finalmargin_negative": "Final surgical margin: Negative",
        "finalmargin_close": "Final surgical margin: Close",
        "finalmargin_positive": "Final surgical margin: Positive",
        "pT_1": "Pathological T stage: pT1",
        "pT_2": "Pathological T stage: pT2",
        "pT_3": "Pathological T stage: pT3",
        "grade_1": "Histologic grade: Grade 1",
        "grade_2": "Histologic grade: Grade 2",
        "grade_3": "Histologic grade: Grade 3",
        "lvi": "Lymphovascular invasion: Present",
        "hormone_receptor": "Hormone receptor: Positive",
        "her2": "HER2 status: Positive",
        "radiation": "Adjuvant therapy: Radiation",
        "chemotherapy": "Adjuvant therapy: Chemotherapy",
        "endocrine": "Adjuvant therapy: Endocrine",
        "targeted": "Adjuvant therapy: Targeted"
    },
    "日本語": {
        "agecategory_<40": "年齢: 40歳未満",
        "agecategory_40s": "年齢: 40代",
        "agecategory_50s": "年齢: 50代",
        "agecategory_60s": "年齢: 60代",
        "agecategory_70+": "年齢: 70歳以上",
        "finalmargin_negative": "術後断端: 陰性",
        "finalmargin_close": "術後断端: 近接",
        "finalmargin_positive": "術後断端: 陽性",
        "pT_1": "腫瘍サイズ: pT1",
        "pT_2": "腫瘍サイズ: pT2",
        "pT_3": "腫瘍サイズ: pT3",
        "grade_1": "グレード: 1",
        "grade_2": "グレード: 2",
        "grade_3": "グレード: 3",
        "lvi": "脈管侵襲: あり",
        "hormone_receptor": "ホルモン受容体: 陽性",
        "her2": "HER2: 陽性",
        "radiation": "補助療法: 放射線治療",
        "chemotherapy": "補助療法: 化学療法",
        "endocrine": "補助療法: 内分泌療法",
        "targeted": "補助療法: 分子標的治療"
    }
}

# Display logo and title
st.image("logo.png", width=180)
st.markdown(f"## {T['title'][lang]}")
st.markdown(f"### {T['version'][lang]}")
st.markdown(T['description'][lang])
