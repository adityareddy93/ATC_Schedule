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

# Calculate forcast date for total load on systems.
def forcast_tool_output(df):
    if (df.empty):
        return pd.DataFrame()

    df = df.drop_duplicates(['unit', "tool_no", "tool_name", "machine", "insert"])

    df["tool_name"] = df['tool_name'].str.lower()
    df["insert"] = df['insert'].str.lower()
    df = df.applymap(lambda x: x.lower() if type(x) == str else x)

    df['tool_info'] = df['tool_no'].astype(str) + " " + df['tool_name'].astype(str)

    df['estimated_hours'] = df['estimated_hours'].fillna(0)
    df['buffer_hours'] = df['buffer_hours'].fillna(10)
    df['estimated_hours'] = df['estimated_hours']*df['num_of_inserts']
    df['buffer_hours'] = df['buffer_hours']*df['num_of_inserts']

    # Buffer hours wiil be in percentage converting percentage to values
    df['buffer_hours'] = df['estimated_hours'] + ((df['estimated_hours']*df['buffer_hours'])/100)
    order = ['turning','milling','edm','wire_cut']
    df['machine'] = pd.Categorical(df['machine'], order)
    df = df.sort_values(by = ['insertion_date','unit','tool_name','machine'])
    insertion_date = df.drop_duplicates(["unit", "tool_info", "machine"])


    df = df.groupby(["unit", "tool_info", "machine"], sort=False)[['estimated_hours', 'buffer_hours']].sum().reset_index()
    df = pd.merge(df,insertion_date[['unit','tool_info','machine','insertion_date']],on=['unit','tool_info','machine'], how='inner')

    # Creating a primary key for total load on systems table (1st table)
    df['total_load_pk'] = df['unit'].astype(str) + '_' + df['tool_info'].astype(str) + '_' + df['machine'].astype(str)

    # convert insert_add_dt to DateTime format
    df['insertion_date'] = pd.to_datetime(df['insertion_date'], format='%Y-%m-%d')

    # return_unit_capacity function returns capacity value.
    df["capacity_day"] = df.apply(lambda x: return_unit_capacity(x['unit'], x['machine']), axis = 1)
    df['total_actual_days'] = round(df['estimated_hours'] /df['capacity_day'])

    #print(df)
    df['actual_start_date'] = ''
    df['Week'] = ''
    df['completion_date_with_out_buffer'] = ''
    u1_tur=u1_mil=u1_edm=u1_wc=u2_tur=u2_mil=u2_edm=u2_wc=u3_tur=u3_mil=u3_edm=u3_wc=u4_tur=u4_mil=u4_edm=u4_wc = df_ref.loc[df_ref['Hours'] == 1,'date'].values[0]
    remaining = 0
    #df_ref.loc[df_ref['Hours'] == 1,'date'].values[0]
    for i in range(len(df)):
        if df.loc[i,'unit']=='unit 1':
            if df.loc[i,'machine']=='turning':
                if u1_tur < df.loc[i,'insertion_date']:
                    # print("if")
                    hours = df_ref.loc[df_ref['date'] == df.loc[i,'insertion_date'],'Hours']
                    end_hours = hours+(df.loc[i,'estimated_hours']/2)
                    end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
                    week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
                    df.at[i,'actual_start_date'] = df.loc[i,'insertion_date']
                    if week_endCheck.shape[0] == 0:
                        u1_tur = end_date.values[0]
                        str_ = str(end_date.values[0]).split('T')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
                    else:
                        end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                        u1_tur = end_date
                        str_ = str(end_date).split(' ')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date
                else:
                    # print("else")
                    hours = df_ref.loc[df_ref['date'] == u1_tur,'Hours']
                    end_hours = hours+(df.loc[i,'estimated_hours']/2)
                    end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
                    week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
                    df.at[i,'actual_start_date'] = pd.Timestamp(u1_tur)
                    if week_endCheck.shape[0] == 0:
                        u1_tur = end_date.values[0]
                        str_ = str(end_date.values[0]).split('T')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
                    else:
                        end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                        u1_tur = end_date
                        str_ = str(end_date).split(' ')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date
            elif df.loc[i,'machine']=='milling':
                if u1_mil < df.loc[i,'insertion_date']:
                    # print("if")
                    hours = df_ref.loc[df_ref['date'] == df.loc[i,'insertion_date'],'Hours']
                    end_hours = hours+(df.loc[i,'estimated_hours']/8)+48
                    end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
                    u1_mil = end_date.values[0]
                    df.at[i,'actual_start_date'] = df.loc[i,'insertion_date']+timedelta(hours=48)
                    week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
                    if week_endCheck.shape[0] == 0:
                        u1_mil = end_date.values[0]
                        str_ = str(end_date.values[0]).split('T')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
                    else:
                        end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                        u1_mil = end_date
                        str_ = str(end_date).split(' ')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date
                else:
                    # print("else")
                    hours = df_ref.loc[df_ref['date'] == u1_mil,'Hours']
                    end_hours = hours+(df.loc[i,'estimated_hours']/8)#+48
                    end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
                    # print(pd.Timestamp(u1_mil))

                    df.at[i,'actual_start_date'] = pd.Timestamp(u1_mil)#+timedelta(hours=48)
                    week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
                    if week_endCheck.shape[0] == 0:
                        u1_mil = end_date.values[0]
                        str_ = str(end_date.values[0]).split('T')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
                    else:
                        end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                        u1_mil = end_date
                        str_ = str(end_date).split(' ')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date
            elif df.loc[i,'machine']=='edm':
                if u1_edm < df.loc[i,'insertion_date']:
                    # print("if")
                    hours = df_ref.loc[df_ref['date'] == df.loc[i,'insertion_date'],'Hours']
                    end_hours = hours+(df.loc[i,'estimated_hours']/5)+96
                    end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']

                    df.at[i,'actual_start_date'] = df.loc[i,'insertion_date']+ timedelta(hours=96)
                    week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
                    if week_endCheck.shape[0] == 0:
                        u1_edm = end_date.values[0]
                        str_ = str(end_date.values[0]).split('T')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
                    else:
                        end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                        u1_edm = end_date
                        str_ = str(end_date).split(' ')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date
                else:
                    # print("else")
                    hours = df_ref.loc[df_ref['date'] == u1_edm,'Hours']
                    end_hours = hours+(df.loc[i,'estimated_hours']/5)#+96
                    end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
                    # print(u1_edm)

                    df.at[i,'actual_start_date'] = pd.Timestamp(u1_edm)#+ timedelta(hours=96)
                    week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
                    if week_endCheck.shape[0] == 0:
                        u1_edm = end_date.values[0]
                        str_ = str(end_date.values[0]).split('T')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
                    else:
                        end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                        u1_edm = end_date
                        str_ = str(end_date).split(' ')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date
            elif df.loc[i,'machine']=='wire_cut':
                if u1_wc < df.loc[i,'insertion_date']:
                    # print("if")
                    hours = df_ref.loc[df_ref['date'] == df.loc[i,'insertion_date'],'Hours']
                    end_hours = hours+(df.loc[i,'estimated_hours']/6)+144
                    end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']

                    df.at[i,'actual_start_date'] = df.loc[i,'insertion_date']+ timedelta(hours=144)
                    week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
                    if week_endCheck.shape[0] == 0:
                        u1_wc = end_date.values[0]
                        str_ = str(end_date.values[0]).split('T')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
                    else:
                        end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                        u1_wc = end_date
                        str_ = str(end_date).split(' ')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date
                else:
                    # print("else")
                    hours = df_ref.loc[df_ref['date'] == u1_wc,'Hours']
                    end_hours = hours+(df.loc[i,'estimated_hours']/6)#+144
                    end_date = df_ref.loc[df_ref['Hours'] == round(end_hours.values[0]),'date']
                    # print(u1_wc)

                    df.at[i,'actual_start_date'] = pd.Timestamp(u1_wc) #+ timedelta(hours=144)
                    week_endCheck = df_ref[(df_ref['date'] >= df.loc[i,'insertion_date']) & (df_ref['date'] <= pd.Timestamp(end_date.values[0])) & (df_ref['is_sunday'] == "True")]
                    if week_endCheck.shape[0] == 0:
                        u1_wc = end_date.values[0]
                        str_ = str(end_date.values[0]).split('T')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date.values[0]
                    else:
                        end_date = pd.Timestamp(end_date.values[0])+timedelta(hours=24)
                        u1_wc = end_date
                        str_ = str(end_date).split(' ')[0]
                        # print(str_)
                        df.at[i,'Week'] = "Week {}".format(dt_1.strptime(str_, '%Y-%m-%d').strftime("%V"))
                        df.at[i,'completion_date_with_out_buffer'] = end_date
            else:pass

    df['completion_date_with_out_buffer'] = pd.to_datetime(df['completion_date_with_out_buffer']).dt.strftime("%Y-%m-%d %H:%M:%S")
    # print(df)


    return df




# Replace with above function in views.py
def total_load_on_systems_output(total_load_on_systems_input):
    isempty = total_load_on_systems_input.empty
    if (isempty):
        return pd.DataFrame()

    total_load_on_systems_output = forcast_tool_output(total_load_on_systems_input)
    # print(total_load_on_systems_output)
    # actual_start_date_df = total_load_on_systems_output[['tool_info', 'actual_start_date']].drop_duplicates(subset = ['tool_info'])

    # Cal dataframe with min of actual start date
    total_load_start_date = total_load_on_systems_output[
        ["unit", "tool_info", "actual_start_date"]]

    total_load_start_date['actual_start_date'] = pd.to_datetime(total_load_start_date.actual_start_date, format='%Y-%m-%d')
    total_load_start_date = total_load_start_date.loc[total_load_start_date.groupby(['unit', 'tool_info']).actual_start_date.idxmin()]

    # calulate another df with max of complete date with out buffer
    total_load_completion_date = total_load_on_systems_output[
        ["unit", "tool_info", "completion_date_with_out_buffer"]]



    total_load_completion_date['completion_date_with_out_buffer'] = pd.to_datetime(total_load_completion_date.completion_date_with_out_buffer, format='%Y-%m-%d %H:%M:%S')
    # total_load_on_systems_output["completion_date_with_out_buffer"] = total_load_on_systems_output["completion_date_with_out_buffer"]check_weekend
    # total_load_on_systems_output = total_load_on_systems_output.loc[total_load_on_systems_output.groupby('unit', 'tool_info').completion_date_with_out_buffer.idxmax()]
    total_load_completion_date = total_load_completion_date.loc[total_load_completion_date.groupby(['unit', 'tool_info']).completion_date_with_out_buffer.idxmax()]
    # End logic to give the max date of machine tools.
    # total_load_on_systems_output = total_load_on_systems_output[total_load_on_systems_output.groupby('tool_info').completion_date_with_out_buffer.transform('max') == total_load_on_systems_output['completion_date_with_out_buffer']]
    # df = total_load_on_systems_output.groupby(['unit', 'tool_info'])[['completion_date_with_out_buffer']].max().reset_index(drop=True)
    merged_df = pd.merge(total_load_start_date, total_load_completion_date,on=['unit', 'tool_info'],how='inner')

    # print("*************************************")
    # print(merged_df)
    merged_df['completion_date_with_out_buffer_week'] = merged_df['completion_date_with_out_buffer'].dt.isocalendar().week
    # merged_df['completion_date_with_buffer_week'] = merged_df['completion_date_with_out_buffer'].dt.isocalendar().week

    return merged_df

def usage_efficiency_report(total_load_input, daily_report_input, *args):

    if ((total_load_input.empty) or (daily_report_input.empty)):
        return pd.DataFrame()

    # ---------------------------------------------88**********************_-------------------------------------------------------------
    daily_df = daily_report_output(total_load_input, daily_report_input, 'DAILY_REPORT')
    if (daily_df.empty):
        return pd.DataFrame()
    # print("*********************************************")
    # print(daily_df)
    daily_df_ = daily_df[daily_df["status"] == 'completed']
    # daily_df["binary_status"] = 1
    daily_df_ = daily_df_.groupby(['unit', 'tool_info', 'machine'])['status'].count().reset_index()

    daily_df_ = daily_df_[daily_df_['status'] == 2]

    if (daily_df_.empty):
        return pd.DataFrame()

    # print(daily_df)
    # daily_df = daily_df[daily_df["count"]]
    # daily_df = daily_df.loc[daily_df.groupby(['unit', 'tool_info', 'machine']).status.eq('completed')]
    # print(daily_df)
    if (args):
        for str in args:
            if (str == 'EFFICIENCY'):
                return daily_df
            else:
                break

    daily_df["tool_info"] = daily_df["unit"] + ', ' + daily_df["tool_info"]
    daily_df['_ID'] = daily_df['tool_info'] + daily_df['machine']
    daily_df['unique_id'] = pd.factorize(daily_df['_ID'])[0]
    # print(merged_df_)
    # daily_df = pd.merge(daily_df_, daily_df, how='inner', on=["unit", "tool_info", "machine"])
    # print(daily_df)
    pivoted_df = daily_df.pivot(index=['unique_id', 'tool_info'], columns='machine', values=["estimated_hours", "num_of_hours", "max_daily_date"]).reset_index()
    pivoted_df.columns.name=None
    pivoted_df = pivoted_df.fillna(0)

    # print(pivoted_df)
    return pivoted_df


def accuarcy_quality_report(quality_report_input, *args):
    # quality_report_input = return_empty_df(quality_report_input)
    isempty = quality_report_input.empty
    if (isempty):
        return pd.DataFrame()

    quality_report_input = quality_report_input.drop_duplicates(['unit', "tool_no", "tool_name"])
    # Convert input to lower case
    quality_report_input = quality_report_input.applymap(lambda x: x.lower() if type(x) == str else x)
    quality_report_input = quality_report_input.drop('id', axis=1)
    # quality_report_input = quality_report_input.melt(id_vars=["unit", "tool_no", "tool_name", "insert", "num_of_rejects", "insertion_date"],
    #     var_name="machine",
    #     value_name="accuracy")

    # quality_report_input['accuracy'] = quality_report_input['accuracy'].astype(str).astype(int)

    quality_report_input['estimated_cost'] = quality_report_input['num_of_rejects'] * 2000

    # print(quality_report_input)
    # if (args):
    #     for str_arg in args:
    #         if str_arg == 'QUALITY_REPORT':
    #             # quality_report_input = quality_report_input[[]]
    #             quality_report_input = pd.melt(quality_report_input, id_vars=["unit", "tool_no", "tool_name", "insert", "num_of_rejects"],
    #                 var_name="machine",
    #                 value_name="accuracy")

    #             print("**************^^^^^^^^^^^^^^^^^^^^###########################")
    #             print(quality_report_input)
    #             print("**************^^^^^^^^^^^^^^^^^^^^###########################")
    #             # quality_report_input['accuracy'] = quality_report_input['accuracy'].astype(str).astype(int)
    #             dff = quality_report_input.groupby(["unit", "tool_info", "machine"], sort=False)[['num_of_rejects', 'estimated_cost']].sum().reset_index()
    #             return dff[["tool_info", "machine", "num_of_rejects"]]
    #         else:
    #             break
    quality_report_input['tool_info'] = quality_report_input['tool_no'] + " " + quality_report_input['tool_name']
    dff = quality_report_input.groupby(["unit", "tool_info"], sort=False)[['num_of_rejects', 'estimated_cost']].sum().reset_index()

    # dff['quality_hours_pk'] = dff['unit'] + "_" + dff['tool_info'] + "_" + dff['machine']

    dff = dff[
        ["unit", "tool_info", "num_of_rejects", "estimated_cost"]]


    return dff

def overall_efficiency_report(total_load_input, daily_report_input, quality_report_input, *args):

    if ((total_load_input.empty) or (daily_report_input.empty) or (quality_report_input.empty)):
        return pd.DataFrame()

    # grouped_daily_df = daily_report_input.groupby(["unit", "tool_no", "tool_name", "insert"], sort=False)[['num_of_hours']].sum().reset_index()
    # print(grouped_daily_df)

    # grouped_total_df = total_load_input.groupby(["unit", "tool_no", "tool_name"], sort=False)[['estimated_hours']].sum().reset_index()
    # print(grouped_total_df)
    # total_load_df = forcast_tool_output(total_load_input)
    quality_report_input = accuarcy_quality_report(quality_report_input)

    # **************^^^^^^^^^^^^^^^^^^^^^^^^^^^*****************************************

    # daily_report_df = daily_report_output(total_load_input, daily_report_input, 'USAGE_EFFICIENCY')
    usage_df = usage_efficiency_report(total_load_input, daily_report_input, 'EFFICIENCY')

    if (usage_df.empty):
        return pd.DataFrame()
    usage_df["overall_efficiency"] = round((usage_df["estimated_hours"] * 100)/ usage_df["num_of_hours"])
    efficiency_with_rejects_df = pd.merge(usage_df, quality_report_input, how='left', on=["unit", "tool_info"])

    efficiency_with_rejects_df["tool_info"] = efficiency_with_rejects_df["unit"] + ', ' + efficiency_with_rejects_df["tool_info"]
    efficiency_with_rejects_df['_ID'] = efficiency_with_rejects_df['tool_info'] + efficiency_with_rejects_df['machine']
    efficiency_with_rejects_df['unique_id'] = pd.factorize(efficiency_with_rejects_df['_ID'])[0]

    pivoted_df = efficiency_with_rejects_df.pivot(index=['unique_id', 'tool_info'], columns='machine', values=["overall_efficiency", "num_of_rejects"]).reset_index()
    pivoted_df.columns.name=None
    pivoted_df = pivoted_df.fillna(0)
    # print("*******************************")
    # print(pivoted_df)
    # print("*******************************")

    return pivoted_df
    # **************^^^^^^^^^^^^^^^^^^^^^^^^^^^*****************************************

    # daily_report = daily_report_output(total_load_input, daily_report_input, 'DAILY_REPORT')
    #
    # if (daily_report.empty):
    #     return pd.DataFrame()
    #
    # daily_report['tool_info'] = daily_report['unit'] + ", " + daily_report['tool_info']
    #
    # # print(daily_report)
    #
    # df_with_estimated_hours = daily_report[["tool_info", "insert", "machine", "estimated_hours"]]
    # df_with_estimated_hours = df_with_estimated_hours.drop_duplicates(subset=["tool_info", "insert", "machine"]).reset_index().copy()
    # grouped_estimated = df_with_estimated_hours.groupby(["tool_info", "machine"], sort=False)[['estimated_hours']].sum().reset_index()
    #
    # df_with_rest = daily_report[["tool_info", "machine", "num_of_hours"]]
    # grouped_ = df_with_rest.groupby(["tool_info", "machine"], sort=False)[['num_of_hours']].sum().reset_index()
    #
    # merged_estimated_daily_df = pd.merge(grouped_estimated, grouped_, how='inner', on=["tool_info", "machine"])
    #
    # merged_estimated_daily_df["balance_hours_as_on_today"] = merged_estimated_daily_df["estimated_hours"] - merged_estimated_daily_df["num_of_hours"]
    #
    # merged_estimated_daily_df = merged_estimated_daily_df.apply(balance_hour_validation, axis=1)
    #
    # if (args):
    #     for str in args:
    #         if str == 'USAGE_EFFICIENCY':
    #             return merged_estimated_daily_df
    #         else:
    #             break
    #
    # if (merged_estimated_daily_df['balance_hours_as_on_today'] == 0).all():
    #     filtered_df = merged_estimated_daily_df
    # else:
    #     return pd.DataFrame()
    #
    # filtered_df = merged_estimated_daily_df
    # # print(grouped_)
    # # filtered_df = daily_report.where(daily_report["balance_hours_as_on_today"] == 0).dropna()
    # grouped_overall_df = filtered_df.groupby(["tool_info", "machine"], sort=False)[['estimated_hours', 'num_of_hours']].sum().reset_index()
    #
    # grouped_overall_df["overall_efficiency"] = round((grouped_overall_df["estimated_hours"] * 100)/ grouped_overall_df["num_of_hours"])
    #
    # quality_report_input["tool_info"] = quality_report_input["unit"] + ', ' + quality_report_input["tool_info"]
    #
    # efficiency_with_rejects_df = pd.merge(grouped_overall_df, quality_report_input, how='left', on=["tool_info"])
    #
    # efficiency_with_rejects_df = efficiency_with_rejects_df[["tool_info", "machine", "overall_efficiency", "num_of_rejects"]]
    #
    # pivoted_df = efficiency_with_rejects_df.pivot_table(index='tool_info', columns='machine', values=["overall_efficiency", "num_of_rejects"]).reset_index()
    # pivoted_df.columns.name=None
    #
    # return pivoted_df

def daily_report_output(total_load_input, daily_report, *args):

    if ((total_load_input.empty) or (daily_report.empty)):
        return pd.DataFrame()

    # Drop duplicates for daily report if it has same unit, tool info, insert, machine, machine_name and daily_date
    daily_report_input = daily_report.drop_duplicates(subset=["unit", "tool_no", "tool_name", "insert", "machine", "machine_name", "daily_date"]).reset_index().copy()

    total_load_on_systems_output = forcast_tool_output(total_load_input)

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
    # daily_date_group_df = daily_date_group_df["daily_date"].max()
    # print("&&&&&&&&*************^^^^^^^^^^^^^^^^^^^^^")
    # print(daily_date_group_df)
    # Output latest daily record for each unit, tool and machine

    daily_date_group_df = daily_date_group_df.rename(columns = {"num_of_hours": "max_date_grouped_daily_hours",
                                                                "daily_date": "max_daily_date"})

    merged_df_with_max_date = pd.merge(daily_date_group_df, tool_hours_group_df, how='inner', left_on=["unit", "tool_info", "machine"], right_on=["unit", "tool_info", "machine"])

    # print(merged_df_with_max_date)
    # Adding minimum date of unit, tool info, machine as start date
    merged_df = pd.merge(daily_date_group_min_df, merged_df_with_max_date, how='inner', left_on=["unit", "tool_info", "machine"], right_on=["unit", "tool_info", "machine"])

    # Merge to add estimated hours to daily report
    merged_df_ = pd.merge(total_load_on_systems_output, merged_df, how='inner', left_on=["unit", "tool_info", "machine"], right_on=["unit", "tool_info", "machine"])

    # print(merged_df_)
    if (args):
        for str_report in args:
            if str_report == 'DAILY_REPORT':
                # print("here")
                # completed_status_df = merged_df_.groupby(["unit", "tool_info", "machine"]).apply(lambda x: (x=='completed'))
                # completed_status_df = merged_df_.groupby(["unit", "tool_info", "machine"]).status.nunique().eq('completed')
                # print(completed_status_df)
                # merged_df_ = merged_df_.groupby(["unit", "tool_info", "machine"]).filter(lambda x: len(x) >= 5)
                return merged_df_
            else:
                break

    if (merged_df_.empty):
        return pd.DataFrame()


    # print(merged_df_)
    merged_df_["balance_hours_as_on_today"] = merged_df_["estimated_hours"] - merged_df_["num_of_hours"]
    merged_df_ = merged_df_.apply(balance_hour_validation, axis=1)
    # print(merged_df_)
    merged_df_ = merged_df_[['unit', 'tool_info', 'machine', 'actual_machine_start_date', 'max_date_grouped_daily_hours', 'max_daily_date', 'balance_hours_as_on_today']]
    # To show the latest date daily report results
    merged_df_ = merged_df_.loc[merged_df_.groupby(['unit', 'tool_info', 'machine']).max_daily_date.idxmax()]
    # print(merged_df_)
    merged_df_["tool_info"] = merged_df_["unit"] + ', ' + merged_df_["tool_info"]
    merged_df_['_ID'] = merged_df_['tool_info'] + merged_df_['machine']
    merged_df_['unique_id'] = pd.factorize(merged_df_['_ID'])[0]
    # print(merged_df_)
    pivoted_df = merged_df_.pivot(index=['unique_id', 'tool_info'], columns='machine', values=["max_date_grouped_daily_hours", "balance_hours_as_on_today", "actual_machine_start_date"]).reset_index()
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
