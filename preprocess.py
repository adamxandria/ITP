import cv2
import face_recognition
import os
import matplotlib.pyplot as plt


def encode_face(image_path):
    # Load the image
    image = face_recognition.load_image_file(image_path)
    # Get the face encodings for the image
    face_encodings = face_recognition.face_encodings(image)
    if face_encodings:
        return face_encodings[0]
    else:
        raise ValueError(f"No faces found in {image_path}")


def detect_and_crop_target_face(image_path, target_encoding, output_path):
    # Load the image
    img = cv2.imread(image_path)
    # Convert the image to RGB
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Find all face locations and face encodings in the image
    face_locations = face_recognition.face_locations(rgb_img)
    face_encodings = face_recognition.face_encodings(rgb_img, face_locations)

    # Find the face that matches the target encoding
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces([target_encoding], face_encoding)
        if matches[0]:
            # Calculate 5% margin from height
            margin = int((bottom - top) * 0.05)
            top, left = (top - margin), (left - margin)
            bottom, right = (bottom + margin), (right + margin)

            # Crop the matching face
            face_crop = img[top:bottom, left:right]

            # resize to 224x224 pixels according to DDPM paper
            face_crop = cv2.resize(face_crop, (224, 224))
            # Save the cropped face image
            cv2.imwrite(output_path, face_crop)
            return face_crop

    print(f"No matching faces found in {image_path}")
    return None


# Paths to the input images and the output directory
target_image_path = 'downloaded_images/Lawrence-Wong-2022.jpg'
input_paths = ['downloaded_images/Lawrence-Wong-2022.jpg', 'downloaded_images/image_57.jpg']
output_paths = ['downloaded_images/Lawrence-Wong-2022-cropped.jpg', 'downloaded_images/image_57-cropped.jpg']

# Encode the target face
target_encoding = encode_face(target_image_path)

# Process each image to find and crop the target face
cropped_images = []
for input_path, output_path in zip(input_paths, output_paths):
    cropped_image = detect_and_crop_target_face(input_path, target_encoding, output_path)
    if cropped_image is not None:
        cropped_images.append(cropped_image)

# Display the cropped images
for cropped_image in cropped_images:
    rgb_cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
    plt.imshow(rgb_cropped_image)
    plt.axis('off')
    plt.show()
