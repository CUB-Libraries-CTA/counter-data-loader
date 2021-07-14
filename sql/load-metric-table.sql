-- Loads corresponding metrics for items in title_report
--
-- Data for this table is derived from the R4 usage_stat table.
-- Each row in the R4 table has a publication ID (FK) linking
-- usage data to a specific publication in the title_report
-- table.
--
-- Some differences from the R4 usage_stat table:
--   * access_type column defaults to 'Controlled' for all R4 data
--   * metric_type defaults to 'Total_Item_Requests' for all R4 data
--
-- The above defaults will vary when loading R5 data.

USE counter5;

-- Load the metric table
INSERT INTO metric
SELECT
    NULL AS id,
    t.id AS title_report_id,
    1 AS access_type,
    2 AS metric_type,
    u.period AS period,
    u.requests AS period_total
FROM
    counter.usage_stat u
JOIN
    title_report t ON t.alt_id = u.publication_id;

-- Last step is to drop the alt_id column in the title_report table
ALTER TABLE title_report DROP alt_id;
