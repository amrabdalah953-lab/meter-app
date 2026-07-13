[app]
title = Meter Reader System
package.name = meterapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1
requirements = python3,kivy,sqlite3,requests,urllib3,chardet,idna,certifi
orientation = portrait
osx.kivy_version = 2.3.0
fullscreen = 1
android.archs = armeabi-v7a, arm64-v8a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.private_storage = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
