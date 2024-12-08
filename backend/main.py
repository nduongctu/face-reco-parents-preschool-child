from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.login import router as auth_router
from backend.admin import router as admin_router
from backend.middleware import TokenExpiryMiddleware
from deepface import DeepFace

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TokenExpiryMiddleware)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

app.mount("/images", StaticFiles(directory="images"), name="images")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def warmup_deepface_model():
    print("Warming up DeepFace model...")
    dummy_image = "temp_image.jpg"  # Sử dụng một ảnh dummy có sẵn
    DeepFace.represent(img_path=dummy_image, model_name="Facenet", enforce_detection=False)
    print("DeepFace model is warmed up and ready!")


@app.on_event("startup")
async def on_startup():
    warmup_deepface_model()


if __name__ == "__main__":
    import uvicorn

    warmup_deepface_model()

    uvicorn.run(app, host="0.0.0.0", port=8000)
