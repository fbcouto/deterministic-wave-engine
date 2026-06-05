struct Particle {
    pos: vec2<f32>,
    vel: vec2<f32>,
    spin: f32,
    mass: f32,
};

struct LinearPotential {
    gradient_strength: f32, // Equivalente à corrente mecânica em laboratório
    shear_modulus: f32,     // N_{VAC} da teoria DGM
    dt: f32,
};

@group(0) @binding(0) var<storage, read_write> particles: array<Particle>;
@group(0) @binding(1) var<uniform> env: LinearPotential;

@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let idx = global_id.x;
    if (idx >= arrayLength(&particles)) { return; }
    
    var p = particles[idx];
    
    // Potencial linear externo atuando contra a direção transversal
    // No experimento Rozenman/Bush, isto cancela a auto-aceleração transversal do pacote de Airy
    let drift_force = vec2<f32>(0.0, -env.gradient_strength * p.mass);
    
    // Efeito Magnus: Acoplamento do Spin à Tensão de Cisalhamento (Shear Modulus)
    // Partículas Gaussianas dispersariam aqui, mas o perfil assimétrico do Airy acoplado
    // ao Magnus anula a dispersão.
    let magnus_lift = vec2<f32>(
        -p.vel.y * p.spin * env.shear_modulus,
        p.vel.x * p.spin * env.shear_modulus
    );
    
    // Atualização cinemática determinística completa
    let total_acceleration = drift_force + magnus_lift;
    
    p.vel = p.vel + (total_acceleration * env.dt);
    p.pos = p.pos + (p.vel * env.dt);
    
    particles[idx] = p;
}