#!/usr/bin/env python3
"""
Humanitarian Visual System - Offline Dashboard
نظام التوثيق البصري الإنساني - لوحة التحكم

Streamlit-based offline dashboard for:
- Visual file review workflow
- Ethical compliance checking
- Caption management
- Activity monitoring

لوحة تحكم Streamlit تعمل بدون إنترنت لـ:
- سير عمل مراجعة الملفات المرئية
- فحص الامتثال الأخلاقي
- إدارة التعليقات
- مراقبة النشاط

Run with: hv dashboard
Or: streamlit run app.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("Streamlit not installed. Install with: pip install streamlit")

# Import HV modules
try:
    from hv.core.files import FileManager
    from hv.core.captions import CaptionEngine
    from hv.core.logger import ActivityLogger
    from hv.ethical.gate import EthicalGate, FileState, ApprovalStatus
    from hv.ethical.blur import FaceBlur
    from hv.ethical.metadata import MetadataStripper
except ImportError:
    from core.files import FileManager
    from core.captions import CaptionEngine
    from core.logger import ActivityLogger
    from ethical.gate import EthicalGate, FileState, ApprovalStatus
    from ethical.blur import FaceBlur
    from ethical.metadata import MetadataStripper


def run_dashboard():
    """Main dashboard entry point"""
    if not STREAMLIT_AVAILABLE:
        print("Error: Streamlit is required for the dashboard")
        print("Install with: pip install streamlit")
        return

    main()


def main():
    """Main Streamlit app"""

    # Page config
    st.set_page_config(
        page_title="HV System | نظام التوثيق البصري",
        page_icon="🟥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #CC0000;
        text-align: center;
        padding: 1rem;
        border-bottom: 3px solid #CC0000;
        margin-bottom: 2rem;
    }
    .status-approved {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
    .status-rejected {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #dc3545;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .rtl {
        direction: rtl;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="main-header">
        🟥 HUMANITARIAN VISUAL SYSTEM<br>
        <span style="font-size: 1rem; font-weight: normal;">
            نظام التوثيق البصري الإنساني | Gaza Edition
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'base_path' not in st.session_state:
        st.session_state.base_path = "./Gaza_Mission"
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings | الإعدادات")

        # Mission path
        base_path = st.text_input(
            "Mission Path | مسار البعثة",
            value=st.session_state.base_path
        )
        st.session_state.base_path = base_path

        # Initialize components
        file_manager = FileManager(base_path)
        ethical_gate = EthicalGate(os.path.join(base_path, ".hv_state.json"))
        face_blur = FaceBlur()
        metadata_stripper = MetadataStripper()
        caption_engine = CaptionEngine()
        activity_logger = ActivityLogger(os.path.join(base_path, "LOGS"))

        # Quick actions
        st.divider()
        st.subheader("🚀 Quick Actions | إجراءات سريعة")

        if st.button("📁 Initialize Mission | تهيئة البعثة", use_container_width=True):
            file_manager.initialize_structure()
            st.session_state.initialized = True
            st.success("✓ Mission initialized | تم تهيئة البعثة")

        # Statistics
        st.divider()
        st.subheader("📊 Statistics | الإحصائيات")

        try:
            stats = ethical_gate.get_statistics()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total | الإجمالي", stats.get("total", 0))
                st.metric("Approved | موافق", stats.get("approved", 0))
            with col2:
                st.metric("Pending | قيد الانتظار", stats.get("imported", 0) + stats.get("reviewing", 0))
                st.metric("Rejected | مرفوض", stats.get("rejected", 0))
        except Exception:
            st.info("No data yet | لا توجد بيانات بعد")

    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📥 Import | استيراد",
        "🔍 Review | مراجعة",
        "📝 Caption | تعليق",
        "📦 Archive | أرشيف",
        "📋 Logs | السجلات"
    ])

    # ============= TAB 1: IMPORT =============
    with tab1:
        st.header("📥 Import Media | استيراد الوسائط")

        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_files = st.file_uploader(
                "Upload files | رفع الملفات",
                accept_multiple_files=True,
                type=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'mp3', 'wav']
            )

            if uploaded_files:
                st.write(f"📁 Selected: {len(uploaded_files)} files")

                if st.button("⬆️ Import All | استيراد الكل", type="primary"):
                    import_dir = Path(base_path) / "IMPORTED"
                    import_dir.mkdir(parents=True, exist_ok=True)

                    imported = 0
                    for file in uploaded_files:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        new_name = f"HV_{timestamp}_{file.name}"
                        dest = import_dir / new_name

                        with open(dest, 'wb') as f:
                            f.write(file.getbuffer())

                        # Register in ethical gate
                        ethical_gate.register_file(str(dest))

                        # Strip metadata
                        metadata_stripper.strip(str(dest))

                        # Log
                        activity_logger.log("IMPORT", f"Imported: {file.name}", file_path=str(dest))
                        imported += 1

                    st.success(f"✓ Imported {imported} files | تم استيراد {imported} ملفات")
                    st.balloons()

        with col2:
            st.info("""
            **Workflow | سير العمل:**

            1. 📥 Import → استيراد
            2. 🔍 Review → مراجعة
            3. ✓/✗ Approve/Reject → موافقة/رفض
            4. 📝 Caption → تعليق
            5. 📦 Archive → أرشيف

            ⚠️ **Stages cannot be skipped**
            لا يمكن تجاوز المراحل
            """)

    # ============= TAB 2: REVIEW =============
    with tab2:
        st.header("🔍 Ethical Review | المراجعة الأخلاقية")

        # Get files for review
        review_folders = ["IMPORTED", "REVIEW"]
        files_for_review = []

        for folder in review_folders:
            folder_path = Path(base_path) / folder
            if folder_path.exists():
                for f in folder_path.glob("*"):
                    if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.mp4', '.mov']:
                        files_for_review.append(f)

        if not files_for_review:
            st.info("No files pending review | لا توجد ملفات للمراجعة")
        else:
            st.write(f"📁 Files pending: {len(files_for_review)}")

            selected_file = st.selectbox(
                "Select file | اختر ملف",
                files_for_review,
                format_func=lambda x: x.name
            )

            if selected_file:
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Display file
                    if selected_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        st.image(str(selected_file), caption=selected_file.name)
                    else:
                        st.video(str(selected_file))

                with col2:
                    st.subheader("🔍 Analysis | التحليل")

                    # Face detection
                    face_count = face_blur.detect_faces(str(selected_file))

                    if face_count > 0:
                        st.markdown(f"""
                        <div class="warning-box">
                            ⚠️ <strong>Faces detected: {face_count}</strong><br>
                            وجوه مكتشفة: {face_count}
                        </div>
                        """, unsafe_allow_html=True)

                        consent = st.checkbox("✓ Consent documented | موافقة موثقة")

                        if not consent:
                            if st.button("🔲 Blur Faces | طمس الوجوه", type="primary"):
                                blurred = face_blur.blur_faces(str(selected_file))
                                st.success(f"✓ Blurred {blurred} faces | تم طمس {blurred} وجه")
                                activity_logger.log("BLUR", f"Blurred faces", file_path=str(selected_file))
                                st.rerun()
                    else:
                        st.success("✓ No faces detected | لا توجد وجوه")

                    st.divider()

                    # Actions
                    st.subheader("Actions | الإجراءات")

                    col_a, col_b = st.columns(2)

                    with col_a:
                        if st.button("✓ Approve | موافقة", type="primary", use_container_width=True):
                            # Check if can approve
                            can_approve, blockers = ethical_gate.can_approve(str(selected_file))

                            if face_count > 0 and not st.session_state.get('consent_checked'):
                                st.error("Cannot approve: faces without consent")
                            else:
                                # Move to approved
                                approved_dir = Path(base_path) / "APPROVED"
                                approved_dir.mkdir(exist_ok=True)
                                dest = approved_dir / selected_file.name
                                selected_file.rename(dest)
                                ethical_gate.update_state(str(dest), FileState.APPROVED)
                                activity_logger.log("APPROVE", f"Approved", file_path=str(dest))
                                st.success("✓ File approved | تمت الموافقة")
                                st.rerun()

                    with col_b:
                        if st.button("✗ Reject | رفض", type="secondary", use_container_width=True):
                            reason = st.text_input("Reason | السبب")
                            rejected_dir = Path(base_path) / "REJECTED"
                            rejected_dir.mkdir(exist_ok=True)
                            dest = rejected_dir / selected_file.name
                            selected_file.rename(dest)
                            ethical_gate.update_state(str(dest), FileState.REJECTED, reason=reason)
                            activity_logger.log("REJECT", f"Rejected: {reason}", file_path=str(dest))
                            st.success("✗ File rejected | تم الرفض")
                            st.rerun()

    # ============= TAB 3: CAPTION =============
    with tab3:
        st.header("📝 Add Caption | إضافة تعليق")

        # Get approved files
        approved_dir = Path(base_path) / "APPROVED"
        approved_files = list(approved_dir.glob("*")) if approved_dir.exists() else []

        if not approved_files:
            st.info("No approved files | لا توجد ملفات موافق عليها")
        else:
            selected_file = st.selectbox(
                "Select file | اختر ملف",
                approved_files,
                format_func=lambda x: x.name,
                key="caption_file"
            )

            if selected_file:
                col1, col2 = st.columns([1, 1])

                with col1:
                    if selected_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        st.image(str(selected_file), caption=selected_file.name)

                with col2:
                    st.markdown("""
                    <div class="rtl">
                    <h4>قالب التعليق التوضيحي</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    what = st.text_area("What is happening? | ما الذي يحدث؟", key="what")
                    where = st.text_input("Where? (General only) | أين؟ (عام فقط)", key="where")
                    intervention = st.text_area("Humanitarian intervention | التدخل الإنساني", key="intervention")
                    impact = st.text_area("Impact | الأثر", key="impact")

                    # Validation warnings
                    caption_data = {
                        "what": what,
                        "where": where,
                        "intervention": intervention,
                        "impact": impact,
                        "language": "ar"
                    }

                    if any([what, where, intervention, impact]):
                        # Check for forbidden patterns
                        forbidden = ["إرهاب", "عدو", "terrorist", "enemy", "massacre"]
                        warnings = []
                        for field, value in caption_data.items():
                            if value:
                                for word in forbidden:
                                    if word.lower() in value.lower():
                                        warnings.append(f"Forbidden term in {field}: {word}")

                        if warnings:
                            st.markdown("""
                            <div class="error-box">
                            ⚠️ <strong>Validation Warnings:</strong>
                            </div>
                            """, unsafe_allow_html=True)
                            for w in warnings:
                                st.warning(w)

                    if st.button("💾 Save Caption | حفظ التعليق", type="primary"):
                        if caption_engine.validate(caption_data):
                            caption_dir = Path(base_path) / "CAPTIONS"
                            caption_dir.mkdir(exist_ok=True)
                            caption_path = caption_dir / f"{selected_file.stem}.json"

                            caption_data["created_at"] = datetime.now().isoformat()
                            caption_data["file"] = selected_file.name

                            with open(caption_path, 'w', encoding='utf-8') as f:
                                json.dump(caption_data, f, ensure_ascii=False, indent=2)

                            activity_logger.log("CAPTION", "Caption saved", file_path=str(selected_file))
                            st.success("✓ Caption saved | تم حفظ التعليق")
                        else:
                            st.error("Caption validation failed | فشل التحقق")

    # ============= TAB 4: ARCHIVE =============
    with tab4:
        st.header("📦 Archive | الأرشيف")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Approved Files | الملفات الموافق عليها")

            approved_dir = Path(base_path) / "APPROVED"
            if approved_dir.exists():
                approved_files = list(approved_dir.glob("*"))
                for f in approved_files:
                    st.write(f"📄 {f.name}")

                if approved_files and st.button("📦 Archive All | أرشفة الكل"):
                    archive_dir = Path(base_path) / "ARCHIVE"
                    archive_dir.mkdir(exist_ok=True)

                    for f in approved_files:
                        dest = archive_dir / f.name
                        f.rename(dest)
                        ethical_gate.update_state(str(dest), FileState.ARCHIVED)

                    activity_logger.log("ARCHIVE", f"Archived {len(approved_files)} files")
                    st.success(f"✓ Archived {len(approved_files)} files")
                    st.rerun()
            else:
                st.info("No approved files | لا توجد ملفات موافق عليها")

        with col2:
            st.subheader("Archived Files | الملفات المؤرشفة")

            archive_dir = Path(base_path) / "ARCHIVE"
            if archive_dir.exists():
                archived_files = list(archive_dir.glob("*"))
                st.write(f"Total: {len(archived_files)} files")
                for f in archived_files[:20]:  # Show first 20
                    st.write(f"📦 {f.name}")
            else:
                st.info("No archived files | لا توجد ملفات مؤرشفة")

    # ============= TAB 5: LOGS =============
    with tab5:
        st.header("📋 Activity Logs | سجلات النشاط")

        try:
            # Get recent logs
            logs = activity_logger.get_logs(limit=50)

            if not logs:
                st.info("No activity logs yet | لا توجد سجلات نشاط بعد")
            else:
                # Filter
                activity_filter = st.selectbox(
                    "Filter by type | تصفية حسب النوع",
                    ["ALL"] + activity_logger.ACTIVITY_TYPES
                )

                for log in logs:
                    if activity_filter != "ALL" and log.get("type") != activity_filter:
                        continue

                    activity_type = log.get("type", "UNKNOWN")
                    icon = {
                        "INIT": "🚀",
                        "IMPORT": "📥",
                        "REVIEW": "🔍",
                        "BLUR": "🔲",
                        "STRIP": "🔒",
                        "APPROVE": "✓",
                        "REJECT": "✗",
                        "CAPTION": "📝",
                        "ARCHIVE": "📦",
                        "EXPORT": "📤",
                        "ERROR": "❌",
                        "WARNING": "⚠️",
                    }.get(activity_type, "•")

                    timestamp = log.get("timestamp_human", log.get("timestamp", "")[:19])
                    message = log.get("message", "")

                    st.markdown(f"`{timestamp}` {icon} **[{activity_type}]** {message}")

                # Verify integrity
                st.divider()
                if st.button("🔐 Verify Log Integrity | التحقق من سلامة السجل"):
                    result = activity_logger.verify_integrity()
                    if result["valid"]:
                        st.success(f"✓ {result['message']}")
                    else:
                        st.error(f"✗ {result['message']}")

        except Exception as e:
            st.error(f"Error loading logs: {e}")

    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        🟥 Humanitarian Visual System v1.0.0 | نظام التوثيق البصري الإنساني<br>
        Ethical Documentation for Humanitarian Operations<br>
        التوثيق الأخلاقي للعمليات الإنسانية
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    if STREAMLIT_AVAILABLE:
        main()
    else:
        print("Please install streamlit: pip install streamlit")
