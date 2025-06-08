"""Feature matching based on clothing and color histograms."""

from typing import List, Tuple
import numpy as np
import cv2


def extract_color_histogram(image_path: str, bins: int = 32) -> np.ndarray:
    """Compute a color histogram for the image."""
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([image], [0, 1, 2], None, [bins, bins, bins], [0, 180, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()


def compare_histograms(known_hists: List[np.ndarray], candidate: np.ndarray, threshold: float = 0.3) -> Tuple[int, float]:
    """Compare candidate histogram with known histograms using correlation."""
    if not known_hists:
        return -1, -1.0
    scores = [cv2.compareHist(h.astype('float32'), candidate.astype('float32'), cv2.HISTCMP_CORREL) for h in known_hists]
    best_idx = int(np.argmax(scores))
    best_score = float(scores[best_idx])
    if best_score >= threshold:
        return best_idx, best_score
    return -1, best_score
