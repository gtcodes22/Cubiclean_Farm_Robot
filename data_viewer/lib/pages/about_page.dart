import 'package:flutter/material.dart';
import 'package:data_viewer/common/build/app_build_timestamp.g.dart';

class AboutPage extends StatefulWidget {
  const AboutPage({super.key, required this.title});
  final String title;

  @override
  State<AboutPage> createState() => _AboutPage();
}

class _AboutPage extends State<AboutPage> {
    final String sDate = DateTime.fromMillisecondsSinceEpoch(
      lastAppBuildTimestamp).toString();

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
            const Text('App Version 0.2.0'),  // update this each revision
            Text('Build Time: $sDate (UK timezone)'),
            const Text('Written by: Jade Cawley'),
          ],
        ),
      ),
    );
  }
}