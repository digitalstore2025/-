#!/usr/bin/env python3
"""
Activity Logger - Immutable Activity Logging
مسجل النشاط - تسجيل غير قابل للحذف

All activities in the system are logged permanently.
This provides accountability and audit trail.

جميع الأنشطة في النظام تُسجل بشكل دائم.
هذا يوفر المساءلة وسجل المراجعة.

Features:
    - Append-only log files
    - Hash-chained entries for integrity
    - JSON format for machine readability
    - Human-readable timestamps

المميزات:
    - ملفات سجل للإضافة فقط
    - إدخالات متسلسلة بالتجزئة للسلامة
    - صيغة JSON للقراءة الآلية
    - طوابع زمنية سهلة القراءة
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActivityLogger:
    """
    مسجل النشاط غير القابل للحذف
    Immutable Activity Logger

    Provides permanent logging of all system activities
    with hash-chaining for integrity verification.

    يوفر تسجيل دائم لجميع أنشطة النظام
    مع تسلسل التجزئة للتحقق من السلامة.
    """

    # Activity types
    ACTIVITY_TYPES = [
        "INIT",       # System initialization
        "IMPORT",     # File import
        "REVIEW",     # Ethical review
        "BLUR",       # Face blur applied
        "STRIP",      # Metadata stripped
        "APPROVE",    # File approved
        "REJECT",     # File rejected
        "CAPTION",    # Caption added
        "ARCHIVE",    # File archived
        "EXPORT",     # File exported
        "BACKUP",     # Backup created
        "ERROR",      # Error occurred
        "WARNING",    # Warning issued
        "ACCESS",     # File accessed
        "CONFIG",     # Configuration changed
    ]

    def __init__(self, log_dir: str):
        """
        Initialize ActivityLogger

        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Current day's log file
        self.current_log = self.log_dir / f"activity_{datetime.now().strftime('%Y%m%d')}.jsonl"

        # Last hash for chaining
        self._last_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        """Get hash of last log entry for chaining"""
        if self.current_log.exists():
            with open(self.current_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return last_entry.get("hash", "0" * 64)

        return "0" * 64  # Genesis hash

    def _compute_hash(self, entry: Dict) -> str:
        """Compute hash for log entry"""
        # Include previous hash for chaining
        entry_str = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        chain_str = f"{self._last_hash}{entry_str}"
        return hashlib.sha256(chain_str.encode()).hexdigest()

    def log(
        self,
        activity_type: str,
        message: str,
        details: Dict = None,
        file_path: str = None,
        user: str = "system"
    ) -> Dict:
        """
        Log an activity

        تسجيل نشاط

        Args:
            activity_type: Type of activity (from ACTIVITY_TYPES)
            message: Human-readable message
            details: Additional details dictionary
            file_path: Related file path (optional)
            user: User/system identifier

        Returns:
            The logged entry
        """
        if activity_type not in self.ACTIVITY_TYPES:
            logger.warning(f"Unknown activity type: {activity_type}")

        timestamp = datetime.now()

        entry = {
            "timestamp": timestamp.isoformat(),
            "timestamp_human": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "type": activity_type,
            "message": message,
            "user": user,
            "previous_hash": self._last_hash
        }

        if file_path:
            entry["file_path"] = file_path

        if details:
            entry["details"] = details

        # Compute hash
        entry["hash"] = self._compute_hash(entry)
        self._last_hash = entry["hash"]

        # Append to log file
        with open(self.current_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    def get_logs(
        self,
        date: str = None,
        activity_type: str = None,
        file_path: str = None,
        limit: int = None
    ) -> List[Dict]:
        """
        Retrieve log entries

        استرجاع إدخالات السجل

        Args:
            date: Date string (YYYYMMDD) or None for today
            activity_type: Filter by activity type
            file_path: Filter by file path
            limit: Maximum entries to return

        Returns:
            List of log entries
        """
        if date:
            log_file = self.log_dir / f"activity_{date}.jsonl"
        else:
            log_file = self.current_log

        if not log_file.exists():
            return []

        entries = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)

                # Apply filters
                if activity_type and entry.get("type") != activity_type:
                    continue
                if file_path and entry.get("file_path") != file_path:
                    continue

                entries.append(entry)

        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x["timestamp"], reverse=True)

        if limit:
            entries = entries[:limit]

        return entries

    def get_file_history(self, file_path: str) -> List[Dict]:
        """
        Get all log entries for a specific file

        الحصول على جميع إدخالات السجل لملف محدد
        """
        all_entries = []

        # Search all log files
        for log_file in sorted(self.log_dir.glob("activity_*.jsonl")):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    # Check if file_path matches (partial match for renamed files)
                    entry_path = entry.get("file_path", "")
                    if file_path in entry_path or Path(file_path).name in entry_path:
                        all_entries.append(entry)

        return sorted(all_entries, key=lambda x: x["timestamp"])

    def verify_integrity(self, date: str = None) -> Dict[str, Any]:
        """
        Verify log integrity using hash chain

        التحقق من سلامة السجل باستخدام سلسلة التجزئة

        Returns:
            Verification result with details
        """
        if date:
            log_file = self.log_dir / f"activity_{date}.jsonl"
        else:
            log_file = self.current_log

        if not log_file.exists():
            return {"valid": True, "message": "Log file does not exist", "entries": 0}

        result = {
            "valid": True,
            "entries": 0,
            "corrupted_entries": [],
            "log_file": str(log_file)
        }

        previous_hash = "0" * 64  # Genesis

        with open(log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                entry = json.loads(line)
                result["entries"] += 1

                # Verify previous hash link
                if entry.get("previous_hash") != previous_hash:
                    result["valid"] = False
                    result["corrupted_entries"].append({
                        "line": line_num,
                        "expected_prev": previous_hash,
                        "found_prev": entry.get("previous_hash")
                    })

                # Verify entry hash
                stored_hash = entry.pop("hash", None)
                computed_hash = self._compute_entry_hash(entry, previous_hash)

                if stored_hash != computed_hash:
                    result["valid"] = False
                    result["corrupted_entries"].append({
                        "line": line_num,
                        "expected_hash": computed_hash,
                        "found_hash": stored_hash
                    })

                entry["hash"] = stored_hash
                previous_hash = stored_hash

        if result["valid"]:
            result["message"] = f"All {result['entries']} entries verified"
        else:
            result["message"] = f"Found {len(result['corrupted_entries'])} corrupted entries"

        return result

    def _compute_entry_hash(self, entry: Dict, previous_hash: str) -> str:
        """Compute hash for verification"""
        entry_str = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        chain_str = f"{previous_hash}{entry_str}"
        return hashlib.sha256(chain_str.encode()).hexdigest()

    def get_statistics(self, days: int = 7) -> Dict[str, int]:
        """
        Get activity statistics

        الحصول على إحصائيات النشاط
        """
        stats = {activity: 0 for activity in self.ACTIVITY_TYPES}
        stats["total"] = 0

        # Get recent log files
        log_files = sorted(self.log_dir.glob("activity_*.jsonl"), reverse=True)[:days]

        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    activity = entry.get("type", "UNKNOWN")
                    stats[activity] = stats.get(activity, 0) + 1
                    stats["total"] += 1

        return stats

    def export_audit_report(
        self,
        output_path: str,
        date_from: str = None,
        date_to: str = None
    ):
        """
        Export audit report

        تصدير تقرير المراجعة
        """
        all_entries = []

        for log_file in sorted(self.log_dir.glob("activity_*.jsonl")):
            # Filter by date if specified
            file_date = log_file.stem.split("_")[1]

            if date_from and file_date < date_from:
                continue
            if date_to and file_date > date_to:
                continue

            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    all_entries.append(json.loads(line))

        report = {
            "generated_at": datetime.now().isoformat(),
            "date_range": {
                "from": date_from or "beginning",
                "to": date_to or "present"
            },
            "statistics": self.get_statistics(30),
            "entries": all_entries
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"Audit report exported: {output_path}")

    def print_recent(self, count: int = 10):
        """
        Print recent log entries

        طباعة إدخالات السجل الأخيرة
        """
        entries = self.get_logs(limit=count)

        print(f"\n📋 آخر {len(entries)} إدخالات | Last {len(entries)} entries")
        print("═" * 70)

        for entry in entries:
            timestamp = entry.get("timestamp_human", entry.get("timestamp", ""))
            activity = entry.get("type", "UNKNOWN")
            message = entry.get("message", "")

            icon = {
                "INIT": "🚀",
                "IMPORT": "📥",
                "REVIEW": "🔍",
                "BLUR": "🔲",
                "STRIP": "🔒",
                "APPROVE": "✓",
                "REJECT": "✗",
                "CAPTION": "📝",
                "ARCHIVE": "📦",
                "EXPORT": "📤",
                "BACKUP": "💾",
                "ERROR": "❌",
                "WARNING": "⚠️",
            }.get(activity, "•")

            print(f"  {timestamp} {icon} [{activity}] {message}")

        print("═" * 70)


if __name__ == "__main__":
    # Test
    logger_instance = ActivityLogger("./test_logs")
    logger_instance.log("INIT", "System initialized for testing")
    logger_instance.log("IMPORT", "Test file imported", file_path="test.jpg")
    logger_instance.print_recent()

    # Verify
    result = logger_instance.verify_integrity()
    print(f"\nIntegrity: {result}")
