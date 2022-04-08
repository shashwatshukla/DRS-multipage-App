import pandas as pd
import streamlit as st
from load_Data import get_data, save_data, get_table_name
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
st.set_page_config(page_title='DRS extended', layout='wide')
disp_cols = ['ship_name', 'dt_ocurred', 'target_dt', 'done_dt', 'ser_no', 'nc_detail', 'est_cause_ship',
                 'init_action_ship', 'init_action_ship_dt',
                 'final_action_ship', 'final_action_ship_dt', 'co_eval',
                 'reason_rc', 'corr_action', 'rpt_by', 'insp_by', 'insp_detail', 'update_by', 'update_dt',
                 'ext_dt', 'ext_rsn', 'req_num', 'ext_cmnt', 'sys_code', 'eq_code']

grid_height = st.sidebar.number_input("Grid height", min_value=200, max_value=800, value=300)
js = JsCode("""
function(e) {
    let api = e.api;
    let rowIndex = e.rowIndex;
    let col = e.column.colId;

    let rowNode = api.getDisplayedRowAtIndex(rowIndex);
    api.flashCells({
      rowNodes: [rowNode],
      columns: [col],
      flashDelay: 10000000000
    });

};
""")

jsAddRow = JsCode("""
function addRow(){
      // Assuming newRow is an object, such as {"slNo": this.index,"id":3, "rank":1}
      this.gridApi.updateRowData({
        add: newRow,
        addIndex: index
    });
};
""")
t = get_table_name('mms_master.sqlite')
tbl_name = st.selectbox(label='Select table', options=t[1:])
df = get_data('mms_master.sqlite', tbl_name)
df_template = df
if tbl_name =='drsend':
    df_template = df[disp_cols]
gb = GridOptionsBuilder.from_dataframe(df_template)
gb.configure_selection(selection_mode='multiple', use_checkbox=True, groupSelectsChildren=True,groupSelectsFiltered=True)
gb.configure_grid_options(onCellValueChanged=js)
gb.configure_grid_options()
#gb.configure_pagination()
gb.configure_side_bar()
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
gridOptions = gb.build()
# st.header(tbl_name+' Data')
response = AgGrid(df_template, editable=True, fit_columns_on_grid_load=False, conversion_errors='coerce',
                  gridOptions=gridOptions, enable_enterprise_modules=True, allow_unsafe_jscode=True,
                  height=grid_height)

st.button("Upload to Database")
if st.button:
 df_template = response['data']
