# https://github.com/heewinkim/retinaface?tab=readme-ov-file
import cv2
import os
from retinaface import RetinaFace

SOURCE = 'testing_dataset'
DESTINATION = 'output/pending'


# init with normal accuracy option
detector = RetinaFace(quality="high")

if not os.path.exists("output"):
    os.mkdir("output")

if not os.path.exists(DESTINATION):
    os.mkdir(DESTINATION)

# for each image in source, run algo, then save in dest
for image_file in os.listdir(SOURCE):
    # Count for naming purposes
    count = 0

    # Get full file path for image
    path = os.path.join(SOURCE, image_file)

    # Load image into rgb_image
    #rgb_image = detector.read(path)
    rgb_image = cv2.imread(path)

    # Process and get faces
    faces = detector.predict(rgb_image)
    for face in faces:
        count += 1
        top, left, bottom, right = face["y1"], face["x1"], face["y2"], face["x2"]

        # Calculate 5% margin from height
        margin = int((bottom - top) * 0.3)
        top, left = (top - margin), (left - margin)
        bottom, right = (bottom + margin), (right + margin)

        # Crop the matching face
        face_crop = rgb_image[top:bottom, left:right]

        # resize to 224x224 pixels according to DDPM paper
        #face_crop = cv2.resize(face_crop, (224, 224))

        # Define output path
        output_path = f"{DESTINATION}/{count}{image_file}"

        # Save the cropped face image
        cv2.imwrite(output_path, face_crop)
