import 'package:flutter/material.dart';
import 'dart:io';
import 'dart:convert';
import 'dart:async';

import 'main.dart';

class SocketService {
  static bool isConnected = false;
  static Socket? _socket;

  static Socket? getSocket() => _socket;
  static bool connected() => isConnected;

  void initializeSocket(String ipPort, List<String> recMessages, VoidCallback getMessage) async {
  // Configure the socket connection
    
    var address = InternetAddress.loopbackIPv4;
    int port = 8002;

    if (ipPort.isNotEmpty) {
      List<String> words = ipPort.split(':');
      address = InternetAddress(words[0]);
      port = int.parse(words[1]);
    }

    Socket socket = await Socket.connect(address, port);
    isConnected = true;
    _socket = socket;

    socket.listen(
      (dynamic message) {
        // from: https://stackoverflow.com/questions/28565242/convert-uint8list-to-string-with-dart
        String sMessage = String.fromCharCodes(message);
        debugPrint("Recieved message: " + sMessage);

        // add incoming message to the received messages list
        recMessages.add(sMessage);

        // calling this updates the NetworkPageState with the new received message
        getMessage();
      },
      onDone: () {
        isConnected = false;
        debugPrint("socket closed");
      },
      onError: (error) {
        isConnected = false;
        debugPrint('error $error');
      },
    );
  }

  static void sendMessage(String message, {bool noNewLine = false}) {
    if (!isConnected) {
      debugPrint("not connected, can't send message");
      return;
    }
    _socket?.add(utf8.encode(message + (noNewLine ? '' : '\r\n') ));
    _socket?.flush();
  }

  void dispose() {
    _socket?.close();
  }
}