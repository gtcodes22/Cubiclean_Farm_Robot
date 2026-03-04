// Source - https://stackoverflow.com/a/71976173
// Posted by Pi Da, modified by community. See post 'Timeline' for change history
// Retrieved 2026-03-02, License - CC BY-SA 4.0

import 'dart:async';
import 'dart:io';
import 'package:build/build.dart';

bool wroteBuildTimestamp = false;
String outputFilePath = 'lib/src/utils/build_info.dart';

Builder myTimestampBuilderFactory(BuilderOptions options) {
  //print('myTimestampBuilderFactory() called...');

  if (!wroteBuildTimestamp) {
    /// Write the current timestamp to the given file.
    print('myTimestampBuilderFactory(): Writing timestamp to file "${outputFilePath}" ...');

    String outputContents = 'const String BUILD_TIMESTAMP = \'${DateTime.now().toIso8601String()}\';\r\n';

    File dartFile = File(outputFilePath);
    dartFile.writeAsStringSync(outputContents, flush: true);  /// truncates the file if it already exists.

    wroteBuildTimestamp = true;
  }

  return MyTimestampBuilder ();
}

/// This class isn't really used. We just need it to convince build_runner to call our myTimestampBuilderFactory() method at build-time.
class MyTimestampBuilder extends Builder {
  /// IMPORTANT: build() only gets called for files that been updated (or if the whole build has been cleaned), since build_runner does incremental builds by default. So we can't rely on this method being called for every build.
  @override
  Future<FutureOr<void>> build(BuildStep buildStep) async {
  }

  @override
  Map<String, List<String>> get buildExtensions {
    return const {
      '.dart': ['.dart_whatever']
    };    
  }
}
