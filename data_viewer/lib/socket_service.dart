import 'dart:typed_data';

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
    List<int> buffer = Uint8List(0);

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

    // send initial confirm message
    sendMessage('Hello TCP Server :)');

    // listen for messages
    socket?.listen(
      (dynamic message) {
        debugPrint("Recieved network message");
        
        buffer = [...buffer, ...message as Uint8List];

        // TODO: handle if different packets are received at once
        if (PacketMessage.bValidPacket(buffer)) {
          debugPrint("Received complete packet message");
          messages.add(PacketMessage(buffer));
          newMessageNotifier?.value = true;

          // clear buffer for next message
          buffer = Uint8List(0);
        } else {
          debugPrint("Received incomplete packet message: ${buffer.length}/${PacketMessage.iLength(buffer)} bytes");
        }
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

  void sendMessage(String message, {bool plainTextMessage = false}) {
    String plainMessage = '$message\r\n';
    if (!isConnected) {
      debugPrint("not connected, can't send message");
      return;
    }

    // create a new packet message to send, with the data as the message string
    PacketMessage packet = PacketMessage.newPacket('APP', 'SPC', 'MSG', message);

    // if the plain text option is selected, send the message as plain text,
    // otherwise send it in the proper format instead
    socket?.add(plainTextMessage ? utf8.encode(plainMessage) : packet.getSocketBytes());
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