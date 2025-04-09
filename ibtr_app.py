import streamlit as st
import pandas as pd
import numpy as np

# Coxモデル用のlog(HR)とSEの情報（Excelから取得した想定）
data = [
    # 変数名, 表示名, log(HR), SE
    ("agecategory_40未満", "40歳未満", 0.925107, 0.447266),
    ("agecategory_40代", "40代（参照）", 0.0, 0.0),
    ("agecategory_50代", "50代", -0.260198, 0.132907),
    ("agecategory_60代", "60代", -0.537844, 0.169046),
    ("agecategory_70歳以上", "70歳以上", -0.642398, 0.188960),

    ("finalmargin_陰性", "陰性断端（参照）", 0.0, 0.0),
    ("finalmargin_近接", "近接断端", 1.112084, 0.523271),
    ("finalmargin_陽性", "陽性断端", 1.481605, 0.416883),

    ("pT_1", "pT1（参照）", 0.0, 0.0),
    ("pT_2", "pT2", 1.123930, 0.284657),
    ("pT_3", "pT3", 1.789473, 0.350000),

    ("grade_1", "Grade 1（参照）", 0.0, 0.0),
    ("grade_2", "Grade 2", 0.625418, 0.274052),
    ("grade_3", "Grade 3", 1.213716, 0.273415),

    ("lvi", "LVIあり", 0.774492, 0.311122),
    ("hormone_receptor", "ホルモン受容体陽性", -0.756010, 0.377652),
    ("her2", "HER2陽性", -0.030972, 0.295476),
    ("radiation", "放射線治療あり", -1.010091, 0.284721),
    ("chemotherapy", "化学療法あり", -0.368108, 0.299216),
    ("endocrine", "周術期内分泌療法あり", -0.808540, 0.300993),
]

# ベースライン再発率
baseline_survival = {"5y": 0.94, "10y": 0.86}

st.title("乳房内再発（IBTR）予測ツール")

# ラジオボタン選択肢
age = st.radio("年齢カテゴリ", ["40歳未満", "40代（参照）", "50代", "60代", "70歳以上"])
margin = st.radio("最終切除断端", ["陰性断端（参照）", "近接断端", "陽性断端"])
t_stage = st.radio("病理T分類", ["pT1（参照）", "pT2", "pT3"])
grade = st.radio("グレード", ["Grade 1（参照）", "Grade 2", "Grade 3"])

# チェックボックス
lvi = st.checkbox("LVIあり")
hormone_receptor = st.checkbox("ホルモン受容体陽性")
her2 = st.checkbox("HER2陽性")
radiation = st.checkbox("放射線治療あり")
chemotherapy = st.checkbox("化学療法あり")

# ホルモン受容体陽性の場合のみ内分泌療法の選択肢を表示
endocrine = False
if hormone_receptor:
    endocrine = st.checkbox("周術期内分泌療法あり")

# 入力に応じた変数辞書を作成
input_dict = {}
for var, label, loghr, se in data:
    input_dict[var] = 0

input_dict[f"agecategory_{age.replace('（参照）', '')}"] = 1
input_dict[f"finalmargin_{margin.replace('断端（参照）', '').replace('断端', '')}"] = 1
input_dict[f"pT_{t_stage.replace('（参照）', '').replace('pT', '')}"] = 1
input_dict[f"grade_{grade[-2]}"] = 1
input_dict["lvi"] = int(lvi)
input_dict["hormone_receptor"] = int(hormone_receptor)
input_dict["her2"] = int(her2)
input_dict["radiation"] = int(radiation)
input_dict["chemotherapy"] = int(chemotherapy)
input_dict["endocrine"] = int(endocrine)

# ログ相対ハザードとSE合計を計算
xb = 0.0
se_sum = 0.0
for var, label, loghr, se in data:
    value = input_dict[var]
    xb += loghr * value
    se_sum += (se * value) ** 2
se_total = np.sqrt(se_sum)

# 生存率から再発率の計算
results = {}
for year, S0 in baseline_survival.items():
    risk = 1 - S0 ** np.exp(xb)
    risk_lower = 1 - S0 ** np.exp(xb - 1.96 * se_total)
    risk_upper = 1 - S0 ** np.exp(xb + 1.96 * se_total)
    results[year] = (risk, risk_lower, risk_upper)

if st.button("再発リスクを計算"):
    for year, (r, lower, upper) in results.items():
        st.subheader(f"{year}のIBTR推定リスク： {r*100:.1f}%")
        st.write(f"95%信頼区間： {lower*100:.1f}% - {upper*100:.1f}%")
