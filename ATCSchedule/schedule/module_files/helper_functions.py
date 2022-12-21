import pandas as pd
import json
import datetime

a_dict = {'turning': 64, 'milling': 168, 'edm': 96, 'wire_cut': 96}
# Helper function to check Sunday and get Monday date
def check_weekend(date):
    if date.weekday() == 6:
        return date + pd.Timedelta(days=1)
    else:
        return date

# Calculate forcast date for total load on systems.
def forcast_tool_output(df):
    df['tool_info'] = df['tool_no'] + " " + df['tool_name']
    
    df['estimated_hours'] = df['estimated_hours'].fillna(0)
    df['buffer_hours'] = df['buffer_hours'].fillna(df['estimated_hours'])

    # Buffer hours wiil be in percentage converting percentage to values
    # df['buffer_hours'] = df['estimated_hours'] + ( (df['estimated_hours']/df['buffer_hours']) * 100)

    # print(df)
    df = df.groupby(["unit", "tool_info", "machine", "insertion_date"], sort=False)[['estimated_hours', 'buffer_hours']].sum().reset_index()

    # Creating a primary key for total load on systems table (1st table)
    df['total_load_pk'] = df['unit'] + '_' + df['tool_info'] + '_' + df['machine']

    # convert insert_add_dt to DateTime format
    df['insertion_date'] = pd.to_datetime(df['insertion_date'], format='%Y-%m-%d')

    # Can be removed once we add this column to table
    df["capacity_day"] = df["machine"].apply(lambda x: a_dict.get(x))

    # print(df)
    # Total actual days
    df['total_actual_days'] = round(df['estimated_hours'] / df['capacity_day'])

    # Total actual days with buffer time
    df['total_actual_days_with_buffer'] = round(df['buffer_hours'] / df['capacity_day'])

    # Calculating forcast end date
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

    # To indentify the Sat and Sun
    df["Weekend"] = df["actual_start_date"].dt.weekday

    df['completion_date_with_out_buffer'] = df['actual_start_date'] + pd.to_timedelta(df['total_actual_days'], unit='D')
    # Considering Monday if the date is Sunday
    df['completion_date_with_out_buffer'] = df['completion_date_with_out_buffer'].transform(lambda row : check_weekend(row))

    df['completion_date_with_buffer'] = df['actual_start_date'] + pd.to_timedelta(df['total_actual_days_with_buffer'], unit='D')
    # Considering Monday if the date is Sunday
    df['completion_date_with_buffer'] = df['completion_date_with_buffer'].transform(lambda row : check_weekend(row))

    return df
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

def daily_report_output(total_load_input, daily_report_input):
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
        ["total_load_pk", "completion_date_with_out_buffer", "estimated_hours", "capacity_day"]]

    combined_df = pd.merge(total_load_df, dff, how='right', left_on="total_load_pk", right_on="daily_hours_pk")

    combined_df["daily_hours_diff"] = combined_df["capacity_day"] - combined_df["num_of_hours"]

    combined_df["daily_hours_diff_in_days"] = round(combined_df["daily_hours_diff"] / combined_df["capacity_day"])
    
    # combined_df = combined_df.groupby('tool_info').agg({'daily_hours_diff': 'sum', 'completion_date_with_out_buffer': 'first', 'estimated_hours': 'first'})

    combined_df['completion_date_with_out_buffer'] = combined_df['completion_date_with_out_buffer'] + pd.to_timedelta(combined_df['daily_hours_diff_in_days'], unit='D')

    combined_df = combined_df[
        ["tool_info", "machine", "completion_date_with_out_buffer", "estimated_hours", "num_of_hours"]]

    return combined_df

def accuarcy_quality_report(quality_report_input):

    quality_report_input = quality_report_input.drop('id', axis=1)
    quality_report_input = quality_report_input.melt(id_vars=["unit", "tool_no", "tool_name", "insert", "num_of_rejects", "insertion_date"], 
        var_name="machine", 
        value_name="accuracy")

    quality_report_input['accuracy'] = quality_report_input['accuracy'].astype(str).astype(int)

    quality_report_input['tool_info'] = quality_report_input['tool_no'] + "_" + quality_report_input['tool_name']
    quality_report_input['estimated_cost'] = quality_report_input['num_of_rejects'] * 1000
    dff = quality_report_input.groupby(["unit", "tool_info", "machine"], sort=False)[['accuracy', 'num_of_rejects', 'estimated_cost']].sum().reset_index()

    # dff['quality_hours_pk'] = dff['unit'] + "_" + dff['tool_info'] + "_" + dff['machine']

    dff = dff[
        ["tool_info", "machine", "accuracy", "num_of_rejects", "estimated_cost"]]

    return dff

def overall_efficiency_report(total_load_input, df1, df2):

    # total_load_df = forcast_tool_output(total_load_input)
    # df1 = daily_report_output(total_load_df, df1)
    df2 = accuarcy_quality_report(df2)

    # forcast_tool_output = total_load_on_systems_output[
    #     ["tool_info", "completion_date_with_out_buffer", "completion_date_with_buffer"]]

    # quality_report_input = quality_report_input.drop('id', axis=1)
    # quality_report_input = quality_report_input.melt(id_vars=["unit", "tool_no", "tool_name", "insert", "num_of_rejects", "insertion_date"], 
    #     var_name="machine", 
    #     value_name="accuracy")

    # quality_report_input['accuracy'] = quality_report_input['accuracy'].astype(str).astype(int)

    # quality_report_input['tool_info'] = quality_report_input['tool_no'] + "_" + quality_report_input['tool_name']
    # quality_report_input['estimated_cost'] = quality_report_input['num_of_rejects'] * 1000
    # dff = quality_report_input.groupby(["unit", "tool_info", "machine"], sort=False)[['accuracy', 'num_of_rejects', 'estimated_cost']].sum().reset_index()

    # print(dff)
    # # dff['quality_hours_pk'] = dff['unit'] + "_" + dff['tool_info'] + "_" + dff['machine']

    # dff = dff[
    #     ["tool_info", "machine", "accuracy", "num_of_rejects", "estimated_cost"]]

    return df2

def usage_efficiency_report(df, df1, df2):

    # df = forcast_tool_output(df)
    # df1 = daily_report_output(df, df1)
    # df2 = accuarcy_quality_report(df2)

    # forcast_tool_output = total_load_on_systems_output[
    #     ["tool_info", "completion_date_with_out_buffer", "completion_date_with_buffer"]]


    return df