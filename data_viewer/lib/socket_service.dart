import 'package:flutter/material.dart';
import 'dart:io';
import 'dart:convert';
import 'dart:async';

import 'main.dart';

class SocketService {
  bool isConnected = false;
  Socket? _socket;

  void initializeSocket(List<String> recMessages) async {
  // Configure the socket connection
  
    var address = InternetAddress.loopbackIPv4;
    int port = 8002;

    Socket socket = await Socket.connect(address, port);
    isConnected = true;
    _socket = socket;

    socket.listen(
      (dynamic message) {
        // from: https://stackoverflow.com/questions/28565242/convert-uint8list-to-string-with-dart
        String sMessage = String.fromCharCodes(message);
        debugPrint("Recieved message: " + sMessage);
        recMessages.add(sMessage);
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

  void sendMessage(String message) {
    if (!isConnected) {
      debugPrint("not connected, can't send message");
      return;
    }
    _socket?.add(utf8.encode(message));
    _socket?.flush();
  }

  void dispose() {
    _socket?.close();
  }
}