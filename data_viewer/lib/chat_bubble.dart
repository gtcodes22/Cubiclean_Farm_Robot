// Shameless stolen and adapted from: https://maxim-gorin.medium.com/advanced-flutter-ui-how-to-build-a-chat-app-with-custom-message-bubbles-4f90282b8be0
import 'package:flutter/material.dart';
import 'packet.dart';

class ChatBubble extends StatelessWidget {
  final PacketMessage packet;
  final String mType;
  final String data;
  final bool isSentByMe;
  final bool isBot;

  ChatBubble({required this.packet}) :
    mType = packet.getType(),
    data = packet.getData(),
    isSentByMe = packet.getSRC() == 'APP',
    isBot = packet.getSRC() == 'RPI';
  
  @override
  Widget build(BuildContext context) {
    Widget textMessage = Text(
              data,
              style: TextStyle(
                color: Colors.white,//isSentByMe ? Colors.white : Colors.black87,
              ),
              softWrap: true,  // Ensures line breaks are handled properly
            );

    return Align(
      alignment: isSentByMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 5, horizontal: 10),
        padding: EdgeInsets.all(10),
        constraints: BoxConstraints(maxWidth: 400),
        decoration: BoxDecoration(
          color: isSentByMe ? Colors.lightGreen : isBot ? Colors.red : Colors.lightBlue,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(15),
            topRight: Radius.circular(15),
            bottomLeft: isSentByMe ? Radius.circular(15) : Radius.zero,
            bottomRight: isSentByMe ? Radius.zero : Radius.circular(15),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black26,
              blurRadius: 5,
            ),
          ],
        ),
        child: Column(
          children: [
            Align(
              alignment: isSentByMe ? Alignment.centerRight : Alignment.centerLeft,
            child: Text(
              isSentByMe ? "Data Viewer": isBot ? "Robot": "TCP Server",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                //decoration: TextDecoration.underline,
                fontSize: 10,
                color: Colors.white,
                ),
              ),
            ),
            mType == 'MSG' ? textMessage : Image(image: packet.getImageData(), height: 200),
          ],
        ),
        /*
        child: Text(
          message,
          style: TextStyle(
            color: Colors.white,//isSentByMe ? Colors.white : Colors.black87,
          ),
          softWrap: true,  // Ensures line breaks are handled properly
        ),
        */
      ),
    );
  }
}