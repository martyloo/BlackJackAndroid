[app]
title = Blackjack Calculator
package.name = blackjackcalculator
package.domain = com.aafacilities
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

# Replace these with finished artwork before Play Store release.
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

android.api = 36
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
android.release_artifact = aab

[buildozer]
log_level = 2
warn_on_root = 1
