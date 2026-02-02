#!/usr/bin/env python3
"""
File Manager - File Organization and Management
إدارة الملفات - تنظيم وإدارة الملفات

Handles file organization, import, and backup operations
for the Humanitarian Visual System.

يتعامل مع تنظيم الملفات، الاستيراد، وعمليات النسخ الاحتياطي
لنظام التوثيق البصري الإنساني.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum
import hashlib
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MediaCategory(Enum):
    """تصنيف الوسائط | Media Category"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    RAW = "raw"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class FileManager:
    """
    إدارة الملفات
    File Management System

    Organizes files in the mission directory structure
    and handles import/export operations.

    ينظم الملفات في هيكل مجلد البعثة
    ويتعامل مع عمليات الاستيراد/التصدير.
    """

    # File extension mappings
    EXTENSIONS = {
        MediaCategory.IMAGE: ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'],
        MediaCategory.VIDEO: ['.mp4', '.mov', '.avi', '.mkv', '.mxf'],
        MediaCategory.AUDIO: ['.mp3', '.wav', '.aac', '.m4a', '.ogg'],
        MediaCategory.RAW: ['.raw', '.cr2', '.nef', '.arw', '.dng', '.orf'],
        MediaCategory.DOCUMENT: ['.pdf', '.doc', '.docx', '.txt']
    }

    # Directory structure
    DIRECTORIES = [
        "RAW",
        "IMPORTED",
        "REVIEW",
        "APPROVED",
        "REJECTED",
        "REDACTED",
        "ARCHIVE",
        "EXPORT",
        "LOGS",
        "CAPTIONS"
    ]

    def __init__(self, base_path: str):
        """
        Initialize FileManager

        Args:
            base_path: Base path for mission directory
        """
        self.base_path = Path(base_path)
        self.current_day = 0

    def initialize_structure(self) -> bool:
        """
        Initialize mission directory structure

        تهيئة هيكل مجلد البعثة

        Returns:
            True if successful
        """
        try:
            for directory in self.DIRECTORIES:
                (self.base_path / directory).mkdir(parents=True, exist_ok=True)

            logger.info(f"Initialized directory structure at: {self.base_path}")
            return True

        except Exception as e:
            logger.error(f"Error initializing structure: {e}")
            return False

    def get_category(self, file_path: str) -> MediaCategory:
        """
        Determine media category from file extension

        تحديد تصنيف الوسائط من امتداد الملف
        """
        ext = Path(file_path).suffix.lower()

        for category, extensions in self.EXTENSIONS.items():
            if ext in extensions:
                return category

        return MediaCategory.UNKNOWN

    def generate_filename(
        self,
        original_name: str,
        day: int = None,
        prefix: str = "HV"
    ) -> str:
        """
        Generate standardized filename

        توليد اسم ملف موحد

        Format: HV_YYYYMMDD_HHMMSS_originalname.ext
        """
        day = day or self.current_day
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original = Path(original_name)

        return f"{prefix}_D{day:02d}_{timestamp}_{original.stem}{original.suffix}"

    def import_file(
        self,
        source_path: str,
        day: int = None,
        copy: bool = True
    ) -> Optional[Path]:
        """
        Import file into the system

        استيراد ملف إلى النظام

        Args:
            source_path: Path to source file
            day: Mission day number
            copy: Copy file (True) or move (False)

        Returns:
            Path to imported file
        """
        source = Path(source_path)

        if not source.exists():
            logger.error(f"Source file not found: {source_path}")
            return None

        # Generate new filename
        new_name = self.generate_filename(source.name, day)

        # Determine destination based on category
        category = self.get_category(source_path)
        dest_dir = self.base_path / "IMPORTED"
        dest = dest_dir / new_name

        # Ensure directory exists
        dest_dir.mkdir(parents=True, exist_ok=True)

        try:
            if copy:
                shutil.copy2(source, dest)
            else:
                shutil.move(source, dest)

            logger.info(f"Imported: {source.name} → {new_name}")
            return dest

        except Exception as e:
            logger.error(f"Import error: {e}")
            return None

    def import_directory(
        self,
        source_dir: str,
        day: int = None,
        recursive: bool = False
    ) -> List[Dict]:
        """
        Import all files from directory

        استيراد جميع الملفات من مجلد

        Returns:
            List of import results
        """
        results = []
        source = Path(source_dir)

        if not source.exists():
            logger.error(f"Source directory not found: {source_dir}")
            return results

        # Get all valid extensions
        all_extensions = []
        for extensions in self.EXTENSIONS.values():
            all_extensions.extend(extensions)

        # Find files
        if recursive:
            files = source.rglob("*")
        else:
            files = source.glob("*")

        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in all_extensions:
                dest = self.import_file(str(file_path), day)
                if dest:
                    results.append({
                        "source": str(file_path),
                        "destination": str(dest),
                        "category": self.get_category(str(file_path))
                    })

        logger.info(f"Imported {len(results)} files from {source_dir}")
        return results

    def move_file(
        self,
        file_path: str,
        destination_folder: str
    ) -> Optional[Path]:
        """
        Move file to different folder

        نقل ملف إلى مجلد آخر
        """
        source = Path(file_path)

        if not source.exists():
            logger.error(f"File not found: {file_path}")
            return None

        dest_dir = self.base_path / destination_folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / source.name

        try:
            shutil.move(source, dest)
            logger.info(f"Moved: {source.name} → {destination_folder}/")
            return dest

        except Exception as e:
            logger.error(f"Move error: {e}")
            return None

    def get_files_in_folder(
        self,
        folder: str,
        category: MediaCategory = None
    ) -> List[Path]:
        """
        Get list of files in folder

        الحصول على قائمة الملفات في مجلد
        """
        folder_path = self.base_path / folder

        if not folder_path.exists():
            return []

        files = list(folder_path.glob("*"))

        if category:
            extensions = self.EXTENSIONS.get(category, [])
            files = [f for f in files if f.suffix.lower() in extensions]

        return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

    def get_mission_summary(self) -> Dict:
        """
        Get summary of mission files

        الحصول على ملخص ملفات البعثة
        """
        summary = {
            "base_path": str(self.base_path),
            "current_day": self.current_day,
            "total_files": 0,
            "total_size_mb": 0,
            "categories": {},
            "folders": {}
        }

        for folder in self.DIRECTORIES:
            folder_path = self.base_path / folder

            if folder_path.exists():
                files = list(folder_path.glob("*"))
                file_count = len([f for f in files if f.is_file()])
                size = sum(f.stat().st_size for f in files if f.is_file())

                summary["folders"][folder] = {
                    "files": file_count,
                    "size_mb": round(size / 1024 / 1024, 2)
                }

                summary["total_files"] += file_count
                summary["total_size_mb"] += size

        summary["total_size_mb"] = round(summary["total_size_mb"] / 1024 / 1024, 2)

        return summary

    def set_current_day(self, day: int):
        """Set current mission day"""
        self.current_day = day
        logger.info(f"Set current day to: {day}")

    def advance_day(self) -> int:
        """Advance to next mission day"""
        self.current_day += 1
        logger.info(f"Advanced to day: {self.current_day}")
        return self.current_day

    def create_backup(
        self,
        destination: str,
        folders: List[str] = None
    ) -> Tuple[int, int]:
        """
        Create backup of mission files

        إنشاء نسخة احتياطية من ملفات البعثة

        Args:
            destination: Backup destination path
            folders: Specific folders to backup (default: all)

        Returns:
            (files_count, total_size)
        """
        folders = folders or ["APPROVED", "ARCHIVE", "CAPTIONS", "LOGS"]
        dest = Path(destination)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = dest / f"HV_Backup_{timestamp}"

        files_count = 0
        total_size = 0

        try:
            for folder in folders:
                folder_path = self.base_path / folder

                if folder_path.exists():
                    backup_folder = backup_dir / folder
                    shutil.copytree(folder_path, backup_folder)

                    # Count files
                    for f in backup_folder.rglob("*"):
                        if f.is_file():
                            files_count += 1
                            total_size += f.stat().st_size

            logger.info(f"Backup created: {backup_dir}")
            return files_count, total_size

        except Exception as e:
            logger.error(f"Backup error: {e}")
            raise

    def get_file_hash(self, file_path: str) -> str:
        """
        Calculate file hash for integrity check

        حساب تجزئة الملف للتحقق من السلامة
        """
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()


if __name__ == "__main__":
    # Test
    fm = FileManager("./test_mission")
    fm.initialize_structure()
    print(fm.get_mission_summary())
