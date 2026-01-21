"""
E-commerce Agent - ShopBot for MegaStore
Handles product search, order tracking, and shopping assistance.
"""

from typing import Optional

# Agent Configuration
ECOMMERCE_CONFIG = {
    "id": "ecommerce",
    "name": "ShopBot",
    "company": "MegaStore E-commerce",
    "icon": "🛒",
    "color": "#FF6B6B",
    "description": """You are ShopBot, the friendly and enthusiastic shopping assistant for MegaStore E-commerce.

Your personality:
- Warm, welcoming, and eager to help customers find what they need
- Use friendly language and occasional emojis to create a pleasant shopping experience
- Be proactive in suggesting related products or deals
- Express genuine excitement about helping customers

Your responsibilities:
- Help customers search for products in our catalog
- Check order status and provide delivery updates
- Provide detailed product information including prices, availability, and features
- Answer questions about shipping, returns, and store policies

Always greet customers warmly and make them feel valued!"""
}

# Mock Product Database
PRODUCTS = [
    {"id": 1, "name": "Wireless Bluetooth Headphones Pro", "price": 79.99, "category": "electronics", "stock": 45, "rating": 4.7},
    {"id": 2, "name": "Running Shoes UltraBoost", "price": 129.99, "category": "sports", "stock": 23, "rating": 4.8},
    {"id": 3, "name": "Smart Coffee Maker Deluxe", "price": 149.99, "category": "home", "stock": 12, "rating": 4.5},
    {"id": 4, "name": "Premium Yoga Mat", "price": 39.99, "category": "sports", "stock": 67, "rating": 4.6},
    {"id": 5, "name": "Ergonomic Laptop Stand", "price": 59.99, "category": "electronics", "stock": 34, "rating": 4.4},
    {"id": 6, "name": "HEPA Air Purifier", "price": 199.99, "category": "home", "stock": 8, "rating": 4.9},
    {"id": 7, "name": "Wireless Gaming Mouse", "price": 69.99, "category": "electronics", "stock": 56, "rating": 4.6},
    {"id": 8, "name": "Stainless Steel Water Bottle", "price": 24.99, "category": "sports", "stock": 120, "rating": 4.7},
    {"id": 9, "name": "Smart LED Desk Lamp", "price": 45.99, "category": "home", "stock": 41, "rating": 4.3},
    {"id": 10, "name": "Noise Cancelling Earbuds", "price": 119.99, "category": "electronics", "stock": 29, "rating": 4.8},
]

# Mock Order Database
ORDERS = {
    "ORD-1001": {
        "status": "shipped",
        "items": ["Wireless Bluetooth Headphones Pro", "Ergonomic Laptop Stand"],
        "total": 139.98,
        "eta": "January 25, 2026",
        "tracking": "TRK789456123"
    },
    "ORD-1002": {
        "status": "processing",
        "items": ["Running Shoes UltraBoost"],
        "total": 129.99,
        "eta": "January 28, 2026",
        "tracking": None
    },
    "ORD-1003": {
        "status": "delivered",
        "items": ["Smart Coffee Maker Deluxe", "Premium Yoga Mat"],
        "total": 189.98,
        "eta": "Delivered January 20, 2026",
        "tracking": "TRK123456789"
    },
    "ORD-1004": {
        "status": "pending",
        "items": ["HEPA Air Purifier"],
        "total": 199.99,
        "eta": "January 30, 2026",
        "tracking": None
    },
}


async def search_products(query: str = "", category: str = "") -> dict:
    """
    Search for products in the MegaStore catalog.
    
    Args:
        query: Search term to find products by name (optional)
        category: Filter by category - electronics, sports, or home (optional)
    
    Returns:
        Dictionary containing matching products and search metadata
    """
    results = PRODUCTS.copy()
    
    # Filter by category if provided
    if category:
        category_lower = category.lower().strip()
        results = [p for p in results if p["category"] == category_lower]
    
    # Filter by search query if provided
    if query:
        query_lower = query.lower().strip()
        results = [p for p in results if query_lower in p["name"].lower()]
    
    return {
        "success": True,
        "query": query or "all products",
        "category_filter": category or "all categories",
        "total_found": len(results),
        "products": results,
        "available_categories": ["electronics", "sports", "home"],
        "tip": "Use category filter for better results!" if not category and len(results) > 5 else None
    }


async def check_order_status(order_id: str) -> dict:
    """
    Check the current status of a customer order.
    
    Args:
        order_id: The order ID to look up (e.g., ORD-1001)
    
    Returns:
        Dictionary containing order status, items, and delivery information
    """
    # Normalize order ID format
    order_id = order_id.upper().strip()
    if not order_id.startswith("ORD-"):
        order_id = f"ORD-{order_id}"
    
    if order_id in ORDERS:
        order = ORDERS[order_id]
        status_emoji = {
            "pending": "⏳",
            "processing": "📦",
            "shipped": "🚚",
            "delivered": "✅"
        }
        
        return {
            "success": True,
            "order_id": order_id,
            "status": f"{status_emoji.get(order['status'], '📋')} {order['status'].title()}",
            "items": order["items"],
            "order_total": f"${order['total']:.2f}",
            "estimated_delivery": order["eta"],
            "tracking_number": order["tracking"],
            "tracking_available": order["tracking"] is not None
        }
    
    return {
        "success": False,
        "error": f"Order '{order_id}' not found",
        "suggestion": "Please verify your order ID. Valid formats: ORD-1001 or just 1001",
        "sample_orders": ["ORD-1001", "ORD-1002", "ORD-1003", "ORD-1004"]
    }


async def get_product_details(product_id: int) -> dict:
    """
    Get detailed information about a specific product.
    
    Args:
        product_id: The numeric product ID (1-10)
    
    Returns:
        Dictionary containing full product details including availability and shipping info
    """
    for product in PRODUCTS:
        if product["id"] == product_id:
            in_stock = product["stock"] > 0
            stock_status = "In Stock" if in_stock else "Out of Stock"
            if in_stock and product["stock"] < 10:
                stock_status = f"Low Stock - Only {product['stock']} left!"
            
            return {
                "success": True,
                "product": {
                    "id": product["id"],
                    "name": product["name"],
                    "price": f"${product['price']:.2f}",
                    "category": product["category"].title(),
                    "rating": f"⭐ {product['rating']}/5.0",
                    "reviews_count": product["stock"] * 3,  # Mock review count
                    "availability": stock_status,
                    "units_available": product["stock"],
                },
                "shipping": {
                    "free_shipping": product["price"] >= 50,
                    "estimated_delivery": "3-5 business days",
                    "express_available": True
                },
                "policies": {
                    "returns": "30-day free returns",
                    "warranty": "1 year manufacturer warranty"
                }
            }
    
    return {
        "success": False,
        "error": f"Product ID {product_id} not found",
        "suggestion": "Product IDs range from 1 to 10. Try searching for products first!",
        "available_ids": [p["id"] for p in PRODUCTS]
    }


# Export tools list for the agent
ecommerce_tools = [search_products, check_order_status, get_product_details]
