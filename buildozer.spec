[app]

title = Blackjack Calculator

package.name = blackjackcalculator
package.domain = com.aafacilities

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas

version = 1.1.5
android.numeric_version = 7

requirements = python3,kivy,pyjnius

orientation = portrait
fullscreen = 1

icon.filename = %(source.dir)s/icon.png

# Android
android.api = 36
android.minapi = 24

android.archs = arm64-v8a

android.accept_sdk_license = True

# Google Play Billing
android.gradle_dependencies = com.android.billingclient:billing:9.1.0,org.jetbrains.kotlin:kotlin-stdlib:1.8.22,org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.8.22,org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.8.22

# Use current python-for-android development branch
p4a.branch = develop

# Build Google Play App Bundle
android.release_artifact = aab

# Required for button vibration/haptic feedback
android.permissions = VIBRATE


[buildozer]

log_level = 2
warn_on_root = 1
