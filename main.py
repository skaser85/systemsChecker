from typing import List
from dataclasses import dataclass, asdict
from enum import Enum, auto
from json import loads, dumps
from datetime import datetime
from service import WinService
from url import Url
from program import WinProc, get_tasklist
from ssis import Ssis
from job import JobQueueEntry, ObjectType
from database_handler import Db

DB_SERVER = 'NKP8590'
DB_NAME = 'NKPSystemsCheck'

class CheckType(Enum):
    JOB = auto()
    PROGRAM = auto()
    SERVICE = auto()
    URL = auto()
    SSIS = auto()

class CheckCategory(Enum):
    NONE = auto()
    AVA = auto()
    EDI = auto()
    JOB = auto()
    NAS = auto()
    PRINT = auto()
    PROPHESY = auto()
    RTC = auto()
    SHAREPOINT = auto()
    SMS = auto()
    SQL = auto()
    WEBPAGE = auto()
    WS09R2 = auto()


@dataclass
class Check:
    _id: int
    name: str
    server: str
    check_type: CheckType
    check_category: CheckCategory = CheckCategory.NONE
    service: str = ''
    url: str = ''
    program: str = ''
    instance_count: int = 0
    database: str = ''
    company: str = ''
    business_unit: str = ''
    system: str = ''
    job_id: str = ''
    object_type: ObjectType = ObjectType.nothing
    object_id: int = 0
    is_running: bool = False

    def to_json(self):
        d = asdict(self)
        d['check_type'] = self.check_type.name.lower()
        d['check_category'] = self.check_category.name.lower()
        d['object_type'] = self.object_type.name.lower()
        return d

@dataclass
class Run:
    checks: List[Check]
    _id: int = 0
    start_dt: datetime = datetime(2000, 1, 1, 0, 0, 0)
    end_dt: datetime = datetime(2000, 1, 1, 0, 0, 0)
    total_checks: int = 0
    duration_secs: int = 0
    running: int = 0
    not_running: int = 0

    def __post_init__(self):
        with Db('NKP8590', 'NKPSystemsCheck') as db:
            runs = db.select('SELECT * FROM [Run Log]').fetchall()
            if len(runs) == 0:
                self._id = 1
            else:
                self._id = runs[-1][0] + 1
            db.insert('''INSERT INTO [Run Log] ([ID]) VALUES (?)''', (self._id))

    def do_checks(self) -> None:
        self.start_dt = datetime.now()
        tasklists = {}
        total = len(self.checks)
        for i, check in enumerate(self.checks):
            print(f'{i + 1} of {total}: Checking {check.name}...')
            if check.check_type == CheckType.JOB:
                start_dt = datetime.now()
                proc = JobQueueEntry(check.server, check.database.upper(), check.object_type, check.object_id, check.name)
                end_dt = datetime.now()
                check.is_running = proc.is_running
                self.log_jqe(proc, check._id, start_dt, end_dt)
            elif check.check_type == CheckType.SSIS:
                start_dt = datetime.now()
                proc = Ssis(check.name, check.job_id, check.server)
                end_dt = datetime.now()
                check.is_running = proc.is_running
                self.log_ssis(proc, check._id, start_dt, end_dt)
            elif check.check_type == CheckType.PROGRAM:
                start_dt = datetime.now()
                if check.server not in tasklists:
                    tasklists[check.server] = get_tasklist(check.server)
                tl = tasklists[check.server]
                proc = WinProc(check.program, check.server, tl)
                end_dt = datetime.now()
                check.is_running = proc.is_running
                self.log_program(proc, check._id, start_dt, end_dt)
            elif check.check_type == CheckType.SERVICE:
                start_dt = datetime.now()
                proc = WinService(check.service, check.server)
                end_dt = datetime.now()
                check.is_running = proc.is_running
                self.log_service(proc, check._id, start_dt, end_dt)
            elif check.check_type == CheckType.URL:
                start_dt = datetime.now()
                proc = Url(check.url)
                end_dt = datetime.now()
                check.is_running = proc.is_running
                self.log_url(proc, check._id, start_dt, end_dt)
            else:
                raise KeyError(f'Unknown check type: {check.check_type}\n{check}')
        self.log_run()

    def log_jqe(self, jqe: JobQueueEntry, check_id: int, start_dt: datetime, end_dt: datetime) -> None:
        duration = end_dt - start_dt
        duration = duration.total_seconds()
        with Db(DB_SERVER, DB_NAME) as db:
            db.insert('''INSERT INTO [Nav Job Check Log] ([Run ID],[Check ID],[Earliest Start DateTime],[Status],[Job Queue Category Code],
                                                          [Is Running],[Last Run DateTime],[Last Run Status],[Last Run Error Message],
                                                          [Start DateTime],[End DateTime],[Duration (secs)])
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', (self._id, check_id, jqe.earliest_start_date_time, jqe.status.value, jqe.job_queue_category_code,
                                                               bool_int(jqe.is_running), jqe.last_run_dt, jqe.last_run_status.value, jqe.last_run_error_msg,
                                                               start_dt, end_dt, duration))

    def log_ssis(self, ssis: Ssis, check_id: int, start_dt: datetime, end_dt: datetime) -> None:
        duration = end_dt - start_dt
        duration = duration.total_seconds()
        with Db(DB_SERVER, DB_NAME) as db:
            db.insert('''INSERT INTO [SSIS Check Log] ([Run ID],[Check ID],[Enabled],[Minutes Between Runs],[Last Run DateTime],[Last Run Status],
                                                       [Is Running],[Start DateTime],[End DateTime],[Duration (secs)]) 
                         VALUES (?,?,?,?,?,?,?,?,?,?)''', (self._id, check_id, bool_int(ssis.enabled), ssis.minutes_between_runs, ssis.last_run_dt, ssis.last_run_status.value,
                                                         bool_int(ssis.is_running), start_dt, end_dt, duration))

    def log_program(self, program: WinProc, check_id: int, start_dt: datetime, end_dt: datetime) -> None:
        duration = end_dt - start_dt
        duration = duration.total_seconds()
        with Db(DB_SERVER, DB_NAME) as db:
            db.insert('''INSERT INTO [Program Check Log] ([Run ID],[Check ID],[Program],[Instance Count],[Is Running]
                                                         ,[Start DateTime],[End DateTime],[Duration (secs)])
                         VALUES (?,?,?,?,?,?,?,?)''', (self._id, check_id, program.name, len(program.instances), bool_int(program.is_running),
                                                       start_dt, end_dt, duration))

    def log_service(self, service: WinService, check_id: int, start_dt: datetime, end_dt: datetime) -> None:
        duration = end_dt - start_dt
        duration = duration.total_seconds()
        with Db(DB_SERVER, DB_NAME) as db:
            db.insert('''INSERT INTO [Service Check Log] ([Run ID],[Check ID],[Service],[State],
                                                          [Is Running],[Start DateTime],[End DateTime],[Duration (secs)])
                         VALUES (?,?,?,?,?,?,?,?)''', (self._id, check_id,service.name,service.state.value,
                                                       bool_int(service.is_running), start_dt, end_dt, duration))

    def log_url(self, url: Url, check_id: int, start_dt: datetime, end_dt: datetime) -> None:
        duration = end_dt - start_dt
        duration = duration.total_seconds()
        with Db(DB_SERVER, DB_NAME) as db:
            db.insert('''INSERT INTO [URL Check Log] ([Run ID],[Check ID],[URL],[Status Code],
                                                      [Is Running],[Start DateTime],[End DateTime],[Duration (secs)])
                         VALUES (?,?,?,?,?,?,?,?)''', (self._id, check_id, url.url, url.status_code,
                                                       bool_int(url.is_running), start_dt, end_dt, duration))

    def log_run(self) -> None:
        self.end_dt = datetime.now()
        duration = self.end_dt - self.start_dt
        self.duration_secs = duration.total_seconds()
        self.total_checks = len(self.checks)
        self.running = len([c for c in self.checks if c.is_running])
        self.not_running = self.total_checks - self.running
        with Db(DB_SERVER, DB_NAME) as db:
            db.update('''UPDATE [Run Log] 
                         SET [Run Start DateTime] = ?,[Run End DateTime] = ?,[Total Checks] = ?,
                             [Running] = ?,[Not Running] = ?,[Run Duration (secs)] = ?
                         WHERE [ID] = ?''', (self.start_dt, self.end_dt, self.total_checks,
                                             self.running, self.not_running, self.duration_secs, self._id))

def bool_int(b: bool) -> int:
    return 1 if b else 0

def write_checklist(checks: List[Check], checklist_filepath: str) -> None:
    data = []
    for check in checks:
        data.append(check.to_json())
    with open(checklist_filepath, 'w') as f:
        f.write(dumps(data, ensure_ascii=True, indent=4))

def get_checks(checklist_filepath: str) -> List[Check]:
    with open(checklist_filepath, 'r') as f:
        data = loads(f.read())
    
    checks: List[Check] = []
    for item in data:
        ct = CheckType[item['check_type'].upper()]
        st = CheckCategory[item['check_category'].upper()]
        object_type = ObjectType[item['object_type'].lower()]

        check = Check(item['_id'], item['name'], item['server'], ct, st, item['service'], item['url'], \
                      item['program'], item['instance_count'], item['database'], \
                      item['company'], item['business_unit'], item['system'], item['job_id'], \
                      object_type, item['object_id'])
        
        checks.append(check)
    return checks

def get_checks_sql() -> List[Check]:
    with Db('NKP8590', 'NKPSystemsCheck') as db:
        checklist = db.select('SELECT * FROM [Check]').fetchall()
    checks: List[Check] = []
    for item in checklist:
        ct = CheckType[item[3].upper()]
        st = CheckCategory[item[4].upper()]
        object_type = ObjectType['nothing' if item[14].lower() == 'null' else item[14].lower()]

        check = Check(item[0], item[1], item[2], ct, st, item[5], item[6], item[7], item[8], item[9], \
                      item[10], item[11], item[12], item[13], object_type, item[15])
        
        checks.append(check)
    return checks

def do_checks(checks) -> None:
    tasklists = {}
    total = len(checks)
    for i, check in enumerate(checks):
        print(f'{i + 1} of {total}: Checking {check.name}...')
        if check.check_type == CheckType.JOB:
            proc = JobQueueEntry(check.server, check.database.upper(), check.object_type, check.object_id, check.name)
        elif check.check_type == CheckType.SSIS:
            proc = Ssis(check.name, check.job_id, check.server)
        elif check.check_type == CheckType.PROGRAM:
            if check.server not in tasklists:
                tasklists[check.server] = get_tasklist(check.server)
            tl = tasklists[check.server]
            proc = WinProc(check.program, check.server, tl)
        elif check.check_type == CheckType.SERVICE:
            proc = WinService(check.service, check.server)
        elif check.check_type == CheckType.URL:
            proc = Url(check.url)
        else:
            raise KeyError(f'Unknown check type: {check.check_type}\n{check}')
        
        if not proc.is_running:
            print(f'NOT RUNNING:\n{proc}')

if __name__ == '__main__':
    # checklist_filepath = 'checklist.json'

    checks = get_checks_sql()
    run = Run(checks)
    run.do_checks()

    # checks = get_checks(checklist_filepath)
    # write_checklist(checks, checklist_filepath)
    # do_checks(checks)

    # with Db('NKP8590', 'NKPSystemsCheck') as db:
    #     for i, check in enumerate(checks):
    #         sql = f'''SET IDENTITY_INSERT "Check" ON;
    #                   INSERT INTO [dbo].[Check] ([ID], [Name], [Server], [Check Type], [Check Category], [Service], 
    #                                              [URL], [Program], [Instance Count], [Database], [Company], [Business Unit], 
    #                                              [System], [Job ID], [Object Type], [Object ID]) 
    #                                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    #                   SET IDENTITY_INSERT "Check" OFF;'''
    #         values = (i+1, check.name, check.server, check.check_type.name.lower(), check.check_category.name.lower(), check.service, check.url, check.program, check.instance_count, check.database, check.company, check.business_unit, check.system, check.job_id, check.object_type.name.lower(), check.object_id)
    #         print(sql)
    #         print(values)
    #         db.insert(sql, values)
