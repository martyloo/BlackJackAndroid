BLACKJACK CALCULATOR — ANDROID PROJECT

This project replaces only the PySide6/Qt screen layer with Kivy controls.
The original blackjack calculation and strategy methods are retained in main.py.

TEST ON YOUR MAC
1. Open Terminal in this folder.
2. Create and activate an environment:
   python3 -m venv venv
   source venv/bin/activate
3. Install Kivy:
   python -m pip install --upgrade pip
   python -m pip install kivy
4. Run:
   python main.py

The preview opens at 360 x 800. Android uses the actual phone screen.

BUILD FOR ANDROID
Buildozer's Android toolchain is most reliable on Linux. On a Mac, the simplest
route is an Ubuntu virtual machine, a Linux computer, or GitHub Actions.

On Ubuntu:
1. Install Buildozer and Android prerequisites.
2. In this folder run:
   buildozer android debug
3. Install the resulting APK from the bin folder on a test phone.
4. For Google Play, run:
   buildozer android release
   The buildozer.spec requests an AAB release artifact.

IMPORTANT BEFORE GOOGLE PLAY
- Replace package.domain/package.name with your permanent package identity.
- Add a proper app icon and store screenshots.
- Create and securely retain a release signing key.
- Test every strategy condition you rely on.
- Review Google Play gambling and real-money gaming policies. This project is
  presented as a calculator/training tool and does not process wagers.
