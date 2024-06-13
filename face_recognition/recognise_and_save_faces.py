import os
import os.path
import pickle
from PIL import Image, ImageDraw, ImageFont
import face_recognition
import cv2

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

SOURCE = "../downloaded_images"
TEST_DIR = "testing_dataset"
TRAINING_DIR = "training_dataset"
OUTPUT_DIR = "output"
TRAINED_MODEL = "trained_knn_model.clf"
KNOWN_FACE_ENCODINGS = {}
COUNT = 0


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
    try:
        X_img = face_recognition.load_image_file(X_img_path)
    except Exception as e:
        print(e)
        return
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
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in
            zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]


# Load and compare faces
def crop_and_save(predictions, img_path):
    # Load image
    try:
        img = face_recognition.load_image_file(img_path)
    except Exception as e:
        print(e)
        return
    # Get file name
    img_name = img_path.split('\\')[-1]

    # Saving cropped image to their respective output folders, ignores faces predicted as unknown
    for name, (top, right, bottom, left) in predictions:
        if name != "unknown":
            print(f'{name}')
            # Compare faces
            # Get the known encoding
            if name not in KNOWN_FACE_ENCODINGS.keys():
                print(f"{name} not in dictionary")
                continue
            known_encodings = [KNOWN_FACE_ENCODINGS[name]]
            # Get the encoding to test
            face_coordinates = (top, right, bottom, left)
            face_encoding = face_recognition.face_encodings(img, [face_coordinates])[0]
            compare = compare_faces(known_encodings, face_encoding)
            if not compare:
                continue
        else:
            global COUNT
            COUNT += 1
            if COUNT % 5 != 0:
                continue
        output_dest = f'{OUTPUT_DIR}/{name}'
        if not os.path.exists(output_dest):
            os.mkdir(output_dest)
        # Calculate 5% margin from height
        margin = int((bottom - top) * 0.05)
        top, left = (top - margin), (left - margin)
        bottom, right = (bottom + margin), (right + margin)

        # Crop the matching face
        faceImg = img[top:bottom, left:right]

        try:
            # resize to 224x224 pixels according to DDPM paper
            face_crop = cv2.resize(faceImg, (224, 224))
            final = Image.fromarray(face_crop)
            final.save(f"{output_dest}/{img_name}")
        except Exception as e:
            print(e)
    return


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
            try:
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
            except Exception as e:
                print(e)
                continue

    print(f"No matching faces found in {image_path}")
    return None


def compare_faces(known_encodings, face_encoding):
    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    if matches[0]:
        return True
    else:
        return False


def load_encodings():
    for person in os.listdir(TRAINING_DIR):
        if person == "lawrencewong":
            base_image = face_recognition.load_image_file(f"{TRAINING_DIR}/{person}/base.jpg")
            known_encoding = face_recognition.face_encodings(base_image)[0]

            KNOWN_FACE_ENCODINGS[person] = known_encoding
    return


def main():
    load_encodings()

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    # For each image
    for image_file in os.listdir(SOURCE):
        img_path = os.path.join(SOURCE, image_file)

        print("Looking for faces in {}".format(image_file))

        # Find all people in the image using a trained classifier model
        # Note: You can pass in either a classifier file name or a classifier model instance
        # Can configure distance_threshold for how strict the model is in facial recognition
        predictions = predict(img_path, model_path=TRAINED_MODEL)

        crop_and_save(predictions, img_path)

        # Display results overlaid on an image
        # show_prediction_labels_on_image(os.path.join(TEST_DIR, image_file), predictions)


if __name__ == "__main__":
    main();
