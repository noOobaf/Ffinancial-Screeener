from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongo(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]

    async def close_mongo_connection(self):
        if self.client:
            self.client.close()

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

db = MongoDB()

async def get_database():
    return db.db

async def connect_to_mongo():
    await db.connect_to_mongo()

async def close_mongo_connection():
    await db.close_mongo_connection()