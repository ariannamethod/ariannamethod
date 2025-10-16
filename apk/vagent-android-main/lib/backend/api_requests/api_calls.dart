import 'dart:convert';

import 'package:flutter/foundation.dart';

import '/flutter_flow/flutter_flow_util.dart';
import 'api_manager.dart';

export 'api_manager.dart' show ApiCallResponse;

const _kPrivateApiFunctionName = 'ffPrivateApiCall';

class GetAgentResponseCall {
  static Future<ApiCallResponse> call({
    String? prompt = '',
    String? webhookURL = '',
    String? webhookAuthValue = '',
    String? sessionID = '',
  }) async {
    // Log the request parameters for debugging
    print('GetAgentResponseCall - Request:');
    print('  Webhook URL: $webhookURL');
    print('  Session ID: $sessionID');
    print('  Prompt: $prompt');

    final ffApiRequestBody = '''
{
  "prompt": "$prompt",
  "sessionID": "$sessionID"
}''';
    
    try {
      final response = await ApiManager.instance.makeApiCall(
        callName: 'GetAgentResponse',
        apiUrl: '$webhookURL',
        callType: ApiCallType.POST,
        headers: {
          'Authorization': '$webhookAuthValue',
        },
        params: {},
        body: ffApiRequestBody,
        bodyType: BodyType.JSON,
        returnBody: true,
        encodeBodyUtf8: false,
        decodeUtf8: false,
        cache: false,
        isStreamingApi: false,
        alwaysAllowBody: false,
      );
      
      // Log the response for debugging
      print('GetAgentResponseCall - Response:');
      print('  Status Code: ${response.statusCode}');
      print('  Success: ${response.succeeded}');
      print('  Body: ${response.bodyText}');
      
      // Log the extracted fields
      final extractedText = text(response.jsonBody);
      final extractedSpeech = speech(response.jsonBody);
      print('  Extracted Text: $extractedText');
      print('  Extracted Speech: $extractedSpeech');
      
      return response;
    } catch (e) {
      print('GetAgentResponseCall - Error: $e');
      rethrow;
    }
  }

  static dynamic text(dynamic response) {
    try {
      final result = getJsonField(
        response,
        r'''$.response.text''',
      );
      return result;
    } catch (e) {
      print('Error extracting text from response: $e');
      print('Response structure: $response');
      return null;
    }
  }
  
  static dynamic speech(dynamic response) {
    try {
      final result = getJsonField(
        response,
        r'''$.response.speech''',
      );
      return result;
    } catch (e) {
      print('Error extracting speech from response: $e');
      print('Response structure: $response');
      return null;
    }
  }
}

class ApiPagingParams {
  int nextPageNumber = 0;
  int numItems = 0;
  dynamic lastResponse;

  ApiPagingParams({
    required this.nextPageNumber,
    required this.numItems,
    required this.lastResponse,
  });

  @override
  String toString() =>
      'PagingParams(nextPageNumber: $nextPageNumber, numItems: $numItems, lastResponse: $lastResponse,)';
}

String _toEncodable(dynamic item) {
  return item;
}

String _serializeList(List? list) {
  list ??= <String>[];
  try {
    return json.encode(list, toEncodable: _toEncodable);
  } catch (_) {
    if (kDebugMode) {
      print("List serialization failed. Returning empty list.");
    }
    return '[]';
  }
}

String _serializeJson(dynamic jsonVar, [bool isList = false]) {
  jsonVar ??= (isList ? [] : {});
  try {
    return json.encode(jsonVar, toEncodable: _toEncodable);
  } catch (_) {
    if (kDebugMode) {
      print("Json serialization failed. Returning empty json.");
    }
    return isList ? '[]' : '{}';
  }
}
