DROP DATABASE IF EXISTS counter5;
CREATE DATABASE counter5 DEFAULT CHARACTER SET latin1;
USE counter5;

CREATE TABLE title_report (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(400) NOT NULL,
    title_type CHAR(1) NOT NULL,
    publisher VARCHAR(100) NOT NULL,
    publisher_id VARCHAR(50) NULL,
    platform_id INT NOT NULL,
    doi VARCHAR(100) NULL,
    proprietary_id VARCHAR(100) NULL,
    isbn VARCHAR(20) NULL,
    print_issn VARCHAR(15) NULL,
    online_issn VARCHAR(15) NULL,
    uri VARCHAR(200) NULL,
    yop VARCHAR(4) NULL,
    status CHAR(1) NULL,
    PRIMARY KEY (id),
    INDEX TITLE_IDX (title)
    INDEX PUBLISHER_IDX (publisher)
    INDEX STATUS_IDX (status));
  
CREATE TABLE metric (
    id INT NOT NULL AUTO_INCREMENT,
    title_report_id INT NOT NULL,
    access_type ENUM('Controlled','OA_Gold','Other_Free_To_Read') DEFAULT NULL,
    metric_type ENUM('Total_Item_Investigations','Total_Item_Requests','Unique_Item_Investigations',
        'Unique_Item_Requests','Unique_Title_Investigations','Unique_Title_Requests','Limit_Exceeded',
        'No_License') DEFAULT NULL,
    period DATE NOT NULL,
    period_total INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    INDEX PERIOD_IDX (period),
    INDEX TITLE_REPORT_ID_IDX (title_report_id ASC),
    CONSTRAINT TITLE_REPORT_ID_FK
        FOREIGN KEY (title_report_id)
        REFERENCES title_report (id));

CREATE TABLE filter (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(250) DEFAULT NULL,
  params VARCHAR(500) NOT NULL,
  created_date DATETIME NOT NULL,
  updated_date DATETIME NOT NULL,
  owner VARCHAR(10) NOT NULL,
  PRIMARY KEY (id));

CREATE TABLE platform_ref (
    id INT NOT NULL,
    alt_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    alias VARCHAR(100) NULL,
    preferred_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (id));

CREATE VIEW title_report_view AS (
    SELECT
        (t.id + m.id) AS id,
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
    ORDER BY
        m.period_total DESC,
        t.title ASC
);
