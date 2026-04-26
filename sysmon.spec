# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Dashboard.html', '.'),
    ],
    hiddenimports=[
        # uvicorn internals
        'uvicorn',
        'uvicorn.main',
        'uvicorn.config',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.lifespan',
        'uvicorn.lifespan.off',
        'uvicorn.lifespan.on',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.logging',
        'uvicorn.middleware',
        'uvicorn.middleware.proxy_headers',
        # fastapi / starlette
        'fastapi',
        'starlette',
        'starlette.responses',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.staticfiles',
        'starlette.routing',
        'anyio',
        'anyio._backends._asyncio',
        'h11',
        # psutil
        'psutil',
        'psutil._pswindows',
        # pystray / Pillow (optional — graceful fallback if missing)
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
    ],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SYSMON',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,        # show console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,           # add an .ico path here if you have one
    uac_admin=True,      # request admin rights (needed for full sensor access)
)
