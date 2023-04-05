import sqlite3

conn = sqlite3.connect('./data/simplewiki.db')
cursor = conn.cursor()


jaccard_sql = ""
results = None
result_offset = 0

# read in the SQL file
with open('jaccard.sql', 'r') as f:
    jaccard_sql = f.read()

def ShowSimilar(target):
  cursor.execute("Select a.title from articles a where a.title like ? order by length(a.title) limit 5;", ( "%"+target+"%" ,))
  results = cursor.fetchall()
  print("  Try: " + ", ".join(str(val[0]) for val in results))

  pass

def search(target):
  global results
  global result_offset

  cursor.execute("SELECT id FROM articles WHERE title = ?", (target,))
  res = cursor.fetchone()

  if res is None:
    print("No match")
    ShowSimilar(target)
    return

  target_id = res[0]

  cursor.execute(jaccard_sql, (target_id, target_id, target_id, target_id,))
  results = cursor.fetchall()
  result_offset = 0

  ShowResults()

def ShowResults():
  global results
  global result_offset

  if results is None:
    print('No search present')
    return

  formatted_results = "  " + "\n  ".join(f'{row[3]:.4f} {row[0]} {row[1]}/{row[2]}' for row in results[result_offset:result_offset+10])
  result_offset = result_offset + 10
  print(formatted_results)

def RunCommand(cmd):
  match cmd:
    case ".more":
      ShowResults()
    case _:
      print(f'Unknown command {cmd}')

while True:
  cmd = input("> ")
  if cmd[0] == ".":
    RunCommand(cmd)
  else:
    search(cmd)