WITH targets AS (
	SELECT from_article_id as article_id
	FROM links
	WHERE to_article_id = ?
),
target_count AS (
	Select Count(*) as num
	From targets
),
intersections AS (
	SELECT
		links.to_article_id AS article_id,
		COUNT(*) AS num
	FROM links
	WHERE links.to_article_id != ?
		and links.from_article_id in targets
	GROUP BY links.to_article_id
),
unions AS (
	SELECT l.to_article_id as article_id, COUNT(*) + tc.num AS num
	FROM (
		SELECT to_article_id, from_article_id
		FROM links
		WHERE to_article_id != ?
			and from_article_id not in targets -- remove double counts
	) l
	INNER JOIN target_count as tc on true
	GROUP BY l.to_article_id
),
jaccard_similarity AS (
	SELECT ic.article_id as id,
		ic.num as intersections,
		uc.num as unions,
		(CAST(ic.num AS FLOAT) / uc.num) AS similarity
	FROM intersections ic
	JOIN unions uc ON ic.article_id = uc.article_id
)
SELECT articles.title, js.similarity, (js.intersections || '/' || js.unions) as helper
FROM jaccard_similarity js
INNER JOIN articles ON js.id = articles.id
ORDER BY js.similarity DESC, js.unions DESC
LIMIT 1000;