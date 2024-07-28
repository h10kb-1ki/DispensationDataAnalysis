import streamlit as st
import pandas as pd
import altair as alt

st.title('外来処方の検証')

with st.sidebar:
    Pop = st.number_input('一包化加点', 5)
    Pc = st.number_input('つぶし加点（1Rpごと）', 3)
    st.write('')
    st.write('---要因---')
    st.write('・軟膏の混合：未設定')
    st.write('・薬品管理室に在庫がある薬：未設定')
    st.write('・麻薬：未設定')
    st.write('・毒薬（Revは追加加点）：未設定')
    st.write('・特定生物由来：未設定')

df = pd.read_excel('調剤負荷データ.xlsx')
df['date'] = pd.to_datetime(df['更新日'])
df['調剤負荷'] = ''
for i in range(len(df)):
    point_rp = df.loc[i, 'Rp数']
    if df.loc[i, '一包化'] == 1:
        point_op = Pop
    else:
        point_op = 0
    point_crush = df.loc[i, 'つぶしRp数'] * Pc
    df.loc[i, '調剤負荷'] = point_rp + point_op + point_crush
df1 = df[['更新日時', 'date', '更新時刻', '曜日', '調剤負荷']]
#---------------------------------------------------------
st.subheader('指定日・時間ごとの調剤負荷', divider="gray")
dates = sorted(list(set(df['更新日時'].tolist())))
day = st.date_input('日を指定', dates[0], min_value=dates[0], max_value=dates[len(dates)-1])
btn2 = st.button('時間ごとの調剤負荷')
if btn2:
    df2 = df1[['更新日時', 'date', '更新時刻', '曜日', '調剤負荷']]
    df2q = df2.query(f'date == "{day}"')
    
    df2qp = pd.pivot_table(df2q, index='更新時刻', values='調剤負荷', aggfunc='sum')
    df2qp.reset_index(inplace=True)
    bars = alt.Chart(df2qp).mark_bar(size=25).encode(
                x=alt.X('更新時刻', title='時間', axis=alt.Axis(labelAngle=-30)),
                y=alt.Y('調剤負荷', title='調剤負荷'),
                ).properties(
                    width=450,
                    height=350,
                    title=f'時間ごとの調剤負荷  {day}'
                    )
    st.altair_chart(bars, use_container_width=True)
    st.dataframe(df2qp)
#---------------------------------------------------------
st.write('')
st.subheader('曜日・時間ごとの調剤負荷', divider="gray")
weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
wd = st.selectbox('曜日を選択', weekdays)
y_max = st.number_input('y軸最大値', 400)
btn3 = st.button('曜日別の調剤負荷')
if btn3:
    df3 = df1[['更新日時', 'date', '更新時刻', '曜日', '調剤負荷']]
    df3q = df3.query(f'曜日 == "{wd}"')
    df3qp = pd.pivot_table(df3q, index='date', columns='更新時刻', values='調剤負荷', aggfunc='sum')
    df3qp = df3qp.T
    df3qp.reset_index(inplace=True)
    df3qp = df3qp.fillna(0)
    df3qpm = pd.melt(df3qp, id_vars=['更新時刻'])
    line = alt.Chart(df3qpm).mark_line().encode(
                x='更新時刻',
                y='mean(value)'
            )
    band = alt.Chart(df3qpm).mark_errorband(extent='ci').encode(
                x=alt.X('更新時刻', title='調剤負荷'),
                y=alt.Y('mean(value)', title='調剤負荷', 
                        scale=alt.Scale(domain=[0, y_max]))
            )
    st.altair_chart(band + line)