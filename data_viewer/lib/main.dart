import 'package:data_viewer/pages/bed_list_page.dart';
import 'package:flutter/material.dart';
import 'dart:io';
//import 'dart:convert';
//import 'dart:async';

import 'socket_service.dart';
import 'pages/network_page.dart';
import 'pages/test_page.dart';
import 'pages/about_page.dart';
import 'pages/webview_page.dart';

/// DO NOT RUN THIS PROGRAM VIA THE WEB APP DEBUGGER, AS THE DART:IO
/// LIBRARY IS NOT COMPATIBLE.

void main() => runApp(const MyApp()); // run MyApp as the main program

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of the application.
  @override
  StatefulWidget build(BuildContext context) {
    String url1 = 'https://flutter.dev';
    String url2 = 'https://www.youtube.com/watch?v=EgH0pyo5Fbc';
    String url3 = 'https://https://linktr.ee/techtuesdays_betaden';
    // open config file
    String configFile = './config.txt';
    try {
      final file = File(configFile);
      String contents =  file.readAsStringSync();
      url1 = contents.split('\n')[0].substring(5);
      url2 = contents.split('\n')[1].substring(5);
      url3 = contents.split('\n')[2].substring(5);
    } catch (e) {
      debugPrint("Error resolving config file path: $e");
      debugPrint("Creating default config file with urls: $url1, $url2, $url3");

      try {
        final file = File(configFile);
        file.writeAsStringSync('url1:$url1\nurl2:$url2\nurl3:$url3');
      } catch (e) {
        debugPrint("Error creating default config file: $e");
      }
    }

    //return networkMessenger(this);
    return MaterialApp(
      //home: const MyNetworkPage(title: 'Network Test Page'),
      home: MyHomePage(title: 'Home Page', url1: url1, url2: url2, url3: url3),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title, required this.url1, required this.url2, required this.url3});
  final String title;
  final String url1;
  final String url2;
  final String url3;


  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int pageIndex = 2;
  SocketService socketService = SocketService();

  /// The following code is adapted from one of the flutter tutorials
  @override
  Widget build(BuildContext context) {
    final GlobalKey<WebViewPageState> resetPage = GlobalKey();

    // This switches which page to display based on the page index, which
    // the Navigation Rail changes
    debugPrint('Building page index: $pageIndex');
    Widget page;
    switch (pageIndex) {
      case 0:
        page = TestPage(title: 'System Status');
      case 1:
        page = BedListPage(title: 'Beds Overview');
      case 2:
        page = MyNetworkPage(title: 'Network Debug Function', socketService: socketService);
      case 3:
        page = WebViewPage(key: resetPage, title: 'Bedding Overview: Web', url: widget.url1);
        resetPage.currentState?.reload();
      case 4:
        page = WebViewPage(key: resetPage, title: 'Robot Visualisation', url: widget.url2);
        resetPage.currentState?.reload();
      case 5:
        page = WebViewPage(key: resetPage, title: 'Rameez\'s Section', url: widget.url3);
        resetPage.currentState?.reload();
      case 6:
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
                      label: Text('Bedding Overview: Web'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.handyman),
                      label: Text('Robot Visualisation'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.handyman),
                      label: Text('Rameez\'s Section'),
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


