// ignore_for_file: non_constant_identifier_names

class FarmBedPoint {
  final double tempAir;
  final double humidAir;
  final double CO2ppm;
  final double NH3ppm;
  final double H2Sppm;
  final double CH4volts;

  FarmBedPoint({required this.tempAir, required this.humidAir,
    required this.CO2ppm, required this.NH3ppm, required this.H2Sppm,
    required this.CH4volts});

}