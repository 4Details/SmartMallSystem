"""
添加示例商品数据脚本
"""
from app import create_app
from app.models import db
from app.models.product import Product
import random
import uuid

app = create_app()

# 示例商品数据
sample_products = [
    {
        "name": "无线蓝牙耳机",
        "description": "高品质无线蓝牙耳机，支持降噪功能，续航时间长达8小时。",
        "points_price": 2000,
        "cash_price": 199.00,
        "stock": 50,
        "category": "电子产品",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTUywI7b55qCPCadANkfrr3tXVA_ZvYrpHVEA&s"
    },
    {
        "name": "智能手环",
        "description": "多功能智能手环，支持心率监测、睡眠分析、运动追踪等功能。",
        "points_price": 1500,
        "cash_price": 149.00,
        "stock": 30,
        "category": "电子产品",
        "image_url": "https://gw.alicdn.com/imgextra/i3/2201415823401/O1CN013O9t9V1azhzfplGLN_!!2-item_pic.png_468x468Q75.jpg_.webp"
    },
    {
        "name": "便携式移动电源",
        "description": "大容量便携式移动电源，10000mAh，支持快充，轻巧便携。",
        "points_price": 1000,
        "cash_price": 99.00,
        "stock": 100,
        "category": "电子产品",
        "image_url": "https://www.canadadz.com/wp-content/uploads/2023/09/2023110518034852.jpg"
    },
    {
        "name": "多功能按摩枕",
        "description": "舒适的多功能按摩枕，缓解颈部和背部疲劳，提供舒适的按摩体验。",
        "points_price": 1200,
        "cash_price": 119.00,
        "stock": 20,
        "category": "家居用品",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRe7MLiUwws5CWSVuLmgxkQSGaDTPevpF89SQ&s"
    },
    {
        "name": "高级保温杯",
        "description": "不锈钢高级保温杯，保温效果好，容量500ml，适合办公室和户外使用。",
        "points_price": 800,
        "cash_price": 79.00,
        "stock": 80,
        "category": "家居用品",
        "image_url": "https://gw.alicdn.com/imgextra/i2/4009389495/O1CN01gv8fPd2K0lZU2JXkX_!!2-item_pic.png_.webp"
    },
    {
        "name": "时尚太阳镜",
        "description": "时尚设计的太阳镜，UV400防紫外线，适合户外活动和日常使用。",
        "points_price": 1000,
        "cash_price": 99.00,
        "stock": 40,
        "category": "服装配饰",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRYI16MRGSbTsmJy2I3MDV2TdVzGbPTJNVzgA&s"
    },
    {
        "name": "精致手表",
        "description": "精致设计的石英手表，防水30米，适合日常佩戴和商务场合。",
        "points_price": 2500,
        "cash_price": 249.00,
        "stock": 15,
        "category": "服装配饰",
        "image_url": "https://s.alicdn.com/@sc04/kf/H2267b96c155f4d2f81245195747123e9L.jpg_720x720q50.jpg"
    },
    {
        "name": "护肤套装",
        "description": "高品质护肤套装，包含洁面乳、爽肤水、精华液和面霜，适合各种肤质。",
        "points_price": 1800,
        "cash_price": 179.00,
        "stock": 25,
        "category": "美妆护肤",
        "image_url": "https://edge.dis.commercecloud.salesforce.com/dw/image/v2/BKBN_PRD/on/demandware.static/-/Sites-catalog_master_sfcc_krs/default/dwedbd5030/images/large/3425003843_1_b.jpg?sw=768&sh=768&sm=fit"
    },
    {
        "name": "有机茶叶礼盒",
        "description": "精选有机茶叶礼盒，包含绿茶、红茶和乌龙茶，送礼自用两相宜。",
        "points_price": 1200,
        "cash_price": 119.00,
        "stock": 35,
        "category": "食品饮料",
        "image_url": "https://gw.alicdn.com/imgextra/bao/upload/O1CN01aosPlm1q940DP5psF_!!6000000005452-2-yinhe.png_.webp"
    },
    {
        "name": "畅销小说集",
        "description": "精选畅销小说集，包含多本热门小说，适合文学爱好者。",
        "points_price": 1500,
        "cash_price": 149.00,
        "stock": 30,
        "category": "图书音像",
        "image_url": "https://imgt.bookschina.com/2024/3/9262385ct01.jpg"
    },
    {
        "name": "瑜伽垫",
        "description": "环保材质瑜伽垫，防滑耐用，厚度适中，适合各种瑜伽练习。",
        "points_price": 600,
        "cash_price": 59.00,
        "stock": 50,
        "category": "其他",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTv37OBB7l30Z3BZMCyUjJqmw_44NyYG3bPag&s"
    },
    {
        "name": "旅行箱",
        "description": "耐用轻便的旅行箱，容量大，带TSA锁，适合商务和休闲旅行。",
        "points_price": 3000,
        "cash_price": 299.00,
        "stock": 10,
        "category": "其他",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJlMy0Vq_QkZWWKDnSAinaYyXoMIGEIPI90A&s"
    }
]

def add_sample_products():
    """添加示例商品数据到数据库"""
    with app.app_context():
        # 检查数据库中是否已有商品
        # existing_count = Product.query.count()
        # if existing_count > 0:
        #     print(f"数据库中已有 {existing_count} 个商品，跳过添加示例商品")
        #     return

        # 添加示例商品
        for product_data in sample_products:
            product = Product(
                name=product_data["name"],
                description=product_data["description"],
                points_price=product_data["points_price"],
                cash_price=product_data["cash_price"],
                stock=product_data["stock"],
                category=product_data["category"],
                image_url=product_data["image_url"]
            )
            db.session.add(product)

        # 提交事务
        db.session.commit()
        print(f"成功添加 {len(sample_products)} 个示例商品")

if __name__ == "__main__":
    add_sample_products()