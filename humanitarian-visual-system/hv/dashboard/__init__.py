#!/usr/bin/env python3
"""
Dashboard Module - Offline Streamlit Interface
وحدة لوحة التحكم - واجهة Streamlit تعمل بدون إنترنت

Provides a visual interface for:
- File import and review
- Ethical compliance checking
- Caption editing
- Archive management

يوفر واجهة مرئية لـ:
- استيراد ومراجعة الملفات
- فحص الامتثال الأخلاقي
- تحرير التعليقات
- إدارة الأرشيف
"""

from .app import run_dashboard

__all__ = ['run_dashboard']
