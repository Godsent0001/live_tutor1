// lib/providers/lesson_provider.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/lesson.dart';
import '../services/api_service.dart';
import '../services/lesson_service.dart';
import 'auth_provider.dart';

export '../services/lesson_service.dart' show LessonFile;

final lessonServiceProvider = Provider<LessonService>((ref) {
  return LessonService(ref.read(apiServiceProvider));
});

class LessonState {
  final Lesson? lesson;
  final bool isLoading;
  final String? error;

  const LessonState({this.lesson, this.isLoading = false, this.error});

  LessonState copyWith({
    Lesson? lesson,
    bool? isLoading,
    String? error,
    bool clearError = false,
  }) {
    return LessonState(
      lesson: lesson ?? this.lesson,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : error ?? this.error,
    );
  }
}

class LessonNotifier extends StateNotifier<LessonState> {
  final LessonService _lessonService;
  final Ref _ref;

  LessonNotifier(this._lessonService, this._ref) : super(const LessonState());

  Future<Lesson?> createLesson(String topic, {String? extraContext}) async {
    final userId = _ref.read(authProvider).user?.userId ?? '';
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final lesson = await _lessonService.createLesson(
          topic: topic, userId: userId, extraContext: extraContext);
      state = state.copyWith(lesson: lesson, isLoading: false);
      return lesson;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return null;
    }
  }

  Future<Lesson?> createLessonFromFiles({
    required String userId,
    required List<LessonFile> files,
    String? contextPrompt,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final lesson = await _lessonService.createLessonFromFiles(
        userId: userId,
        files: files,
        contextPrompt: contextPrompt,
      );
      state = state.copyWith(lesson: lesson, isLoading: false);
      return lesson;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return null;
    }
  }

  void clear() {
    state = const LessonState();
  }
}

final lessonProvider =
    StateNotifierProvider<LessonNotifier, LessonState>((ref) {
  return LessonNotifier(ref.read(lessonServiceProvider), ref);
});
