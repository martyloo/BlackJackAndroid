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
version = 1.1.0

# Android's internal version number.
# Increase this for every future Play Store update:
# 1, then 2, then 3, etc.
android.numeric_version = 1

# Python dependencies.
requirements = python3,kivy

# Phone display.
orientation = portrait
fullscreen = 1

# Add these after creating the artwork.
icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

# Android versions.
android.api = 36
android.minapi = 24

# Modern 64-bit Android phones.
android.archs = arm64-v8a

# Automatically accept Android SDK licences during GitHub Actions builds.
android.accept_sdk_license = True

# Produce the Google Play App Bundle.
android.release_artifact = aab

# Your app currently does not need Android permissions.
android.permissions =

[buildozer]

log_level = 2
warn_on_root = 1
