// ---------- room: basement
const floor = mk(new THREE.PlaneGeometry(30, 30), mat(0x3e3a36, {roughness: 1}), 0, 0, 0);
floor.rotation.x = -Math.PI / 2;
const wallM = mat(0x2a2825);
mk(new THREE.BoxGeometry(30, 20, 0.5), wallM, 0, 10, -10);
mk(new THREE.BoxGeometry(0.5, 20, 30), wallM, -10, 10, 0);
const light = new THREE.PointLight(0xffcc88, 150, 25);
light.position.set(0, 8, 2); scene.add(light);

// Gags 3D Props
// Aseguramos que 'phone' esté definido globalmente o accesible para no romper el render
window.phone = mk(new THREE.BoxGeometry(0.8, 1.6, 0.1), mat(0x222), 0, 0.8, 2);
window.K = window.K || ((key) => key === 'telefono' ? 2.0 : null); 

const outlet = mk(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial(), 5, 4, -9.8);
outlet.material.map = canvasTex(256, 256, (ctx) => {
    ctx.fillStyle = "#fff"; ctx.fillRect(0,0,256,256);
    ctx.strokeStyle = "#000"; ctx.lineWidth = 10;
    ctx.strokeRect(50, 50, 156, 156);
    ctx.fillStyle = "#000"; ctx.fillRect(80, 100, 30, 50); ctx.fillRect(140, 100, 30, 50);
});

const cable = mk(new THREE.CylinderGeometry(0.05, 0.05, 4), mat(0xffffff), 0, 0, 0);
const battery = mk(new THREE.BoxGeometry(1, 1, 1), mat(0x00ff00), 0, 1, 2);
const tentacle = mk(new THREE.CylinderGeometry(0.1, 0.02, 2), mat(0xff6666), 5, 4, -9);

// ---------- timeline
const getPhoneTime = () => (typeof K !== 'undefined' && K('telefono') ? K('telefono') : 2.0);
const T_HOOKEND = getPhoneTime() - 0.3;
const SW = new Set(['pinche', 'pendejo', 'culero', 'chingada', 'verga', 'mamada', 'puta', 'mediocre']);
const isSW = w => SW.has(norm(w));
const swT = words.filter(w => isSW(w[0])).map(w => w[1]);
const blinks = [1.5, 5.0, 10.0, 15.0, 20.0];

function applyHero(t) {
    hero.position.set(0, 0, 0);
    if(t < 4) {
        if(typeof arms !== 'undefined') {
            if(arms[0]) arms[0].rotation.z = -0.5 + Math.sin(t * 10) * 0.2;
            if(arms[1]) arms[1].rotation.z = 0.5 - Math.sin(t * 10) * 0.2;
        }
    }
    hero.updateMatrixWorld(true);
    if(typeof head !== 'undefined') head.getWorldPosition(HP);
}

function applyProps(t) {
    if (typeof phone !== 'undefined') {
        if(t > 10.6 && t < 11.3) phone.scale.set(1 + Math.sin(t * 50)*0.1, 1, 1);
        else phone.scale.set(1, 1, 1);
        
        if(t > 21.0) phone.position.y += (t - 21.0) * 0.1;
    }
    
    if(t > 13.7 && t < 16.7) battery.scale.set(1 + (t-13), 1 + (t-13), 1);
    tentacle.rotation.z = Math.sin(t * 10);
}

const CUTS = [0, 1, 2.5, 4, 5.5, 7, 9, 11, 13, 15, 17, 18.5, 20, 21.4];
const shots = CUTS.map((_, i) => (u, t) => ({
    p: [Math.sin(i) * 5, 4, 10], l: [0, 2, 0], f: 45
}));

function applyCam(t) {
    let si = 0; while(si < CUTS.length - 1 && t >= CUTS[si+1]) si++;
    const r = shots[si](0, t);
    cam.position.set(r.p[0], r.p[1], r.p[2]);
    cam.lookAt(r.l[0], r.l[1], r.l[2]);
}

const HOOK_TEXT = "¡CARGA ESA MADRE!";
const TITLE_HTML = "PUTOR.IALES<br>TELEFONOS";
const TITLE_WORD = "cargado";
const PILL_TEXT = "TUTORIAL #1";
const PILL = [0, 5];
const FLASH = [[5.9, 0.5], [9.9, 0.5], [19.0, 0.8]];