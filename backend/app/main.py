from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="CareFlow AI Backend",
    version="0.1.0",
    description="AI-powered patient triage and hospital flow management system"
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "CareFlow AI Backend"
    }

# -----------------------------------
# Safe router inclusion
# -----------------------------------

def safe_include(router_module):
    if hasattr(router_module, "router"):
        app.include_router(router_module.router)

from app.routers import patients, realtime, upload

safe_include(patients)
safe_include(realtime)
safe_include(upload)

# Optional / teammate routers
try:
    from app.routers import admin
    safe_include(admin)
except Exception:
    pass

try:
    from app.routers import departments
    safe_include(departments)
except Exception:
    pass
