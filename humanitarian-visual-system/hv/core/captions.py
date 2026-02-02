#!/usr/bin/env python3
"""
Caption Engine - Ethical Caption Generation and Validation
محرك التعليقات التوضيحية - توليد والتحقق من التعليقات الأخلاقية

Ensures captions follow humanitarian documentation guidelines:
- No political characterization
- No emotional manipulation
- No exaggeration
- Facts only

يضمن أن التعليقات تتبع إرشادات التوثيق الإنساني:
- لا توصيف سياسي
- لا استعطاف
- لا مبالغة لغوية
- حقائق فقط
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CaptionEngine:
    """
    محرك التعليقات التوضيحية
    Caption Generation and Validation Engine

    Provides templates and validation for humanitarian media captions.
    يوفر قوالب والتحقق من تعليقات الوسائط الإنسانية.
    """

    # Caption template
    TEMPLATE = {
        "what": {
            "ar": "ما الذي يحدث؟",
            "en": "What is happening?"
        },
        "where": {
            "ar": "أين؟ (بصيغة عامة فقط)",
            "en": "Where? (general location only)"
        },
        "intervention": {
            "ar": "التدخل الإنساني:",
            "en": "Humanitarian intervention:"
        },
        "impact": {
            "ar": "الأثر:",
            "en": "Impact:"
        }
    }

    # Forbidden words/patterns (political, emotional manipulation, exaggeration)
    FORBIDDEN_PATTERNS = {
        "ar": [
            r"إرهاب",
            r"عدو",
            r"انتصار",
            r"هزيمة",
            r"أبطال",
            r"شهيد",  # Use neutral terms
            r"مجزرة",  # Use factual descriptions
            r"وحشي",
            r"بربري",
            r"إجرام",
            r"عملاء",
            r"خونة",
            r"صهاين",
            r"صهيوني",
        ],
        "en": [
            r"terrorist",
            r"enemy",
            r"victory",
            r"defeat",
            r"heroes",
            r"martyr",  # Use neutral terms
            r"massacre",  # Use factual descriptions
            r"savage",
            r"barbaric",
            r"criminal",
            r"agents",
            r"traitors",
            r"zionist",
        ]
    }

    # Emotional manipulation patterns
    EMOTIONAL_PATTERNS = [
        r"!\s*!",  # Multiple exclamation marks
        r"\?\s*\?",  # Multiple question marks
        r"\.{4,}",  # Excessive ellipsis
        r"[A-Z]{5,}",  # All caps words (English)
    ]

    # Valid general locations for Gaza
    VALID_LOCATIONS = [
        "غزة", "Gaza",
        "شمال غزة", "Northern Gaza",
        "جنوب غزة", "Southern Gaza",
        "وسط غزة", "Central Gaza",
        "رفح", "Rafah",
        "خان يونس", "Khan Younis",
        "دير البلح", "Deir al-Balah",
        "جباليا", "Jabalia",
        "بيت لاهيا", "Beit Lahia",
        "بيت حانون", "Beit Hanoun"
    ]

    def __init__(self, language: str = "ar"):
        """
        Initialize CaptionEngine

        Args:
            language: Default language ('ar' or 'en')
        """
        self.language = language

    def show_template(self, language: str = None):
        """
        Display caption template

        عرض قالب التعليق
        """
        lang = language or self.language

        print("\n📝 قالب التعليق التوضيحي | Caption Template")
        print("═" * 60)

        for field, labels in self.TEMPLATE.items():
            label = labels.get(lang, labels["en"])
            print(f"\n  {label}")
            print(f"  {'─' * 40}")
            print(f"  [                                        ]")

        print("\n" + "═" * 60)
        print("⚠️  ممنوع | Forbidden:")
        print("   • توصيف سياسي | Political characterization")
        print("   • استعطاف | Emotional manipulation")
        print("   • مبالغة لغوية | Exaggeration")
        print("═" * 60)

    def interactive_capture(self, language: str = None) -> Dict[str, str]:
        """
        Interactive caption capture

        التقاط تعليق تفاعلي
        """
        lang = language or self.language
        caption_data = {
            "language": lang,
            "created_at": datetime.now().isoformat()
        }

        print("\n📝 إدخال التعليق | Enter Caption")
        print("═" * 60)

        for field, labels in self.TEMPLATE.items():
            label = labels.get(lang, labels["en"])
            print(f"\n{label}")

            # Get input
            value = input("→ ").strip()

            # Validate immediately
            if value:
                issues = self._check_text(value, lang)
                if issues:
                    print(f"\n⚠️  تحذير | Warning:")
                    for issue in issues:
                        print(f"   • {issue}")
                    # Allow correction
                    retry = input("هل تريد إعادة الإدخال؟ (y/n) | Retry? (y/n): ")
                    if retry.lower() == 'y':
                        value = input("→ ").strip()

            caption_data[field] = value

        return caption_data

    def validate(self, caption_data: Dict[str, str]) -> bool:
        """
        Validate caption against ethical guidelines

        التحقق من التعليق وفق الإرشادات الأخلاقية

        Returns:
            True if caption is valid
        """
        issues = []
        lang = caption_data.get("language", self.language)

        # Check required fields
        required_fields = ["what", "where", "intervention", "impact"]
        for field in required_fields:
            if not caption_data.get(field):
                issues.append(f"Missing required field: {field}")

        # Check each field
        for field, value in caption_data.items():
            if field in required_fields and value:
                field_issues = self._check_text(value, lang)
                issues.extend(field_issues)

        # Check location
        location = caption_data.get("where", "")
        if location and not self._is_valid_location(location):
            issues.append(f"Location too specific or invalid: {location}")

        if issues:
            print("\n❌ تحذيرات التحقق | Validation Warnings:")
            for issue in issues:
                print(f"   • {issue}")
            return False

        return True

    def _check_text(self, text: str, language: str) -> List[str]:
        """Check text for forbidden patterns"""
        issues = []

        # Check forbidden words
        forbidden = self.FORBIDDEN_PATTERNS.get(language, [])
        for pattern in forbidden:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Forbidden term detected: {pattern}")

        # Check emotional patterns
        for pattern in self.EMOTIONAL_PATTERNS:
            if re.search(pattern, text):
                issues.append(f"Emotional manipulation detected: {pattern}")

        # Check length (captions should be concise)
        if len(text) > 500:
            issues.append("Caption too long (max 500 characters)")

        return issues

    def _is_valid_location(self, location: str) -> bool:
        """Check if location is general enough"""
        location_lower = location.lower()

        # Check against valid locations
        for valid in self.VALID_LOCATIONS:
            if valid.lower() in location_lower or location_lower in valid.lower():
                return True

        # Reject if contains specific indicators
        specific_indicators = [
            r"\d+",  # Numbers (street numbers, coordinates)
            r"شارع|street",  # Street names
            r"مبنى|building",
            r"coordinates|إحداثيات",
        ]

        for indicator in specific_indicators:
            if re.search(indicator, location, re.IGNORECASE):
                return False

        return True

    def format_caption(
        self,
        caption_data: Dict[str, str],
        style: str = "standard"
    ) -> str:
        """
        Format caption for output

        تنسيق التعليق للإخراج

        Args:
            caption_data: Caption data dictionary
            style: Output style ('standard', 'minimal', 'full')
        """
        lang = caption_data.get("language", self.language)

        if style == "minimal":
            return f"{caption_data.get('what', '')} - {caption_data.get('where', '')}"

        elif style == "full":
            lines = []
            for field, labels in self.TEMPLATE.items():
                label = labels.get(lang, labels["en"])
                value = caption_data.get(field, "")
                if value:
                    lines.append(f"{label} {value}")
            return "\n".join(lines)

        else:  # standard
            what = caption_data.get("what", "")
            where = caption_data.get("where", "")
            intervention = caption_data.get("intervention", "")
            impact = caption_data.get("impact", "")

            return f"{what}\n📍 {where}\n🤝 {intervention}\n📊 {impact}"

    def save_caption(
        self,
        caption_data: Dict[str, str],
        output_path: str
    ):
        """
        Save caption to file

        حفظ التعليق في ملف
        """
        # Add metadata
        caption_data["saved_at"] = datetime.now().isoformat()
        caption_data["version"] = "1.0"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(caption_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Caption saved: {output_path}")

    def load_caption(self, file_path: str) -> Optional[Dict[str, str]]:
        """
        Load caption from file

        تحميل التعليق من ملف
        """
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_suggested_caption(
        self,
        media_type: str,
        location: str,
        intervention_type: str
    ) -> Dict[str, str]:
        """
        Generate suggested caption template

        توليد قالب تعليق مقترح
        """
        templates = {
            "food_distribution": {
                "what": "توزيع مساعدات غذائية على العائلات المتضررة",
                "intervention": "تقديم سلال غذائية تحتوي على مواد أساسية",
                "impact": "استفادت [عدد] عائلة من التوزيع"
            },
            "medical_aid": {
                "what": "تقديم رعاية طبية للمصابين والمرضى",
                "intervention": "فرق طبية تقدم العلاج والأدوية الضرورية",
                "impact": "تلقى [عدد] شخص الرعاية الطبية"
            },
            "shelter": {
                "what": "توفير مأوى للنازحين",
                "intervention": "إقامة خيام وتوزيع بطانيات ومستلزمات",
                "impact": "استفادت [عدد] عائلة من خدمات الإيواء"
            },
            "water_sanitation": {
                "what": "توزيع مياه نظيفة ومستلزمات صحية",
                "intervention": "توفير مياه صالحة للشرب ومواد تعقيم",
                "impact": "استفاد [عدد] شخص من خدمات المياه والصرف"
            }
        }

        template = templates.get(intervention_type, {
            "what": "[وصف ما يحدث]",
            "intervention": "[وصف التدخل الإنساني]",
            "impact": "[الأثر المباشر]"
        })

        return {
            "what": template["what"],
            "where": location,
            "intervention": template["intervention"],
            "impact": template["impact"],
            "language": "ar"
        }


if __name__ == "__main__":
    engine = CaptionEngine()
    engine.show_template()
