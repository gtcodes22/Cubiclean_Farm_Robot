import 'package:flutter/material.dart';
import 'dart:io';
import 'dart:convert';
import 'dart:async';

import 'socket_service.dart';

/** DO NOT RUN THIS PROGRAM VIA THE WEB APP DEBUGGER, AS THE DART:IO LIBRARY
 * IS NOT COMPATIBLE.
 */


void main() => runApp(const MyApp()); // run MyApp as the main program

// ignore: avoid_print
void testClick() => print('Click');

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  StatefulWidget build(BuildContext context) {
    //return networkMessenger(this);
    return MaterialApp(
      home: const MyNetworkPage(title: 'Network Test Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});
  
  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text('You have pushed the button this many times:'),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}

class MyNetworkPage extends StatefulWidget {
  const MyNetworkPage({super.key, required this.title});
  
  final String title;

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
  List messages = [];
  List<String> recMessages = [];
  int _counter = 0;

  // from: https://stackoverflow.com/questions/69464611/how-can-i-connect-to-tcp-socket-not-web-socket-in-flutter
  // from: https://docs.flutter.dev/cookbook/networking/web-sockets#complete-example
  /*
  // ignore: non_constant_identifier_names
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

  void _getMessage() {
    while (recMessages.isNotEmpty) { _addMsg(netMsg:recMessages.removeLast()); }
  }

  void _sendMessage(String msg) async {
    SocketService.sendMessage(msg);
  }

  void _serverConnect() async {
    SocketService().initializeSocket(addrTextController.text, recMessages, _getMessage);
  }

  Widget _formatMessage(String _message, int i) {
    String src = _message.substring(0, _message.indexOf(':'));
    String message = _message.substring(_message.indexOf(':') + 1);
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
          child: Center(child: Text(i.toString() + ": " + message)),
      );
  }

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  void _addMsg({String netMsg = ""}) {
    String msg;
    
    if (myController.text == "" && netMsg == "") { return; }

    // add counter to message 
    setState(() {
      if (netMsg != "") {
        msg = 'PC:' + netMsg;
      } else {
        msg = 'APP:' + myController.text;
        myController.clear();
        _sendMessage(msg);

        testClick();
      }
      // add message to message log widget
      messages.add(msg);
      
      _incrementCounter();
    });
  }

  @override
  Widget build(BuildContext context) {
    List<Widget> widgetChildren = [];
    int numberOfMessages = messages.length;

    for (int i = 0; i < numberOfMessages; i++) {
      widgetChildren.add(_formatMessage(messages[i], i));
    }

    Widget NetMsg = ListView(
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
          Expanded(child: NetMsg),
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
                ElevatedButton(onPressed: _getMessage, child: const Text('Refresh')),
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
    
    /*
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text('You have pushed the button this many times:'),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
  */
}
