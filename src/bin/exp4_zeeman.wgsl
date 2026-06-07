struct Particle {
    position: vec4<f32>,
    velocity: vec4<f32>,
    orbital_energy: f32,
    helicity: f32,
    _padding: vec2<f32>,
}

@group(0) @binding(0)
var<storage, read_write> particles: array<Particle>;

@compute @workgroup_size(256)
fn compute_zeeman_splitting(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let id = global_id.x;
    var vortex = particles[id];
    
    let dt = 0.05;
    
    // Loop temporal para acumular o cisalhamento macroscópico do banho de vácuo
    for (var step: u32 = 0u; step < 500u; step++) {
        // Matriz Rotacional (Coriolis Global / Banho Fluídico Rotatório)
        let rotation_speed = 0.05;
        let center = vec2<f32>(0.0, 0.0);
        let radius_vec = vortex.position.xy - center;
        let fluid_macroscopic_velocity = vec2<f32>(-radius_vec.y, radius_vec.x) * rotation_speed;
        
        // O Produto Escalar (dot) JÁ carrega o sinal direcional natural!
        // Alinhado = Positivo (Ressonância). Oposto = Negativo (Cisalhamento).
        let fluid_coupling = dot(vortex.velocity.xy, fluid_macroscopic_velocity);
        
        // Adicionamos diretamente. O prógrado soma (+), o retrógrado subtrai (-).
        vortex.orbital_energy += fluid_coupling * 0.5 * dt; 
        
        // Atualiza a posição da órbita wobble
        vortex.position.x += vortex.velocity.x * dt;
        vortex.position.y += vortex.velocity.y * dt;
    }
    
    particles[id] = vortex;
}