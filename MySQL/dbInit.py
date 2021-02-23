tokens_query = "CREATE TABLE IF NOT EXISTS tokens (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, access_token VARCHAR(64), refresh_token VARCHAR(64), expires_in INT, registration_at DATETIME)"

def initDb(db):
    db.execute(tokens_query)