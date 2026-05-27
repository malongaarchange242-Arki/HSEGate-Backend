import os
from pathlib import Path
from ultralytics import YOLO


def find_fallback_image():
    base = Path("uploads")
    if not base.exists():
        return None
    for p in base.rglob("*"):
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            return p
    return None


img_path = os.environ.get("TEST_IMAGE", "test.jpg")
img = Path(img_path)
if not img.exists():
    fallback = find_fallback_image()
    if fallback:
        print(f"test.jpg not found — using fallback image: {fallback}")
        img = fallback
    else:
        print("No test image found. Place 'test.jpg' in the project root or set TEST_IMAGE environment variable.")
        raise SystemExit(1)


model = YOLO("yolov8n.pt")

print(f"Running detection on: {img}")
results = model(str(img), save=True)
print("Détection terminée")
if results:
    try:
        out_dir = results[0].path
    except Exception:
        out_dir = "runs/detect/predict"
    print(f"Saved results in: {out_dir}")
