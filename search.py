import sqlite3

conn = sqlite3.connect('./data/simplewiki.db')
cursor = conn.cursor()


jaccard_sql = ""

# read in the SQL file
with open('jaccard.sql', 'r') as f:
    jaccard_sql = f.read()

def search(target):
  cursor.execute("SELECT id FROM articles WHERE title = ?", (target,))
  res = cursor.fetchone()

  if res is None:
    print("Invalid")
    return

  target_id = res[0]

  cursor.execute(jaccard_sql, (target_id, target_id, target_id, target_id,))
  results = cursor.fetchall()

  formatted_results = "  " + "\n  ".join(" ".join(str(value) for value in row) for row in results)
  print(formatted_results)


while True:
  search(input("Search: "))