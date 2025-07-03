# AI Room Staging App

This project is a web application that allows users to generate AI-powered room staging images using various image generation models. The app features a Streamlit frontend for user interaction and a FastAPI backend for handling image generation requests and communication with the Stable Horde API.

---

## Features

- **Text-to-Image Generation:** Enter a prompt describing your desired room style and generate an image using advanced AI models.
- **Model Selection:** Choose from a variety of image generation models (e.g., Stable Diffusion, Dreamshaper, Realistic Vision, etc.).
- **Image Size Options:** Select from multiple output image sizes.
- **Context Image Upload:** Optionally upload a room image to guide the AI generation.
- **Progress Feedback:** See real-time progress as your image is being generated.
- **Result Display:** View and download the generated image directly from the app.

---

## Project Structure

```
ArtGenerator/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── routes.py            # API routes for image generation and status checking
│   ├── config.py            # Configuration and API keys
│   ├── utils.py             # Model and size options
│   └── streamlit_app.py     # Streamlit frontend
├── .env                     # Environment variables (not committed)
├── .gitignore
└── README.md
```

---

## How It Works

1. **User Input:**  
   The user enters a text prompt, selects a model and image size, and optionally uploads a context image via the Streamlit interface.

2. **Request Handling:**  
   The Streamlit app sends a POST request to the FastAPI backend (`/generate-image` endpoint).

3. **Image Generation:**  
   The backend validates the input, encodes the context image (if provided), and submits a request to the Stable Horde API for asynchronous image generation.

4. **Progress Tracking:**  
   The frontend polls the backend’s `/check-status/{request_id}` endpoint to check the generation status and updates a progress bar.

5. **Result Display:**  
   Once the image is ready, the app displays it to the user.

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd ArtGenerator
```

### 2. Install Dependencies

It’s recommended to use a virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, install manually:

```sh
pip install fastapi uvicorn streamlit requests python-dotenv pillow httpx
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root with your Stable Horde API key:

```
STABLE_HORDE_KEY=your_stable_horde_api_key
```

**Never commit your `.env` file!**

### 4. Run the Backend (FastAPI)

From the project root:

```sh
uvicorn app.main:app --reload
```

### 5. Run the Frontend (Streamlit)

In a new terminal (with the virtual environment activated):

```sh
streamlit run app/streamlit_app.py
```

---

## Usage

- Open the Streamlit app in your browser (usually at `http://localhost:8501`).
- Enter a prompt, select a model and image size, and optionally upload a context image.
- Click "Generate Image" and wait for the progress bar to complete.
- View and download your generated image.

---

## Customization

- **Add More Models:**  
  Edit `app/utils.py` to add or remove available models.
- **Change API Endpoints:**  
  Update `app/config.py` if you want to use a different backend or API.
- **UI Tweaks:**  
  Modify `app/streamlit_app.py` for custom interface elements.

---

## Security

- **API Keys:**  
  Your API keys are loaded from `.env` and never committed to git.
- **Secret Scanning:**  
  GitHub push protection is enabled to prevent accidental secret leaks.

---

## License

MIT License

---

## Acknowledgments

- [Stable Horde](https://stablehorde.net/) for the image generation API.
- [Streamlit](https://streamlit.io/) for the frontend framework.
- [FastAPI](https://fastapi.tiangolo.com/) for the backend API.

---

## Troubleshooting

- **Connection Errors:**  
  Ensure both FastAPI and Streamlit servers are running.
- **API Key Errors:**  
  Make sure your `.env` file is present and correct.
- **Module Not Found:**  
  Activate your virtual environment and check your Python path.

---

Enjoy generating AI-powered room staging images!
