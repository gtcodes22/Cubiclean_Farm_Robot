import 'package:flutter/material.dart';
import 'packet.dart';
import 'dart:io';
import 'dart:convert';
//import 'dart:async';

class SocketService {
  bool isConnected = false;
  Socket? socket;
  List<PacketMessage> messages = [];
  ValueNotifier<bool>? newMessageNotifier;

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
        newMessageNotifier?.value = true;
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

    // create a new packet message to send, with the data as the message string
    PacketMessage packet = PacketMessage.newPacket('APP', 'SPC', 'MSG', message);

    // for now, just send the data as a string, but in the future we can
    // change this to send the whole packet as bytes
    socket?.add(utf8.encode(message + (noNewLine ? '' : '\r\n') ));
    socket?.flush();

    debugPrint("Sent network message");
    messages.add(packet);
  }

  void setNewMessageNotifier(ValueNotifier<bool> notifier) {
    // This method would be used to set a notifier that can be used to update UI elements
    // when new messages are received. For example, it could be passed to the network page
    // so that it knows when to rebuild its list of messages.
    newMessageNotifier = notifier;
  }

  void dispose() {
    socket?.close();
    isConnected = false;
  }
}