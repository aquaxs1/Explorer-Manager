/*
 * Explorer Manager — files that sort themselves.
 *
 * Three folders stand in a row. New files keep arriving from the upper left,
 * and each one flies to the folder its type belongs in — documents, media,
 * archives — the way a rule moves it on your disk. Click or tap anywhere and
 * a whole download folder's worth arrives at once.
 */
export default function scene(stage) {
  const { THREE, frame } = stage;
  stage.lights({ key: 2.6 });
  stage.environment(0.8);

  const root = new THREE.Group();
  frame.add(root);
  root.add(stage.halo(stage.accent, 8, 0.22));

  /* ---------------------------------------------------------- folders */

  const KINDS = [
    { name: 'Documents', color: new THREE.Color('#ffc93c'), types: ['.pdf', '.docx', '.xlsx'], tint: '#e8eefc' },
    { name: 'Media', color: new THREE.Color('#4d9fff'), types: ['.mkv', '.png', '.mp3'], tint: '#dff1ff' },
    { name: 'Archives', color: new THREE.Color('#b08cff'), types: ['.zip', '.rar', '.7z'], tint: '#efe6ff' },
  ];

  const folders = KINDS.map((kind, i) => {
    const group = new THREE.Group();
    const material = stage.mat.solid(kind.color, { roughness: 0.42, metalness: 0.15 });
    const dark = stage.mat.solid(kind.color.clone().multiplyScalar(0.62), { roughness: 0.5 });

    const back = new THREE.Mesh(stage.slab(1.5, 1.05, 0.07, 0.1), dark);
    back.position.set(0, 0.05, -0.16);
    const tab = new THREE.Mesh(stage.slab(0.62, 0.26, 0.07, 0.08), dark);
    tab.position.set(-0.42, 0.64, -0.16);

    // The front flap hinges at the bottom edge, so it can open like a mouth.
    const hinge = new THREE.Group();
    hinge.position.set(0, -0.48, 0.12);
    const front = new THREE.Mesh(stage.slab(1.5, 0.9, 0.07, 0.1), material);
    front.position.set(0, 0.45, 0);
    hinge.add(front);

    const label = stage.plate(1.3, 0.3, (g, w, h) => {
      g.fillStyle = 'rgba(20, 14, 0, 0.78)';
      g.font = stage.font.body(Math.round(h * 0.52), 700);
      g.textBaseline = 'middle';
      g.fillText(kind.name, w * 0.06, h * 0.52);
    });
    label.position.set(0, 0.34, 0.04);
    hinge.add(label);

    group.add(back, tab, hinge);
    group.position.set((i - 1) * 1.75, -1.05 + (i === 1 ? -0.12 : 0), i === 1 ? 0.5 : 0);
    group.rotation.y = (1 - i) * 0.24;
    root.add(group);
    return { group, hinge, kind, gulp: 0, mouth: new THREE.Vector3() };
  });

  /* ------------------------------------------------------------ files */

  const pageGeometry = stage.slab(0.62, 0.8, 0.03, 0.06);
  const POOL = Math.round(16 * stage.quality) + 6;
  const files = [];

  const drawFace = (g, w, h, file) => {
    if (!file.kind) return;
    g.fillStyle = `#${file.kind.color.getHexString()}`;
    if (g.roundRect) {
      g.beginPath();
      g.roundRect(w * 0.12, h * 0.1, w * 0.5, h * 0.2, h * 0.04);
      g.fill();
    } else {
      g.fillRect(w * 0.12, h * 0.1, w * 0.5, h * 0.2);
    }
    g.fillStyle = '#10131c';
    g.font = stage.font.mono(Math.round(h * 0.13), 500);
    g.textBaseline = 'middle';
    g.fillText(file.ext, w * 0.16, h * 0.205);
    g.fillStyle = '#aab3c8';
    for (let i = 0; i < 5; i += 1) g.fillRect(w * 0.12, h * (0.42 + i * 0.1), w * (0.44 + ((i * 29) % 30) / 100), h * 0.035);
  };

  for (let i = 0; i < POOL; i += 1) {
    const file = { t: 1, life: 2.6, from: new THREE.Vector3(), mid: new THREE.Vector3(), folder: null, spin: 0, kind: null, ext: '' };
    const group = new THREE.Group();
    const paper = new THREE.Mesh(pageGeometry, stage.mat.solid(0xf4f6fb, { roughness: 0.65, transparent: true }));
    const face = stage.plate(0.62, 0.8, (g, w, h) => drawFace(g, w, h, file));
    face.position.z = 0.018;
    group.add(paper, face);
    group.visible = false;
    root.add(group);
    Object.assign(file, { group, paper, face });
    files.push(file);
  }

  let next = 0;
  let counter = 0;
  const spawn = (delay = 0) => {
    const file = files.find((f) => f.t >= 1);
    if (!file) return;
    const index = counter % folders.length;
    const folder = folders[(index + (counter % 5 === 0 ? 1 : 0)) % folders.length];
    const kind = folder.kind;
    counter += 1;
    file.kind = kind;
    file.ext = kind.types[counter % kind.types.length];
    file.face.userData.redraw();
    file.folder = folder;
    file.t = -delay;
    file.life = 2.3 + Math.random() * 0.8;
    file.from.set(-1.6 + Math.random() * 3.6, 2.7 + Math.random() * 1.1, -1.8 + Math.random() * 2.2);
    file.mid.set(folder.group.position.x * 0.6 - 0.5 + Math.random(), 1.3 + Math.random() * 0.8, 1.1 + Math.random());
    file.spin = (Math.random() - 0.5) * 5;
  };

  stage.onClick(() => {
    for (let i = 0; i < 7; i += 1) spawn(i * 0.09);
  });

  stage.dust({ count: 180, radius: 6.5, opacity: 0.5 });

  const a = new THREE.Vector3();
  const b = new THREE.Vector3();

  stage.onFrame((time, delta) => {
    root.rotation.y = -0.22 + stage.yaw * 0.7 + Math.sin(time * 0.3) * 0.04;
    root.rotation.x = 0.1 + stage.pitch * 0.7;
    root.position.y = Math.sin(time * 0.7) * 0.05;

    if (time > next) {
      spawn();
      next = time + 0.42 + Math.random() * 0.3;
    }

    for (const folder of folders) {
      folder.gulp = Math.max(0, folder.gulp - delta * 2.4);
      folder.hinge.rotation.x = 0.22 + folder.gulp * 0.5 + Math.sin(time * 1.2 + folder.group.position.x) * 0.02;
      folder.group.scale.setScalar(1 + folder.gulp * 0.06);
      // Where a file disappears: just above the opening.
      folder.mouth.copy(folder.group.position).add(a.set(0, 0.2, 0.02));
    }

    for (const file of files) {
      if (file.t >= 1) {
        file.group.visible = false;
        continue;
      }
      const before = file.t;
      file.t += delta / file.life;
      if (file.t < 0) {
        file.group.visible = false;
        continue;
      }
      file.group.visible = true;
      const t = Math.min(1, file.t);
      const e = t * t * (3 - 2 * t);
      // A curve from where it appeared, over a high point, down into its folder.
      a.lerpVectors(file.from, file.mid, e);
      b.lerpVectors(file.mid, file.folder.mouth, e);
      file.group.position.lerpVectors(a, b, e);
      const settle = Math.max(0, 1 - e * 1.15);
      file.group.rotation.set(settle * file.spin * 0.4, settle * file.spin, settle * file.spin * 0.6 + (1 - settle) * 0);
      const fade = t > 0.86 ? 1 - (t - 0.86) / 0.14 : Math.min(1, t * 12);
      file.group.scale.setScalar(0.35 + 0.65 * Math.min(1, fade + 0.15));
      file.paper.material.opacity = fade;
      file.face.material.opacity = fade;
      if (before < 0.86 && file.t >= 0.86) file.folder.gulp = 1;
    }
  });
}
