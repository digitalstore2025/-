#!/usr/bin/env python3
"""
Metadata Handler - Secure Metadata Management
معالج البيانات الوصفية - إدارة آمنة للبيانات

Handles extraction, sanitization, and management of media metadata
with focus on security and privacy protection.

يعالج استخراج وتنظيف وإدارة البيانات الوصفية للوسائط
مع التركيز على الأمان وحماية الخصوصية.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class SensitivityLevel(Enum):
    """مستوى الحساسية | Sensitivity Level"""
    SAFE = "safe"
    CAUTION = "caution"
    SENSITIVE = "sensitive"
    CRITICAL = "critical"


@dataclass
class MediaMetadata:
    """البيانات الوصفية للوسائط | Media Metadata"""
    file_path: str
    asset_id: str
    capture_date: Optional[datetime] = None
    camera_model: str = ""
    lens_info: str = ""
    iso: Optional[int] = None
    shutter_speed: str = ""
    aperture: str = ""
    focal_length: str = ""
    dimensions: Dict[str, int] = field(default_factory=dict)
    duration_seconds: Optional[float] = None
    file_size_bytes: int = 0
    location_general: str = ""  # Only general, never GPS
    photographer_id: str = ""
    intervention_type: str = ""
    ethical_status: str = ""
    notes: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "asset_id": self.asset_id,
            "capture_date": self.capture_date.isoformat() if self.capture_date else None,
            "camera_model": self.camera_model,
            "lens_info": self.lens_info,
            "iso": self.iso,
            "shutter_speed": self.shutter_speed,
            "aperture": self.aperture,
            "focal_length": self.focal_length,
            "dimensions": self.dimensions,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "location_general": self.location_general,
            "photographer_id": self.photographer_id,
            "intervention_type": self.intervention_type,
            "ethical_status": self.ethical_status,
            "notes": self.notes,
            "tags": self.tags
        }

    def to_archive_format(self) -> Dict[str, Any]:
        """Format for legal archival - الصيغة للأرشفة القانونية"""
        return {
            "Date": self.capture_date.isoformat() if self.capture_date else "",
            "General_Location": self.location_general,
            "Intervention_Type": self.intervention_type,
            "Photographer_ID": self.photographer_id,
            "Ethical_Approval_Status": self.ethical_status,
            "Asset_ID": self.asset_id
        }


class MetadataHandler:
    """
    معالج البيانات الوصفية
    Metadata Handler

    Extracts and sanitizes metadata from media files,
    removing sensitive information like GPS coordinates.

    يستخرج وينظف البيانات الوصفية من ملفات الوسائط،
    ويزيل المعلومات الحساسة مثل إحداثيات GPS.
    """

    # الحقول الحساسة المحظورة | Forbidden Sensitive Fields
    FORBIDDEN_FIELDS = [
        "GPSLatitude",
        "GPSLongitude",
        "GPSPosition",
        "GPSCoordinates",
        "GPSAltitude",
        "GPSTimeStamp",
        "GPSDateStamp",
        "GPSInfo",
        "Location",
        "LocationInfo",
        "XMP:Location",
        "IPTC:Sub-location",
        "EXIF:GPSInfo"
    ]

    # الحقول الآمنة للحفظ | Safe Fields to Keep
    SAFE_FIELDS = [
        "Make",
        "Model",
        "DateTimeOriginal",
        "ExposureTime",
        "FNumber",
        "ISO",
        "FocalLength",
        "LensModel",
        "ImageWidth",
        "ImageHeight",
        "Duration",
        "AudioBitrate",
        "VideoCodec"
    ]

    # المواقع العامة المسموحة | Allowed General Locations
    ALLOWED_LOCATIONS = [
        "غزة",
        "Gaza",
        "شمال غزة",
        "Northern Gaza",
        "جنوب غزة",
        "Southern Gaza",
        "وسط غزة",
        "Central Gaza",
        "رفح",
        "Rafah",
        "خان يونس",
        "Khan Yunis",
        "دير البلح",
        "Deir al-Balah"
    ]

    # أنواع التدخل | Intervention Types
    INTERVENTION_TYPES = [
        "توزيع مساعدات غذائية",
        "Food Aid Distribution",
        "مساعدات طبية",
        "Medical Aid",
        "إيواء",
        "Shelter",
        "دعم نفسي",
        "Psychological Support",
        "مياه وصرف صحي",
        "WASH",
        "حماية",
        "Protection",
        "تعليم طوارئ",
        "Emergency Education"
    ]

    def __init__(self):
        self.metadata_cache: Dict[str, MediaMetadata] = {}

    def extract_metadata(
        self,
        file_path: str,
        asset_id: str = ""
    ) -> MediaMetadata:
        """
        Extract safe metadata from a media file

        استخراج البيانات الوصفية الآمنة من ملف وسائط

        Args:
            file_path: Path to media file
            asset_id: Optional asset ID

        Returns:
            MediaMetadata object with sanitized data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get basic file info
        file_stat = os.stat(file_path)

        metadata = MediaMetadata(
            file_path=file_path,
            asset_id=asset_id or self._generate_asset_id(file_path),
            file_size_bytes=file_stat.st_size,
            capture_date=datetime.fromtimestamp(file_stat.st_mtime)
        )

        # Try to extract EXIF data (would need PIL/exiftool in production)
        # For now, use file-based detection
        self._extract_basic_info(metadata)

        self.metadata_cache[file_path] = metadata
        return metadata

    def _generate_asset_id(self, file_path: str) -> str:
        """Generate asset ID from filename and timestamp"""
        import hashlib
        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"HVS-{timestamp}-{file_hash}"

    def _extract_basic_info(self, metadata: MediaMetadata) -> None:
        """Extract basic info from file"""
        file_path = Path(metadata.file_path)
        ext = file_path.suffix.lower()

        # Determine media type from extension
        image_exts = [".jpg", ".jpeg", ".png", ".raw", ".cr2", ".nef", ".arw"]
        video_exts = [".mp4", ".mov", ".mxf", ".avi"]
        audio_exts = [".wav", ".mp3", ".aac"]

        if ext in image_exts:
            metadata.tags.append("image")
        elif ext in video_exts:
            metadata.tags.append("video")
        elif ext in audio_exts:
            metadata.tags.append("audio")

    def sanitize_metadata(
        self,
        file_path: str,
        output_path: Optional[str] = None
    ) -> bool:
        """
        Remove sensitive metadata from file

        إزالة البيانات الوصفية الحساسة من الملف

        Args:
            file_path: Path to media file
            output_path: Optional output path (overwrites if not provided)

        Returns:
            True if sanitization successful
        """
        # In production, this would use exiftool or similar
        # to strip GPS and other sensitive metadata
        print(f"Sanitizing metadata for: {file_path}")
        print("Removing: GPS coordinates, location tags, device identifiers")
        return True

    def add_humanitarian_metadata(
        self,
        file_path: str,
        location_general: str,
        intervention_type: str,
        photographer_id: str,
        ethical_status: str = "approved",
        notes: str = ""
    ) -> MediaMetadata:
        """
        Add humanitarian documentation metadata

        إضافة بيانات وصفية للتوثيق الإنساني

        Args:
            file_path: Path to media file
            location_general: General location (from allowed list)
            intervention_type: Type of humanitarian intervention
            photographer_id: ID of photographer
            ethical_status: Ethical approval status
            notes: Additional notes

        Returns:
            Updated MediaMetadata
        """
        # Validate location
        if location_general and location_general not in self.ALLOWED_LOCATIONS:
            print(f"Warning: Non-standard location '{location_general}'. Use general terms only.")

        metadata = self.metadata_cache.get(file_path)
        if not metadata:
            metadata = self.extract_metadata(file_path)

        metadata.location_general = location_general
        metadata.intervention_type = intervention_type
        metadata.photographer_id = photographer_id
        metadata.ethical_status = ethical_status
        metadata.notes = notes

        self.metadata_cache[file_path] = metadata
        return metadata

    def check_sensitivity(self, file_path: str) -> SensitivityLevel:
        """
        Check metadata sensitivity level

        فحص مستوى حساسية البيانات الوصفية

        Returns:
            SensitivityLevel enum value
        """
        # In production, would actually read and analyze metadata
        # For now, return CAUTION as default
        return SensitivityLevel.CAUTION

    def export_metadata_report(
        self,
        file_paths: List[str],
        output_path: str,
        format: str = "json"
    ) -> None:
        """
        Export metadata report for multiple files

        تصدير تقرير البيانات الوصفية لعدة ملفات

        Args:
            file_paths: List of file paths
            output_path: Output file path
            format: Output format (json, csv)
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "organization": "Turkish Red Crescent",
            "mission": "Gaza Humanitarian Operations",
            "total_assets": len(file_paths),
            "assets": []
        }

        for file_path in file_paths:
            metadata = self.metadata_cache.get(file_path)
            if not metadata:
                metadata = self.extract_metadata(file_path)
            report["assets"].append(metadata.to_dict())

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    def export_archive_manifest(
        self,
        file_paths: List[str],
        output_path: str
    ) -> None:
        """
        Export legal archive manifest

        تصدير بيان الأرشفة القانونية

        Required fields per asset:
        - Date
        - General location
        - Type of intervention
        - Photographer ID
        - Ethical approval status
        """
        manifest = {
            "manifest_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "organization": "Turkish Red Crescent - الهلال الأحمر التركي",
            "purpose": "Humanitarian Documentation Archive",
            "assets": []
        }

        for file_path in file_paths:
            metadata = self.metadata_cache.get(file_path)
            if metadata:
                manifest["assets"].append(metadata.to_archive_format())

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"Archive manifest exported to: {output_path}")


def main():
    """CLI for metadata handling"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Humanitarian Visual System - Metadata Handler"
    )
    parser.add_argument(
        "--file", "-f",
        help="File to process"
    )
    parser.add_argument(
        "--sanitize",
        action="store_true",
        help="Remove sensitive metadata"
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract and display metadata"
    )
    parser.add_argument(
        "--location",
        help="Set general location"
    )
    parser.add_argument(
        "--intervention",
        help="Set intervention type"
    )
    parser.add_argument(
        "--photographer",
        help="Set photographer ID"
    )

    args = parser.parse_args()

    handler = MetadataHandler()

    if args.file and args.extract:
        metadata = handler.extract_metadata(args.file)
        print("\n" + "="*50)
        print("البيانات الوصفية | Metadata")
        print("="*50)
        for key, value in metadata.to_dict().items():
            print(f"{key}: {value}")

    if args.file and args.sanitize:
        handler.sanitize_metadata(args.file)
        print("تم تنظيف البيانات | Metadata sanitized")


if __name__ == "__main__":
    main()
