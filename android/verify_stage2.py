from pathlib import Path
import re, sys
root = Path(__file__).resolve().parent
gradle = (root / "app/build.gradle.kts").read_text()
activity = (root / "app/src/main/java/com/airoboticsinvestor/MainActivity.java").read_text()
manifest = (root / "app/src/main/AndroidManifest.xml").read_text()
checks = {
    "versionCode 231": bool(re.search(r"versionCode\s*=\s*231", gradle)),
    "versionName 0.1.231": 'versionName = "0.1.231"' in gradle,
    "separate AI Robotics screen": 'setText("AI Robotics")' in activity,
    "read-only endpoint": '"/api/robotics/report"' in activity and 'setRequestMethod("GET")' in activity,
    "release_ready gate": 'release_ready' in activity,
    "36h freshness gate": 'toHours() > 36' in activity,
    "strategy gate": "balanced-1.3-audit" in activity,
    "HTTPS-only config": 'startsWith("https://")' in activity,
    "Internet permission": 'android.permission.INTERNET' in manifest,
}
for name, ok in checks.items(): print(("PASS" if ok else "FAIL") + " " + name)
if not all(checks.values()): sys.exit(1)
