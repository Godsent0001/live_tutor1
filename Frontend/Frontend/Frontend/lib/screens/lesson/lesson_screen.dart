// lib/screens/lesson/lesson_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../config/app_theme.dart';
import '../../providers/lesson_provider.dart';
import '../../providers/session_provider.dart';
import '../../widgets/board_widget.dart';
import '../../widgets/teacher_bubble.dart';
import '../../widgets/progress_bar.dart';
import '../../widgets/module_qa_widget.dart';

class LessonScreen extends ConsumerStatefulWidget {
  const LessonScreen({super.key});

  @override
  ConsumerState<LessonScreen> createState() => _LessonScreenState();
}

class _LessonScreenState extends ConsumerState<LessonScreen> {
  final _answerController = TextEditingController();
  final _scrollController = ScrollController();

  // Track which module we were on when the last response came in,
  // so we can show the Q&A panel when the step was the last in that module
  bool _showingModuleQa = false;
  int _qaModuleIndex = 0;
  String _qaModuleTitle = '';

  @override
  void dispose() {
    _answerController.dispose();
    _scrollController.dispose();
    super.dispose();
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

  Future<void> _submitAnswer() async {
    final answer = _answerController.text.trim();
    if (answer.isEmpty) return;
    _answerController.clear();

    final sessionState = ref.read(sessionProvider);
    final currentStep = sessionState.currentStep;

    // Check if we're on the last step of a module before submitting
    // so we know to show Q&A after the response arrives
    final isLastStepInModule = currentStep != null &&
        _isLastStepOfModule(currentStep);

    await ref.read(sessionProvider.notifier).submitAnswer(answer);

    if (isLastStepInModule && mounted) {
      final updatedStep = ref.read(sessionProvider).currentStep;
      // After advancing, if we moved to a new module (or completed), show Q&A
      final movedModule = updatedStep == null ||
          updatedStep.moduleIndex != currentStep.moduleIndex;
      if (movedModule && !ref.read(sessionProvider).session!.isCompleted) {
        setState(() {
          _showingModuleQa = true;
          _qaModuleIndex = currentStep.moduleIndex;
          _qaModuleTitle = currentStep.moduleTitle;
        });
      }
    }

    _scrollToBottom();
  }

  bool _isLastStepOfModule(currentStep) {
    final lesson = ref.read(lessonProvider).lesson;
    if (lesson == null) return false;
    final mIdx = currentStep.moduleIndex;
    if (mIdx >= lesson.modules.length) return false;
    final module = lesson.modules[mIdx];
    return currentStep.stepIndex == module.steps.length - 1;
  }

  Future<void> _continueToNext() async {
    setState(() => _showingModuleQa = false);
    await ref.read(sessionProvider.notifier).advanceToNextStep();
    _scrollToBottom();
  }

  Future<void> _endLesson() async {
    await ref.read(sessionProvider.notifier).pauseSession();
    ref.read(sessionProvider.notifier).clearSession();
    ref.read(lessonProvider.notifier).clear();
    if (mounted) context.go('/home');
  }

  @override
  Widget build(BuildContext context) {
    final sessionState = ref.watch(sessionProvider);
    final lessonState = ref.watch(lessonProvider);

    final currentStep = sessionState.currentStep;
    final lesson = lessonState.lesson;
    final lastResponse = sessionState.lastResponse;
    final isCompleted = sessionState.session?.isCompleted ?? false;

    if (isCompleted && !_showingModuleQa) {
      return _CompletionScreen(onDone: _endLesson);
    }

    if (sessionState.isLoading && currentStep == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator(color: AppTheme.primary)),
      );
    }

    if (currentStep == null && !_showingModuleQa) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('Something went wrong loading the lesson.'),
              const SizedBox(height: 16),
              ElevatedButton(
                  onPressed: () => context.go('/home'),
                  child: const Text('Go Home')),
            ],
          ),
        ),
      );
    }

    final totalSteps = lesson?.totalSteps ?? 1;
    final flatIndex = currentStep == null ? 0 :
        (lesson?.modules
                .take(currentStep.moduleIndex)
                .fold<int>(0, (sum, m) => sum + m.steps.length) ?? 0) +
            currentStep.stepIndex;

    // Module Q&A screen (between modules)
    if (_showingModuleQa) {
      final session = sessionState.session!;
      final lessonId = lesson?.lessonId ?? '';

      return Scaffold(
        appBar: AppBar(
          backgroundColor: AppTheme.background,
          elevation: 0,
          leading: const SizedBox.shrink(),
          title: LessonProgressBar(
            currentStep: flatIndex,
            totalSteps: totalSteps,
            moduleTitle: _qaModuleTitle,
          ),
          titleSpacing: 0,
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: ModuleQaWidget(
            sessionId: session.sessionId,
            lessonId: lessonId,
            moduleIndex: _qaModuleIndex,
            moduleTitle: _qaModuleTitle,
            onContinue: _continueToNext,
          ),
        ),
      );
    }

    final step = currentStep!.step;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: AppTheme.background,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close_rounded, color: AppTheme.onSurfaceMuted),
          onPressed: () => _showExitDialog(context),
        ),
        title: Padding(
          padding: const EdgeInsets.only(right: 16),
          child: LessonProgressBar(
            currentStep: flatIndex,
            totalSteps: totalSteps,
            moduleTitle: currentStep.moduleTitle,
          ),
        ),
        titleSpacing: 8,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              controller: _scrollController,
              padding: const EdgeInsets.all(20),
              children: [
                TeacherBubble(text: step.speech),
                const SizedBox(height: 20),
                BoardWidget(board: step.board),
                const SizedBox(height: 20),
                TeacherBubble(text: step.question.text, isQuestion: true),

                if (lastResponse != null) ...[
                  const SizedBox(height: 20),
                  TeacherBubble(text: lastResponse.teacherResponse),
                  if (lastResponse.boardUpdate != null) ...[
                    const SizedBox(height: 16),
                    BoardWidget(board: lastResponse.boardUpdate!),
                  ],
                  const SizedBox(height: 16),
                  if (!currentStep.isLastStep)
                    ElevatedButton(
                      onPressed:
                          sessionState.isLoading ? null : _continueToNext,
                      child: sessionState.isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                  strokeWidth: 2.5, color: Colors.white))
                          : const Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text('Next Step'),
                                SizedBox(width: 8),
                                Icon(Icons.arrow_forward_rounded, size: 18),
                              ],
                            ),
                    ).animate().fadeIn()
                  else
                    ElevatedButton(
                      onPressed: _endLesson,
                      style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.success),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.check_circle_outline, size: 20),
                          SizedBox(width: 8),
                          Text('Complete Lesson'),
                        ],
                      ),
                    ).animate().fadeIn(),
                ],

                const SizedBox(height: 100),
              ],
            ),
          ),

          if (lastResponse == null)
            _AnswerInputBar(
              controller: _answerController,
              isSubmitting: sessionState.isSubmitting,
              onSubmit: _submitAnswer,
            ),
        ],
      ),
    );
  }

  void _showExitDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.surface,
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
        title: const Text('Leave lesson?'),
        content: const Text(
          'Your progress will be saved. You can resume later.',
          style: TextStyle(color: AppTheme.onSurfaceMuted),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.of(ctx).pop(),
              child: const Text('Stay')),
          TextButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              _endLesson();
            },
            child: Text('Leave', style: TextStyle(color: AppTheme.error)),
          ),
        ],
      ),
    );
  }
}

// ----------------------------
// ANSWER INPUT BAR
// ----------------------------
class _AnswerInputBar extends StatelessWidget {
  final TextEditingController controller;
  final bool isSubmitting;
  final VoidCallback onSubmit;

  const _AnswerInputBar({
    required this.controller,
    required this.isSubmitting,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 24),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        border: Border(
            top: BorderSide(color: AppTheme.primary.withOpacity(0.15))),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: controller,
              maxLines: 3,
              minLines: 1,
              onSubmitted: (_) => isSubmitting ? null : onSubmit(),
              decoration: const InputDecoration(
                hintText: 'Type your answer...',
                contentPadding:
                    EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
            ),
          ),
          const SizedBox(width: 10),
          GestureDetector(
            onTap: isSubmitting ? null : onSubmit,
            child: Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: AppTheme.primary,
                borderRadius: BorderRadius.circular(14),
              ),
              child: isSubmitting
                  ? const Center(
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                            strokeWidth: 2.5, color: Colors.white),
                      ),
                    )
                  : const Icon(Icons.send_rounded,
                      color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    ).animate().slideY(begin: 0.2).fadeIn();
  }
}

// ----------------------------
// COMPLETION SCREEN
// ----------------------------
class _CompletionScreen extends StatelessWidget {
  final VoidCallback onDone;

  const _CompletionScreen({required this.onDone});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(40),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: AppTheme.success.withOpacity(0.15),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.check_circle_rounded,
                    color: AppTheme.success, size: 60),
              ).animate().scale(duration: 500.ms, curve: Curves.elasticOut),
              const SizedBox(height: 32),
              Text('Lesson Complete!',
                  style: Theme.of(context).textTheme.displayLarge,
                  textAlign: TextAlign.center)
                  .animate().fadeIn(delay: 200.ms),
              const SizedBox(height: 12),
              const Text(
                'Great work! You\'ve finished this lesson.\nKeep the momentum going.',
                textAlign: TextAlign.center,
                style: TextStyle(
                    color: AppTheme.onSurfaceMuted,
                    fontSize: 15,
                    height: 1.6),
              ).animate().fadeIn(delay: 300.ms),
              const SizedBox(height: 48),
              ElevatedButton(
                onPressed: onDone,
                child: const Text('Learn Something New'),
              ).animate().fadeIn(delay: 400.ms),
            ],
          ),
        ),
      ),
    );
  }
}
