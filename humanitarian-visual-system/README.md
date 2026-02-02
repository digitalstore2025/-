# 🟥 Humanitarian Visual System - Gaza Edition

**نظام التوثيق البصري الإنساني | Full Stack: CLI + Ethics + Dashboard**

---

## 📦 Quick Install | التثبيت السريع

```bash
pip install humanitarian-visual
```

أو التثبيت من المصدر:
```bash
cd humanitarian-visual-system
pip install -e .
```

---

## 🚀 Quick Start | البدء السريع

```bash
# Initialize mission | تهيئة البعثة
hv init

# Import file | استيراد ملف
hv import IMG_001.CR2

# Review file | مراجعة الملف
hv review IMG_001.CR2

# Approve file | الموافقة
hv approve IMG_001.CR2

# Launch dashboard | تشغيل الواجهة
hv dashboard
```

**⚠️ لا يمكن تجاوز المراحل — النظام يمنع ذلك برمجيًا**

---

## 🏗️ Architecture | البنية

```
humanitarian-visual-system/
├── hv/                      # Main package
│   ├── cli.py               # Command-line interface
│   ├── ethical/             # Ethical automation
│   │   ├── gate.py          # Decision gate | بوابة القرار
│   │   ├── blur.py          # Face blur | طمس الوجوه
│   │   └── metadata.py      # Metadata strip | إزالة البيانات
│   ├── dashboard/           # Offline GUI
│   │   └── app.py           # Streamlit interface
│   ├── core/                # Core modules
│   │   ├── files.py         # File management
│   │   ├── captions.py      # Caption engine
│   │   └── logger.py        # Activity logging
│   └── config.yaml          # Configuration
├── setup.py                 # pip installation
├── requirements.txt         # Dependencies
└── README.md
```

---

## ① CLI Commands | أوامر سطر الأوامر

| Command | Description | الوصف |
|---------|-------------|-------|
| `hv init` | Initialize mission structure | تهيئة هيكل البعثة |
| `hv import <file>` | Import media file | استيراد ملف |
| `hv review <file>` | Ethical review | مراجعة أخلاقية |
| `hv blur <file>` | Auto-blur faces | طمس الوجوه |
| `hv approve <file>` | Approve for use | الموافقة |
| `hv reject <file>` | Reject file | رفض الملف |
| `hv caption <file>` | Add caption | إضافة تعليق |
| `hv archive [file]` | Archive approved files | أرشفة الملفات |
| `hv status` | Show system status | عرض الحالة |
| `hv dashboard` | Launch GUI | تشغيل الواجهة |

---

## ② Ethical Automation | الذكاء الأخلاقي التلقائي

### A. Auto Face Blur | طمس الوجوه تلقائياً

```python
from hv.ethical.blur import blur_faces
blur_faces("photo.jpg")
```

يُفعّل تلقائياً إذا: وجه ظاهر + لا توجد موافقة

### B. Metadata Strip | إزالة البيانات الحساسة

```python
from hv.ethical.metadata import strip_metadata
strip_metadata("photo.jpg")
```

يحذف:
- GPS Coordinates | إحداثيات
- Exact Timestamp | التوقيت الدقيق
- Device ID | معرّف الجهاز

### C. Ethical Gate | بوابة القرار الأخلاقي

```python
if face_detected and not consent:
    blur_faces(file)
if sensitive_metadata:
    strip_metadata(file)
if graphic_content:
    reject(file)
```

**الأخلاق هنا قرار آلي لا يُناقش**

---

## ③ Dashboard | لوحة التحكم

```bash
hv dashboard
# Opens: http://localhost:8501
```

**يعمل بدون إنترنت | Offline-First**

### Features | المميزات:
- 📥 Visual file import
- 🔍 Auto ethical check
- 🔲 One-click face blur
- 📝 Caption templates
- 📊 Activity monitoring
- 🔐 Audit log

---

## 🔒 Non-Negotiable Rules | القواعد غير القابلة للتفاوض

| # | القيد | Constraint |
|---|-------|------------|
| 1 | ❌ لا تصوير يعرّض المستفيد للخطر | No endangering beneficiaries |
| 2 | ❌ لا وجوه بدون موافقة | No faces without consent |
| 3 | ❌ لا جثامين أو إصابات صادمة | No graphic content |
| 4 | ❌ لا تحديد مواقع حساسة | No sensitive locations |
| 5 | ❌ لا مؤثرات درامية | No dramatic effects |
| 6 | ❌ استبعاد تلقائي للمخالف | Auto-exclude unethical |

---

## 📝 Caption Template | قالب التعليق

```
ما الذي يحدث؟     What is happening?
أين؟ (عام فقط)    Where? (general only)
التدخل الإنساني:  Humanitarian intervention:
الأثر:            Impact:
```

**ممنوع | Forbidden:**
- ❌ توصيف سياسي | Political characterization
- ❌ استعطاف | Emotional manipulation
- ❌ مبالغة لغوية | Exaggeration

---

## 📊 Workflow | سير العمل

```
📥 Import
    ↓
🔍 Ethical Check (Auto)
    ↓
🔲 Blur/Strip (If needed)
    ↓
✓/✗ Approve/Reject
    ↓
📝 Caption
    ↓
📦 Archive
```

---

## 🔐 Security | الحماية

- ✓ لا مشاركة خارج النظام | No external sharing
- ✓ لا تصدير بدون موافقة أخلاقية | No export without approval
- ✓ سجل نشاط غير قابل للحذف | Immutable activity log
- ✓ Hash-chained audit trail | سلسلة تدقيق مشفرة

---

## 🧠 What This System Is

✅ نظام مساءلة أخلاقية مبرمج | Programmed ethical accountability
✅ درع قانوني للمؤسسة | Legal shield for the organization
✅ مساعد صامت للمصوّر في بيئة حرب | Silent assistant for photographers in conflict

**This is NOT just a tool or editing software.**

---

## 📋 Requirements | المتطلبات

```bash
pip install pillow opencv-python streamlit piexif pyyaml
```

---

## 📄 License | الترخيص

للاستخدام الإنساني فقط | For humanitarian use only

---

## 📞 Contact | التواصل

فريق الإعلام - الهلال الأحمر التركي
Media Team - Turkish Red Crescent
