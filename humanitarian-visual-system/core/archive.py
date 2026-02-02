#!/usr/bin/env python3
"""
Archive Manager - Legal Documentation Archive System
مدير الأرشيف - نظام الأرشفة القانونية للتوثيق

Manages the legal archival of humanitarian media assets
with full chain of custody documentation.

يدير الأرشفة القانونية للمواد الإعلامية الإنسانية
مع توثيق كامل لسلسلة الحفظ.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class ArchiveStatus(Enum):
    """حالة الأرشفة | Archive Status"""
    PENDING = "pending"
    ARCHIVED = "archived"
    VERIFIED = "verified"
    RESTRICTED = "restricted"


@dataclass
class ArchiveRecord:
    """
    سجل الأرشفة | Archive Record

    Required fields for legal archival:
    - Date | التاريخ
    - General location | الموقع العام
    - Type of intervention | نوع التدخل
    - Photographer ID | معرّف المصور
    - Ethical approval status | حالة الموافقة الأخلاقية
    """
    asset_id: str
    file_path: str
    file_hash: str
    date: datetime
    location_general: str
    intervention_type: str
    photographer_id: str
    ethical_status: str
    archive_status: ArchiveStatus = ArchiveStatus.PENDING
    archived_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    notes: str = ""
    access_level: str = "standard"
    retention_years: int = 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "date": self.date.isoformat(),
            "location_general": self.location_general,
            "intervention_type": self.intervention_type,
            "photographer_id": self.photographer_id,
            "ethical_status": self.ethical_status,
            "archive_status": self.archive_status.value,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "notes": self.notes,
            "access_level": self.access_level,
            "retention_years": self.retention_years
        }

    def to_legal_format(self) -> Dict[str, str]:
        """Format for legal documentation"""
        return {
            "Document_ID": self.asset_id,
            "Capture_Date": self.date.strftime("%Y-%m-%d"),
            "Location": self.location_general,
            "Intervention_Type": self.intervention_type,
            "Photographer": self.photographer_id,
            "Ethical_Clearance": self.ethical_status,
            "Archive_Date": self.archived_at.strftime("%Y-%m-%d") if self.archived_at else "Pending",
            "Verification_Status": "Verified" if self.verified_at else "Unverified",
            "File_Integrity_Hash": self.file_hash,
            "Retention_Period": f"{self.retention_years} years"
        }


class ArchiveManager:
    """
    مدير الأرشيف القانوني
    Legal Archive Manager

    Principle: كل مادة = وثيقة محتملة مستقبلًا
    Every asset = potential future legal document

    Features:
    - Chain of custody tracking
    - File integrity verification
    - Access control
    - Retention management
    - Legal export formats
    """

    def __init__(self, archive_path: str = "./HVS_Archive"):
        self.archive_path = Path(archive_path)
        self.records: Dict[str, ArchiveRecord] = {}
        self.manifest_file = self.archive_path / "archive_manifest.json"

    def initialize(self) -> None:
        """Initialize archive structure"""
        # Create archive directories
        (self.archive_path / "assets").mkdir(parents=True, exist_ok=True)
        (self.archive_path / "manifests").mkdir(parents=True, exist_ok=True)
        (self.archive_path / "exports").mkdir(parents=True, exist_ok=True)
        (self.archive_path / "logs").mkdir(parents=True, exist_ok=True)

        # Initialize manifest
        if not self.manifest_file.exists():
            self._save_manifest()

        self._log("Archive initialized")

    def _calculate_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash for file integrity"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def archive_asset(
        self,
        file_path: str,
        asset_id: str,
        date: datetime,
        location_general: str,
        intervention_type: str,
        photographer_id: str,
        ethical_status: str,
        notes: str = ""
    ) -> ArchiveRecord:
        """
        Archive a media asset with full documentation

        أرشفة مادة إعلامية مع التوثيق الكامل

        Args:
            file_path: Path to media file
            asset_id: Unique asset identifier
            date: Capture date
            location_general: General location (not specific)
            intervention_type: Type of humanitarian intervention
            photographer_id: Photographer identifier
            ethical_status: Ethical approval status
            notes: Additional notes

        Returns:
            ArchiveRecord for the archived asset
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Calculate file hash
        file_hash = self._calculate_hash(file_path)

        # Create archive record
        record = ArchiveRecord(
            asset_id=asset_id,
            file_path=file_path,
            file_hash=file_hash,
            date=date,
            location_general=location_general,
            intervention_type=intervention_type,
            photographer_id=photographer_id,
            ethical_status=ethical_status,
            notes=notes
        )

        # Copy to archive
        archive_dest = self.archive_path / "assets" / Path(file_path).name
        import shutil
        shutil.copy2(file_path, archive_dest)
        record.file_path = str(archive_dest)
        record.archived_at = datetime.now()
        record.archive_status = ArchiveStatus.ARCHIVED

        # Save record
        self.records[asset_id] = record
        self._save_manifest()

        self._log(f"Archived: {asset_id}")
        return record

    def verify_asset(self, asset_id: str) -> bool:
        """
        Verify file integrity of archived asset

        التحقق من سلامة ملف مادة مؤرشفة

        Returns:
            True if file integrity is verified
        """
        record = self.records.get(asset_id)
        if not record:
            return False

        if not os.path.exists(record.file_path):
            return False

        current_hash = self._calculate_hash(record.file_path)
        if current_hash == record.file_hash:
            record.verified_at = datetime.now()
            record.archive_status = ArchiveStatus.VERIFIED
            self._save_manifest()
            self._log(f"Verified: {asset_id}")
            return True

        self._log(f"Verification FAILED: {asset_id}", error=True)
        return False

    def verify_all(self) -> Dict[str, bool]:
        """Verify all archived assets"""
        results = {}
        for asset_id in self.records:
            results[asset_id] = self.verify_asset(asset_id)
        return results

    def get_record(self, asset_id: str) -> Optional[ArchiveRecord]:
        """Get archive record by asset ID"""
        return self.records.get(asset_id)

    def search_by_date(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[ArchiveRecord]:
        """Search archive by date range"""
        return [
            r for r in self.records.values()
            if start_date <= r.date <= end_date
        ]

    def search_by_location(self, location: str) -> List[ArchiveRecord]:
        """Search archive by location"""
        return [
            r for r in self.records.values()
            if location.lower() in r.location_general.lower()
        ]

    def search_by_intervention(self, intervention: str) -> List[ArchiveRecord]:
        """Search archive by intervention type"""
        return [
            r for r in self.records.values()
            if intervention.lower() in r.intervention_type.lower()
        ]

    def export_legal_manifest(
        self,
        output_path: str,
        asset_ids: Optional[List[str]] = None
    ) -> str:
        """
        Export legal documentation manifest

        تصدير بيان التوثيق القانوني

        Args:
            output_path: Output file path
            asset_ids: Specific assets to include (all if None)

        Returns:
            Path to exported manifest
        """
        records_to_export = (
            [self.records[aid] for aid in asset_ids if aid in self.records]
            if asset_ids
            else list(self.records.values())
        )

        manifest = {
            "manifest_type": "Legal Documentation Archive",
            "organization": "Turkish Red Crescent | الهلال الأحمر التركي",
            "generated_at": datetime.now().isoformat(),
            "total_assets": len(records_to_export),
            "verification_statement": (
                "This manifest certifies the chain of custody and integrity "
                "of the documented humanitarian assets."
            ),
            "assets": [r.to_legal_format() for r in records_to_export]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        self._log(f"Legal manifest exported: {output_path}")
        return output_path

    def export_csv(self, output_path: str) -> str:
        """Export archive as CSV for reporting"""
        import csv

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                "Asset ID", "Date", "Location", "Intervention",
                "Photographer", "Ethical Status", "Archive Status",
                "Archived At", "Verified"
            ])

            # Data
            for record in self.records.values():
                writer.writerow([
                    record.asset_id,
                    record.date.strftime("%Y-%m-%d"),
                    record.location_general,
                    record.intervention_type,
                    record.photographer_id,
                    record.ethical_status,
                    record.archive_status.value,
                    record.archived_at.strftime("%Y-%m-%d") if record.archived_at else "",
                    "Yes" if record.verified_at else "No"
                ])

        return output_path

    def get_statistics(self) -> Dict[str, Any]:
        """Get archive statistics"""
        total = len(self.records)
        verified = len([r for r in self.records.values() if r.verified_at])

        by_intervention = {}
        by_location = {}

        for record in self.records.values():
            by_intervention[record.intervention_type] = by_intervention.get(record.intervention_type, 0) + 1
            by_location[record.location_general] = by_location.get(record.location_general, 0) + 1

        return {
            "total_assets": total,
            "verified": verified,
            "unverified": total - verified,
            "by_intervention": by_intervention,
            "by_location": by_location
        }

    def _save_manifest(self) -> None:
        """Save manifest to disk"""
        manifest_data = {
            "last_updated": datetime.now().isoformat(),
            "total_records": len(self.records),
            "records": {
                aid: r.to_dict() for aid, r in self.records.items()
            }
        }

        with open(self.manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=2)

    def _load_manifest(self) -> None:
        """Load manifest from disk"""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Would reconstruct records here
                pass

    def _log(self, message: str, error: bool = False) -> None:
        """Write to archive log"""
        log_file = self.archive_path / "logs" / "archive_operations.log"
        timestamp = datetime.now().isoformat()
        level = "ERROR" if error else "INFO"
        log_line = f"[{timestamp}] [{level}] {message}\n"

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception:
            pass


def main():
    """CLI for archive management"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Humanitarian Visual System - Archive Manager"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize archive structure"
    )
    parser.add_argument(
        "--archive-path",
        default="./HVS_Archive",
        help="Archive directory path"
    )
    parser.add_argument(
        "--verify-all",
        action="store_true",
        help="Verify all archived assets"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show archive statistics"
    )
    parser.add_argument(
        "--export",
        help="Export legal manifest to path"
    )

    args = parser.parse_args()

    manager = ArchiveManager(args.archive_path)

    if args.init:
        manager.initialize()
        print(f"تم تهيئة الأرشيف | Archive initialized at: {args.archive_path}")

    if args.verify_all:
        results = manager.verify_all()
        verified = sum(1 for v in results.values() if v)
        print(f"التحقق | Verification: {verified}/{len(results)} assets verified")

    if args.stats:
        stats = manager.get_statistics()
        print("\n" + "="*50)
        print("إحصائيات الأرشيف | Archive Statistics")
        print("="*50)
        print(f"إجمالي المواد | Total Assets: {stats['total_assets']}")
        print(f"موثقة | Verified: {stats['verified']}")
        print(f"غير موثقة | Unverified: {stats['unverified']}")

    if args.export:
        manager.export_legal_manifest(args.export)
        print(f"تم التصدير | Exported to: {args.export}")


if __name__ == "__main__":
    main()
