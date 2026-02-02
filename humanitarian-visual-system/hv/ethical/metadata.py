#!/usr/bin/env python3
"""
Metadata Stripper - Remove Sensitive Metadata
إزالة البيانات الحساسة

This module removes sensitive metadata from media files
to protect location, device information, and timing data.

هذه الوحدة تزيل البيانات الحساسة من ملفات الوسائط
لحماية الموقع، معلومات الجهاز، وبيانات التوقيت.

Removed Data / البيانات المحذوفة:
    - GPS Coordinates / إحداثيات GPS
    - Exact Timestamp / التوقيت الدقيق
    - Device ID / معرّف الجهاز
    - Camera Serial / رقم الكاميرا التسلسلي
    - Software Version / إصدار البرنامج
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataStripper:
    """
    إزالة البيانات الحساسة
    Sensitive Metadata Removal System

    Removes GPS, device info, and precise timing from media files
    while preserving essential technical metadata.

    يزيل GPS، معلومات الجهاز، والتوقيت الدقيق من ملفات الوسائط
    مع الحفاظ على البيانات الفنية الأساسية.
    """

    # Supported formats
    SUPPORTED_FORMATS = {
        'image': ['.jpg', '.jpeg', '.png', '.tiff', '.webp', '.raw', '.cr2', '.nef', '.arw'],
        'video': ['.mp4', '.mov', '.avi', '.mxf'],
        'audio': ['.mp3', '.wav', '.aac', '.m4a']
    }

    # Sensitive metadata fields to remove
    SENSITIVE_FIELDS = [
        # GPS data
        'GPSLatitude',
        'GPSLatitudeRef',
        'GPSLongitude',
        'GPSLongitudeRef',
        'GPSAltitude',
        'GPSAltitudeRef',
        'GPSTimeStamp',
        'GPSDateStamp',
        'GPSPosition',
        'GPSCoordinates',
        'GPSInfo',

        # Device identification
        'SerialNumber',
        'CameraSerialNumber',
        'InternalSerialNumber',
        'BodySerialNumber',
        'LensSerialNumber',
        'DeviceID',
        'UniqueID',
        'ImageUniqueID',

        # Detailed timing (keep date, remove precise time)
        'SubSecTime',
        'SubSecTimeOriginal',
        'SubSecTimeDigitized',

        # Software/Device info
        'Software',
        'ProcessingSoftware',
        'HostComputer',
        'MakerNote',
        'UserComment',

        # Owner info
        'OwnerName',
        'CameraOwnerName',
        'Artist',
        'Copyright',

        # Location-related text
        'Location',
        'LocationInfo',
        'City',
        'Province-State',
        'Country-PrimaryLocationName',
    ]

    # Fields to preserve
    PRESERVE_FIELDS = [
        'ImageWidth',
        'ImageHeight',
        'Orientation',
        'ColorSpace',
        'ExifImageWidth',
        'ExifImageHeight',
        'Make',  # Camera brand (not serial)
        'Model',  # Camera model (not serial)
        'DateTimeOriginal',  # Date only, not subseconds
    ]

    def __init__(self, log_removals: bool = True):
        """
        Initialize MetadataStripper

        Args:
            log_removals: Whether to log removed metadata
        """
        self.log_removals = log_removals
        self._pil = None
        self._piexif = None

    def _load_dependencies(self) -> bool:
        """Lazy load PIL/Pillow"""
        if self._pil is None:
            try:
                from PIL import Image
                self._pil = Image

                try:
                    import piexif
                    self._piexif = piexif
                except ImportError:
                    logger.warning("piexif not installed. Using basic metadata removal.")
                    self._piexif = None

                return True

            except ImportError:
                logger.warning("Pillow not installed. Install with: pip install Pillow piexif")
                return False

        return True

    def strip(
        self,
        file_path: str,
        output_path: str = None,
        preserve_date: bool = True
    ) -> Dict[str, Any]:
        """
        Strip sensitive metadata from file

        إزالة البيانات الحساسة من الملف

        Args:
            file_path: Path to input file
            output_path: Path to save cleaned file (optional, overwrites if not specified)
            preserve_date: Keep general date (not precise time)

        Returns:
            Dictionary of removed metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        output_path = output_path or file_path
        removed = {}

        ext = Path(file_path).suffix.lower()

        # Determine file type
        file_type = None
        for ftype, extensions in self.SUPPORTED_FORMATS.items():
            if ext in extensions:
                file_type = ftype
                break

        if file_type is None:
            logger.warning(f"Unsupported format: {ext}")
            return removed

        if file_type == 'image':
            removed = self._strip_image_metadata(file_path, output_path, preserve_date)
        elif file_type == 'video':
            removed = self._strip_video_metadata(file_path, output_path)
        elif file_type == 'audio':
            removed = self._strip_audio_metadata(file_path, output_path)

        if self.log_removals and removed:
            logger.info(f"Stripped {len(removed)} metadata fields from {file_path}")

        return removed

    def _strip_image_metadata(
        self,
        file_path: str,
        output_path: str,
        preserve_date: bool
    ) -> Dict[str, Any]:
        """Strip metadata from image file"""
        removed = {}

        if not self._load_dependencies():
            # Fallback: create clean copy without any metadata
            return self._strip_image_basic(file_path, output_path)

        try:
            img = self._pil.open(file_path)

            if self._piexif is not None:
                # Advanced stripping with piexif
                try:
                    exif_dict = self._piexif.load(img.info.get('exif', b''))

                    # Remove sensitive fields from each IFD
                    for ifd_name in ['0th', 'Exif', 'GPS', '1st', 'Interop']:
                        ifd = exif_dict.get(ifd_name, {})
                        if isinstance(ifd, dict):
                            for tag, value in list(ifd.items()):
                                tag_name = self._piexif.TAGS.get(ifd_name, {}).get(tag, {}).get('name', str(tag))
                                if self._should_remove(tag_name):
                                    removed[tag_name] = str(value)[:100]  # Truncate for logging
                                    del exif_dict[ifd_name][tag]

                    # Completely remove GPS IFD
                    if 'GPS' in exif_dict:
                        for tag, value in exif_dict['GPS'].items():
                            tag_name = self._piexif.GPSIFD.get(tag, str(tag))
                            removed[f"GPS:{tag_name}"] = str(value)[:100]
                        exif_dict['GPS'] = {}

                    # Save with cleaned EXIF
                    exif_bytes = self._piexif.dump(exif_dict)
                    img.save(output_path, exif=exif_bytes)

                except Exception as e:
                    logger.warning(f"piexif error: {e}, using basic stripping")
                    return self._strip_image_basic(file_path, output_path)

            else:
                # Basic stripping without piexif
                return self._strip_image_basic(file_path, output_path)

        except Exception as e:
            logger.error(f"Image metadata stripping error: {e}")
            return removed

        return removed

    def _strip_image_basic(self, file_path: str, output_path: str) -> Dict[str, Any]:
        """
        Basic metadata stripping - removes ALL metadata

        الإزالة الأساسية - تحذف جميع البيانات الوصفية
        """
        removed = {"all_metadata": "removed"}

        if not self._load_dependencies():
            # Cannot process without PIL
            import shutil
            shutil.copy2(file_path, output_path)
            return {}

        try:
            img = self._pil.open(file_path)

            # Create new image without metadata
            clean = self._pil.new(img.mode, img.size)
            clean.putdata(list(img.getdata()))

            # Save clean image
            clean.save(output_path)

            logger.info(f"Basic metadata strip completed: {file_path}")

        except Exception as e:
            logger.error(f"Basic stripping error: {e}")
            return {}

        return removed

    def _strip_video_metadata(self, file_path: str, output_path: str) -> Dict[str, Any]:
        """Strip metadata from video file"""
        removed = {}

        try:
            import subprocess

            # Use ffmpeg to strip metadata
            cmd = [
                'ffmpeg', '-y',
                '-i', file_path,
                '-map_metadata', '-1',  # Remove all metadata
                '-c:v', 'copy',  # Copy video stream
                '-c:a', 'copy',  # Copy audio stream
                output_path if output_path != file_path else f"{file_path}.tmp"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                if output_path == file_path:
                    os.replace(f"{file_path}.tmp", file_path)
                removed["video_metadata"] = "removed"
            else:
                logger.warning(f"ffmpeg error: {result.stderr}")

        except FileNotFoundError:
            logger.warning("ffmpeg not installed. Video metadata stripping skipped.")
        except Exception as e:
            logger.error(f"Video metadata stripping error: {e}")

        return removed

    def _strip_audio_metadata(self, file_path: str, output_path: str) -> Dict[str, Any]:
        """Strip metadata from audio file"""
        removed = {}

        try:
            import subprocess

            # Use ffmpeg to strip metadata
            cmd = [
                'ffmpeg', '-y',
                '-i', file_path,
                '-map_metadata', '-1',
                '-c:a', 'copy',
                output_path if output_path != file_path else f"{file_path}.tmp"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                if output_path == file_path:
                    os.replace(f"{file_path}.tmp", file_path)
                removed["audio_metadata"] = "removed"
            else:
                logger.warning(f"ffmpeg error: {result.stderr}")

        except FileNotFoundError:
            logger.warning("ffmpeg not installed. Audio metadata stripping skipped.")
        except Exception as e:
            logger.error(f"Audio metadata stripping error: {e}")

        return removed

    def _should_remove(self, field_name: str) -> bool:
        """Check if field should be removed"""
        field_lower = field_name.lower()
        for sensitive in self.SENSITIVE_FIELDS:
            if sensitive.lower() in field_lower or field_lower in sensitive.lower():
                return True
        return False

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get current metadata from file (for inspection)

        الحصول على البيانات الحالية من الملف (للفحص)
        """
        metadata = {}

        if not self._load_dependencies():
            return metadata

        try:
            ext = Path(file_path).suffix.lower()

            if ext in self.SUPPORTED_FORMATS['image']:
                img = self._pil.open(file_path)
                exif = img._getexif()
                if exif:
                    from PIL.ExifTags import TAGS
                    for tag_id, value in exif.items():
                        tag_name = TAGS.get(tag_id, str(tag_id))
                        metadata[tag_name] = str(value)[:100]

        except Exception as e:
            logger.error(f"Error reading metadata: {e}")

        return metadata

    def has_sensitive_data(self, file_path: str) -> bool:
        """
        Check if file contains sensitive metadata

        التحقق من وجود بيانات حساسة في الملف
        """
        metadata = self.get_metadata(file_path)

        for field_name in metadata.keys():
            if self._should_remove(field_name):
                return True

        return False

    def strip_batch(
        self,
        directory: str,
        output_dir: str = None,
        recursive: bool = False
    ) -> Dict[str, Dict]:
        """
        Strip metadata from all files in directory

        إزالة البيانات من جميع الملفات في المجلد
        """
        results = {}
        directory = Path(directory)
        output_dir = Path(output_dir) if output_dir else directory

        all_extensions = []
        for extensions in self.SUPPORTED_FORMATS.values():
            all_extensions.extend(extensions)

        if recursive:
            files = directory.rglob("*")
        else:
            files = directory.glob("*")

        for file_path in files:
            if file_path.suffix.lower() in all_extensions:
                output_path = output_dir / file_path.name
                removed = self.strip(str(file_path), str(output_path))
                results[file_path.name] = removed

        return results


def strip_metadata(path: str) -> None:
    """
    Convenience function for quick metadata stripping

    دالة مختصرة لإزالة البيانات بسرعة

    Usage:
        from hv.ethical.metadata import strip_metadata
        strip_metadata("photo.jpg")
    """
    stripper = MetadataStripper()
    removed = stripper.strip(path)
    print(f"Stripped {len(removed)} fields from {path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python metadata.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    strip_metadata(file_path)
