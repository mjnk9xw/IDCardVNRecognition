import face_recognition
import numpy as np
from PIL import Image, ImageDraw
from IPython.display import display

def compare_face_cmt_live(link_cmt, link_live):
    # ảnh mặt cho vào đây
    src_image = face_recognition.load_image_file(link_live)
    try:
        src_face_encoding = face_recognition.face_encodings(src_image)[0]

        known_face_encodings = [
            src_face_encoding
        ]

        print('Learned encoding for', len(known_face_encodings), 'images.')

        # ảnh cmt cho vào đây
        cmt_image = face_recognition.load_image_file(link_cmt)

        face_locations = face_recognition.face_locations(cmt_image)
        face_encodings = face_recognition.face_encodings(cmt_image, face_locations)

        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        print(matches)
    except:
        print('cant detection face in file') 