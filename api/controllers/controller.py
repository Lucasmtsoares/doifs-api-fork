from app.db.dashboard_dao import DashboardDAO
from app.db.publication_dao import PublicationDAO
from app.models.publication import Publication

class PublicationController:
    def __init__(self, pub_dao):
        self.dao = pub_dao

    async def get_publication_controller(self, params: dict):
        """
        Recebe o dicionário vindo da Rota (GET ou POST) e 
        converte no modelo Publication esperado pelo DAO.
        """
        # Cria a instância do modelo Publication (Validação inicial automática do Pydantic)
        search_model = Publication(
            name=params.get("name"),
            type=params.get("type"),
            acronym=params.get("acronym"),
            year=params.get("year")
        )
        
        results, total = await self.dao.get_publication(search_model)
        
        return {
            "publications": results,
            "count": total
        }

class SummaryController:
    """
    Controlador para o resumo do Dashboard (Cards Superiores).
    """
    def __init__(self, dashboard_dao: DashboardDAO):
        self.dash = dashboard_dao
    
    async def get_totals_controller(self):
        # Sincronizado com os novos nomes no teste.py (DashboardDAO)
        types_counts = await self.dash.get_type_counts_last_month() # Item 1 do DAO
        latest_pubs = await self.dash.get_latest_by_type()        # Item 5 do DAO
        total_count = await self.dash.get_publication_count()
        total_by_type = await self.dash.get_total_by_type_all_time()   # Item 6 do DAO
        monthly_totals = await self.dash.get_monthly_totals()       # Item 9 do DAO
        
        return {
            "types_counts": types_counts,
            "latest_pubs": latest_pubs,
            "total_count": total_count,
            "count_by_type_all_time": total_by_type,
            "monthly_totals": monthly_totals
        } 

class PeriodicController:
    """
    Controlador para gráficos de evolução temporal.
    """
    def __init__(self, dashboard_dao: DashboardDAO):
        self.dash = dashboard_dao
        
    async def get_periodic_type_controller(self):
        # Sincronizado com Item 2 do DAO
        periodic_types = await self.dash.get_periodic_type_counts()
        return {
            "periodic_types": periodic_types
        }

class PersonnelController:
    """
    Controlador para análise de responsáveis/pessoal.
    """
    def __init__(self, dashboard_dao: DashboardDAO):
        self.dash = dashboard_dao
        
    async def get_top_personnel_controller(self):
        # Sincronizado com Item 4 do DAO
        tops_personnel = await self.dash.get_top_personnel()
        return {
            "tops_personnel": tops_personnel
        }

class InstituteController:
    """
    Controlador para visão por institutos e anos.
    """
    def __init__(self, dashboard_dao: DashboardDAO):
        self.dash = dashboard_dao
        
    async def get_institutes_overview_controller(self):
        # Sincronizado com Item 3 do DAO
        institutes_overview = await self.dash.get_institutes_overview()
        # Item 7 do DAO
        years = await self.dash.get_available_years()
        
        return {
            "institutes_overview": institutes_overview,
            "years": years
        }

class RegionController:
    """
    Controlador para Regiões (Fallback usando dados de estados).
    """
    def __init__(self, dashboard_dao: DashboardDAO):
        self.dash = dashboard_dao
        
    async def get_region_totals_controller(self):
        # Como o DAO não possui get_region_totals, usamos os dados de estados
        # O frontend pode agrupar esses estados por região se necessário.
        region_data = await self.dash.get_region_totals()
        return {
            "region_totals": region_data
        }

class StatesController:
    """
    Controlador para dados geográficos por estado.
    """
    def __init__(self, dashboard_dao: DashboardDAO):
        self.dash = dashboard_dao
        
    async def get_states_totals_controller(self):
        # Sincronizado com Item 8 do DAO
        state_totals = await self.dash.get_states_totals()
        return {
            "state_totals": state_totals
        }
        
class FiltersController:
    """
    Controlador para anos disponíveis (para filtros).
    """
    
    def __init__(self, dashboard_dao: DashboardDAO):
        self.dash = dashboard_dao
        
    async def get_filters_metadata_controller(self):
        # Retorno dos anos disponíveis para filtros available
        
        years = await self.dash.get_available_years()
        types = await self.dash.get_available_types()
        institutes = await self.dash.get_available_institutes()
        
        return {
            "types": types,
            "institutes": institutes,
            "years": years
        }