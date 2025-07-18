import streamlit as st
import requests
import time
import config
import routes
from typing import Optional


st.title("AI Room Staging App")
prompt = st.text_input("Describe how you'd like your space to look:")
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
image_size = st.selectbox("Select image size", ["256x256", "512x512", "1024x1024"], index=1)
context_image = st.file_uploader("Upload a room image (PNG or JPEG)", type=["png", "jpg", "jpeg"])
if context_image:
    st.image(context_image) 
    denoising_strength = st.session_state["denoising_strength"] = st.slider(
        "Denoising Strength (for img2img)",
        min_value=0.1,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Controls how much the original image is preserved.\nLower = closer to original, Higher = more change."
    )
if "steps" not in st.session_state:
    st.session_state["steps"] = 40
steps = st.slider("Number of Diffusion Steps (1–40)", 
                  min_value=1,
                  max_value=40,
                  value= st.session_state["steps"],
                  help="Higher steps = better detail, but longer time.")
st.session_state["steps"] = steps
def send_generation_request(api_url: str, data: dict, files:Optional[dict] = None) -> Optional[requests.Response]:
    try:
        if files:
            response = requests.post(api_url, data=data, files=files, timeout=10)
        else:
            response = requests.post(api_url, data=data, timeout=10)
        return response
    except requests.exceptions.RequestException:
        st.error("Could not connect to the server. Please check your internet connection.")
        return None
def display_images_with_download(status_data: dict):
    if not status_data.get("generations"):
        st.error("No images were generated. Please try again or adjust your prompt.")
        return
    for idx, gen in enumerate(status_data["generations"]):
        try:
            image_url = gen.get("img")
            if not image_url:
                st.warning("One of the generated images is missing a URL.")
                continue
            # Display the image
            st.image(image_url, caption="Here is your generated image!")
            # Fetch image bytes for download
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            image_bytes = image_response.content

            # Input for filename
            default_name = f"generated_image_{idx + 1}.webp"
            filename_key = f"filename_input_{idx}"
            filename = st.text_input("Name your file:", value=default_name, key=filename_key)

            # Download button
            if st.session_state.get(filename_key):
                st.download_button(
                    label="Download Image",
                    data=image_bytes,
                    file_name=st.session_state[filename_key],
                    mime="image/webp",
                    key=f"download_button_{idx}"
                )
        except Exception as e:
            st.error(f"Error with image {idx+1}: {e}")

# Submit button
if st.button("Generate Image"):
    #Raise Error if user doesn't submit a prompt
    if not prompt.strip():
        st.error("Prompt is required to generate an image.")
    else:
        st.info("Sending your request to the server...")
        data = {'prompt': prompt,
                "model": model,
                "image_size": image_size,
                "steps": steps,
                "denoising_strength": denoising_strength
        }
        ROUTE_URL = config.GENERATE_IMAGE_URL
        files = None
        response = None
        try:
            if context_image:
                files = { "context_image": (context_image.name, 
                                context_image,
                                context_image.type)}
                response = send_generation_request(ROUTE_URL, data=data, files= files)
            else:
                response = send_generation_request(ROUTE_URL, data = data, files = None)
        except RuntimeError as e:
            st.error(str(e))
            st.stop()
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
                            display_images_with_download(status_data)
                            break
                        else: 
                            progress= int(response_data.get("progress", 0))
                            progress_bar.progress(progress)
                            status_text.info(f"Progress: {progress}%")
                            time.sleep(3)         
            else:
                    st.error(f"Error: {response.status_code} - {response.text}")

    