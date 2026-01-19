import os
import pandas as pd
from pathlib import Path
from ultralytics import YOLO

IMAGES_DIR = Path("data/raw/images")
OUTPUT_CSV = Path("data/yolo_detections.csv")

model = YOLO("yolov8n.pt")
results_list = []

for channel in IMAGES_DIR.iterdir():
    if not channel.is_dir():
        continue
    for image_path in channel.glob("*.jpg"):
        result = model.predict(str(image_path), save=False)
        for r in result:
            for obj in r.boxes:
                results_list.append({
                    "message_id": image_path.stem,
                    "channel_name": channel.name,
                    "detected_class": obj.cls.item(),
                    "confidence_score": float(obj.conf.item())
                })

df = pd.DataFrame(results_list)
df.to_csv(OUTPUT_CSV, index=False)
print(f"YOLO detections saved to {OUTPUT_CSV}")
