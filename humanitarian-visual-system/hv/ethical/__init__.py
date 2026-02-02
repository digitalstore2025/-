#!/usr/bin/env python3
"""
Ethical Module - Automated Ethical Compliance
وحدة الأخلاقيات - الامتثال الأخلاقي الآلي

Components:
    - FaceBlur: Automatic face detection and blurring
    - MetadataStripper: Remove sensitive metadata (GPS, device info)
    - EthicalGate: Decision gate for ethical compliance

المكونات:
    - طمس الوجوه: كشف وطمس الوجوه تلقائياً
    - إزالة البيانات: حذف البيانات الحساسة (GPS، معلومات الجهاز)
    - بوابة الأخلاق: بوابة قرار للامتثال الأخلاقي
"""

from .blur import FaceBlur
from .metadata import MetadataStripper
from .gate import EthicalGate, ApprovalStatus, FileState

__all__ = ['FaceBlur', 'MetadataStripper', 'EthicalGate', 'ApprovalStatus', 'FileState']
