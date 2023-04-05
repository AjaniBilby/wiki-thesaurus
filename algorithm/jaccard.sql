WITH target_links AS (
  SELECT to_article_id
  FROM links
  WHERE from_article_id = ? -- target ID
),
intersection_count AS (
  SELECT l.from_article_id, COUNT(*) AS intersections
  FROM links l
  INNER JOIN target_links tl ON
    l.to_article_id = tl.to_article_id
  WHERE l.from_article_id != ? -- target ID
  GROUP BY l.from_article_id
),
union_count AS (
  SELECT l.from_article_id, COUNT(*) AS unions
  FROM (
    SELECT from_article_id, to_article_id
    FROM links
    WHERE from_article_id != ? -- target ID
    UNION
    SELECT ? AS from_article_id, to_article_id -- target ID
    FROM target_links
  ) l
  GROUP BY l.from_article_id
),
jaccard_similarity AS (
  SELECT ic.from_article_id as id,
    ic.intersections,
    uc.unions,
    (CAST(ic.intersections AS FLOAT) / uc.unions) AS similarity
  FROM intersection_count ic
  JOIN union_count uc ON ic.from_article_id = uc.from_article_id
)
SELECT articles.title, js.similarity, (js.intersections || '/' || js.unions) as helper
FROM jaccard_similarity js
INNER JOIN articles ON js.id = articles.id
ORDER BY js.similarity DESC
LIMIT 1000;