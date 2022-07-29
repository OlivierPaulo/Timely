from atlassian import Jira
import os
import pandas as pd
from datetime import datetime
import calendar
import datetime as dt

THM = float(os.environ['NOS_THM'])
HOURS_PER_DAY_CONTRACT = float(os.environ['NOS_HRS_PER_DAY_CONTRACT'])


def get_Jira_instance() -> Jira:
    return Jira(
        url=os.environ['JIRA_URL'],
        username=os.environ['JIRA_USER'],
        password=os.environ['JIRA_PWD'],
    )


def get_timetracks(first_day: str, last_day: str, username: str, jira_instance: Jira) -> pd.DataFrame:
    results_dict = jira_instance.jql(f"worklogDate >= '{first_day}' AND worklogDate <= '{last_day}' AND worklogAuthor in ('{username}')")
    timetracks = pd.DataFrame()
    task_names = []
    task_date = []
    task_timeSpent = []

    for task in results_dict['issues']:
        for worklog in task['fields']['worklog']['worklogs']:
            task_names.append(f"[NOS] [{task['key']}] {task['fields']['summary']}")
            task_date.append(worklog['started'][:10])
            task_timeSpent.append(worklog['timeSpentSeconds']/3600)

    timetracks['name'] = task_names
    timetracks['date'] = task_date
    timetracks['timeSpent'] = task_timeSpent
    timetracks.sort_values('date', ascending=True, inplace=True)
    final_timetracks = timetracks[timetracks['date'] >= first_day.replace('/','-')].copy()
    final_timetracks.rename(columns={'name': 'Subject', 'date': 'Start Date'}, inplace=True)
    final_timetracks['Start Date'] = final_timetracks['Start Date'].map(lambda x: ('/').join([x.split('-')[1], x.split('-')[2], x.split('-')[0]]))
    final_timetracks['Start Time'] = "09:00"
    final_timetracks['End Time'] = final_timetracks['timeSpent'].map(lambda x: dt.datetime.strptime(f"{9+int(x)}:{int((x*60)%60)}", "%H:%M").strftime("%H:%M"))
    return final_timetracks


def save_timetracks_to_csv(df: pd.DataFrame) -> None:
    df.to_csv(f"{os.path.dirname(os.path.realpath(__file__))}/data/{datetime.now().strftime('%B')}{datetime.now().year}.csv", index=False, encoding='utf-8')
    print(f"File '{datetime.now().strftime('%B')}{datetime.now().year}.csv' generated in data folder")


if __name__ == '__main__':
    first_day = f"{datetime.now().year}/{datetime.now().strftime('%m')}/01"
    last_day = f"{datetime.now().year}/{datetime.now().strftime('%m')}/{calendar.monthrange(datetime.now().year, datetime.now().month)[1]}"
    timetracks_df = get_timetracks(first_day, last_day, os.environ['JIRA_USER'], get_Jira_instance())
    save_timetracks_to_csv(timetracks_df)
    print(f"Summary for {datetime.now().strftime('%B')} {datetime.now().year} : ")
    print(f"Number of days : {timetracks_df['Start Date'].nunique()}")
    print(f"Number of hours : {timetracks_df['timeSpent'].sum()} of expected hours : {timetracks_df['Start Date'].nunique()*HOURS_PER_DAY_CONTRACT}")
    print(f"Amount of Invoice : {round(timetracks_df['timeSpent'].sum()*THM)} € HT")
