struct Particle {
    position: vec4<f32>,
    velocity: vec4<f32>,
    orbital_energy: f32,
    helicity: f32,
    _padding: vec2<f32>,
}

@group(0) @binding(0)
var<storage, read_write> particles: array<Particle>;

fn get_noise_map(pos: vec2<f32>) -> f32 {
    return fract(sin(dot(pos, vec2<f32>(12.9898, 78.233))) * 43758.5453);
}

@compute @workgroup_size(256)
fn compute_anderson_localization(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let id = global_id.x;
    var vortex = particles[id];
    
    let dt = 0.05; // Delta time per micro-collision
    
    // Simula a evolução temporal: até 500 colisões contra a topografia desordenada
    for (var step: i32 = 0; step < 500; step++) {
        
        // Mapa topográfico dielétrico randomizado (Disordered Terrain) avaliado na posição ATUAL
        let terrain_density = get_noise_map(vortex.position.xy);
        
        // Dispersão e Arrasto Acústico (0.0 a 0.8)
        let scattering_friction = terrain_density * 0.8;
        
        // Atualização da Esteira do Vórtice baseada em reflexos multidirecionais
        vortex.velocity.x -= vortex.velocity.x * scattering_friction;
        vortex.velocity.y -= vortex.velocity.y * scattering_friction;
        
        // Atualiza a Posição com a velocidade residual
        // (Isso é vital para que a partícula caia em coordenadas de ruído diferentes a cada step)
        vortex.position.x += vortex.velocity.x * dt;
        vortex.position.y += vortex.velocity.y * dt;
        
        // Confinamento (Mean Squared Displacement atinge uma Assíntota)
        if (length(vortex.velocity.xy) < 0.01) {
             // O Vórtice atinge o aprisionamento termodinâmico
             vortex.velocity = vec4<f32>(0.0, 0.0, 0.0, vortex.velocity.w);
             break; // Rompe o loop temporal precocemente, a partícula está travada!
        }
    }
    
    particles[id] = vortex;
}