import asyncio
import uuid
from typing import Final

import httpx
from fastapi import FastAPI, Request
from pydantic import BaseModel
from rich import print as rich_print
from rich import print_json

print = rich_print

PROMPT_TEMPLATE: Final = """### Instruction:\nYou are a code completion assistant and your task is to analyze user edits and then rewrite an excerpt that the user provides, suggesting the appropriate edits within the excerpt, taking into account the cursor location.\n\n### User Edits:\n\n{}\n\n### User Excerpt:\n\n{}\n\n### Response:\n"""
RESPONSE_TIMEOUT: Final = 30

MAX_TOKENS: Final = 2048
TEMPERTURE: Final = 0.0

# http://192.168.1.147:10002/predict_edits
LOCAL_LLM_COMPLETIONS_ENDPOINT: Final = "http://localhost:10002/v1/completions"


app = FastAPI()


class PredictEditsRequest(BaseModel):
    input_events: str | None
    input_excerpt: str | None
    outline: str | None = None
    speculated_output: str | None = None
    can_collect_data: bool = False
    diagnostic_groups: list[object] = []


@app.post("/predict_edits")
async def predict_edits(request: Request, predict_request: PredictEditsRequest):
    print("\n\n[bold red]## Zed request body:")
    print(predict_request)

    prompt_template = PROMPT_TEMPLATE
    prompt = prompt_template.format(
        predict_request.input_events, predict_request.input_excerpt
    )

    print("\n\n[bold red]## Prompt:")
    print(prompt)

    async def generate_prediction():
        async with httpx.AsyncClient(timeout=RESPONSE_TIMEOUT) as client:
            request_body = {
                "model": "zeta",
                "prompt": prompt,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERTURE,
            }
            print("\n\n[bold red]## request body => /v1/completions:")
            print_json(data=request_body)

            response = await client.post(
                LOCAL_LLM_COMPLETIONS_ENDPOINT, json=request_body
            )
            response.raise_for_status()
            response_body = response.json()
            print("\n\n[bold red]## /v1/completions => response body:")
            print_json(data=response_body)

            choice_text = response_body.get("choices", [{}])[0].get("text", "")

            print(choice_text)

            return {
                "output_excerpt": choice_text,
                "request_id": str(uuid.uuid4()).replace("-", ""),
            }

    task = asyncio.create_task(generate_prediction())

    while not task.done():
        if await request.is_disconnected():
            print("Client disconnected")
            task.cancel()
            return {
                "error": "Request cancelled",
                "request_id": str(uuid.uuid4()).replace("-", ""),
                "output_excerpt": "",
            }

    try:
        zed_prediction_response_body = await task
        print("\n\n[bold green]## Zed response body:")
        print_json(data=zed_prediction_response_body)
        return zed_prediction_response_body
    except asyncio.CancelledError:
        return {
            "error": "Request cancelled",
            "request_id": str(uuid.uuid4()).replace("-", ""),
            "output_excerpt": "",
        }
    except Exception as e:
        return {
            "error": str(e),
            "request_id": str(uuid.uuid4()).replace("-", ""),
            "output_excerpt": "",
        }
