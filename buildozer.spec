[app]
title = Pemancingan Adem Ayem Dlopo
package.name = ademayemdlopo
package.domain = id.ademayemdlopo
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,md
source.exclude_dirs = .git,.venv,.python,.kivy,__pycache__,tests,wireframes,backups
version = 1.1.0
requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0
icon.filename = assets/generated/brand-adem-ayem-icon.png
presplash.filename = assets/generated/hero-nila.png
android.api = 35
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
