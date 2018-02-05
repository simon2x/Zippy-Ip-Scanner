# -*- mode: python -*-

block_cipher = None


a = Analysis(['zippyipscanner.py'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
             
a.datas += [
    ("icon.ico", "icon.ico", "data"),
    ("splash.png", "splash.png", "data"),
    ("images/start.png", "images/start.png", "data"),
    ("images/stop.png", "images/stop.png", "data"),
]             
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='zippyipscanner-v0.1.0-portable-x64',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon="icon.ico")
