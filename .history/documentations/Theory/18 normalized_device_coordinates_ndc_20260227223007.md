# Normalized Device Coordinates (NDC) 

## The Universal Measuring Stick Analogy

Normalized Device Coordinates can be understood through a universal measuring system:

- **Different Countries, Different Units** = Various screen resolutions and aspect ratios
- **The Meter Stick** = NDC (a universal coordinate system)
- **Converting Measurements** = The viewport transform (converting NDC to pixels)
- **The Standardized Blueprint** = All geometry expressed in this common system

**Just as the meter stick allows builders worldwide to share measurements regardless of local units, NDC allows graphics hardware to process geometry independent of screen resolution.**

---

## Part 1: What is NDC?

### Definition

**Normalized Device Coordinates (NDC)** is a coordinate system that maps the visible region of the scene to a standardized cube where:

- X ranges from -1 to 1 (left to right)
- Y ranges from -1 to 1 (bottom to top in OpenGL)
- Z ranges from -1 to 1 (near to far)

### The NDC Cube

```
NDC SPACE VISUALIZED:
        (+Y)
         ↑
         ●━━━●
        /|   /|
       ●━━━●│ │
       | │  | │   Range: -1 to 1 in all axes
       | ●━━|● → (+X)
       |/   |/
       ●━━━━●
      /
    (+Z)

Corner coordinates:
Front-top-right:  ( 1,  1, -1)  // Note: -Z is into screen in OpenGL NDC
Front-top-left:   (-1,  1, -1)
Front-bottom-right:( 1, -1, -1)
Front-bottom-left: (-1, -1, -1)
Back-top-right:   ( 1,  1,  1)
Back-top-left:    (-1,  1,  1)
Back-bottom-right: ( 1, -1,  1)
Back-bottom-left: (-1, -1,  1)
```

### Key Characteristics

| Aspect | Description |
|--------|-------------|
| **Range** | -1 to 1 in all axes |
| **Shape** | Cube (not frustum) |
| **Resolution Independent** | Same regardless of screen size |
| **Hardware-Friendly** | Simple comparisons for clipping |
| **Post-Perspective Divide** | After w division |

---

## Part 2: The Journey to NDC

### From Clip Space to NDC

```
CLIP SPACE (homogeneous coordinates):
[x_clip, y_clip, z_clip, w_clip]

            ↓
    [ PERSPECTIVE DIVISION ]
    (x/w, y/w, z/w)
            ↓

NDC:
[x_ndc, y_ndc, z_ndc]  (w is now 1)
```

### The Division Step

```glsl
// After vertex shader, OpenGL automatically does:
vec3 ndc = vec3(
    gl_Position.x / gl_Position.w,
    gl_Position.y / gl_Position.w,
    gl_Position.z / gl_Position.w
);

// This is why gl_Position is a vec4 - w is crucial!
// For perspective projection: w contains distance information
// For orthographic projection: w is usually 1
```

### Why Division is Necessary

```cpp
// Without division, perspective doesn't work
// Example: Two points at different distances
vec4 pointNear = vec4(2.0, 0.0, -5.0, 1.0);   // w=1
vec4 pointFar = vec4(2.0, 0.0, -20.0, 4.0);   // w=4 (farther)

// After division:
// pointNear NDC = (2/1, 0/1, -5/1) = (2, 0, -5) ← outside NDC cube!
// pointFar NDC = (2/4, 0/4, -20/4) = (0.5, 0, -5) ← inside NDC cube

// The far point, despite same clip coordinates, ends up inside NDC
// because w correctly represents distance!
```

---

## Part 3: NDC Ranges and Clipping

### The Clipping Test

Any vertex with coordinates outside the -1 to 1 range in NDC is **clipped** (not rendered):

```glsl
// In hardware, this check happens:
if (abs(ndc.x) > 1.0 || abs(ndc.y) > 1.0 || abs(ndc.z) > 1.0) {
    // Vertex is outside view volume
    // Either discard or clip the primitive
}
```

### What Gets Clipped

```
VISIBLE REGION (inside cube):        CLIPPED REGION (outside cube):
    ┌─────┐                              x > 1 or x < -1
    │     │                              y > 1 or y < -1
    │  ●  │  Visible point                z > 1 or z < -1
    │     │
    └─────┘

Example:
Point (2, 0.5, 0) → clipped (x too far right)
Point (0, 2, 0)   → clipped (y too high)
Point (0, 0, 2)   → clipped (z beyond far plane)
```

### Near and Far Planes in NDC

```
OPENGL NDC Z RANGE: -1 to 1

Near plane (z = -1): Closest visible points
Far plane (z = 1): Farthest visible points

Scene depth progression:
Camera → ... -0.8 ... -0.3 ... 0.0 ... 0.5 ... 1.0
        Near                                     Far
        └───────────────────────────────────────┘
                    Visible range
```

---

## Part 4: NDC in Different APIs

### OpenGL vs DirectX vs Vulkan

| API | X Range | Y Range | Z Range | Y Direction |
|-----|---------|---------|---------|-------------|
| **OpenGL** | -1 to 1 | -1 to 1 | -1 to 1 | Bottom = -1, Top = 1 |
| **DirectX** | -1 to 1 | -1 to 1 | 0 to 1 | Bottom = -1, Top = 1 |
| **Vulkan** | -1 to 1 | -1 to 1 | 0 to 1 | Top = -1, Bottom = 1 (Y flipped!) |

### Visual Comparison

```
OPENGL NDC:                   DIRECTX NDC:
    (+Y)                          (+Y)
     ↑                             ↑
    ┌─┴─┐                        ┌─┴─┐
    │   │                        │   │
    │   │ Z: -1..1               │   │ Z: 0..1
    │   │                        │   │
    └───┘                        └───┘
     ↓                             ↓
   (+X)                          (+X)

VULKAN NDC:
    (+Y)
     ↓
    ┌─┴─┐
    │   │
    │   │ Z: 0..1, Y flipped!
    │   │
    └───┘
     ↑
   (+X)
```

### Handling API Differences

```glsl
// When porting shaders between APIs:

// OpenGL to Vulkan - flip Y and adjust Z
#ifdef VULKAN
    gl_Position.y = -gl_Position.y;
    gl_Position.z = (gl_Position.z + gl_Position.w) / 2.0;
#endif

// DirectX to OpenGL - adjust Z range
#ifdef DIRECTX
    gl_Position.z = gl_Position.z * 2.0 - gl_Position.w;
#endif
```

---

## Part 5: The Viewport Transform (NDC to Screen)

### From NDC to Pixels

After NDC, OpenGL automatically transforms to screen space:

```cpp
// Viewport setup
glViewport(0, 0, windowWidth, windowHeight);
glDepthRange(0.0, 1.0);  // Optional: set depth range

// Transformation formula:
screenX = (ndcX + 1.0) * (width / 2.0) + x;
screenY = (ndcY + 1.0) * (height / 2.0) + y;
screenZ = (ndcZ + 1.0) * (far - near) / 2.0 + near;

// Where:
// - x, y: viewport origin (usually 0,0)
// - width, height: viewport dimensions
// - near, far: depth range (usually 0,1)
```

### Examples

```cpp
// Example 1: 1920x1080 display
// NDC point (0, 0, 0) becomes:
screenX = (0 + 1) * (1920/2) + 0 = 960
screenY = (0 + 1) * (1080/2) + 0 = 540
// Center of screen!

// Example 2: NDC point (1, 1, 0) becomes:
screenX = (1 + 1) * 960 = 1920  // Right edge
screenY = (1 + 1) * 540 = 1080  // Top edge

// Example 3: NDC point (-1, -1, 0) becomes:
screenX = (-1 + 1) * 960 = 0    // Left edge
screenY = (-1 + 1) * 540 = 0    // Bottom edge
```

### Multiple Viewports

```cpp
// Split screen for multiplayer
// Player 1 (left half)
glViewport(0, 0, windowWidth/2, windowHeight);
glDepthRange(0.0, 1.0);
// Render player 1 view...

// Player 2 (right half)
glViewport(windowWidth/2, 0, windowWidth/2, windowHeight);
glDepthRange(0.0, 1.0);
// Render player 2 view...

// Same NDC coordinates map to different screen regions!
```

---

## Part 6: NDC and Depth Testing

### Depth Values in NDC

```glsl
// In fragment shader
void main() {
    // gl_FragCoord.z contains the depth value in NDC range
    // after viewport transform: 0 = near, 1 = far
    
    float depth = gl_FragCoord.z;
    
    // Visualize depth
    FragColor = vec4(vec3(depth), 1.0);
    // Near objects: dark, Far objects: light
    
    // Or create a heat map
    vec3 nearColor = vec3(1.0, 0.0, 0.0);  // Red near
    vec3 farColor = vec3(0.0, 0.0, 1.0);   // Blue far
    vec3 depthColor = mix(nearColor, farColor, depth);
    FragColor = vec4(depthColor, 1.0);
}
```

### Depth Precision

The non-linear nature of depth in NDC affects precision:

```
PERSPECTIVE PROJECTION DEPTH:
Near plane:  z_ndc = -1  (lots of precision)
Far plane:   z_ndc =  1  (little precision)

Why: Depth is stored as 1/z in NDC
This gives more precision to near objects (where it matters)
```

### Visualizing the Non-Linearity

```cpp
// Z values in view space vs NDC
View Z    →    NDC Z
-0.1      →    ~0.999  (near plane)
-1.0      →     0.5
-10.0     →    -0.8
-100.0    →    -0.98   (far plane)

// Notice how most of the NDC range is used for near objects!
// This is why you should keep near plane as far as possible
// to maximize depth precision.
```

---

## Part 7: Working with NDC in Shaders

### Accessing NDC in Fragment Shader

```glsl
#version 330 core
out vec4 FragColor;

void main() {
    // Method 1: From gl_FragCoord
    // gl_FragCoord.xy is screen space (pixels)
    // To get NDC, you need to convert:
    vec2 ndc = (gl_FragCoord.xy / resolution.xy) * 2.0 - 1.0;
    
    // Method 2: Pass from vertex shader (more accurate)
    // (See vertex shader example below)
    
    // Use NDC for effects
    float xGradient = ndc.x * 0.5 + 0.5;  // Map -1..1 to 0..1
    float yGradient = ndc.y * 0.5 + 0.5;
    
    FragColor = vec4(xGradient, yGradient, 0.0, 1.0);
}
```

### Passing NDC from Vertex Shader

```glsl
// Vertex Shader
#version 330 core
layout (location = 0) in vec3 aPos;

out vec3 vNDC;  // Pass NDC to fragment shader

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    // Clip space
    vec4 clipPos = projection * view * model * vec4(aPos, 1.0);
    
    // Compute NDC (perspective division)
    // Note: This is usually done automatically, but we can compute it manually
    vNDC = clipPos.xyz / clipPos.w;
    
    gl_Position = clipPos;  // OpenGL will do division again, but that's fine
}

// Fragment Shader
#version 330 core
in vec3 vNDC;
out vec4 FragColor;

void main() {
    // Use the NDC we passed
    // vNDC.x: -1 (left) to 1 (right)
    // vNDC.y: -1 (bottom) to 1 (top)
    // vNDC.z: -1 (near) to 1 (far)
    
    // Create a checkerboard based on NDC
    float checker = step(0.5, fract(vNDC.x * 5.0)) * 
                    step(0.5, fract(vNDC.y * 5.0));
    
    FragColor = vec4(vec3(checker), 1.0);
}
```

---

## Part 8: NDC-Based Effects

### Screen-Space Effects

```glsl
// Vignette effect based on NDC distance from center
#version 330 core
in vec3 vNDC;
out vec4 FragColor;
uniform sampler2D screenTexture;

void main() {
    vec4 color = texture(screenTexture, (vNDC.xy * 0.5 + 0.5));
    
    // Distance from center (0,0 in NDC)
    float dist = length(vNDC.xy);
    
    // Darken edges
    float vignette = 1.0 - smoothstep(0.5, 1.0, dist);
    
    FragColor = vec4(color.rgb * vignette, color.a);
}

// Scanline effect
void main() {
    float scanline = sin(vNDC.y * 500.0) * 0.5 + 0.5;
    FragColor = texture(screenTexture, (vNDC.xy * 0.5 + 0.5)) * scanline;
}

// Edge distortion (fisheye)
void main() {
    vec2 centered = vNDC.xy;
    float dist = length(centered);
    vec2 distorted = centered * (1.0 + 0.3 * dist * dist);
    
    if (abs(distorted.x) > 1.0 || abs(distorted.y) > 1.0) {
        discard;  // Outside view
    }
    
    vec2 uv = distorted * 0.5 + 0.5;
    FragColor = texture(screenTexture, uv);
}
```

### Grid Overlay

```glsl
// Render a grid in NDC space
#version 330 core
in vec3 vNDC;
out vec4 FragColor;

void main() {
    // Grid size in NDC units
    float gridSize = 0.1;
    
    // Compute grid lines
    vec2 grid = abs(fract(vNDC.xy / gridSize - 0.5) - 0.5) / fwidth(vNDC.xy);
    float lines = min(grid.x, grid.y);
    
    // Smooth grid lines
    float gridIntensity = 1.0 - min(lines, 1.0);
    
    // Axis highlights
    float axisX = 1.0 - min(abs(vNDC.x) * 100.0, 1.0);
    float axisY = 1.0 - min(abs(vNDC.y) * 100.0, 1.0);
    
    vec3 color = vec3(0.2, 0.2, 0.2);
    color = mix(color, vec3(1.0, 1.0, 1.0), gridIntensity * 0.5);
    color = mix(color, vec3(1.0, 0.0, 0.0), axisX);
    color = mix(color, vec3(0.0, 1.0, 0.0), axisY);
    
    FragColor = vec4(color, 1.0);
}
```

---

## Part 9: Debugging with NDC

### Visual Debugging Techniques

```glsl
// 1. Visualize X coordinate (red = right, black = left)
FragColor = vec4(vNDC.x * 0.5 + 0.5, 0.0, 0.0, 1.0);

// 2. Visualize Y coordinate (green = top, black = bottom)
FragColor = vec4(0.0, vNDC.y * 0.5 + 0.5, 0.0, 1.0);

// 3. Visualize Z coordinate (depth)
FragColor = vec4(vec3(vNDC.z * 0.5 + 0.5), 1.0);

// 4. Color-coded regions
vec3 color;
if (vNDC.x > 0.0 && vNDC.y > 0.0) color = vec3(1.0, 0.0, 0.0);  // Quadrant 1
else if (vNDC.x < 0.0 && vNDC.y > 0.0) color = vec3(0.0, 1.0, 0.0);  // Quadrant 2
else if (vNDC.x < 0.0 && vNDC.y < 0.0) color = vec3(0.0, 0.0, 1.0);  // Quadrant 3
else color = vec3(1.0, 1.0, 0.0);  // Quadrant 4

FragColor = vec4(color, 1.0);

// 5. Show clipping boundaries
if (abs(vNDC.x) > 0.99 || abs(vNDC.y) > 0.99) {
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red edges
} else {
    FragColor = texture(screenTexture, vNDC.xy * 0.5 + 0.5);
}
```

### Common NDC Issues

```glsl
// PROBLEM: Geometry appears stretched
// Check aspect ratio in projection matrix
if (screenWidth > screenHeight) {
    // Horizontal stretching - adjust projection
    proj = glm::perspective(fov, aspect, near, far);
}

// PROBLEM: Z-fighting (depth conflicts)
// Near and far planes too far apart
// Keep near as far as possible, far as close as possible

// PROBLEM: Geometry clipped unexpectedly
// Check w component in vertex shader
if (gl_Position.w < 0.0) {
    // Vertex behind camera - will be clipped
    // This is normal for points behind camera
}

// PROBLEM: NDC values > 1 or < -1
// Object outside view frustum
// Either move camera, or adjust view/projection
```

---

## Part 10: NDC and Ray Casting

### Converting Screen to NDC for Picking

```cpp
// Convert mouse position to NDC for ray casting
glm::vec3 screenToNDC(float mouseX, float mouseY, int width, int height) {
    float ndcX = (2.0f * mouseX / width) - 1.0f;
    float ndcY = 1.0f - (2.0f * mouseY / height);  // Flip Y
    float ndcZ = -1.0f;  // Near plane
    
    return glm::vec3(ndcX, ndcY, ndcZ);
}

// Generate ray from NDC
glm::vec3 generateRay(glm::vec3 ndc, glm::mat4 view, glm::mat4 proj) {
    glm::vec4 rayClip(ndc.x, ndc.y, ndc.z, 1.0f);
    
    glm::mat4 invProj = glm::inverse(proj);
    glm::vec4 rayEye = invProj * rayClip;
    rayEye = glm::vec4(rayEye.x, rayEye.y, -1.0f, 0.0f);  // Direction
    
    glm::mat4 invView = glm::inverse(view);
    glm::vec3 rayWorld = glm::normalize(glm::vec3(invView * rayEye));
    
    return rayWorld;
}
```

### World Reconstruction from Depth

```glsl
// Reconstruct world position from depth buffer
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D depthTexture;
uniform mat4 invProjectionView;
uniform vec2 screenSize;

void main() {
    // Get depth
    float depth = texture(depthTexture, vTexCoord).r;
    
    // Compute NDC from UV and depth
    vec4 ndc;
    ndc.xy = vTexCoord * 2.0 - 1.0;
    ndc.z = depth * 2.0 - 1.0;  // Convert 0-1 to -1-1
    ndc.w = 1.0;
    
    // Transform to world space
    vec4 worldPos = invProjectionView * ndc;
    worldPos /= worldPos.w;
    
    // Now worldPos.xyz is the 3D position of this pixel
    FragColor = vec4(worldPos.xyz * 0.5 + 0.5, 1.0);
}
```

---

## Part 11: NDC Precision and Numerical Issues

### Floating Point Precision

```cpp
// NDC values are floats with limited precision
// At 1920x1080, NDC precision needed:
float ndcPrecisionNeeded = 2.0f / 1920.0f;  // ~0.001

// Standard float has ~6-7 decimal digits of precision
// This is sufficient for most cases
```

### Dealing with w = 0

```cpp
// Special case: w = 0 (direction vectors, not positions)
// These represent infinite points (directions)
// They don't undergo perspective division properly

// Example: Light direction in clip space
vec4 lightDirClip = projection * view * vec4(lightDir, 0.0);
// w = 0 means this is a direction, not a position
// OpenGL handles these specially
```

### Preventing NDC Overflow

```cpp
// If vertices have very large coordinates, NDC may overflow
// Solution: Use floating point with sufficient range
// Or normalize coordinates before transformation

// In rare cases, clamp to prevent issues
gl_Position = projection * view * model * vec4(aPos, 1.0);
gl_Position = clamp(gl_Position, -1e38, 1e38);  // Extreme cases only!
```

---

## The 30-Second Summary

- **NDC** = Normalized Device Coordinates (-1 to 1 cube)
- **Origin** = After perspective division (clip → NDC)
- **Range** = X: -1..1, Y: -1..1, Z: -1..1 (OpenGL)
- **Purpose** = Resolution-independent intermediate space
- **Clipping** = Any vertex outside -1..1 range is clipped
- **Viewport Transform** = Maps NDC to screen pixels
- **Depth** = Non-linear in perspective (more precision near camera)
- **API Differences** = OpenGL: Z -1..1, Y up; DirectX/Vulkan: Z 0..1, Y varies

**NDC is the universal coordinate system that bridges 3D world space and 2D screen space - it's where perspective happens and where visibility is finally determined.**

---

