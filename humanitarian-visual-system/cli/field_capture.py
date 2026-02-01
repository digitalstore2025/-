#!/usr/bin/env python3
"""
Field Capture CLI - Humanitarian Visual System
أداة التصوير الميداني - سطر الأوامر

Command-line tool for field photographers to manage
daily capture workflow, file organization, and ethical compliance.

أداة سطر أوامر للمصورين الميدانيين لإدارة
سير العمل اليومي للتصوير، تنظيم الملفات، والامتثال الأخلاقي.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_manager import FileManager, MediaCategory
from core.ethical_gate import EthicalGate, ApprovalStatus
from core.metadata import MetadataHandler


class FieldCaptureCLI:
    """
    أداة التصوير الميداني
    Field Capture Command Line Interface
    """

    def __init__(self, base_path: str = "./Gaza_Mission"):
        self.base_path = Path(base_path)
        self.file_manager = FileManager(str(self.base_path))
        self.ethical_gate = EthicalGate()
        self.metadata_handler = MetadataHandler()

    def show_banner(self):
        """Display the system banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🌙 الهلال الأحمر التركي | Turkish Red Crescent                ║
║   ─────────────────────────────────────────────────────────────  ║
║   نظام التنفيذ البصري الإنساني                                   ║
║   Humanitarian Visual Execution System                           ║
║   ─────────────────────────────────────────────────────────────  ║
║   Gaza Edition | إصدار غزة                                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def show_constraints(self):
        """Display ethical constraints reminder"""
        constraints = """
⚠️  القيود المطلقة | Non-Negotiable Constraints
═══════════════════════════════════════════════════════════════

  ❌ لا تصوير يعرّض المستفيد للخطر | No endangering beneficiaries
  ❌ لا وجوه بدون موافقة | No faces without consent
  ❌ لا جثامين أو إصابات صادمة | No bodies or graphic injuries
  ❌ لا تحديد مواقع حساسة | No sensitive locations
  ❌ لا مؤثرات درامية | No dramatic effects

═══════════════════════════════════════════════════════════════
        """
        print(constraints)

    def init_mission(self):
        """Initialize mission directory structure"""
        print("\n📁 تهيئة هيكل البعثة | Initializing Mission Structure...")
        self.file_manager.initialize_structure()
        print(f"✓ تم إنشاء الهيكل في | Structure created at: {self.base_path}")
        print("\nالمجلدات المنشأة | Created folders:")
        for folder in ["RAW", "AUDIO", "SELECTS", "EDIT", "FINAL", "LOGS"]:
            print(f"  📂 {folder}/")

    def start_day(self, day_number: int = None):
        """Start a new capture day"""
        if day_number:
            self.file_manager.set_current_day(day_number)
        else:
            day_number = self.file_manager.advance_day()

        print(f"\n📅 بدء يوم جديد | Starting Day {day_number}")
        print("="*50)

        # Show camera preset reminder
        self.show_camera_preset()

        # Show shot sequence
        self.show_shot_sequence()

    def show_camera_preset(self):
        """Display recommended camera settings"""
        print("""
📷 إعدادات الكاميرا | Camera Settings
──────────────────────────────────────
  الوضع | Mode:        Manual + Auto ISO
  الحد الأقصى ISO:     6400
  سرعة الغالق | Shutter: ≥ 1/100
  الفتحة | Aperture:   f/2.8 – f/4
  توازن الأبيض:       تلقائي | Auto
  ملف الصورة:         محايد | Neutral
──────────────────────────────────────
        """)

    def show_shot_sequence(self):
        """Display required shot sequence"""
        print("""
🎬 تسلسل اللقطات | Shot Sequence
──────────────────────────────────────
  1️⃣  لقطة تأسيسية | Establishing (Wide)
      ↓
  2️⃣  لقطة فعل | Action (Aid in progress)
      ↓
  3️⃣  لقطة تفصيلية | Detail (Hands/interaction)
      ↓
  🚪 الخروج إذا زاد الخطر | Exit if risk increases
──────────────────────────────────────
        """)

    def import_media(self, source_path: str, day: int = None):
        """Import media from source directory"""
        print(f"\n📥 استيراد من | Importing from: {source_path}")

        if not os.path.exists(source_path):
            print(f"❌ المسار غير موجود | Path not found: {source_path}")
            return

        results = self.file_manager.import_directory(source_path, day=day)

        print(f"\n✓ تم استيراد | Imported: {len(results)} files")

        # Categorize results
        images = len([r for r in results if 'image' in str(r.category)])
        videos = len([r for r in results if 'video' in str(r.category) or r.category == MediaCategory.RAW])
        audio = len([r for r in results if r.category == MediaCategory.AUDIO])

        print(f"  📷 صور | Images: {images}")
        print(f"  🎬 فيديو | Video: {videos}")
        print(f"  🎙️ صوت | Audio: {audio}")

    def quick_review(self, directory: str = None):
        """Perform quick ethical review"""
        directory = directory or str(self.base_path / "RAW")

        print(f"\n🔍 مراجعة أخلاقية سريعة | Quick Ethical Review")
        print("="*50)

        results = self.ethical_gate.batch_review(directory)

        approved = len([r for r in results if r.status == ApprovalStatus.APPROVED])
        rejected = len([r for r in results if r.status == ApprovalStatus.REJECTED])
        pending = len([r for r in results if r.status == ApprovalStatus.REQUIRES_REVIEW])

        print(f"\n📊 النتائج | Results:")
        print(f"  ✓ موافق | Approved: {approved}")
        print(f"  ✗ مرفوض | Rejected: {rejected}")
        print(f"  ⏳ قيد المراجعة | Pending: {pending}")

        if rejected > 0:
            print("\n⚠️ أسباب الرفض | Rejection Reasons:")
            summary = self.ethical_gate.get_rejection_summary()
            for reason, count in summary.items():
                print(f"  - {reason}: {count}")

    def daily_summary(self):
        """Show daily summary"""
        summary = self.file_manager.get_mission_summary()

        print("\n📊 ملخص البعثة | Mission Summary")
        print("="*50)
        print(f"  المسار | Path: {summary['base_path']}")
        print(f"  اليوم الحالي | Current Day: {summary['current_day']}")
        print(f"  إجمالي الملفات | Total Files: {summary['total_files']}")
        print(f"  الحجم | Size: {summary['total_size_mb']} MB")

        print("\n📁 حسب التصنيف | By Category:")
        for cat, info in summary['categories'].items():
            print(f"  {cat}: {info['files']} files ({info['size_mb']} MB)")

    def backup(self, destination: str):
        """Create backup of mission files"""
        print(f"\n💾 إنشاء نسخة احتياطية | Creating Backup...")

        try:
            files_count, total_size = self.file_manager.create_backup(destination)
            print(f"✓ تم النسخ | Backup complete:")
            print(f"  📁 الملفات | Files: {files_count}")
            print(f"  📦 الحجم | Size: {total_size / 1024 / 1024:.2f} MB")
        except Exception as e:
            print(f"❌ فشل النسخ | Backup failed: {e}")


def main():
    """Main entry point for Field Capture CLI"""
    parser = argparse.ArgumentParser(
        description="نظام التنفيذ البصري الإنساني | Humanitarian Visual System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / أمثلة:
  %(prog)s --init                    Initialize mission structure
  %(prog)s --day 1                   Start day 1
  %(prog)s --import /path/to/card    Import from memory card
  %(prog)s --review                  Quick ethical review
  %(prog)s --summary                 Show daily summary
  %(prog)s --backup /path/to/backup  Create backup
        """
    )

    parser.add_argument(
        "--base",
        default="./Gaza_Mission",
        help="Base path for mission files"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize mission structure"
    )
    parser.add_argument(
        "--day",
        type=int,
        help="Set/start mission day number"
    )
    parser.add_argument(
        "--import",
        dest="import_path",
        help="Import media from path"
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="Run quick ethical review"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show mission summary"
    )
    parser.add_argument(
        "--backup",
        help="Backup destination path"
    )
    parser.add_argument(
        "--constraints",
        action="store_true",
        help="Show ethical constraints"
    )

    args = parser.parse_args()

    cli = FieldCaptureCLI(args.base)
    cli.show_banner()

    if args.constraints:
        cli.show_constraints()
        return

    if args.init:
        cli.init_mission()
        return

    if args.day:
        cli.start_day(args.day)

    if args.import_path:
        cli.import_media(args.import_path, day=args.day)

    if args.review:
        cli.quick_review()

    if args.summary:
        cli.daily_summary()

    if args.backup:
        cli.backup(args.backup)

    # If no specific action, show help
    if not any([args.init, args.day, args.import_path, args.review, args.summary, args.backup]):
        cli.show_constraints()
        cli.daily_summary()


if __name__ == "__main__":
    main()
