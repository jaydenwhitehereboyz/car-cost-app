import * as THREE from "https://esm.sh/three@0.166.1";
import { GLTFLoader } from "https://esm.sh/three@0.166.1/examples/jsm/loaders/GLTFLoader.js";
import { RoomEnvironment } from "https://esm.sh/three@0.166.1/examples/jsm/environments/RoomEnvironment.js";

const nativeFetch = window.fetch.bind(window);

window.fetch = async (input, init) => {
  const requestedUrl = new URL(
    typeof input === "string" ? input : input.url,
    window.location.href
  );

  if (requestedUrl.pathname.endsWith("/models/demo-car.glb")) {
    const sourceResponse = await nativeFetch(
      new URL("./models/aurora-gt.glb.b64", window.location.href),
      { cache: "no-store" }
    );

    if (!sourceResponse.ok) {
      return sourceResponse;
    }

    const encoded = (await sourceResponse.text()).trim();
    const binary = atob(encoded);
    const bytes = new Uint8Array(binary.length);

    for (let index = 0; index < binary.length; index += 1) {
      bytes[index] = binary.charCodeAt(index);
    }

    return new Response(bytes, {
      status: 200,
      headers: {
        "Content-Type": "model/gltf-binary",
        "Content-Length": String(bytes.byteLength)
      }
    });
  }

  return nativeFetch(input, init);
};

const nativeMaterialClone = THREE.Material.prototype.clone;

THREE.Material.prototype.clone = function cloneMaterialSafely() {
  const cloned = nativeMaterialClone.call(this);
  const materialName = String(cloned.name || "").toLowerCase();
  const isBodyPaint = /carpaint|bodypaint|exteriorpaint|body|paint/.test(materialName);

  if (!isBodyPaint && cloned.color) {
    const originalColor = cloned.color.clone();
    cloned.color.set = () => {
      cloned.color.copy(originalColor);
      return cloned.color;
    };
  }

  return cloned;
};

const nativeParse = GLTFLoader.prototype.parse;

GLTFLoader.prototype.parse = function parseAurora(data, path, onLoad, onError) {
  return nativeParse.call(
    this,
    data,
    path,
    (gltf) => {
      gltf.scene.traverse((object) => {
        if (!object.isMesh) {
          return;
        }

        if (!object.geometry.getAttribute("normal")) {
          object.geometry.computeVertexNormals();
        }

        object.castShadow = true;
        object.receiveShadow = true;
      });

      onLoad(gltf);
    },
    onError
  );
};

const nativeRender = THREE.WebGLRenderer.prototype.render;

THREE.WebGLRenderer.prototype.render = function renderEnhanced(scene, camera) {
  if (!this.userData.auroraEnhanced) {
    this.userData.auroraEnhanced = true;
    this.toneMapping = THREE.ACESFilmicToneMapping;
    this.toneMappingExposure = 1.12;
    this.shadowMap.enabled = true;
    this.shadowMap.type = THREE.PCFSoftShadowMap;

    const environmentGenerator = new THREE.PMREMGenerator(this);
    scene.environment = environmentGenerator
      .fromScene(new RoomEnvironment(), 0.04)
      .texture;
    environmentGenerator.dispose();

    scene.traverse((object) => {
      if (object.isDirectionalLight) {
        object.castShadow = true;
        object.shadow.mapSize.set(1024, 1024);
      }

      if (object.isMesh) {
        object.castShadow = true;
        object.receiveShadow = true;
      }
    });
  }

  return nativeRender.call(this, scene, camera);
};

const nativeFillText = CanvasRenderingContext2D.prototype.fillText;
const nativeStrokeText = CanvasRenderingContext2D.prototype.strokeText;
const badgeNames = new Map([
  ["GLB", "AURORA"],
  ["CONCEPT", "GT"]
]);

CanvasRenderingContext2D.prototype.fillText = function fillAuroraBadge(text, ...args) {
  return nativeFillText.call(this, badgeNames.get(text) || text, ...args);
};

CanvasRenderingContext2D.prototype.strokeText = function strokeAuroraBadge(text, ...args) {
  return nativeStrokeText.call(this, badgeNames.get(text) || text, ...args);
};

await import("./app-core.js");

function relabelAurora() {
  document.querySelectorAll("option").forEach((option) => {
    if (option.textContent === "GLB Demo") {
      option.textContent = "Aurora Studio";
    }

    if (option.textContent === "Concept Car") {
      option.textContent = "Aurora GT";
    }
  });

  const selectedName = document.querySelector("#selectedCarName");
  const selectedHint = document.querySelector("#selectedCarHint");

  if (selectedName?.textContent === "GLB Demo Concept Car") {
    selectedName.textContent = "Aurora Studio Aurora GT";
  }

  if (selectedHint && selectedHint.textContent.includes("Настоящий GLB-файл")) {
    selectedHint.textContent = "Стилизованная GLB-модель · потяните мышкой для вращения";
  }
}

relabelAurora();

new MutationObserver(relabelAurora).observe(document.body, {
  childList: true,
  subtree: true,
  characterData: true
});
