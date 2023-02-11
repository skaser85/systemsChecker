from datetime import datetime
from dataclasses import dataclass
from enum import Enum, auto
from database_handler import Db

class ObjectType(Enum):
    nothing = 0
    report = 3
    codeunit = 5

class JobStatus(Enum):
    Uninitialized = 0
    Ready = auto()
    In_Process = auto()
    Error = auto()
    On_Hold = auto()
    Finished = auto()

class LogJobStatus(Enum):
    Uninitialized = 0
    Success = auto()
    In_Process = auto()
    Error = auto()

@dataclass
class JobQueueEntry:
    server: str
    database_name: str
    object_type_to_run: ObjectType
    object_id_to_run: int
    description: str
    earliest_start_date_time: datetime = datetime(2000, 1, 1, 0, 0, 0)
    status: JobStatus = JobStatus.Uninitialized
    num_mins_between_runs: int = 0
    run_on_mondays: bool = False
    run_on_tuesdays: bool = False
    run_on_wednesdays: bool = False
    run_on_thursdays: bool = False
    run_on_fridays: bool = False
    run_on_saturdays: bool = False
    run_on_sundays: bool = False
    job_queue_category_code: str = ''
    is_running: bool = False
    last_run_dt: datetime = datetime(2000, 1, 1, 0, 0, 0)
    last_run_status: LogJobStatus = LogJobStatus.Uninitialized
    last_run_error_msg: str = ''

    def __post_init__(self):
        jqe = get_jqe(self)
        self.earliest_start_date_time =  jqe[0]
        self.status =  JobStatus(jqe[3] + 1)
        self.num_mins_between_runs =  int(jqe[4])
        self.run_on_mondays = bool_str(jqe[5])
        self.run_on_tuesdays = bool_str(jqe[6])
        self.run_on_wednesdays = bool_str(jqe[7])
        self.run_on_thursdays = bool_str(jqe[8])
        self.run_on_fridays = bool_str(jqe[9])
        self.run_on_saturdays = bool_str(jqe[10])
        self.run_on_sundays = bool_str(jqe[11])
        self.job_queue_category_code = jqe[13]
        self.is_running = self.status not in [JobStatus.Error, JobStatus.On_Hold]
        last_run = get_last_run_info(self)
        if last_run is not None:
            self.last_run_dt = last_run[0]
            self.last_run_status = LogJobStatus(last_run[1] + 1)
            self.last_run_error_msg = ' '.join(last_run[2:]).strip()

def get_jqe(jqe: JobQueueEntry) -> list:
    with Db(jqe.server, jqe.database_name) as db:
        rec = db.select(f'SELECT [Earliest Start Date_Time],[Object Type to Run],[Object ID to Run] ,[Status],[No_ of Minutes between Runs],[Run on Mondays],[Run on Tuesdays] ,[Run on Wednesdays],[Run on Thursdays],[Run on Fridays],[Run on Saturdays] ,[Run on Sundays],[Description],[Job Queue Category Code] FROM [{jqe.database_name}$Job Queue Entry] WHERE [Object ID to Run] = ? AND [Description] = ?', (jqe.object_id_to_run, jqe.description))
        return rec.fetchall()[0]

def get_last_run_info(jqe: JobQueueEntry) -> list:
    with Db(jqe.server, jqe.database_name) as db:
        rec = db.select(f'SELECT [Start Date_Time], [Status], [Error Message], [Error Message 2], [Error Message 3], [Error Message 4] FROM [{jqe.database_name}$Job Queue Log Entry] WHERE [Object ID to Run] = ? AND [Description] = ?', (jqe.object_id_to_run, jqe.description))
        rec = rec.fetchall()
        if len(rec) > 0:
            return rec[-1]

def bool_str(bs: str) -> bool:
    return True if bs == '1' else False

if __name__ == '__main__':
    # jqe = JobQueueEntry(r'SQL14\Prod', 'AEP', ObjectType.Codeunit, 50052, 'Process In Train Status')
    print(ObjectType['codeunit'].value)