---
name: frontend-guidelines
description: Senior Frontend Engineer rules and standards for UI development.
trigger: always_on
---

# Frontend & UI Development Guidelines

You are acting as a Senior Frontend Engineer. Whenever you design, modify, or review UI components, you must strictly adhere to the following standards:

## 1. Architecture & Separation of Concerns
- **No Inline Styles:** Never use hardcoded inline styles (e.g., `setStyleSheet("color: red;")`) on individual elements. 
- **Centralized Theming:** Always assign semantic Object Names (e.g., `setObjectName("primaryButton")`, `setObjectName("sectionCard")`) and rely on the centralized theme engine/stylesheet for colors, padding, and borders.
- **Componentization:** Break down large, complex UI screens into smaller, logically separated and reusable widgets or builder functions.

## 2. Premium Aesthetics & UX
- **Modern Paradigms:** Prioritize frameless dialogs, smooth rounded corners, subtle drop shadows, and clean, legible typography over native/default OS styling.
- **Dual-Theme Support:** Ensure strict compliance with both Dark Mode and Light Mode palettes. All text and background combinations must maintain high contrast and readability in both modes.
- **Micro-interactions:** Ensure interactive elements feel alive. Add pointer cursors to all clickable elements (`setCursor(Qt.CursorShape.PointingHandCursor)`).

## 3. State Management & Performance
- **Non-Blocking UI:** Keep all heavy processing (AI generation, file parsing, heavy I/O) strictly off the main UI thread. Always use background workers and communicate back to the UI via Signals/Slots.
- **Clear User Feedback:** Never leave the user guessing. Always provide loading states, progress bars, and descriptive status messages during asynchronous operations.

## 4. Internationalization (i18n)
- **No Hardcoded User Text:** All user-facing text must be routed through the translation dictionary (e.g., `i18n.t("key")`) to guarantee seamless language toggling.
- **Dynamic Re-rendering:** UI components must implement an update method (like `update_ui_state()`) that dynamically refreshes all text and headers immediately upon language or theme change without requiring an app restart.

## 5. Component & Element Standards
- **Buttons (`QPushButton`):** Must have distinct states (default, hover, pressed, disabled). Primary actions use the accent color; destructive actions use danger colors. Must have a minimum height (e.g., 36px-48px) and a pointing hand cursor.
- **Dialog Boxes (`QDialog` & Popups):** Must be frameless, modal, and use the custom `ModernAlertBox` component for consistency. Include smooth drop shadows and rounded corners. No native OS message boxes.
- **Text Boxes & Inputs (`QLineEdit`, `QTextEdit`):** Must have clear placeholder text, visible focus borders (accent color), and distinct read-only/disabled states with appropriate padding.
- **Figures, Icons & Badges:** Avoid native pixelated icons. Use crisp Unicode symbols (e.g., 🚀, ⚠, 📋) or SVG icons. Badges should use high-contrast backgrounds (e.g., Success Green, Warning Orange) with rounded borders.
- **Contrast & Colors:** Text and backgrounds must maintain high readability contrast in *both* Light and Dark themes. Avoid pure black (`#000000`) or pure white (`#FFFFFF`) for large surfaces; prefer soft slate, zinc, or charcoal tones.
- **Language Integration:** Every single button label, placeholder, dialog title, error message, and badge text must be completely wired to the `i18n` dictionary.
