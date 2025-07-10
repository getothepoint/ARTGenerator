from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Query
from PIL import Image
from io import BytesIO
import base64
import requests
from app import config 
import json
import httpx
from app import utils
from typing import Optional
from fastapi.responses import JSONResponse
import uuid

router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "Art Generator API is running!"}
@router.post("/generate-image")
async def generate_image(prompt: str = Form(...), 
                         context_image: Optional[UploadFile] = File(None),
                         steps: int = 40,
                         image_size: str = Query("512x512", description = "Select the image size", enum=utils.valid_sizes), 
                         model: str = Query("stable_diffusion", description= "Choose the image generation model", enum= utils.TOP_IMAGE_MODELS)):
    if not prompt.strip(): 
        raise HTTPException(status_code=400, detail = "Please include a description of what you would like to do" )
    base64_string: Optional[str] = None
    if context_image:
       print("Image:", context_image)
       image_data = await context_image.read()
       try:
            image = Image.open(BytesIO(image_data))
            format = image.format
            base64_string = base64.b64encode(image_data).decode('utf-8')  
            if format.upper() not in ["PNG", "JPEG", "JPG"]:
                raise HTTPException(status_code = 400, detail= "Only PNG and JPEG files are allowed.")
       except:
            raise HTTPException(status_code=400, detail= " This is not a valid image file")
    payload = {
                "prompt": prompt,
                "context_image": base64_string}
    request_id = await submit_to_stable_horde(prompt, model, image_size, steps)  # Just an example to uniquely identify the request
    return JSONResponse(
        content={
        "message": "Your image is being processed. Check back soon.",
        "request_id": request_id
        },
        status_code=202 ) 
async def generate_image_from_prompt(prompt: str, image_size: str = "512x512", context_image: Optional[str] = None, model: str = "stable_diffusion"):
    if model not in utils.TOP_IMAGE_MODELS:
        raise HTTPException(status_code=400, detail= "This is a model that is not support on the list. Please choose another model.")
    if image_size not in utils.valid_sizes:
        raise HTTPException(status_code=400, detail = "Invalid image size. Choose from 256x256, 512x512, or 1024x1024.") 
async def submit_to_stable_horde(prompt: str, model: str, image_size: str, steps:int, context_image: Optional[str] = None):
    size_parts = image_size.split("x")
    width, height = map(int, size_parts)
    params = {"model": model,
              "n": 10,
              "width": width,
              "height": height,
              "steps": steps}
    payload = {"prompt": prompt,
               "params": params
               }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(config.STABLE_HORDE_ENDPOINT, 
                                     headers = config.HEADERS, 
                                     json= payload)
    if response.status_code != 202:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to submit image generation: {response.text}")
    # Step 6: Parse and return the request ID
    data = response.json()
    return data.get("id")
@router.get("/check-status/{request_id}")
async def check_generation_status(request_id: str):
    status_url = f"{config.STABLE_HORDE_STATUS_ENDPOINT}/{request_id}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(status_url, headers=config.HEADERS)
    if response.status_code not in (200, 202):
        # Something went wrong
        return JSONResponse(
            status_code=response.status_code,
            content={"error": f"Failed to get status: {response.text}"})
    data = response.json()
    if response.status_code == 202:
        # Extract progress info from data if available, or just notify user
        progress = data.get("progress", "Processing")
        return {"status": "processing", "progress": progress, "message": "Your image is still being generated. Check back soon."}
    if response.status_code == 200:
        image_url = data.get("images")  
        return {"status": "completed", "image_url": image_url}