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

    df = df.groupby(["department", "tool_info", "machines", "insertion_date"], sort=False)[['estimated_hours', 'buffer_hours']].sum().reset_index()

    print(df)
    # Creating a primary key for total load on systems table (1st table)
    df['total_load_pk'] = df['department'] + df['tool_info'] + df['machines']

    # convert insert_add_dt to DateTime format
    df['insertion_date'] = pd.to_datetime(df['insertion_date'], format='%Y-%m-%d')

    # Can be removed once we add this column to table
    df["capacity_day"] = df["machines"].apply(lambda x: a_dict.get(x))

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

    print(df['actual_start_date'])
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
    # End logic to give the max date of machine tools.
    total_load_on_systems_output = total_load_on_systems_output[
        ["tool_info", "completion_date_with_out_buffer", "completion_date_with_buffer"]]

    # print(total_load_on_systems_output)

    total_load_on_systems_output = total_load_on_systems_output[total_load_on_systems_output.groupby('tool_info').completion_date_with_out_buffer.transform('max') == total_load_on_systems_output['completion_date_with_out_buffer']]

    total_load_on_systems_output = pd.merge(total_load_on_systems_output,actual_start_date_df,on=['tool_info'],how='inner')
    return total_load_on_systems_output

def daily_report_output(total_load_input, daily_report_input):
    # daily_hours_df['tool_info'] = daily_hours_df['tool_no'] + daily_hours_df['tool_name']
    daily_report_input['tool_info'] = daily_report_input['tool_no'] + " " + daily_report_input['tool_name']
    dff = daily_report_input.groupby(["department", "tool_info", "machines", "insert"]).num_of_hours.sum().reset_index()

    # ADD '_' to total machine hours table to primary key
    # replace insert add date with inserts
    dff['daily_hours_pk'] = dff['department'] + "_" + dff['tool_info'] + \
            "_" + dff['insert'] + "_" + dff['machines']

    total_load_df = forcast_tool_output(total_load_input)

    total_load_df = total_load_df[
        ["total_load_pk", "completion_date_with_out_buffer", "estimated_hours", "total_actual_days"]]


    # convert days in to hours in total_load_df
    total_load_df["total_actual_days_in_hours"] = total_load_df["total_actual_days"].mul(24)

    new_df = pd.merge(total_load_df, dff, how='right', left_on="total_load_pk", right_on="daily_hours_pk")

    print(new_df)

    # add num of hours to total number of hours

    # convert to days and add them to completion date.

    # return estimated hours, num of hours, date aas output

    return daily_report_input
