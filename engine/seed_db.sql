-- Economies Baseline (2024 Estimates)
INSERT INTO economies (id, name, gdp_usd_bn) VALUES
('USA', 'United States', 29000.0),
('CHN', 'China', 18800.0),
('SGP', 'Singapore', 547.0),
('MYS', 'Malaysia', 400.0),
('VNM', 'Vietnam', 400.0),
('JPN', 'Japan', 4200.0),
('DEU', 'Germany', 4500.0),
('GBR', 'United Kingdom', 3300.0),
('FRA', 'France', 3000.0),
('IND', 'India', 3900.0),
('IDN', 'Indonesia', 1400.0),
('KOR', 'South Korea', 1700.0),
('AUS', 'Australia', 1700.0)
ON CONFLICT (id) DO UPDATE SET gdp_usd_bn = EXCLUDED.gdp_usd_bn;

-- Industry Definitions (ISIC Rev 4)
INSERT INTO industries (id, name, category) VALUES
('D26', 'Computer, electronic and optical products', 'Manufacturing'),
('D27', 'Electrical equipment', 'Manufacturing'),
('D28', 'Machinery and equipment n.e.c.', 'Manufacturing'),
('D29', 'Motor vehicles, trailers and semi-trailers', 'Manufacturing'),
('D01T03', 'Agriculture, forestry and fishing', 'Primary'),
('D05T09', 'Mining and quarrying', 'Primary'),
('D64T66', 'Financial and insurance activities', 'Services'),
('D61', 'Telecommunications', 'Services'),
('D62T63', 'IT and other information services', 'Services')
ON CONFLICT (id) DO NOTHING;

-- Comprehensive Trade Matrix (Value Added Flows)
-- Corridor: China -> USA
INSERT INTO trade_matrix (source_econ_id, target_econ_id, industry_id, value_added_usd_mn) VALUES
('CHN', 'USA', 'D26', 80000.0), -- Electronics (Domestic VA)
('SGP', 'CHN', 'D26', 5000.0),  -- SG Components in CN Electronics
('CHN', 'USA', 'D27', 45000.0), -- Electrical Equipment (Domestic VA)
('SGP', 'CHN', 'D27', 2500.0),  -- SG Components in CN Electrical Equipment
('CHN', 'USA', 'D01T03', 12000.0), -- Agriculture (Domestic VA)
('VNM', 'CHN', 'D01T03', 800.0)    -- VN Raw Materials in CN Ag Exports
ON CONFLICT (source_econ_id, target_econ_id, industry_id) DO UPDATE 
SET value_added_usd_mn = EXCLUDED.value_added_usd_mn;

-- Corridor: Auto Sector (Global)
INSERT INTO trade_matrix (source_econ_id, target_econ_id, industry_id, value_added_usd_mn) VALUES
('JPN', 'USA', 'D29', 35000.0), -- Japan Domestic VA in Auto Exports to US
('DEU', 'USA', 'D29', 28000.0), -- Germany Domestic VA in Auto Exports to US
('KOR', 'JPN', 'D29', 4200.0)    -- Korea Components in Japanese Cars
ON CONFLICT (source_econ_id, target_econ_id, industry_id) DO UPDATE 
SET value_added_usd_mn = EXCLUDED.value_added_usd_mn;

-- Corridor: Southeast Asia & Resources
INSERT INTO trade_matrix (source_econ_id, target_econ_id, industry_id, value_added_usd_mn) VALUES
('IDN', 'USA', 'D01T03', 15000.0), -- Indonesia Agriculture VA in exports to USA
('IDN', 'CHN', 'D05T09', 22000.0), -- Indonesia Mining VA in exports to China
('AUS', 'IDN', 'D05T09', 1200.0),   -- Australian Mining resources in Indonesian Exports
('MYS', 'USA', 'D26', 25000.0),    -- Malaysia Electronics VA in exports to USA
('SGP', 'MYS', 'D26', 3200.0)      -- SG Components in Malaysian Electronics
ON CONFLICT (source_econ_id, target_econ_id, industry_id) DO UPDATE 
SET value_added_usd_mn = EXCLUDED.value_added_usd_mn;
