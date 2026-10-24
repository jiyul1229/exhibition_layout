"""장생포문화창고 전시장 맵(3층 갤러리B, 4층 갤러리C, 4층 특별전시관)을 만들어 index.html에 넣습니다.

울산시립미술관 맵과 같은 형식(layout JSON + GLB 모델 + 평면도 SVG 미리보기)으로 만들어
index.html 안의 <script id="floorplanAssetData"> JSON에 jsp_* 키로 추가/교체합니다.

치수 출처: 제공된 도면 jpg (단위 mm)
  - 장생포문화창고 3층 갤러리 B.jpg
  - 장생포문화창고 4층 갤러리 C.jpg
  - 특별전시관.jpg
도면이 축척대로 그려지지 않아, 치수가 적히지 않은 값(기둥 크기, 비품실 길이, 입구 위치)은
옆에 적힌 치수와의 그림 비율로 추정했습니다. 추정값은 ASSUMED 표시와 assumptions에 남깁니다.

실행: python tools/build_jangsaengpo_maps.py
"""
import base64
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / 'index.html'

COLUMN = 0.8            # ASSUMED: 기둥 한 변 (도면에 치수 없음)
PARTITION_W = 2.4       # 이동식 가벽 2,700 x 2,400 x 50 → 폭 2.4m, 높이 2.7m, 두께 0.05m로 해석
PARTITION_H = 2.7
PARTITION_T = 0.05
WALL_T = 0.18
DOOR_HEADER_H = 2.4     # 좁은 출입구 위 상인방 높이 (3m 이상 넓은 개구부는 상인방 없이 완전히 열어 둠)


def partitions_between(x_left_col, x_right_col, z):
    """두 기둥 중심 사이에 이동식 가벽 2개를 같은 간격으로 놓습니다(도면: '기둥사이 2개 배치가능')."""
    free_a, free_b = x_left_col + COLUMN / 2, x_right_col - COLUMN / 2
    gap = (free_b - free_a - 2 * PARTITION_W) / 3
    a1 = free_a + gap
    a2 = a1 + PARTITION_W + gap
    return [(a1, a1 + PARTITION_W, z), (a2, a2 + PARTITION_W, z)]


# ---------------------------------------------------------------------------
# 전시실 정의 (x: 오른쪽 +, z: 도면 아래쪽 +, 원점: 전시실 안쪽 왼쪽 위 모서리)
# walls: (id, a, b, height, hangable, openings[(t0,t1)], name)
# ---------------------------------------------------------------------------
def gallery_b():
    W, D, H = 18.8, 10.5, 3.2
    # 오른쪽 벽: 위 4,800 → 기둥 → 1,370 → 비품실 → 930 (비품실 길이는 1,370과의 그림 비율로 2.59m 추정)
    col_z = 4.8 + COLUMN / 2
    store0 = 4.8 + COLUMN + 1.37
    store1 = D - 0.93
    # 왼쪽(로비 쪽): 위 출입구 / 벽 / 아래 출입구 / 고정벽 3,200 — 개구부 위치는 그림 비율로 추정
    left_open = [(0.0, 2.57), (5.29, D - 3.2)]
    walls = [
        ('north', (0, 0), (W, 0), H, True, [], '북쪽 고정벽'),
        ('east_1', (W, 0), (W, store0), H, True, [], '동쪽 고정벽'),
        ('east_store', (W, store0), (W, store1), H, False, [], '비품실 문'),
        ('east_2', (W, store1), (W, D), H, True, [], '동쪽 고정벽(남)'),
        ('south', (W, D), (0, D), H, True, [], '남쪽 고정벽'),
        ('west_fixed', (0, D), (0, D - 3.2), H, True, [], '서쪽 고정벽 3,200'),
        ('west_lobby', (0, D - 3.2), (0, 0), H, False,
         [((D - 3.2 - b) / (D - 3.2), (D - 3.2 - a) / (D - 3.2)) for a, b in left_open], '로비 쪽 벽(출입구 2곳)'),
    ]
    cols = [(5.34, col_z), (12.61, col_z)]
    return dict(
        id='jsp_gallery_b', title='3층 갤러리B', room='gallery_b', W=W, D=D, H=H, walls=walls,
        columns=cols, wall_columns=[(W - 0.6 / 2, col_z, 0.6, COLUMN)],
        partitions=partitions_between(cols[0][0], cols[1][0], col_z),
        entrance=('west_lobby', 1), source='장생포문화창고 3층 갤러리 B.jpg',
        known=[('가로(북·남)', 18.8), ('동쪽 벽 위 구간', 4.8), ('기둥~비품실', 1.37), ('비품실~남쪽 끝', 0.93),
               ('서쪽 고정벽', 3.2), ('고정벽 높이', 3.2)],
        notes=['세로 길이 10.5m는 동쪽 벽 치수(4,800 + 기둥 + 1,370 + 비품실 + 930)의 합으로 추정했습니다(비품실 2.59m, 기둥 0.8m 가정).',
               '로비 쪽 출입구 2곳의 위치·폭은 도면 그림 비율로 추정했습니다.'],
        movable=9,
    )


def gallery_c():
    W, D, H = 18.5, 10.5, 3.2
    col_z = 4.75 + COLUMN / 2
    store0 = 4.75 + COLUMN + 1.4
    store1 = D - 0.93
    walls = [
        ('north', (0, 0), (W, 0), H, True, [], '북쪽 고정벽'),
        ('east_1', (W, 0), (W, store0), H, True, [], '동쪽 고정벽'),
        ('east_store', (W, store0), (W, store1), H, False, [], '비품실 문'),
        ('east_2', (W, store1), (W, D), H, True, [], '동쪽 고정벽(남)'),
        ('south', (W, D), (0, D), H, True, [], '남쪽 고정벽'),
        ('west_fixed', (0, D), (0, D - 4.8), H, True, [], '서쪽 고정벽 4,800'),
        ('west_lobby', (0, D - 4.8), (0, 0), H, False, [(0.0, 1.0)], '로비 쪽 개구부'),
    ]
    cols = [(5.22, col_z), (12.41, col_z)]
    return dict(
        id='jsp_gallery_c', title='4층 갤러리C', room='gallery_c', W=W, D=D, H=H, walls=walls,
        columns=cols, wall_columns=[(W - 0.6 / 2, col_z, 0.6, COLUMN)],
        partitions=partitions_between(cols[0][0], cols[1][0], col_z),
        entrance=('west_lobby', 0), source='장생포문화창고 4층 갤러리 C.jpg',
        known=[('가로(북·남)', 18.5), ('동쪽 벽 위 구간', 4.75), ('기둥~비품실', 1.4), ('비품실~남쪽 끝', 0.93),
               ('서쪽 고정벽', 4.8), ('고정벽 높이', 3.2)],
        notes=['세로 길이 10.5m는 동쪽 벽 치수(4,750 + 기둥 + 1,400 + 비품실 + 930)의 합으로 추정했습니다(비품실 2.63m, 기둥 0.8m 가정).',
               '서쪽 고정벽 4,800 위쪽은 로비로 열린 개구부로 보았고, 로비 앞 5,200 복도 벽은 전시실 밖이라 넣지 않았습니다.'],
        movable=7,
    )


def special_hall():
    W, D, H = 37.3, 9.2, 3.5
    # 가로 37,300(위), 아래 고정벽 24,100, 세로 9,200 — 가로/세로 그림 비율이 달라 각각의 치수로 환산
    sx = lambda px: (px - 240) / 42.49
    sz = lambda px: (px - 250) / 72.8
    lx0, lx1, lz0 = 24.1, round(sx(1540), 2), round(sz(662), 2)   # 빛의 방
    hyd0, hyd1 = round(sz(475), 2), round(sz(612), 2)              # 소화전
    col_z = round(sz(551), 2)
    walls = [
        ('north', (0, 0), (W, 0), H, True, [], '북쪽 고정벽'),
        ('east_lobby', (W, 0), (W, D), H, False, [(0.0, 1.0)], '로비 쪽 개구부'),
        ('light_e', (lx1, D), (lx1, lz0), H, False, [], '빛의 방 동쪽 벽'),
        ('light_n', (lx1, lz0), (lx0, lz0), H, False, [], '빛의 방 북쪽 벽'),
        ('light_w', (lx0, lz0), (lx0, D), H, False, [], '빛의 방 서쪽 벽'),
        ('south', (lx0, D), (0, D), H, True, [], '남쪽 고정벽 24,100'),
        ('west_s', (0, D), (0, hyd1), H, True, [], '서쪽 고정벽(남)'),
        ('west_hydrant', (0, hyd1), (0, hyd0), H, False, [], '소화전'),
        ('west_n', (0, hyd0), (0, 0), H, True, [], '서쪽 고정벽(북)'),
    ]
    cols = [(round(sx(482), 2), col_z), (round(sx(773), 2), col_z), (round(sx(1048), 2), col_z)]
    poly = [(0, 0), (W, 0), (W, D), (lx1, D), (lx1, lz0), (lx0, lz0), (lx0, D), (0, D)]
    return dict(
        id='jsp_special', title='4층 특별전시관', room='special_hall', W=W, D=D, H=H, walls=walls, poly=poly,
        columns=cols, wall_columns=[],
        partitions=partitions_between(cols[0][0], cols[1][0], col_z),
        entrance=('east_lobby', 0), source='특별전시관.jpg',
        known=[('가로(북)', 37.3), ('남쪽 고정벽', 24.1), ('세로', 9.2), ('고정벽 높이', 3.5)],
        notes=['기둥·소화전·빛의 방 위치는 도면 그림 비율로 환산했습니다(가로 37,300 / 세로 9,200 기준).',
               '빛의 방 내부와 로비는 전시실 밖이라 넣지 않았고, 빛의 방 바깥벽은 고정벽이 아니라 작품을 걸지 않습니다.'],
        movable=7,
    )


# ---------------------------------------------------------------------------
# GLB 작성 (위치 + 정점 색 + 인덱스, 울산 모델과 같은 구조)
# ---------------------------------------------------------------------------
def box(cx, cz, along_x, w, d, y0, y1):
    """w: 진행 방향 길이, d: 두께. along_x=True면 x축 방향 상자."""
    hx, hz = (w / 2, d / 2) if along_x else (d / 2, w / 2)
    xs, zs = (cx - hx, cx + hx), (cz - hz, cz + hz)
    v = [(x, y, z) for y in (y0, y1) for z in zs for x in xs]
    idx = [0, 2, 1, 1, 2, 3, 4, 5, 6, 5, 7, 6, 0, 1, 4, 1, 5, 4, 2, 6, 3, 3, 6, 7, 0, 4, 2, 2, 4, 6, 1, 3, 5, 3, 7, 5]
    return v, idx


def wall_box(a, b, t0, t1, y0, y1, thick):
    ax, az = a
    bx, bz = b
    x0, z0 = ax + (bx - ax) * t0, az + (bz - az) * t0
    x1, z1 = ax + (bx - ax) * t1, az + (bz - az) * t1
    along_x = abs(bz - az) < 1e-9
    length = abs(x1 - x0) if along_x else abs(z1 - z0)
    return box((x0 + x1) / 2, (z0 + z1) / 2, along_x, length + (thick if along_x else 0), thick, y0, y1)


def triangulate(poly):
    """단순 다각형 귀 자르기."""
    pts = list(poly)
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    order = list(range(len(pts))) if area > 0 else list(range(len(pts)))[::-1]
    tris = []
    def inside(p, a, b, c):
        def s(p1, p2, p3): return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        d1, d2, d3 = s(p, a, b), s(p, b, c), s(p, c, a)
        return not ((d1 < -1e-9 or d2 < -1e-9 or d3 < -1e-9) and (d1 > 1e-9 or d2 > 1e-9 or d3 > 1e-9))
    guard = 0
    while len(order) > 3 and guard < 1000:
        guard += 1
        for k in range(len(order)):
            i0, i1, i2 = order[k - 1], order[k], order[(k + 1) % len(order)]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 1e-9:
                continue
            if any(inside(pts[j], a, b, c) for j in order if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            order.pop(k)
            break
    tris.append(tuple(order))
    # y가 위(+)이고 z가 아래쪽(+)인 좌표계에서 윗면이 위를 보도록 감기 방향을 뒤집음
    return [(a, c, b) for a, b, c in tris]


def build_glb(meshes):
    """meshes: [(name, vertices[(x,y,z)], indices, rgb)]"""
    bin_parts, views, accessors, gl_meshes, nodes = [], [], [], [], [{'name': 'world', 'children': []}]
    offset = 0

    def add_view(data, target):
        nonlocal offset
        pad = (-len(data)) % 4
        bin_parts.append(data + b'\0' * pad)
        views.append({'buffer': 0, 'byteOffset': offset, 'byteLength': len(data), 'target': target})
        offset += len(data) + pad
        return len(views) - 1

    for name, verts, idx, rgb in meshes:
        iv = add_view(struct.pack(f'<{len(idx)}I', *idx), 34963)
        accessors.append({'componentType': 5125, 'type': 'SCALAR', 'bufferView': iv, 'count': len(idx),
                          'max': [max(idx)], 'min': [min(idx)]})
        ia = len(accessors) - 1
        pv = add_view(b''.join(struct.pack('<3f', *v) for v in verts), 34962)
        accessors.append({'componentType': 5126, 'type': 'VEC3', 'bufferView': pv, 'count': len(verts),
                          'max': [max(v[i] for v in verts) for i in range(3)],
                          'min': [min(v[i] for v in verts) for i in range(3)]})
        pa = len(accessors) - 1
        cv = add_view(bytes([*rgb, 255]) * len(verts), 34962)
        accessors.append({'componentType': 5121, 'normalized': True, 'type': 'VEC4', 'bufferView': cv, 'count': len(verts)})
        ca = len(accessors) - 1
        gl_meshes.append({'name': name, 'primitives': [{'attributes': {'POSITION': pa, 'COLOR_0': ca}, 'indices': ia, 'mode': 4}]})
        nodes.append({'name': name, 'mesh': len(gl_meshes) - 1})
        nodes[0]['children'].append(len(nodes) - 1)

    binary = b''.join(bin_parts)
    gltf = {'asset': {'version': '2.0', 'generator': 'tools/build_jangsaengpo_maps.py'}, 'scene': 0,
            'scenes': [{'nodes': [0]}], 'nodes': nodes, 'meshes': gl_meshes, 'accessors': accessors,
            'bufferViews': views, 'buffers': [{'byteLength': len(binary)}]}
    js = json.dumps(gltf, separators=(',', ':')).encode()
    js += b' ' * ((-len(js)) % 4)
    total = 12 + 8 + len(js) + 8 + len(binary)
    return (struct.pack('<III', 0x46546C67, 2, total) + struct.pack('<II', len(js), 0x4E4F534A) + js
            + struct.pack('<II', len(binary), 0x004E4942) + binary)


# ---------------------------------------------------------------------------
def r3(v): return round(v, 3)


def make_asset(h):
    W, D, H = h['W'], h['D'], h['H']
    poly = h.get('poly') or [(0, 0), (W, 0), (W, D), (0, D)]
    floor_tris = triangulate(poly)
    meshes = [(f"GalleryFloor_{h['room']}", [(x, 0.0, z) for x, z in poly], [i for t in floor_tris for i in t], (224, 226, 222))]
    walls_json = []
    for wid, a, b, height, hangable, openings, name in h['walls']:
        full_id = f"{h['id']}_wall_{wid}"
        L = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
        ops = sorted((min(o), max(o)) for o in openings)
        cuts, t = [], 0.0
        for o0, o1 in ops:
            if o0 > t + 1e-6: cuts.append(('solid', t, o0))
            if (o1 - o0) * L < 3.0: cuts.append(('header', o0, o1))
            t = max(t, o1)
        if t < 1 - 1e-6: cuts.append(('solid', t, 1.0))
        for n, (kind, t0, t1) in enumerate(cuts):
            y0 = DOOR_HEADER_H if kind == 'header' else 0.0
            v, idx = wall_box(a, b, t0, t1, y0, height, WALL_T)
            meshes.append((f'{full_id}_{kind}_{n}', v, idx, (232, 231, 225) if hangable else (216, 215, 207)))
        walls_json.append({'id': full_id, 'name': name, 'aXZ': [r3(a[0]), r3(a[1])], 'bXZ': [r3(b[0]), r3(b[1])],
                           'kind': 'gallery_boundary' if hangable else 'non_hanging', 'hangable': hangable,
                           'heightM': height, 'thicknessM': WALL_T,
                           'openingsAlongWallFraction': [[round(o0, 4), round(o1, 4)] for o0, o1 in ops],
                           'rooms': [h['room']], 'lengthM': r3(L)})
    columns_json = []
    for i, (x, z) in enumerate(h['columns'], 1):
        v, idx = box(x, z, True, COLUMN, COLUMN, 0, H)
        meshes.append((f"{h['id']}_column_{i}_wall", v, idx, (226, 220, 208)))
        columns_json.append({'id': f"{h['id']}_column_{i}", 'name': f'기둥 {i}', 'xz': [r3(x), r3(z)],
                             'sizeXZ': [COLUMN, COLUMN], 'sizeAssumed': True})
    for i, (x, z, w, d) in enumerate(h['wall_columns'], len(h['columns']) + 1):
        v, idx = box(x, z, True, w, d, 0, H)
        meshes.append((f"{h['id']}_column_{i}_wall", v, idx, (226, 220, 208)))
        columns_json.append({'id': f"{h['id']}_column_{i}", 'name': f'벽 기둥 {i}', 'xz': [r3(x), r3(z)],
                             'sizeXZ': [w, d], 'sizeAssumed': True})
    for i, (x0, x1, z) in enumerate(h['partitions'], 1):
        wid = f"{h['id']}_wall_partition_{i}"
        v, idx = wall_box((x0, z), (x1, z), 0, 1, 0, PARTITION_H, PARTITION_T)
        meshes.append((f'{wid}_solid_0', v, idx, (240, 238, 232)))
        walls_json.append({'id': wid, 'name': f'이동식 가벽 {i}', 'aXZ': [r3(x0), r3(z)], 'bXZ': [r3(x1), r3(z)],
                           'kind': 'movable_partition', 'hangable': True, 'heightM': PARTITION_H,
                           'thicknessM': PARTITION_T, 'openingsAlongWallFraction': [], 'rooms': [h['room']],
                           'lengthM': PARTITION_W})
    glb = build_glb(meshes)
    xs = [p[0] for m in meshes for p in m[1]]
    zs = [p[2] for m in meshes for p in m[1]]
    bounds = {'min': [r3(min(xs)), 0.0, r3(min(zs))], 'max': [r3(max(xs)), H, r3(max(zs))],
              'widthX': r3(max(xs) - min(xs)), 'heightY': H, 'depthZ': r3(max(zs) - min(zs))}
    area = abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2
    ent_wall, ent_index = h['entrance']
    ent = next(w for w in walls_json if w['id'] == f"{h['id']}_wall_{ent_wall}")
    layout = {
        'id': h['id'], 'title': h['title'], 'venue': '장생포문화창고', 'units': 'm',
        'coordinateSystem': {'origin': '전시실 안쪽 북서쪽 모서리', 'x': 'right/east positive', 'z': 'down/south positive',
                             'y': 'vertical height; floor at y=0'},
        'sourceDrawing': h['source'],
        'knownDimensions': [{'name': n, 'value_m': v, 'confidence': '도면 표기'} for n, v in h['known']],
        'defaultGeometry': {'wallHeightM': H, 'outerWallThicknessM': WALL_T, 'wallHeightIsAssumption': False},
        'buildingFootprintXZ': [[r3(x), r3(z)] for x, z in poly],
        'rooms': [{'id': h['room'], 'name': h['title'], 'role': 'gallery', 'polygonXZ': [[r3(x), r3(z)] for x, z in poly],
                   'areaM2Approx': round(area, 2), 'dimensionsStatus': '도면 치수 기반, 일부 그림 비율 추정'}],
        'walls': walls_json,
        'columns': columns_json,
        'movablePartitions': {'sizeMM': [2700, 2400, 50], 'available': h['movable'], 'placedInModel': len(h['partitions'])},
        'assumptions': [
            f"{h['title']} 치수는 제공된 도면(단위 mm)을 기준으로 했습니다. 흰색 고정벽에만 작품을 겁니다.",
            *h['notes'],
            f'기둥 크기 {COLUMN}m×{COLUMN}m는 도면에 치수가 없어 가정한 값입니다.',
            f'이동식 가벽(2,700×2,400×50)은 폭 {PARTITION_W}m·높이 {PARTITION_H}m로 보고, 도면대로 기둥 사이에 2개 배치했습니다.',
        ],
        'generatedAsset': {'glb': f"models/{h['id']}.glb", 'meshCount': len(meshes), 'boundsM': bounds},
        'exhibitionFootprintsXZ': [[[r3(x), r3(z)] for x, z in poly]],
        'entrances': [{'roomId': h['room'], 'wallId': ent['id'],
                       'openingFractions': [ent['openingsAlongWallFraction'][ent_index]], 'note': '로비 쪽 출입구'}],
    }
    return {'layout': layout, 'modelBase64': base64.b64encode(glb).decode(), 'previewData': preview_svg(h, layout),
            'title': h['title']}


def preview_svg(h, layout):
    pad, top = 34, 58
    scale = min(560 / h['W'], 320 / h['D'])
    Wpx, Dpx = h['W'] * scale + pad * 2, h['D'] * scale + top + 74
    X = lambda x: pad + x * scale
    Z = lambda z: top + z * scale
    poly = layout['rooms'][0]['polygonXZ']
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx:.0f}" height="{Dpx:.0f}" viewBox="0 0 {Wpx:.0f} {Dpx:.0f}">',
         '<rect width="100%" height="100%" fill="#f7f8f5"/>',
         f'<text x="{Wpx / 2:.1f}" y="22" font-size="15" font-weight="700" font-family="Arial,sans-serif" text-anchor="middle" fill="#27342d">장생포문화창고 {h["title"]}</text>',
         f'<text x="{Wpx / 2:.1f}" y="40" font-size="10" font-family="Arial,sans-serif" text-anchor="middle" fill="#5b6a61">{h["W"]:g}m × {h["D"]:g}m · 벽 높이 {h["H"]:g}m · 출처: {h["source"]}</text>',
         '<polygon points="' + ' '.join(f'{X(x):.1f},{Z(z):.1f}' for x, z in poly) + '" fill="#eef2ed"/>']
    for w in layout['walls']:
        (ax, az), (bx, bz) = w['aXZ'], w['bXZ']
        if w['kind'] == 'movable_partition':
            s.append(f'<line x1="{X(ax):.1f}" y1="{Z(az):.1f}" x2="{X(bx):.1f}" y2="{Z(bz):.1f}" stroke="#6f7d75" stroke-width="3" stroke-dasharray="5 3"/>')
            continue
        color, width = ('#d69a6b', 5) if w['hangable'] else ('#2c3933', 3)
        t = 0.0
        for o0, o1 in w['openingsAlongWallFraction'] + [[1.0, 1.0]]:
            if o0 > t:
                s.append(f'<line x1="{X(ax + (bx - ax) * t):.1f}" y1="{Z(az + (bz - az) * t):.1f}" x2="{X(ax + (bx - ax) * o0):.1f}" y2="{Z(az + (bz - az) * o0):.1f}" stroke="{color}" stroke-width="{width}"/>')
            if o1 > o0:
                mx, mz = ax + (bx - ax) * (o0 + o1) / 2, az + (bz - az) * (o0 + o1) / 2
                s.append(f'<line x1="{X(ax + (bx - ax) * o0):.1f}" y1="{Z(az + (bz - az) * o0):.1f}" x2="{X(ax + (bx - ax) * o1):.1f}" y2="{Z(az + (bz - az) * o1):.1f}" stroke="#32936a" stroke-width="2" stroke-dasharray="3 3"/>')
                s.append(f'<text x="{X(mx) + 4:.1f}" y="{Z(mz) + 4:.1f}" font-size="10" font-family="Arial,sans-serif" fill="#236c4a">입구</text>')
            t = max(t, o1)
        if not w['hangable'] and not w['openingsAlongWallFraction'] and not w['name'].startswith('빛의 방'):
            mx, mz = (ax + bx) / 2, (az + bz) / 2
            if abs(ax - bx) < 1e-6:   # 세로 벽: 벽 안쪽(방 쪽)에 세로 방향 이름
                inside = -1 if ax > h['W'] / 2 else 1
                s.append(f'<text x="{X(mx) + inside * 6:.1f}" y="{Z(mz) + 3:.1f}" font-size="9" font-family="Arial,sans-serif" text-anchor="{"start" if inside > 0 else "end"}" fill="#2c3933">{w["name"]}</text>')
            else:
                s.append(f'<text x="{X(mx):.1f}" y="{Z(mz) - 5:.1f}" font-size="9" font-family="Arial,sans-serif" text-anchor="middle" fill="#2c3933">{w["name"]}</text>')
    if 'poly' in h:   # 특별전시관: 빛의 방(전시실 밖) 표시
        lx0, lz0, lx1 = h['poly'][5][0], h['poly'][4][1], h['poly'][4][0]
        s.append(f'<text x="{X((lx0 + lx1) / 2):.1f}" y="{Z((lz0 + h["D"]) / 2) + 4:.1f}" font-size="11" font-weight="700" font-family="Arial,sans-serif" text-anchor="middle" fill="#2c3933">빛의 방</text>')
    for c in layout['columns']:
        (x, z), (sw, sd) = c['xz'], c['sizeXZ']
        s.append(f'<rect x="{X(x - sw / 2):.1f}" y="{Z(z - sd / 2):.1f}" width="{sw * scale:.1f}" height="{sd * scale:.1f}" fill="#e9c4a6" stroke="#a5795a"/>')
    ly = Dpx - 30
    s += [f'<line x1="{pad}" y1="{ly}" x2="{pad + 22}" y2="{ly}" stroke="#d69a6b" stroke-width="5"/>',
          f'<text x="{pad + 28}" y="{ly + 4}" font-size="10" font-family="Arial,sans-serif" fill="#27342d">고정벽(작품 거는 벽)</text>',
          f'<line x1="{pad + 150}" y1="{ly}" x2="{pad + 172}" y2="{ly}" stroke="#6f7d75" stroke-width="3" stroke-dasharray="5 3"/>',
          f'<text x="{pad + 178}" y="{ly + 4}" font-size="10" font-family="Arial,sans-serif" fill="#27342d">이동식 가벽</text>',
          f'<rect x="{pad + 260}" y="{ly - 6}" width="12" height="12" fill="#e9c4a6" stroke="#a5795a"/>',
          f'<text x="{pad + 278}" y="{ly + 4}" font-size="10" font-family="Arial,sans-serif" fill="#27342d">기둥(크기 가정)</text>',
          f'<text x="{pad}" y="{ly + 20}" font-size="9" font-family="Arial,sans-serif" fill="#6a756e">치수 없는 부분(기둥 크기·입구 위치 등)은 도면 비율로 추정</text>',
          '</svg>']
    return 'data:image/svg+xml;base64,' + base64.b64encode(''.join(s).encode()).decode()


def main():
    text = INDEX.read_text(encoding='utf-8')
    m = re.search(r'(<script id="floorplanAssetData" type="application/json">)(.*?)(</script>)', text, re.S)
    data = json.loads(m.group(2))
    for builder in (gallery_b, gallery_c, special_hall):
        asset = make_asset(builder())
        data[asset['layout']['id']] = asset
        L = asset['layout']
        print(L['id'], L['title'], f"{L['rooms'][0]['areaM2Approx']}m2", L['generatedAsset']['boundsM'])
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    INDEX.write_text(text[:m.start(2)] + payload + text[m.end(2):], encoding='utf-8', newline='')


if __name__ == '__main__':
    main()
