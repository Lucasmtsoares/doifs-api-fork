import re
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

    async def get_publication(self, publication: Publication):
        print("Buscando...")
        
        match_query = {}
        
        def is_valid_param(param):
            return param is not None and param != ""
        
        if  is_valid_param(publication.type):
            match_query["type"] = publication.type
        
        if is_valid_param(publication.year):
            try:
                match_query["year"] = int(publication.year)
            except (ValueError, TypeError):
                print(f"Ano inválido fornecido: {publication.year}")
                
        if is_valid_param(publication.institute):
                match_query["institute"] = publication.institute
                
        if is_valid_param(publication.name):
                search_pattern = re.escape(publication.name)
                match_query["content"] = {
                    "$regex": search_pattern,
                    "$options": "i"
                }
                
        total_count = await self.colletion.count_documents(match_query)
        
        cursor = None
                
        if not match_query:
            print("Nenhum parâmetro de busca fornecido. Retornando os 10 mais recentes.") 
            cursor = self.colletion.find({}).sort("date", -1).limit(10)
            
        else:   
            pipeline = [
                
                {
                    "$match": match_query
                },
                
                {
                    "$sort": {"date": -1}
                },
                
                {
                    "$project": {
                        "_id": 0,
                        "institute": 1,
                        "concierge": 1,
                        "type": 1,
                        "date": 1,
                        "url": 1
                    }
                }
            ]
            cursor = self.colletion.aggregate(pipeline)
        
        res = await cursor.to_list(None)
        
        for doc in res:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
                
        if not match_query:
            total_count = len(res) 
                
        return res, total_count
        
