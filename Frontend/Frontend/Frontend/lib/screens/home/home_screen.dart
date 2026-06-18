// lib/screens/home/home_screen.dart

import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/lesson_provider.dart';
import '../../providers/session_provider.dart';

// Represents a single picked file
class _PickedFile {
  final String name;
  final Uint8List bytes;
  _PickedFile({required this.name, required this.bytes});
}

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final _topicController = TextEditingController();
  final _contextController = TextEditingController(); // context/prompt for files

  // Multiple files
  final List<_PickedFile> _pickedFiles = [];
  bool _isLoadingFile = false;

  static const _supportedExts = [
    'pdf',
    'jpg', 'jpeg', 'png', 'gif', 'webp',
    'txt', 'md', 'csv', 'json', 'html',
    'py', 'js', 'ts',
  ];

  static const _imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp'];

  final List<String> _suggestedTopics = [
    'Photosynthesis',
    'World War II',
    'Python basics',
    'Linear algebra',
    'Supply & demand',
    'Newton\'s laws',
    'The French Revolution',
    'DNA & genetics',
  ];

  @override
  void dispose() {
    _topicController.dispose();
    _contextController.dispose();
    super.dispose();
  }

  IconData _iconForFile(String fileName) {
    final ext = fileName.split('.').last.toLowerCase();
    if (_imageExts.contains(ext)) return Icons.image_outlined;
    if (ext == 'pdf') return Icons.picture_as_pdf_outlined;
    if (ext == 'csv') return Icons.table_chart_outlined;
    if (ext == 'json') return Icons.data_object_outlined;
    if (ext == 'html') return Icons.html_outlined;
    if (['py', 'js', 'ts'].contains(ext)) return Icons.code_outlined;
    if (['md', 'txt'].contains(ext)) return Icons.article_outlined;
    return Icons.insert_drive_file_outlined;
  }

  Future<void> _pickFiles() async {
    setState(() => _isLoadingFile = true);
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: _supportedExts,
        withData: true,
        allowMultiple: true, // allow picking multiple at once
      );
      if (result != null && result.files.isNotEmpty) {
        setState(() {
          for (final file in result.files) {
            if (file.bytes != null) {
              // Avoid duplicates by name
              if (!_pickedFiles.any((f) => f.name == file.name)) {
                _pickedFiles.add(_PickedFile(name: file.name, bytes: file.bytes!));
              }
            }
          }
        });
      }
    } finally {
      setState(() => _isLoadingFile = false);
    }
  }

  void _removeFile(int index) {
    setState(() => _pickedFiles.removeAt(index));
  }

  void _clearAllFiles() {
    setState(() {
      _pickedFiles.clear();
      _contextController.clear();
    });
  }

  Future<void> _startLesson() async {
    final userId = ref.read(authProvider).user?.userId ?? '';
    final hasFiles = _pickedFiles.isNotEmpty;
    final topic = _topicController.text.trim();
    final contextText = _contextController.text.trim();

    if (!hasFiles && topic.isEmpty) {
      ScaffoldMessenger.of(this.context).showSnackBar(
        const SnackBar(content: Text('Please enter a topic or upload a file')),
      );
      return;
    }

    final lessonNotifier = ref.read(lessonProvider.notifier);

    final lesson = hasFiles
        ? await lessonNotifier.createLessonFromFiles(
            userId: userId,
            files: _pickedFiles
                .map((f) => LessonFile(name: f.name, bytes: f.bytes))
                .toList(),
            contextPrompt: contextText,
          )
        : await lessonNotifier.createLesson(topic, extraContext: contextText.isEmpty ? null : contextText);

    if (lesson == null || !mounted) return;

    final success = await ref
        .read(sessionProvider.notifier)
        .startSession(lesson.lessonId, userId);

    if (success && mounted) this.context.push('/lesson');
  }

  @override
  Widget build(BuildContext context) {
    final lessonState = ref.watch(lessonProvider);
    final user = ref.watch(authProvider).user;
    final isLoading = lessonState.isLoading;
    final hasFiles = _pickedFiles.isNotEmpty;

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Hello, ${user?.name.split(' ').first ?? 'Learner'} 👋',
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(color: AppTheme.onSurfaceMuted),
                      ),
                      Text('What will you\nlearn today?',
                          style: Theme.of(context).textTheme.displayLarge),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.logout_rounded,
                        color: AppTheme.onSurfaceMuted),
                    onPressed: () async {
                      await ref.read(authProvider.notifier).logout();
                      if (mounted) context.go('/login');
                    },
                  ),
                ],
              ).animate().fadeIn(duration: 400.ms),

              const SizedBox(height: 36),

              // Main card
              Container(
                decoration: BoxDecoration(
                  color: AppTheme.surface,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(
                    color: hasFiles
                        ? AppTheme.secondary.withOpacity(0.4)
                        : AppTheme.primary.withOpacity(0.3),
                  ),
                ),
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Mode chips
                    Row(
                      children: [
                        _ModeChip(
                          label: 'Enter topic',
                          icon: Icons.edit_outlined,
                          active: !hasFiles,
                          onTap: _clearAllFiles,
                        ),
                        const SizedBox(width: 10),
                        _ModeChip(
                          label: 'Upload files',
                          icon: Icons.upload_file_outlined,
                          active: hasFiles,
                          onTap: _pickFiles,
                        ),
                      ],
                    ),

                    const SizedBox(height: 18),

                    if (hasFiles) ...[
                      // File list
                      ...List.generate(_pickedFiles.length, (i) {
                        final f = _pickedFiles[i];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: _FilePreviewCard(
                            fileName: f.name,
                            icon: _iconForFile(f.name),
                            onRemove: () => _removeFile(i),
                          ).animate().fadeIn().slideY(begin: 0.1),
                        );
                      }),

                      // Add more files button
                      GestureDetector(
                        onTap: _isLoadingFile ? null : _pickFiles,
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          decoration: BoxDecoration(
                            color: AppTheme.surfaceVariant,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(
                                color: AppTheme.secondary.withOpacity(0.3)),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.add_rounded,
                                  size: 16, color: AppTheme.secondary),
                              const SizedBox(width: 6),
                              Text(
                                'Add more files',
                                style: TextStyle(
                                    fontSize: 12, color: AppTheme.secondary),
                              ),
                            ],
                          ),
                        ),
                      ),

                      const SizedBox(height: 14),

                      // Context prompt field
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Context (optional)',
                            style: TextStyle(
                                fontSize: 12,
                                color: AppTheme.onSurfaceMuted,
                                fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _contextController,
                            maxLines: 3,
                            minLines: 2,
                            style: const TextStyle(fontSize: 14),
                            decoration: const InputDecoration(
                              hintText:
                                  'e.g. "Focus on Chapter 3" or "I\'m a beginner" or "Explain for a 10-year-old"',
                              contentPadding: EdgeInsets.symmetric(
                                  horizontal: 14, vertical: 12),
                            ),
                          ),
                        ],
                      ),
                    ] else ...[
                      // Topic text field
                      TextField(
                        controller: _topicController,
                        maxLines: 2,
                        minLines: 1,
                        onSubmitted: (_) => isLoading ? null : _startLesson(),
                        style: const TextStyle(fontSize: 16),
                        decoration: const InputDecoration(
                          hintText: 'e.g. "How does the immune system work?"',
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.zero,
                          fillColor: Colors.transparent,
                          filled: true,
                        ),
                      ),
                      const SizedBox(height: 10),
                      GestureDetector(
                        onTap: _isLoadingFile ? null : _pickFiles,
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          decoration: BoxDecoration(
                            color: AppTheme.surfaceVariant,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                                color: AppTheme.primary.withOpacity(0.2)),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.upload_file_outlined,
                                  size: 18, color: AppTheme.onSurfaceMuted),
                              const SizedBox(width: 8),
                              Text(
                                _isLoadingFile
                                    ? 'Loading...'
                                    : 'Or upload files  •  PDF, image, code, text',
                                style: const TextStyle(
                                    fontSize: 12,
                                    color: AppTheme.onSurfaceMuted),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],

                    const SizedBox(height: 16),

                    ElevatedButton(
                      onPressed: isLoading ? null : _startLesson,
                      child: isLoading
                          ? Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const SizedBox(
                                  width: 18, height: 18,
                                  child: CircularProgressIndicator(
                                      strokeWidth: 2.5, color: Colors.white),
                                ),
                                const SizedBox(width: 12),
                                Text(
                                  hasFiles
                                      ? 'Analysing files...'
                                      : 'Generating lesson...',
                                  style: TextStyle(
                                      color: Colors.white.withOpacity(0.8)),
                                ),
                              ],
                            )
                          : Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  hasFiles
                                      ? Icons.auto_stories_rounded
                                      : Icons.bolt_rounded,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Text(hasFiles ? 'Teach me this' : 'Start Lesson'),
                              ],
                            ),
                    ),
                  ],
                ),
              ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.1),

              const SizedBox(height: 32),

              if (!hasFiles) ...[
                Text('Supported formats',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.onSurfaceMuted, fontSize: 12))
                    .animate().fadeIn(delay: 140.ms),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _FormatChip(label: 'PDF', icon: Icons.picture_as_pdf_outlined),
                    _FormatChip(label: 'Image', icon: Icons.image_outlined),
                    _FormatChip(label: 'TXT / MD', icon: Icons.article_outlined),
                    _FormatChip(label: 'CSV', icon: Icons.table_chart_outlined),
                    _FormatChip(label: 'JSON', icon: Icons.data_object_outlined),
                    _FormatChip(label: 'HTML', icon: Icons.html_outlined),
                    _FormatChip(label: 'Python / JS / TS', icon: Icons.code_outlined),
                  ],
                ).animate().fadeIn(delay: 160.ms),

                const SizedBox(height: 28),

                Text('Suggested topics',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: AppTheme.onSurfaceMuted, fontSize: 14))
                    .animate().fadeIn(delay: 180.ms),
                const SizedBox(height: 14),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: _suggestedTopics
                      .asMap()
                      .entries
                      .map((e) => GestureDetector(
                            onTap: () => setState(
                                () => _topicController.text = e.value),
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 14, vertical: 8),
                              decoration: BoxDecoration(
                                color: AppTheme.surfaceVariant,
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(
                                    color: AppTheme.primary.withOpacity(0.2)),
                              ),
                              child: Text(e.value,
                                  style: const TextStyle(
                                      fontSize: 13,
                                      color: AppTheme.onSurface)),
                            ),
                          )
                              .animate(delay: (200 + e.key * 40).ms)
                              .fadeIn()
                              .scale(begin: const Offset(0.9, 0.9)))
                      .toList(),
                ),
              ],

              if (lessonState.error != null) ...[
                const SizedBox(height: 20),
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppTheme.error.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(lessonState.error!,
                      style: const TextStyle(
                          color: AppTheme.error, fontSize: 13)),
                ).animate().fadeIn().shakeX(),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

// ----------------------------
// MODE CHIP
// ----------------------------
class _ModeChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool active;
  final VoidCallback onTap;

  const _ModeChip(
      {required this.label,
      required this.icon,
      required this.active,
      required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        decoration: BoxDecoration(
          color:
              active ? AppTheme.primary.withOpacity(0.15) : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: active
                ? AppTheme.primary
                : AppTheme.onSurfaceMuted.withOpacity(0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon,
                size: 14,
                color: active ? AppTheme.primary : AppTheme.onSurfaceMuted),
            const SizedBox(width: 6),
            Text(label,
                style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: active ? AppTheme.primary : AppTheme.onSurfaceMuted)),
          ],
        ),
      ),
    );
  }
}

// ----------------------------
// FILE PREVIEW CARD (compact, dismissible)
// ----------------------------
class _FilePreviewCard extends StatelessWidget {
  final String fileName;
  final IconData icon;
  final VoidCallback onRemove;

  const _FilePreviewCard(
      {required this.fileName, required this.icon, required this.onRemove});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppTheme.secondary.withOpacity(0.08),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppTheme.secondary.withOpacity(0.25)),
      ),
      child: Row(
        children: [
          Icon(icon, color: AppTheme.secondary, size: 18),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              fileName,
              style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: AppTheme.onSurface),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          GestureDetector(
            onTap: onRemove,
            child: const Icon(Icons.close_rounded,
                size: 16, color: AppTheme.onSurfaceMuted),
          ),
        ],
      ),
    );
  }
}

// ----------------------------
// FORMAT CHIP
// ----------------------------
class _FormatChip extends StatelessWidget {
  final String label;
  final IconData icon;

  const _FormatChip({required this.label, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: AppTheme.surfaceVariant,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: AppTheme.onSurfaceMuted),
          const SizedBox(width: 5),
          Text(label,
              style: const TextStyle(
                  fontSize: 11, color: AppTheme.onSurfaceMuted)),
        ],
      ),
    );
  }
}
