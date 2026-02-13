import 'package:flutter/material.dart';
//import 'dart:io';
//import 'dart:convert';
//import 'dart:async';

import 'socket_service.dart';
import 'pages/network_page.dart';
import 'pages/test_page.dart';
import 'pages/about_page.dart';

/// DO NOT RUN THIS PROGRAM VIA THE WEB APP DEBUGGER, AS THE DART:IO
/// LIBRARY IS NOT COMPATIBLE.

void main() => runApp(const MyApp()); // run MyApp as the main program

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of the application.
  @override
  StatefulWidget build(BuildContext context) {
    //return networkMessenger(this);
    return MaterialApp(
      //home: const MyNetworkPage(title: 'Network Test Page'),
      home: const MyHomePage(title: 'Home Page'),
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
  int pageIndex = 0;
  int numberOfMessages = 0;

  // any messages sent to/from the app
  List<String> netMessages = [];
  String addr = "";
  var attemptConnect = false;

  void _serverConnect(String addr) async {
    SocketService().initializeSocket(addr, netMessages, _newMessage);
  }

  // gets called whenever there's a new network message
  void _newMessage(String newMessage) {
    setState(() {
      numberOfMessages++;
      netMessages.add(newMessage);
    });
  }

  /// The following code is adapted from one of the flutter tutorials
  @override
  Widget build(BuildContext context) {
    // This switches which page to display based on the page index, which
    // the Navigation Rail changes
    Widget page;
    switch (pageIndex) {
      case 0:
        page = TestPage(title: 'Bed Overview');
      case 1:
        page = TestPage(title: 'Bed Health Inspector');
      case 2:
        page = MyNetworkPage(title: 'Network Debug Function',
          addrChange: _serverConnect,
          netMessages : netMessages);
      case 3:
        page = TestPage(title: 'Test Page');
      case 4:
        page = AboutPage(title: 'About Data Viewer...');
      default:
        throw UnimplementedError('no widget for $pageIndex');
    }

    // This adds a Navigation Rail widget to the app, which is displayed on
    // all pages. It allows the user to select which 'page' of the app to
    // display 
    return LayoutBuilder(
      builder: (context,constraints) {
        return Scaffold(
          body: Row(
            children: [
              SafeArea(
                child: NavigationRail(
                  extended: constraints.maxWidth >= 600,
                  destinations: [
                    NavigationRailDestination(
                      icon: Icon(Icons.table_chart),
                      label: Text('Bedding Overview'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.monitor_heart_sharp),
                      label: Text('Bed Health Inspector'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.question_answer),
                      label: Text('Network Debug Chat'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.handyman),
                      label: Text('Test Page'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.question_mark),
                      label: Text('About Page'),
                    ),
                  ],
                  selectedIndex: pageIndex,
                  onDestinationSelected: (value) {
                    setState(() {
                      pageIndex = value;
                    });
                  },
                ),
              ),
              // Displays page widget in space not used by the Navigation
              // rail.
              Expanded(
                child: Container(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  child: page,
                ),
              ),
            ],
          ),
        );
      }
    );
  }
}


