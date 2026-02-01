# Humanitarian Visual Execution System - Gaza Edition

**المنظمة:** الهلال الأحمر التركي
**الغرض:** عمل إنساني بحت - بلا أي محتوى سياسي أو عسكري

---

## نظرة عامة | Overview

نظام تنفيذ إعلامي تقني يعمل في بيئة حرب نشطة، مهمته إدارة التصوير، التوثيق، المعالجة، والأرشفة الإعلامية الإنسانية وفق أعلى المعايير الأخلاقية، القانونية، والتقنية.

A technical media execution system operating in an active conflict environment, managing photography, documentation, processing, and humanitarian media archiving according to the highest ethical, legal, and technical standards.

---

## القيود المطلقة | Non-Negotiable Constraints

| # | القيد | Constraint |
|---|-------|------------|
| 1 | لا تصوير أو نشر يعرّض أي مستفيد للخطر | No photography or publishing that endangers any beneficiary |
| 2 | لا إظهار وجوه في حالات النزوح، الصدمة، أو الأطفال دون موافقة | No faces shown during displacement, trauma, or children without consent |
| 3 | لا تصوير جثامين مكشوفة أو إصابات مروّعة | No exposed bodies or graphic injuries |
| 4 | لا تحديد مواقع حساسة | No sensitive location identification |
| 5 | لا مؤثرات بصرية أو صوتية درامية | No dramatic visual or audio effects |
| 6 | أي مادة تخالف الأخلاقيات تُستبعد تلقائيًا | Any unethical material is automatically excluded |

---

## الهيكل | Structure

```
humanitarian-visual-system/
├── core/                 # Python core modules
│   ├── ethical_gate.py   # Ethical review system
│   ├── file_manager.py   # File organization
│   ├── metadata.py       # Metadata handling
│   ├── caption_engine.py # Caption generation
│   └── archive.py        # Legal archival
├── config/               # Configuration files
│   ├── camera_presets.yaml
│   ├── ethical_rules.yaml
│   └── export_settings.yaml
├── templates/            # Output templates
├── docs/                 # SOP documentation
├── web/                  # Web interface
├── cli/                  # Command line tools
└── tests/                # Unit tests
```

---

## التثبيت | Installation

```bash
cd humanitarian-visual-system
pip install -r requirements.txt
```

---

## الاستخدام | Usage

### CLI للمصور الميداني | Field Photographer CLI
```bash
python cli/field_capture.py --mode daily --day 01
```

### المراجعة الأخلاقية | Ethical Review
```bash
python core/ethical_gate.py --input /path/to/media
```

### الواجهة الويب | Web Interface
```bash
python web/app.py
```

---

## الترخيص | License

للاستخدام الإنساني فقط - الهلال الأحمر التركي
For humanitarian use only - Turkish Red Crescent

---

## التواصل | Contact

فريق الإعلام - الهلال الأحمر التركي
Media Team - Turkish Red Crescent
