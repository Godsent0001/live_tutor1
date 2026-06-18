// lib/services/session_service.dart

import '../config/api_config.dart';
import '../models/session.dart';
import '../models/step.dart';
import '../models/teacher_response.dart';
import 'api_service.dart';

class SessionService {
  final ApiService _api;

  SessionService(this._api);

  Future<Session> startSession({
    required String userId,
    required String lessonId,
  }) async {
    final data = await _api.post(ApiConfig.startSession, data: {
      'user_id': userId,
      'lesson_id': lessonId,
    });
    return Session.fromJson(data['session'] ?? data);
  }

  Future<Session> getSession(String sessionId) async {
    final data = await _api.get(ApiConfig.getSession(sessionId));
    return Session.fromJson(data);
  }

  Future<CurrentStepData?> getCurrentStep(String sessionId) async {
    final data = await _api.get(ApiConfig.currentStep(sessionId));
    return CurrentStepData.fromJson(data);
  }

  Future<Session> nextStep(String sessionId) async {
    final data = await _api.post(ApiConfig.nextStep(sessionId));
    return Session.fromJson(data['session'] ?? data);
  }

  Future<Session> pauseSession(String sessionId) async {
    final data = await _api.post(ApiConfig.pauseSession(sessionId));
    return Session.fromJson(data['session'] ?? data);
  }

  Future<Session> resumeSession(String sessionId) async {
    final data = await _api.post(ApiConfig.resumeSession(sessionId));
    return Session.fromJson(data['session'] ?? data);
  }

  Future<({TeacherResponse response, CurrentStepData? nextStep})>
      submitResponse({
    required String sessionId,
    required String lessonId,
    required String stepId,
    required String studentAnswer,
  }) async {
    final data = await _api.post(ApiConfig.submitResponse, data: {
      'session_id': sessionId,
      'lesson_id': lessonId,
      'step_id': stepId,
      'student_answer': studentAnswer,
    });

    final teacherResponse = TeacherResponse.fromJson(data);

    // Backend already advances the step before returning,
    // so next_step in the response is the already-advanced step.
    // We hold it but don't auto-navigate — let the user tap Next Step.
    CurrentStepData? nextStep;
    if (data['next_step'] != null) {
      nextStep = CurrentStepData.fromJson(data['next_step']);
    }

    return (response: teacherResponse, nextStep: nextStep);
  }

  Future<Map<String, dynamic>> askModuleQuestion({
    required String sessionId,
    required String lessonId,
    required int moduleIndex,
    required String question,
  }) async {
    return await _api.post(ApiConfig.askModuleQuestion, data: {
      'session_id': sessionId,
      'lesson_id': lessonId,
      'module_index': moduleIndex,
      'student_question': question,
    });
  }
}
