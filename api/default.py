from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Body
from typing import AsyncGenerator, Any
from fastapi.middleware.cors import CORSMiddleware

# Importações internas
from app.models.publication import Publication
from app.db.publication_dao import PublicationDAO
from app.db.dashboard_dao import DashboardDAO
from app.db.connection_db import mongo_client_manager

from api.controllers.controller import (
    PublicationController,
    SummaryController,
    PeriodicController,
    PersonnelController,
    InstituteController,
    RegionController,
    StatesController,
    YearsController
)

load_dotenv()
DB_NAME = os.getenv("DB_NAME")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    mongo_client = mongo_client_manager.connection()
    try:
        await mongo_client.admin.command('ping')
        db = mongo_client[DB_NAME]
        
        # Instanciação dos DAOs
        pub_dao = PublicationDAO(db)
        dash_dao = DashboardDAO(db)
        
        # Injeção de dependência nos Controllers
        app.state.publication_controller = PublicationController(pub_dao)
        app.state.summary_controller = SummaryController(dash_dao)
        app.state.periodic_controller = PeriodicController(dash_dao)
        app.state.personnel_controller = PersonnelController(dash_dao)
        app.state.institute_controller = InstituteController(dash_dao)
        app.state.region_controller = RegionController(dash_dao)
        app.state.state_controller = StatesController(dash_dao)
        app.state.years_controller = YearsController(dash_dao)
        
        yield
    finally:
        mongo_client.close()

app = FastAPI(lifespan=lifespan)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_ctrl(name: str):
    return getattr(app.state, name)

# --- ROTAS ---

@app.post("/buscar", response_model=None)
async def buscar_publicacoes(publication: Any = Body(...)):
    """Rota de busca textual e filtrada."""
    ctrl = get_ctrl('publication_controller')
    return await ctrl.get_publication_controller(publication)

@app.get("/get-totals") # Ok ----
async def get_totals():
    """Resumo: tipos no último mês, últimas pubs e contagem total."""
    return await get_ctrl('summary_controller').get_totals_controller()

@app.get("/periodic-types") # Ok ----
async def get_periodic_types_data():
    """Evolução temporal (90 dias)."""
    return await get_ctrl('periodic_controller').get_periodic_type_controller()

@app.get("/institutes-overview") # Ok ---
async def get_institutes_overview_data():
    """Visão por institutos e anos."""
    return await get_ctrl('institute_controller').get_institutes_overview_controller()

@app.get("/top-personnel") # Ok ---
async def get_top_personnel_data():
    """Ranking de responsáveis."""
    return await get_ctrl('personnel_controller').get_top_personnel_controller()

@app.get("/region-totals") # ?
async def get_region_totals_data():
    """Dados geográficos (Regiões/Estados)."""
    return await get_ctrl('region_controller').get_region_totals_controller()

@app.get("/states-totals") # ?
async def get_state_totals_data():
    """Dados geográficos detalhados por estado."""
    return await get_ctrl('state_controller').get_states_totals_controller()

@app.get("/years")
async def get_avalable_years_data():
    """Anos disponiveis"""
    return await get_ctrl('years_controller').get_available_years_controller()

