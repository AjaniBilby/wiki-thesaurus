WITH target_links AS (
  SELECT to_article_id
  FROM links
  WHERE from_article_id = ? -- replace ? with the target ID
),
intersection_count AS (
  SELECT l.from_article_id, COUNT(*) AS intersection
  FROM links l
  JOIN target_links tl ON l.to_article_id = tl.to_article_id
  WHERE l.from_article_id != ? -- replace ? with the target ID
  GROUP BY l.from_article_id
),
union_count AS (
  SELECT l.from_article_id, COUNT(*) AS union_count
  FROM (
    SELECT from_article_id, to_article_id
    FROM links
    WHERE from_article_id != ? -- replace ? with the target ID
    UNION
    SELECT ? AS from_article_id, to_article_id -- replace ? with the target ID
    FROM target_links
  ) l
  GROUP BY l.from_article_id
),
jaccard_similarity AS (
  SELECT ic.from_article_id as id,
         (CAST(ic.intersection AS FLOAT) / uc.union_count) AS similarity
  FROM intersection_count ic
  JOIN union_count uc ON ic.from_article_id = uc.from_article_id
)
SELECT articles.title, jaccard_similarity.similarity
FROM jaccard_similarity
INNER JOIN articles ON jaccard_similarity.id = articles.id
ORDER BY similarity DESC
LIMIT 20;