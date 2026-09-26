"""
Simulated live vitals stream over WebSocket.
No real hardware is available for the hackathon timeline, so this generates
plausible, slowly-drifting vitals — this is explicitly documented as
simulated in the architecture doc, not claimed as real IoT hardware.
Real ESP32/sensor integration is Future Scope; swapping this generator for
a real device feed later only requires replacing `_generate_reading()`.
"""
import asyncio
import random

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Baseline "healthy adult" vitals — each tick drifts slightly from these.
_BASELINE = {
    "heart_rate": 72,
    "bp_systolic": 118,
    "bp_diastolic": 78,
    "spo2": 98,
    "temperature": 36.8,
    "respiration": 16,
}


def _generate_reading(state: dict) -> dict:
    """Small random walk around baseline so the chart looks alive but stays realistic."""
    state["heart_rate"] = max(55, min(110, state["heart_rate"] + random.randint(-2, 2)))
    state["bp_systolic"] = max(100, min(140, state["bp_systolic"] + random.randint(-2, 2)))
    state["bp_diastolic"] = max(65, min(90, state["bp_diastolic"] + random.randint(-1, 1)))
    state["spo2"] = max(94, min(100, state["spo2"] + random.randint(-1, 1)))
    state["temperature"] = round(max(36.0, min(37.8, state["temperature"] + random.uniform(-0.1, 0.1))), 1)
    state["respiration"] = max(12, min(20, state["respiration"] + random.randint(-1, 1)))
    return dict(state)


@router.websocket("/ws/vitals/{patient_id}")
async def stream_vitals(websocket: WebSocket, patient_id: str):
    """
    Streams a simulated vitals reading every 2 seconds.
    Frontend connects via: new WebSocket(`ws://.../ws/vitals/${patientId}`)
    """
    await websocket.accept()
    state = dict(_BASELINE)
    try:
        while True:
            reading = _generate_reading(state)
            await websocket.send_json({"patient_id": patient_id, **reading})
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
