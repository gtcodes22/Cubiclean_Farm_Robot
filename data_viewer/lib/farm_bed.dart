// Shameless stolen and adapted from: https://maxim-gorin.medium.com/advanced-flutter-ui-how-to-build-a-chat-app-with-custom-message-bubbles-4f90282b8be0
import 'package:flutter/material.dart';
import 'farm_bed_point.dart';

class FarmBed extends StatelessWidget {
  List<FarmBedPoint> points;
  final int bedID;
  final int bedTime;
  int? trafficLight; // 0 = green, 1 = yellow, 2 = red

  FarmBed({super.key, required this.points, required this.bedID, required this.bedTime}) {
    trafficLight = 2;
  }
  
  Widget _highLevel(String text, [double fontSize = 14.0]) {
    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
          color: Colors.white,
          shape: BoxShape.circle,
          border: BoxBorder.all(
            width: 5,
            color: Colors.white,
          ),
        ),
      child: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: Colors.white,
          shape: BoxShape.circle,
          border: BoxBorder.all(
            width: 3,
            color: Colors.red,
          ),
        ),
        child: Center(
          child: Text(
            text,
            style: TextStyle(
              color: Colors.black,
              fontWeight: FontWeight.bold,
              fontSize: fontSize,
            ),
          ),
        ),
      )
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(vertical: 5, horizontal: 10),
      padding: EdgeInsets.all(5),
      constraints: BoxConstraints(minWidth: 200, maxWidth: 400, minHeight:60, maxHeight: 60),
      decoration: BoxDecoration(
        color: trafficLight == 0 ? Colors.lightGreen : trafficLight == 1 ? Colors.yellow : Colors.redAccent,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(15),
          topRight: Radius.circular(15),
          bottomLeft: Radius.circular(15),
          bottomRight: Radius.circular(15),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black26,
            blurRadius: 5,
          ),
        ],
      ),
      child: Row(
        children: [
          Align(
            alignment: Alignment.centerLeft, // isSentByMe ? Alignment.centerRight : 
            child: Text(
              "Bed ${bedID.toString()}",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                //decoration: TextDecoration.underline,
                fontSize: 16,
                color: Colors.white,
                ),
              ),
          ),
          SizedBox(width: 30),
          trafficLight! >= 1 ? _highLevel("🌡️", 22.0) : Container(),
          SizedBox(width: 10),
          trafficLight! >= 2 ? _highLevel("💧", 20.0) : Container(),
          SizedBox(width: 10),
          trafficLight! >= 1 ? _highLevel("CO₂") : Container(),
          SizedBox(width: 10),
          trafficLight! >= 2 ? _highLevel("NH₃") : Container(),
          SizedBox(width: 10),
          trafficLight! >= 1 ? _highLevel("H₂S") : Container(),
          SizedBox(width: 10),
          trafficLight! >= 2 ? _highLevel("CH₄") : Container(),
          //mType == 'MSG' ? textMessage : Image(image: packet.getImageData(), height: 200),
        ],
      ),
    );
  }
}