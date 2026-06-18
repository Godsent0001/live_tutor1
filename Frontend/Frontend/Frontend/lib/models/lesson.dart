// lib/models/lesson.dart

import 'step.dart';

class LessonModule {
  final String moduleTitle;
  final List<LessonStep> steps;

  const LessonModule({required this.moduleTitle, required this.steps});

  factory LessonModule.fromJson(Map<String, dynamic> json) {
    return LessonModule(
      moduleTitle: json['module_title'] ?? '',
      steps: (json['steps'] as List? ?? [])
          .map((s) => LessonStep.fromJson(s))
          .toList(),
    );
  }
}

class Lesson {
  final String lessonId;
  final String userId;
  final String topic;
  final List<LessonModule> modules;

  const Lesson({
    required this.lessonId,
    required this.userId,
    required this.topic,
    required this.modules,
  });

  int get totalSteps =>
      modules.fold(0, (sum, m) => sum + m.steps.length);

  factory Lesson.fromJson(Map<String, dynamic> json) {
    return Lesson(
      lessonId: json['lesson_id'] ?? '',
      userId: json['user_id'] ?? '',
      topic: json['topic'] ?? '',
      modules: (json['modules'] as List? ?? [])
          .map((m) => LessonModule.fromJson(m))
          .toList(),
    );
  }
}
