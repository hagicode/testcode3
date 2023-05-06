import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from streamlit_option_menu import option_menu

@st.cache_data
def cache_image(img):
    st.image(img)


#screening_file = 'demo.xlsx'
#df = pd.read_excel(screening_file,sheet_name="DEMO")

screening_file = 'DEMO (1).xlsx'
df = pd.read_excel(screening_file,sheet_name="Sheet1")

st.set_page_config(layout="wide")

st.subheader('Screening Option') 
st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">手法選択</p>', unsafe_allow_html=True)

method = option_menu("Method Menu", options=["グランビルNo3", "Granville3", "Granville4", "Perfect Order", "Zenmo", "SMA200"],
    #icons=['house', 'gear', 'gear'],
    menu_icon="cast", default_index=0, orientation="horizontal")


st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">プライスアクション・移動平均線</p>', unsafe_allow_html=True)

col1,col2,col3,col4 = st.columns([1,1,1,1])

#マルチセレクトで抽出可能なカラムから選択肢を作成
#multi_selectbox_columns = ["ローソク","髭","寄り天・底","大陽線・陰線"]
multi_selectbox_columns = df.filter(like="R@",axis=1).columns
select_option = list(df[multi_selectbox_columns].stack().unique())

multi_selectbox_columns2 = df.filter(like="MA@",axis=1).columns
select_option2 = list(df[multi_selectbox_columns2].stack().unique())

with col1:
    #選択された項目
    mul_sel = st.multiselect("ローソク足・プライスアクション", (select_option)) 


with col2:
    #選択された項目
    mul_sel2 = st.multiselect("移動平均線との関係", (select_option2)) 


#選択された項目を含む列
select_columns = df.columns[df.isin(mul_sel).sum(axis=0)>0] + df.columns[df.isin(mul_sel2).sum(axis=0)>0]

#選択された項目で抽出したデータフレーム
data = df[df[select_columns].isin(mul_sel).sum(axis=1)==len(select_columns)]
# selected = [method,"ローソク"]
# print(selected)
# data = df[df[method]=="〇"][df["ローソク"]==button1].drop(columns=selected)


st.subheader('Data') 
st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">20個程度まで絞ってください。</p>', unsafe_allow_html=True)

gb = GridOptionsBuilder.from_dataframe(data)
#gb.configure_grid_options(rowHeight=30)
#https://www.ag-grid.com/javascript-data-grid/column-groups/
gb.configure_side_bar()
gb.configure_pagination(paginationPageSize=30)
gb.configure_selection(selection_mode = 'multiple', use_checkbox=True)
gb.configure_default_column(filterable=True,sortable=True,enablePivot = False, enableValue = False)
gb.configure_column("コード", headerCheckboxSelection = True, headerCheckboxSelectionFilteredOnly=True)#めちゃ大事

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
        storage_df = df.copy().set_index("コード").loc[storaged_data].iloc[:,:1]
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
    st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">サイドバーのサイズでチャートサイズを変えられます</p>', unsafe_allow_html=True)
    if num > 0 :
        
        for i, selcect in enumerate(selects):
            code = selects[i]["コード"]
            stock_name = selects[i]["銘柄"]
            st.write(f"Kabutan URL [{code}  {stock_name} ](https://kabutan.jp/stock/chart?code={code})")
            img=f"https://www.kabudragon.com/chart/s={code}/e=230502.png/"
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

