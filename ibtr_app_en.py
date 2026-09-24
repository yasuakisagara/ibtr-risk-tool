"""Bilingual interface refresh. Model 1.61 calculation is preserved."""
import copy
from html import escape
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
from ibtr_model import MODEL, calculate, normalize

st.set_page_config(page_title='IBTR Risk Estimation', page_icon='📊', layout='wide')
st.markdown('''<style>
:root{--ibtr-navy:#14334a;--ibtr-teal:#087e82}
.stApp{background:#f4f7f9;color:#14334a}.block-container{max-width:1320px;padding-top:2rem}
h1,h2,h3{color:#14334a!important;letter-spacing:-.025em}h1{font-size:2rem!important}h3{font-size:1.15rem!important}
div[data-testid="stVerticalBlockBorderWrapper"]>div{border-color:#dce5ea!important;border-radius:14px!important;background:white}
div[data-testid="stRadio"] label p,div[data-testid="stSelectbox"] label p{font-size:14px!important}
div[data-testid="stRadio"] [role="radiogroup"]{gap:.6rem}div[data-testid="stRadio"] label{padding:5px 8px;border:1px solid #dce5ea;border-radius:7px}
button[kind="primary"]{background:#087e82;border-color:#087e82;color:white}
.eyebrow{color:#087e82;font-size:12px;letter-spacing:1.7px;font-weight:700;margin:0}
.risk-cards{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:12px 0 20px}
.risk-card{padding:20px;background:#f2f8f8;border:1px solid #d5e9e7;border-radius:10px}
.risk-card .value{color:#07686e;font-size:44px;line-height:1.4;font-weight:650;letter-spacing:-1px;font-variant-numeric:tabular-nums}
.risk-card .value span{font-size:22px}.risk-card .label{font-size:14px;font-weight:600}.risk-card .ci{font-size:13px;color:#566c79}
.empty-result{text-align:center;padding:45px 18px;color:#566c79}.empty-result .icon{font-size:36px;color:#087e82;margin-bottom:15px}
.condition{display:inline-block;border:1px solid #dce5ea;border-radius:5px;padding:3px 7px;margin:3px;font-size:12px;color:#405c6c}
@media(max-width:400px){.risk-cards{grid-template-columns:1fr}.block-container{padding:1rem}}
</style>''', unsafe_allow_html=True)

brand, language = st.columns([4, 1])
with brand:
    st.image(str(Path(__file__).with_name('logo.png')), width=130)
with language:
    lang = st.selectbox('Language / 言語', ['ja', 'en'], format_func=lambda x: '日本語' if x == 'ja' else 'English', key='ui_language')
def t(ja, en): return ja if lang == 'ja' else en

# Store canonical values independently of translated widget labels.
if 'values' not in st.session_state: st.session_state['values'] = {}
values = st.session_state['values']
def read_selection(key):
    values[key] = st.session_state.get('field_' + key)
    if key == 'hormone_receptor' and values[key] != '1':
        values.pop('endocrine', None)
        st.session_state.pop('field_endocrine', None)
    if key == 'her2' and values[key] != '1':
        values.pop('targeted', None)
        st.session_state.pop('field_targeted', None)
    st.session_state.pop('result', None)
    st.session_state.pop('error_field', None)

def reset():
    for field in MODEL['fields']: st.session_state.pop('field_' + field['id'], None)
    values.clear()
    for key in ['result', 'comparison', 'error_field']: st.session_state.pop(key, None)

st.markdown('<p class="eyebrow">IBTR RISK ESTIMATION · MODEL 1.61</p>', unsafe_allow_html=True)
st.title(t('患者背景から、再発リスクを推定', 'Estimate risk from patient characteristics'))
st.write(t('臨床・病理情報と術後治療を選択してください。', 'Select clinical, pathological and treatment information.'))
left, right = st.columns([1.15, 1], gap='large')
with left, st.container(border=True):
    for n, group in enumerate(['patient', 'pathology', 'treatment']):
        if n: st.divider()
        st.subheader(f'0{n + 1}  ' + t(['患者背景', '病理情報', '術後治療'][n], ['Patient background', 'Pathology', 'Adjuvant treatment'][n]))
        for field in MODEL['fields']:
            key = field['id']
            if field['group'] != group: continue
            if key == 'endocrine' and values.get('hormone_receptor') != '1': continue
            if key == 'targeted' and values.get('her2') != '1': continue
            opts = [o['value'] for o in field['options']]
            labels = {o['value']: o[lang] for o in field['options']}
            widget = 'field_' + key
            st.session_state[widget] = values.get(key)
            st.radio(field[lang], opts, index=None, format_func=lambda v, labels=labels: labels[v], horizontal=True, key=widget, on_change=read_selection, args=(key,))
    calculate_col, reset_col = st.columns([2, 1])
    if calculate_col.button(t('リスクを計算', 'Calculate risk'), type='primary', use_container_width=True):
        try:
            st.session_state['result'] = calculate(values)
            st.session_state.pop('error_field', None)
        except ValueError as error: st.session_state['error_field'] = str(error)
    reset_col.button(t('リセット', 'Reset'), on_click=reset, use_container_width=True)
    if 'error_field' in st.session_state:
        missing = next(f for f in MODEL['fields'] if f['id'] == st.session_state['error_field'])
        st.error(t(f'「{missing[lang]}」を選択してください。', f'Please select {missing[lang]}.'))

with right, st.container(border=True):
    st.markdown('<p class="eyebrow">ESTIMATED RISK</p>', unsafe_allow_html=True)
    st.subheader(t('推定結果', 'Risk estimate'))
    result = st.session_state.get('result')
    if result:
        cards = ''
        for year, r in result['results'].items():
            period = t('5年リスク' if year == '5y' else '10年リスク', '5-year risk' if year == '5y' else '10-year risk')
            cards += f'<div class="risk-card"><div class="label">{period}</div><div class="value">{r["risk"]*100:.1f}<span>%</span></div><div class="ci">{t("95%信頼区間", "95% confidence interval")}<br>{r["lower"]*100:.1f}–{r["upper"]*100:.1f}%</div></div>'
        st.markdown('<div class="risk-cards">' + cards + '</div>', unsafe_allow_html=True)
        st.markdown('**' + t('推定リスクと不確実性', 'Estimated risk and uncertainty') + '**')
        maximum = max(r['upper'] for r in result['results'].values())
        limit = next(x for x in [.05, .1, .2, .5, 1] if x >= maximum)
        fig = go.Figure()
        for year, r in result['results'].items():
            y = 1 if year == '5y' else 0
            fig.add_trace(go.Scatter(x=[r['lower'], r['upper']], y=[y, y], mode='lines', line={'color': '#6baeb0', 'width': 6}, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=[r['risk']], y=[y], mode='markers', marker={'color': '#087e82', 'size': 13, 'line': {'color': 'white', 'width': 2}}, hovertemplate='%{x:.1%}<extra></extra>'))
        fig.update_layout(height=190, margin={'l': 5, 'r': 15, 't': 15, 'b': 30}, showlegend=False, paper_bgcolor='white', plot_bgcolor='white', font={'family': 'sans-serif', 'color': '#566c79', 'size': 14}, xaxis={'range': [0, limit], 'tickvals': [0, limit/2, limit], 'tickformat': '.0%', 'fixedrange': True, 'gridcolor': '#e9eef2', 'zeroline': False}, yaxis={'tickvals': [1, 0], 'ticktext': [t('5年', '5y'), t('10年', '10y')], 'range': [-.5, 1.5], 'fixedrange': True, 'showgrid': False, 'zeroline': False})
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.caption(t('点：推定値　線：95%信頼区間。目盛りは結果に応じて変わります。', 'Point: estimate · Line: 95% CI. Scale adjusts to results.'))
        if result['input']['age'] == 'agecategory_<40' or result['input']['stage'] == 'pT_3':
            st.warning(t('40歳未満・pT3は症例数が少ない条件です。推定値と区間の解釈に注意が必要です。', 'Under-40 and pT3 groups have limited cases. Interpret estimates and intervals cautiously.'))
        st.divider()
        st.markdown('**' + t('今回の入力条件', 'Selected conditions') + '**')
        chips = []
        for field in MODEL['fields']:
            key = field['id']
            if key == 'endocrine' and result['input']['hormone_receptor'] == '0': continue
            if key == 'targeted' and result['input']['her2'] == '0': continue
            label = next(o[lang] for o in field['options'] if o['value'] == result['input'][key])
            chips.append(f'<span class="condition">{escape(field[lang])}: {escape(label)}</span>')
        st.markdown(''.join(chips), unsafe_allow_html=True)
        st.divider()
        st.markdown('**' + t('治療条件を比較', 'Compare treatment scenarios') + '**')
        if st.button(t('この条件を比較用に保持', 'Keep this scenario for comparison'), use_container_width=True):
            st.session_state['comparison'] = copy.deepcopy(result)
        st.caption(t('保持したあと治療条件を変更し、再計算してください。', 'Keep this scenario, change treatment selections, then recalculate.'))
        saved = st.session_state.get('comparison')
        if saved:
            same = all(saved['input'][f['id']] == result['input'][f['id']] for f in MODEL['fields'] if f['group'] != 'treatment')
            if same:
                st.table({t('期間', 'Period'): [t('5年', '5 years'), t('10年', '10 years')], t('保持した条件', 'Saved'): [f'{saved["results"][y]["risk"]*100:.1f}%' for y in ['5y', '10y']], t('現在', 'Current'): [f'{result["results"][y]["risk"]*100:.1f}%' for y in ['5y', '10y']]})
                treatments = [f[lang] + ': ' + next(o[lang] for o in f['options'] if o['value'] == saved['input'][f['id']]) for f in MODEL['fields'] if f['group'] == 'treatment']
                st.caption(t('保持した治療：', 'Saved treatments: ') + ' / '.join(treatments))
                st.caption(t('モデル上の推定値の比較であり、個人の治療効果を保証するものではありません。', 'This compares model estimates; it does not establish individual treatment effects.'))
            else: st.info(t('患者背景・病理情報が異なるため比較できません。条件を保持し直してください。', 'Background or pathology differs. Save a new matching scenario to compare.'))
            if st.button(t('比較を解除', 'Clear comparison')):
                st.session_state.pop('comparison', None)
                st.rerun()
    else:
        st.markdown('<div class="empty-result"><div class="icon">%</div><b>' + t('入力すると、ここに結果が表示されます', 'Your estimate will appear here') + '</b><p>' + t('全項目を選択して「リスクを計算」を押してください。', 'Complete all fields and select Calculate risk.') + '</p></div>', unsafe_allow_html=True)
        if st.session_state.get('comparison'): st.caption(t('比較用の治療条件を保持しています。', 'A treatment scenario is saved for comparison.'))
    st.divider()
    st.caption(t('診療における説明支援のための統計的推定です。個別の治療方針を決定するものではありません。', 'A statistical estimate to support clinical discussions, not to determine individual treatment.'))

with st.expander(t('対象とモデルについて', 'Population and model')):
    st.write(t('2008〜2017年に乳房温存術を受けた日本の浸潤性乳がん患者8,938人を対象とした多施設共同研究に基づきます。乳房切除への変更、術前化学療法、両側・多発癌、必要情報の欠損がある症例は除外されています。適用範囲の詳細は原著をご確認ください。', 'Based on a Japanese multicentre study of 8,938 women undergoing breast-conserving surgery for invasive breast cancer in 2008–2017. Mastectomy conversion, neoadjuvant chemotherapy, bilateral/multiple cancers and missing essential data were excluded. See the publication for eligibility.'))
    st.markdown('[Sagara et al. · JCO Clinical Cancer Informatics (2025)](https://ascopubs.org/doi/10.1200/CCI-25-00182)')
with st.expander(t('計算方法と95%信頼区間', 'Calculation and 95% confidence intervals')):
    st.write(t('モデル1.61の係数とベースライン生存率を使用しています。リスク = 1 − S₀(t)^exp(Σβx)。表示区間は既存実装の近似計算を継承し、係数間の共分散とベースライン生存率の不確実性は含みません。個人の将来の結果を95%の確率で保証する範囲ではありません。', 'Uses model 1.61 coefficients and baseline survival. Risk = 1 − S₀(t)^exp(Σβx). Intervals retain the original approximation, excluding coefficient covariance and baseline-survival uncertainty. They do not guarantee an individual outcome with 95% probability.'))
with st.expander(t('プライバシー', 'Privacy')):
    st.write(t('このStreamlit版では、入力値は計算のためサーバーに送信され、セッション内で処理されます。アプリのコードは入力値や計算結果をファイル・データベースに保存しません。ホスティング基盤のアクセスログ等は別途扱われます。氏名や患者IDの入力欄はありません。iOS版およびSites版とは処理方式が異なります。', 'In this Streamlit edition, inputs are sent to the server and processed within the session. The app code does not write clinical inputs or results to files or databases. Hosting access logs are handled separately. There are no name or patient-ID fields. Processing differs from the iOS and Sites editions.'))
with st.expander(t('研究・アプリ・フィードバック', 'Research, app and feedback')):
    st.write(t('日本乳癌学会第29回研究班（班長：坂井威彦）。モデル開発・検証とアプリ実装：相良安昭。研究・教育目的のツールです。医療上の判断は医療従事者とご相談ください。', 'Japanese Breast Cancer Society, Task Force 29 (Takehiko Sakai). Model development, validation and app implementation: Yasuaki Sagara. For research and education. Discuss medical decisions with a healthcare professional.'))
    st.markdown('[iPhone / iPad](https://apps.apple.com/jp/app/ibtr-risk-estimation/id6744888499) · [Feedback](https://docs.google.com/forms/d/e/1FAIpQLScZOEWa4osyS0K9Xg9Fq0p1EGeyyIOqXvfdkyxj07l9vyeGZw/viewform)')
with st.expander(t('更新履歴', 'Version history')):
    st.write(t('画面改良版：日英対応、未入力の確認、5年・10年の並列表示、治療条件比較。計算モデルは1.61を維持。', 'Interface update: bilingual inputs, completeness checks, side-by-side estimates and treatment comparison. Calculation model remains 1.61.'))
    st.write(t('1.0 初版（2025-04-11）／1.5 データ整合性修正（2025-04-17）／1.6 項目名称修正（2025-05-23）／1.61 説明更新（2025-09-16）', '1.0 initial release (2025-04-11) / 1.5 data consistency (2025-04-17) / 1.6 variable labels (2025-05-23) / 1.61 explanatory text (2025-09-16)'))
st.caption('© Japanese Breast Cancer Society · Task Force 29 | Model 1.61')
