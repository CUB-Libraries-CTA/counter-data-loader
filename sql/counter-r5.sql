DROP DATABASE IF EXISTS counter5;
CREATE DATABASE counter5 DEFAULT CHARACTER SET utf8mb4;
USE counter5;

CREATE TABLE platform_ref (
    id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    preferred_name VARCHAR(100) NOT NULL,
    has_faq TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
);

CREATE TABLE title_report (
    id INT AUTO_INCREMENT,
    title VARCHAR(400) NOT NULL,
    title_type CHAR(1) NOT NULL,
    publisher VARCHAR(200) NULL,
    publisher_id VARCHAR(50) NULL,
    platform_id INT NOT NULL,
    doi VARCHAR(100) NULL,
    proprietary_id VARCHAR(200) NULL,
    isbn VARCHAR(20) NULL,
    print_issn VARCHAR(20) NULL,
    online_issn VARCHAR(20) NULL,
    uri VARCHAR(200) NULL,
    yop VARCHAR(4) NULL,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_dupe_check (title(50), publisher(50), platform_id, isbn, yop),
    FOREIGN KEY fk_platform_id (platform_id) REFERENCES platform_ref (id)
);

CREATE TABLE title_report_temp (
    id INT AUTO_INCREMENT,
    title VARCHAR(400),
    title_type CHAR(1),
    publisher VARCHAR(200),
    publisher_id VARCHAR(50),
    platform VARCHAR(100),
    doi VARCHAR(100),
    proprietary_id VARCHAR(200),
    isbn VARCHAR(20),
    print_issn VARCHAR(20),
    online_issn VARCHAR(20),
    uri VARCHAR(200),
    yop VARCHAR(4),
    excel_name VARCHAR(100),
    row_num INT,
    title_report_id INT,
    PRIMARY KEY (id),
    UNIQUE INDEX idx_excel_name_row_num (excel_name, row_num)
);

CREATE TABLE metric (
    id INT AUTO_INCREMENT,
    title_report_id INT NOT NULL,
    title_type CHAR(1) NOT NULL,
    access_type ENUM('Controlled','OA_Gold','Other_Free_To_Read') NOT NULL,
    metric_type ENUM('Total_Item_Investigations','Total_Item_Requests','Unique_Item_Investigations',
        'Unique_Item_Requests','Unique_Title_Investigations','Unique_Title_Requests','Limit_Exceeded',
        'No_License') NOT NULL,
    period DATE NOT NULL,
    period_total INT NOT NULL DEFAULT 0,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE INDEX idx_dupe_check (title_report_id, access_type, metric_type, period),
    FOREIGN KEY fk_title_report_id (title_report_id) REFERENCES title_report (id)
);

CREATE TABLE metric_temp (
    id INT AUTO_INCREMENT,
    title_report_id INT,
    title_type CHAR(1),
    access_type INT,
    metric_type INT,
    period DATE,
    period_total INT,
    excel_name VARCHAR(100),
    row_num INT,
    PRIMARY KEY (id)
);

CREATE TABLE filter (
    id INT AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(250) DEFAULT NULL,
    params VARCHAR(500) NOT NULL,
    title_type CHAR(1) NOT NULL,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    owner VARCHAR(10) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE report_inventory (
	id INT AUTO_INCREMENT,
    excel_name VARCHAR(100) NOT NULL,
    platform VARCHAR(100) NOT NULL,
    run_date DATE NOT NULL,
    begin_date DATE NOT NULL,
    end_date DATE NOT NULL,
    row_cnt INT NOT NULL,
    load_start DATETIME NOT NULL,
    load_end DATETIME NOT NULL,
    load_date DATE NOT NULL,
    PRIMARY KEY (id),
    UNIQUE INDEX idx_platform_begin_end (platform, begin_date, end_date, row_cnt)
);
