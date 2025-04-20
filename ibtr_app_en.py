## ibtr_app.py - Full Model with HR-based Calculation, ver1.5　logo cloudinary
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Language selector must come first
lang = st.selectbox("Language / 言語", ["English", "日本語"])

# Translation dictionary (T) must come after lang is defined
T = {
    "title": {
        "English": "IBTR Risk Estimation Tool Integrating Real-World Data and Evidence from Meta-Analyses",
        "日本語": "リアルワールドデータとメタ解析に基づくIBTR発症率推定ツール"
    },
    "version": {"English": "Version 1.5", "日本語": "バージョン1.5"},
    "description": {
        "English": "Please enter the patient's clinical and pathological information below.",
        "日本語": "以下に患者の臨床および病理情報を入力してください。"
    },
    "calculate": {"English": "Calculate IBTR Risk", "日本語": "乳戸内再発リスクを計算"},
    "estimated_risk": {"English": "Estimated IBTR risk at", "日本語": "推定された乳戸内再発リスク（"},
    "ci": {"English": "95% Confidence Interval", "日本語": "95%信頼区間"}
}

# --- Display title and description ---
logo_url = "https://res.cloudinary.com/dqlawunmg/image/upload/v1745049473/logo_pjk79t.png"
st.image(logo_url, width=250)
    
st.markdown(f"## {T['title'][lang]}")
st.markdown(f"### {T['version'][lang]}")
st.markdown(T['description'][lang])

# Patient Characteristics (multilingual)
if lang == "日本語":
    st.markdown("### 患者背景")
    age = st.radio("年齢カテゴリ", ["40歳未満", "40代", "50代", "60代", "70歳以上"])
    margin = st.radio("最終断端状況", ["陰性断端", "近接断端(<5mm)", "陽性断端"])
    t_stage = st.radio("病理T分類", ["pT1", "pT2", "pT3（極少数）"])
    grade = st.radio("結等学的グレード", ["Grade 1", "Grade 2", "Grade 3"])
    lvi = st.checkbox("脈管侵撃あり")
    hormone_receptor = st.checkbox("ホルモン受容体陽性")
    her2 = st.checkbox("HER2受容体陽性")
else:
    st.markdown("### Patient Characteristics")
    age = st.radio("Age category", ["Under 40", "40s", "50s", "60s", "70 or older"])
    margin = st.radio("Final surgical margin", ["Negative margin", "Close margin(<5mm)", "Positive margin"])
    t_stage = st.radio("Pathological T stage", ["pT1", "pT2", "pT3 (very few cases)"])
    grade = st.radio("Histologic grade", ["Grade 1", "Grade 2", "Grade 3"])
    lvi = st.checkbox("Lymphovascular invasion: Present")
    hormone_receptor = st.checkbox("Hormone receptor: Positive")
    her2 = st.checkbox("HER2 status: Positive")

# Treatment Section
if lang == "日本語":
    st.markdown("### 治療")
    radiation = st.checkbox("放射線療法あり")
    chemotherapy = st.checkbox("化学療法あり")
    targeted = st.checkbox("抗HER2療法あり") if her2 else False
    endocrine = st.checkbox("内分泌療法あり") if hormone_receptor else False
else:
    st.markdown("### Treatment")
    radiation = st.checkbox("Received radiation therapy")
    chemotherapy = st.checkbox("Received chemotherapy")
    targeted = st.checkbox("Received Anti-HER2 therapy") if her2 else False
    endocrine = st.checkbox("Received endocrine therapy") if hormone_receptor else False

# --- HR Model Coefficients  ---
variables = [
    ("agecategory_<40", "Under 40", 0.874573, 0.417364),
    ("agecategory_40s", "40s", 0.0, 0.0),
    ("agecategory_50s", "50s", -0.182361, 0.136322),
    ("agecategory_60s", "60s", -0.267784, 0.132929),
    ("agecategory_70+", "70 or older", -0.489379, 0.129613),
    ("finalmargin_negative", "Negative margin", 0.0, 0.0),
    ("finalmargin_close(<5mm)", "Close margin(<5mm)", 0.511362, 0.227433),
    ("finalmargin_positive", "Positive margin", 0.861087, 0.456145),
    ("pT_1", "pT1", 0.0, 0.0),
    ("pT_2", "pT2", 0.134593, 0.170066),
    ("pT_3", "pT3", 0.682241, 1.413398),
    ("grade_1", "Grade 1", 0.0, 0.0),
    ("grade_2", "Grade 2", 0.192654, 0.171228),
    ("grade_3", "Grade 3", 0.413136, 0.297550),
    ("lvi", "Lymphovascular invasion (LVI)", 0.415052, 0.201020),
    ("hormone_receptor", "Hormone receptor positive", -0.107287, 0.213524),
    ("her2", "HER2 positive", 0.383047, 0.408019),
    ("radiation", "Received radiation therapy", -1.171182982, 0.04),
    ("chemotherapy", "Received chemotherapy", -0.46203546, 0.08),
    ("endocrine", "Received endocrine therapy", -0.616186139, 0.07),
    ("targeted", "Received Anti-HER2 therapy", -0.195477, 0.264011),
]

baseline_survival = {"5y": 0.9425415, "10y": 0.8746572}

# --- Input dictionary ---

# マッピング用辞書を定義
age_mapping = {
    "Under 40": "agecategory_<40",
    "40s": "agecategory_40s",
    "50s": "agecategory_50s",
    "60s": "agecategory_60s",
    "70 or older": "agecategory_70+",
    "40歳未満": "agecategory_<40",
    "40代": "agecategory_40s",
    "50代": "agecategory_50s",
    "60代": "agecategory_60s",
    "70歳以上": "agecategory_70+"
}

margin_mapping = {
    "Negative margin": "finalmargin_negative",
    "Close margin(<5mm)": "finalmargin_close(<5mm)",
    "Positive margin": "finalmargin_positive",
    "陰性断端": "finalmargin_negative",
    "近接断端(<5mm)": "finalmargin_close(<5mm)",
    "陽性断端": "finalmargin_positive"
}

t_stage_mapping = {
    "pT1": "pT_1",
    "pT2": "pT_2",
    "pT3": "pT_3",
    "pT3（極少数）": "pT_3",
    "pT3 (very few cases)": "pT_3"
}

grade_mapping = {
    "Grade 1": "grade_1",
    "Grade 2": "grade_2",
    "Grade 3": "grade_3"
}

# input_dictの設定
input_dict = {var: 0 for var, _, _, _ in variables}
input_dict[age_mapping[age]] = 1
input_dict[margin_mapping[margin]] = 1
input_dict[t_stage_mapping[t_stage]] = 1
input_dict[grade_mapping[grade]] = 1

# 残りのチェックボックス項目
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

# Result output section
if st.button(T['calculate'][lang]):
    for year, (r, lower, upper) in results.items():
        if lang == "日本語":
            year_label = year.replace("y", "年")
            st.markdown(f"### {year_label} 再発リスク")
        else:
            st.markdown(f"### Estimated {year} IBTR Risk")

        # Display risk point and CI numerically
        st.markdown(f"<div style='font-size: 24px; font-weight: bold;'>{r*100:.1f}%</div>", unsafe_allow_html=True)
        if lang == "日本語":
            st.caption(f"95%信頼区間: {lower*100:.1f}% - {upper*100:.1f}%")
        else:
            st.caption(f"95% Confidence Interval: {lower*100:.1f}% - {upper*100:.1f}%")

        # Draw CI bar with matplotlib
        fig, ax = plt.subplots(figsize=(4.5, 0.8))
        ax.hlines(1, lower, upper, colors='gray', linewidth=3)
        ax.plot(r, 1, 'o', color='red' if year == "5y" else 'orange', markersize=10)
        ax.set_xlim(0, 1)
        ax.set_yticks([])
        ax.set_xticks([0.1, 0.2, 0.3, 0.4, 0.5])
        ax.set_xlabel("Probability")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('lightgray')
        st.pyplot(fig)

# Footnote section (multilingual)
if lang == "日本語":
    st.markdown("""
---
### 本ツールについて
本リスク推定ツールは、2008年から2017年に部分切除術を受けた浸潤性乳がん女性を対象とした多施設後ろ向きコホート研究により開発・検証されました。全摘術への移行、術前化学療法の使用、両側・多発がん、主要データの欠落などの症例は除外されました。

本研究は日本乳癌学会共同研究グループによる共同研究として実施され、以下の日本国内の7つの施設が参加しました：がん研究会有明病院、聖路加国際病院、京都大学医学部附属病院、大阪公立大学医学部附属病院、三重大学医学部附属病院、岡山大学病院、博愛会相良病院

モデルは Cox 比例ハザード回帰を用いて構築され、ブートストラップ再サンプリングにより検証されました。モデル性能は Harrell のC-index、Brierスコア、キャリブレーションプロット、および適合度検定で評価されました。再発予測のベースラインとして、Fine and Gray モデルにより死亡を競合リスクとした IBTR の累積発生率を使用しました。

8,938人の患者を対象とした多施設共同研究のハザード比を用いて検証され、以下を実施しました：
- ブートストラップ検証（500回）
- HarrellのC-indexとBrierスコアによる性能評価(Harrell's C: 0.65, Brier 0.036)
- 推定リスクと実測リスクの一致度を評価するキャリブレーションプロット

さらに、局所再発リスク低減効果を考慮するため、EBCTCG メタアナリシス（Lancet 2005, 2011）から得られた以下の補助療法のHRを統合しました：化学療法（HR 0.63, SE 0.08）、内分泌療法（HR 0.54, SE 0.07）、放射線治療（HR 0.31, SE 0.04）

ツールの識別能や予測能には限界があり、特に対象症例が少ないポピュレーション（例：40歳未満や病理学的T3）では95%信頼区間が広く解釈に注意が必要です。

学会や論文にて本ツールの開発方法について近日報告予定です。報告後に参考文献を掲示いたします。


### 免責事項
このツールは学術目的および教育目的のために提供されており、医学的助言、診断、治療の代替とはなりません。医療上の判断は必ず医療従事者にご相談ください。
""")
else:
    st.markdown("""
---
### About this tool
This risk estimation tool was developed and validated through a multi-center retrospective cohort study including women who underwent partial mastectomy for invasive breast cancer between 2008 and 2017. Cases involving conversion to mastectomy, use of neoadjuvant chemotherapy, bilateral/multiple cancers, or missing key data were excluded.

The study was conducted as a collaborative project of the Japanese Breast Cancer Society Collaborative Research Group and involved seven institutions in Japan: Cancer Institute Hospital of JFCR, St. Luke's International Hospital, Kyoto University Hospital, Osaka Metropolitan University Hospital, Mie University Hospital, Okayama University Hospital, and Hakuaikai Sagara Hospital.

Candidate models were developed using Cox proportional hazards regression and validated via bootstrap resampling. Model performance was assessed using Harrell’s C-index, Brier scores, calibration plots, and goodness-of-fit tests. The estimated cumulative incidence of ipsilateral breast tumor recurrence (IBTR), which served as the baseline for the prediction model, was calculated using the Fine and Gray model, treating death as a competing risk.

We used hazard ratios from the multi-institutional cohort study comprising 8,938 patients. Internal validation was performed by assessing discrimination and calibration of Cox regression models:
- Bootstrap validation (500 iterations)
- Performance assessed using Harrell’s C-index and Brier score (Harrell’s C: 0.65, Brier score: 0.036)
- Calibration plot was made to evaluate concordance between the estimated risk and observed risk

In addition, we incorporated hazard ratios from the EBCTCG meta-analyses (Lancet 2005, 2011) to account for the effects of adjuvant therapies on reducing the risk of isolated local recurrence: chemotherapy (HR 0.63, SE 0.08), endocrine therapy (HR 0.54, SE 0.07), and radiotherapy (HR 0.31, SE 0.04).

The tool has limitations in its discrimination and predictive accuracy, particularly in subpopulations with small sample sizes (e.g., patients under 40 years or with pathological T3 tumors), where the 95% confidence intervals are wide and require cautious interpretation.

The development methodology of this tool will be reported at academic conferences and in peer-reviewed publications in the near future. The references will be provided after the presentation and publication.

### Disclaimer
This tool is intended for academic and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Please consult with a healthcare provider for medical guidance.
""")
    
# Footnote section (multilingual)
if lang == "日本語":
    st.markdown("""
---
### バージョン履歴
- ver1.0（2025年4月11日公表）：初期バージョン
- ver1.5（2025年4月17日更新）：データ整合性の見直しを行い、一部症例のIBTRイベント情報および分類を修正。
""")
else:
    st.markdown("""
---
### Version History
- ver1.0 (Released on April 11, 2025): Initial version
- ver1.5 (Updated on April 17, 2025): Minor revisions made to ensure data consistency, including adjustments to IBTR event classification.
""")

# --- Credit and Feedback section (multilingual) ---
st.markdown("---")  # 区切り線

if lang == "日本語":
    st.markdown("""
### クレジット
日本乳癌学会第29回研究班（班長：坂井威彦）において多施設共同研究が行われました。モデルの開発と検証およびウェブアプリの実装は、相良安昭により主に行われました。

© 日本乳癌学会第29回研究班  
出典を明記した上での学術・教育目的での引用・共有を歓迎します。無断の商用利用や改変はご遠慮ください。

### フィードバックのお願い
本ツールに関するご意見や不具合のご報告などがありましたら、以下のフォームよりお寄せください。  
いただいた内容は今後の改良や学術的評価の参考にさせていただきます。

[フィードバックフォームはこちら](https://docs.google.com/forms/d/e/1FAIpQLScZOEWa4osyS0K9Xg9Fq0p1EGeyyIOqXvfdkyxj07l9vyeGZw/viewform)
""")
else:
    st.markdown("""
### Credit
This multi-institutional research was conducted under the 29th Research Task Force of the Japanese Breast Cancer Society (Team Leader: Takehiko Sakai, MD, PhD).

Yasuaki Sagara, MD, MPH primarily developed and validated the prediction model and web application tool.

© 2025 Japanese Breast Cancer Society, Task Force 29  
Academic and educational use with proper attribution is encouraged. Commercial use or modification without permission is not allowed.

### Feedback
If you have any comments, suggestions, or would like to report a technical issue related to this tool, please feel free to use the form below (optional).  
Your feedback will help us improve the tool in future updates and academic evaluations.

[Click here to access the feedback form](https://docs.google.com/forms/d/e/1FAIpQLScZOEWa4osyS0K9Xg9Fq0p1EGeyyIOqXvfdkyxj07l9vyeGZw/viewform)
""")
