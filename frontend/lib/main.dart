import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/services.dart';
import 'background_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Herramienta Cifrado y Descifrado',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: Stack(
        children: [
          const BackgroundScreen(), // El fondo
          const CipherPage(), // El contenido principal
        ],
      ),
    );
  }
}

class CipherPage extends StatefulWidget {
  const CipherPage({super.key});

  @override
  _CipherPageState createState() => _CipherPageState();
}

class _CipherPageState extends State<CipherPage> {
  final _textController = TextEditingController();
  final _keyController = TextEditingController();
  String _cipherType = 'caesar';
  String _mode = 'encrypt';
  String _result = '';
  bool _isLoading = false;

  Future<void> _processCipher() async {
    setState(() {
      _isLoading = true;
    });

    final response = await http.post(
      Uri.parse('http://127.0.0.1:8000/cipher'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'text': _textController.text,
        'key': _keyController.text,
        'cipher_type': _cipherType,
        'mode': _mode,
      }),
    );

    final responseData = json.decode(response.body);
    setState(() {
      _result = responseData['result'] ?? 'Error';
      _isLoading = false;
    });
  }

  void _copyToClipboard() {
    Clipboard.setData(ClipboardData(text: _result));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Resultado copiado al portapapeles')),
    );
  }

  bool _isKeyRequired() {
    return _cipherType == 'caesar' ||
        _cipherType == 'playfair' ||
        _cipherType == 'amsco';
  }

  bool _isKeyNumeric() {
    return _cipherType == 'caesar' || _cipherType == 'amsco';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Albert Ll.')),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Herramienta de Cifrado y Descifrado',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _textController,
                decoration: InputDecoration(
                  labelText: 'Texto',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                  filled: true,
                  fillColor: Colors.blue[50],
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _cipherType,
                decoration: InputDecoration(
                  labelText: 'Tipo de Cifrado',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                  filled: true,
                  fillColor: Colors.blue[50],
                ),
                onChanged: (value) {
                  setState(() {
                    _cipherType = value!;
                  });
                },
                items: const [
                  DropdownMenuItem(value: 'caesar', child: Text('César')),
                  DropdownMenuItem(value: 'atbash', child: Text('Atbash')),
                  DropdownMenuItem(value: 'playfair', child: Text('Playfair')),
                  DropdownMenuItem(value: 'polybios', child: Text('Polybios')),
                  DropdownMenuItem(value: 'amsco', child: Text('Amsco')),
                  DropdownMenuItem(value: 'route', child: Text('Ruta')),
                ],
              ),
              const SizedBox(height: 16),
              if (_isKeyRequired())
                TextField(
                  controller: _keyController,
                  decoration: InputDecoration(
                    labelText: 'Clave',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                    ),
                    filled: true,
                    fillColor: Colors.blue[50],
                  ),
                  keyboardType: _isKeyNumeric()
                      ? TextInputType.number
                      : TextInputType.text,
                ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _mode,
                decoration: InputDecoration(
                  labelText: 'Modo',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                  filled: true,
                  fillColor: Colors.blue[50],
                ),
                onChanged: (value) {
                  setState(() {
                    _mode = value!;
                  });
                },
                items: const [
                  DropdownMenuItem(value: 'encrypt', child: Text('Cifrar')),
                  DropdownMenuItem(value: 'decrypt', child: Text('Descifrar')),
                ],
              ),
              const SizedBox(height: 24),
              _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : ElevatedButton.icon(
                      onPressed: _processCipher,
                      icon: const Icon(Icons.play_arrow),
                      label: const Text('Procesar'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16.0),
                      ),
                    ),
              const SizedBox(height: 24),
              Text(
                'Resultado:',
                style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue[800]),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(16.0),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(8.0),
                  border: Border.all(color: Colors.blue.shade100),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        _result,
                        style: const TextStyle(fontSize: 16),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.copy, color: Colors.blue),
                      onPressed: _result.isNotEmpty ? _copyToClipboard : null,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
