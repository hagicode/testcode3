import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from streamlit_option_menu import option_menu
import glob
import pathlib
import os

@st.cache_data
def cache_image(img):
    st.image(img)

def clear_multi():
    st.session_state.multiselect = []
    st.session_state.multiselect2 = []
    st.session_state.multiselect3 = []
    return

#github
st.set_page_config(layout="wide")

l2 = sorted(glob.glob('files/*.xlsx', recursive=True))
p = pathlib.Path(l2[-1])
update_date = os.path.split(p)[1].replace("_demo.xlsx","")
st.write("データ更新日：" + update_date)

screening_file = p
df = pd.read_excel(screening_file,sheet_name="Sheet1",index_col=0 )

#ローカル用
# screening_file = '/content/drive/MyDrive/master_ColabNotebooks/kabu_files/multi_account_files/20230518/230518_demo.xlsx'
# df = pd.read_excel(screening_file,index_col=0 )
# update_date = os.path.basename(screening_file).replace("_demo.xlsx","")
# st.write("データ更新日：" + update_date)


st.subheader('Screening Option') 
st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">手法選択</p>', unsafe_allow_html=True)
method_menu = ["Granvil", "PerfectOrder", "Zenmo #工事中", "All Data"]
method = option_menu("Method Menu", options= method_menu,
    #icons=['house', 'gear', 'gear'],
    menu_icon="cast", default_index=0, orientation="horizontal")


st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">プライスアクション・移動平均線</p>', unsafe_allow_html=True)
default_button = st.radio("設定例",    ('Granvil_example', 'PerfectOrder_example'),horizontal=True)
st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">デモ用にSMA5,25,75の設定にしています。</p>', unsafe_allow_html=True)


col1,col2,col3 = st.columns([1,2,1])

#マルチセレクトで抽出可能なカラムから選択肢を作成
multi_selectbox_columns = df.filter(like="R@",axis=1).columns
select_option = sorted(list(df[multi_selectbox_columns].stack().unique()))

multi_selectbox_columns2 = df.filter(like="MA@",axis=1).columns
SO2 = sorted(list(df[multi_selectbox_columns2].stack().unique()))

so2 = ([s for s in SO2 if '傾き正' in s]
        +[s for s in SO2 if 'V字に反転' in s]
        +[s for s in SO2 if '収束' in s]
        +[s for s in SO2 if '乖離小' in s]
        +[s for s in SO2 if 'ローソク足内' in s]
        +[s for s in SO2 if '下髭内' in s]
        +[s for s in SO2 if '連日推移' in s]
        +[s for s in SO2 if 'PO' in s]
        +[s for s in SO2 if '>' in s])

select_option2 = so2 + list(set(SO2) - set(so2))

multi_selectbox_columns3 = df.filter(like="Vol@",axis=1).columns
select_option3 = sorted(list(df[multi_selectbox_columns3].stack().unique()))



if default_button =='Granvil_example':
  with col1:
      mul_sel = st.multiselect("ローソク足・プライスアクション", (select_option),default=["陽線"],key="multiselect") #選択項目

  with col2:
      mul_sel2 = st.multiselect("移動平均線との関係", (select_option2),default=["SMA25:傾き正","SMA25 > 75","SMA5:V字に反転"],key="multiselect2")#選択項目 

  with col3:
      mul_sel3 = st.multiselect("出来高", (select_option3),default=["出来高前日比プラス"],key="multiselect3")#選択項目

elif default_button =='PerfectOrder_example':
  with col1:
      mul_sel = st.multiselect("ローソク足・プライスアクション", (select_option),default=["当日下髭"],key="multiselect") #選択項目
  with col2:
      mul_sel2 = st.multiselect("移動平均線との関係", (select_option2),default=["SMA5,25,75_PO_start"],key="multiselect2")#選択項目 
  with col3:
      mul_sel3 = st.multiselect("出来高", (select_option3),key="multiselect3")#選択項目

# else:
#   with col1:
#       mul_sel = st.multiselect("ローソク足・プライスアクション", (select_option),default=["陽線"],key="multiselect") #選択項目
#   with col2:
#       mul_sel2 = st.multiselect("移動平均線との関係", (select_option2),default=["SMA25:傾き正","SMA25 > 75"],key="multiselect2")#選択項目 
#   with col3:
#       mul_sel3 = st.multiselect("出来高", (select_option3),default=["出来高前日比プラス"],key="multiselect3")#選択項目

with st.expander("show more"):
    values1 = st.slider('2つの値で範囲を指定します。',  0, 10000, (900, 1050) ,step=50)
    st.write(values1)
    
st.button("Clear selection", on_click=clear_multi)
st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">設定変更後にdefault条件に戻したい場合はブラウザを再読込みしてください。<br>その場合Storage Listも初期化されます。</p>', unsafe_allow_html=True)

#選択された項目
mul_sel_all = mul_sel + mul_sel2 + mul_sel3

#選択された項目を含む列
select_columns = df.columns[df.isin(mul_sel).sum(axis=0)>0].tolist() + df.columns[df.isin(mul_sel2).sum(axis=0)>0].tolist() + df.columns[df.isin(mul_sel3).sum(axis=0)>0].tolist()

#選択された項目で抽出したデータフレーム

if method == "All Data" :
    data = df[(df[select_columns].isin(mul_sel_all).sum(axis=1)==len(select_columns))].drop(multi_selectbox_columns, axis=1).drop(multi_selectbox_columns2, axis=1).drop(multi_selectbox_columns3, axis=1).drop(method_menu, axis=1, errors='ignore')
else:
    data = df[(df[method]>0)&(df[select_columns].isin(mul_sel_all).sum(axis=1)==len(select_columns))].drop(multi_selectbox_columns, axis=1).drop(multi_selectbox_columns2, axis=1).drop(multi_selectbox_columns3, axis=1).drop(method_menu, axis=1, errors='ignore')


st.subheader('Data:' + str(len(data)) + "銘柄") 
st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">20個程度まで絞ってください。キリバンや出来高偏差のフィルタには表内機能で可能です。<br>ソートも可能ですが、ChartBarの順番には反映されません。</p>', unsafe_allow_html=True)


gb = GridOptionsBuilder.from_dataframe(data)
#gb.configure_grid_options(rowHeight=30)
#https://www.ag-grid.com/javascript-data-grid/column-groups/
gb.configure_side_bar()
gb.configure_pagination(paginationPageSize=30)
gb.configure_selection(selection_mode = 'multiple', use_checkbox=True)
gb.configure_default_column(filterable=True,sortable=True,enablePivot = False, enableValue = False)
gb.configure_column("ticker", headerCheckboxSelection = True, headerCheckboxSelectionFilteredOnly=True)#めちゃ大事

gridOptions = gb.build()
selects =AgGrid(data,theme="streamlit",
    gridOptions=gridOptions,
    fit_columns_on_grid_load=True
    ).selected_rows


#data = grid_response['data']
#selects = grid_response['selected_rows']


num=len(selects)

if "storage_list" not in st.session_state:
  st.session_state["storage_list"] = []

with st.sidebar:
    st.header("Storage List")
    st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">リストの確認とダウンロード</p>', unsafe_allow_html=True)
    if st.button(label="show"):
        storaged_data = [code for code in st.session_state["storage_list"]]
        storage_df = df.copy().set_index("ticker").loc[storaged_data][["name"]]
        st.table(storage_df)

        storage_df["Kabutan"]=[f"https://kabutan.jp/stock/chart?code={code_}" for code_ in storage_df.index.tolist()]
        

        if len(storage_df)>0:
            st.download_button(
                label="Download data as CSV",
                data=storage_df.to_csv().encode('shift_jis'),
                file_name='selected.csv',
                mime='text/csv',
                )

    st.header("Chart Bar")
    st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">サイドバーのサイズでチャートサイズを変えられます<br>他のMAの組合せや詳細を確認したいときはKabutanURLへ</p>', unsafe_allow_html=True)
    if num > 0 :
        
        for i, selcect in enumerate(selects):
            code = selects[i]["ticker"]
            stock_name = selects[i]["name"]
            Kessan_schedule = selects[i]["決算発表日"]
            st.write(f"Kabutan URL [{code}  {stock_name} ](https://kabutan.jp/stock/chart?code={code})")

            if Kessan_schedule is not None : 
                st.write(f"決算発表日(予) {Kessan_schedule}")
                st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">予定日は掲載後に変更される可能性があります。</p>', unsafe_allow_html=True)
            else:
                Kessan_schedule = "未定"
                st.write(f"決算発表日(予) {Kessan_schedule}")

            img=f"https://www.kabudragon.com/chart/s={code}/e={update_date}.png/"
            cache_image(img) #cache

            #html_code =  f'<iframe src="//www.invest-jp.net/blogparts/stocharmini/{code}/d/1/160" width="160" height="300" style="border:none;margin:0;" scrolling="no"></iframe><div style="font-size:7pt;">by <a href="https://www.invest-jp.net/" target="_blank">株価チャート</a>「ストチャ」</div>'
            #stc.html(html_code,height = 500)

            if st.button(label=f"Storage / Remove {code}"):
                if code not in st.session_state["storage_list"]:
                    st.session_state["storage_list"].append(code)
                    storaged_data = [code for code in st.session_state["storage_list"]]
                    st.write(str(storaged_data))
                else:
                    st.session_state["storage_list"].remove(code)
                    st.write(str(code) + "removed!")
                    storaged_data = [code for code in st.session_state["storage_list"]]
                    st.write(str(storaged_data))
    else:
        pass
