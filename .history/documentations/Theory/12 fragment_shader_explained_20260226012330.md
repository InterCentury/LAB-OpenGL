# Fragment ShaderExplained - Beginner's Documentation

## The Digital Painter Analogy

A fragment shader can be understood through a massive team of digital painters:

- **The Painters** = Fragment shader instances (one per pixel)
- **The Canvas** = The framebuffer (final image)
- **The Paint Colors** = Texture samples, calculations, lighting
- **The Instructions** = The shader program (what color to paint)
- **The Sketch Lines** = Rasterized geometry (which pixels to paint)
- **The Reference Photos** = Textures (image data to sample)

**Each painter stands before one pixel, follows the same instructions, and decides exactly what color that pixel should become. Thousands of painters work simultaneously.**

---

## Part 1: What is a Fragment Shader?

### Definition

A **fragment shader** (also called pixel shader) is a programmable stage in the graphics pipeline that processes each fragment (potential pixel) and determines its final color. It runs after rasterization and before per-fragment operations.

### Core Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Color Calculation** | Determine the final RGBA color of each pixel |
| **Texture Sampling** | Fetch colors from textures at specified coordinates |
| **Lighting Computation** | Calculate per-pixel lighting effects |
| **Alpha Handling** | Determine transparency and blending |
| **Discarding** | Reject fragments (creating holes, cutouts) |
| **Post-Processing** | Apply effects to rendered images |

### Key Characteristics

| Aspect | Value |
|--------|-------|
| **Invocation** | Once per fragment (pixel) that passes early tests |
| **Input** | Interpolated vertex data + Uniforms + Textures |
| **Output** | Final color (and optionally depth) |
| **Parallelism** | Millions of instances simultaneously |
| **Mandatory?** | Yes (in Core Profile) |

---

## Part 2: The Fragment Lifecycle

### From Vertex to Pixel

```
VERTEX SHADER (processes vertices)
    ↓
RASTERIZER (fixed function)
    ├─ Determines which pixels are covered by triangles
    ├─ Interpolates vertex data across the triangle
    └─ Generates FRAGMENTS (one per covered pixel)
    ↓
EARLY DEPTH TEST (optional, fixed function)
    ├─ Tests if fragment is visible
    └─ Discards occluded fragments before shading
    ↓
FRAGMENT SHADER (runs on visible fragments)
    ├─ Calculates final color
    └─ Can optionally modify depth
    ↓
LATE DEPTH/STENCIL TESTS (fixed function)
    ├─ Final visibility tests
    └─ Blending with existing framebuffer
    ↓
FRAMEBUFFER (final pixel written)
```

### What is a Fragment?

A **fragment** is not yet a pixel - it's a **candidate pixel** with:

- Screen coordinates (x, y)
- Depth value (z)
- Interpolated vertex data (UVs, normals, colors)
- Coverage information (for anti-aliasing)

---

## Part 3: Fragment Shader Inputs

### Input Category 1: Interpolated Data (Varyings)

Data coming from the vertex shader, interpolated across the primitive.

```glsl
// VERTEX SHADER
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;

// Outputs to fragment shader
out vec3 vNormal;
out vec2 vTexCoord;
out vec3 vFragPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    vec4 worldPos = model * vec4(aPos, 1.0);
    vFragPos = worldPos.xyz;
    vNormal = mat3(transpose(inverse(model))) * aNormal;
    vTexCoord = aTexCoord;
    gl_Position = projection * view * worldPos;
}
```

```glsl
// FRAGMENT SHADER
#version 330 core

// Inputs from vertex shader (INTERPOLATED!)
in vec3 vNormal;      // Smoothly varying across triangle
in vec2 vTexCoord;    // Smoothly varying across triangle  
in vec3 vFragPos;     // Smoothly varying across triangle

out vec4 FragColor;

void main()
{
    // vTexCoord is now interpolated between vertices
    // For a triangle:
    // - Near vertex 0: close to TexCoord0
    // - Near vertex 1: close to TexCoord1
    // - Center: blend of all three
    FragColor = vec4(vTexCoord, 0.0, 1.0);
}
```

### How Interpolation Works

```
TRIANGLE VERTICES:
Vertex 0: TexCoord = (0,0) - Bottom left
Vertex 1: TexCoord = (1,0) - Bottom right
Vertex 2: TexCoord = (0.5,1) - Top middle

INTERPOLATION:
Pixel at bottom-left: near (0,0)
Pixel at bottom-right: near (1,0)
Pixel at top-middle: near (0.5,1)
Pixel at center: (0.5,0.33) - weighted average
```

### Interpolation Qualifiers

| Qualifier | Description | Example |
|-----------|-------------|---------|
| **smooth** | Perspective-correct interpolation (default) | `smooth in vec2 vTexCoord;` |
| **flat** | No interpolation (first vertex value only) | `flat in vec3 vColor;` |
| **noperspective** | Linear interpolation in screen space | `noperspective in vec2 vScreenPos;` |

```glsl
// Example: Flat shading (one color per triangle)
// Vertex shader
flat out vec3 vFaceColor;

// Fragment shader
flat in vec3 vFaceColor;  // Same color for entire triangle
```

### Input Category 2: Uniforms

Global values constant for the entire draw call.

```glsl
#version 330 core
in vec2 vTexCoord;
in vec3 vNormal;
in vec3 vFragPos;

// Uniforms - same for all fragments
uniform sampler2D diffuseTexture;
uniform sampler2D specularTexture;
uniform vec3 lightPos;
uniform vec3 lightColor;
uniform vec3 viewPos;
uniform float time;

out vec4 FragColor;

void main()
{
    // Use uniforms for lighting and effects
    vec3 lightDir = normalize(lightPos - vFragPos);
    float diff = max(dot(vNormal, lightDir), 0.0);
    
    // Time-based effect
    float pulse = sin(time * 2.0) * 0.5 + 0.5;
    
    vec4 texColor = texture(diffuseTexture, vTexCoord);
    FragColor = texColor * diff * pulse;
}
```

### Input Category 3: Built-in Variables

Special variables provided by the system.

```glsl
#version 330 core
out vec4 FragColor;

void main()
{
    // gl_FragCoord: screen position (x, y, z, 1/w)
    vec2 screenPos = gl_FragCoord.xy;
    
    // Create checkerboard pattern based on screen position
    float checker = mod(floor(screenPos.x / 20.0) + floor(screenPos.y / 20.0), 2.0);
    
    // gl_FrontFacing: true if fragment is from front face of triangle
    if (gl_FrontFacing) {
        FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Front face red
    } else {
        FragColor = vec4(0.0, 0.0, 1.0, 1.0);  // Back face blue
    }
    
    // gl_PointCoord: for point sprites (0-1 coordinates within point)
    // gl_PrimitiveID: which primitive this fragment belongs to
}
```

### Built-in Variables Reference

| Variable | Type | Description |
|----------|------|-------------|
| `gl_FragCoord` | `vec4` | Window-relative coordinates (x,y) + depth (z) |
| `gl_FrontFacing` | `bool` | True if fragment belongs to front face |
| `gl_PointCoord` | `vec2` | Within-point coordinates for point sprites |
| `gl_PrimitiveID` | `int` | Index of current primitive |
| `gl_SampleID` | `int` | Sample number for multisampling |
| `gl_SamplePosition` | `vec2` | Sample position within pixel |

---

## Part 4: Fragment Shader Outputs

### Primary Output: FragColor

The final color of the fragment.

```glsl
#version 330 core
out vec4 FragColor;  // RGBA output

void main()
{
    // Output final color
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Opaque red
    
    // Alpha = 0.5 for transparency
    FragColor = vec4(1.0, 0.0, 0.0, 0.5);  // Semi-transparent red
}
```

### Multiple Render Targets (MRT)

Rendering to multiple textures simultaneously.

```glsl
#version 330 core

// Multiple outputs for different render targets
layout (location = 0) out vec4 colorBuffer;   // Main color
layout (location = 1) out vec4 normalBuffer;  // Normals for deferred shading
layout (location = 2) out vec4 positionBuffer; // Positions

in vec3 vNormal;
in vec3 vFragPos;
in vec2 vTexCoord;

uniform sampler2D diffuseTexture;

void main()
{
    // Write to multiple buffers in one pass
    colorBuffer = texture(diffuseTexture, vTexCoord);
    normalBuffer = vec4(vNormal * 0.5 + 0.5, 1.0);  // Store normals
    positionBuffer = vec4(vFragPos, 1.0);           // Store positions
}
```

### Depth Output (Optional)

Fragment shaders can optionally write to `gl_FragDepth`.

```glsl
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    
    // Override depth value (rarely needed)
    gl_FragDepth = 0.5;  // Force depth to 0.5
}
```

**WARNING:** Writing to `gl_FragDepth` disables early depth testing, hurting performance. Only use when necessary.

---

## Part 5: Texture Sampling

### Basic Texture Sampling

```glsl
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

// Sampler uniform (texture unit)
uniform sampler2D ourTexture;

void main()
{
    // Sample texture at interpolated coordinates
    vec4 texColor = texture(ourTexture, vTexCoord);
    FragColor = texColor;
}
```

### Multiple Textures

```glsl
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D diffuseMap;
uniform sampler2D specularMap;
uniform sampler2D normalMap;
uniform sampler2D emissionMap;

void main()
{
    vec4 diffuse = texture(diffuseMap, vTexCoord);
    vec4 specular = texture(specularMap, vTexCoord);
    vec4 normal = texture(normalMap, vTexCoord);
    vec4 emission = texture(emissionMap, vTexCoord);
    
    // Combine textures creatively
    FragColor = diffuse + specular * 0.5 + emission;
}
```

### Texture Sampling Options

```glsl
// Different texture sampling functions
vec4 color1 = texture(tex, vTexCoord);                    // Standard sampling
vec4 color2 = textureLod(tex, vTexCoord, 2.0);            // Force mipmap level
vec4 color3 = textureProj(tex, vec3(vTexCoord, 1.0));     // Projective texturing
vec4 color4 = texelFetch(tex, ivec2(100, 100), 0);        // Direct pixel access

// Array textures
uniform sampler2DArray texArray;
vec4 color5 = texture(texArray, vec3(vTexCoord, layer));

// Cube maps
uniform samplerCube cubeMap;
vec4 color6 = texture(cubeMap, directionVector);
```

---

## Part 6: Lighting Calculations

### Per-Pixel Lighting (Phong Model)

```glsl
#version 330 core
in vec3 vNormal;
in vec3 vFragPos;
in vec2 vTexCoord;

out vec4 FragColor;

uniform vec3 lightPos;
uniform vec3 lightColor;
uniform vec3 viewPos;
uniform sampler2D diffuseTexture;
uniform sampler2D specularTexture;

void main()
{
    // Normalize interpolated values
    vec3 norm = normalize(vNormal);
    vec3 lightDir = normalize(lightPos - vFragPos);
    vec3 viewDir = normalize(viewPos - vFragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    
    // Texture sampling
    vec4 diffuseTex = texture(diffuseTexture, vTexCoord);
    vec4 specularTex = texture(specularTexture, vTexCoord);
    
    // Ambient lighting
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;
    
    // Diffuse lighting
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // Specular lighting
    float specularStrength = 0.5;
    float shininess = 32.0;
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular = specularStrength * spec * lightColor * specularTex.rgb;
    
    // Combine
    vec3 result = (ambient + diffuse + specular) * diffuseTex.rgb;
    FragColor = vec4(result, diffuseTex.a);
}
```

### Toon Shading (Cel-Shading)

```glsl
#version 330 core
in vec3 vNormal;
in vec3 vFragPos;
in vec2 vTexCoord;

out vec4 FragColor;

uniform vec3 lightDir;
uniform sampler2D diffuseTexture;

void main()
{
    vec3 norm = normalize(vNormal);
    float intensity = dot(norm, -lightDir);
    
    // Quantize intensity to cel levels
    float level;
    if (intensity > 0.95)
        level = 1.0;
    else if (intensity > 0.5)
        level = 0.7;
    else if (intensity > 0.25)
        level = 0.4;
    else
        level = 0.1;
    
    vec4 texColor = texture(diffuseTexture, vTexCoord);
    FragColor = vec4(texColor.rgb * level, texColor.a);
}
```

---

## Part 7: Discarding Fragments

### Creating Holes and Cutouts

```glsl
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D diffuseTexture;

void main()
{
    vec4 texColor = texture(diffuseTexture, vTexCoord);
    
    // Discard fragments with low alpha (cutout transparency)
    if (texColor.a < 0.1) {
        discard;  // This fragment won't be drawn
    }
    
    FragColor = texColor;
}
```

### Alpha Testing vs Discard

```glsl
// Method 1: discard (flexible, but disables early Z)
if (texColor.a < 0.1) discard;

// Method 2: Alpha testing (fixed function, faster but less flexible)
// Enable with: glEnable(GL_ALPHA_TEST); glAlphaFunc(GL_GREATER, 0.1f);
// But alpha test is deprecated - use discard in modern OpenGL
```

### Discard for Effects

```glsl
// Draw only half the pixels (checkerboard effect)
if (mod(gl_FragCoord.x + gl_FragCoord.y, 2.0) < 1.0) {
    discard;
}

// Discard based on distance
vec2 center = vec2(400, 300);
float dist = distance(gl_FragCoord.xy, center);
if (dist > 200.0) {
    discard;  // Draw circle only
}
```

---

## Part 8: Derivatives and Gradients

### What Are Derivatives?

Derivatives measure how a value changes between neighboring pixels.

```glsl
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D texture;

void main()
{
    // Calculate how much UV coordinates change between pixels
    vec2 dx = dFdx(vTexCoord);  // Change in x direction
    vec2 dy = dFdy(vTexCoord);  // Change in y direction
    
    // Use derivatives for:
    // 1. Automatic mipmap level selection (done automatically)
    // 2. Edge detection
    // 3. Parallax mapping
    // 4. Analytical anti-aliasing
    
    float sharpness = length(dx) * 1000.0;
    FragColor = texture(texture, vTexCoord);
    
    // Highlight edges where UVs change rapidly
    if (sharpness > 1.0) {
        FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red edges
    }
}
```

### fwidth for Anti-Aliasing

```glsl
// fwidth = abs(dFdx) + abs(dFdy)
float width = fwidth(vTexCoord.x);

// Smooth step for anti-aliased edges
float edge = smoothstep(0.5 - width, 0.5 + width, vTexCoord.x);
FragColor = mix(color1, color2, edge);
```

---

## Part 9: Common Fragment Shader Effects

### 1. Grayscale

```glsl
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D screenTexture;

void main()
{
    vec4 color = texture(screenTexture, vTexCoord);
    float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    FragColor = vec4(gray, gray, gray, color.a);
}
```

### 2. Sepia Tone

```glsl
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D screenTexture;

void main()
{
    vec4 color = texture(screenTexture, vTexCoord);
    
    // Sepia matrix
    float r = dot(color.rgb, vec3(0.393, 0.769, 0.189));
    float g = dot(color.rgb, vec3(0.349, 0.686, 0.168));
    float b = dot(color.rgb, vec3(0.272, 0.534, 0.131));
    
    FragColor = vec4(r, g, b, color.a);
}
```

### 3. Blur (Simple Box Blur)

```glsl
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D screenTexture;
uniform vec2 texelSize;  // 1.0 / texture size

void main()
{
    vec4 result = vec4(0.0);
    
    // Sample 3x3 neighborhood
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            vec2 offset = vec2(x, y) * texelSize;
            result += texture(screenTexture, vTexCoord + offset);
        }
    }
    
    FragColor = result / 9.0;  // Average
}
```

### 4. Edge Detection (Sobel)

```glsl
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D screenTexture;
uniform vec2 texelSize;

void main()
{
    // Sobel operators
    float[9] kernelX = float[](
        -1, 0, 1,
        -2, 0, 2,
        -1, 0, 1
    );
    
    float[9] kernelY = float[](
        -1, -2, -1,
         0,  0,  0,
         1,  2,  1
    );
    
    float Gx = 0.0, Gy = 0.0;
    int index = 0;
    
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 offset = vec2(x, y) * texelSize;
            float brightness = dot(
                texture(screenTexture, vTexCoord + offset).rgb,
                vec3(0.299, 0.587, 0.114)
            );
            
            Gx += brightness * kernelX[index];
            Gy += brightness * kernelY[index];
            index++;
        }
    }
    
    float edge = sqrt(Gx * Gx + Gy * Gy);
    FragColor = vec4(edge, edge, edge, 1.0);
}
```

### 5. Pulse Effect

```glsl
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D screenTexture;
uniform float time;

void main()
{
    vec4 color = texture(screenTexture, vTexCoord);
    
    // Pulsing brightness
    float pulse = sin(time * 3.0) * 0.3 + 0.7;
    
    // Pulsing color shift
    float shift = sin(time * 2.0) * 0.2;
    vec3 shifted = vec3(
        color.r * (1.0 + shift),
        color.g,
        color.b * (1.0 - shift)
    );
    
    FragColor = vec4(shifted * pulse, color.a);
}
```

---

## Part 10: Performance Considerations

### Expensive vs Cheap Operations

| Cheap Operations | Expensive Operations |
|-----------------|---------------------|
| Basic math (+, -, *, /) | Texture sampling |
| Vector operations (dot, normalize) | Conditional branches (divergence) |
| Swizzling (color.rgb) | pow() with large exponent |
| min(), max(), clamp() | sin(), cos(), tan() |
| lerp/mix() | log(), exp() |
| saturate() | reciprocal square root |

### Optimization Tips

```glsl
// BAD: Expensive operations in every fragment
float spec = pow(max(dot(viewDir, reflectDir), 0.0), 128.0);

// BETTER: Pre-calculate what you can
// (but still per-fragment)

// GOOD: Move calculations to vertex shader when possible
// Pass pre-computed values as varyings

// BAD: Conditional branching causing divergence
if (vTexCoord.x > 0.5) {
    // Complex path A
} else {
    // Complex path B
}

// BETTER: Use mix() for simple cases
float factor = step(0.5, vTexCoord.x);
result = mix(resultA, resultB, factor);

// GOOD: Keep branching coherent (same path for nearby pixels)
```

### Early Depth Testing

```glsl
// To benefit from early depth testing:
// 1. Don't write to gl_FragDepth
// 2. Don't discard fragments unnecessarily
// 3. Keep shaders simple for occluded geometry

// Early Z rejects fragments before shader runs
// Massive performance gain for complex scenes
```

---

## Part 11: Debugging Fragment Shaders

### Visual Debugging Techniques

```glsl
// 1. Output UV coordinates as colors
FragColor = vec4(vTexCoord, 0.0, 1.0);
// Red = U coordinate, Green = V coordinate

// 2. Output normals as colors
FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);
// Maps -1..1 to 0..1 for visualization

// 3. Output screen position
FragColor = vec4(gl_FragCoord.xy / 1000.0, 0.0, 1.0);

// 4. Highlight specific pixels
if (gl_FragCoord.x < 10.0 && gl_FragCoord.y < 10.0) {
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red corner
} else {
    FragColor = texture(tex, vTexCoord);
}

// 5. Heat map for performance
float complexity = calculateComplexity();
FragColor = vec4(complexity, 0.0, 1.0 - complexity, 1.0);
```

### Common Errors

```glsl
// ERROR: Not writing to output
void main() {
    // No FragColor assignment - undefined behavior!
}

// ERROR: Wrong component count
out vec4 FragColor;
void main() {
    FragColor = vec3(1.0, 0.0, 0.0);  // vec3 can't assign to vec4
}

// ERROR: Sampling outside 0-1 UV range (if wrapping not enabled)
FragColor = texture(tex, vTexCoord * 2.0);  // May clamp to edge

// ERROR: Discard in wrong context
if (someCondition) {
    discard;  // Valid
    color = vec4(1.0);  // Unreachable code!
}
```

---

## Part 12: Fragment Shader vs Compute Shader

| Aspect | Fragment Shader | Compute Shader |
|--------|-----------------|----------------|
| **Purpose** | Graphics rendering | General computation |
| **Invocation** | Per fragment (automatic) | Per work group (manual) |
| **Input** | Interpolated varyings | Arbitrary buffers |
| **Output** | Framebuffer | Arbitrary buffers |
| **Access Pattern** | 2D grid (screen) | 1D/2D/3D work groups |
| **Best For** | Visual effects | Data processing, simulations |
| **Limitations** | Must output color | No fixed function |

---

## The 30-Second Summary

- **Fragment Shader** = Program that determines color of each pixel
- **Input** = Interpolated vertex data + Uniforms + Textures
- **Output** = Final color (RGBA) + optional depth
- **Key Operations** = Texture sampling, lighting, effects, discard
- **Parallelism** = Millions of instances (one per visible pixel)
- **Performance** = Most expensive stage; optimize texture access and branching
- **Debugging** = Visualize intermediates (UVs, normals, screen position)

**The fragment shader is where pixels get their final appearance - it transforms raw geometry and textures into the beautiful images seen on screen.**

---

**Next Step:** Ready to understand how vertex and fragment shaders work together?