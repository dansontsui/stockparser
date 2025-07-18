print("Python測試成功")
print("當前目錄內容:")
import os
for item in os.listdir('.'):
    print(f"  {item}")

print("\n測試SQLite:")
import sqlite3
try:
    conn = sqlite3.connect('test.db')
    conn.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER, name TEXT)')
    conn.execute('INSERT INTO test VALUES (1, "測試")')
    conn.commit()
    
    cursor = conn.execute('SELECT * FROM test')
    for row in cursor:
        print(f"  資料: {row}")
    
    conn.close()
    print("SQLite測試成功")
except Exception as e:
    print(f"SQLite測試失敗: {e}")
