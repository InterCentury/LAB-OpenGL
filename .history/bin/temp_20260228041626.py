import cv2
import os

video_path = r"H:\H_downloads\github--banner.mp4"
output_folder = r"H:\H_downloads\allpng"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load video
cap = cv2.VideoCapture(video_path)

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    output_path = os.path.join(output_folder, f"frame_{frame_count:04d}.png")
    cv2.imwrite(output_path, frame)

    frame_count += 1

cap.release()

print(f"Done! Extracted {frame_count} frames.")