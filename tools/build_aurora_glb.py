from __future__ import annotations

from pathlib import Path
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "demo-car.glb"
APP_PATH = ROOT / "app.js"


def material(name, rgba, metallic=0.0, roughness=0.5, emissive=None, alpha_mode=None):
    kwargs = {
        "name": name,
        "baseColorFactor": [channel / 255 for channel in rgba],
        "metallicFactor": metallic,
        "roughnessFactor": roughness,
        "doubleSided": True,
    }
    if emissive is not None:
        kwargs["emissiveFactor"] = emissive
    if alpha_mode is not None:
        kwargs["alphaMode"] = alpha_mode
    return PBRMaterial(**kwargs)


MATERIALS = {
    "CarPaint": material("CarPaint", [71, 120, 190, 255], 0.75, 0.22),
    "Glass": material("Glass", [20, 38, 60, 210], 0.15, 0.10, alpha_mode="BLEND"),
    "Tire": material("Tire", [10, 12, 16, 255], 0.0, 0.92),
    "Rim": material("Rim", [180, 190, 205, 255], 0.92, 0.16),
    "Chrome": material("Chrome", [205, 215, 230, 255], 0.95, 0.10),
    "Trim": material("Trim", [20, 25, 34, 255], 0.25, 0.55),
    "Headlight": material("Headlight", [255, 240, 190, 255], 0.1, 0.18, [1.0, 0.72, 0.25]),
    "Taillight": material("Taillight", [255, 65, 55, 255], 0.05, 0.24, [0.9, 0.06, 0.03]),
    "License": material("License", [235, 238, 245, 255], 0.05, 0.55),
    "Brake": material("Brake", [105, 110, 120, 255], 0.8, 0.25),
    "Caliper": material("Caliper", [220, 55, 40, 255], 0.45, 0.28),
}


def assign(mesh, material_name, object_name):
    mesh.visual = TextureVisuals(material=MATERIALS[material_name])
    mesh.metadata["name"] = object_name
    return mesh


def transformed(mesh, translation=(0, 0, 0), scale=(1, 1, 1), rotation=None):
    result = mesh.copy()
    matrix = np.eye(4)
    matrix[:3, :3] = np.diag(scale)
    if rotation is not None:
        matrix = trimesh.transformations.euler_matrix(*rotation) @ matrix
    matrix[:3, 3] = translation
    result.apply_transform(matrix)
    return result


def loft(xs, widths, bottoms, tops, squareness=3.5, ring_points=32):
    xs = np.asarray(xs, dtype=float)
    widths = np.asarray(widths, dtype=float)
    bottoms = np.asarray(bottoms, dtype=float)
    tops = np.asarray(tops, dtype=float)

    vertices = []
    for x, width, bottom, top in zip(xs, widths, bottoms, tops):
        center_y = (bottom + top) / 2
        half_height = (top - bottom) / 2
        for point in range(ring_points):
            angle = 2 * np.pi * point / ring_points
            cosine = np.cos(angle)
            sine = np.sin(angle)
            z = width * np.sign(cosine) * abs(cosine) ** (2 / squareness)
            y = center_y + half_height * np.sign(sine) * abs(sine) ** (2 / squareness)
            if y < center_y:
                z *= 0.93 + 0.07 * ((y - bottom) / (center_y - bottom + 1e-9))
            vertices.append([x, y, z])

    faces = []
    station_count = len(xs)

    for station in range(station_count - 1):
        for point in range(ring_points):
            next_point = (point + 1) % ring_points
            a = station * ring_points + point
            b = station * ring_points + next_point
            c = (station + 1) * ring_points + next_point
            d = (station + 1) * ring_points + point
            faces.extend(([a, b, c], [a, c, d]))

    first_center = len(vertices)
    last_center = first_center + 1
    vertices.extend(
        [
            [xs[0], (bottoms[0] + tops[0]) / 2, 0],
            [xs[-1], (bottoms[-1] + tops[-1]) / 2, 0],
        ]
    )

    for point in range(ring_points):
        next_point = (point + 1) % ring_points
        faces.append([first_center, next_point, point])
        a = (station_count - 1) * ring_points + point
        b = (station_count - 1) * ring_points + next_point
        faces.append([last_center, a, b])

    mesh = trimesh.Trimesh(
        vertices=np.asarray(vertices),
        faces=np.asarray(faces),
        process=True,
    )
    mesh.fix_normals()
    return mesh


def add(scene, mesh, material_name, object_name):
    mesh = assign(mesh, material_name, object_name)
    scene.add_geometry(mesh, node_name=object_name, geom_name=object_name)


def build_model():
    scene = trimesh.Scene()

    xs = np.linspace(-2.55, 2.55, 25)
    widths = np.interp(
        xs,
        [-2.55, -2.3, -1.8, -1.0, 0, 1.0, 1.8, 2.3, 2.55],
        [0.58, 0.90, 1.04, 1.08, 1.10, 1.08, 1.00, 0.82, 0.45],
    )
    bottoms = np.interp(xs, [-2.55, -2.2, 2.2, 2.55], [0.36, 0.24, 0.24, 0.43])
    tops = np.interp(
        xs,
        [-2.55, -2.15, -1.5, -0.7, 0.5, 1.4, 2.15, 2.55],
        [0.72, 0.92, 1.00, 1.04, 1.08, 1.02, 0.86, 0.64],
    )
    add(scene, loft(xs, widths, bottoms, tops, 4.2, 40), "CarPaint", "BodyShell")

    cabin_x = np.linspace(-1.45, 1.05, 18)
    cabin_width = np.interp(
        cabin_x,
        [-1.45, -1.15, -0.55, 0.35, 0.85, 1.05],
        [0.56, 0.78, 0.83, 0.81, 0.64, 0.42],
    )
    cabin_bottom = np.interp(cabin_x, [-1.45, -1.15, 0.75, 1.05], [0.98, 1.02, 1.05, 0.96])
    cabin_top = np.interp(
        cabin_x,
        [-1.45, -1.15, -0.55, 0.25, 0.75, 1.05],
        [1.12, 1.55, 1.84, 1.88, 1.55, 1.13],
    )
    add(scene, loft(cabin_x, cabin_width, cabin_bottom, cabin_top, 3.2, 32), "Glass", "GlassCabin")

    roof_x = np.linspace(-1.05, 0.58, 12)
    roof_width = np.interp(roof_x, [-1.05, -0.7, 0.2, 0.58], [0.52, 0.67, 0.66, 0.48])
    roof_bottom = np.interp(roof_x, [-1.05, -0.5, 0.2, 0.58], [1.64, 1.79, 1.82, 1.62])
    add(scene, loft(roof_x, roof_width, roof_bottom, roof_bottom + 0.10, 3.0, 28), "CarPaint", "RoofPanel")

    add(
        scene,
        transformed(
            trimesh.creation.box(extents=[1.35, 0.09, 1.28]),
            translation=(1.35, 1.05, 0),
            rotation=(0, 0, -0.04),
        ),
        "CarPaint",
        "HoodDome",
    )

    static_parts = [
        ("FrontSplitter", [0.34, 0.18, 1.78], [2.56, 0.27, 0], "Trim"),
        ("RearDiffuser", [0.30, 0.20, 1.72], [-2.55, 0.30, 0], "Trim"),
        ("SideSkirtLeft", [3.65, 0.14, 0.12], [0, 0.29, 1.06], "Trim"),
        ("SideSkirtRight", [3.65, 0.14, 0.12], [0, 0.29, -1.06], "Trim"),
        ("FrontGrille", [0.08, 0.38, 0.90], [2.57, 0.61, 0], "Trim"),
        ("FrontPlate", [0.035, 0.18, 0.52], [2.61, 0.54, 0], "License"),
        ("RearPlate", [0.035, 0.18, 0.52], [-2.61, 0.58, 0], "License"),
    ]

    for name, extents, position, material_name in static_parts:
        add(
            scene,
            transformed(trimesh.creation.box(extents=extents), translation=position),
            material_name,
            name,
        )

    for side in (-1, 1):
        add(
            scene,
            transformed(
                trimesh.creation.box(extents=[0.07, 0.24, 0.34]),
                translation=(2.56, 0.48, side * 0.70),
            ),
            "Trim",
            f"FrontIntake{side}",
        )

        headlight = transformed(
            trimesh.creation.icosphere(subdivisions=2, radius=1),
            translation=(2.47, 0.88, side * 0.67),
            scale=(0.10, 0.13, 0.36),
        )
        add(scene, headlight, "Headlight", f"Headlight{side}")

        taillight = transformed(
            trimesh.creation.icosphere(subdivisions=2, radius=1),
            translation=(-2.45, 0.83, side * 0.70),
            scale=(0.10, 0.12, 0.33),
        )
        add(scene, taillight, "Taillight", f"Taillight{side}")

        mirror = transformed(
            trimesh.creation.icosphere(subdivisions=2, radius=1),
            translation=(0.62, 1.38, side * 1.03),
            scale=(0.22, 0.11, 0.13),
        )
        add(scene, mirror, "CarPaint", f"Mirror{side}")

        exhaust = trimesh.creation.cylinder(radius=0.07, height=0.18, sections=24)
        exhaust.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
        exhaust.apply_translation([-2.58, 0.34, side * 0.58])
        add(scene, exhaust, "Chrome", f"Exhaust{side}")

    for x in (-1.62, 1.62):
        for z in (-1.05, 1.05):
            suffix = f"{'F' if x > 0 else 'R'}{'L' if z > 0 else 'R'}"

            tire = trimesh.creation.torus(
                major_radius=0.36,
                minor_radius=0.14,
                major_sections=48,
                minor_sections=16,
            )
            tire.apply_translation([x, 0.50, z])
            add(scene, tire, "Tire", f"Tire{suffix}")

            rim = trimesh.creation.cylinder(radius=0.31, height=0.18, sections=48)
            rim.apply_translation([x, 0.50, z])
            add(scene, rim, "Rim", f"Rim{suffix}")

            brake = trimesh.creation.cylinder(radius=0.22, height=0.19, sections=48)
            brake.apply_translation([x, 0.50, z])
            add(scene, brake, "Brake", f"BrakeDisc{suffix}")

            for spoke_index in range(5):
                angle = 2 * np.pi * spoke_index / 5
                spoke = trimesh.creation.box(extents=[0.025, 0.24, 0.055])
                spoke.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1]))
                spoke.apply_translation([x, 0.50, z + (0.10 if z > 0 else -0.10)])
                add(scene, spoke, "Chrome", f"Spoke{suffix}{spoke_index}")

            caliper = trimesh.creation.box(extents=[0.08, 0.20, 0.08])
            caliper.apply_translation([x + 0.18, 0.50, z])
            add(scene, caliper, "Caliper", f"Caliper{suffix}")

    for x in (-0.86, 0.02, 0.72):
        for side in (-1, 1):
            pillar = trimesh.creation.box(extents=[0.07, 0.68, 0.055])
            pillar.apply_translation([x, 1.43, side * 0.83])
            add(scene, pillar, "Trim", f"Pillar{x}{side}")

    for x in (-0.60, 0.45):
        for side in (-1, 1):
            handle = trimesh.creation.box(extents=[0.20, 0.045, 0.04])
            handle.apply_translation([x, 1.00, side * 1.095])
            add(scene, handle, "Chrome", f"Handle{x}{side}")

    add(
        scene,
        transformed(
            trimesh.creation.box(extents=[0.42, 0.08, 1.18]),
            translation=(-2.03, 1.13, 0),
            rotation=(0, 0, 0.02),
        ),
        "CarPaint",
        "RearSpoiler",
    )

    for side in (-1, 1):
        add(
            scene,
            transformed(
                trimesh.creation.box(extents=[0.08, 0.18, 0.06]),
                translation=(-2.02, 1.03, side * 0.42),
            ),
            "Trim",
            f"SpoilerSupport{side}",
        )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_bytes(scene.export(file_type="glb"))


def replace_once(text, old, new):
    if old not in text:
        raise RuntimeError(f"Expected app.js fragment was not found:\n{old[:160]}")
    return text.replace(old, new, 1)


def patch_app():
    text = APP_PATH.read_text(encoding="utf-8")

    if "RoomEnvironment" not in text:
        text = replace_once(
            text,
            'import { GLTFLoader } from "https://esm.sh/three@0.166.1/examples/jsm/loaders/GLTFLoader.js";',
            'import { GLTFLoader } from "https://esm.sh/three@0.166.1/examples/jsm/loaders/GLTFLoader.js";\n'
            'import { RoomEnvironment } from "https://esm.sh/three@0.166.1/examples/jsm/environments/RoomEnvironment.js";',
        )

    text = text.replace(
        '"GLB Demo":[["Concept Car","glb","./models/demo-car.glb"]],',
        '"Aurora Studio":[["Aurora GT","glb","./models/demo-car.glb"]],',
    )
    text = text.replace("GLB Demo Concept Car", "Aurora Studio Aurora GT")
    text = text.replace(
        "Настоящий GLB-файл · потяните мышкой для вращения",
        "Детализированная GLB-модель · потяните мышкой для вращения",
    )
    text = text.replace('brand.value="GLB Demo"', 'brand.value="Aurora Studio"')

    old_paint = (
        'paint=(object,color)=>object.traverse(c=>{if(!c.isMesh||!c.material)return;'
        'const mats=(Array.isArray(c.material)?c.material:[c.material]).map(m=>{'
        'const n=m.clone();n.vertexColors=false;n.color?.set(color);n.metalness=.55;'
        'n.roughness=.32;return n});c.material=Array.isArray(c.material)?mats:mats[0]}),fit='
    )
    new_paint = (
        'paint=(object,color)=>object.traverse(c=>{if(!c.isMesh||!c.material)return;'
        'const mats=(Array.isArray(c.material)?c.material:[c.material]).map(m=>{'
        'const n=m.clone(),name=(n.name||"").toLowerCase();'
        'if(/carpaint|bodypaint|exteriorpaint|body|paint/.test(name)){'
        'n.color?.set(color);n.metalness=.76;n.roughness=.22;n.envMapIntensity=1.25}'
        'return n});c.material=Array.isArray(c.material)?mats:mats[0];'
        'c.castShadow=true;c.receiveShadow=true}),fit='
    )
    if old_paint in text:
        text = replace_once(text, old_paint, new_paint)

    old_renderer = (
        'const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});'
        'renderer.setPixelRatio(Math.min(devicePixelRatio,2));'
        'renderer.outputColorSpace=THREE.SRGBColorSpace;host.appendChild(renderer.domElement);'
    )
    new_renderer = (
        'const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});'
        'renderer.setPixelRatio(Math.min(devicePixelRatio,2));'
        'renderer.outputColorSpace=THREE.SRGBColorSpace;'
        'renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;'
        'renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;'
        'host.appendChild(renderer.domElement);'
        'const pmrem=new THREE.PMREMGenerator(renderer);'
        'scene.environment=pmrem.fromScene(new RoomEnvironment(),.04).texture;pmrem.dispose();'
    )
    if old_renderer in text:
        text = replace_once(text, old_renderer, new_renderer)

    text = text.replace(
        'const key=new THREE.DirectionalLight(0xffffff,3.2);key.position.set(6,9,7);scene.add(key);',
        'const key=new THREE.DirectionalLight(0xffffff,4.2);key.position.set(6,9,7);'
        'key.castShadow=true;key.shadow.mapSize.set(2048,2048);scene.add(key);',
    )
    text = text.replace(
        'floor.rotation.x=-Math.PI/2;floor.position.y=-.56;scene.add(floor);',
        'floor.rotation.x=-Math.PI/2;floor.position.y=-.56;floor.receiveShadow=true;scene.add(floor);',
    )
    text = text.replace('status("Загрузка GLB…")', 'status("Загрузка Aurora GT…")')
    text = text.replace(
        'car.add(badge("GLB",.6,new THREE.Vector3(2.28,.5,0),Math.PI/2));'
        'car.add(badge("CONCEPT",.92,new THREE.Vector3(-2.28,.52,0),-Math.PI/2));',
        'car.add(badge("AURORA",.72,new THREE.Vector3(2.36,.62,0),Math.PI/2));'
        'car.add(badge("GT",.36,new THREE.Vector3(-2.36,.64,0),-Math.PI/2));',
    )
    text = text.replace('status("GLB загружен","is-ready")', 'status("Aurora GT загружена","is-ready")')
    text = text.replace(
        'hint.textContent=data[1]==="glb"?"Настоящий GLB-файл · потяните мышкой для вращения"',
        'hint.textContent=data[1]==="glb"?"Детализированная GLB-модель · потяните мышкой для вращения"',
    )

    APP_PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    build_model()
    patch_app()
    marker = ROOT / "models" / "preview-note.txt"
    if marker.exists():
        marker.unlink()
    print(f"Created {MODEL_PATH} ({MODEL_PATH.stat().st_size} bytes)")
