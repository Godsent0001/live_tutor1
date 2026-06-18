// lib/models/step.dart

class Board {
  final String type;
  final List<String> content;

  const Board({required this.type, required this.content});

  factory Board.fromJson(Map<String, dynamic> json) {
    return Board(
      type: json['type'] ?? 'bullet',
      content: List<String>.from(json['content'] ?? []),
    );
  }

  Map<String, dynamic> toJson() => {
        'type': type,
        'content': content,
      };
}

class Question {
  final String type;
  final String text;

  const Question({required this.type, required this.text});

  factory Question.fromDynamic(dynamic json) {
    if (json is String) {
      return Question(type: 'recall', text: json);
    }
    if (json is Map<String, dynamic>) {
      return Question(
        type: json['type'] ?? 'recall',
        text: json['text'] ?? '',
      );
    }
    return const Question(type: 'recall', text: '');
  }
}

class LessonStep {
  final String stepId;
  final String speech;
  final Board board;
  final Question question;
  final List<String> expectedConcepts;
  final String? moduleTitle;

  const LessonStep({
    required this.stepId,
    required this.speech,
    required this.board,
    required this.question,
    required this.expectedConcepts,
    this.moduleTitle,
  });

  factory LessonStep.fromJson(Map<String, dynamic> json) {
    return LessonStep(
      stepId: json['step_id']?.toString() ?? '',
      speech: json['speech'] ?? '',
      board: Board.fromJson(json['board'] ?? {}),
      question: Question.fromDynamic(json['question']),
      expectedConcepts: List<String>.from(json['expected_concepts'] ?? []),
      moduleTitle: json['module_title'],
    );
  }
}

class CurrentStepData {
  final String sessionId;
  final String lessonId;
  final int moduleIndex;
  final int stepIndex;
  final String moduleTitle;
  final LessonStep step;
  final bool isLastStep;

  const CurrentStepData({
    required this.sessionId,
    required this.lessonId,
    required this.moduleIndex,
    required this.stepIndex,
    required this.moduleTitle,
    required this.step,
    required this.isLastStep,
  });

  factory CurrentStepData.fromJson(Map<String, dynamic> json) {
    return CurrentStepData(
      sessionId: json['session_id'] ?? '',
      lessonId: json['lesson_id'] ?? '',
      moduleIndex: json['module_index'] ?? 0,
      stepIndex: json['step_index'] ?? 0,
      moduleTitle: json['module_title'] ?? '',
      step: LessonStep.fromJson(json['step'] ?? {}),
      isLastStep: json['is_last_step'] ?? false,
    );
  }
}
