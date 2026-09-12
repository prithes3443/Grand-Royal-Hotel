-- =======================================================
-- GRAND ROYAL HOTEL - RESTAURANT & FOOD BILLING SYSTEM
-- MySQL Database Initialization Script
-- =======================================================

CREATE DATABASE IF NOT EXISTS grand_royal_hotel;
USE grand_royal_hotel;

-- Drop tables in reverse order of foreign keys
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS foods;
DROP TABLE IF EXISTS users;

-- 1. USERS TABLE
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'staff',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. FOODS TABLE
CREATE TABLE foods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    food_type VARCHAR(20) NOT NULL, -- 'Veg' or 'Non-Veg'
    image VARCHAR(255),
    rating DECIMAL(2, 1) DEFAULT 4.5,
    is_available BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. ORDERS TABLE
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(100) NOT NULL,
    table_number VARCHAR(50) NOT NULL,
    order_type VARCHAR(50) NOT NULL, -- 'Dine-In' or 'Parcel / Takeaway'
    subtotal DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    gst DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    grand_total DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL, -- 'Cash', 'Card', 'UPI / GPay'
    status VARCHAR(50) DEFAULT 'Completed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. ORDER_ITEMS TABLE
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    food_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. BILLS TABLE
CREATE TABLE bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bill_number VARCHAR(50) NOT NULL UNIQUE,
    order_id INT NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    table_number VARCHAR(50) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    gst DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    grand_total DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- SAMPLE DATA INSERTION
-- =======================================================

-- Users (passwords hashed with Werkzeug generate_password_hash)
-- admin: admin123
-- staff: staff123
INSERT INTO users (username, password_hash, full_name, role) VALUES 
('admin', 'scrypt:32768:8:1$4rbe27pIFM0S58DB$e712897fa07d2dc1e9650c75efa463235fdfd84dde94cbcca6bc805107f296ed595b4e8b2d3de04afd07c40a20a47c8efd56e7f4f0c126abdb967113086dcd58', 'Restaurant General Manager', 'admin'),
('staff', 'scrypt:32768:8:1$EtlAmOvAhpSrm53H$1a726ee0f1fa76669836d6a499fe354833cd4785c2f4c2914e7f083da1dc7f2a6ee7573e88add1c710617ea9f52085ca0df7f4df1a4d49f7545e617921293c73', 'Front Desk Staff', 'staff');

-- 38 Food Items across all categories
INSERT INTO foods (name, category, description, price, food_type, image, rating, is_available) VALUES
-- Tiffin
('Steaming Hot Idly', 'Tiffin', 'Soft, fluffy steamed rice cakes served with sambar and 3 chutneys', 60.00, 'Veg', 'idly.jpg', 4.8, 1),
('Crispy Medu Vada', 'Tiffin', 'Deep-fried crispy lentil doughnuts seasoned with pepper and curry leaves', 60.00, 'Veg', 'medu_vada.jpg', 4.7, 1),
('Ven Pongal', 'Tiffin', 'Ghee tempered hot rice and moong dal porridge with cashews and peppercorns', 80.00, 'Veg', 'idly.jpg', 4.6, 1),
('Poori Masala', 'Tiffin', 'Fluffy deep-fried golden wheat pooris served with spiced potato masala', 85.00, 'Veg', 'samosa.jpg', 4.5, 1),

-- Dosa
('Crispy Ghee Roast Dosa', 'Dosa', 'Thin, golden crispy crepe roasted in pure desi ghee served with chutneys', 110.00, 'Veg', 'dosa.jpg', 4.9, 1),
('Masala Dosa', 'Dosa', 'Classic crispy crepe folded with spiced potato & onion filling', 100.00, 'Veg', 'dosa.jpg', 4.8, 1),
('Onion Rava Dosa', 'Dosa', 'Lacy semolina crepe studded with diced onions, green chilies, and coriander', 120.00, 'Veg', 'dosa.jpg', 4.6, 1),
('Paneer Butter Dosa', 'Dosa', 'Rich crispy dosa generously filled with spiced shredded paneer and butter', 150.00, 'Veg', 'dosa.jpg', 4.7, 1),

-- Biryani
('Special Chicken Biryani', 'Biryani', 'Aromatic basmati rice cooked with tender marinated chicken pieces and rich spices', 240.00, 'Non-Veg', 'biryani.jpg', 4.9, 1),
('Mutton Dum Biryani', 'Biryani', 'Traditional slow-cooked dum biryani with succulent mutton cubes & aromatic herbs', 300.00, 'Non-Veg', 'biryani.jpg', 4.8, 1),
('Royal Veg Biryani', 'Biryani', 'Fragrant basmati rice layered with garden-fresh vegetables and saffron essence', 180.00, 'Veg', 'biryani.jpg', 4.5, 1),
('Egg Dum Biryani', 'Biryani', 'Flavor-packed dum biryani served with roasted seasoned boiled eggs and gravy', 200.00, 'Non-Veg', 'biryani.jpg', 4.6, 1),

-- Noodles
('Chicken Hakka Noodles', 'Noodles', 'Wok-tossed noodles with shredded chicken, crisp cabbage, capsicum and scallions', 190.00, 'Non-Veg', 'noodles.jpg', 4.7, 1),
('Veg Hakka Noodles', 'Noodles', 'Stir-fried noodles with fresh julienned vegetables and mild Chinese seasonings', 150.00, 'Veg', 'noodles.jpg', 4.5, 1),
('Schezwan Chicken Noodles', 'Noodles', 'Spicy wok-tossed noodles tossed in fiery home-made Schezwan chili paste', 210.00, 'Non-Veg', 'noodles.jpg', 4.8, 1),
('Veg Schezwan Noodles', 'Noodles', 'Spicy wok noodles tossed with crunchy vegetables in hot garlic sauce', 170.00, 'Veg', 'noodles.jpg', 4.4, 1),

-- Parotta
('Malabar Flaky Parotta', 'Parotta', 'Multi-layered flaky, soft Kerala style parottas served with salna gravy', 80.00, 'Veg', 'parotta.jpg', 4.8, 1),
('Veg Kothu Parotta', 'Parotta', 'Shredded flaky parotta stir-fried on a griddle with vegetables and spices', 150.00, 'Veg', 'parotta.jpg', 4.6, 1),
('Chicken Kothu Parotta', 'Parotta', 'Iconic street food delicacy: shredded parotta scrambled with eggs, chicken & gravy', 200.00, 'Non-Veg', 'parotta.jpg', 4.9, 1),

-- Samosa
('Crispy Punjabi Samosa', 'Samosa', 'Crisp, golden pastry crust stuffed with savory spiced potato and peas filling (2 pcs)', 50.00, 'Veg', 'samosa.jpg', 4.7, 1),
('Samosa Chaat', 'Samosa', 'Crushed samosas topped with spicy chole, sweetened yogurt, tamarind and mint chutney', 80.00, 'Veg', 'samosa.jpg', 4.8, 1),

-- Starters
('Chicken 65', 'Starters', 'Crispy, deep-fried spicy boneless chicken morsels coated in Southern spices', 170.00, 'Non-Veg', 'chicken65.jpg', 4.8, 1),
('Tandoori Chicken (Half)', 'Starters', 'Clay-oven charcoal roasted chicken marinated in yogurt and tandoori masala', 280.00, 'Non-Veg', 'tandoori.jpg', 4.9, 1),
('Chicken Lollipop', 'Starters', 'Crisp seasoned winglets tossed in sweet spicy Schezwan sauce with scallions', 220.00, 'Non-Veg', 'chicken65.jpg', 4.7, 1),
('Crispy Paneer 65', 'Starters', 'Tender cottage cheese cubes tossed in spicy yogurt batter with curry leaves', 160.00, 'Veg', 'paneer.jpg', 4.6, 1),
('Gobi Manchurian Dry', 'Starters', 'Crisp cauliflower florets tossed with garlic, ginger, soya and green chillies', 140.00, 'Veg', 'paneer.jpg', 4.5, 1),

-- Main Course
('Paneer Butter Masala', 'Main Course', 'Succulent cottage cheese cubes simmered in a silky, buttery tomato cream gravy', 180.00, 'Veg', 'paneer.jpg', 4.9, 1),
('Butter Naan', 'Main Course', 'Soft tandoori leavened flatbread brushed with generous dairy butter', 45.00, 'Veg', 'parotta.jpg', 4.7, 1),
('Royal Chicken Curry', 'Main Course', 'Traditional home-style chicken curry infused with roasted aromatic spices', 220.00, 'Non-Veg', 'chicken65.jpg', 4.8, 1),
('Chettinad Mutton Curry', 'Main Course', 'Fiery spiced mutton gravy with freshly stone-ground Chettinad spices', 290.00, 'Non-Veg', 'biryani.jpg', 4.7, 1),

-- Rice
('Veg Fried Rice', 'Rice', 'Wok-tossed basmati rice with finely chopped garden vegetables and soy sauce', 140.00, 'Veg', 'friedrice.jpg', 4.5, 1),
('Egg Fried Rice', 'Rice', 'Fluffy rice tossed with scrambled farm eggs, spring onions, and pepper', 160.00, 'Non-Veg', 'friedrice.jpg', 4.6, 1),
('Chicken Fried Rice', 'Rice', 'Classic Asian style fried rice tossed with juicy diced chicken and vegetables', 180.00, 'Non-Veg', 'friedrice.jpg', 4.8, 1),

-- Desserts
('Gulab Jamun (2 pcs)', 'Desserts', 'Soft melt-in-mouth milk solids dumplings soaked in rose cardamom sugar syrup', 80.00, 'Veg', 'desserts.jpg', 4.8, 1),
('Royal Ice Cream Sundae', 'Desserts', 'Triple scoop ice cream topped with chocolate fudge sauce, nuts and a cherry', 110.00, 'Veg', 'desserts.jpg', 4.7, 1),

-- Drinks
('South Indian Filter Coffee', 'Drinks', 'Freshly brewed decoction coffee frothed with creamy hot milk in brass davarah', 40.00, 'Veg', 'coffee.jpg', 4.9, 1),
('Masala Chai', 'Drinks', 'Invigorating Indian tea brewed with crushed ginger, cardamom, and whole spices', 35.00, 'Veg', 'coffee.jpg', 4.8, 1),
('Fresh Lime Soda', 'Drinks', 'Refreshing chilled sparkling soda mixed with fresh lemon juice and mint', 60.00, 'Veg', 'coffee.jpg', 4.6, 1),
('Mango Milkshake', 'Drinks', 'Thick creamy milkshake prepared with sweet Alphonso mango pulp and vanilla ice cream', 120.00, 'Veg', 'desserts.jpg', 4.8, 1);

-- Sample initial order and bill for immediate demonstration
INSERT INTO orders (order_number, customer_name, table_number, order_type, subtotal, discount, gst, grand_total, payment_method, status, created_by) VALUES
('ORD-1001', 'Ramesh Kumar', 'Table 4', 'Dine-In', 590.00, 59.00, 26.55, 557.55, 'UPI / GPay', 'Completed', 'staff');

INSERT INTO order_items (order_id, food_id, quantity, price, total) VALUES
(1, 9, 2, 240.00, 480.00),  -- 2x Special Chicken Biryani
(1, 5, 1, 110.00, 110.00);  -- 1x Ghee Roast Dosa

INSERT INTO bills (bill_number, order_id, customer_name, table_number, subtotal, discount, gst, grand_total, payment_method) VALUES
('BILL-1001', 1, 'Ramesh Kumar', 'Table 4', 590.00, 59.00, 26.55, 557.55, 'UPI / GPay');
