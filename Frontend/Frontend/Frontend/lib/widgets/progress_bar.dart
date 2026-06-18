// lib/widgets/progress_bar.dart

import 'package:flutter/material.dart';
import '../config/app_theme.dart';

class LessonProgressBar extends StatelessWidget {
  final int currentStep;
  final int totalSteps;
  final String moduleTitle;

  const LessonProgressBar({
    super.key,
    required this.currentStep,
    required this.totalSteps,
    required this.moduleTitle,
  });

  @override
  Widget build(BuildContext context) {
    final progress = totalSteps > 0 ? (currentStep + 1) / totalSteps : 0.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                moduleTitle,
                style: const TextStyle(
                  fontSize: 13,
                  color: AppTheme.onSurfaceMuted,
                  fontWeight: FontWeight.w500,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            Text(
              '${currentStep + 1} / $totalSteps',
              style: const TextStyle(
                fontSize: 12,
                color: AppTheme.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: AppTheme.surfaceVariant,
            valueColor:
                const AlwaysStoppedAnimation<Color>(AppTheme.primary),
            minHeight: 5,
          ),
        ),
      ],
    );
  }
}
