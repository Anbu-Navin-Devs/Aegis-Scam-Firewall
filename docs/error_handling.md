# Aegis Backend — Error Handling Reference
## For the Flutter Frontend Team

> **Purpose:** This document maps every HTTP status code the Aegis backend can return to the correct Flutter UI behaviour. Treat this as the definitive error-handling contract between backend and frontend.

---

## Global Rules

1. **All errors are JSON** — every non-2xx response returns `{ "detail": "<message>" }`.
2. **Never show raw `detail` strings to end users** — map to friendly UI copy per the table below.
3. **The `is_scam` / `risk_level` field is only present on 2xx responses** — never assume it exists on error payloads.
4. **Network timeouts are not HTTP errors** — handle them separately in Dio/http client config (recommended timeout: 30 s for REST, 60 s for document uploads).

---

## Status Code Reference

### ✅ 200 OK — Success

All detection endpoints return `200` on success.

| Endpoint | Flutter Action |
|---|---|
| `POST /analyze/intent` | Parse `IntentResponse`, display scam verdict card |
| `POST /document/scan` | Parse `DocumentAnalysisResponse`, display risk level + clause list |
| `GET /history/logs` | Populate threat history `ListView` |

---

### ❌ 400 Bad Request — Client Validation Error

**Cause:** The request payload is malformed or violates a business rule.

| Trigger | `detail` message | Flutter UI Action |
|---|---|---|
| Empty transcript | `"Transcript cannot be empty"` | Show inline field error: *"Please enter some text to analyse."* |
| Empty file upload | `"Uploaded file is empty."` | Show snackbar: *"The selected file appears to be empty."* |
| Wrong MIME type | `"Unsupported file type 'image/gif'. Accepted formats: PDF, PNG, JPEG."` | Show dialog: *"Only PDF, PNG, or JPEG files are supported."* |
| Invalid JSON body | `"value is not a valid..."` (Pydantic) | Log error, show generic: *"Invalid request. Please try again."* |

**Flutter pattern:**
```dart
if (response.statusCode == 400) {
  final detail = jsonDecode(response.body)['detail'] as String;
  showErrorSnackbar(context, _mapDetailToUserMessage(detail));
}
```

---

### ❌ 413 Request Entity Too Large — File Size Exceeded

**Trigger:** Uploaded file exceeds the module's size limit.

| Module | Limit | `detail` message |
|---|---|---|
| Document scan | 20 MB | `"File size (X bytes) exceeds the 20 MB limit."` |
| Audio upload | 10 MB | `"File size (X bytes) exceeds the 10 MB limit."` |

**Flutter UI Action:**
- Before uploading, check `file.lengthSync()` client-side and show:
  *"This file is too large. Maximum size is 20 MB."*
- If the 413 slips through: snackbar with the same copy.

```dart
if (response.statusCode == 413) {
  showErrorSnackbar(context, 'File too large. Max 20 MB for documents, 10 MB for audio.');
}
```

---

### ❌ 422 Unprocessable Entity — Schema Validation Failure

**Cause:** FastAPI/Pydantic rejected the request body structure (missing required field, wrong type).

**Flutter UI Action:** This should never appear in production if the Flutter models are typed correctly. Treat as a developer error — log to Crashlytics/Sentry and show:
*"Something went wrong preparing your request. Please update the app."*

```dart
if (response.statusCode == 422) {
  FirebaseCrashlytics.instance.log('422 from ${request.url}: ${response.body}');
  showErrorDialog(context, 'App update required', 'Please update Aegis to the latest version.');
}
```

---

### ❌ 500 Internal Server Error — Backend / AI Failure

**Cause:** Gemini API timeout, unexpected exception in a service function, or database failure on a synchronous path.

| Common trigger | `detail` prefix |
|---|---|
| Gemini API timeout or quota exceeded | `"Intent analysis failed: ..."` |
| Gemini document vision error | `"Document analysis failed: ..."` |
| Audio analysis crash | `"Audio analysis failed: ..."` |

**Flutter UI Action:**
- Show a **dismissible error card** (not a blocking dialog) so the user can retry.
- Include a **Retry button** that re-submits the same request.
- After 3 consecutive 500s, show: *"Aegis servers are experiencing issues. Please try again later."*

```dart
if (response.statusCode == 500) {
  _retryCount++;
  if (_retryCount >= 3) {
    showPersistentBanner(context, 'Service temporarily unavailable. Retrying…');
  } else {
    showRetrySnackbar(context, 'Analysis failed. Tap to retry.');
  }
}
```

> **Note on threat logging:** Database persistence failures in BackgroundTasks are swallowed silently — they do **not** cause a 500 on the detection endpoints. The AI verdict is always returned regardless of DB state.

---

### ❌ 503 Service Unavailable — Startup / DB Not Ready

**Cause:** Uvicorn is starting up and the DB `init_db()` hasn't completed yet, or PostgreSQL is unreachable.

**Flutter UI Action:** Show a **loading screen** with *"Aegis is starting up…"* and poll `/health` every 3 seconds until it returns `200`.

```dart
Future<void> waitForBackend() async {
  while (true) {
    try {
      final res = await http.get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 5));
      if (res.statusCode == 200) return;
    } catch (_) {}
    await Future.delayed(const Duration(seconds: 3));
  }
}
```

---

## WebSocket Error Frames

The `/live-audio/stream` WebSocket sends structured JSON error frames (not HTTP codes) for protocol violations:

| `event` value | Trigger | Flutter Action |
|---|---|---|
| `"error"` + `detail: "Handshake timeout (10 s)."` | Client didn't send handshake within 10 s | Reconnect with exponential backoff |
| `"error"` + `detail: "sample_rate must be 1–48000 Hz."` | Invalid sample rate in handshake | Fix to `16000` and reconnect |
| `"error"` + `detail: "Frame too large..."` | Binary frame > 5 MB | Reduce chunk size to ≤ 1 s of audio |
| `"error"` + `detail: "PCM decode error: ..."` | Non-float32 bytes sent | Ensure audio is encoded as `float32` LE |
| `"session_end"` | Clean close after `"STOP"` sent | Normal — update UI to show session summary |

**Flutter WebSocket error handling:**
```dart
channel.stream.listen(
  (message) {
    final data = jsonDecode(message as String);
    if (data['event'] == 'error') {
      _handleWsError(data['detail']);
    } else if (data['event'] == 'session_end') {
      _onSessionComplete(data['windows_analysed']);
    } else {
      _onWindowResult(data); // { is_deepfake, confidence_score, ... }
    }
  },
  onError: (error) => _reconnectWithBackoff(),
  onDone: () => _onConnectionClosed(),
);
```

---

## Recommended Dio Interceptor (Flutter)

```dart
// aegis_api_client.dart
class AegisErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    switch (err.response?.statusCode) {
      case 400:
        throw AegisValidationException(err.response?.data['detail']);
      case 413:
        throw AegisFileTooLargeException();
      case 422:
        FirebaseCrashlytics.instance.log('422: ${err.response?.data}');
        throw AegisClientException('App update required');
      case 500:
        throw AegisServerException(err.response?.data['detail']);
      default:
        if (err.type == DioExceptionType.connectionTimeout) {
          throw AegisTimeoutException();
        }
        handler.next(err);
    }
  }
}
```

---

*Last updated: 2026-04-14 | Aegis Backend v1.0.0*
