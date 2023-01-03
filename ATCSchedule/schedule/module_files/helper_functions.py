import pandas as pd
import json
import datetime

# Number of machine models in each machine.
a_dict_unit_1 = {'turning': 2, 'milling': 7, 'edm': 5, 'wire_cut': 6}
a_dict_unit_2 = {'turning': 3, 'milling': 5, 'edm': 2, 'wire_cut': 0}
a_dict_unit_3 = {'turning': 0, 'milling': 0, 'edm': 0, 'wire_cut': 0}
a_dict_unit_4 = {'turning': 2, 'milling': 7, 'edm': 4, 'wire_cut': 4}
UNITS = ['unit 1', 'unit 2', 'unit 3', 'unit 4']


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

    if df.shape[0] > 1:
        df.loc[0, 'actual_start_date'] = df.loc[0, 'insertion_date']
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
    else:
        df["actual_start_date"] = df["insertion_date"]
        return df

    return df

# Calculate forcast date for total load on systems.
def forcast_tool_output(df):
    # print(df.dtypes)
    df = df.applymap(lambda x: x.lower() if type(x) == str else x)

    df['tool_info'] = df['tool_no'] + " " + df['tool_name']

    df['estimated_hours'] = df['estimated_hours'].fillna(0)
    df['buffer_hours'] = df['buffer_hours'].fillna(df['estimated_hours'])

    # Buffer hours wiil be in percentage converting percentage to values
    df['buffer_hours'] = df['estimated_hours'] + (df['estimated_hours']/df['buffer_hours'])

    # print(df)
    df = df.groupby(["unit", "tool_info", "machine", "insertion_date"], sort=False)[['estimated_hours', 'buffer_hours']].sum().reset_index()

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
    df_lst = [cal_dates(x) for _, x in df.groupby('unit')]

    # Concatenating dataframs and removing nan values when primary key is nan
    concat_df = pd.concat(df_lst, axis=0)
    concat_df = concat_df.dropna(subset=["total_load_pk"])

    # To indentify the Sat and Sun
    concat_df["Weekend"] = concat_df["actual_start_date"].dt.weekday

    concat_df['completion_date_with_out_buffer'] = concat_df['actual_start_date'] + pd.to_timedelta(df['total_actual_days'], unit='D')
    # Considering Monday if the date is Sunday
    concat_df['completion_date_with_out_buffer'] = concat_df['completion_date_with_out_buffer'].transform(lambda row : check_weekend(row))

    concat_df['completion_date_with_buffer'] = concat_df['actual_start_date'] + pd.to_timedelta(df['total_actual_days_with_buffer'], unit='D')
    # Considering Monday if the date is Sunday
    concat_df['completion_date_with_buffer'] = concat_df['completion_date_with_buffer'].transform(lambda row : check_weekend(row))

    return concat_df
    # total_load_on_systems_df = df[
    #     ["tool_info", "completion_date_with_out_buffer", "completion_date_with_buffer", "insertion_date"]]
    #
    # return total_load_on_systems_df.iloc[::5, :]

# Replace with above function in views.py
def total_load_on_systems_output(total_load_on_systems_input):

    total_load_on_systems_output = forcast_tool_output(total_load_on_systems_input)

    actual_start_date_df = total_load_on_systems_output[['tool_info', 'actual_start_date']].drop_duplicates(subset = ['tool_info'])

    total_load_on_systems_output = total_load_on_systems_output[
        ["tool_info", "completion_date_with_out_buffer", "completion_date_with_buffer"]]

    # End logic to give the max date of machine tools.
    total_load_on_systems_output = total_load_on_systems_output[total_load_on_systems_output.groupby('tool_info').completion_date_with_out_buffer.transform('max') == total_load_on_systems_output['completion_date_with_out_buffer']]

    total_load_on_systems_output = pd.merge(total_load_on_systems_output,actual_start_date_df,on=['tool_info'],how='inner')
    return total_load_on_systems_output

def daily_report_output(total_load_input, daily_report_input, *args):

    # Convert input to lower case
    daily_report_input = daily_report_input.applymap(lambda x: x.lower() if type(x) == 'str' else x)

    # daily_hours_df['tool_info'] = daily_hours_df['tool_no'] + daily_hours_df['tool_name']
    daily_report_input.melt(id_vars=["unit", "tool_no", "tool_name", "insert", "num_of_hours", "daily_date"],
        var_name="machine",
        value_name="accuracy")

    daily_report_input['tool_info'] = daily_report_input['tool_no'] + " " + daily_report_input['tool_name']
    dff = daily_report_input.groupby(["unit", "tool_info", "machine", "insert"], sort=False).num_of_hours.sum().reset_index()

    # replace insert add date with inserts
    dff['daily_hours_pk'] = dff['unit'] + "_" + dff['tool_info'] + "_" + dff['machine']

    total_load_df = forcast_tool_output(total_load_input)

    total_load_df = total_load_df[
        ["total_load_pk", "completion_date_with_out_buffer", "estimated_hours", "capacity_day", "buffer_hours"]]

    combined_df = pd.merge(total_load_df, dff, how='inner', left_on="total_load_pk", right_on="daily_hours_pk")

    combined_df["daily_hours_diff"] = combined_df["capacity_day"] - combined_df["num_of_hours"]

    combined_df["daily_hours_diff_in_days"] = round(combined_df["daily_hours_diff"] / combined_df["capacity_day"])

    # combined_df = combined_df.groupby('tool_info').agg({'daily_hours_diff': 'sum', 'completion_date_with_out_buffer': 'first', 'estimated_hours': 'first'})

    combined_df['completion_date_with_out_buffer'] = combined_df['completion_date_with_out_buffer'] + pd.to_timedelta(combined_df['daily_hours_diff_in_days'], unit='D')

    if (args):
        for str in args:
            if str == 'OVERALL_EFFICIENCY':
                return combined_df[["daily_hours_pk", "tool_info", "machine", "daily_hours_diff_in_days"]]
            else:
                break

    combined_df = combined_df[
        ["tool_info", "machine", "completion_date_with_out_buffer", "estimated_hours", "num_of_hours"]]

    pivoted_df = combined_df.pivot(index='tool_info', columns='machine', values=["completion_date_with_out_buffer", "estimated_hours", "num_of_hours"]).reset_index()
    pivoted_df.columns.name=None
    pivoted_df = pivoted_df.fillna(0)

    # print(pivoted_df)
    return pivoted_df

def accuarcy_quality_report(quality_report_input, *args):

    # Convert input to lower case
    quality_report_input = quality_report_input.applymap(lambda x: x.lower() if type(x) == str else x)
    quality_report_input = quality_report_input.drop('id', axis=1)
    quality_report_input = quality_report_input.melt(id_vars=["unit", "tool_no", "tool_name", "insert", "num_of_rejects", "insertion_date"],
        var_name="machine",
        value_name="accuracy")

    quality_report_input['accuracy'] = quality_report_input['accuracy'].astype(str).astype(int)

    quality_report_input['tool_info'] = quality_report_input['tool_no'] + " " + quality_report_input['tool_name']
    quality_report_input['estimated_cost'] = quality_report_input['num_of_rejects'] * 2000

    if (args):
        for str_arg in args:
            if str_arg == 'QUALITY_REPORT':
                dff = quality_report_input.groupby(["unit", "tool_info", "machine"], sort=False)[['accuracy', 'num_of_rejects', 'estimated_cost']].sum().reset_index()
                return dff[["tool_info", "machine", "accuracy", "num_of_rejects", "estimated_cost"]]
            else:
                break
    dff = quality_report_input.groupby(["unit", "tool_info"], sort=False)[['accuracy', 'num_of_rejects', 'estimated_cost']].sum().reset_index()

    # dff['quality_hours_pk'] = dff['unit'] + "_" + dff['tool_info'] + "_" + dff['machine']

    dff = dff[
        ["tool_info", "accuracy", "num_of_rejects", "estimated_cost"]]


    return dff

def overall_efficiency_report(total_load_input, daily_report_input, quality_report_input):

    total_load_df = forcast_tool_output(total_load_input)
    daily_report_df = daily_report_output(total_load_input, daily_report_input, 'OVERALL_EFFICIENCY')
    quality_report_input = accuarcy_quality_report(quality_report_input, 'QUALITY_REPORT')

    total_load_df["overall_total_load_pk"] = total_load_df['unit'] + '_' + total_load_df['tool_info'] + '_' + total_load_df['machine']
    total_load_df = total_load_df[["overall_total_load_pk", "total_actual_days"]]

    combined_df = pd.merge(total_load_df, daily_report_df, how='inner', left_on="overall_total_load_pk", right_on="daily_hours_pk")

    combined_df["daily_hours_diff_in_days"] = combined_df["daily_hours_diff_in_days"].abs()
    combined_df["daily_total_diff_days"] = combined_df["total_actual_days"] - combined_df["daily_hours_diff_in_days"]

    combined_df["overall_efficiency"] = round((combined_df["total_actual_days"] / combined_df["daily_total_diff_days"]) * 100)

    required_combined_df = combined_df[["tool_info", "machine", "overall_efficiency"]]

    # print(quality_report_input)
    accuracy_df = quality_report_input[["tool_info", "machine", "num_of_rejects"]]
    efficiency_with_rejects_df = pd.merge(required_combined_df, accuracy_df, how='inner', on=["tool_info", "machine"])

    efficiency_with_rejects_df = efficiency_with_rejects_df[["tool_info", "machine", "overall_efficiency", "num_of_rejects"]]

    pivoted_df = efficiency_with_rejects_df.pivot_table(index='tool_info', columns='machine', values=["overall_efficiency", "num_of_rejects"]).reset_index()
    pivoted_df.columns.name=None
    # print(efficiency_with_rejects_df)
    return pivoted_df

def usage_efficiency_report(total_load_input, daily_report_input):

    # Convert input to lower case
    total_load_input = total_load_input.applymap(lambda x: x.lower() if type(x) == str else x)

    # Convert input to lower case
    daily_report_input = daily_report_input.applymap(lambda x: x.lower() if type(x) == str else x)

    total_load_input = total_load_input[["unit", "tool_no", "tool_name", "machine", "estimated_hours", "buffer_hours"]]
    total_load_input['estimated_hours'] = total_load_input['estimated_hours'].fillna(0)
    total_load_input['buffer_hours'] = total_load_input['buffer_hours'].fillna(total_load_input['estimated_hours'])
    # Buffer hours wiil be in percentage converting percentage to values
    total_load_input['buffer_hours'] = total_load_input['estimated_hours'] + (total_load_input['estimated_hours']/total_load_input['buffer_hours'])
    total_load_input['tool_info'] = total_load_input['tool_no'] + " " + total_load_input['tool_name']

    total_load_df = total_load_input.groupby(["unit", "tool_info", "machine"], sort=False)[['estimated_hours', 'buffer_hours']].sum().reset_index()

    total_load_df['total_load_pk'] = total_load_df['unit'] + '_' + total_load_df['tool_info'] + '_' + total_load_df['machine']


    daily_report_input = daily_report_input[["unit", "tool_no", "tool_name", "machine", "num_of_hours", "daily_date"]]
    daily_report_input['tool_info'] = daily_report_input['tool_no'] + " " + daily_report_input['tool_name']

    daily_report_df = daily_report_input.groupby(["unit", "tool_info", "machine", "daily_date"], sort=False).num_of_hours.sum().reset_index()

    daily_report_df['daily_hours_pk'] = daily_report_df['unit'] + '_' + daily_report_df['tool_info'] + '_' + daily_report_df['machine']


    total_load_df = total_load_df[["total_load_pk", "estimated_hours", "buffer_hours"]]
    daily_report_df = daily_report_df[["daily_hours_pk", "tool_info", "machine", "num_of_hours"]]
    combined_df = pd.merge(total_load_df, daily_report_df, how='inner', left_on="total_load_pk", right_on="daily_hours_pk")

    combined_df["balance_hours_as_on_today"] = combined_df["estimated_hours"] - combined_df["num_of_hours"]

    pivoted_df = combined_df.pivot_table(index='tool_info', columns='machine', values=["balance_hours_as_on_today", "estimated_hours", "num_of_hours", "buffer_hours"]).reset_index()
    pivoted_df.columns.name=None

    return pivoted_df
