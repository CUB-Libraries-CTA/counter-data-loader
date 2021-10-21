DROP DATABASE IF EXISTS counter5;
CREATE DATABASE counter5 DEFAULT CHARACTER SET utf8mb4;
USE counter5;

CREATE TABLE title_report (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(400) NOT NULL,
    title_type CHAR(1) NOT NULL,
    publisher VARCHAR(200) NULL,
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
    INDEX (title(50)),
    INDEX (publisher(50)),
    INDEX (title(50), publisher(50), platform_id),
    FOREIGN KEY (platform_id) REFERENCES platform_ref (id)
);
  
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
    INDEX (period),
    INDEX (title_report_id ASC),
    FOREIGN KEY (title_report_id) REFERENCES title_report (id)
);

CREATE TABLE filter (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(250) DEFAULT NULL,
  params VARCHAR(500) NOT NULL,
  title_type CHAR(1) NOT NULL,
  created_date DATETIME NOT NULL,
  updated_date DATETIME NOT NULL,
  owner VARCHAR(10) NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE report_inventory (
	id INT NOT NULL AUTO_INCREMENT,
    excel_name VARCHAR(100) NOT NULL,
    platform VARCHAR(100) NOT NULL,
    begin_date DATE NOT NULL,
    end_date DATE NOT NULL,
    row_cnt INT NOT NULL,
    load_date DATETIME NOT NULL,
    PRIMARY KEY (id),
    INDEX (platform, begin_date, end_date)
);

CREATE TABLE platform_ref (
    id INT NOT NULL,
    alt_id INT NULL,
    name VARCHAR(100) NOT NULL,
    preferred_name VARCHAR(100) NOT NULL,
    has_faq TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
);

CREATE TABLE title_report_journal_mview (
    id INT AUTO_INCREMENT,
    title_report_id INT,
    metric_id INT,
    title VARCHAR(400),
    title_type CHAR(1),
    platform VARCHAR(100),
    publisher VARCHAR(200),
    doi VARCHAR(100),
    proprietary_id VARCHAR(100),
    print_issn VARCHAR(15),
    online_issn VARCHAR(15),
    uri VARCHAR(200),
    status CHAR(1),
    access_type ENUM('Controlled','OA_Gold','Other_Free_To_Read'),
    metric_type ENUM('Total_Item_Investigations','Total_Item_Requests','Unique_Item_Investigations',
        'Unique_Item_Requests','Unique_Title_Investigations','Unique_Title_Requests','Limit_Exceeded',
        'No_License'),
    period DATE,
    period_total INT,
    INDEX (title_report_id),
    INDEX (platform),
    INDEX (publisher),
    INDEX (period),
    PRIMARY KEY (id)
);

CREATE TABLE title_report_book_mview (
    id INT AUTO_INCREMENT,
    title_report_id INT,
    metric_id INT,
    title VARCHAR(400),
    title_type CHAR(1),
    platform VARCHAR(100),
    publisher VARCHAR(200),
    doi VARCHAR(100),
    proprietary_id VARCHAR(100),
    isbn VARCHAR(20),
    print_issn VARCHAR(15),
    online_issn VARCHAR(15),
    uri VARCHAR(200),
    yop VARCHAR(4),
    status CHAR(1),
    access_type ENUM('Controlled','OA_Gold','Other_Free_To_Read'),
    metric_type ENUM('Total_Item_Investigations','Total_Item_Requests','Unique_Item_Investigations',
        'Unique_Item_Requests','Unique_Title_Investigations','Unique_Title_Requests','Limit_Exceeded',
        'No_License'),
    period DATE,
    period_total INT,
    INDEX (title_report_id),
    INDEX (platform),
    INDEX (publisher),
    INDEX (period),
    PRIMARY KEY (id)
);
