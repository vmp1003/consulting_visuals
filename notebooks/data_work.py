import pandas as pd
import re
from datetime import timedelta

def load_data():
    df_1 = pd.read_csv('../data/customers.csv')
    df_2 = pd.read_csv('../data/contracts.csv')
    df_1.rename(columns = {'id':'customer_id'}, inplace=True)
    df_1.set_index('customer_id', inplace=True)
    df_2.set_index('customer_id', inplace=True)
    
    return df_2.join(df_1)

def clean_values(df):
    for each in ['deposit', 'monthly_amt']:
        df.loc[:, each] = pd.to_numeric([re.sub('[^0-9.]', '', str(s)) for s in df[each]])
    
    return df

def summary_calculations(df):
    df['monthly_total_revenue'] = df['monthly_amt'] * df['contract_term']
    df['total_revenue'] = df['deposit'] + df['monthly_total_revenue']
    
    return df

def expand_timeline(row):
    cu_id = row['customer_id']
    co_id = row['contract_id']
    st_dt = row['contract_start']
    m_term = row['contract_term']
    dep = row['deposit']
    mnthly = row['monthly_amt']
    
    new_data = []
    
    deposit_row = [
        cu_id, 
        co_id,
        st_dt,
        True, 
        dep
    ]
    new_data.append(deposit_row)

    for ea in range(m_term):
        monthly_row = [
            cu_id,
            co_id,
            (st_dt + timedelta(weeks=(ea * 4))),
            False,
            mnthly
        ]
        new_data.append(monthly_row)
        df = pd.DataFrame(new_data, columns = ['customer_id', 'contract_id', 'due_date', 'deposit', 'amt_due'])
    return df

def detail_calculations(orig_df):
    orig_df['contract_start'] = pd.to_datetime(orig_df['contract_start'], format='%m/%d/%Y')
    orig_df = orig_df.reset_index()
    interim_df = orig_df.apply(lambda x: expand_timeline(x), axis=1)
    
    new_df = pd.DataFrame()
    for each in range(len(interim_df)):
        new_df = new_df.append(interim_df[each])
      
    df_c = pd.read_csv('../data/customers.csv')
    df_c.rename(columns = {'id':'customer_id'}, inplace=True)
    df_c.set_index('customer_id', inplace=True)
    new_df.set_index('customer_id', inplace=True)
    new_df = new_df.join(df_c)
    new_df.reset_index(inplace=True)
    
    new_df.set_index('due_date', inplace=True)
    new_df.sort_index(inplace=True)
    
    return new_df