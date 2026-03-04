# What is Depth Testing and Z-Buffer? - Beginner's Documentation

## The Painter's Dilemma Analogy

Depth testing and the Z-buffer can be understood through a painter creating a complex scene:

- **The Naive Painter** = Paints objects in random order, later objects cover earlier ones incorrectly
- **The Careful Painter** = Paints from back to front (painter's algorithm), but struggles with intersecting objects
- **The Magic Canvas** = Z-buffer - remembers the distance of every painted pixel
- **The Magic Rule** = Depth testing - "Only paint if this would be closer than what's already here"

**Just as a painter needs to know which objects are in front of others, the GPU needs to know which pixels are visible and which are hidden behind other surfaces.**

---

## Part 1: The Visibility Problem

### What Problem Does Depth Testing Solve?

Without depth testing, the GPU draws triangles in the order they're submitted:

```
SCENE WITH TWO CUBES:

    Cube A (front)      Cube B (back)
         ■                  ■
         ■                  ■
         ■                  ■
    (closer)            (farther)

RENDER ORDER 1: Draw Cube A first, then Cube B
Result: Cube B draws over Cube A - WRONG! (back in front)

RENDER ORDER 2: Draw Cube B first, then Cube A
Result: Cube A draws over Cube B - CORRECT!

Problem: Correctness depends on draw order!
```

### The Painter's Algorithm (The Old Way)

```cpp
// Sort all triangles by depth (back to front)
sort(triangles.begin(), triangles.end(), 
     [](Triangle a, Triangle b) {
         return a.averageZ > b.averageZ;  // Farthest first
     });

// Draw in sorted order
for (Triangle& tri : triangles) {
    drawTriangle(tri);
}

// Problems:
// 1. Sorting is expensive (O(n log n))
// 2. Intersecting triangles impossible
// 3. Per-triangle sorting required
// 4. Doesn't handle transparency well
```

### The Z-Buffer Solution

```
WITHOUT Z-BUFFER:                WITH Z-BUFFER:
    ██████                          ██████
   ████████                        ████████
  ██████████                      ██████████
 ████████████                    ████████████
██████████████                  ██████████████

Depends on draw order          Always correct regardless
                                of draw order
```

---

## Part 2: What is the Z-Buffer?

### Definition

The **Z-buffer** (also called **depth buffer**) is a 2D array of memory, the same size as the screen, that stores the depth (distance from camera) of the closest fragment at each pixel.

### Visual Representation

```
SCREEN PIXELS (2D view):
    x=0 → → → → → → → → → width
y=0 ┌─────────────────────┐
 ↓  │ 0.2 0.2 0.3 0.5 0.7 │  Each number = depth value
 ↓  │ 0.2 0.3 0.5 0.7 0.9 │  (0 = near, 1 = far)
 ↓  │ 0.3 0.5 0.7 0.9 1.0 │
 ↓  │ 0.5 0.7 0.9 1.0 1.0 │
y=h └─────────────────────┘

Darker = closer to camera
Lighter = farther from camera
```

### Memory Layout

```cpp
// Conceptual Z-buffer
struct ZBuffer {
    int width;           // Screen width in pixels
    int height;          // Screen height in pixels
    float* depths;       // Array of depth values
    
    // Each pixel gets a depth value
    float getDepth(int x, int y) {
        return depths[y * width + x];
    }
    
    void setDepth(int x, int y, float depth) {
        depths[y * width + x] = depth;
    }
};

// At 1920x1080, Z-buffer size = 1920*1080*4 = ~8 MB
// Plus stencil buffer (optional) = another ~8 MB
```

---

## Part 3: How Depth Testing Works

### The Depth Test Algorithm

```cpp
// For each fragment (potential pixel)
bool depthTest(int x, int y, float fragmentDepth) {
    // Get current depth from Z-buffer
    float currentDepth = zBuffer[x][y];
    
    // Test: Is fragment closer than what's already there?
    // (In OpenGL, LESS = closer wins)
    if (fragmentDepth < currentDepth) {
        // Fragment is visible - update Z-buffer
        zBuffer[x][y] = fragmentDepth;
        return true;  // Pass depth test
    } else {
        // Fragment is hidden - discard
        return false; // Fail depth test
    }
}
```

### Visual Example

```
DEPTH TEST IN ACTION:

Initial Z-buffer (all 1.0 = far plane):
[1.0] [1.0] [1.0]
[1.0] [1.0] [1.0]
[1.0] [1.0] [1.0]

Draw red triangle (depth = 0.2):
┌─────┐
│█ 0.2│  Update where triangle covers
│█ 0.2│  Z-buffer becomes 0.2 in those pixels
│█ 0.2│
└─────┘
[0.2] [1.0] [1.0]
[0.2] [1.0] [1.0]
[0.2] [1.0] [1.0]

Draw blue triangle (depth = 0.5):
┌─────┐
│ ███ │  Blue triangle tries to write
│ ███ │  Depth test: 0.5 > 0.2? FAIL
│ ███ │  Blue pixels are discarded!
└─────┘
Result: Only red triangle visible (correct!)
```

### Depth Test Diagram

```
CAMERA VIEW:
    [Camera] ----● (near object, z=0.2)
              \
               \---● (far object, z=0.5)
                \   (hidden behind near object)

Z-BUFFER AFTER RENDERING:
Pixel (x,y) where both project:
┌─────────────────────┐
│        0.2          │ ← Stores closest depth (near object)
│                     │    Far object's depth test fails
└─────────────────────┘
```

---

## Part 4: Enabling and Configuring Depth Testing

### Basic Setup

```cpp
// In initialization
#include <glad/glad.h>
#include <GLFW/glfw3.h>

// Enable depth testing
glEnable(GL_DEPTH_TEST);

// Set depth function (how to compare)
glDepthFunc(GL_LESS);  // Default: pass if fragment depth < stored depth

// Clear depth buffer each frame
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
```

### Depth Functions

```cpp
// Available depth comparison functions
glDepthFunc(GL_NEVER);    // Never pass (nothing visible)
glDepthFunc(GL_LESS);     // Pass if fragment depth < stored (default, most common)
glDepthFunc(GL_EQUAL);    // Pass if equal
glDepthFunc(GL_LEQUAL);   // Pass if fragment depth ≤ stored
glDepthFunc(GL_GREATER);  // Pass if fragment depth > stored
glDepthFunc(GL_NOTEQUAL); // Pass if not equal
glDepthFunc(GL_GEQUAL);   // Pass if fragment depth ≥ stored
glDepthFunc(GL_ALWAYS);   // Always pass (no depth testing)

// Visual effects of different functions:
// GL_LESS:   Normal rendering (closer objects visible)
// GL_GREATER: "X-ray" effect (farther objects visible)
// GL_ALWAYS:  No depth testing (draw order matters)
```

### Depth Mask (Writing to Z-buffer)

```cpp
// Enable/disable depth writing
glDepthMask(GL_TRUE);   // Enable writing to depth buffer (default)
glDepthMask(GL_FALSE);  // Disable writing (read-only mode)

// Use cases:
// - Skybox: Write disabled (always background)
// - Transparent objects: Write disabled (need special handling)
// - Shadow maps: Write enabled (need depth info)
// - Depth prepass: Write enabled, color disabled
```

### Clearing the Depth Buffer

```cpp
// Each frame, clear both color and depth
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

// Set clear depth value
glClearDepth(1.0f);  // Default: 1.0 (far plane)

// Depth values range from glDepthRange
glDepthRange(0.0f, 1.0f);  // Default: near=0, far=1
```

---

## Part 5: Depth Values and Precision

### How Depth is Calculated

```cpp
// In perspective projection, depth is NOT linear!
// View space Z → Depth buffer value

// For perspective projection:
depthBuffer = (far * (z_view + near)) / (z_view * (far - near));
// This is approximately 1/z, giving more precision near camera

// For orthographic projection:
depthBuffer = (z_view + far) / (far - near);
// This is linear (equal precision everywhere)
```

### Depth Precision Visualization

```
PERSPECTIVE DEPTH DISTRIBUTION:

Near plane (z = -0.1) → depth = 0.999  (lots of precision)
                     ↓
                     ↓  Most depth values used here
                     ↓
Far plane (z = -100) → depth = 0.001   (little precision)

The graph of 1/z shows why:
depth
1.0 ┤          ╱
    │        ╱
0.5 ┤      ╱
    │    ╱
0.0 ┼──╱────────── z
    0  near     far

Precision is highest where slope is steepest (near camera)
```

### Why Near/Far Planes Matter

```cpp
// BAD: Huge range kills precision
glm::perspective(45.0f, aspect, 0.0001f, 1000000.0f);
// Result: Z-fighting everywhere, especially at distance

// GOOD: Tight ranges preserve precision
glm::perspective(45.0f, aspect, 0.1f, 100.0f);   // Indoor scene
glm::perspective(45.0f, aspect, 1.0f, 10000.0f); // Outdoor scene

// Rule of thumb: near as far as possible, far as close as possible
// Ratio far/near > 1000 starts to lose precision
```

### Depth Precision in Practice

```cpp
// At 24-bit depth buffer (16.7 million possible values)

// With near=0.1, far=100.0 (ratio 1000:1)
// At near plane:  precision ~0.00005 units
// At far plane:   precision ~0.5 units

// With near=0.1, far=10000.0 (ratio 100,000:1)
// At near plane:  precision ~0.00005 units (same)
// At far plane:   precision ~50 units! (very coarse)

// This is why distant objects Z-fight - not enough precision!
```

---

## Part 6: Z-Fighting (The Depth Buffer's Enemy)

### What is Z-Fighting?

**Z-fighting** occurs when two surfaces have nearly identical depth values, causing them to flicker as the render order changes.

```
VISUAL Z-FIGHTING:
Frame 1:          Frame 2:          Frame 3:
████▒▒▒▒          ▒▒▒▒████          ████▒▒▒▒
████▒▒▒▒          ▒▒▒▒████          ████▒▒▒▒
████▒▒▒▒          ▒▒▒▒████          ████▒▒▒▒

Surfaces alternate which one "wins" the depth test
Result: Flickering, moiré patterns, "shimmering"
```

### Common Z-Fighting Scenarios

```cpp
// 1. Coplanar surfaces
float groundHeight = 0.0f;
float decalHeight = 0.0001f;  // Very slight offset
// The decal and ground will Z-fight!

// 2. Large distance ranges
// Near plane 0.1, far plane 10000
// Two objects at 9999.9 and 10000.0 share same depth value

// 3. Low precision depth buffer (16-bit)
// Not enough unique values for the depth range

// 4. Bad projection matrix
// Near plane too close, far plane too far
```

### Solutions to Z-Fighting

```cpp
// SOLUTION 1: Polygon offset (for coplanar surfaces)
glEnable(GL_POLYGON_OFFSET_FILL);
glPolygonOffset(1.0f, 1.0f);  // Factor, units

// Render ground first (no offset)
drawGround();

// Enable offset for decals
glEnable(GL_POLYGON_OFFSET_FILL);
glPolygonOffset(-1.0f, -1.0f);  // Push decals closer
drawDecals();
glDisable(GL_POLYGON_OFFSET_FILL);

// SOLUTION 2: Tighten near/far planes
float minDist = getClosestObjectDistance();
float maxDist = getFarthestObjectDistance();
nearPlane = minDist * 0.5f;  // Some margin
farPlane = maxDist * 1.5f;

// SOLUTION 3: Reverse Z-buffer (advanced)
// Use floating point depth, map near=1, far=0
// Better precision distribution

// SOLUTION 4: Logarithmic depth (advanced)
// Custom projection matrix that distributes depth logarithmically
```

---

## Part 7: Early Depth Testing (Hierarchical Z)

### What is Early Z?

Modern GPUs can test depth **before** running the fragment shader, saving massive amounts of work.

```
WITHOUT EARLY Z:
Fragment → [Fragment Shader] → [Depth Test] → Write
           (expensive!)          (maybe discard)

WITH EARLY Z:
Fragment → [Depth Test] → [Fragment Shader] → Write
           (cheap!)         (only if visible)

Hidden pixels never run fragment shader!
```

### Early Z Conditions

```cpp
// Early Z works when:
// 1. No modifications to gl_FragDepth in shader
// 2. No discard statements
// 3. No alpha testing
// 4. Shader doesn't write to depth

// Example where early Z works:
#version 330 core
out vec4 FragColor;

void main() {
    // Early Z can run before this shader
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}

// Example where early Z is disabled:
#version 330 core
out vec4 FragColor;

void main() {
    if (someCondition) {
        discard;  // Early Z disabled!
    }
    gl_FragDepth = 0.5;  // Early Z disabled!
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
```

### Depth Prepass Technique

```cpp
// Technique: Render depth first, then color
// Useful for complex shaders

// PASS 1: Depth only
glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE); // Disable color writes
glDepthMask(GL_TRUE);  // Enable depth writes

for (Object& obj : scene) {
    simpleDepthShader.use();  // Minimal shader
    obj.draw();
}

// PASS 2: Color with depth test
glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);  // Enable color
glDepthFunc(GL_EQUAL);  // Only draw where depth already set

for (Object& obj : scene) {
    complexShader.use();  // Expensive shader
    obj.draw();  // Only visible pixels run complex shader
}

glDepthFunc(GL_LESS);  // Restore default
```

---

## Part 8: Depth Buffer in Practice

### Creating a Depth Buffer

```cpp
// With GLFW, depth buffer is created automatically
glfwWindowHint(GLFW_DEPTH_BITS, 24);  // Request 24-bit depth

// With manual framebuffer creation
unsigned int depthBuffer;
glGenRenderbuffers(1, &depthBuffer);
glBindRenderbuffer(GL_RENDERBUFFER, depthBuffer);
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, width, height);
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                          GL_RENDERBUFFER, depthBuffer);

// Or create depth texture
unsigned int depthTexture;
glGenTextures(1, &depthTexture);
glBindTexture(GL_TEXTURE_2D, depthTexture);
glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24,
             width, height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, NULL);
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                       GL_TEXTURE_2D, depthTexture, 0);
```

### Reading the Depth Buffer

```cpp
// Read a single pixel's depth
float depth;
glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, &depth);
// depth is 0.0 (near) to 1.0 (far)

// Copy depth buffer to texture
glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT,
                 0, 0, width, height, 0);

// Save depth buffer as image (debugging)
std::vector<float> depths(width * height);
glReadPixels(0, 0, width, height, GL_DEPTH_COMPONENT, GL_FLOAT, depths.data());
// Save to file, visualize, etc.
```

### Visualizing Depth in Shaders

```glsl
// Fragment shader to visualize depth
#version 330 core
out vec4 FragColor;

void main() {
    // gl_FragCoord.z contains depth (0 near, 1 far)
    float depth = gl_FragCoord.z;
    
    // Visualize as grayscale
    FragColor = vec4(vec3(depth), 1.0);
    
    // Or create a heat map
    vec3 nearColor = vec3(1.0, 0.0, 0.0);  // Red = near
    vec3 farColor = vec3(0.0, 0.0, 1.0);   // Blue = far
    vec3 color = mix(nearColor, farColor, depth);
    FragColor = vec4(color, 1.0);
    
    // Or show depth bands
    float bands = fract(depth * 10.0);
    if (bands < 0.1) {
        FragColor = vec4(1.0, 1.0, 1.0, 1.0);  // White bands
    } else {
        FragColor = vec4(0.2, 0.2, 0.2, 1.0);  // Dark elsewhere
    }
}
```

---

## Part 9: Depth Testing and Transparency

### The Transparency Problem

```cpp
// Transparent objects need special handling!
glEnable(GL_BLEND);
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

// Problem: Depth testing + transparency
// If a transparent object writes to depth buffer,
// it can hide objects behind it that should be visible through it!
```

### Solutions for Transparency

```cpp
// METHOD 1: Sort transparent objects (painter's algorithm)
// Draw opaque objects first (with depth write)
glDepthMask(GL_TRUE);
drawOpaqueObjects();

// Sort transparent objects back-to-front
sort(transparentObjects, [](auto a, auto b) {
    return a.distance > b.distance;  // Farthest first
});

// Draw transparent objects without depth write
glDepthMask(GL_FALSE);
for (auto& obj : transparentObjects) {
    obj.draw();
}
glDepthMask(GL_TRUE);

// METHOD 2: Order Independent Transparency (advanced)
// - Depth peeling
// - Linked lists of fragments
// - Requires modern OpenGL (4.x+)
```

---

## Part 10: Advanced Depth Techniques

### Shadow Mapping with Depth

```cpp
// Shadow maps use depth buffer from light's perspective
// 1. Render scene from light's view, store depths
// 2. Render from camera, compare depths

// Light's depth texture
glBindFramebuffer(GL_FRAMEBUFFER, depthFBO);
glClear(GL_DEPTH_BUFFER_BIT);
renderSceneFromLight();  // Only depth writes

// Camera's view - compare depths
vec4 lightSpacePos = lightMatrix * worldPos;
float closestDepth = texture(shadowMap, lightSpacePos.xy).r;
float currentDepth = lightSpacePos.z;
float shadow = currentDepth > closestDepth ? 1.0 : 0.0;
```

### Depth of Field Effect

```glsl
// Use depth buffer to blur based on distance
#version 330 core
uniform sampler2D sceneTexture;
uniform sampler2D depthTexture;
uniform float focusDistance;
uniform float focusRange;

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    float depth = texture(depthTexture, uv).r;
    
    // Calculate blur amount based on depth difference
    float blurAmount = abs(depth - focusDistance) / focusRange;
    blurAmount = clamp(blurAmount, 0.0, 1.0);
    
    // Sample multiple times with offset
    vec4 color = vec4(0.0);
    for (int i = 0; i < samples; i++) {
        vec2 offset = vec2(cos(i), sin(i)) * blurAmount * pixelSize;
        color += texture(sceneTexture, uv + offset);
    }
    
    FragColor = color / samples;
}
```

### Infinite Ocean/Landscape

```cpp
// For infinite scenes, use logarithmic depth
// Custom projection matrix
float C = 1.0;  // Controls depth distribution
float far = 1000000.0;
float near = 0.1;

glm::mat4 logProjection = glm::mat4(0.0);
logProjection[0][0] = 1.0f / (aspect * tan(fov/2));
logProjection[1][1] = 1.0f / tan(fov/2);
logProjection[2][2] = 2.0f / log2(far/near);
logProjection[3][2] = 2.0f * log2(near) / log2(far/near) + 1.0f;
logProjection[2][3] = -1.0f;

// This gives far better precision at distance
```

---

## Part 11: Debugging Depth Issues

### Visualizing the Depth Buffer

```glsl
// Fragment shader to debug depth
#version 330 core
out vec4 FragColor;

uniform sampler2D depthTexture;
uniform vec2 screenSize;

void main() {
    vec2 uv = gl_FragCoord.xy / screenSize;
    float depth = texture(depthTexture, uv).r;
    
    // Option 1: Grayscale
    FragColor = vec4(vec3(depth), 1.0);
    
    // Option 2: Heat map
    vec3 color;
    if (depth < 0.33)
        color = mix(vec3(1,0,0), vec3(1,1,0), depth * 3.0);
    else if (depth < 0.66)
        color = mix(vec3(1,1,0), vec3(0,1,0), (depth - 0.33) * 3.0);
    else
        color = mix(vec3(0,1,0), vec3(0,0,1), (depth - 0.66) * 3.0);
    
    FragColor = vec4(color, 1.0);
    
    // Option 3: Banding (show depth quantization)
    float bands = round(depth * 20.0) / 20.0;
    FragColor = vec4(vec3(bands), 1.0);
}
```

### Common Depth Problems

```cpp
// PROBLEM: Objects disappear when too close
// Cause: Near plane too far
// Fix: Decrease near plane value

// PROBLEM: Distant objects Z-fight
// Cause: Far/near ratio too large
// Fix: Increase near plane, decrease far plane

// PROBLEM: Transparent objects block others
// Cause: Transparent objects writing to depth buffer
// Fix: glDepthMask(GL_FALSE) for transparent objects

// PROBLEM: Decals flicker on surfaces
// Cause: Coplanar surfaces
// Fix: Use polygon offset or small epsilon

// PROBLEM: Shadow acne (shadows have dots/patterns)
// Cause: Shadow map precision issues
// Fix: Add bias, use slope-scaled bias
```

### Depth Testing State Queries

```cpp
// Check current depth state
GLboolean depthEnabled;
glGetBooleanv(GL_DEPTH_TEST, &depthEnabled);

GLint depthFunc;
glGetIntegerv(GL_DEPTH_FUNC, &depthFunc);

GLboolean depthMask;
glGetBooleanv(GL_DEPTH_WRITEMASK, &depthMask);

GLfloat clearDepth;
glGetFloatv(GL_DEPTH_CLEAR_VALUE, &clearDepth);

GLfloat depthRange[2];
glGetFloatv(GL_DEPTH_RANGE, depthRange);
```

---

## The 30-Second Summary

- **Z-Buffer** = Memory array storing depth of closest fragment at each pixel
- **Depth Testing** = Process of comparing fragment depth against stored depth
- **Default Behavior** = Closer fragments (smaller Z) replace farther ones (GL_LESS)
- **Enabling** = `glEnable(GL_DEPTH_TEST)` and clear each frame
- **Precision** = Non-linear in perspective (more precision near camera)
- **Z-Fighting** = Occurs when depths are nearly equal (flickering)
- **Early Z** = Hardware optimization testing depth before fragment shading
- **Transparency** = Requires special handling (sorting, no depth write)
- **Near/Far Planes** = Keep ranges tight for best precision

**Depth testing and the Z-buffer solve the visibility problem efficiently, allowing correct rendering of complex 3D scenes regardless of draw order - they're fundamental to modern real-time graphics.**