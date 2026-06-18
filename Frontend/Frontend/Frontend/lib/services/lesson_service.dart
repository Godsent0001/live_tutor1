// lib/services/lesson_service.dart

import 'dart:convert';
import 'dart:typed_data';
import '../config/api_config.dart';
import '../models/lesson.dart';
import 'api_service.dart';

class LessonFile {
  final String name;
  final Uint8List bytes;
  LessonFile({required this.name, required this.bytes});
}

class LessonService {
  final ApiService _api;

  LessonService(this._api);

  static const _imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
  static const _textExts  = ['txt', 'md', 'csv', 'json', 'html', 'py', 'js', 'ts'];

  Future<Lesson> createLesson({
    required String topic,
    required String userId,
    String? extraContext,
  }) async {
    final data = await _api.post(ApiConfig.createLesson, data: {
      'topic': topic,
      'user_id': userId,
      if (extraContext != null && extraContext.isNotEmpty)
        'context_prompt': extraContext,
    });
    return Lesson.fromJson(data['lesson'] ?? data);
  }

  Future<Lesson> createLessonFromFiles({
    required String userId,
    required List<LessonFile> files,
    String? contextPrompt,
  }) async {
    final extraMaterials = <String>[];
    final topics = <String>[];

    for (final file in files) {
      final ext = file.name.split('.').last.toLowerCase();

      if (_imageExts.contains(ext)) {
        final base64Image = base64Encode(file.bytes);
        extraMaterials.add('[IMAGE:${file.name}:$base64Image]');
        topics.add('image: ${file.name}');

      } else if (ext == 'pdf') {
        final text = _extractTextFromPdf(file.bytes);
        extraMaterials.add('[PDF:${file.name}]\n$text');
        topics.add('PDF: ${file.name}');

      } else if (_textExts.contains(ext)) {
        final text = utf8.decode(file.bytes, allowMalformed: true);
        extraMaterials.add('[FILE:${file.name}]\n$text');
        topics.add('file: ${file.name}');

      } else {
        final text = utf8.decode(file.bytes, allowMalformed: true);
        extraMaterials.add('[FILE:${file.name}]\n$text');
        topics.add('file: ${file.name}');
      }
    }

    final topic = 'Content from uploaded material(s): ${topics.join(', ')}';

    final data = await _api.post(ApiConfig.createLesson, data: {
      'topic': topic,
      'user_id': userId,
      'extra_materials': extraMaterials,
      if (contextPrompt != null && contextPrompt.isNotEmpty)
        'context_prompt': contextPrompt,
    });

    return Lesson.fromJson(data['lesson'] ?? data);
  }

  String _extractTextFromPdf(Uint8List bytes) {
    try {
      final raw = String.fromCharCodes(bytes);
      final buffer = StringBuffer();

      final btEt = RegExp(r'BT(.*?)ET', dotAll: true);
      for (final match in btEt.allMatches(raw)) {
        final block = match.group(1) ?? '';
        final textParts = RegExp(r'\((.*?)\)', dotAll: true);
        for (final t in textParts.allMatches(block)) {
          final chunk = t.group(1) ?? '';
          if (chunk.trim().isNotEmpty) buffer.write('$chunk ');
        }
      }

      final result = buffer.toString().trim();
      if (result.length >= 50) return result;

      final fallback = StringBuffer();
      for (final m in RegExp(r'[ -~]{4,}').allMatches(raw)) {
        fallback.write('${m.group(0)} ');
      }
      return fallback.toString().trim();
    } catch (_) {
      return 'Could not extract text from PDF.';
    }
  }

  Future<Lesson> getLesson(String lessonId) async {
    final data = await _api.get(ApiConfig.getLesson(lessonId));
    return Lesson.fromJson(data['lesson'] ?? data);
  }
}
