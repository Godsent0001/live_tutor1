# Live Tutor - Flutter App

AI-powered interactive tutoring app for the Live Tutor backend.

## Setup

### 1. Install dependencies
```bash
flutter pub get
```

### 2. Configure the backend URL

Open `lib/config/api_config.dart` and set your backend URL:

```dart
// Local emulator (Android)
static const String baseUrl = 'http://10.0.2.2:8000';

// Local emulator (iOS)
static const String baseUrl = 'http://localhost:8000';

// Physical device — use your machine's local IP
static const String baseUrl = 'http://192.168.x.x:8000';
```

### 3. Run the backend
```bash
cd live_tutor-main
uvicorn app.main:app --reload
```

### 4. Run the app
```bash
flutter run
```

---

## Project structure

```
lib/
├── main.dart                        # App entry point
├── config/
│   ├── api_config.dart              # Base URL + all endpoints
│   ├── app_theme.dart               # Dark theme tokens
│   └── router.dart                  # go_router with auth guard
├── models/
│   ├── user.dart
│   ├── lesson.dart
│   ├── session.dart
│   ├── step.dart                    # LessonStep, Board, Question, CurrentStepData
│   └── teacher_response.dart
├── services/
│   ├── api_service.dart             # Dio wrapper (get/post + error handling)
│   ├── auth_service.dart            # Login, register, persist token
│   ├── lesson_service.dart          # Create + fetch lessons
│   └── session_service.dart        # Start, advance, submit, pause
├── providers/
│   ├── auth_provider.dart           # AuthState + AuthNotifier (Riverpod)
│   ├── lesson_provider.dart         # LessonState + LessonNotifier
│   └── session_provider.dart       # SessionState + SessionNotifier
├── screens/
│   ├── auth/
│   │   ├── login_screen.dart
│   │   └── register_screen.dart
│   ├── home/
│   │   └── home_screen.dart         # Topic input + suggested topics
│   └── lesson/
│       └── lesson_screen.dart       # Full tutor flow (step + board + answer + feedback)
└── widgets/
    ├── board_widget.dart            # Renders bullet/flowchart/timeline/hierarchy/table
    ├── teacher_bubble.dart          # Chat-style teacher message
    └── progress_bar.dart            # Module title + step counter + progress bar
```

## Notes

- Auth middleware is currently commented out in the backend — login/register
  endpoints may behave as simple user creation. Adjust `AuthService` if your
  backend returns tokens differently.
- The Gemini model name in `llm_service.py` may need updating — verify
  the model string against the Gemini API docs.
- Session storage is file-based on the backend (flat JSON). Suitable for
  local dev; swap to MongoDB for production.
