import pandas as pd
import streamlit as st
import sqlite3 as sq
st.set_page_config(page_title='DRS extended', layout='wide')
db = 'mms_master.sqlite'

disp_cols = ['ship_name', 'dt_ocurred', 'target_dt', 'done_dt', 'ser_no', 'nc_detail', 'est_cause_ship',
             'init_action_ship', 'init_action_ship_dt',
             'final_action_ship', 'final_action_ship_dt', 'co_eval',
             'reason_rc', 'corr_action', 'rpt_by', 'insp_by', 'insp_detail', 'update_by', 'update_dt',
             'ext_dt', 'ext_rsn', 'req_num', 'ext_cmnt', 'sys_code', 'eq_code']
conn = sq.connect(db)
df_DRS = pd.read_sql_query(f'select * from drsend', conn) # get DR sender data
df_vsl = pd.read_sql_query(f'select * from vessels', conn)# get vessel data
df_SI = pd.read_sql_query(f'select * from si', conn) # Get SI details
df_DRS[['delay_hr', 'downtime_hr', 'VET_risk']] = df_DRS[['delay_hr', 'downtime_hr', 'VET_risk']].apply(pd.to_numeric,errors='coerce',axis=1) #convert to numeric
df_DRS = df_DRS.loc[df_DRS['DRS_ID'].str.startswith('T', na=False)]  # remove all cargo DRS id
df_DRS['vsl_imo'] = df_DRS['vsl_imo'].astype(int) # convert IMO number to int
df_DRS = df_DRS[df_DRS.ext_dt != '']  # remove rows with no ext date
df_DRS['ext_dt'] = pd.to_datetime(df_DRS['ext_dt'], format='%Y-%m-%d', errors='coerce') # Convert date as str to datetime
df_DRS = df_DRS.query('status in ("OPEN")')# get only open items
#df_vsl= df_vsl.join(df_vsl)
df_vsl = pd.merge(df_vsl, df_SI[['SI_UID','siEmail']], left_on='vslTechSI', right_on='SI_UID', how='right')
st.write(df_vsl.shape)
st.write(df_vsl)
df_DRS = pd.merge(df_DRS,df_vsl[['vsl_imo','siEmail']],on='vsl_imo', how='left')
#df_vsl = pd.merge(df_vsl,df_SI[['vslTechSI','statusActiveInactive']],on='vsl_imo', how='left')
df_DRS = pd.merge(df_DRS,df_vsl[['vsl_imo','statusActiveInactive']],on='vsl_imo', how='left')
df_DRS.drop(df_DRS.index[df_DRS['statusActiveInactive'] == 0], inplace=True)
mask = (df_DRS['ext_dt'] < pd.to_datetime('today'))
df_DRS = df_DRS.loc[mask]
st.write(df_DRS)