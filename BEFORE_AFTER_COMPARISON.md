# Before & After Comparison

## Key Changes in pages/4_Resume_Analyzer.py

### 1. Imports & Logging Setup

#### BEFORE
```python
import os
import time
import base64
import textwrap
from pathlib import Path

import streamlit as st
import logging
import plotly.graph_objects as go

# No logging setup
```

#### AFTER
```python
import os
import time
import base64
import textwrap
from pathlib import Path
from io import BytesIO  # ← NEW: For BytesIO operations

import streamlit as st
import logging
import plotly.graph_objects as go

# ==========================================================
# LOGGING SETUP — detailed instrumentation for debugging
# ==========================================================
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
```

---

### 2. Session State Initialization

#### BEFORE
```python
# No initialization
# Session state keys would be created on-demand, unreliably
```

#### AFTER
```python
# ==========================================================
# SESSION STATE INITIALIZATION — persist upload across reruns
# ==========================================================
def init_resume_upload_session():
    """Initialize session state keys for upload pipeline."""
    if "resume_name" not in st.session_state:
        st.session_state["resume_name"] = None
        logger.debug("Initialized: resume_name = None")
    
    if "resume_bytes" not in st.session_state:
        st.session_state["resume_bytes"] = None
        logger.debug("Initialized: resume_bytes = None")
    
    if "resume_type" not in st.session_state:
        st.session_state["resume_type"] = None
        logger.debug("Initialized: resume_type = None")
    
    if "resume_upload_complete" not in st.session_state:
        st.session_state["resume_upload_complete"] = False
        logger.debug("Initialized: resume_upload_complete = False")
    
    if "resume_cloud_url" not in st.session_state:
        st.session_state["resume_cloud_url"] = None
        logger.debug("Initialized: resume_cloud_url = None")
    
    if "resume_cloud_public_id" not in st.session_state:
        st.session_state["resume_cloud_public_id"] = None
        logger.debug("Initialized: resume_cloud_public_id = None")
    
    if "resume_upload_error" not in st.session_state:
        st.session_state["resume_upload_error"] = None
        logger.debug("Initialized: resume_upload_error = None")
    
    if "rerun_count" not in st.session_state:
        st.session_state["rerun_count"] = 0
        logger.debug("Initialized: rerun_count = 0")
    else:
        st.session_state["rerun_count"] += 1
        logger.debug(f"Rerun count incremented: {st.session_state['rerun_count']}")

init_resume_upload_session()
```

---

### 3. File Upload Section

#### BEFORE
```python
with up_col:
    uploaded_file = st.file_uploader(
        "Drag & drop your resume here",
        type=["pdf"],
        help="PDF format · up to 200MB",
    )

    if uploaded_file is not None:
        size_kb = len(uploaded_file.getbuffer()) / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        st.markdown(
            f"""
            <div class="dp-glass" style="padding:1rem 1.2rem; margin-top:.8rem;">
              <div style="display:flex; align-items:center; gap:.9rem;">
                <div style="width:42px;height:42px;border-radius:10px;background:var(--dp-gradient);display:flex;align-items:center;justify-content:center;color:#001022;">
                  {SVG['doc']}
                </div>
                <div style="flex:1; min-width:0;">
                  <div style="font-weight:700; color:var(--dp-text); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{uploaded_file.name}</div>
                  <div style="color:var(--dp-muted); font-size:.82rem;">
                    {size_str} · PDF · uploaded {time.strftime('%H:%M')}
                  </div>
                </div>
                <span class="dp-chip match">{SVG['check']} Ready</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
```

#### AFTER
```python
with up_col:
    uploaded_file = st.file_uploader(
        "Drag & drop your resume here",
        type=["pdf"],
        help="PDF format · up to 200MB",
    )

    # ===== CRITICAL: Persist upload immediately to session_state =====
    if uploaded_file is not None:
        logger.info(f"[UPLOAD] File selected: {uploaded_file.name}")
        logger.info(f"[UPLOAD] File size: {len(uploaded_file.getbuffer())} bytes")
        logger.info(f"[UPLOAD] MIME type: {uploaded_file.type}")
        logger.info(f"[UPLOAD] Rerun count at upload: {st.session_state['rerun_count']}")
        
        # Convert to bytes immediately — this prevents stream consumption issues on mobile
        try:
            resume_bytes = uploaded_file.getvalue()
            logger.info(f"[UPLOAD] Successfully extracted {len(resume_bytes)} bytes from UploadedFile")
            
            # Store in session_state so it survives reruns
            st.session_state["resume_name"] = uploaded_file.name
            st.session_state["resume_bytes"] = resume_bytes
            st.session_state["resume_type"] = uploaded_file.type
            logger.info(f"[UPLOAD] Persisted to session_state: name={uploaded_file.name}, size={len(resume_bytes)} bytes")
        except Exception as e:
            logger.error(f"[UPLOAD] Failed to extract bytes from UploadedFile: {e}", exc_info=True)
            st.error(f"Failed to process uploaded file: {str(e)}")
            st.stop()
    
    # ===== Display persisted resume if it exists (survives reruns) =====
    if st.session_state["resume_bytes"] is not None:
        size_kb = len(st.session_state["resume_bytes"]) / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        
        # Show cloud upload status
        status_badge = "Ready"
        badge_class = "match"
        if st.session_state["resume_upload_error"]:
            status_badge = "Upload Failed"
            badge_class = "danger"
        elif st.session_state["resume_upload_complete"]:
            status_badge = "Uploaded"
            badge_class = "match"
        elif st.session_state["resume_cloud_url"]:
            status_badge = "Uploaded"
            badge_class = "match"
        
        st.markdown(
            f"""
            <div class="dp-glass" style="padding:1rem 1.2rem; margin-top:.8rem;">
              <div style="display:flex; align-items:center; gap:.9rem;">
                <div style="width:42px;height:42px;border-radius:10px;background:var(--dp-gradient);display:flex;align-items:center;justify-content:center;color:#001022;">
                  {SVG['doc']}
                </div>
                <div style="flex:1; min-width:0;">
                  <div style="font-weight:700; color:var(--dp-text); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{st.session_state["resume_name"]}</div>
                  <div style="color:var(--dp-muted); font-size:.82rem;">
                    {size_str} · PDF · uploaded {time.strftime('%H:%M')}
                  </div>
                </div>
                <span class="dp-chip {badge_class}">{SVG['check']} {status_badge}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Show error message if cloud upload failed
        if st.session_state["resume_upload_error"]:
            st.warning(f"Cloud upload failed: {st.session_state['resume_upload_error']}")
            st.info("The file is saved locally. Retry will attempt cloud upload again.")
```

**Key Differences:**
- ✅ Extract bytes immediately: `resume_bytes = uploaded_file.getvalue()`
- ✅ Persist to session_state immediately
- ✅ Display uses persisted data: `st.session_state["resume_bytes"]`
- ✅ Show upload status badges: "Ready", "Uploaded", "Upload Failed"
- ✅ Show error messages if upload fails
- ✅ Comprehensive logging at every step

---

### 4. Analyze Button Validation

#### BEFORE
```python
analyze_clicked = st.button("Analyze Resume", use_container_width=True, key="dp_analyze")
```

#### AFTER
```python
# ===== Validation before enabling button =====
def validate_resume_for_analysis():
    """
    Validate that resume is ready for analysis.
    Returns: (is_valid: bool, error_message: str or None)
    """
    logger.info("[VALIDATION] Starting resume validation...")
    
    if st.session_state["resume_bytes"] is None:
        logger.warning("[VALIDATION] resume_bytes is None")
        return False, "Please upload a resume first."
    
    if len(st.session_state["resume_bytes"]) == 0:
        logger.warning("[VALIDATION] resume_bytes is empty")
        return False, "Resume file is empty. Please upload a valid PDF."
    
    logger.info(f"[VALIDATION] resume_bytes exists: {len(st.session_state['resume_bytes'])} bytes")
    logger.info(f"[VALIDATION] resume_name: {st.session_state['resume_name']}")
    logger.info(f"[VALIDATION] Cloud upload completed: {st.session_state['resume_upload_complete']}")
    logger.info(f"[VALIDATION] Cloud URL set: {bool(st.session_state['resume_cloud_url'])}")
    logger.info(f"[VALIDATION] Upload error: {st.session_state['resume_upload_error']}")
    
    return True, None

is_valid, error_msg = validate_resume_for_analysis()

# Disable analyze button if resume not ready
analyze_disabled = not is_valid
analyze_clicked = st.button(
    "Analyze Resume",
    use_container_width=True,
    key="dp_analyze",
    disabled=analyze_disabled,
    help=error_msg if error_msg else "Analyze your resume for ATS compatibility and skill gaps"
)
```

**Key Differences:**
- ✅ Validate BEFORE button is rendered
- ✅ Button disabled if validation fails
- ✅ Tooltip shows error message
- ✅ Comprehensive logging of validation state

---

### 5. Cloud Upload with Retry Logic

#### BEFORE
```python
if analyze_clicked:
    if uploaded_file is None:
        st.error("Please upload a resume first.")
        st.stop()

    import tempfile

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Read uploaded file bytes once and reuse everywhere to avoid stream consumption issues on mobile
    try:
        pdf_bytes = uploaded_file.getbuffer().tobytes()
    except Exception:
        # fallback
        uploaded_file.seek(0)
        pdf_bytes = uploaded_file.read()

    logger.info(f"File selected: {uploaded_file.name}")
    logger.info(f"File size bytes: {len(pdf_bytes)}")

    # Create a temporary file for analysis (write bytes, flush and close)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        tmp.write(pdf_bytes)
        tmp.flush()
        tmp.close()
        save_path = Path(tmp.name)
        logger.info(f"Temporary file created: {save_path} ({save_path.stat().st_size} bytes)")
    except Exception as e:
        logger.exception("Failed to write temporary file")
        st.error("Internal error creating temporary file for analysis.")
        st.stop()

    # Upload to Cloudinary using raw bytes (upload_resume was updated to accept bytes)
    logger.info("Starting Cloudinary upload")
    try:
        resume_url, public_id = upload_resume(pdf_bytes, uploaded_file.name)
        logger.info(f"Cloudinary upload finished: {resume_url}")
    except Exception:
        logger.exception("Cloudinary upload failed")
        st.error("Failed to upload resume to cloud storage.")
        st.stop()

    saved_resume = save_resume(
        user_id=user_id,
        resume_name=uploaded_file.name,
        resume_url=resume_url,
        public_id=public_id,
    )
    # ... rest of analysis
```

#### AFTER
```python
def upload_resume_with_retry(pdf_bytes, filename, max_retries=3):
    """
    Upload resume to Cloudinary with retry logic.
    
    Args:
        pdf_bytes: The resume PDF as bytes
        filename: Original filename
        max_retries: Number of retry attempts
    
    Returns:
        (success: bool, url: str or None, public_id: str or None, error: str or None)
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[CLOUD_UPLOAD] Attempt {attempt}/{max_retries}")
            logger.info(f"[CLOUD_UPLOAD] Uploading {len(pdf_bytes)} bytes")
            
            resume_url, public_id = upload_resume(pdf_bytes, filename)
            
            logger.info(f"[CLOUD_UPLOAD] Upload succeeded on attempt {attempt}")
            logger.info(f"[CLOUD_UPLOAD] Cloud URL: {resume_url}")
            logger.info(f"[CLOUD_UPLOAD] Public ID: {public_id}")
            
            return True, resume_url, public_id, None
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[CLOUD_UPLOAD] Attempt {attempt} failed: {error_msg}", exc_info=True)
            
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                logger.info(f"[CLOUD_UPLOAD] Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"[CLOUD_UPLOAD] All {max_retries} attempts failed. Final error: {error_msg}")
                return False, None, None, error_msg
    
    return False, None, None, "Unknown error after all retries"


if analyze_clicked:
    logger.info(f"[ANALYZE] Analyze button clicked. Session state: resume_bytes={bool(st.session_state['resume_bytes'])}")
    
    # ===== REVALIDATE (defensive check) =====
    if st.session_state["resume_bytes"] is None or len(st.session_state["resume_bytes"]) == 0:
        logger.error("[ANALYZE] Resume validation failed at analyze time")
        st.error("Please upload a resume first.")
        st.stop()
    
    logger.info(f"[ANALYZE] Starting analysis workflow. Resume size: {len(st.session_state['resume_bytes'])} bytes")
    
    # ===== STAGE 1: Cloud upload (with retry) =====
    if not st.session_state["resume_upload_complete"] or st.session_state["resume_upload_error"]:
        logger.info("[ANALYZE] Cloud upload not completed yet. Starting upload...")
        
        with st.spinner("Uploading resume to cloud storage..."):
            upload_success, cloud_url, cloud_public_id, upload_error = upload_resume_with_retry(
                st.session_state["resume_bytes"],
                st.session_state["resume_name"],
                max_retries=3
            )
        
        if upload_success:
            st.session_state["resume_upload_complete"] = True
            st.session_state["resume_cloud_url"] = cloud_url
            st.session_state["resume_cloud_public_id"] = cloud_public_id
            st.session_state["resume_upload_error"] = None
            logger.info("[ANALYZE] Cloud upload completed successfully")
        else:
            st.session_state["resume_upload_error"] = upload_error
            st.session_state["resume_upload_complete"] = False
            logger.error(f"[ANALYZE] Cloud upload failed: {upload_error}")
            st.error(f"Failed to upload resume to cloud storage after 3 attempts.\n\nError: {upload_error}\n\nThe file is saved locally. You can retry.")
            st.stop()
    else:
        logger.info("[ANALYZE] Cloud upload already completed. URL: " + str(st.session_state["resume_cloud_url"])[:80])
    
    # ===== STAGE 2: Create temp file from session_state bytes (not original UploadedFile) =====
    import tempfile
    
    logger.info("[ANALYZE] Creating temporary file for analysis...")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        tmp.write(st.session_state["resume_bytes"])
        tmp.flush()
        tmp.close()
        save_path = Path(tmp.name)
        logger.info(f"[ANALYZE] Temporary file created: {save_path} ({save_path.stat().st_size} bytes)")
    except Exception as e:
        logger.exception("[ANALYZE] Failed to write temporary file")
        st.error("Internal error creating temporary file for analysis.")
        st.stop()
    
    # ===== STAGE 3: Save to database =====
    logger.info("[ANALYZE] Saving resume record to database...")
    saved_resume = save_resume(
        user_id=user_id,
        resume_name=st.session_state["resume_name"],
        resume_url=st.session_state["resume_cloud_url"],
        public_id=st.session_state["resume_cloud_public_id"],
    )
    logger.info(f"[ANALYZE] Resume saved with ID: {saved_resume.id}")

    # ... rest of analysis with logging at each stage
```

**Key Differences:**
- ✅ Retry function with exponential backoff
- ✅ Uses session_state bytes instead of original UploadedFile
- ✅ Defensive re-validation
- ✅ Graceful error handling (keep bytes, allow retry)
- ✅ Detailed logging at every stage

---

## Summary of Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Session persistence** | None | Full session_state tracking |
| **Bytes persistence** | Lost on rerun | Survives all reruns |
| **Upload validation** | After click | Before click (disabled button) |
| **Cloud upload retries** | None (1 attempt) | 3 attempts with backoff |
| **Logging** | Minimal | Comprehensive with prefixes |
| **Error handling** | Generic errors | Specific messages + retry |
| **Mobile compatibility** | Poor | Optimized for mobile |
| **User feedback** | Limited | Status badges + messages |
| **Code clarity** | Mixed concerns | Separated stages with comments |

---

## Testing the Changes

### Simple Test: Upload → Analyze (Desktop)
1. Open app
2. Upload resume
3. Click "Analyze Resume"
4. Verify analysis completes
5. Check logs for all [UPLOAD], [VALIDATION], [CLOUD_UPLOAD], [ANALYZE] messages

### Mobile Test: Upload → Rerun → Analyze
1. Open app on mobile device
2. Upload resume
3. **Verify:** File displays with badge
4. Click any other input to trigger rerun
5. **Verify:** File STILL displays (because session_state persisted)
6. Click "Analyze Resume"
7. Verify analysis completes
8. Check logs for all expected messages

### Retry Test: Simulate Cloud Upload Failure
1. Upload resume
2. Intercept Cloudinary request (DevTools, proxy, etc.)
3. Fail first 2 attempts
4. Unblock network
5. **Verify:** App retried with 2s, 4s delays
6. Verify 3rd attempt succeeded
7. Verify analysis continues automatically
