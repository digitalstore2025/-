#!/usr/bin/env python3
"""
Humanitarian Visual System (HV)
نظام التوثيق البصري الإنساني

Gaza Edition - Full Stack System
إصدار غزة - النظام المتكامل

Components:
    - CLI: Command-line interface for field operations
    - Ethical: Automated ethical compliance (blur, metadata, gate)
    - Dashboard: Offline Streamlit interface
    - Core: File management, captions, logging

المكونات:
    - CLI: واجهة سطر الأوامر للعمليات الميدانية
    - الأخلاقيات: الامتثال الأخلاقي الآلي (طمس، بيانات، بوابة)
    - لوحة التحكم: واجهة Streamlit تعمل بدون إنترنت
    - النواة: إدارة الملفات، التعليقات، السجلات
"""

__version__ = "1.0.0"
__author__ = "Humanitarian Visual System Team"
__license__ = "Humanitarian Use License"

from .core.files import FileManager
from .core.captions import CaptionEngine
from .core.logger import ActivityLogger
from .ethical.gate import EthicalGate, ApprovalStatus
from .ethical.blur import FaceBlur
from .ethical.metadata import MetadataStripper
