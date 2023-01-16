import pandas as pd
import json
import datetime

# Number of machine models in each machine.
a_dict_unit_1 = {'turning': 2, 'milling': 8, 'edm': 5, 'wire_cut': 6}
a_dict_unit_2 = {'turning': 3, 'milling': 5, 'edm': 2, 'wire_cut': 0}
a_dict_unit_3 = {'turning': 0, 'milling': 0, 'edm': 0, 'wire_cut': 0}
a_dict_unit_4 = {'turning': 2, 'milling': 7, 'edm': 4, 'wire_cut': 4}
UNITS = ['unit 1', 'unit 2', 'unit 3', 'unit 4']


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
    # if (!(df)) {
    #     return pd.DataFrame()
    # }
    df = df.drop_duplicates(['unit', "tool_no", "tool_name", "machine", "insert"])

    # order = ['turning','milling','edm','wire_cut']
    order = ['wire_cut', 'edm', 'milling', 'turning']
    df['machine'] = pd.Categorical(df['machine'], order, ordered = True)
    df = df[::-1]                             # Reverse order of rows

    df["tool_name"] = df['tool_name'].str.lower()
    df["insert"] = df['insert'].str.lower()
    df = df.applymap(lambda x: x.lower() if type(x) == str else x)

    df['tool_info'] = df['tool_no'] + " " + df['tool_name']

    df['estimated_hours'] = df['estimated_hours'].fillna(0)
    df['estimated_hours'] = df['estimated_hours'] * df['num_of_inserts']
    df['buffer_hours'] = df['buffer_hours'].fillna(df['estimated_hours'])

    # Buffer hours wiil be in percentage converting percentage to values
    df['buffer_hours'] = df['estimated_hours'] + ((df['estimated_hours']*df['buffer_hours'])/100)

    df = df.groupby(["unit", "tool_info", "machine", "insertion_date", "insert"], sort=False)[['estimated_hours', 'buffer_hours']].sum().reset_index()

    # Creating a primary key for total load on systems table (1st table)
    df['total_load_pk'] = df['unit'] + '_' + df['tool_info'] + '_' + df['machine']

    # convert insert_add_dt to DateTime format
    df['insertion_date'] = pd.to_datetime(df['insertion_date'], format='%Y-%m-%d')

    # return_unit_capacity function returns capacity value.
    df["capacity_day"] = df.apply(lambda x: return_unit_capacity(x['unit'], x['machine']), axis = 1)

    # Total actual days
    df['total_actual_days'] = round(df['estimated_hours'] / df['capacity_day'])

    # Total actual days with buffer time
    df['total_actual_days_with_buffer'] = round(df['buffer_hours'] / df['capacity_day'])

    # Calculate actual dates based on unit and add them to list
    #df_lst = [cal_dates(x) for _, x in df.groupby('unit')]
    df_lst = []
    for _,x in df.groupby('unit'):
        x = x.reset_index()
        del x['index']
        df_lst.append(cal_dates(x))

    # Concatenating dataframs and removing nan values when primary key is nan
    concat_df = pd.concat(df_lst, axis=0)
    # print(concat_df)
    concat_df = concat_df.dropna(subset=["total_load_pk"])
    # To indentify the Sat and Sun
    concat_df["Weekend"] = concat_df["actual_start_date"].dt.weekday
    concat_df = concat_df.reset_index()
    del concat_df['index']
    concat_df['completion_date_with_out_buffer'] = concat_df['actual_start_date'] + pd.to_timedelta(df['total_actual_days'], unit='D')
    # Considering Monday if the date is Sunday
    concat_df['completion_date_with_out_buffer'] = concat_df['completion_date_with_out_buffer'].transform(lambda row : check_weekend(row))

    # concatenating the columns
    # concat_df['completion_date_with_out_buffer'] = concat_df['completion_date_with_out_buffer'] + "(" + concat_df['week_number'] + ")"

    concat_df['completion_date_with_buffer'] = concat_df['actual_start_date'] + pd.to_timedelta(df['total_actual_days_with_buffer'], unit='D')
    # Considering Monday if the date is Sunday
    concat_df['completion_date_with_buffer'] = concat_df['completion_date_with_buffer'].transform(lambda row : check_weekend(row))

    # print(concat_df)
    return concat_df
    # total_load_on_systems_df = df[
    #     ["tool_info", "completion_date_with_out_buffer", "completion_date_with_buffer", "insertion_date"]]
    #
    # return total_load_on_systems_df.iloc[::5, :]

# Replace with above function in views.py
def total_load_on_systems_output(total_load_on_systems_input):
    isempty = total_load_on_systems_input.empty
    if (isempty):
        return pd.DataFrame()

    total_load_on_systems_output = forcast_tool_output(total_load_on_systems_input)

    actual_start_date_df = total_load_on_systems_output[['tool_info', 'actual_start_date']].drop_duplicates(subset = ['tool_info'])

    total_load_on_systems_output = total_load_on_systems_output[
        ["unit", "tool_info", "completion_date_with_out_buffer", "completion_date_with_buffer"]]


    total_load_on_systems_output = total_load_on_systems_output.loc[total_load_on_systems_output.groupby('tool_info').completion_date_with_out_buffer.idxmax()]
    # End logic to give the max date of machine tools.
    # total_load_on_systems_output = total_load_on_systems_output[total_load_on_systems_output.groupby('tool_info').completion_date_with_out_buffer.transform('max') == total_load_on_systems_output['completion_date_with_out_buffer']]

    merged_df = pd.merge(total_load_on_systems_output,actual_start_date_df,on=['tool_info'],how='inner')

    merged_df['completion_date_with_out_buffer_week'] = merged_df['completion_date_with_out_buffer'].dt.isocalendar().week
    merged_df['completion_date_with_buffer_week'] = merged_df['completion_date_with_out_buffer'].dt.isocalendar().week

    return merged_df

def usage_efficiency_report(total_load_input, daily_report_input, quality_report_input, *args):
    
    if ((total_load_input.empty) or (daily_report_input.empty)):
        return pd.DataFrame()

     # ---------------------------------------------88**********************_-------------------------------------------------------------
    # Estimated
    total_df = forcast_tool_output(total_load_input)
    total_df = total_df[["unit", "tool_info", "insert", "machine", "completion_date_with_out_buffer"]]
    total_df["tool_info"] = total_df["unit"] + ', ' + total_df["tool_info"]
    total_df = total_df.loc[total_df.groupby(['tool_info', 'machine']).completion_date_with_out_buffer.idxmax()].reset_index()

    # Efficinecy
    efficiency_df = overall_efficiency_report(total_load_input, daily_report_input, quality_report_input, 'USAGE_EFFICIENCY')
    print(efficiency_df)

    merged_df = pd.merge(total_df, efficiency_df, how='inner', left_on=["tool_info", "machine"], right_on=["tool_info", "machine"])

    if (merged_df.empty):
        return pd.DataFrame()
    grouped_overall_df = merged_df.groupby(["tool_info", "machine"], sort=False)[['estimated_hours', 'num_of_hours']].sum().reset_index()

    # print(merged_df)
    merged_df["capacity_day"] = merged_df.apply(lambda x: return_unit_capacity(x['unit'], x['machine']), axis = 1)

    # merged_df["daily_hours_diff"] = merged_df["capacity_day"] - merged_df["num_of_hours"]
    # merged_df["cap_value"] = round(merged_df["num_of_hours"] / merged_df["capacity_day"])

    print(merged_df)
    merged_df = merged_df.apply(cap_value_validation, axis=1)
    merged_df['completion_date_with_out_buffer'] = merged_df['completion_date_with_out_buffer'] + pd.to_timedelta(merged_df['cap_value'], unit='D')

    print("KKkKKKK))))))))))))))))))))))))))))))***********")
    print(merged_df)

    pivoted_df = merged_df.pivot(index='tool_info', columns='machine', values=["completion_date_with_out_buffer", "estimated_hours", "num_of_hours"]).reset_index()
    pivoted_df.columns.name=None

    pivoted_df = pivoted_df.fillna(0)
    # print(pivoted_df)
    return pivoted_df

    # ---------------------------------------------88**********************_-------------------------------------------------------------

    daily_df = daily_report_output(total_load_input, daily_report_input, 'DAILY_REPORT')
    if (not(daily_df.empty)):
        grouped_daily_df = daily_df.groupby(["unit", "tool_info", "machine", "insert"], sort=False)[['estimated_hours', 'num_of_hours']].sum().reset_index()
    else:
        grouped_daily_df = pd.Dataframe()

    # Estimated
    total_df = forcast_tool_output(total_load_input)
    total_df = total_df[["unit", "tool_info", "insert", "machine", "completion_date_with_out_buffer"]]
    total_df["tool_info"] = total_df["unit"] + ', ' + total_df["tool_info"]
    # print(total_df)
    # total_df = total_df.loc[total_df.groupby('tool_info').completion_date_with_out_buffer.idxmax()]

    # Daily Report
    grouped_daily_df["tool_info"] = grouped_daily_df["unit"] + ', ' + grouped_daily_df["tool_info"]

    merged_df = pd.merge(total_df, grouped_daily_df, how='inner', left_on=["tool_info", "insert", "machine"], right_on=["tool_info", "insert", "machine"])

    if (merged_df.empty):
        return pd.DataFrame()
    # print(merged_df)
    merged_df["capacity_day"] = merged_df.apply(lambda x: return_unit_capacity(x['unit_x'], x['machine']), axis = 1)

    # merged_df["daily_hours_diff"] = merged_df["capacity_day"] - merged_df["num_of_hours"]
    merged_df["cap_value"] = round(merged_df["num_of_hours"] / merged_df["capacity_day"])

    merged_df['completion_date_with_out_buffer'] = merged_df['completion_date_with_out_buffer'] + pd.to_timedelta(merged_df['cap_value'], unit='D')

    if (args):
        for str in args:
            if str == 'OVERALL_EFFICIENCY':
                return merged_df[["tool_info", "machine", "estimated_hours", "num_of_hours"]]
            else:
                break
    
    merged_df['tool_info'] = merged_df['tool_info'] + '_' + merged_df['insert'] + '_' + merged_df['machine']
    merged_df = merged_df[
        ["tool_info", "machine", "completion_date_with_out_buffer", "estimated_hours", "num_of_hours"]]

    merged_df = merged_df.groupby('completion_date_with_out_buffer').max()

    # print(merged_df)
    pivoted_df = merged_df.pivot(index='tool_info', columns='machine', values=["completion_date_with_out_buffer", "estimated_hours", "num_of_hours"]).reset_index()
    pivoted_df.columns.name=None

    # To remove the null values
    pivoted_df = pivoted_df.fillna(0)
    # print(pivoted_df)
    return pivoted_df
    # return pivoted_df

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
    total_load_df = forcast_tool_output(total_load_input)
    # daily_report_df = usage_efficiency_report(total_load_input, daily_report_input, 'OVERALL_EFFICIENCY')
    quality_report_input = accuarcy_quality_report(quality_report_input)

    daily_report = daily_report_output(total_load_input, daily_report_input, 'DAILY_REPORT')

    daily_report['tool_info'] = daily_report['unit'] + ", " + daily_report['tool_info']

    # print(daily_report)

    df_with_estimated_hours = daily_report[["tool_info", "insert", "machine", "estimated_hours"]]
    df_with_estimated_hours = df_with_estimated_hours.drop_duplicates(subset=["tool_info", "insert", "machine"]).reset_index().copy()
    grouped_estimated = df_with_estimated_hours.groupby(["tool_info", "machine"], sort=False)[['estimated_hours']].sum().reset_index()

    df_with_rest = daily_report[["tool_info", "machine", "num_of_hours"]]
    grouped_ = df_with_rest.groupby(["tool_info", "machine"], sort=False)[['num_of_hours']].sum().reset_index()

    merged_estimated_daily_df = pd.merge(grouped_estimated, grouped_, how='inner', on=["tool_info", "machine"])

    merged_estimated_daily_df["balance_hours_as_on_today"] = merged_estimated_daily_df["estimated_hours"] - merged_estimated_daily_df["num_of_hours"]

    merged_estimated_daily_df = merged_estimated_daily_df.apply(balance_hour_validation, axis=1)

    if (args):
        for str in args:
            if str == 'USAGE_EFFICIENCY':
                return merged_estimated_daily_df
            else:
                break

    if (merged_estimated_daily_df['balance_hours_as_on_today'] == 0).all():
        filtered_df = merged_estimated_daily_df
    else:
        return pd.DataFrame()

    filtered_df = merged_estimated_daily_df
    # print(grouped_)
    # filtered_df = daily_report.where(daily_report["balance_hours_as_on_today"] == 0).dropna()
    grouped_overall_df = filtered_df.groupby(["tool_info", "machine"], sort=False)[['estimated_hours', 'num_of_hours']].sum().reset_index()

    grouped_overall_df["overall_efficiency"] = round((grouped_overall_df["estimated_hours"] * 100)/ grouped_overall_df["num_of_hours"])

    quality_report_input["tool_info"] = quality_report_input["unit"] + ', ' + quality_report_input["tool_info"]

    efficiency_with_rejects_df = pd.merge(grouped_overall_df, quality_report_input, how='left', on=["tool_info"])

    efficiency_with_rejects_df = efficiency_with_rejects_df[["tool_info", "machine", "overall_efficiency", "num_of_rejects"]]

    pivoted_df = efficiency_with_rejects_df.pivot_table(index='tool_info', columns='machine', values=["overall_efficiency", "num_of_rejects"]).reset_index()
    pivoted_df.columns.name=None

    return pivoted_df

def daily_report_output(total_load_input, daily_report, *args):

    if ((total_load_input.empty) or (daily_report.empty)):
        return pd.DataFrame()

    # Drop duplicates for daily report if it has same unit, tool info, insert, machine, machine_name and daily_date    
    daily_report_input = daily_report.drop_duplicates(subset=["unit", "tool_no", "tool_name", "insert", "machine", "machine_name", "daily_date"]).reset_index().copy()
    
    total_load_on_systems_output = forcast_tool_output(total_load_input)
    total_load_on_systems_output = total_load_on_systems_output[["total_load_pk", "insert", "estimated_hours", "buffer_hours", "capacity_day"]]
    # Convert input to lower case
    daily_report_input["insert"] = daily_report_input['insert'].str.lower()
    daily_report_input["tool_name"] = daily_report_input['tool_name'].str.lower()
    daily_report_input["machine_name"] = daily_report_input['machine_name'].str.lower()
    daily_report_input = daily_report_input.applymap(lambda x: x.lower() if type(x) == str else x)

    # daily_report_input = daily_report_input[["unit", "tool_no", "tool_name", "insert", "machine", "num_of_hours", "daily_date"]]
    daily_report_input['tool_info'] = daily_report_input['tool_no'] + " " + daily_report_input['tool_name']

    daily_report_df = daily_report_input.groupby(["unit", "tool_info", "insert", "machine", "daily_date"], sort=False).num_of_hours.sum().reset_index()

    daily_report_df['daily_hours_pk'] = daily_report_df['unit'] + '_' + daily_report_df['tool_info'] + '_' + daily_report_df['machine']

    # Included unit, insert, daily date
    daily_report_df = daily_report_df[["unit", "daily_hours_pk", "tool_info", "insert", "machine", "num_of_hours", "daily_date"]]

    combined_df = pd.merge(total_load_on_systems_output, daily_report_df, how='inner', left_on=["total_load_pk", "insert"], right_on=["daily_hours_pk", "insert"])
    
    if (combined_df.empty):
        return pd.DataFrame()
    
    grouped_df = combined_df.groupby(["unit", "tool_info", "insert", "machine", "daily_date"], sort=False)[['estimated_hours', 'buffer_hours', 'num_of_hours']].sum().reset_index()
    
    grouped_df["balance_hours_as_on_today"] = grouped_df["estimated_hours"] - grouped_df["num_of_hours"]
    
    # grouped_with_out_insert = combined_df.groupby(["unit", "tool_info", "machine", "daily_date"], sort=False)[['estimated_hours', 'buffer_hours']].sum().reset_index()
    # print(grouped_with_out_insert)
    # result_df_1 = cal_expected_hours_as_on_today(grouped_with_out_insert)
    # print(result_df_1)
    result_df = cal_expected_hours_as_on_today(grouped_df)

    # print(result_df)
    # TO remove the decimals
    result_df['expected_hours_as_on_today'] = result_df['expected_hours_as_on_today'].astype(int)
    result_df['expected_hours_as_on_today_with_buffer'] = result_df['expected_hours_as_on_today_with_buffer'].astype(int)

    result_df = result_df.apply(add_progress_to_expected_hours, axis=1)

    if (args):
        for str_arg in args:
            print()
            if str_arg == 'DAILY_REPORT':
                return result_df
            else:
                break
    result_df["tool_info"] = result_df["unit"] + ', ' + result_df["tool_info"] + ', ' + result_df["insert"]

    # To get the latest date
    latest_date = max(result_df['daily_date'])
    # Output latest daily record for each unit, tool and machine
    result_df = result_df.loc[(result_df['daily_date'] == latest_date)]

    pivoted_df = result_df.pivot(index=['tool_info', 'insert', 'daily_date'], columns='machine', values=["num_of_hours", "balance_hours_as_on_today", "expected_hours_as_on_today", "expected_hours_as_on_today_with_buffer"]).reset_index()
    pivoted_df.columns.name=None

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
    
