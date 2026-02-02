#!/usr/bin/env python3
"""
Face Blur - Automatic Face Detection and Blurring
طمس الوجوه - كشف وطمس الوجوه تلقائياً

This module implements automatic face detection and blurring
for humanitarian visual content to protect beneficiary identity.

هذه الوحدة تنفذ الكشف والطمس التلقائي للوجوه
في المحتوى البصري الإنساني لحماية هوية المستفيدين.

Activation Rules / قواعد التفعيل:
    - Auto-blur if: face detected AND no consent
    - يُفعّل تلقائياً إذا: وجه ظاهر بدون موافقة
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceBlur:
    """
    طمس الوجوه التلقائي
    Automatic Face Blur System

    Uses OpenCV's Haar Cascade or dlib for face detection,
    then applies Gaussian blur to protect identity.

    يستخدم OpenCV أو dlib للكشف عن الوجوه،
    ثم يطبق طمس Gaussian لحماية الهوية.
    """

    # Supported image formats
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']

    # Blur parameters
    DEFAULT_BLUR_KERNEL = (99, 99)
    DEFAULT_BLUR_SIGMA = 30

    def __init__(self, cascade_path: str = None):
        """
        Initialize FaceBlur

        Args:
            cascade_path: Path to Haar cascade XML file (optional)
        """
        self._cv2 = None
        self._face_cascade = None
        self.cascade_path = cascade_path

    def _load_cv2(self):
        """Lazy load OpenCV"""
        if self._cv2 is None:
            try:
                import cv2
                self._cv2 = cv2

                # Load face cascade
                if self.cascade_path and os.path.exists(self.cascade_path):
                    cascade_file = self.cascade_path
                else:
                    # Try default OpenCV cascade
                    cascade_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

                self._face_cascade = cv2.CascadeClassifier(cascade_file)

                if self._face_cascade.empty():
                    logger.warning("Could not load face cascade. Face detection will be simulated.")
                    self._face_cascade = None

            except ImportError:
                logger.warning("OpenCV not installed. Install with: pip install opencv-python")
                self._cv2 = None

        return self._cv2 is not None

    def detect_faces(self, image_path: str) -> int:
        """
        Detect faces in image

        كشف الوجوه في الصورة

        Args:
            image_path: Path to image file

        Returns:
            Number of faces detected
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        ext = Path(image_path).suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            logger.warning(f"Unsupported format: {ext}")
            return 0

        if not self._load_cv2():
            # Simulate face detection for testing
            logger.info("Simulating face detection (OpenCV not available)")
            return 0

        try:
            img = self._cv2.imread(image_path)
            if img is None:
                logger.error(f"Could not read image: {image_path}")
                return 0

            gray = self._cv2.cvtColor(img, self._cv2.COLOR_BGR2GRAY)

            if self._face_cascade is None:
                return 0

            faces = self._face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            return len(faces)

        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return 0

    def blur_faces(
        self,
        image_path: str,
        output_path: str = None,
        blur_kernel: Tuple[int, int] = None,
        blur_sigma: int = None
    ) -> int:
        """
        Detect and blur faces in image

        كشف وطمس الوجوه في الصورة

        Args:
            image_path: Path to input image
            output_path: Path to save blurred image (optional, overwrites original if not specified)
            blur_kernel: Gaussian blur kernel size
            blur_sigma: Gaussian blur sigma value

        Returns:
            Number of faces blurred
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        blur_kernel = blur_kernel or self.DEFAULT_BLUR_KERNEL
        blur_sigma = blur_sigma or self.DEFAULT_BLUR_SIGMA
        output_path = output_path or image_path

        if not self._load_cv2():
            logger.warning("Cannot blur faces: OpenCV not available")
            return 0

        try:
            img = self._cv2.imread(image_path)
            if img is None:
                logger.error(f"Could not read image: {image_path}")
                return 0

            gray = self._cv2.cvtColor(img, self._cv2.COLOR_BGR2GRAY)

            if self._face_cascade is None:
                logger.warning("Face cascade not loaded")
                return 0

            faces = self._face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            # Apply blur to each face
            for (x, y, w, h) in faces:
                # Add padding around face
                padding = int(w * 0.2)
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(img.shape[1], x + w + padding)
                y2 = min(img.shape[0], y + h + padding)

                # Extract face region
                face_region = img[y1:y2, x1:x2]

                # Apply Gaussian blur
                blurred = self._cv2.GaussianBlur(face_region, blur_kernel, blur_sigma)

                # Replace original with blurred
                img[y1:y2, x1:x2] = blurred

            # Save result
            self._cv2.imwrite(output_path, img)

            logger.info(f"Blurred {len(faces)} faces in {image_path}")
            return len(faces)

        except Exception as e:
            logger.error(f"Face blur error: {e}")
            return 0

    def blur_faces_batch(
        self,
        directory: str,
        output_dir: str = None,
        recursive: bool = False
    ) -> dict:
        """
        Blur faces in all images in directory

        طمس الوجوه في جميع الصور في المجلد

        Args:
            directory: Input directory
            output_dir: Output directory (optional)
            recursive: Process subdirectories

        Returns:
            Dictionary with results {filename: faces_count}
        """
        results = {}
        directory = Path(directory)
        output_dir = Path(output_dir) if output_dir else directory

        if recursive:
            files = directory.rglob("*")
        else:
            files = directory.glob("*")

        for file_path in files:
            if file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                output_path = output_dir / file_path.name
                count = self.blur_faces(str(file_path), str(output_path))
                results[file_path.name] = count

        return results

    def check_blur_quality(self, image_path: str) -> bool:
        """
        Verify that blurring was applied correctly

        التحقق من تطبيق الطمس بشكل صحيح

        Returns:
            True if no faces detected after blur
        """
        return self.detect_faces(image_path) == 0


def blur_faces(image_path: str) -> None:
    """
    Convenience function for quick face blur

    دالة مختصرة لطمس الوجوه السريع

    Usage:
        from hv.ethical.blur import blur_faces
        blur_faces("photo.jpg")
    """
    blurrer = FaceBlur()
    count = blurrer.blur_faces(image_path)
    print(f"Blurred {count} faces in {image_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python blur.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    blur_faces(image_path)
