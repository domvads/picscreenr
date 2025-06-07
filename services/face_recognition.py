"""Face recognition service using face_recognition library."""

from typing import List, Tuple
import numpy as np
import face_recognition


def detect_faces(image_path: str) -> List[np.ndarray]:
    """Return face embeddings for all detected faces in an image."""
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, face_locations)
    return encodings


def compare_faces(known_embeddings: List[np.ndarray], candidate: np.ndarray, tolerance: float = 0.6) -> Tuple[int, float]:
    """Compare candidate embedding to known embeddings.

    Returns index of matching embedding and distance, or (-1, distance) if none."""
    if not known_embeddings:
        return -1, float('inf')
    distances = face_recognition.face_distance(known_embeddings, candidate)
    best_idx = np.argmin(distances)
    best_distance = distances[best_idx]
    if best_distance <= tolerance:
        return int(best_idx), float(best_distance)
    return -1, float(best_distance)
