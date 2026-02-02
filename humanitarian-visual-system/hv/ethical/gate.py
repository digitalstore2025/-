#!/usr/bin/env python3
"""
Ethical Gate - Decision Gate for Ethical Compliance
بوابة القرار الأخلاقي

This module implements the ethical decision gate that
ensures all media passes ethical requirements before approval.

هذه الوحدة تنفذ بوابة القرار الأخلاقي التي تضمن
مرور جميع الوسائط بالمتطلبات الأخلاقية قبل الموافقة.

Decision Rules / قواعد القرار:
    if face_detected and not consent:
        blur_faces(file)
    if sensitive_metadata:
        strip_metadata(file)
    if graphic_content:
        reject(file)

الأخلاق هنا قرار آلي لا يُناقش
Ethics here is an automatic decision, non-negotiable
"""

import os
import json
from pathlib import Path
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """حالة الموافقة | Approval Status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"
    REDACTED = "redacted"


class FileState(Enum):
    """حالة الملف | File State"""
    IMPORTED = "imported"
    REVIEWING = "reviewing"
    REDACTED = "redacted"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class RejectionReason(Enum):
    """أسباب الرفض | Rejection Reasons"""
    FACE_WITHOUT_CONSENT = "face_visible_without_consent"
    SENSITIVE_LOCATION = "sensitive_location_exposed"
    GRAPHIC_CONTENT = "graphic_content_detected"
    CHILD_IDENTIFIABLE = "identifiable_child"
    SECURITY_RISK = "security_risk"
    DRAMATIC_MANIPULATION = "dramatic_manipulation"
    BODY_EXPOSED = "exposed_body_or_injury"
    METADATA_LEAK = "sensitive_metadata"


@dataclass
class FileRecord:
    """سجل الملف | File Record"""
    file_id: str
    file_path: str
    original_name: str
    state: FileState
    created_at: datetime
    updated_at: datetime
    consent_documented: bool = False
    faces_detected: int = 0
    faces_blurred: bool = False
    metadata_stripped: bool = False
    rejection_reason: Optional[str] = None
    notes: str = ""
    location_general: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_id": self.file_id,
            "file_path": self.file_path,
            "original_name": self.original_name,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "consent_documented": self.consent_documented,
            "faces_detected": self.faces_detected,
            "faces_blurred": self.faces_blurred,
            "metadata_stripped": self.metadata_stripped,
            "rejection_reason": self.rejection_reason,
            "notes": self.notes,
            "location_general": self.location_general
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileRecord':
        return cls(
            file_id=data["file_id"],
            file_path=data["file_path"],
            original_name=data["original_name"],
            state=FileState(data["state"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            consent_documented=data.get("consent_documented", False),
            faces_detected=data.get("faces_detected", 0),
            faces_blurred=data.get("faces_blurred", False),
            metadata_stripped=data.get("metadata_stripped", False),
            rejection_reason=data.get("rejection_reason"),
            notes=data.get("notes", ""),
            location_general=data.get("location_general", "")
        )


class EthicalGate:
    """
    بوابة المراجعة الأخلاقية
    Ethical Review Gate

    Enforces ethical compliance through a strict workflow:
    import → review → blur/approve/reject → archive

    لا يمكن تجاوز المراحل — النظام يمنع ذلك برمجيًا
    Stages cannot be skipped — the system prevents this programmatically
    """

    # القواعد غير القابلة للتفاوض | Non-Negotiable Rules
    NON_NEGOTIABLE_RULES = [
        "no_beneficiary_endangerment",
        "no_faces_without_consent",
        "no_graphic_content",
        "no_sensitive_locations",
        "no_dramatic_effects",
        "auto_exclude_unethical"
    ]

    # Valid state transitions
    VALID_TRANSITIONS = {
        FileState.IMPORTED: [FileState.REVIEWING, FileState.REJECTED],
        FileState.REVIEWING: [FileState.REDACTED, FileState.APPROVED, FileState.REJECTED],
        FileState.REDACTED: [FileState.APPROVED, FileState.REJECTED],
        FileState.APPROVED: [FileState.ARCHIVED, FileState.REJECTED],
        FileState.REJECTED: [],  # Terminal state
        FileState.ARCHIVED: []   # Terminal state
    }

    def __init__(self, state_file: str = None):
        """
        Initialize EthicalGate

        Args:
            state_file: Path to persist state (JSON file)
        """
        self.state_file = state_file
        self.files: Dict[str, FileRecord] = {}

        if state_file and os.path.exists(state_file):
            self._load_state()

    def _load_state(self):
        """Load state from file"""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for file_id, record_data in data.get("files", {}).items():
                    self.files[file_id] = FileRecord.from_dict(record_data)
        except Exception as e:
            logger.error(f"Error loading state: {e}")

    def _save_state(self):
        """Save state to file"""
        if not self.state_file:
            return

        try:
            data = {
                "updated_at": datetime.now().isoformat(),
                "total_files": len(self.files),
                "files": {fid: record.to_dict() for fid, record in self.files.items()}
            }

            # Ensure directory exists
            Path(self.state_file).parent.mkdir(parents=True, exist_ok=True)

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def generate_file_id(self, file_path: str) -> str:
        """Generate unique file ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        return f"HV-{timestamp}-{name_hash}"

    def register_file(self, file_path: str) -> FileRecord:
        """
        Register new file in the system

        تسجيل ملف جديد في النظام

        Args:
            file_path: Path to the file

        Returns:
            FileRecord for the new file
        """
        file_id = self.generate_file_id(file_path)
        now = datetime.now()

        record = FileRecord(
            file_id=file_id,
            file_path=file_path,
            original_name=Path(file_path).name,
            state=FileState.IMPORTED,
            created_at=now,
            updated_at=now
        )

        self.files[file_id] = record
        self._save_state()

        logger.info(f"Registered file: {file_path} as {file_id}")
        return record

    def get_file_state(self, file_path: str) -> Optional[FileRecord]:
        """Get file record by path"""
        for record in self.files.values():
            if record.file_path == file_path or file_path.endswith(record.original_name):
                return record
        return None

    def update_state(
        self,
        file_path: str,
        new_state: FileState,
        reason: str = None,
        **kwargs
    ) -> bool:
        """
        Update file state

        تحديث حالة الملف

        Args:
            file_path: Path to file
            new_state: New state to set
            reason: Rejection reason (if rejecting)
            **kwargs: Additional record updates

        Returns:
            True if state was updated
        """
        record = self.get_file_state(file_path)
        if not record:
            logger.warning(f"File not found in registry: {file_path}")
            return False

        # Validate state transition
        current_state = record.state
        valid_next = self.VALID_TRANSITIONS.get(current_state, [])

        if new_state not in valid_next:
            logger.error(
                f"Invalid state transition: {current_state.value} → {new_state.value}. "
                f"Valid transitions: {[s.value for s in valid_next]}"
            )
            return False

        # Update record
        record.state = new_state
        record.updated_at = datetime.now()
        record.file_path = file_path  # Update path if moved

        if reason:
            record.rejection_reason = reason

        # Apply additional updates
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)

        self._save_state()

        logger.info(f"Updated state: {record.original_name} → {new_state.value}")
        return True

    def can_approve(self, file_path: str) -> tuple[bool, List[str]]:
        """
        Check if file can be approved

        التحقق من إمكانية الموافقة على الملف

        Returns:
            (can_approve, list_of_blockers)
        """
        record = self.get_file_state(file_path)
        if not record:
            return False, ["File not registered"]

        blockers = []

        # Check state
        if record.state not in [FileState.REVIEWING, FileState.REDACTED]:
            blockers.append(f"Invalid state: {record.state.value}")

        # Check faces
        if record.faces_detected > 0 and not record.consent_documented and not record.faces_blurred:
            blockers.append("Faces detected without consent or blur")

        # Check metadata
        if not record.metadata_stripped:
            blockers.append("Metadata not stripped")

        return len(blockers) == 0, blockers

    def auto_decide(
        self,
        file_path: str,
        face_count: int = 0,
        has_consent: bool = False,
        has_sensitive_metadata: bool = False,
        has_graphic_content: bool = False
    ) -> Dict[str, Any]:
        """
        Automatic ethical decision

        القرار الأخلاقي التلقائي

        Args:
            file_path: Path to file
            face_count: Number of faces detected
            has_consent: Whether consent is documented
            has_sensitive_metadata: Whether file has sensitive metadata
            has_graphic_content: Whether file contains graphic content

        Returns:
            Decision dictionary with actions to take
        """
        decision = {
            "file_path": file_path,
            "actions": [],
            "status": "pending",
            "can_proceed": True
        }

        # Rule 1: Graphic content → REJECT
        if has_graphic_content:
            decision["actions"].append({
                "action": "REJECT",
                "reason": RejectionReason.GRAPHIC_CONTENT.value
            })
            decision["status"] = "rejected"
            decision["can_proceed"] = False
            return decision

        # Rule 2: Faces without consent → BLUR
        if face_count > 0 and not has_consent:
            decision["actions"].append({
                "action": "BLUR",
                "reason": "Faces detected without consent",
                "face_count": face_count
            })

        # Rule 3: Sensitive metadata → STRIP
        if has_sensitive_metadata:
            decision["actions"].append({
                "action": "STRIP_METADATA",
                "reason": "Sensitive metadata detected"
            })

        # If actions required, set status
        if decision["actions"]:
            decision["status"] = "requires_processing"
        else:
            decision["status"] = "ready_for_approval"

        return decision

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about file states"""
        stats = {
            "total": len(self.files),
            "imported": 0,
            "reviewing": 0,
            "redacted": 0,
            "approved": 0,
            "rejected": 0,
            "archived": 0
        }

        for record in self.files.values():
            stats[record.state.value] = stats.get(record.state.value, 0) + 1

        return stats

    def get_pending_files(self) -> List[FileRecord]:
        """Get files pending review"""
        return [
            r for r in self.files.values()
            if r.state in [FileState.IMPORTED, FileState.REVIEWING]
        ]

    def get_approved_files(self) -> List[FileRecord]:
        """Get approved files"""
        return [
            r for r in self.files.values()
            if r.state == FileState.APPROVED
        ]

    def export_audit_log(self, output_path: str):
        """
        Export audit log for compliance

        تصدير سجل المراجعة للامتثال
        """
        log_data = {
            "export_date": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "files": [r.to_dict() for r in self.files.values()]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Audit log exported to: {output_path}")


def main():
    """CLI interface for ethical gate"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Ethical Gate - Humanitarian Visual System"
    )
    parser.add_argument("--state", default=".hv_state.json",
                        help="State file path")
    parser.add_argument("--stats", action="store_true",
                        help="Show statistics")
    parser.add_argument("--export", help="Export audit log to file")

    args = parser.parse_args()

    gate = EthicalGate(args.state)

    if args.stats:
        stats = gate.get_statistics()
        print("\n📊 Ethical Gate Statistics")
        print("=" * 40)
        for key, value in stats.items():
            print(f"  {key}: {value}")

    if args.export:
        gate.export_audit_log(args.export)
        print(f"✓ Audit log exported: {args.export}")


if __name__ == "__main__":
    main()
