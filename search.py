import sqlite3
import sys

conn = sqlite3.connect('./data/simplewiki.db')
cursor = conn.cursor()


algorithm_sql = ""
results = None
result_offset = 0

def SelectAlgorithm(algo):
  global algorithm_sql
  with open("./algorithm/"+algo+'.sql', 'r') as f:
    algorithm_sql = f.read()

  print(f'  Loaded algorithm {algo}')

SelectAlgorithm("jaccard")

def ShowSimilar(target):
  cursor.execute("Select a.title from articles a where a.title like ? order by length(a.title) limit 5;", ( "%"+target+"%" ,))
  results = cursor.fetchall()
  print("  Try: " + ", ".join(str(val[0]) for val in results))

  pass

def Search(target):
  global results
  global result_offset

  cursor.execute("SELECT id FROM articles WHERE title = ?", (target,))
  res = cursor.fetchone()

  if res is None:
    print("No match")
    ShowSimilar(target)
    return

  target_id = res[0]

  placeholders = algorithm_sql.count("?")
  cursor.execute(algorithm_sql, (target_id, )*placeholders)
  results = cursor.fetchall()
  result_offset = 0

  ShowResults()

def ShowResults():
  global results
  global result_offset

  if results is None:
    print('No search present')
    return

  formatted_results = "  " + "\n  ".join(f'{row[1]:.4f} {row[0]} {row[2]}' for row in results[result_offset:result_offset+10])
  result_offset = result_offset + 10
  print(formatted_results)



def RunCommand(cmd):
  cmd = cmd.split(" ")

  match cmd[0]:
    case ".more":
      ShowResults()
    case ".algo":
      SelectAlgorithm(cmd[1])
    case ".exit":
      sys.exit(0)
    case _:
      print(f'Unknown command {cmd[0]}')


if __name__ == '__main__':
  while True:
    cmd = input("> ")
    if cmd[0] == ".":
      RunCommand(cmd)
    else:
      Search(cmd)