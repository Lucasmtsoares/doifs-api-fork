from dotenv import load_dotenv
import os
load_dotenv()

from app.db.connection_db import Connection
import asyncio
from app.models.publication import Publication
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

COLLETION_NAME = os.getenv("COLLETION_NAME")

class PublicationDAO:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.colletion: AsyncIOMotorCollection = db[COLLETION_NAME]

    async def get_publication(self, publication):
        print("Buscando...")
        
        pipeline = [
            {
                "$match": {
                    "type": publication.type,
                    "year": publication.year
                }
            }
        ]
        
        res = await self.colletion.aggregate(pipeline).to_list(None)
        
        
        
        
        
        
        
        
    
# execução


"""
#publication = Publicaton("REINALDO RAFAEL DE ALBUQUERQUE PEREIRA JUNIOR", "IFAL", type=None, year=None)
        
        
filter = {
            **({"content": {"$regex": publication.name , "$options": "i"}} if publication.name else {}),
            **({"type": publication.type} if publication.type else {}),
            **({"year": publication.year} if publication.year else {})
        }
        if not publication.institute:
            return {"erro": "Instituto é obrigatório"}
        
        colletion = self.db.list_collections()
        print("SAIDA >>>> ", colletion)
        
        collection = self.db[publication.institute]
        cursor = collection.find(filter, {"_id": 0, "institute": 1, "type": 1, "concierge": 1, "date": 1, "url": 1})
        res = await cursor.to_list(length=100)
"""