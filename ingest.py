import os
import re
import sqlite3
import xml.etree.ElementTree as ET


input_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), './data/simplewiki-latest-pages-articles.xml')


def page_get_meta(page):
  title = "Unknown"
  link_txt = ""

  for child in page:
    if child.tag.endswith('title'):
      title = child.text
    if child.tag.endswith('revision'):
      for elem in child:
        if elem.tag.endswith('text'):
          link_txt = elem.text

  if link_txt is None:
    print(f'\n    Error: No Link text for {title}')
    link_txt = ""

  link_pattern = re.compile(r'\[\[([^|\]]+)(?:\|[^\]]+)?\]\]')
  links = link_pattern.findall(link_txt)
  return (title, [link.strip() for link in links])


def Ingest_Links(cursor, conn):
  total_bytes = os.path.getsize(input_file)
  context = ET.iterparse(input_file, events=('end',))
  processed_bytes = 0

  batch_size = 1000
  batch = 0

  for event, elem in context:
    if elem.tag.endswith('page'):
      title, links = page_get_meta(elem)
      title = title.lower()

      # Insert the from article if not present
      cursor.execute("INSERT OR IGNORE INTO articles (title) VALUES (?)", (title,))

      # Get the from article ID
      cursor.execute("SELECT id FROM articles WHERE title = ?", (title,))
      from_article_id = cursor.fetchone()[0]

      for link in links:
        link = link.lower()

        # Insert the to_article if not present
        cursor.execute("INSERT OR IGNORE INTO articles (title) VALUES (?)", (link,))

        # Get the to article ID
        cursor.execute("SELECT id FROM articles WHERE title = ?", (link,))
        to_article_id = cursor.fetchone()[0]

        # Insert the link between them if not already present
        cursor.execute("INSERT OR IGNORE INTO links (from_article_id, to_article_id) VALUES (?, ?)", (from_article_id, to_article_id))

        # Batch the commits
        if batch == batch_size:
          progress = (processed_bytes / total_bytes) * 100
          print(f'\r  Processed: {progress:.2f}%', end='')

          conn.commit()
          batch = 0
        batch += 1

      # Free up memory by clearing the XML element after processing
      processed_bytes += len(ET.tostring(elem, encoding='utf-8'))
      elem.clear()

  conn.commit()
  cursor.execute("SELECT COUNT(*) FROM links")
  print(f"\n  Total links: {cursor.fetchone()[0]}")


def main():
  conn = sqlite3.connect('./data/simplewiki.db')
  cursor = conn.cursor()

  cursor.execute("CREATE TABLE IF NOT EXISTS articles (id INTEGER PRIMARY KEY, title TEXT UNIQUE)")
  cursor.execute("CREATE TABLE IF NOT EXISTS links (from_article_id INTEGER, to_article_id INTEGER, UNIQUE(from_article_id, to_article_id))")

  # print("Ingesting article titles:")
  # Ingest_Titles(cursor=cursor, conn=conn)

  print("\nIngesting article link:")
  Ingest_Links(cursor=cursor, conn=conn)

  conn.close()

if __name__ == '__main__':
  main()