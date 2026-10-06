# Workspace Guidelines: Aegis Scam Firewall

## UI/UX Engineering Directive (UI/UX Pro Max)

Whenever designing, implementing, reviewing, or refactoring user interfaces in this project (Android Jetpack Compose frontend or web/dashboard components):

### 1. Mandate & Design Intelligence
Always follow the **`ui-ux-pro-max`** design intelligence framework.
To query design systems, styles, typography, color palettes, or stack-specific patterns, run:
```bash
python "C:\Users\anbua\.gemini\config\skills\ui-ux-pro-max\scripts\search.py" "<query>" [--design-system] [--stack jetpack-compose] [--domain <domain>]
```
- **Product Domain**: Cybersecurity / Fraud Defense / Privacy Firewall.
- **Visual Aesthetic**: High-contrast, dark-mode first, tactical cyber defense theme with clean readability, glowing accents, and high-trust status indicators.

### 2. Priority Rules (Strict Hierarchy)
1. **Accessibility (CRITICAL)**: WCAG AA contrast (≥ 4.5:1), visible focus states, proper content descriptions for TalkBack/screen readers.
2. **Touch & Interaction (CRITICAL)**: Minimum target size 48×48dp on Android, instant press feedback (ripple/elevation/opacity within 80–150ms).
3. **Performance (HIGH)**: Zero layout shift, smooth 60/120fps animations, lightweight vector graphics (`ImageVector` / vector XML).
4. **Visual Style (HIGH)**: Vector-only icons (no emojis as UI controls), cohesive stroke weights and icon styling.
5. **Layout & Spacing (HIGH)**: 8dp grid rhythm, safe-area insets (`WindowInsets`, system bar padding, gesture bars).
6. **Typography & Color (MEDIUM)**: Semantic design tokens via `MaterialTheme.colorScheme` and `MaterialTheme.typography` (never raw hardcoded hex in Composables).
7. **Animation & Motion (MEDIUM)**: State transitions with intent, respect system reduced-motion settings.
8. **Feedback & Forms (MEDIUM)**: Immediate inline error states, contextual progress bars for scanning telemetry.
9. **Navigation (HIGH)**: Single-activity Jetpack Navigation with predictable back stack.

### 3. Pre-Delivery Checklist
Before finishing any UI task:
- [ ] No emojis used as structural UI icons.
- [ ] Touch targets are at least 48×48dp with adequate spacing.
- [ ] Semantic tokens used for colors and typography.
- [ ] Light and dark mode contrast verified (≥ 4.5:1).
- [ ] Safe areas respected across status bars, navigation bars, and cutouts.
