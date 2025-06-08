"""Flask application for picscreenr."""

import os
import io
from typing import List
from flask import Flask, request, jsonify, send_from_directory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PIL import Image
import numpy as np
import pickle

from models import Base, Image as ImageModel, Person, PersonImage
from services.image_caption import load_model as load_caption_model, generate_caption, extract_tags
from services.face_recognition import detect_faces, compare_faces
from services.feature_matching import extract_color_histogram, compare_histograms

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
DB_PATH = os.path.join(os.getcwd(), "picscreenr.db")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

caption_model, caption_processor, caption_tokenizer = load_caption_model()

@app.post('/upload_image')
def upload_image():
    session = SessionLocal()
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file provided'}), 400
    image = Image.open(file.stream).convert('RGB')
    # normalize size
    image = image.resize((512, 512))
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    image.save(filename)

    caption = generate_caption(caption_model, caption_processor, caption_tokenizer, filename)
    tags = extract_tags(caption)
    image_record = ImageModel(filename=filename, caption=caption, tags=','.join(tags))
    session.add(image_record)
    session.commit()

    # face recognition
    known_persons = session.query(Person).all()
    known_embeddings = [pickle.loads(p.face_embedding) for p in known_persons]
    face_embeddings = detect_faces(filename)
    persons_in_image: List[PersonImage] = []

    for embedding in face_embeddings:
        idx, distance = compare_faces(known_embeddings, embedding)
        if idx >= 0:
            person = known_persons[idx]
        else:
            person = Person(face_embedding=pickle.dumps(embedding))
            session.add(person)
            session.commit()
            known_persons.append(person)
            known_embeddings.append(embedding)
        link = PersonImage(person_id=person.id, image_id=image_record.id, confidence=1-distance)
        session.add(link)
        persons_in_image.append(link)

    # clothing features
    known_features = [pickle.loads(p.feature_vector) if p.feature_vector else None for p in known_persons]
    candidate_hist = extract_color_histogram(filename)
    idx, score = compare_histograms([f for f in known_features if f is not None], candidate_hist)
    if idx >= 0:
        person = known_persons[idx]
        link = PersonImage(person_id=person.id, image_id=image_record.id, confidence=score)
        session.add(link)
        persons_in_image.append(link)
    else:
        # save histogram to new or existing person
        if face_embeddings:
            person = persons_in_image[0].person
        else:
            person = Person(feature_vector=pickle.dumps(candidate_hist))
            session.add(person)
            session.commit()
        person.feature_vector = pickle.dumps(candidate_hist)

    session.commit()
    return jsonify({'image_id': image_record.id, 'caption': caption, 'tags': tags})

@app.get('/description/<int:image_id>')
def get_description(image_id: int):
    session = SessionLocal()
    image_record = session.query(ImageModel).filter(ImageModel.id == image_id).first()
    if not image_record:
        return jsonify({'error': 'Image not found'}), 404
    return jsonify({'caption': image_record.caption, 'tags': image_record.tags.split(',')})

@app.get('/identify/<int:image_id>')
def identify(image_id: int):
    session = SessionLocal()
    links = session.query(PersonImage).filter(PersonImage.image_id == image_id).all()
    result = []
    for link in links:
        result.append({'person_id': link.person_id, 'confidence': link.confidence})
    return jsonify({'persons': result})

@app.get('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
