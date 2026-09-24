from streamlit.testing.v1 import AppTest
import pathlib,sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
at=AppTest.from_file(str(ROOT / 'ibtr_app_en.py'),default_timeout=30).run()
assert not at.exception, at.exception
at.button[0].click().run();assert len(at.error)==1
selected={'age':'agecategory_50s','margin':'finalmargin_negative','stage':'pT_1','grade':'grade_2','lvi':'0','hormone_receptor':'1','her2':'1','radiation':'1','chemotherapy':'0'}
for key,val in selected.items():at.radio(key='field_'+key).set_value(val).run()
for key in ['endocrine','targeted']:at.radio(key='field_'+key).set_value('1').run()
at.button[0].click().run();assert not at.exception,at.exception
original=at.session_state['result'];assert original
at.selectbox[0].set_value('en').run();assert not at.exception,at.exception
assert at.session_state['result']==original
for key,val in selected.items():assert at.radio(key='field_'+key).value==val,(key,at.radio(key='field_'+key).value)
next(b for b in at.button if b.label=='Keep this scenario for comparison').click().run()
at.radio(key='field_radiation').set_value('0').run();assert 'result' not in at.session_state
at.button[0].click().run();assert at.session_state['result']['results']['10y']['risk']>original['results']['10y']['risk']
assert len(at.table)==1
at.radio(key='field_her2').set_value('0').run();assert 'targeted' not in at.session_state['values']
at.radio(key='field_her2').set_value('1').run();assert at.radio(key='field_targeted').value is None
at.button[0].click().run();assert len(at.error)==1
next(b for b in at.button if b.label=='Reset').click().run()
assert not at.session_state['values'];assert 'result' not in at.session_state;assert 'comparison' not in at.session_state
assert not at.exception,at.exception
print('Streamlit 1.33 AppTest passed: incomplete inputs, complete calculation, language preservation, scenario comparison, dependent treatment reset and full reset')
