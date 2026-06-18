// lib/widgets/board_widget.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/step.dart';

class BoardWidget extends StatefulWidget {
  final Board board;

  const BoardWidget({super.key, required this.board});

  @override
  State<BoardWidget> createState() => _BoardWidgetState();
}

class _BoardWidgetState extends State<BoardWidget> {
  final List<_WritingController> _controllers = [];

  @override
  void initState() {
    super.initState();
    _startWriting();
  }

  @override
  void didUpdateWidget(BoardWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.board != widget.board) {
      for (final c in _controllers) {
        c.dispose();
      }
      _controllers.clear();
      _startWriting();
    }
  }

  // Lines animate strictly one after another: each line waits for the previous to finish
  void _startWriting() {
    final items = _buildItems(widget.board);

    // Each controller starts only after the prior one finishes
    for (int i = 0; i < items.length; i++) {
      final ctrl = _WritingController(
        fullText: items[i],
        // charDelay determines speed; 28ms per char feels natural
        charDelay: const Duration(milliseconds: 28),
      );
      _controllers.add(ctrl);
      ctrl.addListener(() => setState(() {}));
    }

    // Chain them: start first immediately, then each subsequent one
    // starts when its predecessor notifies completion
    _chainStart(0);
  }

  void _chainStart(int index) {
    if (index >= _controllers.length) return;

    final ctrl = _controllers[index];

    // Add a one-time listener that fires when this controller finishes
    void onDone() {
      if (!ctrl.isWriting && ctrl.displayed.length == ctrl.fullText.length) {
        ctrl.removeListener(onDone);
        // Small pause between lines for readability
        Future.delayed(const Duration(milliseconds: 120), () {
          if (!ctrl._disposed) _chainStart(index + 1);
        });
      }
    }

    ctrl.addListener(onDone);

    // First line has a short initial delay; others are driven by chaining
    if (index == 0) {
      Future.delayed(const Duration(milliseconds: 300), () {
        if (!ctrl._disposed) ctrl.start();
      });
    } else {
      ctrl.start();
    }
  }

  List<String> _buildItems(Board board) {
    final type = board.type;
    if (type == 'table') {
      final items = <String>[];
      for (int i = 0; i < board.content.length; i += 2) {
        if (i + 1 < board.content.length) {
          items.add('${board.content[i]}  →  ${board.content[i + 1]}');
        } else {
          items.add(board.content[i]);
        }
      }
      return items;
    }
    return board.content;
  }

  @override
  void dispose() {
    for (final c in _controllers) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final items = _buildItems(widget.board);
    return _Whiteboard(
      boardType: widget.board.type,
      items: items,
      controllers: _controllers,
    );
  }
}

// ----------------------------
// WHITEBOARD FRAME
// ----------------------------
class _Whiteboard extends StatelessWidget {
  final String boardType;
  final List<String> items;
  final List<_WritingController> controllers;

  const _Whiteboard({
    required this.boardType,
    required this.items,
    required this.controllers,
  });

  String get _boardLabel => switch (boardType) {
        'flowchart' || 'process' => '⟶  FLOW',
        'timeline' => '⏱  TIMELINE',
        'hierarchy' => '⬡  HIERARCHY',
        'table' => '⊞  TABLE',
        'formula' => 'Σ  FORMULA',
        'comparison' => '⇌  COMPARE',
        _ => '✎  BOARD',
      };

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: const Color(0xFFF8F6EE),
        borderRadius: BorderRadius.circular(4),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.18),
            blurRadius: 8,
            offset: const Offset(2, 4),
          ),
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 2,
            offset: const Offset(0, 1),
          ),
        ],
        border: Border.all(color: const Color(0xFFD6CFA8), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _BoardTray(label: _boardLabel),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 10, 20, 20),
            child: boardType == 'flowchart' || boardType == 'process'
                ? _FlowContent(items: items, controllers: controllers)
                : boardType == 'timeline'
                    ? _TimelineContent(items: items, controllers: controllers)
                    : _DefaultContent(
                        items: items,
                        controllers: controllers,
                        boardType: boardType),
          ),
        ],
      ),
    );
  }
}

// ----------------------------
// BOARD TRAY
// ----------------------------
class _BoardTray extends StatelessWidget {
  final String label;
  const _BoardTray({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: const BoxDecoration(
        color: Color(0xFFE8E0C0),
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(3),
          topRight: Radius.circular(3),
        ),
        border:
            Border(bottom: BorderSide(color: Color(0xFFD0C890), width: 1)),
      ),
      child: Row(
        children: [
          Container(
            width: 28,
            height: 14,
            decoration: BoxDecoration(
              color: const Color(0xFFF4C2C2),
              borderRadius: BorderRadius.circular(2),
              border: Border.all(color: const Color(0xFFD49090), width: 0.5),
            ),
          ),
          const SizedBox(width: 10),
          Container(
            width: 40,
            height: 8,
            decoration: BoxDecoration(
              color: const Color(0xFFF0EDD8),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(color: const Color(0xFFCCC8A0), width: 0.5),
            ),
          ),
          const Spacer(),
          Text(
            label,
            style: GoogleFonts.caveat(
              fontSize: 13,
              color: const Color(0xFF888060),
              fontWeight: FontWeight.w600,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}

// ----------------------------
// DEFAULT (bullet / formula / etc.)
// ----------------------------
class _DefaultContent extends StatelessWidget {
  final List<String> items;
  final List<_WritingController> controllers;
  final String boardType;

  const _DefaultContent({
    required this.items,
    required this.controllers,
    required this.boardType,
  });

  String _prefix(int index) => switch (boardType) {
        'formula' => '',
        'hierarchy' => index == 0 ? '' : '  ↳  ',
        'comparison' => index % 2 == 0 ? '✦  ' : '✧  ',
        _ => '•  ',
      };

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: List.generate(items.length, (i) {
        final ctrl = i < controllers.length ? controllers[i] : null;
        final displayed = ctrl?.displayed ?? '';
        final showCursor =
            ctrl != null && ctrl.isWriting && displayed.isNotEmpty;

        return Padding(
          padding: const EdgeInsets.only(bottom: 14),
          child: _RuledLine(
            child: RichText(
              text: TextSpan(
                children: [
                  TextSpan(
                    text: displayed.isEmpty ? '' : '${_prefix(i)}$displayed',
                    style: GoogleFonts.caveat(
                      fontSize: 20,
                      color: const Color(0xFF1A237E),
                      height: 1.3,
                    ),
                  ),
                  if (showCursor)
                    TextSpan(
                      text: '|',
                      style: GoogleFonts.caveat(
                        fontSize: 20,
                        color: const Color(0xFF1A237E).withOpacity(0.6),
                      ),
                    ),
                ],
              ),
            ),
          ),
        );
      }),
    );
  }
}

// ----------------------------
// FLOW CONTENT
// ----------------------------
class _FlowContent extends StatelessWidget {
  final List<String> items;
  final List<_WritingController> controllers;

  const _FlowContent({required this.items, required this.controllers});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: List.generate(items.length, (i) {
        final ctrl = i < controllers.length ? controllers[i] : null;
        final displayed = ctrl?.displayed ?? '';
        final showCursor =
            ctrl != null && ctrl.isWriting && displayed.isNotEmpty;
        final isLast = i == items.length - 1;

        return Column(
          children: [
            Container(
              width: double.infinity,
              padding:
                  const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                border:
                    Border.all(color: const Color(0xFF9FA8DA), width: 1.5),
                borderRadius: BorderRadius.circular(4),
                color: const Color(0xFFF0F2FF),
              ),
              child: RichText(
                textAlign: TextAlign.center,
                text: TextSpan(children: [
                  TextSpan(
                    text: displayed,
                    style: GoogleFonts.caveat(
                      fontSize: 19,
                      color: const Color(0xFF1A237E),
                    ),
                  ),
                  if (showCursor)
                    TextSpan(
                      text: '|',
                      style: GoogleFonts.caveat(
                        fontSize: 19,
                        color: const Color(0xFF1A237E).withOpacity(0.5),
                      ),
                    ),
                ]),
              ),
            ),
            if (!isLast)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Text(
                  '↓',
                  style: GoogleFonts.caveat(
                    fontSize: 22,
                    color: const Color(0xFF5C6BC0),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
          ],
        );
      }),
    );
  }
}

// ----------------------------
// TIMELINE CONTENT
// ----------------------------
class _TimelineContent extends StatelessWidget {
  final List<String> items;
  final List<_WritingController> controllers;

  const _TimelineContent({required this.items, required this.controllers});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(items.length, (i) {
        final ctrl = i < controllers.length ? controllers[i] : null;
        final displayed = ctrl?.displayed ?? '';
        final showCursor =
            ctrl != null && ctrl.isWriting && displayed.isNotEmpty;
        final isLast = i == items.length - 1;

        return IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Column(
                children: [
                  Container(
                    width: 26,
                    height: 26,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                          color: const Color(0xFF5C6BC0), width: 2),
                      color: const Color(0xFFF0F2FF),
                    ),
                    child: Center(
                      child: Text(
                        '${i + 1}',
                        style: GoogleFonts.caveat(
                          fontSize: 14,
                          color: const Color(0xFF3949AB),
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                  if (!isLast)
                    Expanded(
                      child: Container(
                        width: 1.5,
                        color: const Color(0xFF9FA8DA),
                        margin: const EdgeInsets.symmetric(vertical: 2),
                      ),
                    ),
                ],
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 16, top: 2),
                  child: _RuledLine(
                    child: RichText(
                      text: TextSpan(children: [
                        TextSpan(
                          text: displayed,
                          style: GoogleFonts.caveat(
                            fontSize: 19,
                            color: const Color(0xFF1A237E),
                            height: 1.3,
                          ),
                        ),
                        if (showCursor)
                          TextSpan(
                            text: '|',
                            style: GoogleFonts.caveat(
                              fontSize: 19,
                              color: const Color(0xFF1A237E).withOpacity(0.5),
                            ),
                          ),
                      ]),
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      }),
    );
  }
}

// ----------------------------
// RULED LINE
// ----------------------------
class _RuledLine extends StatelessWidget {
  final Widget child;
  const _RuledLine({required this.child});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        child,
        Container(
          height: 1,
          color: const Color(0xFFBBB090).withOpacity(0.5),
          margin: const EdgeInsets.only(top: 4),
        ),
      ],
    );
  }
}

// ----------------------------
// WRITING CONTROLLER
// ----------------------------
class _WritingController extends ChangeNotifier {
  final String fullText;
  final Duration charDelay;

  String _displayed = '';
  bool _isWriting = false;
  bool _disposed = false;

  _WritingController({
    required this.fullText,
    required this.charDelay,
  });

  String get displayed => _displayed;
  bool get isWriting => _isWriting;

  void start() async {
    if (_disposed) return;
    _isWriting = true;
    for (int i = 0; i <= fullText.length; i++) {
      if (_disposed) return;
      _displayed = fullText.substring(0, i);
      notifyListeners();
      if (i < fullText.length) await Future.delayed(charDelay);
    }
    _isWriting = false;
    notifyListeners();
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}
