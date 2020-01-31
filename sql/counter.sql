-- Database for COUNTER Reporting Project

-- -----------------------------------------------------
-- Database counter
-- -----------------------------------------------------
CREATE DATABASE counter
  CHARACTER SET = utf8;

USE counter;

-- -----------------------------------------------------
-- Table platform
-- -----------------------------------------------------
CREATE TABLE platform (
  id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  PRIMARY KEY (id));

-- -----------------------------------------------------
-- Table publisher
-- -----------------------------------------------------
CREATE TABLE publisher (
  id INT NOT NULL,
  name VARCHAR(200) NOT NULL,
  platform_id INT NOT NULL,
  PRIMARY KEY (id));

-- -----------------------------------------------------
-- Table publication
-- -----------------------------------------------------
CREATE TABLE publication (
  id INT NOT NULL,
  publisher_id INT NOT NULL,
  title VARCHAR(400) NOT NULL,
  print_issn VARCHAR(15) NULL,
  online_issn VARCHAR(15) NULL,
  journal_doi VARCHAR(100) NULL,
  proprietary_id VARCHAR(100) NULL,
  PRIMARY KEY (id),
  INDEX PUBLISHER_ID_IDX (publisher_id ASC),
  CONSTRAINT PUBLISHER_ID_FK
    FOREIGN KEY (publisher_id)
    REFERENCES publisher (id));

-- -----------------------------------------------------
-- Table usage_stat
-- -----------------------------------------------------
CREATE TABLE usage_stat (
  id INT NOT NULL,
  publication_id INT NOT NULL,
  period DATE NOT NULL,
  requests INT NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  INDEX PUBLICATION_ID_IDX (publication_id ASC),
  CONSTRAINT PUBLICATION_ID_FK
    FOREIGN KEY (publication_id)
    REFERENCES publication (id));

-- -----------------------------------------------------
-- Table filter
-- -----------------------------------------------------
CREATE TABLE filter (
  id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(250) DEFAULT NULL,
  params VARCHAR(500) NOT NULL,
  created_date DATETIME NOT NULL,
  updated_date DATETIME NOT NULL,
  owner VARCHAR(10) NOT NULL,
  PRIMARY KEY (id));

-- -----------------------------------------------------
-- View counter_result_detail
-- -----------------------------------------------------
CREATE VIEW counter_result_detail AS (
  SELECT
    (((m.id + p.id) + j.id) + u.id) AS id,
    j.title AS title,
    p.name AS publisher,
    m.name AS platform,
    j.print_issn AS print_issn,
    j.online_issn AS online_issn,
    j.journal_doi AS journal_doi,
    j.proprietary_id AS proprietary_id,
    u.period AS period,
    u.requests AS requests
  FROM
    (((publication j JOIN publisher p ON j.publisher_id = p.id)
    JOIN usage_stat u ON j.id = u.publication_id)
    JOIN platform m ON p.platform_id = m.id)
);
