// Automatic FlutterFlow imports
import '/backend/schema/structs/index.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import 'index.dart'; // Imports other custom actions
import 'package:flutter/material.dart';
// Begin custom action code
// DO NOT REMOVE OR MODIFY THE CODE ABOVE!

import 'index.dart'; // Imports other custom actions

import 'package:record/record.dart';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'dart:convert';

final _audioRecorder = Record();

Future<dynamic> stopTextRecording() async {
  if (FFAppState().isRecording) {
    try {
      // Stop the recording
      final path = FFAppState().audioRecorderPath;
      await _audioRecorder.stop();
      print('Stopped audio recording');

      if (path.isNotEmpty) {
        final file = File(path);
        
        // Check if file exists
        if (!await file.exists()) {
          print('Audio file does not exist at path: $path');
          FFAppState().speechToTextResponse = "";
          return {'success': false, 'message': 'Audio file not found'};
        }
        
        final bytes = await file.readAsBytes();
        
        // Check if file has content
        if (bytes.isEmpty) {
          print('Audio file is empty');
          FFAppState().speechToTextResponse = "";
          return {'success': false, 'message': 'Audio file is empty'};
        }

        final apiKey = FFAppState().apiKey;
        final request = http.MultipartRequest(
          'POST',
          Uri.parse('https://api.openai.com/v1/audio/transcriptions'),
        );
        request.headers['Authorization'] = 'Bearer $apiKey';
        request.fields['model'] = 'whisper-1';
        
        // Get file extension from path
        final fileExtension = path.split('.').last.toLowerCase();
        
        // Verify file extension is supported by Whisper API
        final supportedFormats = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm'];
        if (!supportedFormats.contains(fileExtension)) {
          print('Warning: File extension $fileExtension may not be supported by Whisper API');
          print('Supported formats are: $supportedFormats');
        }
        
        request.files.add(http.MultipartFile.fromBytes(
          'file',
          bytes,
          filename: 'audio.$fileExtension',
        ));

        print('Sending file with extension .$fileExtension and size ${bytes.length} bytes');
        
        try {
          final streamedResponse = await request.send();
          final response = await http.Response.fromStream(streamedResponse);

          if (response.statusCode == 200) {
            final jsonResponse = json.decode(response.body);
            final transcription =
                utf8.decode(latin1.encode(jsonResponse['text']));
            FFAppState().speechToTextResponse = transcription;
            print('Transcription: $transcription');
            return {'success': true, 'message': ''};
          } else {
            String errorMsg = 'Unknown error occurred';
            try {
              final errorJSON = json.decode(response.body);
              if (errorJSON is Map && errorJSON.containsKey('error')) {
                errorMsg = errorJSON['error']['message'] ?? errorMsg;
              }
            } catch (e) {
              errorMsg = 'Failed to parse error response: ${response.body}';
            }
            print('Error: ${response.statusCode} - $errorMsg');
            FFAppState().speechToTextResponse = "";
            return {
              'success': false,
              'message': 'Transcription failed: $errorMsg'
            };
          }
        } catch (e) {
          print('Network error during transcription: $e');
          FFAppState().speechToTextResponse = "";
          return {'success': false, 'message': 'Network error: $e'};
        } finally {
          try {
            await file.delete();
            print('Deleted temporary audio file');
          } catch (e) {
            print('Failed to delete temporary file: $e');
          }
        }
      } else {
        FFAppState().speechToTextResponse = "";
        return {'success': false, 'message': 'Temporary file path is empty'};
      }
    } catch (e) {
      print('Error stopping recording: $e');
      FFAppState().speechToTextResponse = "";
      return {'success': false, 'message': 'Error stopping recording: $e'};
    } finally {
      FFAppState().audioRecorderPath = '';
      FFAppState().isRecording = false;
    }
  }
  return {'success': false, 'message': 'Not recording'};
}

// Set your action name, define your arguments and return parameter,
// and then add the boilerplate code using the green button on the right!
