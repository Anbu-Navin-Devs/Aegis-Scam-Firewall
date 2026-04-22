class AppConfig {
  // Use '10.0.2.2' if testing on Android Emulator
  // Use your local IPv4 e.g. '192.168.1.5' for physical devices
  static const String devBaseUrl = 'http://172.16.0.124:8000';
  static const String devWsUrl = 'ws://172.16.0.124:8000';

  static const String prodBaseUrl = 'https://api.aegisfirewall.com';
  static const String prodWsUrl = 'wss://api.aegisfirewall.com';

  // Toggle this for prod
  static const bool isProduction = false;

  static String get baseUrl => isProduction ? prodBaseUrl : devBaseUrl;
  static String get wsUrl => isProduction ? prodWsUrl : devWsUrl;
}
