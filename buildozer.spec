[app]

title = Pemancingan Adem Ayem Dlopo

package.name = ademayemdlopo
package.domain = id.ademayemdlopo

source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,kv,json,md,sql
source.exclude_dirs = .git,.venv,.python,.kivy,__pycache__,tests,wireframes,backups

version = 1.3.0
android.numeric_version = 10300

requirements = python3,kivy==2.3.1,requests,pyjnius

orientation = portrait
fullscreen = 0

icon.filename = assets/generated/app-launcher-icon.png
presplash.filename = assets/generated/hero-nila.png

android.api = 36
android.minapi = 24
android.ndk = 29

android.archs = arm64-v8a, armeabi-v7a

android.permissions = INTERNET
android.accept_sdk_license = True

android.debug_artifact = apk
android.release_artifact = aab

p4a.branch = develop

[buildozer]

log_level = 2
warn_on_root = 1
