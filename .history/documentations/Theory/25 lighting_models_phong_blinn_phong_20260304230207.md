# Lighting Models: Phong and Blinn-Phong 

## The Stage Lighting Analogy

Lighting models can be understood through a theater stage with different lighting techniques:

- **The Stage Lights** = Light sources (position, color, intensity)
- **The Actors** = 3D objects with surfaces
- **The Audience** = The camera/viewer
- **Ambient Light** = The general house lights that illuminate everything evenly
- **Diffuse Light** = The main spotlights that create shading based on surface angle
- **Specular Light** = The shiny spotlights that create glints and highlights

**Just as a lighting designer combines different types of lights to create a scene, graphics programmers combine lighting components to make 3D objects look realistic.**

---

## Part 1: Why Do We Need Lighting Models?

### The Problem: Flat Shading

```
WITHOUT LIGHTING:                WITH LIGHTING:
    ▲                                 ▲
   / \                               /█\
  /   \                             /███\
 /     \                           /█████\
/_______\                         /███████\

Object appears flat and            Object appears 3D with
unrealistic - no depth cues        shading and highlights

Every surface the same color,      Surfaces facing light are bright,
no sense of 3D form                sides are darker, shiny spots appear
```

### What Lighting Models Calculate

Lighting models determine the color of each pixel based on:

1. **Surface properties** (color, shininess)
2. **Light properties** (position, color, intensity)
3. **Viewer position** (for specular highlights)
4. **Surface orientation** (normals)

---

## Part 2: The Three Components of Light

### Visual Breakdown

```
TOTAL LIGHTING = AMBIENT + DIFFUSE + SPECULAR

    AMBIENT:           DIFFUSE:            SPECULAR:
    ░░░░░░             ██████               ✦✦✦✦
    ░░░░░░             ██████               ✦✦✦✦
    ░░░░░░             ██████               ✦✦✦✦

Base illumination    Directional shading    Shiny highlights
that reaches all     based on surface       that reflect light
surfaces equally     angle to light         toward viewer
```

### The Three Components Separately

```glsl
// Ambient - constant base illumination
float ambientStrength = 0.1;
vec3 ambient = ambientStrength * lightColor;

// Diffuse - depends on angle to light
vec3 norm = normalize(Normal);
vec3 lightDir = normalize(lightPos - FragPos);
float diff = max(dot(norm, lightDir), 0.0);
vec3 diffuse = diff * lightColor;

// Specular - depends on view direction
vec3 viewDir = normalize(viewPos - FragPos);
vec3 reflectDir = reflect(-lightDir, norm);
float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
vec3 specular = spec * lightColor;

// Combine
vec3 result = (ambient + diffuse + specular) * objectColor;
```

---

## Part 3: Ambient Lighting

### What is Ambient Light?

**Ambient light** represents light that has bounced around the scene so much that it comes from all directions equally. It ensures that surfaces not directly lit still have some visibility.

```
AMBIENT ONLY:
    ░░░░░░
    ░░░░░░
    ░░░░░░
    ░░░░░░

- Constant across all surfaces
- No directional information
- Prevents completely black shadows
- Usually a small percentage of total light
```

### Ambient Implementation

```glsl
// Simple ambient
float ambientStrength = 0.1;
vec3 ambient = ambientStrength * lightColor;

// Ambient with color
vec3 ambientColor = vec3(0.2, 0.2, 0.3);  // Slightly blue
vec3 ambient = ambientStrength * ambientColor;

// Result: All surfaces get this base color, regardless of orientation
```

### Ambient Limitations

```
REALITY:                         AMBIENT APPROXIMATION:
Light bounces                    Constant term is a
multiple times                   cheap approximation

    ████                              ░░░░
  ██░░██                            ░░░░░░
██░░░░██                            ░░░░░░
██░░░░██                            ░░░░░░
  ██░░██                            ░░░░░░
    ████                              ░░░░

Ambient is a hack - it doesn't create the soft
bounce lighting of reality, but it's cheap!
```

---

## Part 4: Diffuse Lighting

### What is Diffuse Light?

**Diffuse light** represents light that scatters equally in all directions when it hits a surface. It's what gives objects their "matte" appearance and creates shading based on surface orientation.

```
DIFFUSE ONLY:
    
    Light →   ↗     ████
                     ████  (facing light - bright)
                     
              →     ░███   (angled - medium)
              
              →     ░░██   (side - dark)
              
              →     ░░░░   (away - black)

Brightness depends on angle between surface normal and light direction
```

### The Math of Diffuse Lighting

```glsl
// Diffuse calculation
vec3 norm = normalize(Normal);           // Surface direction
vec3 lightDir = normalize(lightPos - FragPos);  // Light direction

float diff = max(dot(norm, lightDir), 0.0);  // Cosine of angle
// dot = cos(angle) between vectors
// max() ensures no negative lighting

vec3 diffuse = diff * lightColor * objectColor;

// Visualizing dot product values:
// angle = 0°   (facing light)   → dot = 1.0 → full brightness
// angle = 45°                     dot = 0.7 → 70% brightness
// angle = 90°  (side)            → dot = 0.0 → black
// angle > 90° (away from light)  → dot = negative → clamped to 0
```

### Diffuse Diagram

```
LIGHT DIRECTION AND NORMALS:

    Light
      ↓
      ↓    ↗ Normal (45°)
      ↓  ↗
      ↓↗
    ●───── Surface
      ↘
       ↘ Normal (135°) - faces away

For normal at 45°: dot = cos(45°) = 0.7 → 70% brightness
For normal at 135°: dot = cos(135°) = -0.7 → clamped to 0 → black
```

### Distance Attenuation

In reality, light gets weaker with distance. Add attenuation:

```glsl
// Distance attenuation
float distance = length(lightPos - FragPos);
float attenuation = 1.0 / (constant + linear * distance + 
                           quadratic * distance * distance);

// Apply to diffuse
diffuse *= attenuation;

// Typical values:
// constant = 1.0
// linear = 0.09
// quadratic = 0.032
```

---

## Part 5: Specular Lighting (Phong Model)

### What is Specular Light?

**Specular light** represents the bright highlights that appear on shiny surfaces when light reflects directly toward the viewer. It's what makes materials look glossy, wet, or metallic.

```
SPECULAR HIGHLIGHTS:

    Viewer
      ●
       \          Shiny surface
        \          ████
         \        ██████
          ✦      ████████
         /        ██████
        /          ████
       /
      ●
    Light

The highlight appears where reflection angle = view angle
```

### Phong Specular Model

```glsl
// Phong specular calculation
vec3 viewDir = normalize(viewPos - FragPos);
vec3 lightDir = normalize(lightPos - FragPos);
vec3 reflectDir = reflect(-lightDir, norm);

float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
vec3 specular = spec * lightColor * specularStrength;

// Parameters:
// - reflectDir: Direction light bounces off surface
// - viewDir: Direction to viewer
// - dot: 1.0 if viewer sees perfect reflection
// - shininess: Controls highlight size (2-256)
```

### Shininess Factor

```glsl
// Shininess controls highlight size and falloff
float spec;

// Low shininess (2-16) - broad, dull highlight
spec = pow(dotValue, 2.0);   // Wide, soft highlight
spec = pow(dotValue, 16.0);  // Medium highlight

// High shininess (32-256) - sharp, bright highlight
spec = pow(dotValue, 32.0);  // Shiny
spec = pow(dotValue, 128.0); // Very shiny
spec = pow(dotValue, 256.0); // Mirror-like

// Visual effect:
// shininess=2:   ████████████
// shininess=32:     ██████
// shininess=256:       ██
```

### Specular Diagram

```
PHONG SPECULAR GEOMETRY:

        Normal
          ↑
          |  Light
          |  ↓
          | ↙
    Viewer●←───Surface
          ↙
        Reflect

Steps:
1. Light hits surface at angle θ
2. Light reflects at same angle (reflectDir)
3. Compare reflectDir to viewDir
4. If aligned, bright highlight!
```

---

## Part 6: Complete Phong Model

### Phong Reflection Model Equation

```
I_total = I_ambient + I_diffuse + I_specular

Where:
I_ambient = k_ambient * light_ambient
I_diffuse = k_diffuse * (N·L) * light_diffuse
I_specular = k_specular * (R·V)^shininess * light_specular

k = material coefficients (surface properties)
N = surface normal
L = light direction
R = reflection vector
V = view direction
```

### Full Phong Shader Implementation

```glsl
#version 330 core
out vec4 FragColor;

in vec3 Normal;
in vec3 FragPos;
in vec2 TexCoord;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 objectColor;

uniform sampler2D diffuseTexture;
uniform sampler2D specularTexture;

void main() {
    // Sample textures
    vec3 diffuseTex = texture(diffuseTexture, TexCoord).rgb;
    vec3 specularTex = texture(specularTexture, TexCoord).rgb;
    
    // Ambient
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor * diffuseTex;
    
    // Diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor * diffuseTex;
    
    // Specular (Phong)
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightColor * specularTex;
    
    // Result
    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, 1.0);
}
```

### Material Properties

```cpp
// Define material structures
struct Material {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
};

// Example materials
Material gold = {
    vec3(0.24725, 0.1995, 0.0745),    // Ambient
    vec3(0.75164, 0.60648, 0.22648),   // Diffuse
    vec3(0.628281, 0.555802, 0.366065), // Specular
    51.2                                 // Shininess
};

Material plastic = {
    vec3(0.0, 0.0, 0.0),                // Ambient
    vec3(0.55, 0.55, 0.55),             // Diffuse
    vec3(0.70, 0.70, 0.70),             // Specular
    32.0                                 // Shininess
};
```

---

## Part 7: Blinn-Phong Model (The Improvement)

### The Problem with Phong

```glsl
// Phong can have artifacts when shininess is low
// and light/view angles are extreme

PHONG ARTIFACT:
    Surface
    ────────
       \    ✦  Highlight appears
        \      even on back faces!
         \
          \
           \
            Light

The highlight "breaks" at edges - not physically correct
```

### Blinn-Phong Solution

**Blinn-Phong** uses the **half-vector** instead of the reflection vector, which is more stable and efficient.

```glsl
// Blinn-Phong specular
vec3 lightDir = normalize(lightPos - FragPos);
vec3 viewDir = normalize(viewPos - FragPos);
vec3 halfDir = normalize(lightDir + viewDir);  // Half-vector

float spec = pow(max(dot(norm, halfDir), 0.0), shininess);
vec3 specular = spec * lightColor * specularStrength;

// No reflection vector needed!
// More efficient and artifact-free
```

### Half-Vector Visualization

```
BLINN-PHONG GEOMETRY:

        Normal
          ↑
          |  Half-vector
          |  ↗
          | ↙
    Viewer●───●Light
          ↙
        Surface

Half-vector = normalize(lightDir + viewDir)
This is the direction halfway between light and view

Why it works:
- When half-vector aligns with normal, we see highlight
- More stable than Phong's reflection vector
- Always produces valid results
```

### Phong vs Blinn-Phong Comparison

| Aspect | Phong | Blinn-Phong |
|--------|-------|-------------|
| **Uses** | Reflection vector (R·V) | Half-vector (N·H) |
| **Performance** | Slower (reflect calculation) | Faster (no reflect) |
| **Artifacts** | Can break at edges | Smooth everywhere |
| **Accuracy** | Good | Better for most cases |
| **Shininess Mapping** | Direct | Need different exponent |

### Shininess Adjustment

```glsl
// Phong and Blinn-Phong use different shininess values
// To get similar results, adjust exponent

// Phong with shininess = 32
float phongSpec = pow(dot(reflectDir, viewDir), 32.0);

// Blinn-Phong equivalent needs different exponent
// Typically 2-4 times smaller
float blinnSpec = pow(dot(norm, halfDir), 8.0);  // For similar look

// Rule of thumb: Blinn exponent ≈ Phong exponent / 4
```

---

## Part 8: Complete Blinn-Phong Implementation

### Vertex Shader

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoord = aTexCoord;
    
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
```

### Fragment Shader (Blinn-Phong)

```glsl
#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

struct Light {
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    
    // Attenuation
    float constant;
    float linear;
    float quadratic;
};

struct Material {
    sampler2D diffuse;
    sampler2D specular;
    float shininess;
};

uniform Light light;
uniform Material material;
uniform vec3 viewPos;

void main() {
    // Distance attenuation
    float distance = length(light.position - FragPos);
    float attenuation = 1.0 / (light.constant + 
                               light.linear * distance + 
                               light.quadratic * (distance * distance));
    
    // Ambient
    vec3 ambient = light.ambient * texture(material.diffuse, TexCoord).rgb;
    
    // Diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(light.position - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * diff * texture(material.diffuse, TexCoord).rgb;
    
    // Specular (Blinn-Phong)
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 halfDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(norm, halfDir), 0.0), material.shininess);
    vec3 specular = light.specular * spec * texture(material.specular, TexCoord).rgb;
    
    // Apply attenuation
    ambient *= attenuation;
    diffuse *= attenuation;
    specular *= attenuation;
    
    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, 1.0);
}
```

### Multiple Lights

```glsl
#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

struct PointLight {
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    
    float constant;
    float linear;
    float quadratic;
};

#define NR_POINT_LIGHTS 4
uniform PointLight pointLights[NR_POINT_LIGHTS];
uniform Material material;
uniform vec3 viewPos;

vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir) {
    vec3 lightDir = normalize(light.position - fragPos);
    
    // Diffuse
    float diff = max(dot(normal, lightDir), 0.0);
    
    // Specular (Blinn-Phong)
    vec3 halfDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(normal, halfDir), 0.0), material.shininess);
    
    // Attenuation
    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + 
                               light.quadratic * (distance * distance));
    
    // Combine
    vec3 ambient = light.ambient * texture(material.diffuse, TexCoord).rgb;
    vec3 diffuse = light.diffuse * diff * texture(material.diffuse, TexCoord).rgb;
    vec3 specular = light.specular * spec * texture(material.specular, TexCoord).rgb;
    
    ambient *= attenuation;
    diffuse *= attenuation;
    specular *= attenuation;
    
    return (ambient + diffuse + specular);
}

void main() {
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    
    vec3 result = vec3(0.0);
    for(int i = 0; i < NR_POINT_LIGHTS; i++) {
        result += CalcPointLight(pointLights[i], norm, FragPos, viewDir);
    }
    
    FragColor = vec4(result, 1.0);
}
```

---

## Part 9: Visual Comparison and Parameters

### Light Component Visualization

```
AMBIENT ONLY:          DIFFUSE ONLY:         SPECULAR ONLY:
    ░░░░░░                ██████                  ✦
    ░░░░░░                ██████                 ✦✦
    ░░░░░░                ██████                ✦✦✦
    ░░░░░░                ██████                 ✦✦

COMBINED:
    ░░██████ ✦
    ░░██████ ✦✦
    ░░██████ ✦✦✦
    ░░██████ ✦✦

Each component contributes to the final image
```

### Parameter Effects

```glsl
// Ambient strength
0.0 → 0.1 → 0.2 → 0.3
Dark shadows gradually lighten

// Diffuse strength
0.0 → 0.5 → 1.0 → 1.5
Flat → Normal → Bright → Overexposed

// Specular strength
0.0 → 0.2 → 0.5 → 1.0
Matte → Slight shine → Glossy → Mirror-like

// Shininess
2 → 16 → 32 → 128 → 256
Broad → Medium → Sharp → Very sharp → Pinpoint
```

### Material Examples

| Material | Ambient | Diffuse | Specular | Shininess |
|----------|---------|---------|----------|-----------|
| **Emerald** | 0.0215,0.1745,0.0215 | 0.07568,0.61424,0.07568 | 0.633,0.727811,0.633 | 76.8 |
| **Gold** | 0.24725,0.1995,0.0745 | 0.75164,0.60648,0.22648 | 0.628281,0.555802,0.366065 | 51.2 |
| **Silver** | 0.19225,0.19225,0.19225 | 0.50754,0.50754,0.50754 | 0.508273,0.508273,0.508273 | 51.2 |
| **Plastic** | 0.0,0.0,0.0 | 0.55,0.55,0.55 | 0.70,0.70,0.70 | 32.0 |
| **Rubber** | 0.02,0.02,0.02 | 0.01,0.01,0.01 | 0.4,0.4,0.4 | 10.0 |

---

## Part 10: Performance Considerations

### Lighting Calculation Costs

```cpp
// Per-pixel lighting (Phong shading) - most expensive
for each pixel {
    for each light {
        calculate diffuse  // dot product
        calculate specular // pow, reflect, dot
    }
}

// Per-vertex lighting (Gouraud shading) - cheaper
for each vertex {
    for each light {
        calculate lighting
    }
}
// Interpolate results across pixels

// Performance comparison:
// Per-pixel: O(pixels × lights × operations)
// Per-vertex: O(vertices × lights × operations)
// For 1080p: 2M pixels vs 50k vertices = 40x difference!
```

### Optimization Techniques

```glsl
// 1. Early exit for back-facing fragments
if (dot(normal, lightDir) <= 0.0) {
    // No diffuse or specular contribution
    return ambient;
}

// 2. Pre-calculate what you can
// In vertex shader:
vViewDir = viewPos - FragPos;  // Not normalized yet
// In fragment shader:
vec3 viewDir = normalize(vViewDir);  // Only once

// 3. Use uniforms for light data (not per-fragment calculation)
// BAD: light.position in fragment shader changes per light
// GOOD: loop over lights in fragment shader with uniform array

// 4. Reduce shininess power for distant lights
if (distance > threshold) {
    spec = 0.0;  // No specular for distant lights
}
```

### Shader Complexity Impact

```glsl
// Simple shader: 10 instructions per pixel
// Complex shader: 100+ instructions per pixel
// At 1080p 60fps: 2M × 60 = 120M pixels/second

// 10 instructions: 1.2B operations/second
// 100 instructions: 12B operations/second
// GPU limits: ~5-10 TFLOPs (trillions of operations)

// Keep it balanced!
```

---

## Part 11: Common Artifacts and Solutions

### 1. Banding (Mach Bands)

```
PROBLEM:                     SOLUTION:
██████                       ██████
██████                       ██████
██████    Visible            ██████  Smooth
██████    steps              ██████  gradient
██████                       ██████

Cause: Low precision or insufficient samples
Fix: Use higher precision, dithering, or more lights
```

### 2. Specular Aliasing

```
PROBLEM:                     SOLUTION:
    ✦                           ██
   ✦✦✦                         ████
  ✦✦✦✦✦                       ██████
   ✦✦✦                         ████
    ✦                           ██

Cause: High shininess on low-poly models
Fix: Normal mapping, higher tessellation
```

### 3. Light Leaking

```
PROBLEM: Light appears through walls
Fix: Adjust normals, use proper geometry
```

### 4. Dark Spots (Shadow Acne)

```
PROBLEM: Random dark pixels on lit surfaces
Fix: Add bias to shadow maps, adjust normal calculations
```

### Debugging Visualization

```glsl
// Visualize normals
FragColor = vec4(norm * 0.5 + 0.5, 1.0);

// Visualize diffuse only
FragColor = vec4(vec3(diff), 1.0);

// Visualize specular only
FragColor = vec4(vec3(spec), 1.0);

// Visualize light direction
vec3 lightDirVis = lightDir * 0.5 + 0.5;
FragColor = vec4(lightDirVis, 1.0);
```

---

## Part 12: Beyond Phong - Modern Lighting

### Physically Based Rendering (PBR)

```glsl
// Modern games use PBR, which is more physically accurate
// Key differences from Phong:

// 1. Energy conservation - reflected light ≤ incoming light
// 2. Microfacet theory - surfaces have micro-geometry
// 3. Fresnel effect - reflections stronger at grazing angles
// 4. Metal vs dielectric - different behavior

// Example PBR approximation:
float NDF = DistributionGGX(N, H, roughness);
float G = GeometrySmith(N, V, L, roughness);
vec3 F = fresnelSchlick(max(dot(H, V), 0.0), F0);

vec3 numerator = NDF * G * F;
float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0);
vec3 specular = numerator / max(denominator, 0.001);
```

### Comparison: Phong vs PBR

| Aspect | Phong | PBR |
|--------|-------|-----|
| **Parameters** | Ambient, Diffuse, Specular, Shininess | Albedo, Roughness, Metalness, AO |
| **Physics** | Ad-hoc model | Based on real physics |
| **Flexibility** | Easy to tweak | Consistent across lighting |
| **Realism** | Good enough | Cinematic quality |
| **Performance** | Fast | Heavier |

---

## The 30-Second Summary

- **Phong Model** = Ambient + Diffuse + Specular
- **Ambient** = Constant base illumination (prevents black shadows)
- **Diffuse** = Lambertian reflection (depends on angle to light: N·L)
- **Specular (Phong)** = Shiny highlights (R·V)^shininess
- **Specular (Blinn-Phong)** = Half-vector method (N·H)^shininess (better!)
- **Shininess** = Controls highlight size (2 = dull, 256 = sharp)
- **Attenuation** = Light gets weaker with distance (1/(constant + linear*d + quadratic*d²))
- **Materials** = Different ambient/diffuse/specular/shininess values

**Lighting models transform flat geometry into believable 3D objects - they're the difference between a wireframe and a living, breathing world.**