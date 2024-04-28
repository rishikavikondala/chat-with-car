import os
import json
import requests
import smartcar
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from openai import OpenAI
from anthropic import Anthropic
from pydantic import BaseModel
from tools import tools

print(tools)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

global openai_client
global anthropic_client
global smartcar_client
global smartcar_access_token

OPUS_MODEL_NAME = "claude-3-opus-20240229"
HAIKU_MODEL_NAME = "claude-3-haiku-20240307"
WHISPER_MODEL_NAME = "whisper-1"
ALLOWED_SCOPES = ["read_vehicle_info", "control_security",
                  "control_navigation", "control_trunk", "control_climate"]


class VehicleResponse(BaseModel):
    id: str
    make: str
    model: str
    year: int


@app.on_event("startup")
async def startup_event():
    global smartcar_access_token
    smartcar_access_token = None

    global openai_client
    openai_client = OpenAI()

    global anthropic_client
    anthropic_client = Anthropic()

    global smartcar_client
    smartcar_client = smartcar.AuthClient(mode="live")


@app.get("/")
async def root():
    return {"message": "chat-with-car"}


@app.get("/login")
def login():
    auth_url = smartcar_client.get_auth_url(ALLOWED_SCOPES)
    return RedirectResponse(url=auth_url)


@app.get("/exchange")
def exchange(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(
            status_code=400, detail="Code query parameter is required")
    global smartcar_access_token
    smartcar_access_token = smartcar_client.exchange_code(code)
    return RedirectResponse(url="http://localhost:8000/vehicle")


@app.get("/vehicle")
async def get_vehicle():
    global smartcar_access_token
    if not smartcar_access_token:
        raise HTTPException(
            status_code=400, detail="Smartcar access token is missing")

    try:
        vehicles = smartcar.get_vehicles(smartcar_access_token.access_token)
        vehicle_ids = vehicles.vehicles

        # [0] will access the first vehicle listed when you authenticate with Smartcar
        vehicle = smartcar.Vehicle(
            vehicle_ids[0], smartcar_access_token.access_token)
        attributes = vehicle.attributes()

        return VehicleResponse(
            id=vehicle_ids[0],
            make=attributes.make,
            model=attributes.model,
            year=attributes.year,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def process_tool_call(vehicle, tool_name, tool_input):
    if tool_name == "unlock":
        vehicle.unlock()
        return "Vehicle unlocked"
    elif tool_name == "lock":
        vehicle.lock()
        return "Vehicle locked"
    elif tool_name == "open_trunk":
        vehicle.request(
            "POST",
            "tesla/security/trunk",
            {"action": "OPEN"}
        )
        return "Vehicle trunk opened"
    elif tool_name == "close_trunk":
        vehicle.request(
            "POST",
            "tesla/security/trunk",
            {"action": "CLOSE"}
        )
        return "Vehicle trunk closed"
    elif tool_name == "open_frunk":
        vehicle.request(
            "POST",
            "tesla/security/frunk",
            {"action": "OPEN"}
        )
        return "Vehicle frunk opened"
    elif tool_name == "set_cabin_climate":
        vehicle.request(
            "POST",
            "tesla/climate/cabin",
            {
                "action": "SET",
                "temperature": tool_input["temperature"]
            }
        )
        return "Cabin climate set"
    elif tool_name == "navigate":
        global smartcar_access_token

        vehicles = smartcar.get_vehicles(smartcar_access_token.access_token)
        vehicle_id = vehicles.vehicles[0]

        url = f"https://api.smartcar.com/v2.0/vehicles/{vehicle_id}/navigation/destination"
        headers = {
            "Authorization": f"Bearer {smartcar_access_token.access_token}",
            "Content-Type": "application/json"
        }
        latitude = tool_input["latitude"]
        longitude = tool_input["longitude"]

        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            raise ValueError("Latitude and longitude must be numbers")

        data = {
            "latitude": latitude,
            "longitude": longitude
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return "Navigation destination set"
    else:
        raise ValueError(f"Unknown tool name: {tool_name}")


@ app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    with open(file.filename, "wb") as f:
        f.write(await file.read())

    with open(file.filename, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            model=WHISPER_MODEL_NAME, file=audio_file)
        command = transcription.text
        print(f"\n{'='*50}\nUser Command: {command}\n{'='*50}")

    os.remove(file.filename)

    response = anthropic_client.beta.tools.messages.create(
        model=HAIKU_MODEL_NAME,
        max_tokens=4096,
        system="You are an AI assistant that has access to a limited set of tools to control a vehicle. You may need to use more than one tool to accomplish the task at hand. Please feel free to any information you know to infer the best input to the tools to achieve the desired outcome.",
        messages=[{"role": "user", "content": command}],
        tools=tools,
    )

    print(f"\nInitial Response:")
    print(f"Stop Reason: {response.stop_reason}")
    content = next(
        (block.text for block in response.content if hasattr(block, "text")),
        None,
    )
    print(f"Content: {content}")

    while response.stop_reason == "tool_use":
        global smartcar_access_token
        vehicles = smartcar.get_vehicles(smartcar_access_token.access_token)
        vehicle_ids = vehicles.vehicles

        vehicle = smartcar.Vehicle(
            vehicle_ids[2], smartcar_access_token.access_token)

        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                result = process_tool_call(vehicle, block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result)
                })

        print(f"\nTool Results:")
        print(json.dumps(tool_results, indent=2))

        messages = [
            {"role": "user", "content": command},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": tool_results,
            },
        ]

        response = anthropic_client.beta.tools.messages.create(
            model=HAIKU_MODEL_NAME,
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        print(f"\nResponse:")
        print(f"Stop Reason: {response.stop_reason}")

    final_response = next(
        (block.text for block in response.content if hasattr(block, "text")),
        None,
    )

    print(f"\nFinal Response: {final_response}")

    return {"text": final_response}
