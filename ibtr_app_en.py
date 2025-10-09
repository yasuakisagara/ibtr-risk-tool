## ibtr_app.py - Full Model with HR-based Calculation, ver1.5　logo cloudinary
import streamlit as st

# --- Safariフォント問題回避：システムネイティブフォント指定 ---
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Language selector must come first
lang = st.selectbox("Language/言語", ["English", "日本語"])

# Translation dictionary (T) must come after lang is defined
T = {
    "title": {
    "English": "IBTR Risk Estimation Tool<br>Integrating Real-World Data and Evidence from Meta-Analyses",
    "日本語": "リアルワールドデータと<br>メタ解析に基づくIBTR発症率推定ツール"
    },
    "version": {"English": "Version 1.61", "日本語": "バージョン1.61"},
    "description": {
        "English": "This tool estimates the likelihood of Ipsilateral Breast Tumor Recurrence (IBTR) based on selected patient background and treatments.\nPlease select the clinical and pathological features below.",
        "日本語": "このツールでは、同側乳房内再発（IBTR）の可能性を推定します。\n以下の臨床・病理情報を選択してください。"
    },
    "calculate": {"English": "Calculate IBTR Risk", "日本語": "乳房内再発リスクを計算"},
    "estimated_risk": {"English": "Estimated IBTR risk at", "日本語": "推定された乳房内再発リスク（"},
    "ci": {"English": "95% Confidence Interval", "日本語": "95%信頼区間"}
}


# --- Display logo, title, version, and description (left-aligned) ---
st.image("https://res.cloudinary.com/dqlawunmg/image/upload/v1745049473/logo_pjk79t.png", width=250)

main_title = "IBTR Risk Estimation" if lang == "English" else "乳房内再発リスク推定ツール"
subtitle = "Integrating Real-World Data and Evidence from Meta-Analyses" if lang == "English" else "リアルワールドデータとメタ解析に基づく"

st.markdown(f"## {main_title}")
st.markdown(f"**{subtitle}**")
st.markdown(f"**{T['version'][lang]}**")
st.markdown(T['description'][lang].replace("\\n", "<br>"), unsafe_allow_html=True)

# Patient Characteristics (multilingual)
if lang == "日本語":
    st.markdown("### 患者背景")
    age = st.radio("年齢カテゴリ", ["40歳未満", "40代", "50代", "60代", "70歳以上"], index=1)
    margin = st.radio("最終断端状況", ["陰性断端(≥5mm)", "近接断端(<5mm)", "陽性断端（tumor on ink）"])
    t_stage = st.radio("病理T分類", ["pT1", "pT2", "pT3（極少数）"])
    grade = st.radio("組織学的/核 グレード", ["Grade 1", "Grade 2", "Grade 3"])
    lvi = st.checkbox("脈管侵撃あり")
    hormone_receptor = st.checkbox("ホルモン受容体陽性")
    her2 = st.checkbox("HER2受容体陽性")
else:
    st.markdown("### Patient Characteristics")
    age = st.radio("Age category", ["Under 40", "40s", "50s", "60s", "70 or older"], index=1)
    margin = st.radio("Final surgical margin", ["Clear (≥5mm)", "Close (<5mm)", "Involved (tumor on ink)"])
    t_stage = st.radio("Pathological T stage", ["pT1", "pT2", "pT3 (very few cases)"])
    grade = st.radio("Histologic/nuclear grade", ["Grade 1", "Grade 2", "Grade 3"])
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
    "Clear (≥5mm)": "finalmargin_negative",
    "Close (<5mm)": "finalmargin_close(<5mm)",
    "Involved (tumor on ink)": "finalmargin_positive",
    "陰性断端(≥5mm)": "finalmargin_negative",
    "近接断端(<5mm)": "finalmargin_close(<5mm)",
    "陽性断端（tumor on ink）": "finalmargin_positive"
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

# Show a centered button using a styled div for layout, but use a true Streamlit button for action
st.markdown(
    f"""
    <style>
    div.stButton > button {{
        border: 2px solid red;
        padding: 10px 25px;
        font-size: 18px;
        color: black;
        background-color: white;
        border-radius: 8px;
        cursor: pointer;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    f"<div style='text-align: center; margin-top: 20px; margin-bottom: 20px;'>",
    unsafe_allow_html=True
)

if st.button(T['calculate'][lang]):
    for year, (r, lower, upper) in results.items():
        if lang == "日本語":
            year_label = year.replace("y", "年") if "y" in year else f"{year}年"
            st.markdown(f"### {year_label} 乳房内再発の可能性")
        else:
            st.markdown(f"### {year} IBTR estimate")

        st.markdown(f"<div style='font-size: 24px; font-weight: bold;'>{r*100:.1f}%</div>", unsafe_allow_html=True)
        if lang == "日本語":
            st.caption(f"95%信頼区間: {lower*100:.1f}% - {upper*100:.1f}%")
        else:
            st.caption(f"95% Confidence Interval: {lower*100:.1f}% - {upper*100:.1f}%")

        # PlotlyによるCIバー
        fig = go.Figure()

        # CI線
        fig.add_trace(go.Scatter(
            x=[lower, upper],
            y=[1, 1],
            mode='lines',
            line=dict(color='darkgray', width=6),
            name="95% CI"
        ))

        # 推定リスク点
        fig.add_trace(go.Scatter(
            x=[r],
            y=[1],
            mode='markers+text',
            marker=dict(
                color='orange' if str(year).startswith("5") else 'red',  # 5yはorange、10yはred
                size=9,
                line=dict(color='black', width=1)
            ),
            text=[f"{r*100:.1f}%"],
            textposition="top center",
            name="Estimated Risk"
        ))

        # レイアウト
        fig.update_layout(
            height=140,
            margin=dict(l=30, r=30, t=30, b=10),
            xaxis=dict(
                range=[0, 1],
                title="Probability",
                tickvals=[0.1, 0.2, 0.3, 0.4, 0.5],
                ticktext=["10%", "20%", "30%", "40%", "50%"],
                showgrid=False
            ),
            yaxis=dict(visible=False),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
# Footnote section (multilingual)
if lang == "日本語":
    st.markdown("""
---
### 本ツールについて
このツールは、2008〜2017年に乳房温存術（部分切除術）を受けた浸潤性乳がん患者 8,938人を対象とした日本の多施設共同研究の結果に基づいて開発・検証されました。

研究のポイント
    •    乳房温存術後の乳房内再発（IBTR）のリスクを5年・10年で推定
    •    年齢、腫瘍の大きさ、断端状況、グレード、リンパ管侵襲、ホルモン受容体やHER2の状態、術後治療（放射線、内分泌療法、化学療法など）を考慮
    •    大規模メタアナリシス（EBCTCG）のデータを組み込み、治療効果を反映

注意点
    •    このツールはあくまで統計モデルに基づく推定であり、診断や治療を決定するものではありません。
    •    特に40歳未満やまれな病理型など、対象患者が少ない条件では予測の幅が広くなるため、解釈には注意が必要です。
    •    実際の診療では、主治医と相談のうえ治療方針を決定してください。

発表について
本研究成果は 2025年ASCO年次総会（演題番号575） にて発表され、JCO Clinical Cancer Informatics に論文掲載されています。  詳細な解析や方法については論文をご参照ください。
https://ascopubs.org/doi/10.1200/CCI-25-00182
  

### iPhoneおよびiPad版ツール 
インターネット環境がなくても利用できるiPhoneおよびiPad向けアプリとなります。10年間のIBTRリスクの推定に加え、選択した術後治療の効果を視覚的に分かりやすく提示することが可能です。
https://apps.apple.com/jp/app/ibtr-risk-estimation/id6744888499

### 免責事項
このツールは学術目的および教育目的のために提供されており、医学的助言、診断、治療の代替とはなりません。医療上の判断は必ず医療従事者にご相談ください。
""")
else:
    st.markdown("""
---
### About this tool
This tool was developed based on a multi-center study of 8,938 women in Japan who underwent breast-conserving surgery (partial mastectomy) for invasive breast cancer between 2008 and 2017. Patients who had mastectomy conversion, received neoadjuvant chemotherapy, had bilateral/multiple cancers, or lacked essential data were excluded.

The model estimates the risk of ipsilateral breast tumor recurrence (IBTR) at 5 and 10 years after surgery. It incorporates clinical and pathological factors (such as age, tumor size, margin status, grade, lymphovascular invasion, hormone receptor and HER2 status) as well as the effects of adjuvant therapies (chemotherapy, endocrine therapy, and radiotherapy). Treatment effects were informed by large-scale EBCTCG meta-analyses.

Key points
    •    Risk estimates are generated using robust statistical methods and internally validated.
    •    Results are presented with 95% confidence intervals, showing the uncertainty range.
    •    In smaller subgroups (e.g., patients under 40 years or with rare tumor types), the prediction intervals are wider, so results should be interpreted with caution.
    •    This tool is designed to support discussion between patients and physicians, not to replace medical advice.

Publication
The methodology was presented at the 2025 ASCO Annual Meeting (Abstract No. 575) and published in JCO Clinical Cancer Informatics (Sagara et al., 2025). For detailed methods and results, please refer to the published article(https://ascopubs.org/doi/10.1200/CCI-25-00182).

### iPhone and iPad version
An iPhone and iPad version of the app is available now, designed to work offline without the need for an internet connection. This application provides not only a 10-year IBTR risk estimate but also a visual representation of the anticipated effects of selected treatment options. 
    https://apps.apple.com/jp/app/ibtr-risk-estimation/id6744888499

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
- ver1.6（2025年5月23日更新）：変数の名称を変更
- ver1.61（2025年9月16日更新）：本ツール説明を変更
""")
else:
    st.markdown("""
---
### Version History
- ver1.0 (Released on April 11, 2025): Initial version
- ver1.5 (Updated on April 17, 2025): Minor revisions made to ensure data consistency, including adjustments to IBTR event classification.
- ver1.6 (Updated on May 23, 2025): Variable names revised
- ver1.61 (Updated on Sep 16, 2025): Explanation of this tool revised
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

# --- Privacy Policy Section (multilingual) ---
st.markdown("---")

if lang == "日本語":
    st.markdown("""
### プライバシーポリシー

本ウェブツールとiOSのアプリケーション（IBTR Risk Estimation）は、医療従事者による乳房内再発（IBTR）リスクの説明支援を目的として開発されたツールです。

本アプリでは、以下のとおりユーザーのプライバシーを尊重し、個人情報の収集・保存・送信は一切行いません。

- ユーザーの氏名、メールアドレス、位置情報、デバイス識別子等の個人情報は収集しません。
- 入力された臨床情報や計算結果はすべて端末内で処理され、外部サーバーに送信されません。
- いかなる情報も第三者へ提供されることはありません。
- 本アプリは広告配信機能を使用していません。
- 本プライバシーポリシーに関するご質問は、上記のフィードバックフォームにてご連絡ください。
""")
else:
    st.markdown("""
### Privacy Policy

The IBTR Risk Estimation web tool and iOS application is a non-commercial medical support tool designed to assist healthcare professionals in explaining the risk of ipsilateral breast tumor recurrence (IBTR).

This app fully respects user privacy and does not collect, store, or transmit any personal information.

- No personal data such as name, email address, location, or device identifiers is collected.
- All entered clinical data and results are processed locally on your device and are not transmitted to external servers.
- No information is shared with third parties.
- This app does not use any advertising.
- If you have any questions regarding this privacy policy, please contact us using the feedback form above.
""")
