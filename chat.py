import httpx
import asyncio
import time
from typing import Dict, Any

ENDPOINT = "https://motionime.my.id/api/"
API_KEY = "DM_FOR_KEY_TESTING"

async def get_ai_response(prompt: str) -> tuple[Dict[str, Any], float]:
    payload: Dict[str, str] = {"q": prompt}
    headers: Dict[str, str] = {"Authorization": API_KEY}
    start_time: float = time.time()
    try:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.post(ENDPOINT, json=payload, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data: Dict[str, Any] = response.json()
            finish_time: float = time.time()
            elapsed_time: float = finish_time - start_time
            return data, elapsed_time
    except httpx.RequestError as e:
        return {"answer": f"Error: Failed to connect to the API: {e}"}, 0.0


async def main() -> None:
    while True:
        user_input: str = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye","adios","dadah"]:
            print("Sayonara!")
            break

        ai_response, elapsed_time = await get_ai_response(user_input)

        if "answer" in ai_response:
            print(f"Motion Ime: {ai_response['answer']}")
            if elapsed_time > 0:
                print(f"Finish: {elapsed_time:.2f}s")
        else:
            print(f"Motion Ime: {ai_response}")

if __name__ == "__main__":
    asyncio.run(main())