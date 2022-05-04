from atlassian import Jira
import os
import pandas as pd
from datetime import datetime
import calendar

def get_Jira_instance() -> Jira:
    return Jira(
        url = os.environ['JIRA_URL'],
        username = os.environ['JIRA_USER'],
        password = os.environ['JIRA_PWD'],
    )

def get_timetracks(first_day:str, last_day:str, username:str, jira_instance:Jira) -> pd.DataFrame:
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
    return timetracks[timetracks['date'] >= first_day.replace('/','-')].copy()


def save_timetracks_to_csv(df:pd.DataFrame) -> None:
    df.to_csv(f"{os.path.dirname(os.path.realpath(__file__))}/data/{datetime.now().strftime('%B')}{datetime.now().year}.csv", index=False, encoding='utf-8')

if __name__ == '__main__':
    first_day=f"{datetime.now().year}/{datetime.now().strftime('%m')}/01"
    last_day=f"{datetime.now().year}/{datetime.now().strftime('%m')}/{calendar.monthrange(datetime.now().year, datetime.now().month)[1]}"
    timetracks_df = get_timetracks(first_day, last_day, os.environ['JIRA_USER'], get_Jira_instance())
    save_timetracks_to_csv(timetracks_df)