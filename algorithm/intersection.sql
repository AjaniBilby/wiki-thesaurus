WITH targets AS (
	SELECT to_article_id as article_id
	FROM links
	WHERE from_article_id = ? -- target ID
),
intersections AS (
	SELECT
		links.to_article_id AS article_id,
		COUNT(*) AS num
	FROM links
	WHERE links.to_article_id in targets
	GROUP BY links.from_article_id
),
jaccard_similarity AS (
	SELECT ic.article_id as id,
		ic.num as intersections,
		uc.num as unions,
		(CAST(ic.num AS FLOAT) / uc.num) AS similarity
	FROM intersections ic
	Inner JOIN unions uc ON ic.article_id = uc.article_id
)
SELECT articles.title, ic.num, ic.num
FROM intersections ic
INNER JOIN articles ON ic.article_id = articles.id
ORDER BY ic.num DESC
LIMIT 1000;