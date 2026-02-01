#!/usr/bin/env python3
"""
File Manager - Field Level File Organization System
مدير الملفات - نظام تنظيم الملفات الميداني

Implements the standardized file structure for Gaza mission operations.
ينفذ هيكل الملفات القياسي لعمليات بعثة غزة.
"""

import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class MediaCategory(Enum):
    """تصنيف المواد | Media Categories"""
    RAW = "RAW"
    AUDIO = "AUDIO"
    SELECTS = "SELECTS"
    EDIT = "EDIT"
    FINAL = "FINAL"
    LOGS = "LOGS"


@dataclass
class FileInfo:
    """معلومات الملف | File Information"""
    original_path: str
    new_path: str
    category: MediaCategory
    day: int
    file_hash: str
    size_bytes: int
    created_at: datetime
    backed_up: bool = False


class FileManager:
    """
    مدير الملفات الميداني
    Field File Manager

    Manages the standardized directory structure:
    /Gaza_Mission/
    ├── RAW/
    │   ├── Day_01/
    │   ├── Day_02/
    ├── AUDIO/
    ├── SELECTS/
    ├── EDIT/
    ├── FINAL/
    └── LOGS/
    """

    # هيكل المجلدات الإلزامي | Mandatory Folder Structure
    REQUIRED_FOLDERS = [
        "RAW",
        "AUDIO",
        "SELECTS",
        "EDIT",
        "FINAL",
        "LOGS"
    ]

    # امتدادات الملفات حسب التصنيف | File Extensions by Category
    EXTENSION_MAP = {
        MediaCategory.RAW: [".jpg", ".jpeg", ".png", ".raw", ".cr2", ".nef", ".arw", ".mp4", ".mov", ".mxf"],
        MediaCategory.AUDIO: [".wav", ".mp3", ".aac", ".m4a"],
        MediaCategory.LOGS: [".json", ".txt", ".log", ".csv"]
    }

    def __init__(self, base_path: str = "./Gaza_Mission"):
        """
        Initialize File Manager

        Args:
            base_path: Base directory for mission files
        """
        self.base_path = Path(base_path)
        self.file_registry: List[FileInfo] = []
        self.current_day = 1

    def initialize_structure(self) -> None:
        """
        Create the standard directory structure
        إنشاء هيكل المجلدات القياسي
        """
        for folder in self.REQUIRED_FOLDERS:
            folder_path = self.base_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)

        # Create first day folder in RAW
        self._create_day_folder(1)

        # Create logs file
        log_file = self.base_path / "LOGS" / "file_operations.log"
        log_file.touch()

        self._log(f"Initialized mission structure at {self.base_path}")

    def _create_day_folder(self, day: int) -> Path:
        """Create a new day folder in RAW"""
        day_folder = self.base_path / "RAW" / f"Day_{day:02d}"
        day_folder.mkdir(parents=True, exist_ok=True)
        return day_folder

    def set_current_day(self, day: int) -> None:
        """Set the current mission day"""
        self.current_day = day
        self._create_day_folder(day)
        self._log(f"Current day set to {day}")

    def advance_day(self) -> int:
        """Advance to the next mission day"""
        self.current_day += 1
        self._create_day_folder(self.current_day)
        self._log(f"Advanced to day {self.current_day}")
        return self.current_day

    def _calculate_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _get_category(self, file_path: str) -> MediaCategory:
        """Determine category based on file extension"""
        ext = Path(file_path).suffix.lower()
        for category, extensions in self.EXTENSION_MAP.items():
            if ext in extensions:
                return category
        return MediaCategory.RAW

    def import_file(
        self,
        source_path: str,
        category: Optional[MediaCategory] = None,
        day: Optional[int] = None
    ) -> FileInfo:
        """
        Import a file into the mission structure

        استيراد ملف إلى هيكل البعثة

        Args:
            source_path: Path to source file
            category: Override automatic category detection
            day: Day number (uses current day if not specified)

        Returns:
            FileInfo: Information about the imported file
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Determine category and day
        file_category = category or self._get_category(source_path)
        file_day = day or self.current_day

        # Calculate destination path
        source_name = Path(source_path).name
        if file_category == MediaCategory.RAW:
            dest_folder = self.base_path / "RAW" / f"Day_{file_day:02d}"
        else:
            dest_folder = self.base_path / file_category.value

        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / source_name

        # Handle duplicate names
        counter = 1
        while dest_path.exists():
            stem = Path(source_name).stem
            suffix = Path(source_name).suffix
            dest_path = dest_folder / f"{stem}_{counter}{suffix}"
            counter += 1

        # Copy file
        shutil.copy2(source_path, dest_path)

        # Create file info
        file_info = FileInfo(
            original_path=source_path,
            new_path=str(dest_path),
            category=file_category,
            day=file_day,
            file_hash=self._calculate_hash(str(dest_path)),
            size_bytes=os.path.getsize(dest_path),
            created_at=datetime.now()
        )

        self.file_registry.append(file_info)
        self._log(f"Imported {source_name} to {dest_path}")

        return file_info

    def import_directory(
        self,
        source_dir: str,
        day: Optional[int] = None
    ) -> List[FileInfo]:
        """
        Import all supported files from a directory

        استيراد جميع الملفات المدعومة من مجلد

        Args:
            source_dir: Source directory path
            day: Day number for RAW files

        Returns:
            List of FileInfo for imported files
        """
        imported: List[FileInfo] = []

        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_info = self.import_file(file_path, day=day)
                    imported.append(file_info)
                except Exception as e:
                    self._log(f"Error importing {file}: {e}", error=True)

        return imported

    def move_to_selects(self, file_path: str) -> str:
        """Move a file to SELECTS folder"""
        return self._move_to_category(file_path, MediaCategory.SELECTS)

    def move_to_edit(self, file_path: str) -> str:
        """Move a file to EDIT folder"""
        return self._move_to_category(file_path, MediaCategory.EDIT)

    def move_to_final(self, file_path: str) -> str:
        """Move a file to FINAL folder"""
        return self._move_to_category(file_path, MediaCategory.FINAL)

    def _move_to_category(self, file_path: str, category: MediaCategory) -> str:
        """Move file to specified category folder"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        dest_folder = self.base_path / category.value
        dest_folder.mkdir(parents=True, exist_ok=True)

        file_name = Path(file_path).name
        dest_path = dest_folder / file_name

        shutil.move(file_path, dest_path)
        self._log(f"Moved {file_name} to {category.value}")

        return str(dest_path)

    def create_backup(self, backup_path: str) -> Tuple[int, int]:
        """
        Create backup of all mission files

        إنشاء نسخة احتياطية لجميع ملفات البعثة

        Args:
            backup_path: Destination path for backup

        Returns:
            Tuple of (files_backed_up, total_size_bytes)
        """
        backup_base = Path(backup_path) / f"Gaza_Mission_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        files_count = 0
        total_size = 0

        for folder in self.REQUIRED_FOLDERS:
            source = self.base_path / folder
            if source.exists():
                dest = backup_base / folder
                shutil.copytree(source, dest)

                for root, _, files in os.walk(dest):
                    for file in files:
                        files_count += 1
                        total_size += os.path.getsize(os.path.join(root, file))

        self._log(f"Backup created: {files_count} files, {total_size / 1024 / 1024:.2f} MB")
        return files_count, total_size

    def get_day_summary(self, day: int) -> Dict:
        """Get summary of files for a specific day"""
        day_folder = self.base_path / "RAW" / f"Day_{day:02d}"

        if not day_folder.exists():
            return {"day": day, "exists": False, "files": 0, "size": 0}

        files = list(day_folder.iterdir())
        total_size = sum(f.stat().st_size for f in files if f.is_file())

        return {
            "day": day,
            "exists": True,
            "files": len(files),
            "size_bytes": total_size,
            "size_mb": round(total_size / 1024 / 1024, 2)
        }

    def get_mission_summary(self) -> Dict:
        """Get complete mission file summary"""
        summary = {
            "base_path": str(self.base_path),
            "current_day": self.current_day,
            "categories": {},
            "total_files": 0,
            "total_size_bytes": 0
        }

        for folder in self.REQUIRED_FOLDERS:
            folder_path = self.base_path / folder
            if folder_path.exists():
                files = list(folder_path.rglob("*"))
                files = [f for f in files if f.is_file()]
                size = sum(f.stat().st_size for f in files)

                summary["categories"][folder] = {
                    "files": len(files),
                    "size_bytes": size,
                    "size_mb": round(size / 1024 / 1024, 2)
                }
                summary["total_files"] += len(files)
                summary["total_size_bytes"] += size

        summary["total_size_mb"] = round(summary["total_size_bytes"] / 1024 / 1024, 2)
        return summary

    def _log(self, message: str, error: bool = False) -> None:
        """Write to operations log"""
        log_file = self.base_path / "LOGS" / "file_operations.log"
        timestamp = datetime.now().isoformat()
        level = "ERROR" if error else "INFO"
        log_line = f"[{timestamp}] [{level}] {message}\n"

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception:
            pass  # Don't fail on log errors


def main():
    """CLI interface for file management"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Humanitarian Visual System - File Manager"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize mission structure"
    )
    parser.add_argument(
        "--base",
        default="./Gaza_Mission",
        help="Base path for mission files"
    )
    parser.add_argument(
        "--import-dir",
        help="Import files from directory"
    )
    parser.add_argument(
        "--day",
        type=int,
        help="Mission day number"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show mission summary"
    )

    args = parser.parse_args()

    fm = FileManager(args.base)

    if args.init:
        fm.initialize_structure()
        print(f"تم تهيئة هيكل البعثة | Mission structure initialized at: {args.base}")

    if args.day:
        fm.set_current_day(args.day)

    if args.import_dir:
        results = fm.import_directory(args.import_dir, day=args.day)
        print(f"تم استيراد | Imported: {len(results)} files")

    if args.summary:
        summary = fm.get_mission_summary()
        print("\n" + "="*50)
        print("ملخص البعثة | Mission Summary")
        print("="*50)
        print(f"المسار | Path: {summary['base_path']}")
        print(f"اليوم الحالي | Current Day: {summary['current_day']}")
        print(f"إجمالي الملفات | Total Files: {summary['total_files']}")
        print(f"الحجم الإجمالي | Total Size: {summary['total_size_mb']} MB")
        print("\nتفصيل حسب التصنيف | By Category:")
        for cat, info in summary['categories'].items():
            print(f"  {cat}: {info['files']} files ({info['size_mb']} MB)")


if __name__ == "__main__":
    main()
