"""
This is the server file that serves the webpages and talks to the database.
"""

from flask import Flask, render_template, request
from flask_cors import CORS
import json
from main import get_checks_sql, get_checks, CheckType, CheckCategory, ObjectType, Check
from database_handler import Db

app = Flask(__name__)
CORS(app)

DB_SERVER = 'NKP8590'
DB_NAME = 'NKPSystemsCheck'
CHECK_TABLE = '[Check]'

@app.route('/')
def index():
    """ serves the home page """
    return render_template('index.html', checks=get_checks('checklist.json'))

@app.route('/documentation')
def documentation():
    """ serves the documentation page """
    return render_template('documentation.html')

@app.route('/edit/<check_id>')
def edit(check_id):
    check_id = int(check_id)
    checks = get_checks('checklist.json')
    if check_id == len(checks) + 1:
        check = checks[-1]
    elif check_id == 0:
        check = checks[0]
    else:
        check = [c for c in checks if c._id == check_id][0]
    return render_template('edit.html', check=check, 
                                        check_types=[c.name.upper() for c in list(CheckType)], 
                                        check_categories=[s.name.upper() for s in list(CheckCategory)], 
                                        object_types=[o.name.upper() for o in list(ObjectType)])

@app.route('/edit/save', methods=['POST'])
def save():
    data = json.loads(request.data)
    check = Check(int(data['id']), data['name'], data['server'], CheckType[data['checkType']], CheckCategory[data['checkCategory']], 
                  data['service'], data['url'], data['program'], int(data['instanceCount']), data['database'], data['company'], 
                  data['businessUnit'], data['system'], data['jobID'], ObjectType[data['objectType'].lower()], int(data['objectID']))
    with Db(DB_SERVER, DB_NAME) as db:
        db.update(f'''UPDATE {CHECK_TABLE}
                      SET [Name] = ?, [Server] = ?, [Check Type] = ?, 
                          [Check Category] = ?, [Service] = ?, [URL] = ?, 
                          [Program] = ?, [Instance Count] = ?, [Database] = ?, 
                          [Company] = ?, [Business Unit] = ?, [System] = ?, 
                          [Job ID] = ?, [Object Type] = ?, [Object ID] = ?
                      WHERE [ID] = ?''', 
                      (check.name, check.server, check.check_type.name.lower(), 
                       check.check_category.name.lower(), check.service, check.url,
                       check.program, check.instance_count, check.database, 
                       check.company, check.business_unit, check.system, 
                       check.job_id, check.object_type.name.lower(), check.object_id, check._id))
    return check.to_json()

@app.route('/add')
def add():
    return render_template('addCheck.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)