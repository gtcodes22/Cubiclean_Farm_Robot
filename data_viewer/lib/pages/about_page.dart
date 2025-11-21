import 'package:flutter/material.dart';

class AboutPage extends StatefulWidget {
  const AboutPage({super.key, required this.title});
  final String title;

  @override
  State<AboutPage> createState() => _AboutPage();
}

class _AboutPage extends State<AboutPage> {
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
            const Text('App Version 0.1.0'),  // update this each revision
            const Text('Commit Time: 2025-11-21 5:44pm'),  // update this each revision
            const Text('Written by: Jade Cawley'),
          ],
        ),
      ),
    );
  }
}