import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/intent_response.dart';
import '../../models/document_scan_response.dart';
import '../../models/threat_log.dart';
import '../config/app_config.dart';
import '../constants/api_endpoints.dart';
import '../utils/error_mapper.dart';

class ApiService {
  void _handleErrors(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) return;
    throw ApiException(
      response.statusCode, 
      ErrorMapper.getMessage(response.statusCode)
    );
  }

  Future<IntentResponse> analyzeIntent(String transcript) async {
    final response = await http.post(
      Uri.parse('${AppConfig.baseUrl}${ApiEndpoints.intentAnalysis}'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'transcript': transcript}),
    );
    
    _handleErrors(response);
    return IntentResponse.fromJson(jsonDecode(response.body));
  }

  Future<DocumentScanResponse> scanDocument(String filePath) async {
    final request = http.MultipartRequest(
      'POST', 
      Uri.parse('${AppConfig.baseUrl}${ApiEndpoints.documentScan}')
    );
    request.files.add(await http.MultipartFile.fromPath('file', filePath));
    
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    _handleErrors(response);
    return DocumentScanResponse.fromJson(jsonDecode(response.body));
  }

  Future<List<ThreatLog>> getHistoryLogs({int limit = 20}) async {
    final response = await http.get(
      Uri.parse('${AppConfig.baseUrl}${ApiEndpoints.historyLogs}?limit=$limit'),
    );
    
    _handleErrors(response);
    final List<dynamic> data = jsonDecode(response.body);
    return data.map((json) => ThreatLog.fromJson(json)).toList();
  }
}
