// Automatic FlutterFlow imports
import '/backend/schema/structs/index.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import 'index.dart'; // Imports other custom actions
import 'package:flutter/material.dart';
// Begin custom action code
// DO NOT REMOVE OR MODIFY THE CODE ABOVE!

//import '/flutter_flow/custom_functions.dart'; // Imports custom functions

import 'dart:async'; // Required for the Completer
import 'dart:convert';
import 'dart:io';
import 'package:just_audio/just_audio.dart'; // Import for audio playback
import 'package:just_audio_cache/just_audio_cache.dart'; // Import for caching audio
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';

// Add this line at the top of the file, outside of any function
GlobalAudioPlayer globalAudioPlayer = GlobalAudioPlayer();

Future<int> fetchSpeechAndPlay(
  String promptText,
  String? apiKey,
) async {
  print('fetchSpeechAndPlay - Starting with text: ${promptText.substring(0, min(50, promptText.length))}...');
  
  try {
    // Reset audioplayer every time
    // fixes bug where audio would not play after locking the screen once on iOS
    print('fetchSpeechAndPlay - Reinitializing audio player');
    await globalAudioPlayer.reinitialize();
    
    // Ensure the API key is provided
    if (apiKey == null || apiKey.isEmpty) {
      print('fetchSpeechAndPlay - Error: API key is empty or null');
      throw Exception('API key is required.');
    }
    
    print('fetchSpeechAndPlay - API key is valid (first 4 chars): ${apiKey.substring(0, min(4, apiKey.length))}...');
    
    // Set up the POST request headers.
    Map<String, String> headers = {
      'Authorization': 'Bearer $apiKey',
      'Content-Type': 'application/json',
    };

    // Set up the POST request body.
    String body = json.encode(
        {'model': 'tts-1', 'input': promptText, 'voice': 'nova', 'speed': '1'});
    
    print('fetchSpeechAndPlay - Sending request to OpenAI TTS API');
    
    // Make the POST request to fetch the speech audio.
    final response = await http.post(
      Uri.parse('https://api.openai.com/v1/audio/speech'),
      headers: headers,
      body: body,
    );

      // Handle the response
      print('fetchSpeechAndPlay - Response status code: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        print('fetchSpeechAndPlay - Received audio data: ${response.bodyBytes.length} bytes');
        
        try {
          // Replace the local AudioPlayer with the global one
          print('fetchSpeechAndPlay - Setting audio source');
          final duration = await globalAudioPlayer.setAudioSource(
            BytesAudioSource(response.bodyBytes),
          );
          
          if (duration == null) {
            print('fetchSpeechAndPlay - Warning: Duration is null');
            throw Exception('Audio duration is null');
          }
          
          print('fetchSpeechAndPlay - Audio duration: ${duration.inMilliseconds} ms');
          
          // Play the audio
          print('fetchSpeechAndPlay - Playing audio');
          await globalAudioPlayer.play();
          
          // Return the duration in milliseconds
          return duration.inMilliseconds;
        } catch (e) {
          print('fetchSpeechAndPlay - Error setting audio source or playing: $e');
          
          // Try with a different approach for Android
          try {
            print('fetchSpeechAndPlay - Trying alternative approach for Android');
            // Dispose and recreate the player
            await globalAudioPlayer.reinitialize();
            
            // Create a temporary file to store the audio data
            final tempDir = await getTemporaryDirectory();
            final tempFile = File('${tempDir.path}/temp_speech_${DateTime.now().millisecondsSinceEpoch}.mp3');
            await tempFile.writeAsBytes(response.bodyBytes);
            
            print('fetchSpeechAndPlay - Saved audio to temporary file: ${tempFile.path}');
            
            // Use the file as the audio source
            final duration = await globalAudioPlayer.player.setAudioSource(
              AudioSource.file(tempFile.path),
            );
            
            if (duration == null) {
              print('fetchSpeechAndPlay - Warning: Duration is null with alternative approach');
              throw Exception('Audio duration is null with alternative approach');
            }
            
            print('fetchSpeechAndPlay - Alternative approach audio duration: ${duration.inMilliseconds} ms');
            
            // Play the audio
            print('fetchSpeechAndPlay - Playing audio with alternative approach');
            await globalAudioPlayer.player.play();
            
            // Return the duration in milliseconds
            return duration.inMilliseconds;
          } catch (e2) {
            print('fetchSpeechAndPlay - Error with alternative approach: $e2');
            
            // Try one more approach with progressive buffering
            try {
              print('fetchSpeechAndPlay - Trying progressive buffering approach');
              await globalAudioPlayer.reinitialize();
              
              // Create a memory buffer
              final buffer = response.bodyBytes.buffer.asUint8List();
              
              // Use a progressive audio source
              final duration = await globalAudioPlayer.player.setAudioSource(
                ProgressiveAudioSource(Uri.dataFromBytes(buffer)),
              );
              
              if (duration == null) {
                print('fetchSpeechAndPlay - Warning: Duration is null with progressive approach');
                throw Exception('Audio duration is null with progressive approach');
              }
              
              print('fetchSpeechAndPlay - Progressive approach audio duration: ${duration.inMilliseconds} ms');
              
              // Play the audio
              print('fetchSpeechAndPlay - Playing audio with progressive approach');
              await globalAudioPlayer.player.play();
              
              // Return the duration in milliseconds
              return duration.inMilliseconds;
            } catch (e3) {
              print('fetchSpeechAndPlay - Error with progressive approach: $e3');
              throw Exception('Failed to play audio: Multiple approaches failed');
            }
          }
        }
    } else {
      // If the server did not return a "200 OK response",
      // log the error and throw an exception
      print('fetchSpeechAndPlay - Error: Status code ${response.statusCode}');
      print('fetchSpeechAndPlay - Error response: ${response.body}');
      
      throw Exception(
          'Failed to generate speech. Status code: ${response.statusCode}, Response: ${response.body}');
    }
  } catch (e) {
    print('fetchSpeechAndPlay - Exception: $e');
    rethrow;
  }
}

// Helper function to get minimum of two integers
int min(int a, int b) {
  return a < b ? a : b;
}

// Add this class at the end of the file
class GlobalAudioPlayer {
  AudioPlayer _player = AudioPlayer();

  AudioPlayer get player => _player;

  Future<Duration?> setAudioSource(AudioSource source) {
    return _player.setAudioSource(source);
  }

  Future<void> play() {
    return _player.play();
  }

  Future<void> stop() {
    return _player.stop();
  }

  Duration? get duration => _player.duration;

  // New method to reinitialize the player
  Future<void> reinitialize() async {
    await _player.dispose();
    _player = AudioPlayer();
  }
}

class BytesAudioSource extends StreamAudioSource {
  final List<int> _bytes;
  BytesAudioSource(this._bytes);

  @override
  Future<StreamAudioResponse> request([int? start, int? end]) async {
    start ??= 0;
    end ??= _bytes.length;
    return StreamAudioResponse(
      sourceLength: _bytes.length,
      contentLength: end - start,
      offset: start,
      stream: Stream.value(_bytes.sublist(start, end)),
      contentType: 'audio/mp3',
    );
  }
}
