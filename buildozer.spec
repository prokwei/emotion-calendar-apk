[app]
title = 情绪周期日历
package.name = emotioncalendar
package.domain = org.emotion
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,akshare,numpy,pandas,requests,urllib3,charset-normalizer,idna,certifi,python-dateutil,pytz,six
orientation = portrait
fullscreen = 0
entrypoint = main.py

android.accept_sdk_license = True
android.allow_api_min = 21
android.api = 33
android.minapi = 21
android.ndk = 25b
exclude_patterns = **/test/*, **/tests/*
android.gradle_download = https://services.gradle.org/distributions/gradle-7.6.4-all.zip
android.gradle_plugin = 7.4.2
android.sdk = 33
android.ndk_api = 21
p4a.gradle_dependencies = gradle:7.6.4
p4a.bootstrap = sdl2
p4a.gradle_options = -Dorg.gradle.java.home=/usr/lib/jvm/java-17-openjdk-amd64
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
