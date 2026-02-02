#!/usr/bin/env python3
"""
Core Module - File Management, Captions, and Logging
وحدة النواة - إدارة الملفات، التعليقات، والسجلات

Components:
    - FileManager: File organization and management
    - CaptionEngine: Ethical caption generation and validation
    - ActivityLogger: Immutable activity logging

المكونات:
    - إدارة الملفات: تنظيم وإدارة الملفات
    - محرك التعليقات: توليد والتحقق من التعليقات الأخلاقية
    - مسجل النشاط: تسجيل النشاط غير قابل للحذف
"""

from .files import FileManager
from .captions import CaptionEngine
from .logger import ActivityLogger

__all__ = ['FileManager', 'CaptionEngine', 'ActivityLogger']
