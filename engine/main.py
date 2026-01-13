from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from logic import calculate_simulation, get_economies, get_industries, get_available_industries, CONFIG, get_db_connection
from ingestion.worldbank import WorldBankIngestor
import uvicorn
from typing import Dict, List
from models import PolicyShock, SimulationResult, EconomyProfile, IndustryProfile

app = FastAPI(title="TIPM Engine")

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "tipm-engine"}

@app.get("/economies", response_model=List[EconomyProfile])
def economies():
    return get_economies()

@app.get("/industries", response_model=List[IndustryProfile])
def industries():
    return get_industries()

@app.get("/api/industries/available", response_model=List[IndustryProfile])
def read_available_industries(source_id: str, target_id: str):
    return get_available_industries(source_id, target_id)

import traceback

@app.post("/simulate")
def simulate(shock: PolicyShock) -> SimulationResult:
    """
    Executes a trade policy simulation based on the provided shock.
    """
    try:
        results = calculate_simulation(shock)
        return results
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/data/refresh")
async def refresh_data():
    """
    Triggers the automated data ingestion from external sources.
    This demonstrates the capability to ingest live data without manual intervention.
    """
    try:
        # 1. Initialize Ingestor with centralized config
        ingestor = WorldBankIngestor(CONFIG)
        
        # 2. Fetch list of countries currently in DB to refresh
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM economies")
        country_codes = [row['id'] for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        # 3. Trigger Ingestion (In a real system, this would be a background task)
        # For this demonstration, we'll simulate a targeted refresh of key economies
        updated_data = ingestor.refresh_all_economies(country_codes[:5]) # Limit to 5 for rapid demo
        
        # 4. Update the DB with new GDP figures
        conn = get_db_connection()
        cur = conn.cursor()
        for code, gdp in updated_data.items():
            cur.execute("UPDATE economies SET gdp_usd_bn = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?", (gdp, code))
        conn.commit()
        cur.close()
        conn.close()

        return {
            "status": "ingestion_complete",
            "message": f"Successfully refreshed GDP for {len(updated_data)} economies.",
            "details": updated_data
        }
    except Exception as e:
        logger_err = f"IN_GESTION_ERROR: {str(e)}\n{traceback.format_exc()}"
        print(logger_err)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting TIPM Engine...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
