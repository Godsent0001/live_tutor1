// lib/models/session.dart

class Session {
  final String sessionId;
  final String userId;
  final String lessonId;
  final int currentModuleIndex;
  final int currentStepIndex;
  final String status;
  final List<dynamic> history;

  const Session({
    required this.sessionId,
    required this.userId,
    required this.lessonId,
    required this.currentModuleIndex,
    required this.currentStepIndex,
    required this.status,
    required this.history,
  });

  bool get isCompleted => status == 'completed';
  bool get isPaused => status == 'paused';
  bool get isActive => status == 'active';

  factory Session.fromJson(Map<String, dynamic> json) {
    return Session(
      sessionId: json['session_id'] ?? '',
      userId: json['user_id'] ?? '',
      lessonId: json['lesson_id'] ?? '',
      currentModuleIndex: json['current_module_index'] ?? 0,
      currentStepIndex: json['current_step_index'] ?? 0,
      status: json['status'] ?? 'active',
      history: json['history'] ?? [],
    );
  }
}
