"""
Realtime patient streaming endpoint using Server-Sent Events (SSE).
Streams new synthetic patients every 5 seconds.
"""

import json
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.patient import RealtimePatientPayload
from app.services.simulation_service import create_simulated_patient


router = APIRouter(prefix="/api/patients", tags=["Realtime"])


def event_generator():
    """SSE generator that emits a new patient every 5 seconds."""
    while True:
        try:
            patient = create_simulated_patient()

            payload = RealtimePatientPayload(
                event="patient_created",
                patient=patient
            )

            yield f"data: {json.dumps(payload.model_dump())}\n\n"

            time.sleep(5)

        except Exception:
            # Never kill the stream
            time.sleep(5)
            continue


@router.get("/realtime")
def realtime_patients():
    """Stream new patients every 5 seconds via SSE."""
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
