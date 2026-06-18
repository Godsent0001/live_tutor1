// lib/models/teacher_response.dart

import 'step.dart';

class TeacherResponse {
  final String teacherResponse;
  final Board? boardUpdate;

  const TeacherResponse({
    required this.teacherResponse,
    this.boardUpdate,
  });

  factory TeacherResponse.fromJson(Map<String, dynamic> json) {
    // Backend returns:
    // { "current_response": { "teacher_response": "...", "board_update": ... }, "next_step": ... }
    final currentResponse = json['current_response'] as Map<String, dynamic>?;

    final responseText = currentResponse?['teacher_response']
        ?? json['teacher_response']
        ?? '';

    final boardData = currentResponse?['board_update'] ?? json['board_update'];

    return TeacherResponse(
      teacherResponse: responseText.toString(),
      boardUpdate: boardData != null ? Board.fromJson(boardData) : null,
    );
  }
}
