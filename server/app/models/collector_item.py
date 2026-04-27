from datetime import datetime
import uuid


def create_collector_item(data: dict) -> dict:
    from app import db

    item_id = f"item_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()

    item = {
        "itemId": item_id,
        "taskId": data.get("taskId"),
        "platform": data.get("platform"),
        "sourceUrl": data.get("sourceUrl"),
        "sourceProductId": data.get("sourceProductId"),
        "dedupeKey": data.get("dedupeKey"),
        "title": data.get("title"),
        "subTitle": data.get("subTitle"),
        "description": data.get("description"),
        "mainImageUrl": data.get("mainImageUrl"),
        "imageUrls": data.get("imageUrls", []),
        "priceMin": data.get("priceMin"),
        "priceMax": data.get("priceMax"),
        "currency": data.get("currency"),
        "supplierName": data.get("supplierName"),
        "supplierUrl": data.get("supplierUrl"),
        "shopName": data.get("shopName"),
        "rawData": data.get("rawData", {}),
        "normalizedData": data.get("normalizedData", {}),
        "parseStatus": data.get("parseStatus", "pending"),
        "createdAt": now,
        "updatedAt": now
    }

    db.collector_items.insert_one(item)
    return item
