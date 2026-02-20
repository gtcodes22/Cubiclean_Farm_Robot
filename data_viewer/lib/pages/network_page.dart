//import 'package:data_viewer/main.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../socket_service.dart';
import '../packet.dart';

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

  void _serverConnect() {
    return;
  }

  void _sendMsg() {
    String message = myController.text;
    myController.clear();
    widget.socketService.sendMessage(message, noNewLine: false);

  }

  Widget _formatMessage(PacketMessage packet, int num) {
    // ignore: prefer_interpolation_to_compose_strings
    String message = "$num: " + packet.getData();
    var mColour = Colors.amber[600];

    switch (packet.getSRC()) {
      case 'SPC':
        mColour = const Color.fromARGB(255, 0, 208, 255);
        break;
      case 'RPI':
        mColour = const Color.fromARGB(255, 255, 0, 102);
        break;
      default:
        mColour = Colors.amber[600];
    }

    return Container(
        height: 50,
        color: mColour,
          child: Center(child: Text(message)),
      );
  }

  @override
  Widget build(BuildContext context) {
    List<Widget> widgetChildren = [];

    for (int i = 0; i < widget.socketService.totalMessages(); i++) {
      widgetChildren.add(_formatMessage(widget.socketService.getMessage(i), i));
    }

    Widget netMsg = ListView(
      padding: const EdgeInsets.all(8),
      children: widgetChildren,
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
              spacing: 20,
              children: [
                //ElevatedButton(onPressed: _getMessage, child: const Text('Refresh')),
                Expanded(
                  child: Form(
                    child: TextFormField(
                      // https://stackoverflow.com/questions/72153633/flutter-submit-textformfield-on-enter
                      onFieldSubmitted: (value) { _serverConnect(); },
                      controller: addrTextController,
                      decoration: InputDecoration(
                      border: OutlineInputBorder(),
                      hintText: 'Server IP:Port',
                      ),
                    ),
                  )
                ),
                ElevatedButton(onPressed: _serverConnect, child: widget.socketService.connected() ? const Text('Disconnect') : Text('Connect')),
              ],
            ),
          ),
        ]
      )
    );
  }
}