-- Drop index statements for all tables

-- platform_ref  table
DROP INDEX idx_preferred_name ON platform_ref;

-- title_report table
DROP INDEX idx_title_type ON title_report;
DROP INDEX idx_title_type_publisher ON title_report;
DROP INDEX idx_title_type_title ON title_report;

-- metric table
DROP INDEX idx_title_type_period ON metric;
DROP INDEX idx_all_cols ON metric;
