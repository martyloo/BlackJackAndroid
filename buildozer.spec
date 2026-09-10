[app]

# Name shown beneath the app icon and on Google Play.
title = Blackjack Calculator

# Permanent application ID:
# com.aafacilities.blackjackcalculator
package.name = blackjackcalculator
package.domain = com.aafacilities

# Project files.
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas

# User-visible version.
version = 1.1.3

# Android's internal version number.
# Must increase for every Play Store upload.
android.numeric_version = 5

# Python dependencies.
requirements = python3,kivy,pyjnius

# Phone display.
orientation = portrait
fullscreen = 1

# Artwork.
icon.filename = %(source.dir)s/icon.png

# Android versions.
android.api = 36
android.minapi = 24

# Modern 64-bit Android phones.
android.archs = arm64-v8a

# Automatically accept Android SDK licences during GitHub Actions builds.
android.accept_sdk_license = True

# Google Play Billing Library
android.gradle_dependencies = com.android.billingclient:billing:9.1.0

# Produce the Google Play App Bundle.
android.release_artifact = aab

# Permissions.
android.permissions = VIBRATE

[buildozer]

log_level = 2
warn_on_root = 1
