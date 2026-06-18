// lib/providers/session_provider.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/session.dart';
import '../models/step.dart';
import '../models/teacher_response.dart';
import '../services/session_service.dart';
import 'auth_provider.dart';

final sessionServiceProvider = Provider<SessionService>((ref) {
  return SessionService(ref.read(apiServiceProvider));
});

class SessionState {
  final Session? session;
  final CurrentStepData? currentStep;
  final CurrentStepData? pendingNextStep; // held until user taps Next Step
  final TeacherResponse? lastResponse;
  final bool isLoading;
  final bool isSubmitting;
  final String? error;

  const SessionState({
    this.session,
    this.currentStep,
    this.pendingNextStep,
    this.lastResponse,
    this.isLoading = false,
    this.isSubmitting = false,
    this.error,
  });

  bool get hasActiveSession => session != null && !session!.isCompleted;

  SessionState copyWith({
    Session? session,
    CurrentStepData? currentStep,
    CurrentStepData? pendingNextStep,
    TeacherResponse? lastResponse,
    bool? isLoading,
    bool? isSubmitting,
    String? error,
    bool clearError = false,
    bool clearResponse = false,
    bool clearPending = false,
  }) {
    return SessionState(
      session: session ?? this.session,
      currentStep: currentStep ?? this.currentStep,
      pendingNextStep: clearPending ? null : pendingNextStep ?? this.pendingNextStep,
      lastResponse: clearResponse ? null : lastResponse ?? this.lastResponse,
      isLoading: isLoading ?? this.isLoading,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      error: clearError ? null : error ?? this.error,
    );
  }
}

class SessionNotifier extends StateNotifier<SessionState> {
  final SessionService _sessionService;

  SessionNotifier(this._sessionService) : super(const SessionState());

  Future<bool> startSession(String lessonId, String userId) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final session = await _sessionService.startSession(
        userId: userId,
        lessonId: lessonId,
      );
      final step = await _sessionService.getCurrentStep(session.sessionId);
      state = state.copyWith(
        session: session,
        currentStep: step,
        isLoading: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }

  Future<bool> submitAnswer(String answer) async {
    final session = state.session;
    final step = state.currentStep;
    if (session == null || step == null) return false;

    state = state.copyWith(isSubmitting: true, clearError: true);
    try {
      final result = await _sessionService.submitResponse(
        sessionId: session.sessionId,
        lessonId: session.lessonId,
        stepId: step.step.stepId,
        studentAnswer: answer,
      );

      // Store response + hold next step — don't navigate yet
      state = state.copyWith(
        lastResponse: result.response,
        pendingNextStep: result.nextStep,
        isSubmitting: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(isSubmitting: false, error: e.toString());
      return false;
    }
  }

  Future<void> advanceToNextStep() async {
    final session = state.session;
    if (session == null) return;

    // If we already have the next step from submit response, use it
    if (state.pendingNextStep != null) {
      state = state.copyWith(
        currentStep: state.pendingNextStep,
        clearResponse: true,
        clearPending: true,
      );
      return;
    }

    // Otherwise fetch from backend
    state = state.copyWith(isLoading: true, clearResponse: true);
    try {
      final nextStep = await _sessionService.getCurrentStep(session.sessionId);
      state = state.copyWith(
        currentStep: nextStep,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> pauseSession() async {
    final sessionId = state.session?.sessionId;
    if (sessionId == null) return;
    try {
      final updated = await _sessionService.pauseSession(sessionId);
      state = state.copyWith(session: updated);
    } catch (_) {}
  }

  void clearSession() {
    state = const SessionState();
  }
}

final sessionProvider =
    StateNotifierProvider<SessionNotifier, SessionState>((ref) {
  return SessionNotifier(ref.read(sessionServiceProvider));
});
