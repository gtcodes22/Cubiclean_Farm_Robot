//import 'package:data_viewer/main.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../socket_service.dart';

// Simple test function to check a widget is working as intended.
void testClick() {
  if (kDebugMode) {debugPrint('Click');}
}

class MyNetworkPage extends StatefulWidget {
  final String title;
  final ValueChanged<String> addrChange;
  final List<String> netMessages;
  const MyNetworkPage({
    super.key, required this.title, required this.addrChange,
    required this.netMessages
  });

  static const testImage = Image(image: AssetImage('test.bmp'),);

  @override
  State<MyNetworkPage> createState() => _MyNetworkPageState();

  void addMsg(String message) {
    _MyNetworkPageState()._addMsg(netMsg: message);
  }

}

class _MyNetworkPageState extends State<MyNetworkPage> {
  //late Socket _socket;
  //bool isConnected = false;
  final myController = TextEditingController();
  final addrTextController = TextEditingController();
  //static List messages = [];

  // from: https://stackoverflow.com/questions/69464611/how-can-i-connect-to-tcp-socket-not-web-socket-in-flutter
  // from: https://docs.flutter.dev/cookbook/networking/web-sockets#complete-example
  /*
  
  void _connectToServer(String IP, int port) async {
    _socket = await Socket.connect(IP, port);
    // from: https://stackoverflow.com/questions/72789853/how-to-check-if-the-tcp-socket-is-still-connected-in-flutter
    isConnected = true;
    
    //
  }

  // get contents of connect text and convert it into an ip address and port
  void _serverConnect() {
    List<String> word = addrTextController.text.split(":");
    String ipAddr = word[0];
    int port = int.parse(word[1]);
    print('connecting to ' + ipAddr + ":" + port.toString());
    _connectToServer(ipAddr, port);
  }

  void _getMessages() async {
    String msg;

    // listen to the received data event stream
    _socket.listen((List<int> event) {
      msg = utf8.decode(event);
      print("got: " + msg);
      _addMsg(netMsg: msg);
      return;
    });
  }
  
  void _sendMessage(String msg) async {
    _socket.add(utf8.encode(msg));
    _socket.flush();
  }

  void _disconnectFromServer() async {
      _socket.close();
  }
  */

  /*
  void _getMessage() {
    //while (netMessages.isNotEmpty) { _addMsg(netMsg:netMessages.removeLast()); }
    for (int i = 0; i < widget.netMessages.length; i++) {
      _addMsg(netMsg: widget.netMessages[i]);
    }
  }
  */

  void _sendMessage(String msg) async {
    SocketService.sendMessage(msg);
  }

  void _serverConnect() {
    //SocketService().initializeSocket(addrTextController.text), widget.netMessages);
    //widget.parent.widget.serverConnect(addrTextController.text);
    widget.addrChange(addrTextController.text);
  }

  Widget _formatMessage(String origMessage, int i) {
    String src;
    try {
      src = origMessage.substring(0, origMessage.indexOf(':')); 
    } on RangeError catch (_) {
      src = 'PC';
    }

    String message = origMessage.substring(origMessage.indexOf(':') + 1);
    //String des = message.endsWith("@PC") ? "[PC] " : "[APP] ";
    var mColour = Colors.amber[600];

    switch (src) {
      case 'PC':
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
          child: Center(child: Text("$i : $message")),
      );
  }

  void _addMsg({String netMsg = ""}) {
    String msg;
    
    if (myController.text == "" && netMsg == "") { return; }

    // add counter to message 
    setState(() {
      if (netMsg != "") {
        msg = 'PC:$netMsg';
      } else {
        msg = 'APP:${myController.text}';
        myController.clear();
        _sendMessage(msg);
        testClick();
      }

      // add message to message log widget and update widget
      setState(() {
         widget.netMessages.add(msg);
       });
    });
  }

  @override
  Widget build(BuildContext context) {
    List<Widget> widgetChildren = [];
    int numberOfMessages = widget.netMessages.length;

    for (int i = 0; i < numberOfMessages; i++) {
      widgetChildren.add(_formatMessage(widget.netMessages[i], i));
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
                      onFieldSubmitted: (value) { _addMsg(); },
                      controller: myController,
                      decoration: InputDecoration(
                      border: OutlineInputBorder(),
                      hintText: 'Enter message to send to server',
                      ),
                    ),
                  )
                ),
                ElevatedButton(onPressed: _addMsg, child: const Text('Send')),
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
                ElevatedButton(onPressed: _serverConnect, child: const Text('Connect')),
              ],
            ),
          ),
        ]
      )
    );
  }
}