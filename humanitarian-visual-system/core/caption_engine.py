#!/usr/bin/env python3
"""
Caption Engine - Humanitarian Caption Generator
محرك النصوص التوضيحية - مولد النصوص الإنسانية

Generates ethical, neutral captions for humanitarian media content
following strict guidelines.

ينتج نصوصًا توضيحية أخلاقية ومحايدة للمحتوى الإعلامي الإنساني
وفق إرشادات صارمة.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class CaptionLanguage(Enum):
    """لغة النص | Caption Language"""
    ARABIC = "ar"
    ENGLISH = "en"
    TURKISH = "tr"
    BILINGUAL_AR_EN = "ar_en"


class CaptionTone(Enum):
    """نبرة النص | Caption Tone"""
    NEUTRAL = "neutral"
    INFORMATIVE = "informative"
    DOCUMENTARY = "documentary"


@dataclass
class Caption:
    """النص التوضيحي | Caption"""
    text_ar: str
    text_en: str
    text_tr: Optional[str] = None
    hashtags: List[str] = None
    platform: str = "general"
    character_count: int = 0
    approved: bool = False

    def __post_init__(self):
        self.hashtags = self.hashtags or []
        self.character_count = len(self.text_ar) + len(self.text_en)


class CaptionEngine:
    """
    محرك النصوص التوضيحية
    Caption Engine

    CAPTION STRUCTURE:
    - ماذا يحدث؟ | What is happening?
    - أين؟ (بشكل عام فقط) | Where? (general only)
    - ما التدخل الإنساني؟ | What intervention?
    - ما الأثر؟ | What impact?

    LANGUAGE RULES:
    - محايدة | Neutral
    - دقيقة | Precise
    - بلا توصيف سياسي | No political labeling

    FORBIDDEN:
    - تهويل | Exaggeration
    - استعطاف | Emotional manipulation
    - لغة اتهامية | Accusatory language
    """

    # الكلمات المحظورة | Forbidden Words
    FORBIDDEN_WORDS_AR = [
        "مجزرة", "إبادة", "وحشي", "همجي", "إجرامي",
        "كارثي", "مروع", "صادم", "فظيع", "رهيب",
        "عدوان", "احتلال", "مقاومة", "جهاد", "شهيد"
    ]

    FORBIDDEN_WORDS_EN = [
        "massacre", "genocide", "brutal", "barbaric", "criminal",
        "catastrophic", "horrifying", "shocking", "terrible", "horrible",
        "aggression", "occupation", "resistance", "martyrdom"
    ]

    # العبارات الموصى بها | Recommended Phrases
    RECOMMENDED_AR = {
        "distribution": "توزيع مساعدات",
        "medical": "تقديم خدمات طبية",
        "shelter": "توفير مأوى",
        "water": "توفير مياه نظيفة",
        "food": "توزيع مواد غذائية",
        "support": "تقديم الدعم"
    }

    RECOMMENDED_EN = {
        "distribution": "aid distribution",
        "medical": "medical services provision",
        "shelter": "shelter provision",
        "water": "clean water provision",
        "food": "food supplies distribution",
        "support": "providing support"
    }

    # الهاشتاغات المعتمدة | Approved Hashtags
    APPROVED_HASHTAGS = [
        "#TurkishRedCrescent",
        "#الهلال_الأحمر_التركي",
        "#HumanitarianAid",
        "#Gaza",
        "#غزة",
        "#InsaniyardimKurulusu"
    ]

    def __init__(self, default_language: CaptionLanguage = CaptionLanguage.BILINGUAL_AR_EN):
        self.default_language = default_language
        self.organization_name_ar = "الهلال الأحمر التركي"
        self.organization_name_en = "Turkish Red Crescent"

    def validate_text(self, text: str, language: str = "ar") -> tuple[bool, List[str]]:
        """
        Validate caption text against forbidden words

        التحقق من النص مقابل الكلمات المحظورة

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        text_lower = text.lower()

        forbidden = self.FORBIDDEN_WORDS_AR if language == "ar" else self.FORBIDDEN_WORDS_EN

        for word in forbidden:
            if word in text_lower:
                violations.append(word)

        return len(violations) == 0, violations

    def generate_caption(
        self,
        what: str,
        where: str,
        intervention: str,
        impact: str,
        language: CaptionLanguage = None,
        include_hashtags: bool = True,
        platform: str = "general"
    ) -> Caption:
        """
        Generate ethical caption following the structure

        توليد نص توضيحي أخلاقي وفق الهيكل المحدد

        Args:
            what: ماذا يحدث - What is happening
            where: أين (عام) - Where (general)
            intervention: التدخل الإنساني - Humanitarian intervention
            impact: الأثر - Impact
            language: Target language
            include_hashtags: Include approved hashtags
            platform: Target platform

        Returns:
            Caption object
        """
        language = language or self.default_language

        # Construct Arabic caption
        caption_ar = self._build_arabic_caption(what, where, intervention, impact)

        # Construct English caption
        caption_en = self._build_english_caption(what, where, intervention, impact)

        # Validate both
        valid_ar, _ = self.validate_text(caption_ar, "ar")
        valid_en, _ = self.validate_text(caption_en, "en")

        hashtags = self.APPROVED_HASHTAGS[:4] if include_hashtags else []

        return Caption(
            text_ar=caption_ar,
            text_en=caption_en,
            hashtags=hashtags,
            platform=platform,
            approved=valid_ar and valid_en
        )

    def _build_arabic_caption(
        self,
        what: str,
        where: str,
        intervention: str,
        impact: str
    ) -> str:
        """Build Arabic caption"""
        parts = []

        if what:
            parts.append(what)

        if where:
            parts.append(f"في {where}")

        if intervention:
            parts.append(f"يقدم {self.organization_name_ar} {intervention}")

        if impact:
            parts.append(impact)

        return " | ".join(parts) if parts else ""

    def _build_english_caption(
        self,
        what: str,
        where: str,
        intervention: str,
        impact: str
    ) -> str:
        """Build English caption"""
        parts = []

        if what:
            parts.append(what)

        if where:
            parts.append(f"In {where}")

        if intervention:
            parts.append(f"{self.organization_name_en} provides {intervention}")

        if impact:
            parts.append(impact)

        return " | ".join(parts) if parts else ""

    def generate_report_caption(
        self,
        intervention_type: str,
        location: str,
        beneficiaries: int,
        date: datetime = None
    ) -> Caption:
        """
        Generate caption for official reports

        توليد نص للتقارير الرسمية
        """
        date = date or datetime.now()
        date_str = date.strftime("%Y/%m/%d")

        caption_ar = (
            f"{self.organization_name_ar} | {location}\n"
            f"التاريخ: {date_str}\n"
            f"نوع التدخل: {intervention_type}\n"
            f"عدد المستفيدين: {beneficiaries:,}"
        )

        caption_en = (
            f"{self.organization_name_en} | {location}\n"
            f"Date: {date_str}\n"
            f"Intervention: {intervention_type}\n"
            f"Beneficiaries: {beneficiaries:,}"
        )

        return Caption(
            text_ar=caption_ar,
            text_en=caption_en,
            platform="report",
            approved=True
        )

    def generate_social_caption(
        self,
        main_message: str,
        call_to_action: str = "",
        platform: str = "instagram"
    ) -> Caption:
        """
        Generate caption for social media

        توليد نص لوسائل التواصل الاجتماعي
        """
        # Platform-specific character limits
        limits = {
            "twitter": 280,
            "instagram": 2200,
            "facebook": 63206
        }

        limit = limits.get(platform, 500)

        # Build caption with hashtags
        hashtags_str = " ".join(self.APPROVED_HASHTAGS[:3])

        caption_ar = f"{main_message}"
        if call_to_action:
            caption_ar += f"\n\n{call_to_action}"
        caption_ar += f"\n\n{hashtags_str}"

        # Truncate if needed
        if len(caption_ar) > limit:
            caption_ar = caption_ar[:limit-3] + "..."

        caption_en = main_message  # Would need translation in production

        return Caption(
            text_ar=caption_ar,
            text_en=caption_en,
            hashtags=self.APPROVED_HASHTAGS[:3],
            platform=platform,
            approved=True
        )

    def generate_archive_description(
        self,
        asset_id: str,
        date: datetime,
        location: str,
        intervention: str,
        photographer_id: str
    ) -> str:
        """
        Generate standardized archive description

        توليد وصف قياسي للأرشيف
        """
        return (
            f"Asset ID: {asset_id}\n"
            f"Date: {date.strftime('%Y-%m-%d')}\n"
            f"Location: {location}\n"
            f"Intervention: {intervention}\n"
            f"Photographer: {photographer_id}\n"
            f"Organization: {self.organization_name_en}\n"
            f"---\n"
            f"معرّف المادة: {asset_id}\n"
            f"التاريخ: {date.strftime('%Y-%m-%d')}\n"
            f"الموقع: {location}\n"
            f"التدخل: {intervention}\n"
            f"المصور: {photographer_id}\n"
            f"المنظمة: {self.organization_name_ar}"
        )


# Pre-defined caption templates
CAPTION_TEMPLATES = {
    "food_distribution": {
        "ar": "توزيع مواد غذائية على العائلات المتضررة في {location}",
        "en": "Food supplies distribution to affected families in {location}"
    },
    "medical_aid": {
        "ar": "تقديم خدمات طبية للمحتاجين في {location}",
        "en": "Medical services provision to those in need in {location}"
    },
    "shelter": {
        "ar": "توفير مأوى مؤقت للنازحين في {location}",
        "en": "Temporary shelter provision for displaced persons in {location}"
    },
    "water_sanitation": {
        "ar": "توزيع مياه نظيفة ومستلزمات صحية في {location}",
        "en": "Clean water and sanitation supplies distribution in {location}"
    },
    "psychological_support": {
        "ar": "تقديم الدعم النفسي للأطفال والعائلات في {location}",
        "en": "Psychological support for children and families in {location}"
    }
}


def main():
    """CLI for caption generation"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Humanitarian Visual System - Caption Engine"
    )
    parser.add_argument(
        "--what",
        help="What is happening"
    )
    parser.add_argument(
        "--where",
        help="General location"
    )
    parser.add_argument(
        "--intervention",
        help="Humanitarian intervention type"
    )
    parser.add_argument(
        "--impact",
        help="Impact description"
    )
    parser.add_argument(
        "--template",
        choices=list(CAPTION_TEMPLATES.keys()),
        help="Use predefined template"
    )
    parser.add_argument(
        "--platform",
        default="general",
        help="Target platform"
    )

    args = parser.parse_args()

    engine = CaptionEngine()

    if args.template:
        template = CAPTION_TEMPLATES[args.template]
        location = args.where or "غزة"
        print("\n" + "="*50)
        print("النص العربي | Arabic Caption:")
        print(template["ar"].format(location=location))
        print("\nEnglish Caption:")
        print(template["en"].format(location=location))
    elif args.what:
        caption = engine.generate_caption(
            what=args.what,
            where=args.where or "",
            intervention=args.intervention or "",
            impact=args.impact or "",
            platform=args.platform
        )
        print("\n" + "="*50)
        print("النص العربي | Arabic Caption:")
        print(caption.text_ar)
        print("\nEnglish Caption:")
        print(caption.text_en)
        print(f"\nHashtags: {' '.join(caption.hashtags)}")
        print(f"Approved: {caption.approved}")


if __name__ == "__main__":
    main()
