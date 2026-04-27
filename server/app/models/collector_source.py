from datetime import datetime
import uuid


def create_collector_source(data: dict) -> dict:
    from app import db

    source_id = f"src_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()

    source = {
        "sourceId": source_id,
        "sourceCode": data.get("sourceCode"),
        "sourceName": data.get("sourceName"),
        "platform": data.get("platform"),
        "sourceType": data.get("sourceType", "url"),
        "entryUrl": data.get("entryUrl"),
        "parserCode": data.get("parserCode"),
        "config": data.get("config", {}),
        "status": "enabled",
        "isDeleted": False,
        "createdBy": data.get("createdBy"),
        "updatedBy": data.get("updatedBy"),
        "createdAt": now,
        "updatedAt": now
    }

    db.collector_sources.insert_one(source)
    return source


def update_collector_source(source_id: str, data: dict) -> None:
    from app import db

    update_data = {k: v for k, v in data.items()
                   if k not in ["sourceId", "sourceCode", "isDeleted"]}
    update_data["updatedAt"] = datetime.now().isoformat()

    db.collector_sources.update_one(
        {"sourceId": source_id},
        {"$set": update_data}
    )
