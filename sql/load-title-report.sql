-- Loads the title_report table from the R4 database.
--
-- The data for this table is derived from both the publisher
-- and publication tables in the R4 database. Because the platform
-- ID's have changed, the correponding reference table contains
-- the R4 ID's as a lookup for the revised ID.

USE counter5;

-- Create  a temporary column in title_report to store the R4
-- publication ID which will be needed when loading metric data.
ALTER TABLE title_report ADD alt_id INT AFTER id;

-- Load the title_report table
INSERT INTO title_report
SELECT
    NULL AS id,
    n.id AS alt_id,
    n.title AS title,
    'J' AS title_type,
    r.name AS publisher,
    '' AS publisher_id,
    (SELECT id FROM platform_ref WHERE alt_id = r.platform_id) AS platform_id,
    n.journal_doi AS doi,
    n.proprietary_id AS proprietary_id,
    '' AS isbn,
    n.print_issn AS print_issn,
    n.online_issn AS online_issn,
    '' AS uri,
    '' AS yop,
    '' AS status
FROM
    counter.publication n
JOIN
    counter.publisher r ON r.id = n.publisher_id;
