from typing import List
from dataclasses import dataclass, asdict
from enum import Enum, auto
from json import loads, dumps
from service import WinService
from url import Url
from program import WinProc
from load_db import db
from database_handler import Db

class CheckType(Enum):
    JOB = auto()
    PROGRAM = auto()
    SERVICE = auto()
    URL = auto()
    SSIS = auto()

class ServiceType(Enum):
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
    name: str
    server: str
    check_type: CheckType
    service_type: ServiceType = ServiceType.NONE
    service: str = ''
    url: str = ''
    program: str = ''
    instance_count: int = 0
    database: str = ''
    company: str = ''
    business_unit: str = ''
    system: str = ''
    job_id: str = ''

    def to_json(self):
        d = asdict(self)
        d['check_type'] = self.check_type.name.lower()
        d['service_type'] = self.service_type.name.lower()
        return d

def get_check_type(t: str) -> CheckType:
    t = t.lower()
    types = list(CheckType)
    for tp in types:
        if tp.name.lower() == t:
            return tp
    raise KeyError(f'Cannot find a valid job type for {t}.')

def get_service_type(t: str) -> ServiceType:
    t = t.lower()
    types = list(ServiceType)
    for tp in types:
        if tp.name.lower() == t:
            return tp
    return ServiceType.NONE

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
        ct = get_check_type(item['check_type'])
        st = get_service_type(item['service_type'])
        check = Check(item['name'], item['server'], ct, st, item['service'], item['url'], \
                      item['program'], item['instance_count'], item['database'], \
                      item['company'], item['business_unit'], item['system'], item['job_id'])
        checks.append(check)
    return checks

def do_checks(checks) -> None:
    total = len(checks)
    for i, check in enumerate(checks):
        print(f'{i + 1} of {total}: Checking {check.name}...')
        if check.check_type == CheckType.JOB:
            ...
        elif check.check_type == CheckType.SSIS:
            ...
        elif check.check_type == CheckType.PROGRAM:
            proc = WinProc(check.program, check.server)
        elif check.check_type == CheckType.SERVICE:
            proc = WinService(check.service, check.server)
        elif check.check_type == CheckType.URL:
            proc = Url(check.url)
        else:
            raise KeyError(f'Unknown check type: {check.check_type}\n{check}')
        
        if not proc.is_running:
            print(f'NOT RUNNING:\n{proc}')

if __name__ == '__main__':
    # add SQL16 checks/cleanup jobs
    checklist_filepath = 'checklist.json'
    checks = get_checks(checklist_filepath)
    # write_checklist(checks, checklist_filepath)
    # do_checks(checks)

    with Db('NKP8590', 'NKPSystemsCheck') as db:
        for i, check in enumerate(checks):
            sql = f'SET IDENTITY_INSERT "Check" ON;INSERT INTO [dbo].[Check] ([ID], [Name], [Server], [Check Type], [Service Type], [Service], [URL], [Program], [Instance Count], [Database], [Company], [Business Unit], [System], [Job ID]) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);SET IDENTITY_INSERT "Check" OFF;'
            values = (i+1, check.name, check.server, check.check_type.name.lower(), check.service_type.name.lower(), check.service, check.url, check.program, check.instance_count, check.database, check.company, check.business_unit, check.system, check.job_id)
            print(sql)
            print(values)
            db.insert(sql, values)
