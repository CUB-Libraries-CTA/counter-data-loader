-- Index statements for all tables
--
-- platform_ref table
CREATE INDEX idx_preferred_name ON platform_ref (preferred_name);

-- title_report table
CREATE INDEX idx_title_type ON title_report (title_type);
CREATE INDEX idx_title_type_publisher ON title_report (title_type, publisher(50));
CREATE INDEX idx_title_type_title ON title_report (title_type, title(50));

-- metric table
CREATE INDEX idx_title_type_period ON metric (title_type, period);
CREATE INDEX idx_all_cols ON metric (title_type, metric_type, access_type, period, period_total);
