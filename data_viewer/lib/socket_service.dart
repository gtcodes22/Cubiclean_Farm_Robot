import 'package:flutter/material.dart';
import 'packet.dart';
import 'dart:io';
import 'dart:convert';
//import 'dart:async';

class SocketService {
  static bool isConnected = false;
  static Socket? socket;
  List<PacketMessage> messages = [];

  SocketService();

  Socket? getSocket() => socket;
  bool connected() => isConnected;
  PacketMessage getMessage(int i) => messages[i];
  List<PacketMessage> getMessages() => messages;
  int totalMessages() => messages.length;

  void connectToServer(String ipPort) async {
    // default server ip address and port
    var address = InternetAddress.loopbackIPv4;
    int port = 1991;

    // if an address is specified, use that rather than the default
    if (ipPort.isNotEmpty) {
      List<String> words = ipPort.split(':');
      address = InternetAddress(words[0]);
      port = int.parse(words[1]);
    }

    // if an exisiting connection is still open, close it
    if (connected()) {dispose();}

    // open socket
    socket = await Socket.connect(address, port);
    isConnected = true;

    // listen for messages
    socket?.listen(
      (dynamic message) {
        // add incoming message to the received messages list
        messages.add(PacketMessage(message));
        debugPrint("Recieved network message");
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

  void sendMessage(String message, {bool noNewLine = false}) {
    if (!isConnected) {
      debugPrint("not connected, can't send message");
      return;
    }
    socket?.add(utf8.encode(message + (noNewLine ? '' : '\r\n') ));
    socket?.flush();
  }



  void dispose() {
    socket?.close();
    isConnected = false;
  }
}