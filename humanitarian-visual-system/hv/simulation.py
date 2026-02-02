#!/usr/bin/env python3
"""
Simulation Mode - Training Environment
وضع المحاكاة - بيئة التدريب

Provides a safe training environment with simulated scenarios
for photographers and reviewers to practice without real data.

يوفر بيئة تدريب آمنة مع سيناريوهات محاكاة
للمصورين والمراجعين للتمرن بدون بيانات حقيقية.

Usage:
    hv simulate --scenario basic_import
    hv simulate --scenario face_blur
    hv simulate --scenario graphic_content
    hv simulate --test competency

الاستخدام:
    hv simulate --scenario basic_import
    hv simulate --scenario face_blur
    hv simulate --scenario graphic_content
    hv simulate --test competency
"""

import os
import sys
import json
import shutil
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ScenarioType(Enum):
    """Training scenario types"""
    BASIC_IMPORT = "basic_import"
    FACE_BLUR = "face_blur"
    MULTIPLE_FACES = "multiple_faces"
    GRAPHIC_CONTENT = "graphic_content"
    METADATA_STRIP = "metadata_strip"
    CAPTION_WRITING = "caption_writing"
    FULL_WORKFLOW = "full_workflow"
    EMERGENCY_MODE = "emergency_mode"
    CONSENT_FLOW = "consent_flow"
    REJECTION_CASES = "rejection_cases"


@dataclass
class TrainingScenario:
    """Training scenario definition"""
    name: str
    name_ar: str
    description: str
    description_ar: str
    difficulty: str  # basic, intermediate, advanced
    expected_actions: List[str]
    success_criteria: Dict[str, any]
    hints: List[str]
    hints_ar: List[str]


@dataclass
class CompetencyQuestion:
    """Competency test question"""
    question: str
    question_ar: str
    options: List[str]
    correct_index: int
    explanation: str
    explanation_ar: str


class SimulationEngine:
    """
    محرك المحاكاة للتدريب
    Simulation Engine for Training

    Creates safe training environments with synthetic data
    and guided scenarios for learning the system.
    """

    SCENARIOS = {
        ScenarioType.BASIC_IMPORT: TrainingScenario(
            name="Basic Import",
            name_ar="الاستيراد الأساسي",
            description="Learn to import and review a simple image",
            description_ar="تعلم استيراد ومراجعة صورة بسيطة",
            difficulty="basic",
            expected_actions=["import", "review", "approve"],
            success_criteria={"file_imported": True, "reviewed": True, "approved": True},
            hints=["Use 'hv import <file>' to start", "Then 'hv review <file>'"],
            hints_ar=["استخدم 'hv import <file>' للبدء", "ثم 'hv review <file>'"]
        ),
        ScenarioType.FACE_BLUR: TrainingScenario(
            name="Face Blur",
            name_ar="طمس الوجوه",
            description="Practice detecting and blurring faces",
            description_ar="تمرن على كشف وطمس الوجوه",
            difficulty="basic",
            expected_actions=["import", "review", "blur", "approve"],
            success_criteria={"faces_blurred": True, "approved": True},
            hints=["Review will show face count", "Use 'hv blur' before approve"],
            hints_ar=["المراجعة ستظهر عدد الوجوه", "استخدم 'hv blur' قبل الموافقة"]
        ),
        ScenarioType.MULTIPLE_FACES: TrainingScenario(
            name="Multiple Faces",
            name_ar="وجوه متعددة",
            description="Handle an image with multiple faces",
            description_ar="التعامل مع صورة بوجوه متعددة",
            difficulty="intermediate",
            expected_actions=["import", "review", "blur", "verify", "approve"],
            success_criteria={"all_faces_blurred": True, "verified": True},
            hints=["Check face count after blur", "Verify all are blurred"],
            hints_ar=["تحقق من عدد الوجوه بعد الطمس", "تأكد من طمس الجميع"]
        ),
        ScenarioType.GRAPHIC_CONTENT: TrainingScenario(
            name="Graphic Content Detection",
            name_ar="كشف المحتوى الصادم",
            description="Learn how graphic content is auto-rejected",
            description_ar="تعلم كيف يُرفض المحتوى الصادم تلقائياً",
            difficulty="basic",
            expected_actions=["import"],
            success_criteria={"auto_rejected": True},
            hints=["System will auto-reject", "Check REJECTED folder"],
            hints_ar=["النظام سيرفض تلقائياً", "تحقق من مجلد REJECTED"]
        ),
        ScenarioType.CAPTION_WRITING: TrainingScenario(
            name="Caption Writing",
            name_ar="كتابة التعليقات",
            description="Practice writing ethical captions",
            description_ar="تمرن على كتابة تعليقات أخلاقية",
            difficulty="intermediate",
            expected_actions=["caption", "validate"],
            success_criteria={"caption_valid": True, "no_forbidden_terms": True},
            hints=["Avoid political terms", "Use general locations only"],
            hints_ar=["تجنب المصطلحات السياسية", "استخدم مواقع عامة فقط"]
        ),
        ScenarioType.FULL_WORKFLOW: TrainingScenario(
            name="Full Workflow",
            name_ar="سير العمل الكامل",
            description="Complete end-to-end workflow",
            description_ar="سير العمل الكامل من البداية للنهاية",
            difficulty="advanced",
            expected_actions=["import", "review", "blur", "approve", "caption", "archive"],
            success_criteria={"archived": True, "captioned": True, "log_complete": True},
            hints=["Follow the workflow order", "Check status at each step"],
            hints_ar=["اتبع ترتيب سير العمل", "تحقق من الحالة في كل خطوة"]
        ),
    }

    COMPETENCY_QUESTIONS = [
        CompetencyQuestion(
            question="What happens when a face is detected without consent?",
            question_ar="ماذا يحدث عند اكتشاف وجه بدون موافقة؟",
            options=[
                "The image is automatically deleted",
                "The system requires blur or documented consent",
                "The image is published anyway",
                "Nothing happens"
            ],
            correct_index=1,
            explanation="The system requires either blur or documented consent before approval",
            explanation_ar="النظام يتطلب إما طمس أو موافقة موثقة قبل الموافقة"
        ),
        CompetencyQuestion(
            question="Which of these is a forbidden term in captions?",
            question_ar="أي من هذه المصطلحات ممنوعة في التعليقات؟",
            options=[
                "Humanitarian aid",
                "Food distribution",
                "Massacre",
                "Medical treatment"
            ],
            correct_index=2,
            explanation="Political and emotional terms like 'massacre' are forbidden",
            explanation_ar="المصطلحات السياسية والعاطفية مثل 'مجزرة' ممنوعة"
        ),
        CompetencyQuestion(
            question="What metadata is automatically stripped?",
            question_ar="ما البيانات التي تُحذف تلقائياً؟",
            options=[
                "Image dimensions",
                "GPS coordinates and device ID",
                "File format",
                "Color profile"
            ],
            correct_index=1,
            explanation="GPS, device ID, and exact timestamps are stripped for safety",
            explanation_ar="إحداثيات GPS ومعرّف الجهاز والتوقيت الدقيق تُحذف للسلامة"
        ),
        CompetencyQuestion(
            question="Can workflow stages be skipped?",
            question_ar="هل يمكن تجاوز مراحل سير العمل؟",
            options=[
                "Yes, if in a hurry",
                "Yes, with admin permission",
                "No, the system prevents it programmatically",
                "Only in emergency mode"
            ],
            correct_index=2,
            explanation="Stages cannot be skipped - the system enforces this",
            explanation_ar="لا يمكن تجاوز المراحل - النظام يمنع ذلك برمجياً"
        ),
        CompetencyQuestion(
            question="What is the purpose of hash-chained logs?",
            question_ar="ما الغرض من السجلات المتسلسلة بالتجزئة؟",
            options=[
                "Faster searching",
                "Smaller file size",
                "Integrity verification and tamper detection",
                "Better formatting"
            ],
            correct_index=2,
            explanation="Hash chains ensure logs cannot be tampered with",
            explanation_ar="سلاسل التجزئة تضمن عدم التلاعب بالسجلات"
        ),
        CompetencyQuestion(
            question="When is 'hv approve --consent' used?",
            question_ar="متى يُستخدم 'hv approve --consent'؟",
            options=[
                "Always",
                "When faces are shown with documented permission",
                "For video files only",
                "Never"
            ],
            correct_index=1,
            explanation="Use --consent when you have documented permission to show faces",
            explanation_ar="استخدم --consent عندما تملك إذناً موثقاً لإظهار الوجوه"
        ),
        CompetencyQuestion(
            question="What type of location should be used in captions?",
            question_ar="ما نوع الموقع الذي يجب استخدامه في التعليقات؟",
            options=[
                "Exact street address",
                "GPS coordinates",
                "General area only (e.g., 'Northern Gaza')",
                "Building name"
            ],
            correct_index=2,
            explanation="Only general locations to protect sensitive areas",
            explanation_ar="مواقع عامة فقط لحماية المناطق الحساسة"
        ),
        CompetencyQuestion(
            question="What happens to graphic content during import?",
            question_ar="ماذا يحدث للمحتوى الصادم عند الاستيراد؟",
            options=[
                "It's automatically approved",
                "It requires manual review",
                "It's automatically rejected",
                "It's blurred and approved"
            ],
            correct_index=2,
            explanation="Graphic content is automatically rejected by the ethical gate",
            explanation_ar="المحتوى الصادم يُرفض تلقائياً بواسطة البوابة الأخلاقية"
        ),
        CompetencyQuestion(
            question="Does the system work without internet?",
            question_ar="هل يعمل النظام بدون إنترنت؟",
            options=[
                "No, it requires cloud connection",
                "Yes, it's designed for offline field use",
                "Only for viewing files",
                "Only with special license"
            ],
            correct_index=1,
            explanation="The system is designed for offline field operations",
            explanation_ar="النظام مصمم للعمل الميداني بدون إنترنت"
        ),
        CompetencyQuestion(
            question="What is the correct workflow order?",
            question_ar="ما الترتيب الصحيح لسير العمل؟",
            options=[
                "Caption → Import → Approve → Archive",
                "Import → Review → Approve/Reject → Caption → Archive",
                "Archive → Import → Caption → Review",
                "Approve → Import → Review → Caption"
            ],
            correct_index=1,
            explanation="Import → Review → Approve/Reject → Caption → Archive",
            explanation_ar="استيراد → مراجعة → موافقة/رفض → تعليق → أرشفة"
        ),
    ]

    def __init__(self, base_path: str = "./Training_Mission"):
        """Initialize simulation engine"""
        self.base_path = Path(base_path)
        self.results_path = self.base_path / "SIMULATION_RESULTS"
        self.current_scenario: Optional[TrainingScenario] = None
        self.actions_log: List[Dict] = []
        self.score = 0

    def initialize(self):
        """Initialize training environment"""
        print("\n" + "=" * 60)
        print("🎓 SIMULATION MODE | وضع المحاكاة")
        print("=" * 60)

        # Create training directory structure
        directories = [
            "RAW", "IMPORTED", "REVIEW", "APPROVED", "REJECTED",
            "REDACTED", "ARCHIVE", "LOGS", "CAPTIONS",
            "SIMULATION_RESULTS", "TRAINING_ASSETS"
        ]

        for dir_name in directories:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)

        print(f"✓ Training environment created: {self.base_path}")
        print("✓ All directories initialized")
        print("\n⚠️  This is a SIMULATION - no real data is used")
        print("   هذه محاكاة - لا تُستخدم بيانات حقيقية\n")

    def generate_training_image(
        self,
        scenario: ScenarioType,
        filename: str = None
    ) -> Path:
        """Generate a synthetic training image"""
        if not PIL_AVAILABLE:
            print("⚠️  PIL not available - using placeholder")
            return self._create_placeholder(filename or "training_image.txt")

        # Image settings based on scenario
        settings = {
            ScenarioType.BASIC_IMPORT: {
                "size": (800, 600),
                "color": "#4a90d9",
                "text": "TRAINING IMAGE\nصورة تدريبية",
                "faces": 0
            },
            ScenarioType.FACE_BLUR: {
                "size": (800, 600),
                "color": "#5cb85c",
                "text": "FACE DETECTION TEST\nاختبار كشف الوجوه",
                "faces": 1
            },
            ScenarioType.MULTIPLE_FACES: {
                "size": (1200, 800),
                "color": "#f0ad4e",
                "text": "MULTIPLE FACES\nوجوه متعددة",
                "faces": 3
            },
            ScenarioType.GRAPHIC_CONTENT: {
                "size": (800, 600),
                "color": "#d9534f",
                "text": "⚠️ GRAPHIC CONTENT SIMULATION\n⚠️ محاكاة محتوى صادم",
                "faces": 0,
                "flag": "graphic"
            },
        }

        config = settings.get(scenario, settings[ScenarioType.BASIC_IMPORT])

        # Create image
        img = Image.new('RGB', config["size"], config["color"])
        draw = ImageDraw.Draw(img)

        # Add text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except:
            font = ImageFont.load_default()

        text = config["text"]
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (config["size"][0] - text_width) // 2
        y = (config["size"][1] - text_height) // 2
        draw.text((x, y), text, fill="white", font=font)

        # Add simulated faces (circles)
        if config["faces"] > 0:
            for i in range(config["faces"]):
                cx = 150 + i * 250
                cy = config["size"][1] - 150
                r = 50
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline="yellow", width=3)
                draw.text((cx-20, cy+r+10), f"Face {i+1}", fill="yellow")

        # Add simulation watermark
        draw.text((10, 10), "🎓 SIMULATION MODE", fill="white")
        draw.text((10, config["size"][1] - 30), f"Scenario: {scenario.value}", fill="white")

        # Save
        if filename is None:
            filename = f"training_{scenario.value}_{datetime.now().strftime('%H%M%S')}.jpg"

        output_path = self.base_path / "TRAINING_ASSETS" / filename
        img.save(output_path, "JPEG", quality=85)

        # Add metadata flag if graphic content
        if config.get("flag") == "graphic":
            self._add_graphic_flag(output_path)

        print(f"✓ Generated: {filename}")
        return output_path

    def _create_placeholder(self, filename: str) -> Path:
        """Create placeholder file when PIL unavailable"""
        output_path = self.base_path / "TRAINING_ASSETS" / filename
        with open(output_path, 'w') as f:
            f.write(f"SIMULATION PLACEHOLDER\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
            f.write(f"This is a training file\n")
        return output_path

    def _add_graphic_flag(self, path: Path):
        """Add flag file for graphic content simulation"""
        flag_path = path.with_suffix('.flag')
        with open(flag_path, 'w') as f:
            f.write("GRAPHIC_CONTENT_SIMULATION")

    def run_scenario(self, scenario_type: ScenarioType) -> Dict:
        """Run a training scenario"""
        if scenario_type not in self.SCENARIOS:
            print(f"❌ Unknown scenario: {scenario_type}")
            return {"success": False}

        scenario = self.SCENARIOS[scenario_type]
        self.current_scenario = scenario
        self.actions_log = []

        print(f"\n{'='*60}")
        print(f"🎯 SCENARIO: {scenario.name}")
        print(f"   {scenario.name_ar}")
        print(f"{'='*60}")
        print(f"\n📋 Description: {scenario.description}")
        print(f"   الوصف: {scenario.description_ar}")
        print(f"\n⭐ Difficulty: {scenario.difficulty}")
        print(f"\n📝 Expected actions: {' → '.join(scenario.expected_actions)}")

        print(f"\n💡 Hints:")
        for i, hint in enumerate(scenario.hints, 1):
            print(f"   {i}. {hint}")
            print(f"      {scenario.hints_ar[i-1]}")

        # Generate training asset
        print(f"\n⏳ Generating training assets...")
        asset_path = self.generate_training_image(scenario_type)

        print(f"\n🚀 START THE SCENARIO:")
        print(f"   hv import {asset_path}")

        return {
            "success": True,
            "scenario": scenario.name,
            "asset_path": str(asset_path),
            "expected_actions": scenario.expected_actions
        }

    def run_competency_test(self, language: str = "en") -> Dict:
        """Run competency test"""
        print("\n" + "=" * 60)
        print("📝 COMPETENCY TEST | اختبار الكفاءة")
        print("=" * 60)

        questions = self.COMPETENCY_QUESTIONS
        random.shuffle(questions)

        correct = 0
        total = len(questions)
        results = []

        print(f"\n📊 {total} questions | {total} أسئلة")
        print("   Select the correct answer (1-4)\n")

        for i, q in enumerate(questions, 1):
            print(f"\n{'─'*50}")
            print(f"Question {i}/{total}:")

            if language == "ar":
                print(f"  {q.question_ar}")
            else:
                print(f"  {q.question}")

            for j, opt in enumerate(q.options, 1):
                print(f"    {j}. {opt}")

            # In real implementation, would get user input
            # For now, show correct answer
            print(f"\n  ✓ Correct answer: {q.correct_index + 1}")
            print(f"    {q.explanation}")
            if language == "ar":
                print(f"    {q.explanation_ar}")

            results.append({
                "question": q.question,
                "correct": q.correct_index + 1
            })

        # Calculate score
        score_percent = (correct / total) * 100 if total > 0 else 0

        print(f"\n{'='*60}")
        print(f"📊 TEST COMPLETE | انتهى الاختبار")
        print(f"{'='*60}")
        print(f"\n   Questions: {total}")
        print(f"   Passing score: 80%")
        print(f"\n   Run this test interactively with:")
        print(f"   hv simulate --test competency --interactive")

        # Save results
        self._save_test_results(results)

        return {
            "total_questions": total,
            "passing_score": 80,
            "results": results
        }

    def _save_test_results(self, results: List[Dict]):
        """Save test results"""
        results_file = self.results_path / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.results_path.mkdir(exist_ok=True)

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_type": "competency",
                "results": results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Results saved: {results_file}")

    def list_scenarios(self):
        """List available scenarios"""
        print("\n" + "=" * 60)
        print("📚 AVAILABLE SCENARIOS | السيناريوهات المتاحة")
        print("=" * 60)

        for scenario_type, scenario in self.SCENARIOS.items():
            difficulty_icon = {
                "basic": "🟢",
                "intermediate": "🟡",
                "advanced": "🔴"
            }.get(scenario.difficulty, "⚪")

            print(f"\n{difficulty_icon} {scenario_type.value}")
            print(f"   {scenario.name} | {scenario.name_ar}")
            print(f"   {scenario.description}")

        print(f"\n{'─'*60}")
        print("Usage: hv simulate --scenario <name>")
        print("       hv simulate --test competency")


def main():
    """CLI entry point for simulation"""
    parser = argparse.ArgumentParser(
        description="🎓 HV Simulation Mode | وضع المحاكاة",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--scenario", "-s",
                        choices=[s.value for s in ScenarioType],
                        help="Scenario to run")
    parser.add_argument("--test", "-t",
                        choices=["competency"],
                        help="Test to run")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List available scenarios")
    parser.add_argument("--language", default="en",
                        choices=["en", "ar"],
                        help="Language for test")
    parser.add_argument("--base", "-b", default="./Training_Mission",
                        help="Base path for training")

    args = parser.parse_args()

    engine = SimulationEngine(args.base)
    engine.initialize()

    if args.list:
        engine.list_scenarios()
    elif args.scenario:
        scenario_type = ScenarioType(args.scenario)
        engine.run_scenario(scenario_type)
    elif args.test:
        if args.test == "competency":
            engine.run_competency_test(args.language)
    else:
        engine.list_scenarios()


if __name__ == "__main__":
    main()
