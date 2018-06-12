# -*- mode: python -*-

block_cipher = None

from os.path import dirname, abspath

path = 'zippyipscanner.py'

a = Analysis([path],
             pathex=[dirname(path)],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['.devmode.txt'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='zippyipscanner',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          onefile=True,
          console=False,
          icon="zippyipscanner.ico")
