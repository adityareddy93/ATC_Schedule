import pandas as pd
import json
import datetime
import sys
from datetime import timedelta
from datetime import datetime as dt_1
import math
# Number of machine models in each machine.
a_dict_unit_1 = {'turning': 2, 'milling': 8, 'edm': 5, 'wire_cut': 6}
a_dict_unit_2 = {'turning': 3, 'milling': 5, 'edm': 2, 'wire_cut': 0}
a_dict_unit_3 = {'turning': 0, 'milling': 0, 'edm': 0, 'wire_cut': 0}
a_dict_unit_4 = {'turning': 2, 'milling': 7, 'edm': 4, 'wire_cut': 4}
UNITS = ['unit 1', 'unit 2', 'unit 3', 'unit 4']

starting_day_of_current_year = dt_1.now().date().replace(month=1, day=1, year = dt_1.now().date().year)
hourly_periods = 8760
#start_date_ref = pd.to_datetime(starting_day_of_current_year.strftime('%Y-%m-%d'))# - pd.Timedelta(days=365)
drange = pd.date_range(starting_day_of_current_year, periods=hourly_periods, freq='H')
data_ref = list(range(1,len(drange)+1))
# create data frame with drange index
df_ref = pd.DataFrame({'date':drange})
df_ref['Hours'] = data_ref
#print(df_ref)
hours_split = df_ref['date'].astype(str).str.split(pat = ' ', expand = True,n=1)
df_ref.insert(loc = 2, column = 'Date', value = hours_split[0])
def check_weekend(date):
    if date.weekday() == 6:
        return "True"
    else:
        return "False"
df_ref["is_sunday"] = pd.to_datetime(df_ref["Date"]).map(lambda x: check_weekend(x))
print(df_ref)
#print('-----------')


def return_empty_df(df):
    isempty = df.empty
    if (isempty):
        return pd.DataFrame()
    else:
        return df

# Helper function to check Sunday and get Monday date
def check_weekend(date):
    if date.weekday() == 6:
        return date + pd.Timedelta(days=1)
    else:
        return date

# Function to filter dataframe with
def return_unit_capacity(unit, machine_name):
    capacity_value = 1
    if unit == 'unit 1':
        capacity_value = a_dict_unit_1.get(machine_name)
    elif unit == 'unit 2':
        capacity_value = a_dict_unit_2.get(machine_name)
    elif unit == 'unit 3':
        capacity_value = a_dict_unit_3.get(machine_name)
    elif unit == 'unit 4':
        capacity_value = a_dict_unit_4.get(machine_name)
    else:
        capacity_value = capacity_value

    return capacity_value * 24

# Function to calculate actual dates for each machine
def cal_dates(df):
    df.loc[0, 'actual_start_date'] = df.loc[0, 'insertion_date']
    if df.shape[0] >= 4:
        index = 1
        for i in range(index, len(df)):
            if i < index + 3:
                df.loc[i, 'actual_start_date'] = df.loc[i - 1, 'actual_start_date'] + pd.Timedelta(days=2)
                # Checking
                df.loc[i, 'actual_start_date'] = check_weekend(df.loc[i, 'actual_start_date'])
            else:
                df.loc[i, 'actual_start_date'] = df.loc[i - 4, 'actual_start_date'] + pd.to_timedelta(
                    df.loc[i - 4, 'total_actual_days'], unit='D') + pd.Timedelta(days=1)
                # Checking
                df.loc[i, 'actual_start_date'] = check_weekend(df.loc[i, 'actual_start_date'])
                if df.loc[i, 'insertion_date'] > df.loc[i, 'actual_start_date']:
                    df.loc[i, 'actual_start_date'] = df.loc[i, 'insertion_date']
                    # Checking
                    df.loc[i, 'actual_start_date'] = check_weekend(df.loc[i, 'actual_start_date'])
                    index = i + 1
                else:
                    continue
    elif (df.shape[0] > 1 & df.shape[0] < 4):
        df['actual_start_date'] = df['actual_start_date'] + pd.Timedelta(days=2)
    else:
        df["actual_start_date"] = df["insertion_date"]
        return df

    return df

def cal_end_hours(machine, hours, estimated_hours):
    total_hours = 0
    if machine == 'turning':
        total_hours = hours+(estimated_hours/2)
    if machine == 'milling':
        total_hours = hours+(estimated_hours/8)+48
    if machine == 'edm':
        total_hours = hours+(estimated_hours//5)+96
    if machine == 'wire_cut':
        total_hours = hours+(estimated_hours//6)+144
    return total_hours

def cal_forcast_dates(df,tur,mil,edm_,wc,i):
    if df.loc[i,'machine']=='turning':
        if tur < df.loc[i,'insertion_date']:
            hours = df_ref.loc[df_ref['date'] == df.loc[i,'insertion_date'],'Hours']
            end_hours = hours+(df.loc[i,'estimated_hours']/2)
            end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
            week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
            df.at[i,'actual_start_date'] = df.loc[i,'insertion_date']
            diff_hours = df.loc[i,'buffer_hours'] - df.loc[i,'estimated_hours']
            if week_endCheck.shape[0] == 0:
                tur = end_date.values[0]
                df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date.values[0])+timedelta(hours=diff_hours)
            else:
                end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                tur = end_date
                df.at[i,'completion_date_with_out_buffer'] = end_date
                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date)+timedelta(hours=diff_hours)
        else:
            hours = df_ref.loc[df_ref['date'] == tur,'Hours']
            end_hours = hours+(df.loc[i,'estimated_hours']/2)
            end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
            df.at[i,'actual_start_date'] = pd.Timestamp(tur)
            diff_hours = df.loc[i,'buffer_hours'] - df.loc[i,'estimated_hours']
            week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'actual_start_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
            if week_endCheck.shape[0] == 0:
                tur = end_date.values[0]

                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date.values[0])+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
            else:
                end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                tur = end_date

                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date)+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date
    elif df.loc[i,'machine']=='milling':
        if mil < df.loc[i,'insertion_date']:
            hours = df_ref.loc[df_ref['date'] == df.loc[i,'insertion_date'],'Hours']
            end_hours = hours+(df.loc[i,'estimated_hours']/8)+48
            end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
            #mil = end_date.values[0]
            df.at[i,'actual_start_date'] = df.loc[i,'insertion_date']+timedelta(hours=48)
            diff_hours = df.loc[i,'buffer_hours'] - df.loc[i,'estimated_hours']
            week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
            if week_endCheck.shape[0] == 0:
                mil = end_date.values[0]

                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date.values[0])+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
            else:
                end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                mil = end_date

                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date)+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date
        else:

            hours = df_ref.loc[df_ref['date'] == mil,'Hours']
            end_hours = hours+(df.loc[i,'estimated_hours']/8)#+48
            end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']

            df.at[i,'actual_start_date'] = pd.Timestamp(mil)#+timedelta(hours=48)
            diff_hours = df.loc[i,'buffer_hours'] - df.loc[i,'estimated_hours']

            week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'actual_start_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]

            if week_endCheck.shape[0] == 0:
                mil = end_date.values[0]

                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date.values[0])+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
            else:
                end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                mil = end_date

                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date)+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date
    elif df.loc[i,'machine']=='edm':
        if edm_ < df.loc[i,'insertion_date']:
            hours = df_ref.loc[df_ref['date'] == df.loc[i,'insertion_date'],'Hours']
            end_hours = hours+(df.loc[i,'estimated_hours']/5)+96
            end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']

            df.at[i,'actual_start_date'] = df.loc[i,'insertion_date']+ timedelta(hours=96)
            diff_hours = df.loc[i,'buffer_hours'] - df.loc[i,'estimated_hours']
            week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
            if week_endCheck.shape[0] == 0:
                edm_ = end_date.values[0]


                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date.values[0])+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
            else:
                end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                edm_ = end_date



                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date)+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date
        else:
            hours = df_ref.loc[df_ref['date'] == edm_,'Hours']
            end_hours = hours+(df.loc[i,'estimated_hours']/5)#+96
            end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
            diff_hours = df.loc[i,'buffer_hours'] - df.loc[i,'estimated_hours']

            df.at[i,'actual_start_date'] = pd.Timestamp(edm_)#+ timedelta(hours=96)
            week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'actual_start_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
            if week_endCheck.shape[0] == 0:
                edm_ = end_date.values[0]

                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date.values[0])+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
            else:
                end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                edm_ = end_date

                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date)+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date
    elif df.loc[i,'machine']=='wire_cut':
        if wc < df.loc[i,'insertion_date']:
            hours = df_ref.loc[df_ref['date'] == df.loc[i,'insertion_date'],'Hours']
            end_hours = hours+(df.loc[i,'estimated_hours']/6)+144
            end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
            diff_hours = df.loc[i,'buffer_hours'] - df.loc[i,'estimated_hours']

            df.at[i,'actual_start_date'] = df.loc[i,'insertion_date']+ timedelta(hours=144)
            week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
            if week_endCheck.shape[0] == 0:
                wc = end_date.values[0]

                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date.values[0])+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
            else:
                end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                wc = end_date

                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date)+timedelta(hours=diff_hours)

                df.at[i,'completion_date_with_out_buffer'] = end_date
        else:

            hours = df_ref.loc[df_ref['date'] == wc,'Hours']
            end_hours = hours+(df.loc[i,'estimated_hours']/6)#+144

            end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
            diff_hours = df.loc[i,'buffer_hours'] - df.loc[i,'estimated_hours']

            df.at[i,'actual_start_date'] = pd.Timestamp(wc) #+ timedelta(hours=144)
            week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'actual_start_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
            if week_endCheck.shape[0] == 0:
                wc = end_date.values[0]
                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date.values[0])+timedelta(hours=diff_hours)
                df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
            else:
                end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                wc = end_date
                df.at[i,'completion_date_with_buffer'] = pd.Timestamp(end_date)+timedelta(hours=diff_hours)
                df.at[i,'completion_date_with_out_buffer'] = end_date
    return df,tur,mil,edm_,wc

# Calculate forcast date for total load on systems.
def forcast_tool_output(df):
    # if (!(df)) {
    #     return pd.DataFrame()
    # }
    # print(df)

    #  Remove \d+ for match digits after decimal for eg: 4.0 -> 4
    df['tool_no'] = df['tool_no'].astype(str).replace('\.\d+', '', regex=True)

    # pd.set_option('precision', 0)
    df = df.drop_duplicates(['unit', "tool_no", "tool_name", "machine", "insert"])

    df["tool_name"] = df['tool_name'].str.lower()
    df["insert"] = df['insert'].str.lower()
    df = df.applymap(lambda x: x.lower() if type(x) == str else x)

    df['tool_info'] = df['tool_no'].astype(str) + " " + df['tool_name'].astype(str)
    df['estimated_hours'] = df['estimated_hours'].fillna(0)
    df['buffer_hours'] = df['buffer_hours'].fillna(10)
    # df['estimated_hours'] = df['estimated_hours']*df['num_of_inserts']
    # df['buffer_hours'] = df['buffer_hours']*df['num_of_inserts']

    # Buffer hours wiil be in percentage converting percentage to values
    df['buffer_hours'] = df['estimated_hours'] + ((df['estimated_hours']*df['buffer_hours'])/100)
    order = ['turning','milling','edm','wire_cut']
    df['machine'] = pd.Categorical(df['machine'], order)
    # print(df)
    # df = df.sort_values(by = ['insertion_date','unit','machine'])
    insertion_date = df.drop_duplicates(["unit", "tool_info", "machine"])

    df_dummy = df.drop_duplicates(["unit", "tool_info", "machine"]).reset_index()

    list_unique = list(df.drop_duplicates(['tool_info']).tool_info.tolist())

    df = df.groupby(["unit", "tool_info", "machine"], sort=False)[['estimated_hours', 'buffer_hours']].sum().reset_index()

    df['tool_info'] = pd.Categorical(df['tool_info'], categories=list_unique, ordered=True)
    df = df.sort_values('tool_info').reset_index(drop=True)

    df = pd.merge(df,insertion_date[['unit','tool_info','machine','insertion_date']],on=['unit','tool_info','machine'], how='inner')
    # Creating a primary key for total load on systems table (1st table)
    df['total_load_pk'] = df['unit'].astype(str) + '_' + df['tool_info'].astype(str) + '_' + df['machine'].astype(str)
    # convert insert_add_dt to DateTime format
    df['insertion_date'] = pd.to_datetime(df['insertion_date'])#, format='%Y-%m-%d')
    #print(df.insertion_date)

    # return_unit_capacity function returns capacity value.
    df["capacity_day"] = df.apply(lambda x: return_unit_capacity(x['unit'], x['machine']), axis = 1)
    df['insertion_date'] = pd.to_datetime(df['insertion_date'])
    # df = df.sort_values(by='insertion_date').reset_index(drop=True)

    df['total_actual_days'] = round(df['estimated_hours'] /df['capacity_day'])

    df['actual_start_date'] = ''
    df['completion_date_with_out_buffer'] = ''
    df['completion_date_with_buffer'] = ''

    u1_tur=u1_mil=u1_edm=u1_wc=u2_tur=u2_mil=u2_edm=u2_wc=u3_tur=u3_mil=u3_edm=u3_wc=u4_tur=u4_mil=u4_edm=u4_wc = df_ref.loc[df_ref['Hours'] == 1,'date'].values[0]
    # print("&&&&&&&&&&&&&&&&&&&&&&&&")
    # print(u1_tur)
    remaining = 0
    # print(df)
    for i in range(len(df)):
        if df.loc[i,'unit']=='unit 1' or df.loc[i,'unit']=='unit1':
            df,u1_tur,u1_mil,u1_edm,u1_wc = cal_forcast_dates(df,u1_tur,u1_mil,u1_edm,u1_wc,i)
        elif df.loc[i,'unit']=='unit 2' or df.loc[i,'unit']=='unit2':
            df,u2_tur,u2_mil,u2_edm,u2_wc = cal_forcast_dates(df,u2_tur,u2_mil,u2_edm,u2_wc,i)
        elif df.loc[i,'unit']=='unit 3' or df.loc[i,'unit']=='unit3':
            df,u3_tur,u3_mil,u3_edm,u3_wc = cal_forcast_dates(df,u3_tur,u3_mil,u3_edm,u3_wc,i)
        elif df.loc[i,'unit']=='unit 4' or df.loc[i,'unit']=='unit4':
            df,u4_tur,u4_mil,u4_edm,u4_wc = cal_forcast_dates(df,u4_tur,u4_mil,u4_edm,u4_wc,i)
    # print(df)
    #df_with_fd = cal_forcast_dates(df)
    # print(df_with_fd)
    #df_ref.loc[df_ref['Hours'] == 1,'date'].values[0]

    df['completion_date_with_out_buffer'] = pd.to_datetime(df['completion_date_with_out_buffer']).dt.strftime("%Y-%m-%d %H:%M:%S")
    df['completion_date_with_buffer'] = pd.to_datetime(df['completion_date_with_buffer']).dt.strftime("%Y-%m-%d %H:%M:%S")

    return df




# Replace with above function in views.py
def total_load_on_systems_output(total_load_on_systems_input):
    isempty = total_load_on_systems_input.empty
    if (isempty):
        return pd.DataFrame()

    total_load_on_systems_output = forcast_tool_output(total_load_on_systems_input)
    # print(total_load_on_systems_output)
    # Cal dataframe with min of actual start date
    total_load_start_date = total_load_on_systems_output[
        ["unit", "tool_info", "actual_start_date"]].copy()

    total_load_start_date['actual_start_date'] = pd.to_datetime(total_load_start_date.actual_start_date, format='%Y-%m-%d')
    total_load_start_date = total_load_start_date.loc[total_load_start_date.groupby(['unit', 'tool_info'],sort=False).actual_start_date.idxmin()]
    # calulate another df with max of complete date with out buffer
    total_load_completion_date = total_load_on_systems_output[
        ["unit", "tool_info", "completion_date_with_out_buffer"]].copy()
    total_load_completion_date['completion_date_with_out_buffer'] = pd.to_datetime(total_load_completion_date.completion_date_with_out_buffer, format='%Y-%m-%d %H:%M:%S')
    total_load_completion_date = total_load_completion_date.loc[total_load_completion_date.groupby(['unit', 'tool_info'],sort=False).completion_date_with_out_buffer.idxmax()]


    # calulate df with max of complete date with  buffer
    total_load_completion_date_wb = total_load_on_systems_output[["unit", "tool_info", "completion_date_with_buffer"]].copy()
    total_load_completion_date_wb['completion_date_with_buffer'] = pd.to_datetime(total_load_completion_date_wb.completion_date_with_buffer, format='%Y-%m-%d %H:%M:%S')

    total_load_completion_date_wb = total_load_completion_date_wb.loc[total_load_completion_date_wb.groupby(['unit', 'tool_info'],sort=False).completion_date_with_buffer.idxmax()]

    merged_df = pd.merge(total_load_start_date, total_load_completion_date,on=['unit', 'tool_info'],how='inner')
    merged_df = pd.merge(merged_df, total_load_completion_date_wb,on=['unit', 'tool_info'],how='inner')

    #print(merged_df)
    merged_df['completion_date_with_out_buffer_week'] = 'Week '+merged_df['completion_date_with_out_buffer'].dt.isocalendar().week.astype(str)
    merged_df['completion_date_with_buffer_week'] = 'Week '+merged_df['completion_date_with_out_buffer'].dt.isocalendar().week.astype(str)
    merged_df['completion_date_with_out_buffer'] = pd.to_datetime(merged_df['completion_date_with_out_buffer'])
    # merged_df = merged_df.sort_values(by='completion_date_with_out_buffer').reset_index()
    # print(merged_df)

    return merged_df

def usage_efficiency_report(total_load_input, daily_report_input, *args):

    if ((total_load_input.empty) or (daily_report_input.empty)):
        return pd.DataFrame()

    result_df = daily_report_output(total_load_input, daily_report_input, 'DAILY_REPORT')

    if (result_df.empty):
        return pd.DataFrame()

    if (args):
        for str in args:
            if (str == 'EFFICIENCY'):
                return result_df
            else:
                break

    # print(result_df)

    result_df["tool_info"] = result_df["unit"] + ', ' + result_df["tool_info"]
    result_df['_ID'] = result_df['tool_info'] + result_df['machine']
    result_df['unique_id'] = pd.factorize(result_df['_ID'])[0]
    # print(merged_df_)
    # daily_df = pd.merge(daily_df_, daily_df, how='inner', on=["unit", "tool_info"])
    # print(daily_df)
    pivoted_df = result_df.pivot(index=['tool_info'], columns='machine', values=["estimated_hours", "num_of_hours", "max_daily_date"]).reset_index()
    pivoted_df.columns.name=None
    pivoted_df = pivoted_df.fillna(0)

    # print(pivoted_df)
    return pivoted_df


def accuarcy_quality_report(quality_report_input, *args):
    # quality_report_input = return_empty_df(quality_report_input)
    isempty = quality_report_input.empty
    if (isempty):
        return pd.DataFrame()

    quality_report_input = quality_report_input.drop_duplicates(['unit', "tool_no", "tool_name", "machine"])
    # print(quality_report_input.dtypes)
    # Convert input to lower case
    quality_report_input["insert"] = quality_report_input['insert'].str.lower()
    quality_report_input["tool_name"] = quality_report_input['tool_name'].str.lower()
    quality_report_input["unit"] = quality_report_input['unit'].str.lower()
    quality_report_input["machine"] = quality_report_input['machine'].str.lower()

    # print(quality_report_input)
    # quality_report_input = quality_report_input.applymap(lambda x: x.lower() if type(x) == str else x)
    quality_report_input = quality_report_input.drop('id', axis=1)
    # quality_report_input = quality_report_input.melt(id_vars=["unit", "tool_no", "tool_name", "insert", "num_of_rejects", "insertion_date"],
    #     var_name="machine",
    #     value_name="accuracy")

    # quality_report_input['accuracy'] = quality_report_input['accuracy'].astype(str).astype(int)

    quality_report_input['estimated_cost'] = quality_report_input['num_of_rejects'] * 2000

    quality_report_input['tool_info'] = quality_report_input['tool_no'] + " " + quality_report_input['tool_name']

    if (args):
        for str in args:
            if (str == 'OVERALL_EFFICIENCY'):
                quality_report_input = quality_report_input.groupby(["unit", "tool_info", "machine"], sort=False)[['num_of_rejects', 'estimated_cost']].sum().reset_index()
                return quality_report_input
            else:
                break
            break
    dff = quality_report_input.groupby(["unit", "tool_info"], sort=False)[['num_of_rejects', 'estimated_cost']].sum().reset_index()

    # dff['quality_hours_pk'] = dff['unit'] + "_" + dff['tool_info'] + "_" + dff['machine']

    dff = dff[
        ["unit", "tool_info", "num_of_rejects", "estimated_cost"]]


    return dff

def overall_efficiency_report(total_load_input, daily_report_input, quality_report_input, *args):

    if ((total_load_input.empty) or (daily_report_input.empty) or (quality_report_input.empty)):
        return pd.DataFrame()

    quality_report_input = accuarcy_quality_report(quality_report_input, 'OVERALL_EFFICIENCY')

    # print(quality_report_input)
    # daily_report_df = daily_report_output(total_load_input, daily_report_input, 'USAGE_EFFICIENCY')
    usage_df = usage_efficiency_report(total_load_input, daily_report_input, 'EFFICIENCY')

    if (usage_df.empty):
        return pd.DataFrame()

    # print(usage_df)
    usage_df["overall_efficiency"] = round((usage_df["estimated_hours"] * 100)/ usage_df["num_of_hours"])
    efficiency_with_rejects_df = pd.merge(usage_df, quality_report_input, how='left', on=["unit", "tool_info", "machine"])

    efficiency_with_rejects_df["tool_info"] = efficiency_with_rejects_df["unit"] + ', ' + efficiency_with_rejects_df["tool_info"]
    efficiency_with_rejects_df['_ID'] = efficiency_with_rejects_df['tool_info'] + efficiency_with_rejects_df['machine']
    efficiency_with_rejects_df['unique_id'] = pd.factorize(efficiency_with_rejects_df['_ID'])[0]

    pivoted_df = efficiency_with_rejects_df.pivot(index=['tool_info'], columns='machine', values=["overall_efficiency", "num_of_rejects"]).reset_index()
    pivoted_df.columns.name=None
    pivoted_df = pivoted_df.fillna(0)

    return pivoted_df

def daily_report_output(total_load_input, daily_report, *args):

    if ((total_load_input.empty) or (daily_report.empty)):
        return pd.DataFrame()

    #  Remove \d+ for match digits after decimal for eg: 4.0 -> 4
    daily_report['tool_no'] = daily_report['tool_no'].astype(str).replace('\.\d+', '', regex=True)

    # Drop duplicates for daily report if it has same unit, tool info, insert, machine, machine_name and daily_date
    daily_report_input = daily_report.drop_duplicates(subset=["unit", "tool_no", "tool_name", "insert", "machine", "machine_name", "daily_date"]).reset_index().copy()
    # df["tool_no"] = df["tool_no"].astype(str).astype(int)
    # convert_dict = {'tool_no': int}
    #
    # daily_report_input = daily_report_input.astype(convert_dict)
    total_load_on_systems_output = forcast_tool_output(total_load_input)

    # print(total_load_on_systems_output)
    load_with_completion_dt = total_load_on_systems_output[["unit", "tool_info", "machine", "completion_date_with_out_buffer"]]
    # print(total_load_on_systems_output)
    total_load_on_systems_output = total_load_on_systems_output[["unit", "tool_info", "machine", "estimated_hours"]]
    # print(total_load_on_systems_output)

    # Convert input to lower case
    daily_report_input["insert"] = daily_report_input['insert'].str.lower()
    daily_report_input["tool_name"] = daily_report_input['tool_name'].str.lower()
    daily_report_input["machine_name"] = daily_report_input['machine_name'].str.lower()
    daily_report_input = daily_report_input.applymap(lambda x: x.lower() if type(x) == str else x)

    # daily_report_input = daily_report_input[["unit", "tool_no", "tool_name", "insert", "machine", "num_of_hours", "daily_date"]]
    daily_report_input['tool_info'] = daily_report_input['tool_no'] + " " + daily_report_input['tool_name']

    tool_hours_group_df = daily_report_input.groupby(["unit", "tool_info", "machine"], sort=False).num_of_hours.sum().reset_index()
    # print(tool_hours_group_df)
    daily_date_group_df = daily_report_input.groupby(["unit", "tool_info", "machine", "status", "daily_date"], sort=False).num_of_hours.sum().reset_index()
    # To get the latest date
    # total_load_start_date = total_load_on_systems_output[["unit", "tool_info", "actual_start_date"]]

    daily_date_group_df['daily_date'] = pd.to_datetime(daily_date_group_df.daily_date, format='%Y-%m-%d')
    # To get the minimum daily date dataframe
    daily_date_group_min_df = daily_date_group_df[["unit", "tool_info", "machine", "daily_date"]]
    daily_date_group_min_df = daily_date_group_min_df.loc[daily_date_group_min_df.groupby(['unit', 'tool_info', 'machine']).daily_date.idxmin()]
    daily_date_group_min_df = daily_date_group_min_df.rename(columns = {"daily_date": "actual_machine_start_date"})

    # To get the maximun daily date dataframe
    daily_date_group_df = daily_date_group_df.loc[daily_date_group_df.groupby(['unit', 'tool_info', 'machine']).daily_date.idxmax()]
    # Output latest daily record for each unit, tool and machine

    daily_date_group_df = daily_date_group_df.rename(columns = {"num_of_hours": "max_date_grouped_daily_hours",
                                                                "daily_date": "max_daily_date"})

    merged_df_with_max_date = pd.merge(daily_date_group_df, tool_hours_group_df, how='inner', left_on=["unit", "tool_info", "machine"], right_on=["unit", "tool_info", "machine"])

    # print(merged_df_with_max_date)
    # Adding minimum date of unit, tool info, machine as start date
    merged_df = pd.merge(daily_date_group_min_df, merged_df_with_max_date, how='inner', left_on=["unit", "tool_info", "machine"], right_on=["unit", "tool_info", "machine"])

    # print("Last Merge")
    # print(total_load_on_systems_output)
    # print(merged_df)
    # Merge to add estimated hours to daily report
    merged_df_ = pd.merge(total_load_on_systems_output, merged_df, how='inner', left_on=["unit", "tool_info", "machine"], right_on=["unit", "tool_info", "machine"])

    # print(merged_df_)
    if (args):
        for str_report in args:
            if str_report == 'DAILY_REPORT':
                return merged_df_
            else:
                break

    if (merged_df_.empty):
        return pd.DataFrame()

    daily_df_ = merged_df_[merged_df_["status"] == 'completed']

    daily_df_ = daily_df_.groupby(['unit', 'tool_info'])['status'].count().reset_index()

    daily_df_ = daily_df_[daily_df_['status'] == 4]


    result_df = pd.merge(merged_df_, daily_df_[["unit", "tool_info"]], on=['unit','tool_info'], how="outer", indicator=True).query('_merge=="left_only"')

    # Merge values to get the completion dates
    with_completion_dt = pd.merge(result_df, load_with_completion_dt, how='inner', left_on=["unit", "tool_info", "machine"], right_on=["unit", "tool_info", "machine"])

    with_completion_dt["balance_hours_as_on_today"] = with_completion_dt["estimated_hours"] - with_completion_dt["num_of_hours"]
    with_completion_dt = with_completion_dt.apply(balance_hour_validation, axis=1)

    with_completion_dt = with_completion_dt[['unit', 'tool_info', 'machine', 'actual_machine_start_date', 'max_date_grouped_daily_hours', 'max_daily_date', 'balance_hours_as_on_today', 'completion_date_with_out_buffer']]
    # To show the latest date daily report results
    with_completion_dt = with_completion_dt.loc[with_completion_dt.groupby(['unit', 'tool_info', 'machine']).max_daily_date.idxmax()]
    # print(merged_df_)
    # with_completion_dt['completion_date_with_out_buffer'] = with_completion_dt['completion_date_with_out_buffer'].dt.date
    with_completion_dt["tool_info"] = with_completion_dt["unit"] + ', ' + with_completion_dt["tool_info"]
    with_completion_dt['_ID'] = with_completion_dt['tool_info'] + with_completion_dt['machine']
    with_completion_dt['unique_id'] = pd.factorize(with_completion_dt['_ID'])[0]
    # print(with_completion_dt)
    pivoted_df = with_completion_dt.pivot(index=['tool_info'], columns='machine', values=["max_date_grouped_daily_hours", "balance_hours_as_on_today", "actual_machine_start_date", "completion_date_with_out_buffer"]).reset_index()
    pivoted_df.columns.name=None
    pivoted_df = pivoted_df.fillna(0)

    return pivoted_df

# Function to calculate expected hours as on today.
def cal_expected_hours_as_on_today(df):
    if df.empty:
        return pd.DataFrame()
    capacity = return_unit_capacity(df.loc[0, "unit"], df.loc[0, "machine"])
    # If Capacity is less than the estimated hours then zero
    if df.loc[0, "estimated_hours"] > capacity:
        df.loc[0, "expected_hours_as_on_today"] = df.loc[0, "estimated_hours"] - capacity
        df.loc[0, "expected_hours_as_on_today_with_buffer"] = df.loc[0, "buffer_hours"] - capacity
    else:
        df.loc[0, "expected_hours_as_on_today"] = 0
        df.loc[0, "expected_hours_as_on_today_with_buffer"] = 0

    if (df.shape[0] == 1):
        return df
    else:
        for i in range(1, len(df)):
            if df.loc[i, "estimated_hours"] > capacity:
                df.loc[i, "expected_hours_as_on_today"] = df.loc[i-1, "expected_hours_as_on_today"] - capacity
                df.loc[i, "expected_hours_as_on_today_with_buffer"] = df.loc[i-1, "expected_hours_as_on_today_with_buffer"] - capacity
            else:
                df.loc[i, "expected_hours_as_on_today"] = 0
                df.loc[i, "expected_hours_as_on_today_with_buffer"] = 0

        return df

    # df.loc[0, "expected_hours_as_on_today"] = df.loc[0, "estimated_hours"] - capacity
    # df.loc[0, "expected_hours_as_on_today_with_buffer"] = df.loc[0, "buffer_hours"] - capacity
    # if (df.shape[0] == 1):
    #     return df
    # else:
    #     for i in range(1, len(df)):
    #         capacity = return_unit_capacity(df.loc[i, "unit"], df.loc[i, "machine"])
    #         df.loc[i, "expected_hours_as_on_today"] = df.loc[i-1, "expected_hours_as_on_today"] - capacity
    #         df.loc[i, "expected_hours_as_on_today_with_buffer"] = df.loc[i-1, "expected_hours_as_on_today_with_buffer"] - capacity

        # return df

# Validations
def add_progress_to_expected_hours(row):
    if row["expected_hours_as_on_today"] < 0:
        row["expected_hours_as_on_today"] = 'Delayed' + '(' + str(row["expected_hours_as_on_today"]) + ')'
    elif row["expected_hours_as_on_today"] == 0:
        row["expected_hours_as_on_today"] = 'Expected'
    else:
        row["expected_hours_as_on_today"] = 'progress' + '(' + str(row["expected_hours_as_on_today"]) + ')'

    if row["expected_hours_as_on_today_with_buffer"] < 0:
        row["expected_hours_as_on_today_with_buffer"] = 'Delayed' + '(' + str(row["expected_hours_as_on_today_with_buffer"]) + ')'
    elif row["expected_hours_as_on_today_with_buffer"] == 0:
        row["expected_hours_as_on_today_with_buffer"] = 'Expected'
    else:
        row["expected_hours_as_on_today_with_buffer"] = 'progress' + '(' + str(row["expected_hours_as_on_today_with_buffer"]) + ')'

    # Validation for balance_hours_as_on_today
    if row["balance_hours_as_on_today"] < 0:
        row["balance_hours_as_on_today"] = 0

    return row

def balance_hour_validation(row):
    # Validation for balance_hours_as_on_today
    if row["balance_hours_as_on_today"] < 0:
        row["balance_hours_as_on_today"] = 0
    if ((row["balance_hours_as_on_today"] > 0) & (row["status"] == "completed")):
        row["balance_hours_as_on_today"] = 0
    return row

def cap_value_validation(row):
    # Validation for balance_hours_as_on_today
    if row["estimated_hours"] < row["num_of_hours"]:
        row["cap_value"] = 0
    elif row["num_of_hours"] == row["estimated_hours"]:
        row["cap_value"] = 0
    else:
        row["cap_value"] = round(row["num_of_hours"] / row["capacity_day"])

    return row

# def status_validation(row):
#     row["status"] == 'completed'
