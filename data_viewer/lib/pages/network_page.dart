//import 'package:data_viewer/main.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../socket_service.dart';
import '../packet.dart';
import '../chat_bubble.dart';

// Simple test function to check a widget is working as intended.
void testClick() {
  if (kDebugMode) {debugPrint('Click');}
}

class MyNetworkPage extends StatefulWidget {
  final String title;
  final SocketService socketService;
  const MyNetworkPage({super.key, required this.title, required this.socketService});

  static const testImage = Image(image: AssetImage('test.bmp'),);

  @override
  State<MyNetworkPage> createState() => _MyNetworkPageState();

}

class _MyNetworkPageState extends State<MyNetworkPage> {
  final myController = TextEditingController();
  final addrTextController = TextEditingController();
  ValueNotifier<bool> updateWidget = ValueNotifier(false);
  bool plainTextMessages = false;

  void _serverConnect() {
    setState(() {
      if (widget.socketService.connected()) {
        widget.socketService.dispose();
      } else {
        widget.socketService.connectToServer(addrTextController.text);
      }
    });
  }

  void _sendMsg() {
    String message = myController.text;
    
    setState(() {
      myController.clear();
      widget.socketService.sendMessage(message, plainTextMessage: plainTextMessages);
    });
  }

  Widget _formatMessage(PacketMessage packet, int num) {
    // ignore: prefer_interpolation_to_compose_strings
    //String message = "[$num][${packet.getSRC()}]: " + packet.getData();
    /*
    var mColour = Colors.amber[600];

    switch (packet.getSRC()) {
      case 'SPC':
        mColour = const Color.fromARGB(255, 0, 208, 255);
        break;
      case 'RPI':
        mColour = const Color.fromARGB(255, 255, 0, 102);
        break;
      case 'APP':
        mColour = const Color.fromARGB(255, 0, 255, 102);
        break;
      case 'UNK':
        mColour = Colors.amber[600];
        break;
      default:
        mColour = Colors.amber[600];
    }
    
    return Container(
        height: 50,
        color: mColour,
          child: packet.getSRC() == 'APP' ? Center(child: Text(message)) : Center(child: Text(message)),
      );
      */
      return ChatBubble(packet: packet);
  }

  Widget buildMessageList() 
  {
    List<Widget> widgetChildren = [];
    for (int i = 0; i < widget.socketService.totalMessages(); i++) {
      widgetChildren.add(_formatMessage(widget.socketService.getMessage(i), i));
    }
    updateWidget.value = false;
    return ListView(
      padding: const EdgeInsets.all(8),
      children: widgetChildren,
      );
  }

  @override
  Widget build(BuildContext context) {
    addrTextController.text = '127.0.0.1:1991';
    widget.socketService.setNewMessageNotifier(updateWidget);

    Widget netMsg = ValueListenableBuilder<bool>(
      valueListenable: updateWidget,
      builder:(context, value, child) => buildMessageList(),
      child: null,
    );

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Column(
        children: [
          Expanded(child: netMsg),
          const Image(
            image: AssetImage('test.bmp'),
          ),
          Padding(
            padding: EdgeInsets.all(8),
            child: Row(
              spacing: 20,
              children: [
                Expanded(
                  child: Form(
                    child: TextFormField(
                      // https://stackoverflow.com/questions/72153633/flutter-submit-textformfield-on-enter
                      onFieldSubmitted: (value) { _sendMsg(); },
                      controller: myController,
                      decoration: InputDecoration(
                      border: OutlineInputBorder(),
                      hintText: 'Enter message to send to server',
                      ),
                    ),
                  )
                ),
                ElevatedButton(onPressed: _sendMsg, child: const Text('Send')),
              ],
            ),
          ),
          Padding(
            padding: EdgeInsets.all(8),
            child: Row(
              spacing: 00,
              children: [
                //ElevatedButton(onPressed: _getMessage, child: const Text('Refresh')),
                Expanded(
                  child: Form(
                    child: TextFormField(
                      // https://stackoverflow.com/questions/72153633/flutter-submit-textformfield-on-enter
                      onFieldSubmitted: (value) { _serverConnect(); },
                      controller: addrTextController,
                      readOnly: widget.socketService.connected() ? true : false,
                      style: TextStyle(
                        color: widget.socketService.connected() ? Colors.grey : Colors.black,
                      ),
                      decoration: InputDecoration(
                        border: OutlineInputBorder(),
                        hintText: 'Server IP:Port',

                      ),
                    ),
                  )
                ),
                Checkbox(checkColor: Colors.black, value: plainTextMessages, onChanged: (value) { setState(() {plainTextMessages = value!;}); },),
                Text('Send as plain text'),
                SizedBox(width: 10),
                ElevatedButton(onPressed: _serverConnect, child: widget.socketService.connected() ? const Text('Disconnect') : Text('Connect')),
              ],
            ),
          ),
        ]
      )
    );
  }
}