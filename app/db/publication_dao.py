import re
from dotenv import load_dotenv
import os
load_dotenv()
from app.models.publication import Publication
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

COLLETION_NAME = os.getenv("COLLETION_NAME")

class PublicationDAO:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection: AsyncIOMotorCollection = db[COLLETION_NAME]

    async def get_publication(self, publication: Publication):
        print("Buscando...")
        
        filters = {} #tttt
        
        def is_valid_param(param):
            return param is not None and param != ""
        
        if  is_valid_param(publication.type):
            filters["type"] = publication.type
            
        if is_valid_param(publication.acronym):
            filters["acronym"] = publication.acronym
        
        if is_valid_param(publication.year):
            try:
                filters["year"] = int(publication.year)
            except (ValueError, TypeError):
                print(f"Ano inválido fornecido: {publication.year}")
        
        if is_valid_param(publication.number):
            number = self.clean_and_convert_number(publication.number)
            filters["number"] = number    
        
                
        pipeline = []
        
        if is_valid_param(publication.name):
            pipeline.append({
                "$search": {
                    "index": "default",
                    "phrase": {
                    "query": publication.name,
                    "path": [
                        "content",
                        "ordinance",
                        "responsible",
                        "organ"
                    ],
                    "slop": 2
}
                }
            })
            
        if filters: 
            pipeline.append({
                "$match": filters
            })
            
        pipeline.append({
            "$sort": {
                "date": -1
            }
        })
        
        pipeline.append({
            "$project": {
                "_id": 0,
                "acronym": 1,
                "institute": 1,
                "ordinance": 1,
                "type": 1,
                "tags": 1,
                "date": 1,
                "year": 1,
                "url": 1,
                "score": {
                    "$meta": "searchScore"
                }
            }
        })
        
        
        if not pipeline or (
            len(pipeline) == 2 and "$sort" in pipeline[0]
        ): 
            print("Nenhum parametro fornecido")
            cursor = (
                self.collection
                .find({})
                .sort("date", -1)
                .limit(10)
            )
            
            res = await cursor.to_list(length=None)
            total_count = len(res)

        else:

            cursor = self.collection.aggregate(pipeline)

            res = await cursor.to_list(length=None)

            total_count = len(res)

        return res, total_count
    
    def clean_and_convert_number(self, number) -> str:
        content = str(number)
        result = re.sub(r'[^\d]', '', content)
        
        return result