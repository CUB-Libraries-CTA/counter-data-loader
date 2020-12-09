-- ----------------------------------------------------------------------------
-- Database schema for COUNTER Reporting Tool
--
-- Usage: This script can either be executed in the shell or when logged
--        into the database server with mysql. In both cases, the database
--        must exist beforehand but be completely empty (no table/view
--        definitions).
--
-- Revision History
-- ----------------------------------------------------------------------------
-- 1.0 2019-12-01 FS Initial release
-- 1.1 2020-12-18 FS Add assigned_id column to publisher table
--                   Add uri, status columns to publication table
--                   Modify journal_doi column name to doi
--                   Modify usage_stat table name to item_request
--                   Add request_total, request_unique columns to item_request
--                   Modify counter_result_detail view name to publication_usage
--                   Add request_total, request_unique columns to view

-- ----------------------------------------------------------------------------
-- platform table
-- ----------------------------------------------------------------------------

CREATE TABLE platform (
  id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  PRIMARY KEY (id));

-- ----------------------------------------------------------------------------
-- publisher table
-- ----------------------------------------------------------------------------

CREATE TABLE publisher (
  id INT NOT NULL,
  name VARCHAR(200) NOT NULL,
  assigned_id VARCHAR(100) NOT NULL,
  platform_id INT NOT NULL,
  PRIMARY KEY (id));

-- ----------------------------------------------------------------------------
-- publication table
-- ----------------------------------------------------------------------------

CREATE TABLE publication (
  id INT NOT NULL,
  publisher_id INT NOT NULL,
  title VARCHAR(400) NOT NULL,
  print_issn VARCHAR(15) NULL,
  online_issn VARCHAR(15) NULL,
  doi VARCHAR(100) NULL,
  proprietary_id VARCHAR(100) NULL,
  uri VARCHAR(200) NULL,
  status CHAR(1) NULL,
  PRIMARY KEY (id),
  INDEX PUBLISHER_ID_IDX (publisher_id ASC),
  CONSTRAINT PUBLISHER_ID_FK
    FOREIGN KEY (publisher_id)
    REFERENCES publisher (id));

-- ----------------------------------------------------------------------------
-- item_request table
-- ----------------------------------------------------------------------------

CREATE TABLE item_request (
  id INT NOT NULL,
  publication_id INT NOT NULL,
  period DATE NOT NULL,
  request_total INT NOT NULL DEFAULT 0,
  request_unique INT NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  INDEX PUBLICATION_ID_IDX (publication_id ASC),
  CONSTRAINT PUBLICATION_ID_FK
    FOREIGN KEY (publication_id)
    REFERENCES publication (id));

-- ----------------------------------------------------------------------------
-- filter table
-- ----------------------------------------------------------------------------

CREATE TABLE filter (
  id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(250) DEFAULT NULL,
  params VARCHAR(500) NOT NULL,
  created_date DATETIME NOT NULL,
  updated_date DATETIME NOT NULL,
  owner VARCHAR(10) NOT NULL,
  PRIMARY KEY (id));

-- ----------------------------------------------------------------------------
-- publication_usage view
-- ----------------------------------------------------------------------------

CREATE VIEW publication_usage AS (
  SELECT
    (((m.id + p.id) + j.id) + r.id) AS id,
    j.title AS title,
    p.name AS publisher,
    m.name AS platform,
    j.print_issn AS print_issn,
    j.online_issn AS online_issn,
    j.doi AS doi,
    j.proprietary_id AS proprietary_id,
    j.status AS status,
    r.period AS period,
    r.request_total AS request_total,
    r.request_unique AS request_unique
  FROM
    (((publication j JOIN publisher p ON j.publisher_id = p.id)
    JOIN item_request r ON j.id = r.publication_id)
    JOIN platform m ON p.platform_id = m.id)
);
