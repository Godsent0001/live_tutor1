// lib/widgets/module_qa_widget.dart
//
// Post-module Q&A panel. Shown after all steps in a module are complete.
// Students can ask as many questions as they want before moving on.

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../config/app_theme.dart';
import '../services/api_service.dart';
import '../services/session_service.dart';
import 'board_widget.dart';
import '../models/step.dart';

class ModuleQaWidget extends StatefulWidget {
  final String sessionId;
  final String lessonId;
  final int moduleIndex;
  final String moduleTitle;
  final VoidCallback onContinue;

  const ModuleQaWidget({
    super.key,
    required this.sessionId,
    required this.lessonId,
    required this.moduleIndex,
    required this.moduleTitle,
    required this.onContinue,
  });

  @override
  State<ModuleQaWidget> createState() => _ModuleQaWidgetState();
}

class _ModuleQaWidgetState extends State<ModuleQaWidget> {
  final _questionController = TextEditingController();
  final _scrollController = ScrollController();

  late final SessionService _sessionService;

  // Each entry: { 'question': String, 'answer': String, 'board': Board? }
  final List<Map<String, dynamic>> _exchanges = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _sessionService = SessionService(ApiService());
  }

  @override
  void dispose() {
    _questionController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _submitQuestion() async {
    final q = _questionController.text.trim();
    if (q.isEmpty) return;

    setState(() {
      _isLoading = true;
      _exchanges.add({'question': q, 'answer': null, 'board': null});
      _questionController.clear();
    });

    _scrollToBottom();

    try {
      final result = await _sessionService.askModuleQuestion(
        sessionId: widget.sessionId,
        lessonId: widget.lessonId,
        moduleIndex: widget.moduleIndex,
        question: q,
      );

      Board? board;
      final boardData = result['board_update'];
      if (boardData != null && boardData is Map<String, dynamic>) {
        try {
          board = Board.fromJson(boardData);
        } catch (_) {}
      }

      setState(() {
        _exchanges.last['answer'] = result['answer'] ?? '';
        _exchanges.last['board'] = board;
        _isLoading = false;
      });

      _scrollToBottom();
    } catch (e) {
      setState(() {
        _exchanges.last['answer'] = 'Sorry, something went wrong. Please try again.';
        _exchanges.last['board'] = null;
        _isLoading = false;
      });
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent + 400,
          duration: const Duration(milliseconds: 400),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Module complete banner
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppTheme.secondary.withOpacity(0.15),
                AppTheme.primary.withOpacity(0.10),
              ],
            ),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppTheme.secondary.withOpacity(0.3)),
          ),
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: AppTheme.secondary.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.check_rounded,
                    color: AppTheme.secondary, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Module complete!',
                      style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.secondary),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      widget.moduleTitle,
                      style: const TextStyle(
                          fontSize: 12, color: AppTheme.onSurfaceMuted),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ).animate().fadeIn(duration: 300.ms).slideY(begin: 0.1),

        const SizedBox(height: 16),

        // Invitation to ask
        const Text(
          'Any questions before we move on?',
          style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: AppTheme.onSurface),
        ).animate().fadeIn(delay: 100.ms),

        const SizedBox(height: 4),

        Text(
          'Ask as many as you need — the tutor is here.',
          style: TextStyle(fontSize: 13, color: AppTheme.onSurfaceMuted),
        ).animate().fadeIn(delay: 150.ms),

        const SizedBox(height: 16),

        // Q&A exchange list
        if (_exchanges.isNotEmpty) ...[
          ListView.builder(
            controller: _scrollController,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _exchanges.length,
            itemBuilder: (context, i) {
              final ex = _exchanges[i];
              return _QaExchange(
                question: ex['question'] as String,
                answer: ex['answer'] as String?,
                board: ex['board'] as Board?,
              );
            },
          ),
          const SizedBox(height: 12),
        ],

        // Input row
        _QuestionInput(
          controller: _questionController,
          isLoading: _isLoading,
          onSubmit: _submitQuestion,
        ).animate().fadeIn(delay: 200.ms),

        const SizedBox(height: 20),

        // Continue button
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: _isLoading ? null : widget.onContinue,
            icon: const Icon(Icons.arrow_forward_rounded, size: 18),
            label: const Text('Continue to next module'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              side: BorderSide(color: AppTheme.primary.withOpacity(0.5)),
              foregroundColor: AppTheme.primary,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ).animate().fadeIn(delay: 250.ms),
      ],
    );
  }
}

// ----------------------------
// SINGLE Q&A EXCHANGE
// ----------------------------
class _QaExchange extends StatelessWidget {
  final String question;
  final String? answer;
  final Board? board;

  const _QaExchange(
      {required this.question, required this.answer, required this.board});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Student question bubble (right-aligned)
          Align(
            alignment: Alignment.centerRight,
            child: Container(
              constraints: BoxConstraints(
                  maxWidth: MediaQuery.of(context).size.width * 0.75),
              padding:
                  const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.12),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(4),
                  bottomLeft: Radius.circular(16),
                  bottomRight: Radius.circular(16),
                ),
                border: Border.all(color: AppTheme.primary.withOpacity(0.2)),
              ),
              child: Text(
                question,
                style: const TextStyle(
                    fontSize: 14, color: AppTheme.onSurface, height: 1.45),
              ),
            ),
          ),

          const SizedBox(height: 10),

          // Answer bubble (left-aligned, tutor style)
          if (answer == null)
            Padding(
              padding: const EdgeInsets.only(left: 4),
              child: Row(
                children: [
                  _TutorAvatar(),
                  const SizedBox(width: 10),
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: AppTheme.primary),
                  ),
                ],
              ),
            )
          else ...[
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _TutorAvatar(),
                const SizedBox(width: 10),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(13),
                    decoration: BoxDecoration(
                      color: AppTheme.surface,
                      borderRadius: const BorderRadius.only(
                        topRight: Radius.circular(16),
                        bottomLeft: Radius.circular(16),
                        bottomRight: Radius.circular(16),
                      ),
                      border: Border.all(
                          color: AppTheme.primary.withOpacity(0.15)),
                    ),
                    child: Text(
                      answer!,
                      style: const TextStyle(
                          fontSize: 14,
                          color: AppTheme.onSurface,
                          height: 1.55),
                    ),
                  ),
                ),
              ],
            ).animate().fadeIn(duration: 300.ms).slideY(begin: 0.08),

            if (board != null) ...[
              const SizedBox(height: 12),
              BoardWidget(board: board!)
                  .animate()
                  .fadeIn(delay: 100.ms)
                  .slideY(begin: 0.05),
            ],
          ],
        ],
      ),
    );
  }
}

// ----------------------------
// TUTOR AVATAR
// ----------------------------
class _TutorAvatar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [AppTheme.primary, AppTheme.primary.withOpacity(0.6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        shape: BoxShape.circle,
      ),
      child: const Icon(Icons.school_rounded, color: Colors.white, size: 16),
    );
  }
}

// ----------------------------
// QUESTION INPUT
// ----------------------------
class _QuestionInput extends StatelessWidget {
  final TextEditingController controller;
  final bool isLoading;
  final VoidCallback onSubmit;

  const _QuestionInput({
    required this.controller,
    required this.isLoading,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Expanded(
          child: TextField(
            controller: controller,
            maxLines: 3,
            minLines: 1,
            textInputAction: TextInputAction.newline,
            style: const TextStyle(fontSize: 14),
            decoration: InputDecoration(
              hintText: 'Ask a question about this module...',
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide:
                    BorderSide(color: AppTheme.primary.withOpacity(0.3)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide:
                    BorderSide(color: AppTheme.primary.withOpacity(0.2)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppTheme.primary),
              ),
            ),
          ),
        ),
        const SizedBox(width: 10),
        GestureDetector(
          onTap: isLoading ? null : onSubmit,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: isLoading
                  ? AppTheme.primary.withOpacity(0.4)
                  : AppTheme.primary,
              borderRadius: BorderRadius.circular(12),
            ),
            child: isLoading
                ? const Padding(
                    padding: EdgeInsets.all(12),
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.send_rounded,
                    color: Colors.white, size: 20),
          ),
        ),
      ],
    );
  }
}
