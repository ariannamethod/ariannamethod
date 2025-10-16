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
import 'package:path_provider/path_provider.dart';
import 'dart:typed_data';
import 'dart:io';

final _audioRecorder = Record();

Future<void> startTextRecording() async {
  try {
    if (await _audioRecorder.hasPermission()) {
      // Get the temporary directory
      final tempDir = await getTemporaryDirectory();
      
      // Use m4a format for both platforms as it's supported by Whisper API
      final fileExtension = '.m4a';
      final tempFilePath =
          '${tempDir.path}/temp_audio_${DateTime.now().millisecondsSinceEpoch}$fileExtension';

      // Configure recorder with compatible settings for both platforms
      final recorderConfig = RecordConfig(
        encoder: AudioEncoder.aacLc,  // AAC in M4A container
        bitRate: 128000,
      );

      // Start recording with configuration
      await _audioRecorder.start(
        path: tempFilePath,
        encoder: recorderConfig.encoder,
        bitRate: recorderConfig.bitRate,
      );
      
      print('Starting audio recording to $tempFilePath with encoder ${recorderConfig.encoder}');

      // Update FlutterFlow app state
      FFAppState().audioRecorderPath = tempFilePath;
      FFAppState().isRecording = true;
    } else {
      print('Audio recording permission not granted');
    }
  } catch (e) {
    print('Error starting recording: $e');
    // Reset recording state in case of error
    FFAppState().isRecording = false;
    FFAppState().audioRecorderPath = '';
  }
}

class RecordConfig {
  final AudioEncoder encoder;
  final int bitRate;

  RecordConfig({
    required this.encoder,
    required this.bitRate,
  });
}

// Set your action name, define your arguments and return parameter,
// and then add the boilerplate code using the green button on the right!
