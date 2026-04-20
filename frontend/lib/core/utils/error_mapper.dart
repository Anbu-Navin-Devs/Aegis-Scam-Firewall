class ErrorMapper {
  static String getMessage(int statusCode) {
    switch (statusCode) {
      case 400:
        return 'Bad Request: Invalid payload structure.';
      case 401:
        return 'Unauthorized: Please check your credentials.';
      case 403:
        return 'Forbidden: You do not have access.';
      case 404:
        return 'Not Found: The requested resource could not be found.';
      case 413:
        return 'Payload Too Large: Document exceeds size limits.';
      case 500:
        return 'Internal Server Error: Aegis engine failure. Please try again.';
      case 502:
      case 503:
      case 504:
        return 'Service Unavailable: Aegis is currently experiencing issues.';
      default:
        return 'An unexpected error occurred. Please try again later.';
    }
  }

  static String getExceptionMessage(dynamic exception) {
    // We can expand this with specific exception types (e.g. SocketException)
    return exception.toString();
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;
  
  ApiException(this.statusCode, this.message);
  
  @override
  String toString() => 'ApiException: $statusCode - $message';
}
