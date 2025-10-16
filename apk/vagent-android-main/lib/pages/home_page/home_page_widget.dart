import '/backend/api_requests/api_calls.dart';
import '/backend/schema/structs/index.dart';
import '/components/menu/menu_widget.dart';
import '/components/message_bubbles/message_bubbles_widget.dart';
import '/components/settings/settings_widget.dart';
import '/flutter_flow/flutter_flow_icon_button.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_timer.dart';
import '/flutter_flow/flutter_flow_util.dart';
import 'dart:async';
import 'dart:math';
import '/custom_code/actions/index.dart' as actions;
import '/custom_code/actions/fetch_speech_and_play.dart';
import 'package:stop_watch_timer/stop_watch_timer.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:lottie/lottie.dart';
import 'package:provider/provider.dart';
import 'home_page_model.dart';
export 'home_page_model.dart';

class HomePageWidget extends StatefulWidget {
  const HomePageWidget({super.key});

  @override
  State<HomePageWidget> createState() => _HomePageWidgetState();
}

class _HomePageWidgetState extends State<HomePageWidget> {
  late HomePageModel _model;

  final scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  void initState() {
    super.initState();
    _model = createModel(context, () => HomePageModel());

    // On page load action.
    SchedulerBinding.instance.addPostFrameCallback((_) async {
      if (FFAppState().sessionID == '') {
        await actions.generateSessionID();
      }
    });

    WidgetsBinding.instance.addPostFrameCallback((_) => safeSetState(() {}));
  }

  @override
  void dispose() {
    _model.dispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    context.watch<FFAppState>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        key: scaffoldKey,
        backgroundColor: FlutterFlowTheme.of(context).primaryBackground,
        appBar: PreferredSize(
          preferredSize: const Size.fromHeight(0.0),
          child: AppBar(
            backgroundColor: FlutterFlowTheme.of(context).primaryBackground,
            automaticallyImplyLeading: false,
            actions: const [],
            centerTitle: true,
            elevation: 0.0,
          ),
        ),
        body: Column(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Flexible(
              child: Container(
                decoration: BoxDecoration(
                  color: FlutterFlowTheme.of(context).primaryBackground,
                ),
                child: Padding(
                  padding: const EdgeInsetsDirectional.fromSTEB(10.0, 0.0, 10.0, 0.0),
                  child: Builder(
                    builder: (context) {
                      final msg = FFAppState().messageHistory.toList();

                      return ListView.separated(
                        padding: const EdgeInsets.fromLTRB(
                          0,
                          10.0,
                          0,
                          10.0,
                        ),
                        shrinkWrap: true,
                        scrollDirection: Axis.vertical,
                        itemCount: msg.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 10.0),
                        itemBuilder: (context, msgIndex) {
                          final msgItem = msg[msgIndex];
                          return Container(
                            child: MessageBubblesWidget(
                              key: Key('Keyjml_${msgIndex}_of_${msg.length}'),
                              messageText: msgItem.text,
                              blueBubble: msgItem.blueBubble,
                            ),
                          );
                        },
                        controller: _model.listViewController,
                      );
                    },
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 2.0),
              child: Container(
                decoration: const BoxDecoration(),
                child: Stack(
                  children: [
                    Container(
                      width: MediaQuery.sizeOf(context).width * 1.0,
                      height: 180.0,
                      decoration: const BoxDecoration(),
                      child: Padding(
                        padding: const EdgeInsetsDirectional.fromSTEB(
                            24.0, 0.0, 24.0, 0.0),
                        child: Row(
                          mainAxisSize: MainAxisSize.max,
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Padding(
                              padding: const EdgeInsetsDirectional.fromSTEB(
                                  0.0, 0.0, 0.0, 36.0),
                              child: Column(
                                mainAxisSize: MainAxisSize.max,
                                mainAxisAlignment: MainAxisAlignment.end,
                                children: [
                                  FlutterFlowIconButton(
                                    borderRadius: 8.0,
                                    buttonSize: 40.0,
                                    disabledIconColor: const Color(0xFFAFAFAF),
                                    icon: FaIcon(
                                      FontAwesomeIcons.cog,
                                      color: FlutterFlowTheme.of(context).info,
                                      size: 24.0,
                                    ),
                                    onPressed: (_model.isRecording ||
                                            _model.isTranscribing)
                                        ? null
                                        : () async {
                                            await showModalBottomSheet(
                                              isScrollControlled: true,
                                              backgroundColor:
                                                  Colors.transparent,
                                              context: context,
                                              builder: (context) {
                                                return GestureDetector(
                                                  onTap: () =>
                                                      FocusScope.of(context)
                                                          .unfocus(),
                                                  child: Padding(
                                                    padding:
                                                        MediaQuery.viewInsetsOf(
                                                            context),
                                                    child: const SettingsWidget(),
                                                  ),
                                                );
                                              },
                                            ).then(
                                                (value) => safeSetState(() {}));
                                          },
                                  ),
                                ],
                              ),
                            ),
                            if (!_model.showWaveform)
                              Column(
                                mainAxisSize: MainAxisSize.max,
                                children: [
                                  SizedBox(
                                    width: 150.0,
                                    height: 150.0,
                                    child: Stack(
                                      alignment: const AlignmentDirectional(0.0, 0.0),
                                      children: [
                                        if (!(_model.isRecording ||
                                            _model.isTranscribing))
                                          FlutterFlowIconButton(
                                            borderRadius: 100.0,
                                            buttonSize: 120.0,
                                            fillColor: const Color(0xFF131313),
                                            icon: Icon(
                                              Icons.mic_rounded,
                                              color:
                                                  FlutterFlowTheme.of(context)
                                                      .info,
                                              size: 60.0,
                                            ),
                                            showLoadingIndicator: true,
                                            onPressed: () async {
                                              var shouldSetState = false;
                                              _model.settingsOK = await actions
                                                  .validateSettings();
                                              shouldSetState = true;
                                              if (!_model.settingsOK!) {
                                                await showModalBottomSheet(
                                                  isScrollControlled: true,
                                                  backgroundColor:
                                                      Colors.transparent,
                                                  context: context,
                                                  builder: (context) {
                                                    return GestureDetector(
                                                      onTap: () =>
                                                          FocusScope.of(context)
                                                              .unfocus(),
                                                      child: Padding(
                                                        padding: MediaQuery
                                                            .viewInsetsOf(
                                                                context),
                                                        child: const SettingsWidget(),
                                                      ),
                                                    );
                                                  },
                                                ).then((value) =>
                                                    safeSetState(() {}));

                                                if (shouldSetState) {
                                                  safeSetState(() {});
                                                }
                                                return;
                                              }
                                              unawaited(
                                                () async {
                                                  await actions
                                                      .startTextRecording();
                                                }(),
                                              );
                                              _model.isRecording = true;
                                              safeSetState(() {});
                                              if (shouldSetState) {
                                                safeSetState(() {});
                                              }
                                            },
                                          ),
                                        if (_model.isRecording)
                                          Align(
                                            alignment:
                                                const AlignmentDirectional(0.0, 0.0),
                                            child: InkWell(
                                              splashColor: Colors.transparent,
                                              focusColor: Colors.transparent,
                                              hoverColor: Colors.transparent,
                                              highlightColor:
                                                  Colors.transparent,
                                              onTap: () async {
                                                var shouldSetState = false;
                                                // Recording stopped
                                                _model.isRecording = false;
                                                // Transcription started
                                                _model.isTranscribing = true;
                                                safeSetState(() {});
                                                // Run STT
                                                _model.recordingError =
                                                    await actions
                                                        .stopTextRecording();
                                                shouldSetState = true;
                                                if (!getJsonField(
                                                  _model.recordingError,
                                                  r'''$.success''',
                                                )) {
                                                  ScaffoldMessenger.of(context)
                                                      .showSnackBar(
                                                    SnackBar(
                                                      content: Text(
                                                        getJsonField(
                                                          _model.recordingError,
                                                          r'''$.message''',
                                                        ).toString(),
                                                        style: TextStyle(
                                                          color: FlutterFlowTheme
                                                                  .of(context)
                                                              .primaryText,
                                                        ),
                                                      ),
                                                      duration: const Duration(
                                                          milliseconds: 5000),
                                                      backgroundColor:
                                                          FlutterFlowTheme.of(
                                                                  context)
                                                              .error,
                                                    ),
                                                  );
                                                  if (shouldSetState) {
                                                    safeSetState(() {});
                                                  }
                                                  return;
                                                }
                                                // Store STT result
                                                _model.queryText = FFAppState()
                                                    .speechToTextResponse;
                                                safeSetState(() {});
                                                // Add blue bubble with STT result
                                                FFAppState()
                                                    .addToMessageHistory(
                                                        MessageStruct(
                                                  text: FFAppState()
                                                      .speechToTextResponse,
                                                  blueBubble: true,
                                                ));
                                                safeSetState(() {});
                                                // Wait for UI elements
                                                await Future.delayed(
                                                    const Duration(
                                                        milliseconds: 100));
                                                // Scroll bubbles
                                                await _model.listViewController
                                                    ?.animateTo(
                                                  _model.listViewController!
                                                      .position.maxScrollExtent,
                                                  duration: const Duration(
                                                      milliseconds: 100),
                                                  curve: Curves.ease,
                                                );
                                                // Call webhook
                                                print('Calling webhook with prompt: ${FFAppState().speechToTextResponse}');
                                                try {
                                                  _model.getResponseAPICall =
                                                      await GetAgentResponseCall
                                                          .call(
                                                    prompt: FFAppState()
                                                        .speechToTextResponse,
                                                    webhookURL:
                                                        FFAppState().webhookURL,
                                                    webhookAuthValue: FFAppState()
                                                        .webhookAuthValue,
                                                    sessionID:
                                                        FFAppState().sessionID,
                                                  );

                                                  shouldSetState = true;
                                                  print('Webhook call completed. Success: ${_model.getResponseAPICall?.succeeded}');
                                                  
                                                  if (_model.getResponseAPICall == null) {
                                                    print('Error: API call response is null');
                                                    ScaffoldMessenger.of(context).showSnackBar(
                                                      SnackBar(
                                                        content: Text(
                                                          'Error: No response from webhook',
                                                          style: TextStyle(
                                                            color: FlutterFlowTheme.of(context).primaryText,
                                                          ),
                                                        ),
                                                        duration: const Duration(milliseconds: 5000),
                                                        backgroundColor: FlutterFlowTheme.of(context).error,
                                                      ),
                                                    );
                                                    return;
                                                  }
                                                  
                                                  if (_model.getResponseAPICall!.succeeded) {
                                                    // Extract text and speech from response
                                                    final responseText = GetAgentResponseCall.text(
                                                      _model.getResponseAPICall!.jsonBody,
                                                    );
                                                    final responseSpeech = GetAgentResponseCall.speech(
                                                      _model.getResponseAPICall!.jsonBody,
                                                    );
                                                    
                                                    print('Response text: $responseText');
                                                    print('Response speech: $responseSpeech');
                                                    
                                                    if (responseText == null || responseSpeech == null) {
                                                      print('Error: Response text or speech is null');
                                                      print('Response body: ${_model.getResponseAPICall!.bodyText}');
                                                      
                                                      ScaffoldMessenger.of(context).showSnackBar(
                                                        SnackBar(
                                                          content: Text(
                                                            'Error: Invalid response format. Expected "response.text" and "response.speech" fields.',
                                                            style: TextStyle(
                                                              color: FlutterFlowTheme.of(context).primaryText,
                                                            ),
                                                          ),
                                                          duration: const Duration(milliseconds: 5000),
                                                          backgroundColor: FlutterFlowTheme.of(context).error,
                                                        ),
                                                      );
                                                      return;
                                                    }
                                                    
                                                    // Add grey bubble to conversation with the response text
                                                    FFAppState().addToMessageHistory(
                                                      MessageStruct(
                                                        text: responseText.toString(),
                                                      )
                                                    );
                                                    safeSetState(() {});
                                                    
                                                    // Wait for UI elements
                                                    await Future.delayed(
                                                      const Duration(milliseconds: 100)
                                                    );
                                                    
                                                    // Scroll bubbles
                                                    await _model.listViewController?.animateTo(
                                                      _model.listViewController!.position.maxScrollExtent,
                                                      duration: const Duration(milliseconds: 100),
                                                      curve: Curves.ease,
                                                    );
                                                    
                                                    // Calculate wave effect duration based on speech length
                                                    int waveDuration = 6000; // Base duration: 6 seconds for messages under 60 chars
                                                    
                                                    // Get the message length from the speech field (for calculating duration)
                                                    final speechLength = responseSpeech.toString().length;
                                                    print('Speech length: $speechLength characters');
                                                    
                                                    // For every 60 characters, show wave effect for 6 seconds
                                                    // For every additional 12 characters beyond 60, add 1 extra second
                                                    if (speechLength > 60) {
                                                      final additionalChars = speechLength - 60;
                                                      final additionalSeconds = (additionalChars / 12).ceil();
                                                      waveDuration += additionalSeconds * 1000;
                                                    }
                                                    
                                                    // Set a maximum duration to ensure the wave effect stops
                                                    waveDuration = min(waveDuration, 60000); // Maximum 60 seconds
                                                    
                                                    print('Calculated wave duration: $waveDuration ms');
                                                    
                                                    // Keep spinning for 6 seconds after receiving JSON response
                                                    print('Keeping spinning effect for 6 seconds');
                                                    await Future.delayed(const Duration(seconds: 6));
                                                    
                                                    // Stop the spinning circle and start the wave effect
                                                    _model.isTranscribing = false;
                                                    
                                                    // Run TTS for webhook response
                                                    try {
                                                      print('Starting speech playback and wave effect');
                                                      
                                                      // Reset the timer controller
                                                      _model.timerController.onResetTimer();
                                                      
                                                      // Set timer value to calculated duration
                                                      FFAppState().timerValue = waveDuration;
                                                      FFAppState().speechToTextResponse = '';
                                                      
                                                      // Show waveform
                                                      _model.showWaveform = true;
                                                      safeSetState(() {});
                                                      
                                                      // Start timer
                                                      _model.timerController.onStartTimer();
                                                      
                                                      // Also set a backup timer to ensure the wave effect stops
                                                      Future.delayed(Duration(milliseconds: waveDuration + 1000), () {
                                                        if (_model.showWaveform) {
                                                          print('Backup timer stopping wave effect');
                                                          _model.showWaveform = false;
                                                          _model.timerController.onResetTimer();
                                                          safeSetState(() {});
                                                        }
                                                      });
                                                      
                                                      // Start audio playback in background using the speech field
                                                      unawaited(
                                                        () async {
                                                          try {
                                                            await actions.fetchSpeechAndPlay(
                                                              responseSpeech.toString(), // Use speech field for audio
                                                              FFAppState().apiKey,
                                                            );
                                                            
                                                            // After audio playback completes, ensure wave effect stops
                                                            if (_model.showWaveform) {
                                                              print('Audio playback completed, stopping wave effect');
                                                              _model.showWaveform = false;
                                                              _model.timerController.onResetTimer();
                                                              safeSetState(() {});
                                                            }
                                                          } catch (e) {
                                                            print('Error playing speech: $e');
                                                            
                                                            // If there's an error, also ensure wave effect stops
                                                            if (_model.showWaveform) {
                                                              print('Error in audio playback, stopping wave effect');
                                                              _model.showWaveform = false;
                                                              _model.timerController.onResetTimer();
                                                              safeSetState(() {});
                                                            }
                                                          }
                                                        }(),
                                                      );
                                                    } catch (e) {
                                                      print('Error playing speech: $e');
                                                      // Still add the text bubble even if speech fails
                                                      _model.isTranscribing = false;
                                                      safeSetState(() {});
                                                      
                                                      // Add grey bubble to conversation
                                                      FFAppState()
                                                          .addToMessageHistory(
                                                              MessageStruct(
                                                        text: responseText.toString(),
                                                      ));
                                                      safeSetState(() {});
                                                      
                                                      // Show error message
                                                      ScaffoldMessenger.of(context).showSnackBar(
                                                        SnackBar(
                                                          content: Text(
                                                            'Error playing speech: $e',
                                                            style: TextStyle(
                                                              color: FlutterFlowTheme.of(context).primaryText,
                                                            ),
                                                          ),
                                                          duration: const Duration(milliseconds: 5000),
                                                          backgroundColor: FlutterFlowTheme.of(context).error,
                                                        ),
                                                      );
                                                      
                                                      // Scroll bubbles
                                                      await _model
                                                          .listViewController
                                                          ?.animateTo(
                                                        _model
                                                            .listViewController!
                                                            .position
                                                            .maxScrollExtent,
                                                        duration: const Duration(
                                                            milliseconds: 100),
                                                        curve: Curves.ease,
                                                      );
                                                    }
                                                  } else {
                                                    // Display error message in UI
                                                    print('Webhook call failed: ${_model.getResponseAPICall?.statusCode}');
                                                    print('Error response: ${_model.getResponseAPICall?.bodyText}');
                                                    
                                                    _model.isTranscribing = false;
                                                    safeSetState(() {});
                                                    
                                                    ScaffoldMessenger.of(context)
                                                        .showSnackBar(
                                                      SnackBar(
                                                        content: Text(
                                                          'Webhook error (${_model.getResponseAPICall?.statusCode}): ${_model.getResponseAPICall?.bodyText}',
                                                          style: TextStyle(
                                                            color: FlutterFlowTheme
                                                                    .of(context)
                                                                .primaryText,
                                                          ),
                                                        ),
                                                        duration: const Duration(
                                                            milliseconds: 5000),
                                                        backgroundColor:
                                                            FlutterFlowTheme.of(
                                                                    context)
                                                                .error,
                                                      ),
                                                    );
                                                  }
                                                } catch (e) {
                                                  print('Exception during webhook call: $e');
                                                  _model.isTranscribing = false;
                                                  safeSetState(() {});
                                                  
                                                  ScaffoldMessenger.of(context).showSnackBar(
                                                    SnackBar(
                                                      content: Text(
                                                        'Error: $e',
                                                        style: TextStyle(
                                                          color: FlutterFlowTheme.of(context).primaryText,
                                                        ),
                                                      ),
                                                      duration: const Duration(milliseconds: 5000),
                                                      backgroundColor: FlutterFlowTheme.of(context).error,
                                                    ),
                                                  );
                                                }

                                                if (shouldSetState) {
                                                  safeSetState(() {});
                                                }
                                              },
                                              child: Lottie.asset(
                                                'assets/lottie_animations/Stop_Recording.json',
                                                width: 150.0,
                                                height: 150.0,
                                                fit: BoxFit.contain,
                                                animate: true,
                                              ),
                                            ),
                                          ),
                                        if (_model.isTranscribing)
                                          Align(
                                            alignment:
                                                const AlignmentDirectional(0.0, 0.0),
                                            child: Container(
                                              width: 120.0,
                                              height: 120.0,
                                              decoration: const BoxDecoration(
                                                color: Color(0xFF131313),
                                                shape: BoxShape.circle,
                                              ),
                                              child: Align(
                                                alignment: const AlignmentDirectional(
                                                    0.0, 0.0),
                                                child: Lottie.asset(
                                                  'assets/lottie_animations/Loading.json',
                                                  width: 120.0,
                                                  height: 120.0,
                                                  fit: BoxFit.contain,
                                                  animate: true,
                                                ),
                                              ),
                                            ),
                                          ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            Padding(
                              padding: const EdgeInsetsDirectional.fromSTEB(
                                  0.0, 0.0, 0.0, 36.0),
                              child: Column(
                                mainAxisSize: MainAxisSize.max,
                                mainAxisAlignment: MainAxisAlignment.end,
                                children: [
                                  FlutterFlowIconButton(
                                    borderRadius: 8.0,
                                    buttonSize: 40.0,
                                    disabledIconColor: const Color(0xFFAFAFAF),
                                    icon: FaIcon(
                                      FontAwesomeIcons.ellipsisV,
                                      color: FlutterFlowTheme.of(context).info,
                                      size: 24.0,
                                    ),
                                    onPressed: (_model.isRecording ||
                                            _model.isTranscribing)
                                        ? null
                                        : () async {
                                            await showModalBottomSheet(
                                              isScrollControlled: true,
                                              backgroundColor:
                                                  Colors.transparent,
                                              context: context,
                                              builder: (context) {
                                                return GestureDetector(
                                                  onTap: () =>
                                                      FocusScope.of(context)
                                                          .unfocus(),
                                                  child: Padding(
                                                    padding:
                                                        MediaQuery.viewInsetsOf(
                                                            context),
                                                    child: const MenuWidget(),
                                                  ),
                                                );
                                              },
                                            ).then(
                                                (value) => safeSetState(() {}));
                                          },
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    if (_model.showWaveform)
                      InkWell(
                        splashColor: Colors.transparent,
                        focusColor: Colors.transparent,
                        hoverColor: Colors.transparent,
                        highlightColor: Colors.transparent,
                        onTap: () async {
                          await actions.interruptSpeech();
                          _model.isRecording = false;
                          _model.showWaveform = false;
                          safeSetState(() {});
                          _model.timerController.onStopTimer();
                        },
                        child: Lottie.asset(
                          'assets/lottie_animations/Animation_-_1700152506198.json',
                          width: MediaQuery.sizeOf(context).width * 1.0,
                          height: 160.0,
                          fit: BoxFit.fill,
                          animate: true,
                        ),
                      ),
                    if (_model.showWaveform)
                      FlutterFlowTimer(
                        initialTime: valueOrDefault<int>(
                          FFAppState().timerValue,
                          1000,
                        ),
                        getDisplayTime: (value) =>
                            StopWatchTimer.getDisplayTime(
                          value,
                          hours: false,
                          minute: false,
                          milliSecond: false,
                        ),
                        controller: _model.timerController,
                        updateStateInterval: const Duration(milliseconds: 1000),
                        onChanged: (value, displayTime, shouldUpdate) {
                          _model.timerMilliseconds = value;
                          _model.timerValue = displayTime;
                          if (shouldUpdate) safeSetState(() {});
                        },
                        onEnded: () async {
                          _model.timerController.onResetTimer();

                          _model.showWaveform = false;
                          safeSetState(() {});
                        },
                        textAlign: TextAlign.start,
                        style:
                            FlutterFlowTheme.of(context).headlineSmall.override(
                                  fontFamily: 'Outfit',
                                  color: const Color(0x00FFFFFF),
                                  fontSize: 2.0,
                                  letterSpacing: 0.0,
                                ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
