import streamlit as st
import requests
import time
import config
import routes

st.title("AI Room Staging App")

prompt = st.text_input("Describe how you'd like your space to look:")

# Model selection
model = st.selectbox("Choose a model", [
    "stable_diffusion",
    "deliberate_v2",
    "dreamshaper",
    "realistic_vision",
    "absolute_reality",
    "openjourney",
    "pastel_mix",
    "f222",
    "easynegative",
    "anythingv3"
], index=0)

# Image size selection
image_size = st.selectbox("Select image size", ["256x256", "512x512", "1024x1024"], index=1)

# Optional image upload
context_image = st.file_uploader("Upload a room image (PNG or JPEG)", type=["png", "jpg", "jpeg"])

# Submit button
if st.button("Generate Image"):
    if not prompt.strip():
        st.error("Prompt is required to generate an image.")
    else:
        st.info("Sending your request to the server...")
        data = {'prompt': prompt,
                "model": model,
                "image_size": image_size,
        }
        API_URL = "http://localhost:8000/generate-image"
        files = None
        response = None
        if context_image:
            files = { "context_image": (context_image.name, 
                                context_image,
                                context_image.type)}
        try: 
            if files:
                response = requests.post(API_URL, data=data, files=files, timeout= 10)
            else: 
                response = requests.post(API_URL, data=data)
        except requests.exceptions.RequestException:
            st.error("Could not connect to the server. Please check your internet connection.")
        if response: 
            if response.status_code == 202:
                st.success("Image request accepted! Your image is being processed. Should take about 10-20 secs.")
                progress_bar = st.progress(0)
                status_text = st.empty()
                response_data = response.json()
                request_id= response_data["request_id"]
                for i in range(100):
                    status_response = requests.get(f"{config.STABLE_HORDE_STATUS_ENDPOINT}/{request_id}")
                    status_data = status_response.json()
                    if status_data.get("done", False):
                        progress_bar.progress(100)
                        st.success("Image is ready!")
                        image_url = status_data["generations"][0]["img"]
                        st.image(image_url, caption = "Here is your generated image!")
                        break
                    else: 
                        progress= int(status_data.get("progress", 0))
                        progress_bar.progress(progress)
                        status_text.info(f"Progress: {progress}%")
                        time.sleep(3)         
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        
