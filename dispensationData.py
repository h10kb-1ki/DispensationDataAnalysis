import streamlit as st
import pandas as pd
import altair as alt

st.title('外来処方の検証')

@st.cache_data
def load_data(Pop, Pc):
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
    #----------------
    df3 = df[['更新日時', 'date', '更新時刻', '曜日', '調剤負荷']]
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
                x=alt.X('更新時刻', title='時間'),
                y=alt.Y('mean(value)', title='調剤負荷', 
                        scale=alt.Scale(domain=[0, y_max]))
            )
    return line, band

st.subheader('曜日・時間ごとの調剤負荷', divider="gray")
Pop = st.number_input('一包化加点', 5)
Pc = st.number_input('つぶし加点（1Rpごと）', 3)
st.write('')
st.write('---要因---')
st.write('・軟膏の混合：未設定')
st.write('・薬品管理室に在庫がある薬：未設定')
st.write('・麻薬：未設定')
st.write('・毒薬（Revは追加加点）：未設定')
st.write('・特定生物由来：未設定')
st.write('---memo---')
st.write('・祝日フラグ')
st.write('・欠損値の処理（x軸が揃うように）')
st.write('')
weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
wd = st.selectbox('曜日を選択', weekdays)
y_max = st.number_input('y軸最大値', 400)
btn0 = st.button('調剤負荷点数の反映')
if btn0:
    line, band = load_data(Pop, Pc)
    st.altair_chart(band + line)