# Quick Debugging Guide: Mobile Upload Issues

## 1. Check Logs First

When a user reports upload issues, check the Streamlit terminal output for these log prefixes:

```
[UPLOAD]        → File selection and bytes extraction
[VALIDATION]    → Pre-analyze validation
[CLOUD_UPLOAD]  → Cloudinary upload attempts
[ANALYZE]       → Full analysis workflow
[CLEANUP]       → Temporary file cleanup
```

## 2. Common Issues & Solutions

### Issue: "Please upload a resume first"
```
Expected log:
  [UPLOAD] File selected: resume.pdf
  [UPLOAD] Successfully extracted 512000 bytes
  [UPLOAD] Persisted to session_state

If missing:
  ❌ File didn't upload successfully
  ❌ Check browser console for file input errors
  ❌ Verify PDF is valid (< 200MB)
```

### Issue: Upload succeeds but disappears after rerun
```
Expected log:
  [VALIDATION] resume_bytes exists: 512000 bytes

If shows:
  [VALIDATION] resume_bytes is None
  ❌ Session state not persisting
  ❌ Check if page is cleared between visits
  ❌ Expected on page refresh (session cleared is OK)
```

### Issue: "Failed to upload resume to cloud storage"
```
Expected logs (successful retry):
  [CLOUD_UPLOAD] Attempt 1/3
  [CLOUD_UPLOAD] ❌ Attempt 1 failed: Connection timeout
  [CLOUD_UPLOAD] Retrying in 2 seconds...
  [CLOUD_UPLOAD] Attempt 2/3
  [CLOUD_UPLOAD] ✅ Upload succeeded on attempt 2

If all fail:
  [CLOUD_UPLOAD] All 3 attempts failed. Final error: ...
  ❌ Check Cloudinary credentials
  ❌ Check network connection
  ❌ Check API key in st.secrets
```

### Issue: Analysis starts but fails midway
```
Expected log:
  [ANALYZE] Starting analysis workflow. Resume size: 512000 bytes
  [ANALYZE] Cloud upload already completed. URL: https://...
  [ANALYZE] Temporary file created: /tmp/tmpXXXXXX.pdf
  [ANALYZE] Starting full resume analysis
  [ANALYZE] ATS Score: 82.5, Coverage: 76.0
  [ANALYZE] ✅ Complete analysis pipeline finished successfully

If fails:
  [ANALYZE] Full resume analysis failed
  ❌ Check backend dependencies (full_resume_analysis, extract_resume_text, etc.)
  ❌ Check temp file permissions
```

## 3. Session State Inspection

Add this to the page to debug session state:

```python
# At the top of the page, after auth
import json

with st.expander("🐛 Debug: Session State", expanded=False):
    debug_state = {
        "resume_name": st.session_state.get("resume_name"),
        "resume_bytes_size": len(st.session_state.get("resume_bytes") or b""),
        "resume_type": st.session_state.get("resume_type"),
        "resume_upload_complete": st.session_state.get("resume_upload_complete"),
        "resume_cloud_url": st.session_state.get("resume_cloud_url"),
        "resume_upload_error": st.session_state.get("resume_upload_error"),
        "rerun_count": st.session_state.get("rerun_count"),
    }
    st.json(debug_state)
```

## 4. Mobile Testing Checklist

- [ ] Upload on Android Chrome
- [ ] Verify file displays with badge
- [ ] Navigate away → navigate back
- [ ] File still displays
- [ ] Click Analyze
- [ ] Check logs show: Attempt 1/3, ✅ Upload succeeded
- [ ] Analysis completes
- [ ] Test on Mobile Safari (same steps)
- [ ] Test with slow network (DevTools throttling)

## 5. Log Pattern Reference

### Successful Upload → Analysis → Results
```
[UPLOAD] File selected: resume.pdf
[UPLOAD] File size: 512000 bytes
[UPLOAD] MIME type: application/pdf
[UPLOAD] Rerun count at upload: 0
[UPLOAD] Successfully extracted 512000 bytes from UploadedFile
[UPLOAD] Persisted to session_state: name=resume.pdf, size=512000 bytes

[VALIDATION] Starting resume validation...
[VALIDATION] resume_bytes exists: 512000 bytes
[VALIDATION] resume_name: resume.pdf
[VALIDATION] Cloud upload completed: False
[VALIDATION] Cloud URL set: False
[VALIDATION] Upload error: None

[ANALYZE] Analyze button clicked. Session state: resume_bytes=True
[ANALYZE] Starting analysis workflow. Resume size: 512000 bytes
[ANALYZE] Cloud upload not completed yet. Starting upload...
[CLOUD_UPLOAD] Attempt 1/3
[CLOUD_UPLOAD] Uploading 512000 bytes
[CLOUD_UPLOAD] Upload succeeded on attempt 1
[CLOUD_UPLOAD] Cloud URL: https://res.cloudinary.com/...
[CLOUD_UPLOAD] Public ID: datapilot_ai/resumes/uuid
[ANALYZE] Cloud upload completed successfully

[ANALYZE] Creating temporary file for analysis...
[ANALYZE] Temporary file created: /tmp/tmpXXXXXX.pdf (512000 bytes)
[ANALYZE] Saving resume record to database...
[ANALYZE] Resume saved with ID: 42
[ANALYZE] Starting full resume analysis...
[ANALYZE] Full resume analysis completed successfully
[ANALYZE] ATS Score: 82.5, Coverage: 76.0
[ANALYZE] Analysis record saved to database
[ANALYZE] Extracting resume text and skills...
[ANALYZE] Extracted 45 skills
[ANALYZE] Predicting job fit...
[ANALYZE] Best role: Data Scientist (score: 0.92)
[ANALYZE] Missing skills for Data Scientist: 8
[ANALYZE] Job fit history saved
[ANALYZE] ✅ Complete analysis pipeline finished successfully

[CLEANUP] Temporary file deleted: /tmp/tmpXXXXXX.pdf
```

### Failed Upload → Retry → Success
```
[UPLOAD] File selected: resume.pdf
[UPLOAD] Successfully extracted 512000 bytes from UploadedFile
[UPLOAD] Persisted to session_state

[ANALYZE] Analyze button clicked. Session state: resume_bytes=True
[ANALYZE] Cloud upload not completed yet. Starting upload...
[CLOUD_UPLOAD] Attempt 1/3
[CLOUD_UPLOAD] Uploading 512000 bytes
[CLOUD_UPLOAD] ❌ Attempt 1 failed: HTTPError: 503 Service Unavailable
[CLOUD_UPLOAD] Retrying in 2 seconds...
[CLOUD_UPLOAD] Attempt 2/3
[CLOUD_UPLOAD] Uploading 512000 bytes
[CLOUD_UPLOAD] ❌ Attempt 2 failed: Timeout: Connection timed out
[CLOUD_UPLOAD] Retrying in 4 seconds...
[CLOUD_UPLOAD] Attempt 3/3
[CLOUD_UPLOAD] Uploading 512000 bytes
[CLOUD_UPLOAD] ✅ Upload succeeded on attempt 3
[CLOUD_UPLOAD] Cloud URL: https://res.cloudinary.com/...
[ANALYZE] Cloud upload completed successfully
[ANALYZE] Starting analysis workflow. Resume size: 512000 bytes
... (continue with analysis)
```

### Failed Upload → All Retries Exhausted
```
[CLOUD_UPLOAD] Attempt 1/3
[CLOUD_UPLOAD] ❌ Attempt 1 failed: Connection refused
[CLOUD_UPLOAD] Retrying in 2 seconds...
[CLOUD_UPLOAD] Attempt 2/3
[CLOUD_UPLOAD] ❌ Attempt 2 failed: Connection refused
[CLOUD_UPLOAD] Retrying in 4 seconds...
[CLOUD_UPLOAD] Attempt 3/3
[CLOUD_UPLOAD] ❌ Attempt 3 failed: Connection refused
[CLOUD_UPLOAD] ❌ All 3 attempts failed. Final error: Connection refused
[ANALYZE] ❌ Cloud upload failed: Connection refused
```

## 6. Network Issues to Check

- **Android Chrome**: May have stricter CORS policies
- **Mobile Safari**: File upload may timeout faster
- **Slow networks**: Need longer timeouts (addressed by retries)
- **Cloudinary limits**: Check API rate limits

## 7. Cloudinary-Specific Issues

### Credentials Missing
```
Error: 'CLOUD_NAME' not found in st.secrets
Fix: Add CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET to secrets.toml
```

### Invalid API Key
```
Error: Invalid credentials (401)
Fix: Verify API key in Cloudinary dashboard
```

### Folder Not Found
```
Error: Folder datapilot_ai/resumes does not exist
Fix: Create folder in Cloudinary dashboard, or disable folder requirement
```

## 8. Browser DevTools Tips

### Check Network Requests
1. Open DevTools (F12)
2. Network tab
3. Filter by "upload" or "cloudinary"
4. Check response status (200, 201, 5xx, timeout)

### Check Console Errors
1. Console tab
2. Filter errors
3. Look for JS errors (usually none with this fix)

### Check Application → Session Storage
1. Application tab
2. Session Storage
3. Check if Streamlit is storing session properly

## 9. Testing with Simulated Failures

### Simulate Slow Network
1. Chrome DevTools → Network tab
2. Set throttling to "Slow 3G" or "Offline"
3. Upload resume
4. Should see 2s, 4s, 8s retries in logs

### Simulate Connection Loss
1. Disconnect wifi/cellular
2. Upload resume
3. Should show "Upload Failed" badge
4. Reconnect, click "Analyze" again
5. Should retry and succeed

---

## When to Escalate

If logs show:
- ✅ All stages completing = issue is user-specific or intermittent
- ❌ Always failing at [CLOUD_UPLOAD] = check Cloudinary
- ❌ Always failing at [ANALYZE] = check backend dependencies
- ❌ Succeeds desktop, fails mobile = check mobile-specific browser settings
