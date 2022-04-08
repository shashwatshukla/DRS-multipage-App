import datetime
import plotly.express as px
import streamlit as st
import pandas as pd
import sqlite3 as sq
def dashboard():

    db = 'mms_master.sqlite'
    # ___________________________Declarations_____________________________
    disp_cols = ['ship_name', 'ser_no', 'dt_ocurred', 'target_dt', 'nc_detail',
                 'ext_dt', 'ext_rsn', 'req_num', 'ext_cmnt', 'est_cause_ship',
                 'init_action_ship', 'init_action_ship_dt',
                 'final_action_ship', 'final_action_ship_dt', 'co_eval', 'corr_action', 'rpt_by', 'insp_by',
                 'insp_detail',
                 'update_by', 'update_dt']

    # _______________Data collection_______________________
    conn = sq.connect(db)
    df_DRS = pd.read_sql_query('select * from drsend', conn)  # get DR sender data
    df_vsl = pd.read_sql_query(
        "select vslName, vsl_imo, vslTechSI, vslMarSI from vessels where statusActiveInactive = '1' "
        "and (vslFleet = '1' or vslFleet = '2' or vslFleet = '3')",
        conn)  # Get active tanker fleet vessel names and IMO
    df_SI = pd.read_sql_query("select SI_UID, siEmail from si where statusActiveInactive = '1'", conn)  # Get active SI

    # _________________Data cleaning_________________________
    df_DRS[['delay_hr', 'downtime_hr', 'VET_risk']] = df_DRS[['delay_hr', 'downtime_hr', 'VET_risk']] \
        .apply(pd.to_numeric, errors='coerce', axis=1)  # convert to numeric
    df_DRS['vsl_imo'] = df_DRS['vsl_imo'].astype(int)  # convert IMO number to int
    SI_mailid = {row.SI_UID: row.siEmail for (index, row) in
                 df_SI.iterrows()}  # convert SI uniqeid and email to dictionary dunno why i did this
    imoactive = (df_vsl['vsl_imo'])  # Tuple of active tanker vessel IMO
    active = df_DRS['vsl_imo'].isin(imoactive)
    df_active = df_DRS[active]
    df_active = df_active[df_active.ext_dt != '']  # remove rows with no ext date
    df_active['ext_dt'] = pd.to_datetime(df_active['ext_dt'], format='%Y-%m-%d',
                                         errors='coerce')  # Convert date as str to datetime
    df_active = df_active.query('status in ("OPEN")')  # get open items
    mask = (df_active['ext_dt'] < pd.to_datetime('today'))  # ext date is before today
    df_active = df_active.loc[mask]

    uniqShips = list(df_active['ship_name'].unique())  # get list of unique ships from DB
    fltList = {'All vessels': uniqShips,
               'Tanker1': sorted(
                   ['Tokio', 'Taiga', 'Tsushima', 'BW Tokyo', 'BW Kyoto', 'Marvel Kite',
                    'Takasago', 'Tenma', 'Esteem Astro', 'Esteem Explorer', 'Metahne Mickie Harper',
                    'Methane Patricia Camila', 'Red Admiral']),
               'Tanker2 SMI': sorted(
                   ['Ginga Hawk', 'Ginga Kite', 'Ginga Merlin', 'Centennial Misumi',
                    'Centennial Matsuyama', 'Argent Daisy', 'Eagle Sapporo', 'Eagle Melbourne',
                    'Challenge Prospect II', 'St Clemens', 'St Pauli', 'Esteem Houston',
                    'Esteem Energy',
                    'Esteem Discovery', 'Esteem Endeavour', 'Solar Katherine', 'Solar Melissa',
                    'Solar Madelein', 'Solar Claire', 'Esteem Sango']),
               'Tanker2 SIN': sorted(['Hafnia Nordica',
                                      'Peace Victoria', 'Orient Challenge', 'Orient Innovation', 'Crimson Jade',
                                      'Crimson Pearl', 'Hafnia Hong Kong', 'Hafnia Shanghai', 'San Jack',
                                      'Hafnia Shenzhen', 'HARRISBURG', 'Hafnia Nanjing'])
               }

    # _______________________UI elements and logic_____________________

    filterContainer = st.expander('Data for overdue def past extension date')
    col1, col2 = filterContainer.columns(2)
    with col1:
        fltName = st.multiselect('Select the Fleet', options=fltList.keys(), default='Tanker1')

        with filterContainer:
            vslListPerFlt = sum([fltList[x] for x in fltName],
                                [])  # get vsl names as per flt selected and flatten the list (sum)
            vslName = st.multiselect('Select the vessel:', options=vslListPerFlt, default=vslListPerFlt)
            # df_sel_vsl_counts = (df_counts[df_counts['ship_name'].isin(vslName)])
            # st.write(df_sel_vsl_counts)
            # fig = px.bar(df_sel_vsl_counts, x="ship_name", y=["Closed", "Open"], barmode='stack', height=400)
            # st.plotly_chart(fig)



        with filterContainer:
            #  now filter the dataframe using all above filter settings
            df_active = df_active.query("ship_name == @vslName")  # & status == @statusNow & brkdn_tf == @brkdn "
            # "& critical_eq_tf == @criticalEq & docking_tf == @docking & blackout_tf == @blackout"
            # "& coc_tf == @coc & overdue == @overDueStat & Severity == @severity & rpt_by == @rptBy")

            # dfFiltered = dfFiltered[dfFiltered['nc_detail'].str.contains(searchText, regex=False)]  # search on text entered
            st.write(df_active[disp_cols], height=600)
            # TODO: get count of records for each unique vessel (for plot)

        with col2:  # download button and file
            csv = df_active.to_csv().encode('utf-8')  # write df to csv
            btnMsg = 'Download ' + str(df_active.shape[0]) + ' Records as CSV'
            st.download_button(btnMsg, csv, "DRS-file.csv", "text/csv", key='download-csv')
    data = df_active['ship_name'].value_counts()
    data2 = df_active['ext_rsn'].value_counts()
    df_graph = pd.DataFrame({'ship_name': data.index, 'Count': data.values})
    fig = px.bar(df_graph, x='ship_name', y='Count', height=400, width=1200, color='Count',
                 labels={"ship_name": "Vessel", "Count": "Number of def. past the extension date"})
    fig2 = px.bar(df_active, x=["ship_name"], y="ext_rsn", height=400, width=1200, color='ext_rsn')
    st.plotly_chart(fig)
    st.plotly_chart(fig2)