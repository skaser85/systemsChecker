from database import Database

class Db:
    def __init__(self, server: str, name: str):
        self.db = Database(server, name)

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.cursor.close()
        self.db.connection.close()

if __name__ == '__main__':
    with Db('NKP8590', 'NKPSystemsCheck') as db:
        checks = db.select('SELECT * FROM "Check"')
        for c in checks:
            print(c)