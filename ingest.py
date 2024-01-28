import os
import re
import sqlite3
import xml.etree.ElementTree as ET


input_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), './data/simplewiki-latest-pages-articles.xml')


def page_get_meta(page):
  title = "Unknown"
  link_txt = ""
  redirect = None

  for child in page:
    if child.tag.endswith('title'):
      title = child.text
    if child.tag.endswith('redirect'):
      redirect = child.get('title')
    if child.tag.endswith('revision'):
      for elem in child:
        if elem.tag.endswith('text'):
          link_txt = elem.text

  if link_txt is None:
    print(f'\n    \033[36m{title}\033[0m has no body text')
    link_txt = ""

  link_pattern = re.compile(r'\[\[([^|\]]+)(?:\|[^\]]+)?\]\]')
  links = link_pattern.findall(link_txt)
  return (title, [link.strip() for link in links], redirect)


def Get_Article_ID(title, cursor):
  # title = title.lower()
  title = title[0].upper() + title[1:]

  # Insert the to_article if not present
  cursor.execute("INSERT OR IGNORE INTO articles (title) VALUES (?)", (title,))

  # Get the to article ID
  cursor.execute("SELECT id FROM articles WHERE title = ?", (title,))
  return cursor.fetchone()[0]


def Ingest_Links(cursor, conn):
  total_bytes = os.path.getsize(input_file)
  context = ET.iterparse(input_file, events=('end',))
  processed_bytes = 0

  batch_size = 5000
  batch = 0

  for event, elem in context:
    if elem.tag.endswith('page'):
      title, links, redirect = page_get_meta(elem)

      # Get the from article ID
      from_article_id = Get_Article_ID(title, cursor)

      if redirect:
        to_article_id = Get_Article_ID(redirect, cursor)
        cursor.execute("INSERT OR IGNORE INTO redirects (from_article_id, to_article_id) VALUES (?, ?)", (from_article_id, to_article_id))
        batch += 1
      else:
        for link in links:
          if len(link) < 1:
            print(f'\n    \033[36m{title}\033[0m has a blank link')
            continue

          to_article_id = Get_Article_ID(link, cursor)

          # Insert the link between them if not already present
          cursor.execute("INSERT OR IGNORE INTO links (from_article_id, to_article_id) VALUES (?, ?)", (from_article_id, to_article_id))

          # Batch the commits
          if batch >= batch_size:
            progress = (processed_bytes / total_bytes) * 100
            print(f'\r  Processed: {progress:.2f}%', end='')

            conn.commit()
            batch = 0
          batch += 1

        # Free up memory by clearing the XML element after processing
        processed_bytes += len(ET.tostring(elem, encoding='utf-8'))
        elem.clear()

  progress = (processed_bytes / total_bytes) * 100
  print(f'\r  Processed: {progress:.2f}%', end='')
  conn.commit()

  cursor.execute("SELECT COUNT(*) FROM articles")
  print(f"\n\n  Total articles: {cursor.fetchone()[0]}")
  cursor.execute("SELECT COUNT(*) FROM links")
  print(f"  Total links: {cursor.fetchone()[0]}")
  cursor.execute("SELECT COUNT(*) FROM redirects")
  print(f"  Total redirects: {cursor.fetchone()[0]}")


def main():
  conn = sqlite3.connect('./data/simplewiki.db')
  cursor = conn.cursor()

  cursor.execute("CREATE TABLE IF NOT EXISTS articles (id INTEGER PRIMARY KEY, title TEXT UNIQUE)")
  cursor.execute("CREATE TABLE IF NOT EXISTS links (from_article_id INTEGER, to_article_id INTEGER, UNIQUE(from_article_id, to_article_id))")
  cursor.execute("CREATE TABLE IF NOT EXISTS redirects (from_article_id INTEGER, to_article_id INTEGER, UNIQUE(from_article_id, to_article_id))")

  cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_from_to ON links(from_article_id, to_article_id)")
  cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_from ON links(from_article_id)")
  cursor.execute("CREATE INDEX idx_links_to ON links(to_article_id)")
  cursor.execute("CREATE INDEX idx_articles_id ON articles(id)")


  print("\nIngesting articles:")
  Ingest_Links(cursor=cursor, conn=conn)
  conn.commit()

  print("\nApply Redirections:")
  with open('./redirect.sql', 'r') as f:
    sql = f.read()

  conn.executescript(sql)
  print("  done")

  cursor.close()
  conn.close()

if __name__ == '__main__':
  main()