import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/painting.dart';

class PacketMessage {
  // attributes of a Packet
  String src = '';
  String des = '';
  String mtype = '';
  int length = 0;
  String data = '';
  String end = '';
  MemoryImage? imageData;

  PacketMessage(dynamic raw) {
    // convert raw data from socket read into String
    String sRaw = String.fromCharCodes(raw);
    src = sRaw.substring(0,3);

    // check if packet is valid
    if (src != 'SPC' && src != 'RPI') {
      src = 'UNK';
      des = 'UNK';
      mtype = 'MSG';
      length = sRaw.length;
      data = sRaw;
      end = '\x00\xa8\x8b';
      return;
    } 

    des = sRaw.substring(3,6);
    mtype = sRaw.substring(6,9);
    //lengthBytes = utf8.encode(sRaw.substring(9,13));
    
    //length =  (lengthBytes[0] << 24) + (lengthBytes[1] << 16) + 
    //          (lengthBytes[2] << 8) + lengthBytes[3];
    length =  (raw[9] << 24) + (raw[10] << 16) + 
              (raw[11] << 8) + raw[12];

    if (mtype == 'MSG') {
      data = sRaw.substring(13,13 + length);
    } else {
      // change spec to send filename as null-terminated string after the length
      data = 'image with filename ?';

      List<int> imageBytes = raw.sublist(13, 13 + length); // get the image data bytes from the packet

      // assume .jpg for now, but this should be specified in the packet at some point
      imageData = MemoryImage(Uint8List.fromList(imageBytes));
    }
    end = sRaw.substring(13 + length, 13 + length + 4);
  }

  // ignore: no_leading_underscores_for_local_identifiers
  PacketMessage.newPacket (String _src, String _des, String _mtype, String _data) {
    src = _src;
    des = _des;
    mtype = _mtype;
    length = _data.length;
    data = _data;
    end = '\x00\xa8\x6b';
  }

  String getSRC() => src;
  String getDES() => des;
  String getType() => mtype;
  int getLength() => length;
  // from: https://stackoverflow.com/questions/57536300/convert-int32-to-bytes-list-in-dart
  // convert the length integer into a list of 4 bytes to be sent in the packet 
  Uint8List getLengthBytes() => Uint8List(4)..buffer.asByteData().setInt32(0, length, Endian.big);
  String getData() => data;
  MemoryImage getImageData() => (getType() == 'IMG') ? imageData! : MemoryImage(Uint8List(0));
  bool checkValid() {
    return (end == '\x00\xc2\xa8\x6b') ? true : false;
  }

  List<int> getSocketBytes() {
    //String sRaw = '${getLengthBytes()};
    List<int> bytes = utf8.encode('$src$des$mtype') + getLengthBytes() + utf8.encode('$data$end');
    return bytes;
  }

  static bool bValidPacket(dynamic raw) {
    String end = String.fromCharCodes(raw.sublist(raw.length - 4, raw.length));
    return (end == '\x00\xc2\xa8\x6b') ? true : false;
  }

  static int iLength(dynamic raw) {
    return (raw[9] << 24) + (raw[10] << 16) + (raw[11] << 8) + raw[12];
  }
}
