"""Reproduce violet app icons from the unchanged upstream SVG geometry.

Only SVG fill colours are edited. PNGs are rendered directly from those SVGs;
ICO containers embed the rendered PNG frames without raster recolouring.
Pinned renderer: resvg_py 0.5.0 / resvg 0.48.1. Pillow is used for read-only
pixel/alpha/container validation and does not generate the output images.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import xml.etree.ElementTree as ET

import resvg_py
from PIL import Image, __version__ as pillow_version

GREEN = '#00AE42'
VIOLET = '#7C3AED'
MAIN_BASE_SHA256 = '0ab1a121fc86598746a165d94eead0052e0c8815dbefdd6c637429145f511df9'
GLYPH_BASE_SHA256 = 'ed23118524d6c45dada57336f167a9fd8ad00e02d49a6f01a5874022f4607116'
ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 154, 192, 256)
PNG_SIZES = {'BambuStudio_32px.png': 32, 'BambuStudio_128px.png': 128,
             'BambuStudio_192px.png': 192, 'BambuStudio.png': 154}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def svg_paths(text):
    root = ET.fromstring(text)
    if any(element.tag.rsplit('}', 1)[-1] in ('image', 'text', 'script', 'foreignObject', 'use') for element in root.iter()):
        raise ValueError('Unexpected external/text/script SVG content; review the upstream geometry')
    return [element.attrib['d'] for element in root.iter() if element.tag.rsplit('}', 1)[-1] == 'path']


def sources(images):
    main = (images / 'BambuStudio.svg').read_text(encoding='utf-8')
    if main.count(GREEN) == 1 and VIOLET not in main:
        green_main = main
    elif main.count(VIOLET) == 1 and GREEN not in main:
        green_main = main.replace(VIOLET, GREEN)
    else:
        raise ValueError('Unexpected app SVG palette; review rather than recolouring arbitrary elements')
    if sha(green_main.encode('utf-8')) != MAIN_BASE_SHA256:
        raise ValueError('Upstream app SVG changed; review paths before updating the pinned source hash')
    violet_main = green_main.replace(GREEN, VIOLET)
    if svg_paths(green_main) != svg_paths(violet_main):
        raise ValueError('App SVG paths changed')

    glyph = (images / 'BambuStudioBlack.svg').read_text(encoding='utf-8')
    if sha(glyph.encode('utf-8')) != GLYPH_BASE_SHA256:
        raise ValueError('Upstream glyph SVG changed; review paths before updating the pinned source hash')
    original_root = 'width="10" height="12" viewBox="0 0 10 12"'
    if glyph.count(original_root) != 1 or glyph.count('#262E30') != 4:
        raise ValueError('Unexpected standalone glyph layout/palette')
    # Letterbox the original 10:12 glyph in a square icon; do not stretch it or
    # replace the transparent title icon with the tiled desktop icon.
    title = glyph.replace(original_root, 'width="154" height="154" viewBox="-1 0 12 12"')
    green_title = title.replace('#262E30', GREEN)
    violet_title = title.replace('#262E30', VIOLET)
    if svg_paths(glyph) != svg_paths(violet_title) or len(svg_paths(violet_title)) != 4:
        raise ValueError('Standalone title glyph paths changed')
    return green_main, violet_main, green_title, violet_title


def render(svg, size):
    return resvg_py.svg_to_bytes(svg_string=svg, width=size, height=size,
                                 background=None, skip_system_fonts=True,
                                 shape_rendering='geometric_precision')


def rgba(data, size):
    with Image.open(io.BytesIO(data)) as source:
        if source.size != (size, size):
            raise ValueError('Rendered image dimensions differ')
        return source.convert('RGBA')


def ico(frames):
    ordered = sorted(frames.items())
    result = bytearray(struct.pack('<HHH', 0, 1, len(ordered)))
    offset = 6 + 16 * len(ordered)
    for size, png in ordered:
        result.extend(struct.pack('<BBBBHHII', size if size < 256 else 0,
                                  size if size < 256 else 0, 0, 0, 1, 32, len(png), offset))
        offset += len(png)
    for _, png in ordered:
        result.extend(png)
    raw = bytes(result)
    with Image.open(io.BytesIO(raw)) as decoded:
        if decoded.ico.sizes() != {(size, size) for size, _ in ordered}:
            raise ValueError('ICO frame inventory differs')
        for size, png in ordered:
            if decoded.ico.getimage((size, size)).convert('RGBA').tobytes() != rgba(png, size).tobytes():
                raise ValueError('ICO frame differs from its original SVG render')
    return raw


def build(images):
    if resvg_py.__version__ != '0.5.0' or resvg_py.__resvg_version__ != '0.48.1':
        raise ValueError('Use the pinned resvg_py 0.5.0 / resvg 0.48.1 renderer')
    green_main, violet_main, green_title, violet_title = sources(images)
    outputs = {'BambuStudio.svg': violet_main.encode('utf-8'),
               'BambuStudioTitle.svg': violet_title.encode('utf-8')}
    rendered, checks = {}, []
    for kind, green, violet in (('tile', green_main, violet_main), ('title', green_title, violet_title)):
        frames = {}
        for size in ICO_SIZES:
            original = rgba(render(green, size), size)
            png = render(violet, size)
            recoloured = rgba(png, size)
            if original.getchannel('A').tobytes() != recoloured.getchannel('A').tobytes():
                raise ValueError('SVG colour replacement changed alpha coverage')
            if kind == 'tile':
                old, new = original.tobytes(), recoloured.tobytes()
                white = b'\xff\xff\xff\xff'
                if any(old[index:index+4] == white and new[index:index+4] != white for index in range(0, len(old), 4)):
                    raise ValueError('Opaque white logo interior changed')
            frames[size] = png
            checks.append({'kind': kind, 'pixels': size, 'alpha_identical_to_green_svg_render': True,
                           'alpha_sha256': sha(recoloured.getchannel('A').tobytes())})
        rendered[kind] = frames
    outputs.update({name: rendered['tile'][size] for name, size in PNG_SIZES.items()})
    outputs['BambuStudio.ico'] = ico(rendered['tile'])
    outputs['BambuStudioTitle.ico'] = ico(rendered['title'])
    report = {'schema': 'prefect-violet-app-icon-v1', 'colour': VIOLET,
              'base_upstream': 'v02.08.02.61',
              'sources': {'BambuStudio.svg_green_sha256': MAIN_BASE_SHA256,
                          'BambuStudioBlack.svg_sha256': GLYPH_BASE_SHA256},
              'renderer': {'resvg_py': resvg_py.__version__, 'resvg': resvg_py.__resvg_version__,
                           'pillow_read_only_checker': pillow_version, 'system_fonts_used': False},
              'vector_path_data_unchanged': True, 'raster_recolouring_used': False,
              'ico_frame_sizes': list(ICO_SIZES), 'svg_colour_alpha_checks': checks,
              'assets': [{'file': 'resources/images/' + name, 'bytes': len(data), 'sha256': sha(data)}
                         for name, data in sorted(outputs.items())],
              'limits': 'Identical SVG path geometry and identical alpha between green/violet renders using the same renderer. Legacy vendor raster antialiasing is not claimed byte-identical; macOS ICNS and About artwork are unchanged.'}
    return outputs, report


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    mode = cli.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    cli.add_argument('--report', type=Path)
    args = cli.parse_args()
    images = args.repo / 'resources/images'
    outputs, report = build(images)
    for name, data in outputs.items():
        path = images / name
        if args.write:
            path.write_bytes(data)
        if not path.is_file() or path.read_bytes() != data:
            raise ValueError('Generated asset differs: resources/images/' + name)
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'success': True, 'assets': len(outputs), 'alpha_checks': len(report['svg_colour_alpha_checks']),
                      'colour': VIOLET, 'mode': 'write' if args.write else 'check'}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
