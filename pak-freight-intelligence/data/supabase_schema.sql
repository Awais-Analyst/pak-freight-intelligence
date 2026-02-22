-- Pakistan Freight Intelligence Platform - Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Raw scraped data (internal use only, not exposed publicly)
CREATE TABLE IF NOT EXISTS raw_listings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    source VARCHAR(50), -- 'olx', 'pakwheels', 'facebook'
    origin_city VARCHAR(100),
    destination_city VARCHAR(100),
    vehicle_type VARCHAR(100),
    load_weight VARCHAR(50),
    price_pkr INTEGER,
    phone_hash VARCHAR(255), -- hashed for privacy
    scraped_at TIMESTAMP DEFAULT NOW(),
    raw_data JSONB -- original scraped data
);

-- 2. Aggregated daily rates (publicly exposed)
CREATE TABLE IF NOT EXISTS daily_rates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    origin_city VARCHAR(100),
    destination_city VARCHAR(100),
    vehicle_category INTEGER, -- 1: Mini-Truck, 2: Bedford, 3: 20ft, 4: 40ft
    median_rate_pkr INTEGER,
    avg_rate_pkr INTEGER,
    sample_size INTEGER,
    date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(origin_city, destination_city, vehicle_category, date)
);

-- 3. Fuel prices
CREATE TABLE IF NOT EXISTS fuel_prices (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    diesel_price_pkr DECIMAL(10,2),
    date DATE,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date)
);

-- 4. Toll rates (manually updated)
CREATE TABLE IF NOT EXISTS toll_rates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    motorway VARCHAR(50),
    vehicle_category INTEGER,
    toll_pkr INTEGER,
    effective_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Route cache (from openrouteservice)
CREATE TABLE IF NOT EXISTS route_cache (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    origin VARCHAR(200),
    destination VARCHAR(200),
    distance_km DECIMAL(10,2),
    duration_hours DECIMAL(10,2),
    route_data JSONB,
    cached_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(origin, destination)
);

-- 6. Exchange rates
CREATE TABLE IF NOT EXISTS exchange_rates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    usd_to_pkr DECIMAL(10,2),
    date DATE,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date)
);

-- 7. ML model predictions
CREATE TABLE IF NOT EXISTS predictions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    origin_city VARCHAR(100),
    destination_city VARCHAR(100),
    vehicle_category INTEGER,
    predicted_rate_pkr INTEGER,
    confidence_interval_lower INTEGER,
    confidence_interval_upper INTEGER,
    prediction_date DATE,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. Chat sessions (AI agent)
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id VARCHAR(255),
    user_message TEXT,
    bot_response TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- 9. User contributions (CSV uploads)
CREATE TABLE IF NOT EXISTS user_contributions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    origin_city VARCHAR(100),
    destination_city VARCHAR(100),
    vehicle_type VARCHAR(100),
    rate_pkr INTEGER,
    date DATE,
    contributor_hash VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_daily_rates_route_date ON daily_rates(origin_city, destination_city, date);
CREATE INDEX idx_daily_rates_vehicle ON daily_rates(vehicle_category);
CREATE INDEX idx_raw_listings_scraped ON raw_listings(scraped_at);
CREATE INDEX idx_predictions_route ON predictions(origin_city, destination_city, vehicle_category);

-- Insert sample toll data
INSERT INTO toll_rates (motorway, vehicle_category, toll_pkr, effective_date) VALUES
('M-2', 1, 3730, '2025-08-01'), -- Mini-Truck
('M-2', 2, 5595, '2025-08-01'), -- Bedford
('M-2', 3, 6525, '2025-08-01'), -- 20ft
('M-2', 4, 7460, '2025-08-01'), -- 40ft
('M-1', 1, 2800, '2025-08-01'),
('M-1', 2, 4200, '2025-08-01'),
('M-1', 3, 4900, '2025-08-01'),
('M-1', 4, 5600, '2025-08-01');