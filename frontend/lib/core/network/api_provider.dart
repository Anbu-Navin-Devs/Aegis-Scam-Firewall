import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_service.dart';

// Provides a singleton of ApiService for use across the application
final apiServiceProvider = Provider<ApiService>((ref) => ApiService());
