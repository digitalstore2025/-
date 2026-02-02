#!/usr/bin/env python3
"""
Humanitarian Visual System - Main CLI
نظام التوثيق البصري الإنساني - واجهة سطر الأوامر الرئيسية

Commands:
    hv init         - Initialize mission structure
    hv import       - Import media files
    hv review       - Ethical review of file
    hv approve      - Approve file after review
    hv reject       - Reject file with reason
    hv blur         - Apply face blur
    hv strip        - Strip sensitive metadata
    hv caption      - Add caption to file
    hv archive      - Archive approved files
    hv dashboard    - Launch offline dashboard
    hv status       - Show current status
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import json

# Ensure package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from hv.core.files import FileManager
    from hv.core.captions import CaptionEngine
    from hv.core.logger import ActivityLogger
    from hv.ethical.gate import EthicalGate, ApprovalStatus, FileState
    from hv.ethical.blur import FaceBlur
    from hv.ethical.metadata import MetadataStripper
except ImportError:
    # Fallback for development
    from core.files import FileManager
    from core.captions import CaptionEngine
    from core.logger import ActivityLogger
    from ethical.gate import EthicalGate, ApprovalStatus, FileState
    from ethical.blur import FaceBlur
    from ethical.metadata import MetadataStripper


class HVSystem:
    """
    النظام الرئيسي للتوثيق البصري الإنساني
    Main Humanitarian Visual System
    """

    VERSION = "1.0.0"

    def __init__(self, base_path: str = "./Gaza_Mission"):
        self.base_path = Path(base_path)
        self.config_path = self.base_path / ".hv_config.json"

        # Initialize components
        self.file_manager = FileManager(str(self.base_path))
        self.ethical_gate = EthicalGate(str(self.base_path / ".hv_state.json"))
        self.face_blur = FaceBlur()
        self.metadata_stripper = MetadataStripper()
        self.caption_engine = CaptionEngine()
        self.logger = ActivityLogger(str(self.base_path / "LOGS"))

        # Load or create config
        self._load_config()

    def _load_config(self):
        """Load system configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "initialized": False,
                "mission_name": "Gaza Mission",
                "created_at": None,
                "current_day": 0,
                "auto_blur": True,
                "auto_strip_metadata": True,
                "language": "ar"
            }

    def _save_config(self):
        """Save system configuration"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def show_banner(self):
        """Display system banner"""
        print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   🟥 HUMANITARIAN VISUAL SYSTEM                                       ║
║   ═══════════════════════════════════════════════════════════════     ║
║                                                                       ║
║   نظام التوثيق البصري الإنساني | Gaza Edition                         ║
║                                                                       ║
║   ✓ CLI + Ethics + Dashboard                                          ║
║   ✓ Offline-First | يعمل بدون إنترنت                                   ║
║   ✓ Field-Ready | جاهز ميدانياً                                        ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
        """)

    def cmd_init(self, mission_name: str = None):
        """
        Initialize mission structure
        تهيئة هيكل البعثة
        """
        print("\n📁 تهيئة النظام | Initializing System...")

        # Create directory structure
        directories = [
            "RAW",           # ملفات خام
            "IMPORTED",      # ملفات مستوردة
            "REVIEW",        # قيد المراجعة
            "APPROVED",      # موافق عليها
            "REJECTED",      # مرفوضة
            "REDACTED",      # معدّلة (طمس)
            "ARCHIVE",       # الأرشيف
            "EXPORT",        # للتصدير
            "LOGS",          # السجلات
            "CAPTIONS"       # التعليقات التوضيحية
        ]

        for dir_name in directories:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {dir_name}/")

        # Update config
        self.config["initialized"] = True
        self.config["mission_name"] = mission_name or "Gaza Mission"
        self.config["created_at"] = datetime.now().isoformat()
        self._save_config()

        # Log activity
        self.logger.log("INIT", f"Mission initialized: {self.config['mission_name']}")

        print(f"\n✓ تم تهيئة البعثة | Mission initialized: {self.base_path}")
        print("  استخدم 'hv import <file>' لاستيراد الملفات")
        print("  Use 'hv import <file>' to import files")

    def cmd_import(self, file_path: str, day: int = None):
        """
        Import media file into the system
        استيراد ملف إلى النظام

        Workflow: import → review → approve/reject
        """
        if not self.config.get("initialized"):
            print("❌ النظام غير مهيأ | System not initialized")
            print("   استخدم 'hv init' أولاً | Use 'hv init' first")
            return False

        source = Path(file_path)
        if not source.exists():
            print(f"❌ الملف غير موجود | File not found: {file_path}")
            return False

        # Generate unique ID and copy to IMPORTED
        import_dir = self.base_path / "IMPORTED"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"HV_{timestamp}_{source.name}"
        dest = import_dir / new_name

        # Copy file
        import shutil
        shutil.copy2(source, dest)

        # Register in ethical gate
        self.ethical_gate.register_file(str(dest))

        # Auto-process if enabled
        if self.config.get("auto_strip_metadata", True):
            print("  🔒 إزالة البيانات الحساسة | Stripping metadata...")
            self.metadata_stripper.strip(str(dest))

        # Log
        self.logger.log("IMPORT", f"Imported: {source.name} → {new_name}")

        print(f"\n✓ تم الاستيراد | Imported: {new_name}")
        print(f"  الحالة: قيد الانتظار | Status: PENDING")
        print(f"  الخطوة التالية: hv review {new_name}")
        print(f"  Next step: hv review {new_name}")

        return True

    def cmd_review(self, file_name: str):
        """
        Review file for ethical compliance
        مراجعة الملف للامتثال الأخلاقي
        """
        # Find file in IMPORTED
        file_path = self._find_file(file_name, ["IMPORTED", "REVIEW"])
        if not file_path:
            print(f"❌ الملف غير موجود | File not found: {file_name}")
            return False

        # Get current state
        state = self.ethical_gate.get_file_state(str(file_path))
        if not state:
            print("❌ الملف غير مسجل | File not registered")
            return False

        # Move to REVIEW if in IMPORTED
        if "IMPORTED" in str(file_path):
            review_path = self.base_path / "REVIEW" / file_path.name
            file_path.rename(review_path)
            file_path = review_path
            self.ethical_gate.update_state(str(file_path), FileState.REVIEWING)

        # Display review interface
        print(f"\n🔍 مراجعة | Reviewing: {file_path.name}")
        print("═" * 60)

        # Auto-detect faces
        face_count = self.face_blur.detect_faces(str(file_path))

        print(f"\n📊 نتائج الفحص | Scan Results:")
        print(f"  👤 وجوه مكتشفة | Faces detected: {face_count}")

        if face_count > 0:
            print("\n⚠️  تحذير: وجوه مكتشفة بدون موافقة")
            print("   Warning: Faces detected without consent")
            print("\n   الخيارات | Options:")
            print("   1. hv blur {file_name}  → طمس الوجوه | Blur faces")
            print("   2. hv approve {file_name} --consent → موافقة موثقة | Documented consent")
            print("   3. hv reject {file_name}  → رفض | Reject")
        else:
            print("\n✓ لا توجد وجوه | No faces detected")
            print(f"  للموافقة: hv approve {file_path.name}")
            print(f"  To approve: hv approve {file_path.name}")

        self.logger.log("REVIEW", f"Reviewed: {file_path.name}, Faces: {face_count}")
        return True

    def cmd_blur(self, file_name: str):
        """
        Apply face blur to file
        تطبيق طمس الوجوه
        """
        file_path = self._find_file(file_name, ["IMPORTED", "REVIEW"])
        if not file_path:
            print(f"❌ الملف غير موجود | File not found: {file_name}")
            return False

        print(f"\n🔲 طمس الوجوه | Blurring faces: {file_path.name}")

        # Apply blur
        blurred_count = self.face_blur.blur_faces(str(file_path))

        if blurred_count > 0:
            # Move to REDACTED folder
            redacted_path = self.base_path / "REDACTED" / file_path.name
            file_path.rename(redacted_path)
            self.ethical_gate.update_state(str(redacted_path), FileState.REDACTED)

            print(f"✓ تم طمس {blurred_count} وجه | Blurred {blurred_count} faces")
            print(f"  الملف في: {redacted_path}")
            print(f"  للموافقة: hv approve {file_path.name}")
        else:
            print("  لا توجد وجوه للطمس | No faces to blur")

        self.logger.log("BLUR", f"Blurred: {file_path.name}, Count: {blurred_count}")
        return True

    def cmd_approve(self, file_name: str, consent: bool = False, location: str = ""):
        """
        Approve file after review
        الموافقة على الملف بعد المراجعة
        """
        file_path = self._find_file(file_name, ["REVIEW", "REDACTED"])
        if not file_path:
            print(f"❌ الملف غير موجود | File not found: {file_name}")
            return False

        # Check if file can be approved
        state = self.ethical_gate.get_file_state(str(file_path))

        # Verify no unblurred faces without consent
        face_count = self.face_blur.detect_faces(str(file_path))
        if face_count > 0 and not consent:
            print("❌ لا يمكن الموافقة | Cannot approve")
            print("   وجوه مكتشفة بدون موافقة موثقة")
            print("   Faces detected without documented consent")
            print("\n   استخدم --consent إذا كانت الموافقة موثقة")
            print("   Use --consent if consent is documented")
            return False

        # Move to APPROVED
        approved_path = self.base_path / "APPROVED" / file_path.name
        file_path.rename(approved_path)
        self.ethical_gate.update_state(str(approved_path), FileState.APPROVED)

        print(f"\n✓ تمت الموافقة | Approved: {file_path.name}")
        print(f"  الملف في: {approved_path}")
        print(f"  لإضافة تعليق: hv caption {file_path.name}")

        self.logger.log("APPROVE", f"Approved: {file_path.name}, Consent: {consent}")
        return True

    def cmd_reject(self, file_name: str, reason: str = ""):
        """
        Reject file
        رفض الملف
        """
        file_path = self._find_file(file_name, ["IMPORTED", "REVIEW", "REDACTED"])
        if not file_path:
            print(f"❌ الملف غير موجود | File not found: {file_name}")
            return False

        # Move to REJECTED
        rejected_path = self.base_path / "REJECTED" / file_path.name
        file_path.rename(rejected_path)
        self.ethical_gate.update_state(str(rejected_path), FileState.REJECTED, reason=reason)

        print(f"\n✗ تم الرفض | Rejected: {file_path.name}")
        if reason:
            print(f"  السبب | Reason: {reason}")

        self.logger.log("REJECT", f"Rejected: {file_path.name}, Reason: {reason}")
        return True

    def cmd_caption(self, file_name: str, interactive: bool = True):
        """
        Add caption to approved file
        إضافة تعليق توضيحي للملف الموافق عليه
        """
        file_path = self._find_file(file_name, ["APPROVED", "ARCHIVE"])
        if not file_path:
            print(f"❌ الملف غير موجود في الموافق عليها | File not in APPROVED: {file_name}")
            return False

        print(f"\n📝 إضافة تعليق | Adding caption: {file_path.name}")
        print("═" * 60)

        self.caption_engine.show_template()

        if interactive:
            caption_data = self.caption_engine.interactive_capture()

            # Validate caption
            if self.caption_engine.validate(caption_data):
                # Save caption
                caption_path = self.base_path / "CAPTIONS" / f"{file_path.stem}.json"
                with open(caption_path, 'w', encoding='utf-8') as f:
                    json.dump(caption_data, f, ensure_ascii=False, indent=2)

                print(f"\n✓ تم حفظ التعليق | Caption saved: {caption_path}")
            else:
                print("\n❌ التعليق غير مقبول | Caption rejected")

        return True

    def cmd_archive(self, file_name: str = None):
        """
        Archive approved files
        أرشفة الملفات الموافق عليها
        """
        if file_name:
            files = [self._find_file(file_name, ["APPROVED"])]
        else:
            files = list((self.base_path / "APPROVED").glob("*"))

        archived = 0
        for file_path in files:
            if file_path and file_path.exists():
                archive_path = self.base_path / "ARCHIVE" / file_path.name
                file_path.rename(archive_path)
                self.ethical_gate.update_state(str(archive_path), FileState.ARCHIVED)
                archived += 1

        print(f"\n📦 تم الأرشفة | Archived: {archived} files")
        self.logger.log("ARCHIVE", f"Archived {archived} files")
        return True

    def cmd_status(self):
        """
        Show system status
        عرض حالة النظام
        """
        print("\n📊 حالة النظام | System Status")
        print("═" * 60)

        if not self.config.get("initialized"):
            print("❌ النظام غير مهيأ | System not initialized")
            return

        print(f"  البعثة | Mission: {self.config.get('mission_name')}")
        print(f"  المسار | Path: {self.base_path}")
        print(f"  تاريخ الإنشاء | Created: {self.config.get('created_at', 'N/A')}")

        print("\n📁 الملفات | Files:")
        folders = ["IMPORTED", "REVIEW", "APPROVED", "REJECTED", "REDACTED", "ARCHIVE"]
        for folder in folders:
            folder_path = self.base_path / folder
            if folder_path.exists():
                count = len(list(folder_path.glob("*")))
                status_icon = {
                    "IMPORTED": "📥",
                    "REVIEW": "🔍",
                    "APPROVED": "✓",
                    "REJECTED": "✗",
                    "REDACTED": "🔲",
                    "ARCHIVE": "📦"
                }.get(folder, "📁")
                print(f"  {status_icon} {folder}: {count}")

    def cmd_dashboard(self):
        """
        Launch Streamlit dashboard
        تشغيل لوحة التحكم
        """
        print("\n🖥️ تشغيل لوحة التحكم | Launching Dashboard...")
        print("   URL: http://localhost:8501")
        print("   للإيقاف اضغط Ctrl+C | Press Ctrl+C to stop")

        dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(dashboard_path),
            "--server.address", "localhost",
            "--server.port", "8501"
        ])

    def _find_file(self, file_name: str, folders: List[str]) -> Optional[Path]:
        """Find file in specified folders"""
        for folder in folders:
            folder_path = self.base_path / folder
            if folder_path.exists():
                # Exact match
                exact = folder_path / file_name
                if exact.exists():
                    return exact
                # Partial match
                for f in folder_path.glob(f"*{file_name}*"):
                    return f
        return None


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="hv",
        description="🟥 Humanitarian Visual System - نظام التوثيق البصري الإنساني",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands / الأوامر:
  hv init                    Initialize mission | تهيئة البعثة
  hv import <file>           Import media file | استيراد ملف
  hv review <file>           Review for ethics | مراجعة أخلاقية
  hv blur <file>             Blur faces | طمس الوجوه
  hv approve <file>          Approve file | الموافقة
  hv reject <file>           Reject file | الرفض
  hv caption <file>          Add caption | إضافة تعليق
  hv archive [file]          Archive files | الأرشفة
  hv status                  Show status | عرض الحالة
  hv dashboard               Launch GUI | تشغيل الواجهة

Workflow / سير العمل:
  import → review → blur/approve/reject → caption → archive
        """
    )

    parser.add_argument("--base", "-b", default="./Gaza_Mission",
                        help="Base path for mission")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize mission")
    init_parser.add_argument("--name", "-n", default="Gaza Mission",
                             help="Mission name")

    # import
    import_parser = subparsers.add_parser("import", help="Import media file")
    import_parser.add_argument("file", help="File to import")
    import_parser.add_argument("--day", "-d", type=int, help="Mission day")

    # review
    review_parser = subparsers.add_parser("review", help="Review file")
    review_parser.add_argument("file", help="File to review")

    # blur
    blur_parser = subparsers.add_parser("blur", help="Blur faces")
    blur_parser.add_argument("file", help="File to blur")

    # approve
    approve_parser = subparsers.add_parser("approve", help="Approve file")
    approve_parser.add_argument("file", help="File to approve")
    approve_parser.add_argument("--consent", "-c", action="store_true",
                                help="Consent is documented")
    approve_parser.add_argument("--location", "-l", default="",
                                help="General location")

    # reject
    reject_parser = subparsers.add_parser("reject", help="Reject file")
    reject_parser.add_argument("file", help="File to reject")
    reject_parser.add_argument("--reason", "-r", default="",
                               help="Rejection reason")

    # caption
    caption_parser = subparsers.add_parser("caption", help="Add caption")
    caption_parser.add_argument("file", help="File to caption")

    # archive
    archive_parser = subparsers.add_parser("archive", help="Archive files")
    archive_parser.add_argument("file", nargs="?", help="Specific file to archive")

    # status
    subparsers.add_parser("status", help="Show status")

    # dashboard
    subparsers.add_parser("dashboard", help="Launch dashboard")

    args = parser.parse_args()

    # Initialize system
    system = HVSystem(args.base)
    system.show_banner()

    # Execute command
    if args.command == "init":
        system.cmd_init(args.name)
    elif args.command == "import":
        system.cmd_import(args.file, getattr(args, 'day', None))
    elif args.command == "review":
        system.cmd_review(args.file)
    elif args.command == "blur":
        system.cmd_blur(args.file)
    elif args.command == "approve":
        system.cmd_approve(args.file, args.consent, args.location)
    elif args.command == "reject":
        system.cmd_reject(args.file, args.reason)
    elif args.command == "caption":
        system.cmd_caption(args.file)
    elif args.command == "archive":
        system.cmd_archive(args.file)
    elif args.command == "status":
        system.cmd_status()
    elif args.command == "dashboard":
        system.cmd_dashboard()
    else:
        system.cmd_status()


if __name__ == "__main__":
    main()
