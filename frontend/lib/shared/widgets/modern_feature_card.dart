import 'package:flutter/material.dart';

class ModernFeatureCard extends StatefulWidget {
  final String title;
  final String description;
  final IconData icon;
  final Color accentColor;
  final VoidCallback onTap;

  const ModernFeatureCard({
    super.key,
    required this.title,
    required this.description,
    required this.icon,
    required this.accentColor,
    required this.onTap,
  });

  @override
  State<ModernFeatureCard> createState() => _ModernFeatureCardState();
}

class _ModernFeatureCardState extends State<ModernFeatureCard> {
  bool _isPressed = false;

  void _handleTapDown(TapDownDetails details) {
    setState(() => _isPressed = true);
  }

  void _handleTapUp(TapUpDetails details) {
    setState(() => _isPressed = false);
    widget.onTap();
  }

  void _handleTapCancel() {
    setState(() => _isPressed = false);
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return GestureDetector(
      onTapDown: _handleTapDown,
      onTapUp: _handleTapUp,
      onTapCancel: _handleTapCancel,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 100), // Fast interaction < 150ms
        curve: Curves.easeInOut,
        transform: Matrix4.identity()..scale(_isPressed ? 0.96 : 1.0),
        transformAlignment: Alignment.center,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: BorderRadius.circular(20),
          boxShadow: isDark
              ? [
                  BoxShadow(
                    color: widget.accentColor.withOpacity(0.05), // Subtle glow
                    blurRadius: 10,
                    spreadRadius: 1,
                  )
                ]
              : [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 25,
                    offset: const Offset(0, 10),
                  ),
                  BoxShadow(
                    color: Colors.black.withOpacity(0.08),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
        ),
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top: Icon
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isDark 
                    ? widget.accentColor.withOpacity(0.15) 
                    : widget.accentColor.withOpacity(0.1),
              ),
              child: Icon(
                widget.icon,
                color: widget.accentColor,
                size: 24,
              ),
            ),
            const Spacer(),
            // Title & Description
            Text(
              widget.title,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 15,
              ),
            ),
            const SizedBox(height: 4),
            Flexible(
              child: Text(
                widget.description,
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey.shade500,
                  height: 1.3,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const SizedBox(height: 8),
            // Bottom Right: Arrow CTA
            Align(
              alignment: Alignment.bottomRight,
              child: Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: widget.accentColor.withOpacity(0.1),
                ),
                child: Icon(
                  Icons.arrow_forward_rounded,
                  size: 16,
                  color: widget.accentColor,
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}
