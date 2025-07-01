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



router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "Art Generator API is running!"}

@router.post("/generate-image")
async def generate_image(prompt: str = Form(...), 
                         context_image: Optional[UploadFile] = File(None),
                         image_size: str = Query("512x512", description = "Select the image size", enum=utils.valid_sizes), 
                         model: str = Query("stable_diffusion", description= "Choose the image generation model", enum= utils.TOP_IMAGE_MODELS)):
    
    if not prompt.strip(): 
        raise HTTPException(status_code=400, detail = "Please include a description of what you would like to do" )
    base64_string: Optional[str] = None
    if context_image:
       image_data = await context_image.read()
       print("read image")
       try:
            image = Image.open(BytesIO(image_data))
            format = image.format
            base64_string = base64.b64encode(image_data).decode('utf-8')
            print("checked image format")      
            if format not in ["PNG", "JPEG"]:
                raise HTTPException(status_code = 400, detail= "Only PNG and JPEG files are allowed.")
       except: 
            raise HTTPException(status_code=400, detail= " This is not a valid image file")
    payload = {
                "prompt": prompt,
                "context_image": base64_string}
    
async def generate_image_from_prompt(prompt: str, image_size: str = "512x512", context_image: Optional[str] = None, model: str = "stabel_diffusion"):
    if model not in utils.TOP_IMAGE_MODELS:
        raise HTTPException(status_code=400, detail= "This is a model that is not support on the list. Please choose another model.")
    if image_size not in utils.valid_sizes:
        raise HTTPException(status_code=400, detail = "Invalid image size. Choose from 256x256, 512x512, or 1024x1024.")

""""

    
    payload = {
    "prompt": prompt,
    "init_images": context_image
    
}
    if context_image: 
        payload["response_format"] = f"{context_image}"
    async with httpx.AsyncClient() as client:
        response = await client.post(config.OPENAI_IMAGE_ENDPOINT, 
                                     headers = config.HEADERS, 
                                     json= payload)
"""
    
    
        

