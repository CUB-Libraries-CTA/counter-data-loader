-- Loads the view tables (materialized views)
--
-- The materialized views provide improved performance
-- when filtering data from the database.

USE counter5;

INSERT INTO title_report_book_mview
    SELECT
        NULL,
        t.id AS title_report_id,
        m.id AS metric_id,
        t.title AS title,
        t.title_type AS title_type,
        p.preferred_name AS platform,
        t.publisher AS publisher,
        t.doi AS doi,
        t.proprietary_id AS proprietary_id,
        t.isbn AS isbn,
        t.print_issn AS print_issn,
        t.online_issn AS online_issn,
        t.uri AS uri,
        t.yop AS yop,
        t.status AS status,
        m.access_type AS access_type,
        m.metric_type AS metric_type,
        m.period as period,
        m.period_total AS period_total
    FROM
        title_report t
    JOIN
        metric m ON m.title_report_id = t.id
    JOIN
        platform_ref p ON p.id = t.platform_id
    WHERE
        t.title_type = 'B'
    ORDER BY
        m.period_total DESC,
        m.period ASC,
        t.title ASC;
