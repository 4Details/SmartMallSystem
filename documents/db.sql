-- 创建UUID扩展（如果使用PostgreSQL）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    avatar_url VARCHAR(255),
    address JSONB,
    preferences JSONB,
    membership_level_id UUID REFERENCES membership_levels(id)
);

-- 积分交易表
CREATE TABLE points_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    points INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    related_entity_id UUID,
    related_entity_type VARCHAR(50),
    is_expired BOOLEAN DEFAULT false,
    CONSTRAINT points_check CHECK (points != 0)
);

-- 商品表
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    points_price INTEGER NOT NULL,
    cash_price DECIMAL(10,2),
    stock INTEGER NOT NULL DEFAULT 0,
    image_url VARCHAR(255),
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    attributes JSONB,
    currency_id UUID REFERENCES currencies(id),
    CONSTRAINT positive_prices CHECK (points_price >= 0 AND cash_price >= 0),
    CONSTRAINT positive_stock CHECK (stock >= 0)
);

-- 订单表
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    total_points INTEGER NOT NULL DEFAULT 0,
    total_cash DECIMAL(10,2) NOT NULL DEFAULT 0,
    shipping_address JSONB NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    currency_id UUID REFERENCES currencies(id),
    CONSTRAINT positive_totals CHECK (total_points >= 0 AND total_cash >= 0)
);

-- 订单项表
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id),
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    points_price INTEGER NOT NULL,
    cash_price DECIMAL(10,2),
    status VARCHAR(50) NOT NULL,
    CONSTRAINT positive_quantity CHECK (quantity > 0),
    CONSTRAINT positive_item_prices CHECK (points_price >= 0 AND cash_price >= 0)
);

-- 物流表
CREATE TABLE logistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL UNIQUE REFERENCES orders(id),
    tracking_number VARCHAR(100),
    carrier VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    shipped_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    tracking_history JSONB
);

-- 促销活动表
CREATE TABLE promotions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    promotion_type VARCHAR(50) NOT NULL,
    rules JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT valid_dates CHECK (end_date > start_date)
);

-- 通知表
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notification_type VARCHAR(50) NOT NULL,
    related_entity_id UUID,
    related_entity_type VARCHAR(50),
    announcement_id UUID REFERENCES announcements(id)
);

-- 公告表
CREATE TABLE announcements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    importance VARCHAR(20) DEFAULT 'normal',
    CONSTRAINT valid_announcement_dates CHECK (expires_at > published_at)
);

-- 用户行为表
CREATE TABLE user_behaviors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    behavior_type VARCHAR(50) NOT NULL,
    data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- 角色表
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 权限表
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL
);

-- 系统设置表
CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 会员等级表
CREATE TABLE membership_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    required_points INTEGER NOT NULL,
    benefits JSONB,
    color_code VARCHAR(7),
    CONSTRAINT positive_required_points CHECK (required_points >= 0)
);

-- 会员权益表
CREATE TABLE benefits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    membership_level_id UUID NOT NULL REFERENCES membership_levels(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    benefit_type VARCHAR(50) NOT NULL,
    value JSONB NOT NULL
);

-- FAQ表
CREATE TABLE faq (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category_id UUID REFERENCES categories(id),
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT true
);

-- 分类表
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER NOT NULL DEFAULT 0
);

-- 语言表
CREATE TABLE languages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(5) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    native_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    flag_image VARCHAR(255)
);

-- 货币表
CREATE TABLE currencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(3) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(5) NOT NULL,
    exchange_rate DECIMAL(10,6) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT positive_exchange_rate CHECK (exchange_rate > 0)
);

-- 支付表
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id),
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    transaction_id VARCHAR(100),
    payment_details JSONB,
    CONSTRAINT positive_amount CHECK (amount > 0)
);

-- 用户角色关联表
CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id),
    role_id UUID NOT NULL REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- 角色权限关联表
CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id),
    permission_id UUID NOT NULL REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);

-- 商品活动关联表
CREATE TABLE product_promotions (
    product_id UUID NOT NULL REFERENCES products(id),
    promotion_id UUID NOT NULL REFERENCES promotions(id),
    PRIMARY KEY (product_id, promotion_id)
);

-- 创建索引
CREATE INDEX idx_points_transactions_user_id ON points_transactions(user_id);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_user_behaviors_user_id ON user_behaviors(user_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_benefits_membership_level_id ON benefits(membership_level_id);
CREATE INDEX idx_faq_category_id ON faq(category_id);

-- 创建触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要自动更新updated_at的表创建触发器
CREATE TRIGGER update_user_modtime
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_modtime
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_order_modtime
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_modtime
    BEFORE UPDATE ON payments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();