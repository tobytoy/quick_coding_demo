import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hello App',
      home: HelloPage(),
    );
  }
}

class HelloPage extends StatefulWidget {
  @override
  _HelloPageState createState() => _HelloPageState();
}

class _HelloPageState extends State<HelloPage> {
  final TextEditingController _controller = TextEditingController();
  String _response = "";

  Future<void> sendName() async {
    try {
      final response = await http.post(
        // https://expert-succotash-46x55g5wpjp2qpv9-8000.app.github.dev/
        Uri.parse('http://expert-succotash-46x55g5wpjp2qpv9-8000.app.github.dev/hello'),
        // Uri.parse('http://127.0.0.1:8000/hello'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'name': _controller.text}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _response = data['message'];
        });
      } else {
        setState(() {
          _response = "Server error: ${response.statusCode}";
        });
      }
    } catch (e) {
      print("Request error: $e");
      setState(() {
        _response = "Request failed: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Hello App')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              decoration: InputDecoration(labelText: 'Enter your name'),
            ),
            SizedBox(height: 10),
            ElevatedButton(
              onPressed: sendName,
              child: Text('Send'),
            ),
            SizedBox(height: 20),
            Text(
              _response,
              style: TextStyle(fontSize: 18),
            ),
          ],
        ),
      ),
    );
  }
}
