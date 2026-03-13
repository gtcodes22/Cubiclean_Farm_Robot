import 'package:flutter/material.dart';
import 'package:data_viewer/common/build/app_build_timestamp.g.dart';
//import 'package:data_viewer/src/utils/build_info.dart';
import 'package:data_viewer/farm_bed.dart';

class BedListPage extends StatefulWidget {
  const BedListPage({super.key, required this.title});
  final String title;

  @override
  State<BedListPage> createState() => _BedListPage();
}

class _BedListPage extends State<BedListPage> {
  FarmBed testBed = FarmBed(points:[], bedID: 1, bedTime: lastAppBuildTimestamp);
  FarmBed testBed2 = FarmBed(points:[], bedID: 2, bedTime: lastAppBuildTimestamp);
  ValueNotifier<bool> updateWidget = ValueNotifier(false);

  Widget buildBedList() 
  {
    List<Widget> widgetChildren = [];
    widgetChildren.add(testBed);
    widgetChildren.add(testBed2);
    
    return ListView(
      padding: const EdgeInsets.all(8),
      children: widgetChildren,
      );
  }

  void _getBedData() {
    return;
  }

  @override
  Widget build(BuildContext context) {
    Widget bedEntry = ValueListenableBuilder<bool>(
      valueListenable: updateWidget,
      builder:(context, value, child) => buildBedList(),
      child: null,
    );

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Column(
        children: [
          Expanded(child: bedEntry),
          Padding(
            padding: EdgeInsets.all(8),
            child: Row(
              spacing: 20,
              children: [
                ElevatedButton(onPressed: _getBedData, child: const Text('Get Bed Data')),
              ],
            ),
          ),
        ]
      )
    );
  }
}