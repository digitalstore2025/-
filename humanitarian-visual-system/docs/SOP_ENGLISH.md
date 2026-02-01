# Standard Operating Procedures (SOP)
## Humanitarian Visual Execution System - Gaza Edition

**Organization:** Turkish Red Crescent
**Version:** 1.0
**Date:** 2024

---

## Table of Contents

1. [Non-Negotiable Constraints](#1-non-negotiable-constraints)
2. [Camera Settings](#2-camera-settings)
3. [Shot Logic](#3-shot-logic)
4. [File Management](#4-file-management)
5. [Ethical Review](#5-ethical-review)
6. [Post-Production](#6-post-production)
7. [Caption Guidelines](#7-caption-guidelines)
8. [Safe Publishing](#8-safe-publishing)
9. [Legal Archival](#9-legal-archival)

---

## 1. Non-Negotiable Constraints

### ⛔ Absolute Restrictions

| # | Constraint | Action |
|---|------------|--------|
| 1 | No photography or publishing that endangers any beneficiary | Immediate reject |
| 2 | No visible faces during displacement, trauma, or children without clear consent | Reject or blur |
| 3 | No exposed bodies or graphic injuries | Immediate reject |
| 4 | No sensitive location identification (coordinates, landmarks, timings) | Strip metadata |
| 5 | No dramatic visual or audio effects | Reject |
| 6 | Any unethical material is automatically excluded | Auto-exclude |

---

## 2. Camera Settings

### Mandatory Settings

```
MODE: Manual + Auto ISO
ISO MAX: 6400
SHUTTER: ≥ 1/100
APERTURE: f/2.8 – f/4 (lens dependent)
WHITE BALANCE: Auto
PICTURE PROFILE: Neutral / Flat

AUDIO:
- Sample Rate: 48kHz
- Bit Depth: 24bit
- Format: WAV
```

### Scene-Specific Presets

| Scene | ISO | Shutter | Aperture |
|-------|-----|---------|----------|
| Outdoor Daylight | 100-400 | 1/250 | f/4 |
| Outdoor Overcast | 400-800 | 1/125 | f/2.8 |
| Indoor Available Light | 800-3200 | 1/100 | f/2.8 |
| Indoor Low Light | 3200-6400 | 1/60 | f/2.8 |

**Goal:** Speed – Stability – Minimal post-processing

---

## 3. Shot Logic

### Required Shot Sequence

```
For each scene:
  1. Capture Establishing Shot (Wide – Context)
     ↓
  2. Capture Action Shot (Aid in progress)
     ↓
  3. Capture Human Detail (Hands / movement / interaction)
     ↓
  Exit scene immediately if risk increases
```

### ❌ Forbidden Actions

- **No reenactment** - Never stage or recreate scenes
- **No emotional requests** - Never ask for emotional reactions
- **No directing** - Never direct beneficiaries
- **No unconsented faces** - Never capture identifiable faces without documented consent

---

## 4. File Management

### Directory Structure

```
/Gaza_Mission/
├── RAW/
│   ├── Day_01/
│   ├── Day_02/
│   └── ...
├── AUDIO/
├── SELECTS/
├── EDIT/
├── FINAL/
└── LOGS/
```

### Rules

1. **Daily Division:** Each day in separate folder
2. **Multiple Cards:** Use multiple memory cards to minimize loss
3. **Immediate Backup:** Physical/Cloud when available
4. **Unified Naming:** `TRC_Gaza_YYYYMMDD_TYPE_###`

### File Type Codes

| Code | Type |
|------|------|
| AID | Aid Distribution |
| MED | Medical Services |
| SHL | Shelter |
| WSH | WASH (Water, Sanitation, Hygiene) |
| PSS | Psychological Support |
| GEN | General |

---

## 5. Ethical Review

### Automated Gate Logic

```python
For each asset:
    If (face_visible AND consent_missing) → REJECT
    If (location_sensitive == True) → REJECT
    If (graphic_content == True) → REJECT
    Else → APPROVE
```

### Review Checklist

- [ ] No unconsented visible faces
- [ ] No identifiable children
- [ ] No GPS coordinates
- [ ] No sensitive landmarks
- [ ] No graphic content
- [ ] No dramatic effects

### Approval Status Codes

| Status | Symbol | Next Action |
|--------|--------|-------------|
| Approved | ✓ | Ready for post-production |
| Pending Review | ⏳ | Requires human review |
| Rejected | ✗ | Do not use |
| Needs Redaction | ⚠️ | Blur/redact then review |

---

## 6. Post-Production

### Allowed Actions

| Action | Notes |
|--------|-------|
| Cut | No manipulation |
| Color Correction | Correction only, NOT grading |
| Audio Cleanup | Noise reduction only |

### ⛔ Forbidden Actions

| Action | Reason |
|--------|--------|
| Slow motion for tragedy | Unacceptable dramatization |
| Cinematic LUTs | Distorts reality |
| Dramatic music | Emotional manipulation |
| Sound effects | Emotional manipulation |

### Export Specifications

```
VIDEO:
- Codec: H.264 / H.265
- Resolution: 1920x1080
- Duration: 30-45 seconds (unless report requires longer)

AUDIO:
- Codec: AAC
- Bitrate: 320 kbps
```

---

## 7. Caption Guidelines

### Caption Structure

```
1. What is happening?
2. Where? (general location only)
3. What humanitarian intervention?
4. What is the impact?
```

### Language Requirements

| ✓ Required | ✗ Forbidden |
|------------|-------------|
| Neutral | Exaggeration |
| Precise | Emotional manipulation |
| Objective | Accusatory language |
| Factual | Political labeling |

### Allowed General Locations

- Gaza
- Northern Gaza
- Southern Gaza
- Central Gaza
- Rafah
- Khan Yunis
- Deir al-Balah

### Approved Hashtags

```
#TurkishRedCrescent
#HumanitarianAid
#Gaza
#InsaniyardimKurulusu
```

---

## 8. Safe Publishing

### Protocol

```python
If (security_risk == HIGH):
    Delay publishing
Else:
    Publish via official channels only
```

### Publishing Rules

| ⛔ Forbidden | ✓ Allowed |
|--------------|-----------|
| Live/direct publishing from field | Publishing from HQ after review |
| Raw file sharing | Processed file sharing |
| Sensitive metadata | GPS-stripped files |
| Precise location tagging | General location only |

---

## 9. Legal Archival

### Required Metadata per Asset

```
- Date
- General Location
- Type of Intervention
- Photographer ID
- Ethical Approval Status
```

### Core Principle

> **Every asset = Potential future legal document**

### Chain of Custody

| Stage | Responsible | Date |
|-------|-------------|------|
| Capture | Field Photographer | - |
| Import | Media Technician | - |
| Ethical Review | Ethics Officer | - |
| Final Approval | Media Director | - |
| Archive | Archive Manager | - |

---

## Appendix: Daily Checklist

### Before Shooting

- [ ] Verify camera settings
- [ ] Ensure sufficient memory cards
- [ ] Charge batteries
- [ ] Review ethical constraints

### During Shooting

- [ ] Follow shot sequence
- [ ] Do not direct beneficiaries
- [ ] Exit immediately if risk increases

### After Shooting

- [ ] Transfer files to standard structure
- [ ] Create backup
- [ ] Log in operations register
- [ ] Conduct ethical review

---

**Turkish Red Crescent**
**For Humanitarian Use Only**
