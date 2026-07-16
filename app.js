import * as THREE from "https://esm.sh/three@0.166.1";
import { OrbitControls } from "https://esm.sh/three@0.166.1/examples/jsm/controls/OrbitControls.js";

const expenseInputs = document.querySelectorAll("[data-expense]");
const purchasePriceInput = document.querySelector("#purchasePrice");
const depreciationRateInput = document.querySelector("#depreciationRate");

const monthlyTotalElement = document.querySelector("#monthlyTotal");
const weeklyTotalElement = document.querySelector("#weeklyTotal");
const yearlyTotalElement = document.querySelector("#yearlyTotal");
const monthlyDepreciationElement = document.querySelector("#monthlyDepreciation");

const currencyFormatter = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0
});

function getPositiveNumber(input) {
  const value = Number(input.value);
  return Number.isFinite(value) && value > 0 ? value : 0;
}

function calculateTotals() {
  let monthlyTotal = 0;

  expenseInputs.forEach((input) => {
    monthlyTotal += getPositiveNumber(input);
  });

  const purchasePrice = getPositiveNumber(purchasePriceInput);
  const depreciationRate = getPositiveNumber(depreciationRateInput);
  const monthlyDepreciation = purchasePrice * (depreciationRate / 100) / 12;

  monthlyTotal += monthlyDepreciation;

  const weeklyTotal = monthlyTotal * 12 / 52;
  const yearlyTotal = monthlyTotal * 12;

  monthlyDepreciationElement.textContent = `${currencyFormatter.format(monthlyDepreciation)} в месяц`;
  monthlyTotalElement.textContent = currencyFormatter.format(monthlyTotal);
  weeklyTotalElement.textContent = currencyFormatter.format(weeklyTotal);
  yearlyTotalElement.textContent = currencyFormatter.format(yearlyTotal);
}

function createCarScene() {
  const container = document.querySelector("#car3d");

  if (!container) {
    return;
  }

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x0e1219, 12, 22);

  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  camera.position.set(7.2, 4.1, 8.4);

  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true
  });

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.enablePan = false;
  controls.enableZoom = true;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 1.25;
  controls.minDistance = 6;
  controls.maxDistance = 14;
  controls.minPolarAngle = Math.PI / 3.5;
  controls.maxPolarAngle = Math.PI / 2.05;
  controls.target.set(0, 0.75, 0);

  scene.add(new THREE.HemisphereLight(0xdce8ff, 0x171b24, 2.5));

  const keyLight = new THREE.DirectionalLight(0xffffff, 3.2);
  keyLight.position.set(6, 9, 7);
  scene.add(keyLight);

  const rimLight = new THREE.DirectionalLight(0x789dff, 2.1);
  rimLight.position.set(-7, 4, -6);
  scene.add(rimLight);

  const floor = new THREE.Mesh(
    new THREE.CircleGeometry(7.5, 64),
    new THREE.MeshStandardMaterial({
      color: 0x141922,
      roughness: 0.92,
      metalness: 0.08
    })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.56;
  scene.add(floor);

  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(3.25, 64),
    new THREE.MeshBasicMaterial({
      color: 0x000000,
      transparent: true,
      opacity: 0.28,
      depthWrite: false
    })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.scale.set(1.25, 0.72, 1);
  shadow.position.y = -0.54;
  scene.add(shadow);

  const car = new THREE.Group();
  car.rotation.y = -0.55;
  scene.add(car);

  const bodyMaterial = new THREE.MeshStandardMaterial({
    color: 0x79869d,
    metalness: 0.72,
    roughness: 0.25
  });

  const trimMaterial = new THREE.MeshStandardMaterial({
    color: 0x161c27,
    metalness: 0.32,
    roughness: 0.55
  });

  const glassMaterial = new THREE.MeshStandardMaterial({
    color: 0x273b55,
    metalness: 0.18,
    roughness: 0.16
  });

  const tireMaterial = new THREE.MeshStandardMaterial({
    color: 0x0c1017,
    metalness: 0.08,
    roughness: 0.9
  });

  const rimMaterial = new THREE.MeshStandardMaterial({
    color: 0xa8b3c5,
    metalness: 0.8,
    roughness: 0.25
  });

  const frontLightMaterial = new THREE.MeshStandardMaterial({
    color: 0xffe3a0,
    emissive: 0xffc958,
    emissiveIntensity: 1.1,
    roughness: 0.25
  });

  const rearLightMaterial = new THREE.MeshStandardMaterial({
    color: 0xff5e59,
    emissive: 0xff3b36,
    emissiveIntensity: 0.9,
    roughness: 0.3
  });

  const body = new THREE.Mesh(
    new THREE.BoxGeometry(5.05, 1.05, 2.28),
    bodyMaterial
  );
  body.position.y = 0.48;
  car.add(body);

  const hood = new THREE.Mesh(
    new THREE.BoxGeometry(1.55, 0.34, 2.08),
    bodyMaterial
  );
  hood.position.set(1.72, 1.03, 0);
  hood.rotation.z = -0.05;
  car.add(hood);

  const trunk = new THREE.Mesh(
    new THREE.BoxGeometry(1.08, 0.3, 2.06),
    bodyMaterial
  );
  trunk.position.set(-1.92, 0.94, 0);
  trunk.rotation.z = 0.04;
  car.add(trunk);

  const cabin = new THREE.Mesh(
    new THREE.BoxGeometry(2.48, 0.98, 1.82),
    glassMaterial
  );
  cabin.position.set(-0.05, 1.36, 0);
  cabin.scale.set(1, 1, 0.96);
  car.add(cabin);

  const roof = new THREE.Mesh(
    new THREE.BoxGeometry(1.75, 0.18, 1.78),
    bodyMaterial
  );
  roof.position.set(-0.2, 1.92, 0);
  car.add(roof);

  const frontBumper = new THREE.Mesh(
    new THREE.BoxGeometry(0.28, 0.46, 2.18),
    trimMaterial
  );
  frontBumper.position.set(2.64, 0.21, 0);
  car.add(frontBumper);

  const rearBumper = new THREE.Mesh(
    new THREE.BoxGeometry(0.28, 0.46, 2.18),
    trimMaterial
  );
  rearBumper.position.set(-2.64, 0.21, 0);
  car.add(rearBumper);

  const lowerTrim = new THREE.Mesh(
    new THREE.BoxGeometry(4.55, 0.17, 2.34),
    trimMaterial
  );
  lowerTrim.position.set(0, -0.02, 0);
  car.add(lowerTrim);

  const wheelGeometry = new THREE.CylinderGeometry(0.57, 0.57, 0.48, 32);
  const rimGeometry = new THREE.CylinderGeometry(0.29, 0.29, 0.5, 24);

  const wheelPositions = [
    [1.7, -0.02, 1.18],
    [1.7, -0.02, -1.18],
    [-1.72, -0.02, 1.18],
    [-1.72, -0.02, -1.18]
  ];

  wheelPositions.forEach(([x, y, z]) => {
    const wheel = new THREE.Mesh(wheelGeometry, tireMaterial);
    wheel.rotation.x = Math.PI / 2;
    wheel.position.set(x, y, z);
    car.add(wheel);

    const rim = new THREE.Mesh(rimGeometry, rimMaterial);
    rim.rotation.x = Math.PI / 2;
    rim.position.set(x, y, z);
    car.add(rim);
  });

  const frontLightLeft = new THREE.Mesh(
    new THREE.BoxGeometry(0.13, 0.25, 0.48),
    frontLightMaterial
  );
  frontLightLeft.position.set(2.55, 0.61, 0.66);
  car.add(frontLightLeft);

  const frontLightRight = frontLightLeft.clone();
  frontLightRight.position.z = -0.66;
  car.add(frontLightRight);

  const rearLightLeft = new THREE.Mesh(
    new THREE.BoxGeometry(0.13, 0.24, 0.46),
    rearLightMaterial
  );
  rearLightLeft.position.set(-2.55, 0.61, 0.67);
  car.add(rearLightLeft);

  const rearLightRight = rearLightLeft.clone();
  rearLightRight.position.z = -0.67;
  car.add(rearLightRight);

  const frontGrille = new THREE.Mesh(
    new THREE.BoxGeometry(0.14, 0.32, 0.82),
    trimMaterial
  );
  frontGrille.position.set(2.59, 0.35, 0);
  car.add(frontGrille);

  function resizeScene() {
    const width = container.clientWidth;
    const height = container.clientHeight;

    if (width === 0 || height === 0) {
      return;
    }

    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
  }

  const resizeObserver = new ResizeObserver(resizeScene);
  resizeObserver.observe(container);
  resizeScene();

  renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render(scene, camera);
  });
}

const calculatorInputs = document.querySelectorAll("input");

calculatorInputs.forEach((input) => {
  input.addEventListener("input", calculateTotals);
});

calculateTotals();
createCarScene();
