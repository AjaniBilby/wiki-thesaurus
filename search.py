import sqlite3
import sys

conn = sqlite3.connect('./data/simplewiki.db')
cursor = conn.cursor()


algorithm_sql = ""
results = None
result_offset = 0
result_size = 10

def SelectAlgorithm(algo, display=False):
  global algorithm_sql
  with open("./algorithm/"+algo+'.sql', 'r') as f:
    algorithm_sql = f.read()

  if display:
    print(f'  Loaded algorithm {algo}')

SelectAlgorithm("jaccard")

def ShowSimilar(target):
  cursor.execute("Select a.title from articles a where a.title like ? order by length(a.title) limit 10;", ( "%"+target+"%" ,))
  results = cursor.fetchall()
  print("  Try: " + ", ".join(str(val[0]) for val in results))

  pass

def Search(target):
  global results
  global result_offset

  target = target[0].upper() + target[1:]

  cursor.execute("SELECT id FROM articles WHERE title = ?", (target,))
  res = cursor.fetchone()

  if res is None:
    ShowSimilar(target)
    return
  target_id = res[0]

  cursor.execute("select * from redirects where from_article_id= ?", (target_id,))
  res = cursor.fetchone()
  if res is not None:
    target_id = res[1]
    cursor.execute("SELECT title FROM articles WHERE id = ?", (target_id,))
    res = cursor.fetchone()
    print(f' redirect {res[0]}')

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

  nx = result_offset + result_size
  formatted_results = "\n".join(f'{row[1]:.2f} \033[36m{row[0]}\033[0m {row[2]}' for row in results[result_offset:nx])
  result_offset = nx
  print(formatted_results)



def RunCommand(cmd):
  global result_size
  cmd = cmd.split(" ")

  match cmd[0]:
    case ".next":
      ShowResults()
    case ".algo":
      SelectAlgorithm(cmd[1], True)
    case '.limit':
      result_size = int(cmd[1])
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