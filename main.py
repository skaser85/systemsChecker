from typing import List
from dataclasses import dataclass, asdict
from enum import Enum, auto
from json import loads, dumps
from service import WinService
from url import Url
from program import WinProc, get_tasklist
from ssis import Ssis
from job import JobQueueEntry, ObjectType
from database_handler import Db

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

    def to_json(self):
        d = asdict(self)
        d['check_type'] = self.check_type.name.lower()
        d['check_category'] = self.check_category.name.lower()
        d['object_type'] = self.object_type.name.lower()
        return d

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
        object_type = ObjectType[item[14].lower()]

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
    # checks = get_checks_sql()
    # do_checks(checks)
    # write_checklist(checks, 'checklist.json')
    # add SQL16 checks/cleanup jobs
    checklist_filepath = 'checklist.json'
    checks = get_checks(checklist_filepath)
    # write_checklist(checks, checklist_filepath)
    # do_checks(checks)

    with Db('NKP8590', 'NKPSystemsCheck') as db:
        for i, check in enumerate(checks):
            sql = f'''SET IDENTITY_INSERT "Check" ON;
                      INSERT INTO [dbo].[Check] ([ID], [Name], [Server], [Check Type], [Check Category], [Service], 
                                                 [URL], [Program], [Instance Count], [Database], [Company], [Business Unit], 
                                                 [System], [Job ID], [Object Type], [Object ID]) 
                                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                      SET IDENTITY_INSERT "Check" OFF;'''
            values = (i+1, check.name, check.server, check.check_type.name.lower(), check.check_category.name.lower(), check.service, check.url, check.program, check.instance_count, check.database, check.company, check.business_unit, check.system, check.job_id, check.object_type.name.lower(), check.object_id)
            print(sql)
            print(values)
            db.insert(sql, values)
