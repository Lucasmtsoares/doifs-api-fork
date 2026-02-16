from app.db.dashboard_dao import DashboardDAO
from app.db.publication_dao import PublicationDAO

class PublicationController:
    """
    Controlador responsável pela busca textual e filtrada de publicações.
    """
    def __init__(self, publication_dao: PublicationDAO):
        self.publication = publication_dao
        
    async def get_publication_controller(self, publication):
        # Utiliza o método de busca do PublicationDAO
        publications, count = await self.publication.get_publication(publication)
        print("Controller: Busca de publicações concluída.")
        return {
            "publications": publications,
            "count": count
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
        
class YearsController:
    """
    Controlador para anos disponíveis (para filtros).
    """
    
    def __init__(self, dashboard_dao: DashboardDAO):
        self.dash = dashboard_dao
        
    async def get_available_years_controller(self):
        # Retorno dos anos disponíveis para filtros
        
        years = await self.dash.get_available_years()
        
        return {
            "years": years
        }