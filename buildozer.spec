[app]
title = 情绪周期日历
package.name = emotioncalendar
package.domain = org.emotioncalendar
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.include_patterns = main.py
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
