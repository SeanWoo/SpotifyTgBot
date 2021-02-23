tokens_query = "CREATE TABLE IF NOT EXISTS tokens (id INT NOT NULL PRIMARY KEY, access_token VARCHAR(64), refresh_token VARCHAR(64))"

def initDb(db):
    db.execute(tokens_query)