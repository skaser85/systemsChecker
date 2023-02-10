from dataclasses import dataclass
from enum import Enum
from datetime import date, time, datetime
# import time
from database_handler import Db

class FreqType(Enum):
    Never = 0
    Once = 1
    Daily = 4
    Weekly = 8
    Monthly = 16
    Monthly_Relative = 32
    Sql_Agent_Starts = 64
    Computer_is_Idle = 128

class FreqSubdayType(Enum):
    Unspecified = 0
    At_Specified_Time = 1
    Seconds = 2
    Minutes = 4
    Hours = 8

class RunStatus(Enum):
    Failed = 0
    Succeeded = 1
    Retry = 2
    Canceled = 3
    In_Progress = 4

@dataclass
class Ssis:
    name: str
    job_id: str
    server: str
    enabled: bool = False
    minutes_between_runs: int = 0
    last_run_dt: datetime = datetime(2000, 1, 1, 0, 0,0)
    last_run_status: RunStatus = RunStatus.Failed
    is_running: bool = False

    def __post_init__(self):
        schedule = get_job_schedule(self)
        
        self.enabled = True if schedule[0] == 1 else False
        self.minutes_between_runs = calc_minutes_between_runs(schedule)
        
        last_run = get_last_run(self)
        if last_run is not None:
            d = parse_date(last_run[1])
            t = parse_time(last_run[2])
            dt = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
            self.last_run_dt = dt
            self.last_run_status = RunStatus(last_run[0])
            within_target_run_window = last_run_within_target_run_window(self.minutes_between_runs, dt)
            self.is_running = self.last_run_status == RunStatus.Succeeded and within_target_run_window

def last_run_within_target_run_window(minutes_between_runs: int, last_run_dt: datetime) -> bool:
    elapsed = datetime.now() - last_run_dt
    mins = elapsed.total_seconds() / 60
    return mins <= minutes_between_runs

def get_last_run(ssis: Ssis) -> list:
    with Db(ssis.server, 'msdb') as db:
        history = db.select('SELECT [run_status],[run_date],[run_time] FROM [sysjobhistory] WHERE [job_id] = ? AND [step_id] = 0', (ssis.job_id))
        history = history.fetchall()
        if len(history) > 0:
            return history[-1]

def get_job_schedule(ssis: Ssis) -> tuple[int]:
    with Db(ssis.server, 'msdb') as db:
        job_schedule = db.select('SELECT * FROM [sysjobschedules] WHERE job_id = ?', (ssis.job_id))
        job_schedule = job_schedule.fetchall()

        schedule_id = job_schedule[0][0]
        
        schedule = db.select('SELECT enabled, freq_type, freq_interval, freq_subday_type, freq_subday_interval, active_start_time FROM [sysschedules] WHERE [schedule_id] = ?', (schedule_id))
        schedule = schedule.fetchall()[0]
        return schedule

def calc_minutes_between_runs(schedule: tuple[int]) -> int:
    freq_type = FreqType(schedule[1])
    freq_interval = schedule[2]
    freq_subday_type = FreqSubdayType(schedule[3])
    freq_subday_interval = schedule[4]
    active_start_time = schedule[5]
    if schedule[5] > 0:
        active_start_time = parse_time(schedule[5])
    

    minutes = 0
    if freq_type == FreqType.Daily:
        if freq_subday_interval == 0:
            minutes = 24*60
    elif freq_type == FreqType.Weekly:
        minutes = 24*60*7
    elif freq_type == FreqType.Monthly:
        minutes = 24*60*31
    else:
        raise ValueError(f'Unsupported FreqType: {freq_type}')

    if freq_subday_type == FreqSubdayType.Seconds:
        minutes += (freq_subday_interval / 60)
    elif freq_subday_type == FreqSubdayType.Minutes:
        minutes += freq_subday_interval
    elif freq_subday_type == FreqSubdayType.Hours:
        minutes += (freq_subday_interval * 60)
    elif freq_subday_type == FreqSubdayType.At_Specified_Time:
        ...
    else:
        raise ValueError(f'Unsupported FreqSubdayType: {freq_subday_type}')

    return minutes

def parse_time(time_text: str) -> time:
    time_text = str(time_text)
    if len(time_text) == 5:
        time_text = '0' + time_text
    hour = int(time_text[:2])
    minute = int(time_text[2:4])
    second = int(time_text[-2:])
    return time(hour, minute, second)

def parse_date(date_text: str) -> date:
    date_text = str(date_text)
    if len(date_text) == 5:
        date_text = '0' + date_text
    year = int(date_text[:4])
    month = int(date_text[4:6])
    day = int(date_text[-2:])
    return date(year, month, day)

if __name__ == '__main__':
    # job = Ssis('AEP File Cleanup', '69A67C00-AB64-475A-BF25-5E103A65DCB8', 'SQL14\\Prod')
    job = Ssis('ESI_Daily', 'A9A56557-2288-4D76-ABB6-D2DDF0C1C621', 'NKPSQL16')
    print(job)