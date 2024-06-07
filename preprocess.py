import cv2
import os
import matplotlib.pyplot as plt
import math
from sklearn import neighbors
import os.path
import pickle
from PIL import Image, ImageDraw, ImageFont
import face_recognition


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

TEST_DIR = "test"
OUTPUT_DIR = "output"
KNOWN_ENCODED_IMAGES = {}


# To incorporate the face comparison function
def predict(X_img_path, knn_clf=None, model_path=None, distance_threshold=0.35):
    """
    Recognizes faces in given image using a trained KNN classifier

    :param X_img_path: path to image to be recognized
    :param knn_clf: (optional) a knn classifier object. if not specified, model_save_path must be specified.
    :param model_path: (optional) path to a pickled knn classifier. if not specified, model_save_path must be knn_clf.
    :param distance_threshold: (optional) distance threshold for face classification. the larger it is, the more chance
           of mis-classifying an unknown person as a known one.
    :return: a list of names and face locations for the recognized faces in the image: [(name, bounding box), ...].
        For faces of unrecognized persons, the name 'unknown' will be returned.
    """
    if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
        raise Exception("Invalid image path: {}".format(X_img_path))

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either through knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # Load image file and find face locations
    X_img = face_recognition.load_image_file(X_img_path)
    X_face_locations = face_recognition.face_locations(X_img)

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return []

    # Find encodings for faces in the test image
    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Predict classes and remove classifications that aren't within the threshold
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]


def crop_and_save(predictions, img_path):
    # Load image
    img = face_recognition.load_image_file(img_path)

    # Get file name
    img_name = img_path.split('\\')[-1]

    # Saving cropped image to their respective output folders, ignores faces predicted as unknown
    for name, (top, right, bottom, left) in predictions:
        if name != "unknown":
            output_dest = f'{OUTPUT_DIR}/{name}'
            if not os.path.exists(output_dest):
                os.mkdir(output_dest)
            faceImg = img[top:bottom, left:right]
            final = Image.fromarray(faceImg)
            final.save(f"{output_dest}/{img_name}")
    return


def encode_face(image_path):
    # Load the image
    image = face_recognition.load_image_file(image_path)
    # Get the face encodings for the image
    face_encodings = face_recognition.face_encodings(image)
    if face_encodings:
        return face_encodings[0]
    else:
        raise ValueError(f"No faces found in {image_path}")


# Change such that if prediction = true, get label along with target encoding,
# then crop, save and load encoded image into this function,
# if not same, discard the image and return as unknown, else just return label and not delete the cropped image,
# have to verify the accuracy of the face comparison though,
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
# for cropped_image in cropped_images:
#     rgb_cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
#     plt.imshow(rgb_cropped_image)
#     plt.axis('off')
#     plt.show()

# Main function to get encoded images and store into a global variable
# Possibly store in a dictionary