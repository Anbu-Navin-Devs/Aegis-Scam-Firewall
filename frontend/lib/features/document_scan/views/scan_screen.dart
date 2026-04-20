import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../providers/document_provider.dart';
import '../../../shared/widgets/loading_state_view.dart';
import '../../../shared/widgets/error_state_view.dart';

class ScanScreen extends ConsumerStatefulWidget {
  const ScanScreen({super.key});

  @override
  ConsumerState<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends ConsumerState<ScanScreen> {
  String? _selectedFilePath;
  String? _selectedFileName;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'png', 'jpeg'],
    );

    if (result != null && result.files.single.path != null) {
      setState(() {
        _selectedFilePath = result.files.single.path;
        _selectedFileName = result.files.single.name;
      });
      // Clear any previous results
      ref.read(documentProvider.notifier).reset();
    }
  }

  @override
  Widget build(BuildContext context) {
    final scanState = ref.watch(documentProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Document Scan')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    const Icon(Icons.upload_file, size: 64, color: Colors.grey),
                    const SizedBox(height: 16),
                    Text(
                      _selectedFileName ?? 'No file selected',
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    OutlinedButton.icon(
                      onPressed: _pickFile,
                      icon: const Icon(Icons.folder_open),
                      label: const Text('Choose Document'),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _selectedFilePath == null || scanState.isLoading
                          ? null
                          : () => ref.read(documentProvider.notifier).scanDocument(_selectedFilePath!),
                      icon: const Icon(Icons.document_scanner),
                      label: const Text('Analyze Risk'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: scanState.when(
                data: (response) {
                  if (response == null) return const SizedBox.shrink();
                  final isHighRisk = response.riskLevel.toLowerCase() == 'high';
                  
                  return Card(
                    color: isHighRisk ? Colors.red.shade50 : Colors.orange.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'Risk Level: ${response.riskLevel}',
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              color: isHighRisk ? Colors.red : Colors.orange,
                              fontWeight: FontWeight.bold,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 8),
                          Text(response.summary, textAlign: TextAlign.center),
                          const Divider(),
                          const Text('Flagged Clauses:', style: TextStyle(fontWeight: FontWeight.bold)),
                          Expanded(
                            child: ListView.builder(
                              itemCount: response.flaggedClauses.length,
                              itemBuilder: (context, i) => ListTile(
                                leading: const Icon(Icons.warning, color: Colors.red),
                                title: Text(response.flaggedClauses[i]),
                              ),
                            ),
                          )
                        ],
                      ),
                    ),
                  );
                },
                loading: () => const LoadingStateView(message: 'Scanning high-risk document...'),
                error: (error, _) => ErrorStateView(
                  errorMessage: error.toString(),
                  onRetry: () => ref.read(documentProvider.notifier).scanDocument(_selectedFilePath!),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
