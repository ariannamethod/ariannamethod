// Automatic FlutterFlow imports
import '/backend/schema/structs/index.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import 'index.dart'; // Imports other custom actions
import 'package:flutter/material.dart';
// Begin custom action code
// DO NOT REMOVE OR MODIFY THE CODE ABOVE!

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:developer' as developer;

Future<Map<String, dynamic>> testWebhookResponse() async {
  try {
    // Get the webhook URL and auth value from app state
    final webhookURL = FFAppState().webhookURL;
    final webhookAuthValue = FFAppState().webhookAuthValue;
    final sessionID = FFAppState().sessionID;
    
    // Check if the webhook URL and auth value are set
    if (webhookURL.isEmpty || webhookAuthValue.isEmpty) {
      return {
        'success': false,
        'message': 'Webhook URL or Auth Value is not set. Please check settings.'
      };
    }
    
    // Create the request body
    final requestBody = {
      'body': {
        'prompt': 'Test message from Vagent app',
        'sessionID': sessionID.isEmpty ? 'test-session' : sessionID
      }
    };
    
    // Log the request details for debugging
    developer.log('Sending request to: $webhookURL');
    developer.log('With auth value: $webhookAuthValue');
    developer.log('Request body: ${json.encode(requestBody)}');
    
    // Send the request
    developer.log('Sending POST request to webhook...');
    final response = await http.post(
      Uri.parse(webhookURL),
      headers: {
        'Authorization': webhookAuthValue,
        'Content-Type': 'application/json',
      },
      body: json.encode(requestBody),
    );
    
    // Log the response for debugging
    developer.log('Response status code: ${response.statusCode}');
    developer.log('Response body: ${response.body}');
    
    // Print to console for easier debugging
    print('TEST WEBHOOK - Response status code: ${response.statusCode}');
    print('TEST WEBHOOK - Response body: ${response.body}');
    
    // Check if the request was successful
    if (response.statusCode == 200) {
      // Parse the response
      final jsonResponse = json.decode(response.body);
      
      // Check if the response has the expected structure
      if (jsonResponse.containsKey('response')) {
        final responseObj = jsonResponse['response'];
        
        if (responseObj.containsKey('text') && responseObj.containsKey('speech')) {
          // Test the speech playback
          final speechText = responseObj['speech'];
          if (speechText != null && speechText.isNotEmpty) {
            try {
              final speechDuration = await fetchSpeechAndPlay(
                speechText,
                FFAppState().apiKey,
              );
              
              return {
                'success': true,
                'message': 'Webhook test successful. Speech duration: $speechDuration ms',
                'text': responseObj['text'],
                'speech': speechText
              };
            } catch (e) {
              return {
                'success': false,
                'message': 'Speech playback failed: $e',
                'text': responseObj['text'],
                'speech': speechText
              };
            }
          } else {
            return {
              'success': false,
              'message': 'Speech text is empty in the response',
              'text': responseObj['text'],
              'speech': speechText
            };
          }
        } else {
          return {
            'success': false,
            'message': 'Response does not contain text or speech fields',
            'response': jsonResponse
          };
        }
      } else {
        return {
          'success': false,
          'message': 'Response does not have the expected structure',
          'response': jsonResponse
        };
      }
    } else {
      return {
        'success': false,
        'message': 'Request failed with status code: ${response.statusCode}',
        'response': response.body
      };
    }
  } catch (e) {
    return {
      'success': false,
      'message': 'Error testing webhook: $e'
    };
  }
}
