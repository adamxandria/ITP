import math
from sklearn import neighbors
import os
import os.path
import pickle
from PIL import Image, ImageDraw, ImageFont
import face_recognition


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


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

    # Find encodings for faces in the test iamge
    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Predict classes and remove classifications that aren't within the threshold
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]


def crop_and_save(predictions, output_dir, img_path):
    img = face_recognition.load_image_file(img_path)

    img_name = img_path.split('\\')[-1]
    for name, (top, right, bottom, left) in predictions:
        if name != "unknown":
            output_dest = f'{output_dir}/{name}'
            if not os.path.exists(output_dest):
                os.mkdir(output_dest)
            faceImg = img[top:bottom, left:right]
            final = Image.fromarray(faceImg)
            final.save(f"{output_dest}/{img_name}")
    return


def show_prediction_labels_on_image(img_path, predictions):
    """
    Shows the face recognition results visually.

    :param img_path: path to image to be recognized
    :param predictions: results of the predict function
    :return:
    """
    pil_image = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(pil_image)
    font = ImageFont.load_default()

    for name, (top, right, bottom, left) in predictions:
        # Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        # There's a bug in Pillow where it blows up with non-UTF-8 text
        # when using the default bitmap font
        name = str(name.encode("UTF-8"))

        # Draw a label with a name below the face
        # text_width, text_height = draw.textsize(name)
        text_bbox = draw.textbbox((left, bottom), name, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    # Remove the drawing library from memory as per the Pillow docs
    del draw

    # Display the resulting image
    pil_image.show()


if __name__ == "__main__":
    test_dir = "testing_dataset"
    output_dir = "output"

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # For each image
    for image_file in os.listdir(test_dir):
        img_path = os.path.join(test_dir, image_file)

        print("Looking for faces in {}".format(image_file))

        # Find all people in the image using a trained classifier model
        # Note: You can pass in either a classifier file name or a classifier model instance
        # Can configure distance_threshold for how strict the model is in facial recognition
        predictions = predict(img_path, model_path="trained_knn_model.clf")

        crop_and_save(predictions, output_dir, img_path)

        # Print results on the console
        # for name, (top, right, bottom, left) in predictions:
        #     print("- Found {} at ({}, {})".format(name, left, top))

        # Display results overlaid on an image
        #show_prediction_labels_on_image(os.path.join(test_dir, image_file), predictions)