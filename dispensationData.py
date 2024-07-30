import streamlit as st
import pandas as pd
import altair as alt

st.title('外来処方の検証')
with st.sidebar:
    st.write('')
    st.write('---条件---')
    st.write('1. 基本的には、1剤につき1点。棚配置に応じて以下のように配点。')
    st.markdown('&nbsp;&nbsp;&nbsp;✓&nbsp;薬品管理室の薬剤は5点')  #'&nbsp;'はHTMLのスペース(st.write()では無視されるのでst.markdown())
    st.markdown('&nbsp;&nbsp;&nbsp;✓&nbsp;麻薬、覚原、特生は4点')
    st.markdown('&nbsp;&nbsp;&nbsp;✓&nbsp;毒薬、栄養剤は3点')
    st.markdown('&nbsp;&nbsp;&nbsp;✓&nbsp;Revへの追加加点：未設定')
    st.write('2. 一包化指示があれば＋7点')
    st.write('3. つぶし指示があれば1剤につき＋5点')
    st.write('4. 混合指示があれば1剤につき＋5点')
    st.write('')
    st.write('---memo---')
    st.write('- 配点の検討')
    st.write('- 祝日フラグ検討（6月は関係ない）')
    st.write('- ヘルプ人数と照合')
    st.write('- 待ち時間との整合性（調剤負荷グラフよりやや右にずれる）')
    
df = pd.read_excel('調剤負荷データ.xlsx')

col1, col2 = st.columns([0.3, 0.7], vertical_alignment='bottom')
with col1:
    auxiliary_line = st.number_input('補助線', value=275)
with col2:
    btn = st.button('表示')
st.write('---')
if btn:
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    for wd in weekdays:
        dfq = df.query(f'曜日 == "{wd}"')
        dfqp = pd.pivot_table(dfq, index='更新日', columns='更新時刻', values='調剤負荷', aggfunc='sum')
        dfqp = dfqp.T
        dfqp.reset_index(inplace=True)
        dfqp = dfqp.fillna(0)
        dfqpm = pd.melt(dfqp, id_vars=['更新時刻'])
        line = alt.Chart(dfqpm).mark_line().encode(
            x='更新時刻',
            y='mean(value)'
        )
        #折れ線グラフ
        band = alt.Chart(dfqpm).mark_errorband(extent='ci').encode(
            x=alt.X('更新時刻', title='', axis=alt.Axis(labelAngle=-30, grid=True)), 
            y=alt.Y('mean(value)', title='', 
                    scale=alt.Scale(domain=[0, 450])), 
            ).properties(title=f'曜日ごとの調剤負荷（{wd}）', 
            )
        rule = alt.Chart().mark_rule(strokeDash=[5, 5], size=1, color='red').encode(y=alt.datum(auxiliary_line))

        st.altair_chart(band + line + rule, use_container_width=True)
        #ヒートマップ
        hm = alt.Chart(dfqpm).mark_rect().encode(
            x=alt.X('更新時刻', title='', axis=alt.Axis(labelAngle=-30)), 
            y=alt.Y('更新日', title=''), 
            color=alt.Color('value:Q', scale=alt.Scale(domain=[0, 450], range=['azure', 'royalblue']))  # カラースケールを指定
            ).properties(
                width=550,
                height=150
            )
        text = hm.mark_text(baseline='middle').encode(
            text=alt.Text('value:Q', format='.0f'),
            color=alt.condition(
                alt.datum.value >= auxiliary_line,  # 値が基準より大きい場合は赤、そうでない場合は黒
                alt.value('red'),
                alt.value('black')
            )
        )
        st.altair_chart(hm + text, use_container_width=True)
        st.write('---')