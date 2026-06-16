from database.db import get_conn
def init_db():
    conn=get_conn()
    conn.execute("CREATE TABLE IF NOT EXISTS snapshots(id INTEGER PRIMARY KEY AUTOINCREMENT, contract_id INTEGER,last_price REAL,volume INTEGER,open_interest INTEGER,snapshot_time TEXT)")
    conn.commit()
    conn.close()

CREATE INDEX idx_contract_id
ON snapshots(contract_id);
CREATE INDEX idx_snapshot_time
ON snapshots(snapshot_time);
CREATE INDEX idx_contract_code
ON contracts(contract_code);
