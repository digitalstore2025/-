#!/usr/bin/env python3
"""
Ethical Gate - Automated Ethical Review System
بوابة المراجعة الأخلاقية الآلية

This module implements the ethical screening protocol for all media assets
before they can be approved for use in reports, archives, or publishing.

هذه الوحدة تنفذ بروتوكول الفحص الأخلاقي لجميع المواد الإعلامية
قبل الموافقة عليها للاستخدام في التقارير أو الأرشيف أو النشر.
"""

import os
import json
import hashlib
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path


class ApprovalStatus(Enum):
    """حالة الموافقة | Approval Status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"
    REDACTED = "redacted"


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
class EthicalReview:
    """نتيجة المراجعة الأخلاقية | Ethical Review Result"""
    asset_id: str
    file_path: str
    status: ApprovalStatus
    reviewed_at: datetime
    reviewer: str  # "auto" or reviewer ID
    rejection_reasons: List[RejectionReason] = field(default_factory=list)
    notes: str = ""
    requires_redaction: bool = False
    redaction_areas: List[Dict[str, int]] = field(default_factory=list)
    consent_documented: bool = False
    location_general: str = ""  # Only general location, never specific

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "file_path": self.file_path,
            "status": self.status.value,
            "reviewed_at": self.reviewed_at.isoformat(),
            "reviewer": self.reviewer,
            "rejection_reasons": [r.value for r in self.rejection_reasons],
            "notes": self.notes,
            "requires_redaction": self.requires_redaction,
            "redaction_areas": self.redaction_areas,
            "consent_documented": self.consent_documented,
            "location_general": self.location_general
        }


class EthicalGate:
    """
    بوابة المراجعة الأخلاقية
    Ethical Review Gate

    Implements automated ethical screening for humanitarian media content.
    All assets must pass through this gate before approval.

    تنفذ الفحص الأخلاقي الآلي للمحتوى الإعلامي الإنساني.
    يجب أن تمر جميع المواد عبر هذه البوابة قبل الموافقة.
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

    # أنواع الملفات المدعومة | Supported File Types
    SUPPORTED_MEDIA = {
        "image": [".jpg", ".jpeg", ".png", ".raw", ".cr2", ".nef", ".arw"],
        "video": [".mp4", ".mov", ".mxf", ".avi"],
        "audio": [".wav", ".mp3", ".aac"]
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Ethical Gate

        Args:
            config_path: Path to ethical rules configuration file
        """
        self.config = self._load_config(config_path)
        self.review_log: List[EthicalReview] = []

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "auto_reject_faces": True,
            "auto_reject_graphic": True,
            "auto_reject_locations": True,
            "require_consent_documentation": True,
            "strip_sensitive_metadata": True,
            "allowed_general_locations": [
                "غزة",
                "Gaza",
                "شمال غزة",
                "Northern Gaza",
                "جنوب غزة",
                "Southern Gaza",
                "وسط غزة",
                "Central Gaza"
            ],
            "forbidden_metadata_fields": [
                "GPSLatitude",
                "GPSLongitude",
                "GPSPosition",
                "GPSCoordinates"
            ]
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)

        return default_config

    def generate_asset_id(self, file_path: str) -> str:
        """Generate unique asset ID from file hash"""
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()[:12]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"HVS-{timestamp}-{file_hash}"

    def check_file_type(self, file_path: str) -> Optional[str]:
        """Check if file type is supported and return media type"""
        ext = Path(file_path).suffix.lower()
        for media_type, extensions in self.SUPPORTED_MEDIA.items():
            if ext in extensions:
                return media_type
        return None

    def review_asset(
        self,
        file_path: str,
        consent_documented: bool = False,
        location_general: str = "",
        manual_flags: Optional[Dict[str, bool]] = None
    ) -> EthicalReview:
        """
        Review a media asset against ethical guidelines

        مراجعة مادة إعلامية وفق الإرشادات الأخلاقية

        Args:
            file_path: Path to the media file
            consent_documented: Whether consent is documented for visible persons
            location_general: General location description (not specific)
            manual_flags: Manual override flags from human reviewer

        Returns:
            EthicalReview: The review result
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Asset not found: {file_path}")

        media_type = self.check_file_type(file_path)
        if not media_type:
            raise ValueError(f"Unsupported file type: {file_path}")

        asset_id = self.generate_asset_id(file_path)
        rejection_reasons: List[RejectionReason] = []
        requires_redaction = False
        redaction_areas: List[Dict[str, int]] = []

        # المراجعة التلقائية | Automatic Review
        flags = manual_flags or {}

        # فحص الوجوه | Face Check
        if flags.get("face_visible", False) and not consent_documented:
            rejection_reasons.append(RejectionReason.FACE_WITHOUT_CONSENT)

        # فحص الأطفال | Child Check
        if flags.get("child_identifiable", False):
            rejection_reasons.append(RejectionReason.CHILD_IDENTIFIABLE)
            requires_redaction = True

        # فحص المحتوى الصادم | Graphic Content Check
        if flags.get("graphic_content", False):
            rejection_reasons.append(RejectionReason.GRAPHIC_CONTENT)

        # فحص الجثامين | Body Check
        if flags.get("body_visible", False):
            rejection_reasons.append(RejectionReason.BODY_EXPOSED)

        # فحص الموقع | Location Check
        if flags.get("location_sensitive", False):
            rejection_reasons.append(RejectionReason.SENSITIVE_LOCATION)

        # فحص المؤثرات الدرامية | Dramatic Effects Check
        if flags.get("dramatic_manipulation", False):
            rejection_reasons.append(RejectionReason.DRAMATIC_MANIPULATION)

        # تحديد الحالة النهائية | Determine Final Status
        if rejection_reasons:
            status = ApprovalStatus.REJECTED
        elif requires_redaction:
            status = ApprovalStatus.REQUIRES_REVIEW
        elif not consent_documented and media_type in ["image", "video"]:
            status = ApprovalStatus.REQUIRES_REVIEW
        else:
            status = ApprovalStatus.APPROVED

        review = EthicalReview(
            asset_id=asset_id,
            file_path=file_path,
            status=status,
            reviewed_at=datetime.now(),
            reviewer="auto",
            rejection_reasons=rejection_reasons,
            requires_redaction=requires_redaction,
            redaction_areas=redaction_areas,
            consent_documented=consent_documented,
            location_general=location_general
        )

        self.review_log.append(review)
        return review

    def batch_review(
        self,
        directory: str,
        consent_map: Optional[Dict[str, bool]] = None
    ) -> List[EthicalReview]:
        """
        Review all media assets in a directory

        مراجعة جميع المواد الإعلامية في مجلد

        Args:
            directory: Path to directory containing media files
            consent_map: Mapping of file names to consent status

        Returns:
            List of EthicalReview results
        """
        results: List[EthicalReview] = []
        consent_map = consent_map or {}

        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if self.check_file_type(file_path):
                    try:
                        consent = consent_map.get(file, False)
                        review = self.review_asset(
                            file_path,
                            consent_documented=consent
                        )
                        results.append(review)
                    except Exception as e:
                        print(f"Error reviewing {file_path}: {e}")

        return results

    def export_review_log(self, output_path: str) -> None:
        """Export review log to JSON file"""
        log_data = {
            "export_date": datetime.now().isoformat(),
            "total_reviewed": len(self.review_log),
            "approved": len([r for r in self.review_log if r.status == ApprovalStatus.APPROVED]),
            "rejected": len([r for r in self.review_log if r.status == ApprovalStatus.REJECTED]),
            "pending_review": len([r for r in self.review_log if r.status == ApprovalStatus.REQUIRES_REVIEW]),
            "reviews": [r.to_dict() for r in self.review_log]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

    def get_approved_assets(self) -> List[EthicalReview]:
        """Get list of approved assets only"""
        return [r for r in self.review_log if r.status == ApprovalStatus.APPROVED]

    def get_rejection_summary(self) -> Dict[str, int]:
        """Get summary of rejection reasons"""
        summary: Dict[str, int] = {}
        for review in self.review_log:
            for reason in review.rejection_reasons:
                summary[reason.value] = summary.get(reason.value, 0) + 1
        return summary


def main():
    """CLI interface for ethical review"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Humanitarian Visual System - Ethical Gate"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input file or directory to review"
    )
    parser.add_argument(
        "--output", "-o",
        default="ethical_review_log.json",
        help="Output path for review log"
    )
    parser.add_argument(
        "--consent",
        action="store_true",
        help="Mark all assets as having documented consent"
    )

    args = parser.parse_args()

    gate = EthicalGate()

    if os.path.isdir(args.input):
        results = gate.batch_review(args.input)
    else:
        results = [gate.review_asset(args.input, consent_documented=args.consent)]

    # Print summary
    print("\n" + "="*50)
    print("تقرير المراجعة الأخلاقية | Ethical Review Report")
    print("="*50)
    print(f"إجمالي المراجعة | Total Reviewed: {len(results)}")
    print(f"الموافق عليها | Approved: {len([r for r in results if r.status == ApprovalStatus.APPROVED])}")
    print(f"المرفوضة | Rejected: {len([r for r in results if r.status == ApprovalStatus.REJECTED])}")
    print(f"تحتاج مراجعة | Needs Review: {len([r for r in results if r.status == ApprovalStatus.REQUIRES_REVIEW])}")

    # Export log
    gate.export_review_log(args.output)
    print(f"\nتم حفظ السجل في | Log saved to: {args.output}")


if __name__ == "__main__":
    main()
