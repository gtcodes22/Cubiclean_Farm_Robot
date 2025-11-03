import 'package:flutter/material.dart';

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
}

class _MyNetworkPageState extends State<MyNetworkPage> {
  final myController = TextEditingController();
  List messages = [];
  int _counter = 0;

  Widget _formatMessage(String message) {
    
    String src = message.startsWith("@PC") ? "[PC] → " : "[APP] → ";
    String des = message.endsWith("@PC") ? "[PC] " : "[APP] ";

    return Container(
        height: 50,
        color: Colors.amber[600],
          child: Center(child: Text(src + des + message)),
      );
  }

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  void _addMsg() {
    testClick();
    if (myController.text == "") { return; }

    setState(() { 
      String msg = _counter.toString() + ": " + myController.text;
      myController.clear();
      messages.add(msg);
      _incrementCounter();
    });
  }

  @override
  Widget build(BuildContext context) {
    List<Widget> widgetChildren = [];
    int numberOfMessages = messages.length;

    for (int i = 0; i < numberOfMessages; i++) {
      widgetChildren.add(_formatMessage(messages[i]));
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
