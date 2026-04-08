# Card Scan & Live Detection - Requirements

## Overview

A feature that lets users point their device camera at a physical MTG card and have it identified in real time. Once identified, the card is matched to the database, and the user can add it to their collection or a deck.

This document covers the full end-to-end flow from camera input through card identification to database matching. It supersedes the narrow "upload a photo" scope described in issue #87 and establishes the broader vision.

---

## 1. User Experience

### 1.1 Entry Point
- The scan app is a **standalone application** (`frontend/packages/mtgsim-scan` or similar), not a modification to the existing viewer or flashcards apps.
- It communicates with the same backend API but has its own routing, build, and deployment.
- The scan app requests camera permission on first use.

### 1.2 Live Camera Feed
- The browser displays a live camera preview using the device's rear camera (preferred) or front camera.
- A rectangular guide overlay indicates where to position the card.
- The system detects when a card-shaped object enters the frame and highlights it.

### 1.3 Card Detection & Identification
- **Detection** (local, fast): Determine that a card-shaped rectangle is present and reasonably framed. This runs continuously on the video feed.
- **Identification** (remote, slower): Once a stable card is detected, send the cropped frame to the backend for identification. This should not fire on every frame — only when a new, stable card is detected.

### 1.4 Result Display
- When a card is identified and matched, overlay the card name, set, and price on the camera view.
- Tapping the result opens the full card detail view (existing `CardDetailPage`).
- Action buttons: "Add to Collection", "Add to Deck" (with deck picker).

### 1.5 No-Match Handling
- If extraction succeeds but no database match is found, show the extracted name with a "No match found" indicator.
- The user can manually search from this state.

### 1.6 Error States
- Camera permission denied: show instructions to enable.
- No camera available (desktop without webcam): fall back to file upload.
- Backend unavailable: show offline indicator, disable scan.

---

## 2. Architecture

### 2.1 Detection Tiers

The system has two distinct tiers, each with different performance characteristics:

| Tier | Where | Latency Target | Purpose |
|------|-------|----------------|---------|
| **Card Detection** | Browser (client-side) | <100ms/frame | Find card rectangle in video feed, determine stability |
| **Card Identification** | Server (API) | <3s round-trip | Extract card data from image, match to database |

### 2.2 Client-Side Card Detection

Runs in the browser on the video stream. Responsibilities:

1. **Frame capture** from `<video>` element via Canvas API or `ImageCapture` API.
2. **Card rectangle detection** — identify a card-shaped rectangle in the frame. Approaches (in order of preference):
   - **CSS/Canvas heuristics**: edge detection, contour finding for rectangular shapes with MTG aspect ratio (~63:88). Libraries: OpenCV.js (heavy, ~8MB) or lighter alternatives like tracking.js or custom canvas-based edge detection.
   - **MediaStream API + OffscreenCanvas**: for performance, run detection off the main thread in a Web Worker.
3. **Stability check** — only trigger identification when the detected rectangle is stable (same approximate position/size for N consecutive frames, not blurry).
4. **Crop & encode** — extract the card region, encode as JPEG, send to backend.

**Decision: Start with manual capture (Phase 1-2), upgrade to continuous detection later (Phase 3+).**
- **v1**: Manual capture — guide overlay with a shutter button. No CV dependency, ships fastest.
- **Future**: Continuous detection with real-time overlay and auto-capture (see Phase 3). The architecture should keep detection logic isolated so it can be swapped in without reworking the scan flow.

### 2.3 Server-Side Card Identification

The backend receives a cropped card image and returns identification results.

**Data flow:**
```
POST /api/cards/scan (image bytes)
  -> Extraction pipeline (OpenAI GPT-4o or mock)
     -> Card domain object (name, mana cost, types, etc.)
  -> Name matching against card database
     -> Exact match (name index) or fuzzy match (rapidfuzz, threshold 92)
  -> If matched: fetch full card detail from DB
  -> Optional: add to collection or deck
  -> Return ScanResponse
```

**Existing infrastructure used:**
- `ExtractionPipeline` classes in `src/mtgsim/extract/pipelines.py` — OpenAI vision + mock
- `_load_card_name_index()` and fuzzy matching from `src/mtgsim/deck_import.py`
- `CardService` / `CardsData` for card lookup, collection, deck operations

### 2.4 Component Diagram

```
Browser                                    Server
+-----------------------------------+      +---------------------------+
| Camera Feed (<video>)             |      | POST /api/cards/scan      |
|   |                               |      |   |                       |
|   v                               |      |   v                       |
| Frame Capture (Canvas/Worker)     |      | Validate image            |
|   |                               |      |   |                       |
|   v                               |      |   v                       |
| Card Detection (rectangle finder) |      | Extraction Pipeline       |
|   |                               |      | (OpenAI Vision / Mock)    |
|   v                               |      |   |                       |
| Stability Check                   | ---> |   v                       |
| (debounce, blur detection)        | JPEG | Name Matching             |
|   |                               |      | (exact + fuzzy)           |
|   v                               |      |   |                       |
| Result Overlay                    | <--- |   v                       |
| (name, set, price, actions)       | JSON | ScanResponse              |
+-----------------------------------+      +---------------------------+
```

---

## 3. API Specification

### 3.1 `POST /api/cards/scan`

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | file | yes | JPEG or PNG, max 20MB |
| `pipeline` | query string | no | `"openai"` (default) or `"mock"` |
| `add_to_collection` | query bool | no | If true, add 1 copy to collection |
| `deck_id` | query int | no | If provided, add 1 copy to this deck |

**Response: `ScanResponse`**

```json
{
  "extracted_name": "Child of Night",
  "matched": true,
  "match_type": "exact",
  "match_confidence": 100.0,
  "card": { /* CardSummary or CardDetail — reuse existing model */ },
  "extraction": {
    "name": "Child of Night",
    "mana_cost": {"black": 1, "generic": 1},
    "card_types": ["Creature"],
    "subtypes": ["Vampire"],
    "oracle_text": "Lifelink",
    "rarity": "common",
    "power": 2,
    "toughness": 1
  },
  "added_to_collection": false,
  "added_to_deck": null
}
```

**Status codes:**
- `200` — Scan succeeded (even if no DB match; `matched: false`, `card: null`)
- `400` — Bad image (wrong type, empty, too large)
- `502` — Extraction service unavailable

### 3.2 Pipeline Modifications

`ExtractionPipeline` base class and implementations need `extract_bytes(data: bytes, mime_type: str) -> Card` in addition to the existing `extract(image_path: Path) -> Card`. The OpenAI implementation already base64-encodes; this just skips the file read.

### 3.3 Name Matching Extraction

The fuzzy matching logic in `deck_import.py` should be extracted into a standalone `match_card_by_name(name, name_index, name_list) -> MatchResult` function. `resolve_cards()` is then refactored to call it internally. This avoids duplicating matching logic.

---

## 4. Scan App (Standalone)

The scan feature is built as a standalone app within the existing frontend monorepo (`frontend/packages/`), following the same pattern as `@mtgsim/viewer` and `@mtgsim/flashcards`. It shares the `@mtgsim/ui` component library and API client but has its own entry point, routes, and build.

### 4.1 Package Structure

```
frontend/packages/mtgsim-scan/
├── src/
│   ├── main.tsx           # App entry point
│   ├── App.tsx            # Router + layout
│   ├── pages/
│   │   └── ScanPage.tsx   # Main scan view
│   ├── components/
│   │   ├── CameraView.tsx       # Camera stream management
│   │   ├── ScanOverlay.tsx      # Guide rectangle + result display
│   │   ├── ScanResultCard.tsx   # Matched card info + action buttons
│   │   └── FileUpload.tsx       # Drag-and-drop fallback
│   └── hooks/
│       ├── useCamera.ts         # Camera stream lifecycle
│       └── useScan.ts           # Scan state machine + API calls
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### 4.2 Dev Server & Build

| App | Port | Justfile command |
|-----|------|-----------------|
| Viewer | 5173 | `just dev-viewer` |
| Flashcards | 5174 | `just dev-flashcards` |
| **Scan** | **5175** | **`just dev-scan`** |

The scan app runs on port **5175** with its own Vite config. The `/api` proxy points to the backend on :8001, same as the other apps. The root `justfile` gets a `dev-scan` recipe and corresponding `build-scan` recipe.

### 4.3 Shared Dependencies
- `@mtgsim/ui` — card display components, API client, hooks, Tailwind config
- New scan-specific components live in the scan package, not in the shared library (until proven reusable)

### 4.3 Camera Management

- Use `navigator.mediaDevices.getUserMedia()` with `{ video: { facingMode: "environment" } }`.
- Handle permission states: prompt, granted, denied.
- Handle device enumeration for camera switching (front/back).
- Clean up stream on unmount.

### 4.3 Scan State Machine

**v1 (manual capture):**
```
READY -> CAPTURING -> IDENTIFYING -> RESULT
  ^                                    |
  |____________________________________|
            (dismiss or new scan)
```

| State | Description |
|-------|-------------|
| `READY` | Camera active (or file upload ready), waiting for user action |
| `CAPTURING` | User tapped shutter / selected file, encoding image |
| `IDENTIFYING` | Image sent to backend, awaiting response |
| `RESULT` | Card identified, showing result with actions |

**Future (continuous detection, Phase 3):**
```
IDLE -> DETECTING -> STABLE -> IDENTIFYING -> RESULT
  ^                                             |
  |_____________________________________________|
              (new card or timeout)
```

The v1 state machine is a subset of the future one — `READY` maps to `IDLE`, and the `DETECTING -> STABLE` states are added when auto-detection lands.

### 4.4 File Upload Fallback

For devices without cameras or when camera permission is denied:
- Standard file input accepting JPEG/PNG.
- Drag-and-drop zone.
- Same backend endpoint, same result display (minus the live overlay).

---

## 5. Performance Considerations

### 5.1 Client-Side
- Card detection must not block the main thread. Use `requestAnimationFrame` for capture timing and consider Web Workers or `OffscreenCanvas` for processing.
- Don't send every frame to the server. Debounce: only send when a new stable card is detected and at least 2 seconds have passed since the last request.
- JPEG compression quality ~80% for uploads to balance size and recognition accuracy.

### 5.2 Server-Side
- OpenAI Vision API calls are the bottleneck (~1-3s). No way around this for the OpenAI pipeline.
- The name index (`_load_card_name_index`) should be cached at service startup, not rebuilt per request.
- File size validation before reading the full upload into memory.

### 5.3 Future: Local Identification
- A local model (e.g., a card name classifier trained on Scryfall images) could replace or supplement OpenAI for faster identification. Out of scope for v1 but the architecture should not preclude it — the pipeline abstraction already supports swappable backends.

---

## 6. Testing Strategy

### 6.1 Backend
- **Mock pipeline tests**: Scan endpoint with mock pipeline, verify response shape, match types, collection/deck adds. No external API calls.
- **Matching tests**: Unit tests for `match_card_by_name()` with exact, fuzzy, and no-match cases.
- **Validation tests**: Reject bad file types, empty files, oversized files.

### 6.2 Frontend
- **Camera mock**: Tests stub `getUserMedia` to provide a synthetic video stream.
- **State machine**: Unit test transitions: IDLE -> DETECTING -> STABLE -> IDENTIFYING -> RESULT -> IDLE.
- **Fallback**: Verify file upload works when camera is unavailable.

### 6.3 Integration
- Manual testing with real scanned card images against the live server.
- Test with varying image quality, angles, lighting conditions.

---

## 7. Scope & Phasing

### Phase 1: API Endpoint (Issue #87)
- `POST /api/cards/scan` with OpenAI + mock pipelines
- `extract_bytes()` on pipeline classes
- `match_card_by_name()` extracted from deck_import
- `ScanService` + `ScanResponse` model
- Server-side image preprocessing (rotation, contrast, crop via Pillow)
- Rate limiting with documented defaults
- Configurable fuzzy match threshold (default 92)
- Tests with mock pipeline
- **No frontend changes**

### Phase 2: Manual Capture UI (Standalone App)
- New package `@mtgsim/scan` in `frontend/packages/mtgsim-scan/`
- Own entry point, routes, and Vite build; shares `@mtgsim/ui` library
- `ScanPage` with camera preview + shutter button
- File upload fallback (drag-and-drop / file picker) for no-camera devices
- v1 state machine: READY -> CAPTURING -> IDENTIFYING -> RESULT
- Result display reusing shared card components from `@mtgsim/ui`
- Action buttons: "Add to Collection", "Add to Deck"
- Guide overlay for card positioning

### Phase 3: Continuous Detection (Issue #92)
- Client-side card rectangle detection (OpenCV.js or lighter alternative)
- Auto-capture on stable detection
- Real-time detection overlay on camera feed
- Full state machine: IDLE -> DETECTING -> STABLE -> IDENTIFYING -> RESULT
- Web Worker / OffscreenCanvas for off-main-thread processing

### Phase 4: Polish & Performance
- Camera switching (front/back)
- Scan history (recent scans in session)
- Batch mode (scan multiple cards in sequence)
- Name index caching
- Local identification pipeline (stretch)

---

## 8. Decisions (formerly Open Questions)

1. **Client-side detection approach** — **Option A (manual capture) for v1.** Continuous detection with real-time overlay is the long-term goal but will be a separate feature (tracked in its own issue). Architecture should keep detection logic isolated to support the upgrade.

2. **Pipeline default** — **`"openai"` in production.** Mock pipeline is always available for development and testing. Both must be first-class and well-documented.

3. **Rate limiting** — **Yes.** The scan endpoint must be rate-limited. Defaults should be sensible and documented (e.g., N scans per minute per user/IP). OpenAI calls cost ~$0.01-0.03 per image; unrestricted scanning is a cost risk.

4. **Image preprocessing** — **Yes.** The server should preprocess images before sending to the extraction pipeline (rotation correction, contrast/brightness normalization, cropping). This improves accuracy and makes the system less dependent on any single extraction backend — important since OpenAI will eventually be swapped for other pipelines. Pillow is the likely dependency.

5. **Confidence threshold** — **Keep 92 as the default but make it configurable.** Document the threshold clearly. Vision-extracted names may have different error patterns than typed names; the threshold should be easy to tune as we gather real-world data. Expose it as a service-level config, not a per-request parameter.

---

## 9. Out of Scope

- Batch scanning (multiple cards per photo)
- Card condition detection from image quality
- Set/edition identification from expansion symbol
- Price comparison across printings during scan
- Offline/local-only identification
- Card sleeves or altered art handling
