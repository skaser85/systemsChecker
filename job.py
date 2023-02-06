from datetime import datetime
from dataclasses import dataclass
from enum import Enum, auto
import pyodbc

class ObjectType(Enum):
    Report = 3
    Codeunit = 5

class ReportOutputType(Enum):
    Pdf = auto()
    Word = auto()
    Excel = auto()
    Print = auto()
    Processing_Only = auto()

class JobStatus(Enum):
    Ready = auto()
    In_Process = auto()
    Error = auto()
    On_Hold = auto()
    Finished = auto()

@dataclass
class JobQueueEntry:
    timestamp: str
    record_id: str
    user_id: str
    xml: str
    last_ready_state: datetime
    expiration_date_time: datetime
    earliest_start_date_time: datetime
    object_type_to_run: ObjectType
    object_id_to_run: int
    report_output_type: ReportOutputType
    max_num_attempts_to_run: int
    status: JobStatus
    priority: int
    record_id_to_process: int
    parameter_string: str
    recurring_job: bool
    num_mins_between_runs: int
    run_on_mondays: bool
    run_on_tuesdays: bool
    run_on_wednesdays: bool
    run_on_thursdays: bool
    run_on_fridays: bool
    run_on_saturdays: bool
    run_on_sundays: bool
    starting_time: datetime.time
    ending_time: datetime.time
    reference_starting_time: datetime.time
    description: str
    run_in_user_session: bool
    user_session_id: int
    job_queue_category_code: str
    error_message: str
    error_message_2: str
    error_message_3: str
    error_message_4: str
    user_service_instance_id: int
    user_session_started: bool
    timeout_sec: int
    notify_on_success: bool
    user_language_id: int
    printer_name: str
    report_request_page_options: bool
    rerun_delay_sec: int
    num_attempts_to_run: int

def get_object_type(object_type: str) -> ObjectType:
    if object_type == 3:
        return ObjectType.Report
    elif object_type == 5:
        return ObjectType.Codeunit
    else:
        raise KeyError(f'Unsupported object type: {object_type}.')

def get_report_output_type(t: str) -> ReportOutputType:
    t = int(t)
    types = list(ReportOutputType)
    return types[t]

def get_job_status(t: str) -> JobStatus:
    t = int(t)
    types = list(JobStatus)
    return types[t]

def bool_str(bs: str) -> bool:
    return True if bs == '1' else False

def create_job_queue_entry_16(jqe: tuple) -> JobQueueEntry:
    timestamp = jqe[0]
    record_id = jqe[1]
    user_id = jqe[2]
    xml = jqe[3]
    last_ready_state = jqe[4]
    expiration_date_time =  jqe[5]
    earliest_start_date_time =  jqe[6]
    object_type_to_run =  get_object_type(jqe[7])
    object_id_to_run =  int(jqe[8])
    report_output_type =  get_report_output_type(jqe[9])
    max_num_attempts_to_run =  int(jqe[10])
    status =  get_job_status(jqe[11])
    priority =  int(jqe[12])
    record_id_to_process =  jqe[13]
    parameter_string =  jqe[14]
    recurring_job =  bool_str(jqe[15])
    num_mins_between_runs =  int(jqe[16])
    run_on_mondays = bool_str(jqe[17])
    run_on_tuesdays = bool_str(jqe[18])
    run_on_wednesdays = bool_str(jqe[19])
    run_on_thursdays = bool_str(jqe[20])
    run_on_fridays = bool_str(jqe[21])
    run_on_saturdays = bool_str(jqe[22])
    run_on_sundays = bool_str(jqe[23])
    starting_time = jqe[24].time()
    ending_time = jqe[25].time()
    reference_starting_time = jqe[26].time()
    description =  jqe[27]
    run_in_user_session =  bool_str(jqe[28])
    user_session_id = int(jqe[29])
    job_queue_category_code = jqe[30]
    error_message = jqe[31]
    error_message_2 = jqe[32]
    error_message_3 = jqe[33]
    error_message_4 = jqe[34]
    user_service_instance_id = int(jqe[35])
    user_session_started = bool_str(jqe[36])
    timeout_sec = int(jqe[37])
    notify_on_success = bool_str(jqe[38])
    user_language_id = bool_str(jqe[39])
    printer_name = jqe[40]
    report_request_page_options = jqe[41]
    rerun_delay_sec = jqe[42]

    return JobQueueEntry(timestamp, record_id, user_id, xml, last_ready_state, expiration_date_time, earliest_start_date_time, \
                         object_type_to_run, object_id_to_run, report_output_type, max_num_attempts_to_run, status, priority, \
                         record_id_to_process, parameter_string, recurring_job, num_mins_between_runs, run_on_mondays, run_on_tuesdays, \
                         run_on_wednesdays, run_on_thursdays, run_on_fridays, run_on_saturdays, run_on_sundays, starting_time, ending_time, \
                         reference_starting_time, description, run_in_user_session, user_session_id, job_queue_category_code, error_message, \
                         error_message_2, error_message_3, error_message_4, user_service_instance_id, user_session_started, timeout_sec, \
                         notify_on_success, user_language_id, printer_name, report_request_page_options, rerun_delay_sec, 0)

def create_job_queue_entry_18(jqe: tuple) -> JobQueueEntry:
    timestamp = jqe[0]
    record_id = jqe[1]
    user_id = jqe[2]
    xml = jqe[3]
    last_ready_state = jqe[4]
    expiration_date_time =  jqe[5]
    earliest_start_date_time =  jqe[6]
    object_type_to_run =  get_object_type(jqe[7])
    object_id_to_run =  int(jqe[8])
    report_output_type =  get_report_output_type(jqe[9])
    max_num_attempts_to_run =  int(jqe[10])
    num_attempts_to_run = int(jqe[11])

    status =  get_job_status(jqe[12])
    priority =  int(jqe[13])
    record_id_to_process =  jqe[14]
    parameter_string =  jqe[15]
    recurring_job =  bool_str(jqe[16])
    num_mins_between_runs =  int(jqe[17])
    run_on_mondays = bool_str(jqe[18])
    run_on_tuesdays = bool_str(jqe[19])
    run_on_wednesdays = bool_str(jqe[20])
    run_on_thursdays = bool_str(jqe[21])
    run_on_fridays = bool_str(jqe[22])
    run_on_saturdays = bool_str(jqe[23])
    run_on_sundays = bool_str(jqe[24])
    starting_time = jqe[25].time()
    ending_time = jqe[26].time()
    reference_starting_time = jqe[27].time()
    description =  jqe[28]
    run_in_user_session =  bool_str(jqe[29])
    user_session_id = int(jqe[30])
    job_queue_category_code = jqe[31]
    error_message = jqe[32]
    error_message_2 = jqe[33]
    error_message_3 = jqe[34]
    error_message_4 = jqe[35]
    user_service_instance_id = int(jqe[36])
    user_session_started = bool_str(jqe[37])
    timeout_sec = int(jqe[38])
    notify_on_success = bool_str(jqe[39])
    user_language_id = bool_str(jqe[40])
    printer_name = jqe[41]
    report_request_page_options = jqe[42]
    rerun_delay_sec = jqe[43]

    return JobQueueEntry(timestamp, record_id, user_id, xml, last_ready_state, expiration_date_time, earliest_start_date_time, \
                         object_type_to_run, object_id_to_run, report_output_type, max_num_attempts_to_run, status, priority, \
                         record_id_to_process, parameter_string, recurring_job, num_mins_between_runs, run_on_mondays, run_on_tuesdays, \
                         run_on_wednesdays, run_on_thursdays, run_on_fridays, run_on_saturdays, run_on_sundays, starting_time, ending_time, \
                         reference_starting_time, description, run_in_user_session, user_session_id, job_queue_category_code, error_message, \
                         error_message_2, error_message_3, error_message_4, user_service_instance_id, user_session_started, timeout_sec, \
                         notify_on_success, user_language_id, printer_name, report_request_page_options, rerun_delay_sec, num_attempts_to_run)

def db():
    conn = pyodbc.connect('Driver={SQL Server};'
                        r'Server=devsql1;'
                        'Database=AEP;'
                        'Trusted_Connection=yes;')

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM "AEP$Job Queue Entry"')

    for i in cursor:
        j = create_job_queue_entry_18(i)
        print(j)

if __name__ == '__main__':
    db()