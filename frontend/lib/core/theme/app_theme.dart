import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Brand colors based on requirement
  static const Color mBlue = Color(0xFF3B82F6);
  static const Color mOrange = Color(0xFFF97316);
  static const Color mRed = Color(0xFFEF4444);
  static const Color mGreen = Color(0xFF10B981);

  static const Color bgLight = Color(0xFFF5F7FB);
  static const Color cardLight = Colors.white;

  static const Color bgDark = Color(0xFF111827); // Replaced gradient base with strict hex
  static const Color cardDark = Color(0xFF111827);

  static ThemeData get lightTheme {
    return ThemeData(
      brightness: Brightness.light,
      primaryColor: mBlue,
      scaffoldBackgroundColor: bgLight,
      colorScheme: ColorScheme.fromSeed(
        seedColor: mBlue,
        brightness: Brightness.light,
        surface: cardLight,
      ),
      textTheme: GoogleFonts.interTextTheme(ThemeData.light().textTheme),
      useMaterial3: true,
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      primaryColor: mBlue,
      scaffoldBackgroundColor: bgDark,
      colorScheme: ColorScheme.fromSeed(
        seedColor: mBlue,
        brightness: Brightness.dark,
        surface: cardDark,
      ),
      textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).apply(
        bodyColor: Colors.white,
        displayColor: Colors.white,
      ),
      useMaterial3: true,
    );
  }
}
