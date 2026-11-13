from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool
from app.engine import simulate_kinematic_draw

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Only the Quantum Seed is required for the Kinematic Engine
QUANTUM_FILE = "quantum_seed.csv"


@app.get("/")
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/draw")
async def get_draw(
    motor: float = Query(default=0.75, ge=0.1, le=5.0),
    kinetic: float = Query(default=3.14, ge=0.1, le=10.0),
):
    try:
        # Run CPU work outside the event loop so one simulation cannot stall
        # other requests while it searches for resonance openings.
        main_numbers, strong_number = await run_in_threadpool(
            simulate_kinematic_draw,
            historical_data_path="",
            quantum_csv_path=QUANTUM_FILE,
            next_draw_seq=0,
            motor_hz=motor,
            kinetic_hz=kinetic,
        )
        return {
            "yielded_numbers": main_numbers,
            "strong_number": strong_number,
        }
    except Exception as exc:
        print(f"[API ERROR] Draw calculation failed: {exc}")
        return JSONResponse(
            status_code=503,
            content={"error": str(exc)},
        )
