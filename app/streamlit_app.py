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

def send_generation_request(api_url, data, files=None):
    try:
        if files:
            response = requests.post(api_url, data=data, files=files, timeout=10)
        else:
            response = requests.post(api_url, data=data, timeout=10)
        return response
    except requests.exceptions.RequestException:
        st.error("Could not connect to the server. Please check your internet connection.")
        return None
    
def display_generated_images(request_id: str, status_data: dict):
    image_urls = []
    if not status_data.get("generations") or len(status_data["generations"]) == 0:
        st.error("No images were generated. Please try again or adjust your prompt.")
        return []
    for gen in status_data["generations"]:
        try: 
            image_url = gen.get("img")
            if not image_url:
                st.warning("One of the generated images is missing a URL.")
                continue
            image_urls.append(image_url)
            st.image(image_url, caption = "Here is your generated image!")
        except Exception as e: 
            st.error(f"An error occured while displaying an image {e}")
    return image_urls

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
                            image_urls = display_generated_images(request_id, status_data)
                            for idx, image_url in enumerate(image_urls):
                                try:
                                    image_response = requests.get(image_url)
                                    image_response.raise_for_status()
                                    image_bytes = image_response.content
                                except requests.RequestException:
                                    st.error("Failed to download the image. PLease try again later.")
                                    continue
                                filename_key= f"filename_input_{idx}"
                                filename =st.text_input("Name your file:", value = "generated_image.webp", key=filename_key)
                                if st.session_state.get(filename_key):
                                    st.download_button(label="Download Image",
                                               data=image_bytes,
                                               file_name=st.session_state[filename_key],
                                               mime="image/webp", 
                                               key=f"download_{idx}")
                            break
                        else: 
                            progress= int(response_data.get("progress", 0))
                            progress_bar.progress(progress)
                            status_text.info(f"Progress: {progress}%")
                            time.sleep(3)         
            else:
                    st.error(f"Error: {response.status_code} - {response.text}")

    