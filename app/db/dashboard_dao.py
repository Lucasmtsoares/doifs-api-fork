from dotenv import load_dotenv
import os
load_dotenv()

from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

COLLETION_NAME = os.getenv("COLLETION_NAME")

class DashboardDAO:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.colletion: AsyncIOMotorCollection = db[COLLETION_NAME]
        
        # Lista exata de tipos solicitados
        self.type_mapping = {
            "Nomeação": "total_nomeação",
            "Exoneração": "total_exoneração",
            "Afastamento": "total_afastamento",
            "Aposentadoria": "total_aposentadoria",
            "Pensão": "total_pensão",
            "Demissão": "total_demissão",
            "Dispensa": "total_dispensa",
            "Designação": "total_designação",
            "Substituição": "total_substituição"
        }
        self.target_types = list(self.type_mapping.keys())

    def _get_pivot_stage(self):
        """Mapeia dinamicamente os tipos de atos para as chaves de retorno do frontend."""
        return {
            "nomeacoes": {"$sum": {"$cond": [{"$eq": ["$type", "Nomeação"]}, 1, 0]}},
            "exoneracoes": {"$sum": {"$cond": [{"$eq": ["$type", "Exoneração"]}, 1, 0]}},
            "afastamentos": {"$sum": {"$cond": [{"$eq": ["$type", "Afastamento"]}, 1, 0]}},
            "aposentadorias": {"$sum": {"$cond": [{"$eq": ["$type", "Aposentadoria"]}, 1, 0]}},
            "pensoes": {"$sum": {"$cond": [{"$eq": ["$type", "Pensão"]}, 1, 0]}},
            "demissoes": {"$sum": {"$cond": [{"$eq": ["$type", "Demissão"]}, 1, 0]}},
            "dispensas": {"$sum": {"$cond": [{"$eq": ["$type", "Dispensa"]}, 1, 0]}},
            "designacoes": {"$sum": {"$cond": [{"$eq": ["$type", "Designação"]}, 1, 0]}},
            "substituicoes": {"$sum": {"$cond": [{"$eq": ["$type", "Substituição"]}, 1, 0]}},
            "outros": {"$sum": {"$cond": [{"$eq": ["$type", "Outros"]}, 1, 0]}},
            "total_acts": {"$sum": 1}
        }

    def _get_geo_mapping_project(self):
        """
        Mapeia siglas para nomes extensos (já que state_name e region_name não existem no banco).
        Ajuste os nomes conforme sua necessidade.
        """
        return {
            "uf": "$_id.uf",
            "region": "$_id.region",
            "year": "$_id.year",
            "state_name": {
                "$switch": {
                    "branches": [
                        {"case": {"$eq": ["$_id.uf", "AC"]}, "then": "Acre"},
                        {"case": {"$eq": ["$_id.uf", "AL"]}, "then": "Alagoas"},
                        {"case": {"$eq": ["$_id.uf", "BA"]}, "then": "Bahia"},
                        # Adicionar os demais conforme necessário...
                    ],
                    "default": "$_id.uf"
                }
            },
            "region_name": {
                 "$switch": {
                    "branches": [
                        {"case": {"$eq": ["$_id.region", "norte"]}, "then": "Norte"},
                        {"case": {"$eq": ["$_id.region", "nordeste"]}, "then": "Nordeste"},
                        {"case": {"$eq": ["$_id.region", "sul"]}, "then": "Sul"},
                    ],
                    "default": "$_id.region"
                }
            },
            "nomeacoes": 1, "exoneracoes": 1, "afastamentos": 1, "aposentadorias": 1, 
            "pensoes": 1, "demissoes": 1, "dispensas": 1, "designacoes": 1, "substituicoes": 1
        }

    async def get_type_counts_last_month(self): # OK --------
        """Item 8: Totais do último mês."""
        last_month = datetime.now() - timedelta(days=30)
        pipeline = [
            {"$match": {"$expr": {"$gte": [{"$toDate": "$date"}, last_month]}}},
            {"$group": {"_id": None, **self._get_pivot_stage()}},
            {"$project": {"_id": 0}}
        ]
        res = await self.colletion.aggregate(pipeline).to_list(1)
        return res[0] if res else {}
    
    async def get_total_by_type_all_time(self):
        """Totais individuais por tipo de todos os anos."""
        pipeline = [
            {"$match": {"type": {"$in": self.target_types}}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        cursor = self.colletion.aggregate(pipeline)
        totals = {}
        async for doc in cursor:
            key = self.type_mapping.get(doc["_id"], doc["_id"].lower())
            totals[key] = doc["count"]
        
        for target in self.target_types:
            key = self.type_mapping[target]
            if key not in totals:
                totals[key] = 0
                
        return totals
    
    async def get_monthly_totals(self):

        pipeline = [

            # 1️⃣ Criar número do mês para ordenação cronológica
            {
                "$addFields": {
                    "month_number": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$month", "Jan"]}, "then": 1},
                                {"case": {"$eq": ["$month", "Fev"]}, "then": 2},
                                {"case": {"$eq": ["$month", "Mar"]}, "then": 3},
                                {"case": {"$eq": ["$month", "Abr"]}, "then": 4},
                                {"case": {"$eq": ["$month", "Mai"]}, "then": 5},
                                {"case": {"$eq": ["$month", "Jun"]}, "then": 6},
                                {"case": {"$eq": ["$month", "Jul"]}, "then": 7},
                                {"case": {"$eq": ["$month", "Ago"]}, "then": 8},
                                {"case": {"$eq": ["$month", "Set"]}, "then": 9},
                                {"case": {"$eq": ["$month", "Out"]}, "then": 10},
                                {"case": {"$eq": ["$month", "Nov"]}, "then": 11},
                                {"case": {"$eq": ["$month", "Dez"]}, "then": 12},
                            ],
                            "default": 0
                        }
                    }
                }
            },

            # 2️⃣ Agrupar por ano + mês
            {
                "$group": {
                    "_id": {
                        "year": "$year",
                        "month": "$month",
                        "month_number": "$month_number"
                    },
                    "total": {"$sum": 1}
                }
            },

            # 3️⃣ Ordenar cronologicamente
            {
                "$sort": {
                    "_id.year": 1,
                    "_id.month_number": 1
                }
            },

            # 4️⃣ Formatar saída final
            {
                "$project": {
                    "_id": 0,
                    "year": "$_id.year",
                    "month": "$_id.month",
                    "total": 1
                }
            }
        ]

        return await self.colletion.aggregate(pipeline).to_list(None)


    async def get_periodic_type_counts(self):
        """
        Retorna as contagens agrupadas por dia para o gráfico do frontend.
        Garante exatamente o número de registros (days) preenchendo lacunas com zero.
        """
        # 1. Preparação do intervalo de datas
        days = 90
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days - 1)
        
        # Strings para o filtro do MongoDB (formato YYYY-MM-DD)
        start_date_str = start_date.strftime("%Y-%m-%d")
        
        # 2. Agregação no MongoDB
        pipeline = [
            {
                "$match": {
                    "type": {"$in": self.target_types},
                    "date": {"$gte": start_date_str}
                }
            },
            {
                "$group": {
                    "_id": "$date",
                    **self._get_pivot_stage()
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        db_cursor = self.colletion.aggregate(pipeline)
        db_results = await db_cursor.to_list(length=None)
        
        # Mapa para busca rápida: { "2023-10-01": { dados } }
        results_map = {item["_id"]: item for item in db_results}
        
        # 3. Construção da lista final com Backfilling
        final_data = []
        for i in range(days):
            # Gera cada data individualmente no intervalo
            current_dt = start_date + timedelta(days=i)
            date_str = current_dt.strftime("%Y-%m-%d")
            
            if date_str in results_map:
                # Se existe no banco, aproveita os dados
                entry = results_map[date_str]
                entry["date"] = date_str
                entry.pop("_id", None) # Remove o _id para limpar o objeto
                final_data.append(entry)
            else:
                # Se não existe, cria um registro "vazio" (zerado)
                final_data.append({
                    "date": date_str,
                    "total_acts": 0,
                    "nomeacoes": 0,
                    "exoneracoes": 0,
                    "afastamentos": 0,
                    "aposentadorias": 0,
                    "pensoes": 0,
                    "demissoes": 0,
                    "dispensas": 0,
                    "designacoes": 0,
                    "substituicoes": 0
                })
        
        return final_data
        

    async def get_institutes_overview(self):
        """Item 2: Acronym e Institute (extenso)."""
        pipeline = [
            {
                "$group": {
                    "_id": {"acronym": "$acronym", "institute": "$institute", "year": "$year", "month": "$month"},
                    **self._get_pivot_stage()
                }
            },
            {"$project": {"_id": 0, "acronym": "$_id.acronym", "institute": "$_id.institute", "year": "$_id.year", "month": "$_id.month", "nomeacoes": 1, "exoneracoes": 1, "afastamentos": 1, "aposentadorias": 1, "pensoes": 1, "demissoes": 1, "dispensas": 1, "designacoes": 1, "substituicoes": 1}}
        ]
        return await self.colletion.aggregate(pipeline).to_list(None)

    async def get_region_totals(self):

        pipeline = [

            # 1️⃣ Criar campo region_name baseado na sigla
            {
                "$addFields": {
                    "region_name": {
                        "$switch": {
                            "branches": [
                                {"case": {"$in": ["$acronym", ["IFAC", "IFAP", "IFAM", "IFPA", "IFRO", "IFRR", "IFTO"]]}, "then": "Norte"},
                                {"case": {"$in": ["$acronym", ["IFAL", "IFBA", "IF Baiano", "IFCE", "IFMA", "IFPB", "IFPE", "IF Sertão PE", "IFPI", "IFRN", "IFS"]]}, "then": "Nordeste"},
                                {"case": {"$in": ["$acronym", ["IFB", "IFG", "IF Goiano", "IFMT", "IFMS"]]}, "then": "Centro-Oeste"},
                                {"case": {"$in": ["$acronym", ["IFES", "IFMG", "IFNMG", "IFSULDEMINAS", "IF SUDESTE MG", "IFTM", "IFRJ", "IFF", "IFSP"]]}, "then": "Sudeste"},
                                {"case": {"$in": ["$acronym", ["IFPR", "IFRS", "IFFarroupilha", "IFSUL", "IFSC", "IFC"]]}, "then": "Sul"},
                            ],
                            "default": "Outros"
                        }
                    }
                }
            },

            # 2️⃣ Remover documentos sem região válida
            {
                "$match": {
                    "region_name": {"$ne": "Outros"}
                }
            },

            # 3️⃣ Agrupar por REGIÃO + ANO
            {
                "$group": {
                    "_id": {
                        "region": "$region_name",
                        "year": "$year"
                    },

                    "nomeacoes": {
                        "$sum": {"$cond": [{"$eq": ["$type", "Nomeação"]}, 1, 0]}
                    },
                    "exoneracoes": {
                        "$sum": {"$cond": [{"$eq": ["$type", "Exoneração"]}, 1, 0]}
                    },
                    "afastamentos": {
                        "$sum": {"$cond": [{"$eq": ["$type", "Afastamento"]}, 1, 0]}
                    },
                    "aposentadorias": {
                        "$sum": {"$cond": [{"$eq": ["$type", "Aposentadoria"]}, 1, 0]}
                    },
                    "pensoes": {
                        "$sum": {"$cond": [{"$eq": ["$type", "Pensão"]}, 1, 0]}
                    },
                    "demissoes": {
                        "$sum": {"$cond": [{"$eq": ["$type", "Demissão"]}, 1, 0]}
                    },
                    "dispensas": {
                        "$sum": {"$cond": [{"$eq": ["$type", "Dispensa"]}, 1, 0]}
                    },
                    "designacoes": {
                        "$sum": {"$cond": [{"$eq": ["$type", "Designação"]}, 1, 0]}
                    },
                    "substituicoes": {
                        "$sum": {"$cond": [{"$eq": ["$type", "Substituição"]}, 1, 0]}
                    },
                    "outros": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$not": {
                                        "$in": [
                                            "$type",
                                            [
                                                "Nomeação", "Exoneração", "Afastamento",
                                                "Aposentadoria", "Pensão", "Demissão",
                                                "Dispensa", "Designação", "Substituição"
                                            ]
                                        ]
                                    }
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "total_acts": {"$sum": 1}
                }
            },

            # 4️⃣ Ordenar por ano e região
            {
                "$sort": {
                    "_id.year": 1,
                    "_id.region": 1
                }
            },

            # 5️⃣ Formatar saída final
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id.region",
                    "region": {"$toLower": "$_id.region"},
                    "year": "$_id.year",
                    "nomeacoes": 1,
                    "exoneracoes": 1,
                    "afastamentos": 1,
                    "aposentadorias": 1,
                    "pensoes": 1,
                    "demissoes": 1,
                    "dispensas": 1,
                    "designacoes": 1,
                    "substituicoes": 1,
                    "outros": 1,
                    "total_acts": 1
                }
            }
        ]

        result = await self.colletion.aggregate(pipeline).to_list(None)

        return  result
    
    async def get_states_totals(self):

        pipeline = [
            {
                "$addFields": {
                    "state_info": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$acronym", "IFAC"]}, "then": {"uf": "AC", "state_name": "Acre"}},
                                {"case": {"$eq": ["$acronym", "IFAL"]}, "then": {"uf": "AL", "state_name": "Alagoas"}},
                                {"case": {"$eq": ["$acronym", "IFAP"]}, "then": {"uf": "AP", "state_name": "Amapá"}},
                                {"case": {"$eq": ["$acronym", "IFAM"]}, "then": {"uf": "AM", "state_name": "Amazonas"}},
                                {"case": {"$eq": ["$acronym", "IFBA"]}, "then": {"uf": "BA", "state_name": "Bahia"}},
                                {"case": {"$eq": ["$acronym", "IF Baiano"]}, "then": {"uf": "BA", "state_name": "Bahia"}},
                                {"case": {"$eq": ["$acronym", "IFCE"]}, "then": {"uf": "CE", "state_name": "Ceará"}},
                                {"case": {"$eq": ["$acronym", "IFB"]}, "then": {"uf": "DF", "state_name": "Distrito Federal"}},
                                {"case": {"$eq": ["$acronym", "IFES"]}, "then": {"uf": "ES", "state_name": "Espírito Santo"}},
                                {"case": {"$eq": ["$acronym", "IFG"]}, "then": {"uf": "GO", "state_name": "Goiás"}},
                                {"case": {"$eq": ["$acronym", "IF Goiano"]}, "then": {"uf": "GO", "state_name": "Goiás"}},
                                {"case": {"$eq": ["$acronym", "IFMA"]}, "then": {"uf": "MA", "state_name": "Maranhão"}},
                                {"case": {"$eq": ["$acronym", "IFMT"]}, "then": {"uf": "MT", "state_name": "Mato Grosso"}},
                                {"case": {"$eq": ["$acronym", "IFMS"]}, "then": {"uf": "MS", "state_name": "Mato Grosso do Sul"}},
                                {"case": {"$eq": ["$acronym", "IFMG"]}, "then": {"uf": "MG", "state_name": "Minas Gerais"}},
                                {"case": {"$eq": ["$acronym", "IFNMG"]}, "then": {"uf": "MG", "state_name": "Minas Gerais"}},
                                {"case": {"$eq": ["$acronym", "IFSULDEMINAS"]}, "then": {"uf": "MG", "state_name": "Minas Gerais"}},
                                {"case": {"$eq": ["$acronym", "IF Sudeste MG"]}, "then": {"uf": "MG", "state_name": "Minas Gerais"}},
                                {"case": {"$eq": ["$acronym", "IFTM"]}, "then": {"uf": "MG", "state_name": "Minas Gerais"}},
                                {"case": {"$eq": ["$acronym", "IFPA"]}, "then": {"uf": "PA", "state_name": "Pará"}},
                                {"case": {"$eq": ["$acronym", "IFPB"]}, "then": {"uf": "PB", "state_name": "Paraíba"}},
                                {"case": {"$eq": ["$acronym", "IFPR"]}, "then": {"uf": "PR", "state_name": "Paraná"}},
                                {"case": {"$eq": ["$acronym", "IFPE"]}, "then": {"uf": "PE", "state_name": "Pernambuco"}},
                                {"case": {"$eq": ["$acronym", "IF Sertão PE"]}, "then": {"uf": "PE", "state_name": "Pernambuco"}},
                                {"case": {"$eq": ["$acronym", "IFPI"]}, "then": {"uf": "PI", "state_name": "Piauí"}},
                                {"case": {"$eq": ["$acronym", "IFF"]}, "then": {"uf": "RJ", "state_name": "Rio de Janeiro"}},
                                {"case": {"$eq": ["$acronym", "IFRJ"]}, "then": {"uf": "RJ", "state_name": "Rio de Janeiro"}},
                                {"case": {"$eq": ["$acronym", "IFRN"]}, "then": {"uf": "RN", "state_name": "Rio Grande do Norte"}},
                                {"case": {"$eq": ["$acronym", "IFFarroupilha"]}, "then": {"uf": "RS", "state_name": "Rio Grande do Sul"}},
                                {"case": {"$eq": ["$acronym", "IFRS"]}, "then": {"uf": "RS", "state_name": "Rio Grande do Sul"}},
                                {"case": {"$eq": ["$acronym", "IFSul"]}, "then": {"uf": "RS", "state_name": "Rio Grande do Sul"}},
                                {"case": {"$eq": ["$acronym", "IFRO"]}, "then": {"uf": "RO", "state_name": "Rondônia"}},
                                {"case": {"$eq": ["$acronym", "IFRR"]}, "then": {"uf": "RR", "state_name": "Roraima"}},
                                {"case": {"$eq": ["$acronym", "IFC"]}, "then": {"uf": "SC", "state_name": "Santa Catarina"}},
                                {"case": {"$eq": ["$acronym", "IFSC"]}, "then": {"uf": "SC", "state_name": "Santa Catarina"}},
                                {"case": {"$eq": ["$acronym", "IFSP"]}, "then": {"uf": "SP", "state_name": "São Paulo"}},
                                {"case": {"$eq": ["$acronym", "IFS"]}, "then": {"uf": "SE", "state_name": "Sergipe"}},
                                {"case": {"$eq": ["$acronym", "IFTO"]}, "then": {"uf": "TO", "state_name": "Tocantins"}},
                            ],
                            "default": "Outros"
                        }
                    }
                }
            },
            {"$match": {"state_info": {"$ne": "Outros"}}},
            {
                "$group": {
                    "_id": {
                        "year": "$year",
                        "uf": "$state_info.uf",
                        "state_name": "$state_info.state_name"
                    },

                    "nomeacoes": {"$sum": {"$cond": [{"$eq": ["$type", "Nomeação"]}, 1, 0]}},
                    "exoneracoes": {"$sum": {"$cond": [{"$eq": ["$type", "Exoneração"]}, 1, 0]}},
                    "afastamentos": {"$sum": {"$cond": [{"$eq": ["$type", "Afastamento"]}, 1, 0]}},
                    "aposentadorias": {"$sum": {"$cond": [{"$eq": ["$type", "Aposentadoria"]}, 1, 0]}},
                    "pensoes": {"$sum": {"$cond": [{"$eq": ["$type", "Pensão"]}, 1, 0]}},
                    "demissoes": {"$sum": {"$cond": [{"$eq": ["$type", "Demissão"]}, 1, 0]}},
                    "dispensas": {"$sum": {"$cond": [{"$eq": ["$type", "Dispensa"]}, 1, 0]}},
                    "designacoes": {"$sum": {"$cond": [{"$eq": ["$type", "Designação"]}, 1, 0]}},
                    "substituicoes": {"$sum": {"$cond": [{"$eq": ["$type", "Substituição"]}, 1, 0]}},
                    "outros": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$not": {
                                        "$in": [
                                            "$type",
                                            [
                                                "Nomeação", "Exoneração", "Afastamento",
                                                "Aposentadoria", "Pensão", "Demissão",
                                                "Dispensa", "Designação", "Substituição"
                                            ]
                                        ]
                                    }
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "total_acts": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.uf": 1}},
            {
                "$project": {
                    "_id": 0,
                    "uf": "$_id.uf",
                    "state_name": "$_id.state_name",
                    "year": "$_id.year",
                    "nomeacoes": 1,
                    "exoneracoes": 1,
                    "afastamentos": 1,
                    "aposentadorias": 1,
                    "pensoes": 1,
                    "demissoes": 1,
                    "dispensas": 1,
                    "designacoes": 1,
                    "substituicoes": 1,
                    "outros": 1,
                    "total_acts": 1
                }
            }
        ]

        return await self.colletion.aggregate(pipeline).to_list(None)


    async def get_top_personnel(self):
        """
        Retorna os 10 órgãos com mais atos, filtrados pelo último ano (365 dias).
        """
        # Calcula a data de início: hoje menos 365 dias
        one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        pipeline = [
            {
                "$match": {
                    "type": {"$in": self.target_types},
                    "date": {"$gte": one_year_ago}  # Filtro de 1 ano atrás
                }
            },
            {
                "$group": {
                    "_id": {
                        "responsible": "$responsible",
                        "acronym": "$acronym"
                    },
                    **self._get_pivot_stage()
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "responsible": "$_id.responsible",
                    "acronym": "$_id.acronym",
                    "responsible_institute": {"$concat": ["$_id.responsible", " - ", "$_id.acronym"]},
                    "total_acts": 1,
                    "nomeacoes": 1,
                    "exoneracoes": 1,
                    "afastamentos": 1,
                    "aposentadorias": 1,
                    "pensoes": 1,
                    "demissoes": 1,
                    "dispensas": 1,
                    "designacoes": 1,
                    "substituicoes": 1
                }
            },
            {"$sort": {"total_acts": -1}},
            {"$limit": 10}
        ]
        
        cursor = self.colletion.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def get_latest_by_type(self):
        """Item 5: Último ato de cada tipo para latest_pubs."""
        latest_acts = []
        for t in self.target_types:
            # Busca o mais recente pelo campo 'date'
            doc = await self.colletion.find({"type": t}).sort("date", -1).limit(1).to_list(1)
            if doc:
                latest_acts.append({
                    "acronym": doc[0].get("acronym"),
                    "date": doc[0].get("date"),
                    "type": doc[0].get("type")
                })
        return latest_acts

    async def get_publication_count(self):
        """Item 6: Total geral."""
        return await self.colletion.count_documents({})
    
    async def get_available_types(self):
        """
        Retorna uma lista de todos os tipos de atos únicos presentes na coleção.
        Útil para preencher filtros de busca no frontend.
        """
        # O método distinct retorna uma lista com os valores únicos do campo 'type'
        types = await self.colletion.distinct("type")
        # Ordena alfabeticamente para melhor experiência do usuário
        return sorted([t for t in types if t])

    async def get_available_institutes(self):
        """
        Retorna uma lista de todas as siglas (acronym) de institutos únicas.
        """
        acronyms = await self.colletion.distinct("acronym")
        # Filtra valores nulos e ordena
        return sorted([a for a in acronyms if a])

    async def get_available_years(self):
        """Item 7: Anos distintos."""
        years = await self.colletion.distinct("year")
        
        return sorted([y for y in years if y], reverse=True)