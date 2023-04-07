CREATE TEMPORARY TABLE temp_article_links AS
SELECT DISTINCT
  al.from_article_id,
  COALESCE(ar.to_article_id, al.to_article_id) AS to_article_id
FROM
  links al
  LEFT JOIN redirects ar ON al.to_article_id = ar.from_article_id;

BEGIN;
DELETE FROM links;
INSERT INTO links (from_article_id, to_article_id)
SELECT from_article_id, to_article_id FROM temp_article_links;
COMMIT;

DROP TABLE temp_article_links;