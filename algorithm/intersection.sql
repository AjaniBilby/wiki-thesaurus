WITH target_links AS (
  SELECT to_article_id
  FROM links
  WHERE from_article_id = ? -- target ID
),
intersection_count AS (
  SELECT l.from_article_id, COUNT(*) AS intersection
  FROM links l
  INNER JOIN target_links tl ON
    l.to_article_id = tl.to_article_id
  WHERE l.from_article_id != ? -- target ID
  GROUP BY l.from_article_id
),
SELECT articles.title, ic.similarity, ic.similarity as helper
FROM intersection_count ic
INNER JOIN articles ON ic.id = articles.id
ORDER BY ic.similarity DESC
LIMIT 1000;