# What is Rasterization? 

## The Mosaic Artist Analogy

Rasterization can be understood through a mosaic artist creating a picture from tiny tiles:

- **The Sculptor's Model** = The 3D geometry (triangles, lines, points)
- **The Mosaic Grid** = The pixel grid on screen
- **The Artist's Decision** = Rasterization - deciding which tiles (pixels) get which colors
- **The Tile Colors** = Interpolated vertex attributes (UVs, normals, colors)
- **The Finished Mosaic** = The final rendered image

**Just as a mosaic artist must decide which colored tile goes where to recreate a picture, rasterization determines which pixels are covered by each triangle and what color they should be.**

---

## Part 1: What is Rasterization?

### Definition

**Rasterization** is the process of converting geometric primitives (triangles, lines, points) into a grid of pixels (fragments) that can be displayed on screen. It's the step that bridges the gap between the mathematical world of 3D geometry and the physical world of discrete pixels.

### The Rasterization Pipeline Position

```
VERTEX SHADER (programmable)
    ↓
TESSELLATION (optional)
    ↓
GEOMETRY SHADER (optional)
    ↓
[ RASTERIZATION ] ←─── YOU ARE HERE
    ↓
FRAGMENT SHADER (programmable)
    ↓
PER-FRAGMENT OPERATIONS
    ↓
FRAMEBUFFER
```

### Core Concept

```
BEFORE RASTERIZATION (mathematical triangles):
    ▲       ▲
   / \     / \
  /   \   /   \
 /     \ /     \
/_______X_______\

AFTER RASTERIZATION (pixels):
    ████    ████
   ██████  ██████
  ████████████████
 ██████████████████
████████████████████

Each █ represents one pixel/fragment
```

---

## Part 2: The Rasterization Process - Step by Step

### Step 1: Vertex Processing Complete

Before rasterization begins, vertices have been transformed to screen space:

```cpp
// After vertex shader and perspective divide, we have screen coordinates
struct ScreenSpaceVertex {
    float x, y;      // Screen coordinates (pixels)
    float z;         // Depth (0 near, 1 far)
    float u, v;      // Interpolated UVs (will be interpolated)
    float r, g, b;   // Interpolated colors
    // ... other attributes
};

// Example: Triangle vertices in screen space
Vertex v0 = {120, 100, 0.2, 0.0, 0.0, 1.0, 0.0};  // Red at top
Vertex v1 = {50, 300, 0.5, 1.0, 0.0, 0.0, 1.0};   // Green at bottom-left
Vertex v2 = {350, 280, 0.7, 0.0, 1.0, 0.0, 0.0};  // Blue at bottom-right
```

### Step 2: Determine Pixel Coverage

The rasterizer figures out which pixels are inside the triangle:

```
SCREEN PIXEL GRID:
y=0  ┌─────────────────┐
     │. . . . . . . . .│
     │. . . . . . . . .│
     │. . . █████ . . .│  █ = Pixel fully inside triangle
     │. . ███████ . . .│  ▒ = Pixel partially covered (edge)
     │. █████████ . . .│  . = Pixel outside triangle
     │. █████████ . . .│
     │. . ███████ . . .│
     │. . . █████ . . .│
y=h  └─────────────────┘
     x=0              x=w
```

### Step 3: Edge Function Testing

The rasterizer uses **edge functions** to test if a pixel is inside a triangle:

```cpp
// For each edge of the triangle, test which side the pixel is on
bool isPointInsideTriangle(Point p, Triangle t) {
    // For each edge (v0→v1, v1→v2, v2→v0)
    for (each edge) {
        // Compute cross product to determine side
        float edgeTest = (edge.v1.x - edge.v0.x) * (p.y - edge.v0.y) -
                         (edge.v1.y - edge.v0.y) * (p.x - edge.v0.x);
        
        // If pixel is on wrong side of any edge, it's outside
        if (edgeTest < 0) return false;
    }
    return true;  // Inside all edges
}

// This test runs for every candidate pixel!
```

### Step 4: Attribute Interpolation

Once a pixel is determined to be inside the triangle, the rasterizer interpolates all vertex attributes:

```cpp
// Barycentric coordinates determine how much each vertex contributes
// For pixel P, find weights w0, w1, w2 where w0 + w1 + w2 = 1

float w0, w1, w2 = computeBarycentric(p, v0, v1, v2);

// Interpolate all attributes
float pixelZ = w0 * v0.z + w1 * v1.z + w2 * v2.z;
float pixelU = w0 * v0.u + w1 * v1.u + w2 * v2.u;
float pixelV = w0 * v0.v + w1 * v1.v + w2 * v2.v;
Color pixelColor = w0 * v0.color + w1 * v1.color + w2 * v2.color;

// Result: Smooth gradients across the triangle
```

---

## Part 3: Barycentric Coordinates - The Math of Interpolation

### What are Barycentric Coordinates?

**Barycentric coordinates** (w0, w1, w2) represent a point's position relative to triangle vertices, where:

- w0 + w1 + w2 = 1
- At vertex 0: (w0, w1, w2) = (1, 0, 0)
- At vertex 1: (w0, w1, w2) = (0, 1, 0)
- At vertex 2: (w0, w1, w2) = (0, 0, 1)
- At center: (w0, w1, w2) = (1/3, 1/3, 1/3)

### Visualizing Barycentric Coordinates

```
TRIANGLE WITH BARYCENTRIC COORDINATES:
    
    v0 (1,0,0)
        ●
       / \
      /   \
     /     \
    /       \
   /         \
  /           \
 ●─────────────●
v1 (0,1,0)    v2 (0,0,1)

Point P at center: (0.33, 0.33, 0.33)
Point near v0: (0.8, 0.1, 0.1)
Point on edge v1-v2: (0, 0.5, 0.5)
```

### Computing Barycentric Coordinates

```cpp
// Compute barycentric coordinates for point P in triangle (v0,v1,v2)
glm::vec3 computeBarycentric(glm::vec2 p, 
                              glm::vec2 v0, glm::vec2 v1, glm::vec2 v2) {
    // Compute vectors
    glm::vec2 v0v1 = v1 - v0;
    glm::vec2 v0v2 = v2 - v0;
    glm::vec2 v0p = p - v0;
    
    // Compute dot products
    float d00 = glm::dot(v0v1, v0v1);
    float d01 = glm::dot(v0v1, v0v2);
    float d11 = glm::dot(v0v2, v0v2);
    float d20 = glm::dot(v0p, v0v1);
    float d21 = glm::dot(v0p, v0v2);
    
    // Compute barycentric coordinates
    float denom = d00 * d11 - d01 * d01;
    float w1 = (d11 * d20 - d01 * d21) / denom;
    float w2 = (d00 * d21 - d01 * d20) / denom;
    float w0 = 1.0f - w1 - w2;
    
    return glm::vec3(w0, w1, w2);
}
```

---

## Part 4: Perspective-Correct Interpolation

### The Problem with Simple Interpolation

```
WRONG: Linear interpolation in screen space
    v0 (Z=10)                 v1 (Z=100)
      ●────────────────────────●
      Colors should blend correctly, but
      perspective makes it non-linear!

The middle point (50% along screen distance)
is NOT 50% along world distance due to perspective.
```

### Perspective Correction Formula

```glsl
// In hardware, interpolation uses 1/Z weighting
// For attribute A:
A_pixel = (A0/Z0 * w0 + A1/Z1 * w1 + A2/Z2 * w2) / 
          (1/Z0 * w0 + 1/Z1 * w1 + 1/Z2 * w2)

// This is why vertex shader outputs include Z!
// The rasterizer needs depth for correct interpolation
```

### Visual Difference

```
PERSPECTIVE-CORRECT:          LINEAR (WRONG):
    ██████                        ██████
   ████████                      ████████
  ██████████                    ██████████
 ████████████                  ████████████
██████████████                ██████████████

Texture looks right            Texture appears distorted
Objects have proper 3D form    "Skewed" look
```

---

## Part 5: Coverage and Anti-Aliasing

### Pixel Coverage Types

```
PIXEL COVERAGE:
┌─────┬─────┬─────┐
│     │     │     │  □ = No coverage (0%)
├─────┼─────┼─────┤
│     │ ███ │ ▒▒▒ │  █ = Full coverage (100%)
├─────┼─────┼─────┤  ▒ = Partial coverage (edge)
│     │ ▒▒▒ │     │
└─────┴─────┴─────┘

The rasterizer computes coverage percentage for edge pixels
This is crucial for anti-aliasing!
```

### Aliasing (The "Jaggies")

```
WITHOUT ANTI-ALIASING:
    ┌─────┐
    │ ███ │  Jagged edges look stair-stepped
    │███  │  due to binary coverage (either 0% or 100%)
    │██   │
    └─────┘

Each pixel is either triangle color or background
Results in harsh, pixelated edges
```

### Anti-Aliasing Techniques

```cpp
// 1. SUPERSAMPLING (SSAA)
// Render at higher resolution, then downsample
// Example: 4x SSAA renders at 4x resolution
// Expensive but high quality

// 2. MULTISAMPLING (MSAA)
// Run fragment shader once per pixel, but test coverage at multiple samples
// Each pixel has multiple coverage samples, one color
// Good balance of quality and performance

// 3. FXAA (Fast Approximate AA)
// Post-process effect that blurs edges
// Fast but can blur texture detail

// 4. Temporal AA (TAA)
// Use previous frames to smooth edges
// Common in modern games
```

---

## Part 6: Early Rasterization Optimizations

### Back-Face Culling

Before detailed rasterization, the GPU can discard triangles facing away:

```cpp
// In rasterizer, check triangle orientation
bool isFrontFace(Vertex v0, Vertex v1, Vertex v2) {
    // Compute signed area (cross product)
    float area = (v1.x - v0.x) * (v2.y - v0.y) - 
                 (v2.x - v0.x) * (v1.y - v0.y);
    
    // Positive area = front face (in OpenGL with default winding)
    return area > 0;
}

// If triangle is back-facing and back-face culling enabled,
// discard entire triangle without rasterizing!
```

### Frustum Culling

Entire triangles outside viewport are skipped:

```cpp
// Quick reject test
bool triangleInViewport(Vertex v0, Vertex v1, Vertex v2) {
    // Get bounding box of triangle
    float minX = min(v0.x, v1.x, v2.x);
    float maxX = max(v0.x, v1.x, v2.x);
    float minY = min(v0.y, v1.y, v2.y);
    float maxY = max(v0.y, v1.y, v2.y);
    
    // If bounding box doesn't overlap viewport, reject
    if (maxX < 0 || minX > viewportWidth) return false;
    if (maxY < 0 || minY > viewportHeight) return false;
    
    return true;
}
```

### Guard-Band Clipping

Modern GPUs use a guard band around the viewport:

```
VIEWPORT WITH GUARD BAND:
┌─────────────────────────────────────┐
│  Guard band (invisible)             │
│    ┌───────────────────────┐        │
│    │                       │        │
│    │      Viewport         │        │
│    │                       │        │
│    └───────────────────────┘        │
│                                     │
└─────────────────────────────────────┘

Triangles slightly outside viewport but inside guard band
can be rasterized without expensive clipping operations
```

---

## Part 7: The Rasterizer in Hardware

### Parallel Processing

```cpp
// GPUs rasterize many triangles simultaneously
// Each triangle goes to a different rasterizer unit

RASTERIZER UNIT ARCHITECTURE:
┌──────────────────────────────────────────────┐
│ Triangle Setup                       │
│ └→ Edge Walker (generates spans)    │
│    └→ Span Generator (generates fragments)
│       └→ Interpolator (computes attributes)
│          └→ Fragment Output          │
└──────────────────────────────────────────────┘

× 16-128 parallel units!
```

### Tile-Based Rasterization (Mobile GPUs)

```cpp
// Mobile GPUs (PowerVR, Mali, Adreno) use tile-based rendering
// Screen divided into tiles (e.g., 32x32 pixels)

for (each tile) {
    // Find all triangles that affect this tile
    List triangles = binTriangles(tile);
    
    // Rasterize only those triangles
    for (each triangle in triangles) {
        rasterizeTriangle(triangle, tile);
    }
    
    // Write tile to framebuffer
    writeTile(tile);
}

// Benefits:
// - Less memory bandwidth
// - Better power efficiency
// - Early Z and hidden surface removal
```

---

## Part 8: Rasterization in the Graphics Pipeline

### Complete Pipeline View

```
APPLICATION (CPU)
    ↓ (Draw call)
COMMAND PROCESSOR
    ↓ (Vertex data)
VERTEX SHADER (per-vertex)
    ↓ (Transformed vertices)
PRIMITIVE ASSEMBLY
    ↓ (Triangles/Lines/Points)
[ RASTERIZATION ] ←─── FOCUS HERE
    ↓ (Fragments)
FRAGMENT SHADER (per-fragment)
    ↓ (Colored fragments)
PER-FRAGMENT TESTS (Depth, Stencil, Blending)
    ↓ (Final pixels)
FRAMEBUFFER
```

### What Rasterization Produces

```cpp
// A fragment contains:
struct Fragment {
    // Screen position
    int x, y;
    
    // Depth value (for depth testing)
    float depth;
    
    // Interpolated attributes
    vec2 uv;        // Texture coordinates
    vec3 normal;    // Surface normal
    vec3 worldPos;  // World position
    vec4 color;     // Base color
    
    // Coverage information (for anti-aliasing)
    float coverage;
    
    // Which primitive generated this fragment
    int primitiveID;
};
```

---

## Part 9: Rasterization vs Ray Tracing

### Fundamental Difference

| Aspect | Rasterization | Ray Tracing |
|--------|--------------|-------------|
| **Approach** | Project triangles to screen | Shoot rays from camera |
| **Algorithm** | "For each triangle, find pixels" | "For each pixel, find intersections" |
| **Order** | Object-order | Image-order |
| **Complexity** | O(triangles) | O(pixels × rays) |
| **Accuracy** | Approximate (requires tricks) | Physically accurate |
| **Speed** | Very fast (real-time) | Slow (offline or with RT cores) |
| **Hardware** | Traditional GPUs | RTX cores, dedicated hardware |

### Visual Comparison

```
RASTERIZATION:
Triangle 1 → Pixels A,B,C
Triangle 2 → Pixels D,E,F
Triangle 3 → Pixels G,H,I

Processes triangles, finds covering pixels

RAY TRACING:
Pixel 1 → Shoot ray → Find intersection
Pixel 2 → Shoot ray → Find intersection
Pixel 3 → Shoot ray → Find intersection

Processes pixels, finds intersecting triangles
```

### Hybrid Approaches

Modern games combine both:

```cpp
// Rasterization for main geometry
rasterizeScene();

// Ray tracing for specific effects
rayTraceShadows();      // Accurate shadows
rayTraceReflections();  // Perfect reflections
rayTraceGI();          // Global illumination

// Composite results
combineImages();
```

---

## Part 10: Debugging Rasterization

### Visualizing Rasterization

```glsl
// Fragment shader to visualize rasterization process

// 1. Show barycentric coordinates
vec3 bary = getBarycentric();
FragColor = vec4(bary, 1.0);
// Red = weight to vertex 0, Green = vertex 1, Blue = vertex 2

// 2. Show triangle edges
float edgeFactor = min(min(bary.x, bary.y), bary.z);
if (edgeFactor < 0.05) {
    FragColor = vec4(1.0, 1.0, 1.0, 1.0);  // White edges
} else {
    FragColor = texture(tex, uv);
}

// 3. Show pixel coverage
if (gl_FragCoord.x < 10 || gl_FragCoord.y < 10 ||
    gl_FragCoord.x > width-10 || gl_FragCoord.y > height-10) {
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red border
}

// 4. Visualize triangle density
float triSize = calculateTriangleSize();
FragColor = vec4(triSize / maxSize, 0.0, 0.0, 1.0);
```

### Common Rasterization Issues

```cpp
// PROBLEM: Cracks between triangles
// Cause: Floating point precision, non-watertight meshes
// Fix: Ensure vertices exactly match at shared edges

// PROBLEM: T-junctions causing pixel gaps
// Cause: Vertex on edge of another triangle
// Fix: Triangulate properly, avoid T-junctions

// PROBLEM: Overdraw (same pixel shaded multiple times)
// Cause: Transparent objects, overlapping triangles
// Fix: Early Z, sort transparent objects, minimize overlap

// PROBLEM: Pixel sparkles (flickering)
// Cause: Z-fighting, two triangles at nearly same depth
// Fix: Adjust near/far planes, add small offsets
```

### Rasterization Performance Metrics

```cpp
// Key metrics to monitor:
float pixelsRendered = width * height * samples;
float trianglesRasterized = triangleCount;
float overdrawRatio = totalFragments / pixelsRendered;

// Ideal: overdrawRatio close to 1.0
// > 1.0 means pixels are shaded multiple times
// < 1.0 means some pixels never shaded (occluded)
```

---

## Part 11: Advanced Rasterization Features

### Variable Rate Shading (VRS)

```cpp
// Modern GPUs can shade at different rates
// Shade rate per 2x2 pixel block

// 1x1: Full detail (expensive)
rasterizeShadeRate(1, 1);  // Every pixel shaded

// 2x2: Quarter resolution (cheap)
rasterizeShadeRate(2, 2);  // One shade per 4 pixels

// Used for:
// - Peripheral vision (lower detail)
// - Motion blur areas
// - Performance optimization
```

### Conservative Rasterization

```cpp
// Standard rasterization: pixel center inside triangle
// Conservative: any pixel touched by triangle

STANDARD:                      CONSERVATIVE:
    ┌───┬───┐                     ┌───┬───┐
    │   │   │ Pixel center        │███│███│ Full coverage
    ├───┼───┤ inside triangle     ├───┼───┤
    │   │   │ only                │███│███│
    └───┴───┘                     └───┴───┘

Used for:
- Collision detection
- Occlusion culling
- Shadow maps
```

### Multi-View Rasterization

```cpp
// Rasterize same geometry to multiple views simultaneously
// Used for VR (left/right eye) and cubemap rendering

for (int view = 0; view < viewCount; view++) {
    rasterizeToView(view);
}

// Hardware can do this in one pass!
```

---

## The 30-Second Summary

- **Rasterization** = Converting triangles to pixels (fragments)
- **Process** = Coverage testing → Attribute interpolation → Fragment generation
- **Barycentric Coordinates** = Weights for interpolation (w0,w1,w2 sum to 1)
- **Perspective Correction** = Using 1/Z for correct texture mapping
- **Coverage** = How much of pixel triangle covers (0-100%)
- **Anti-Aliasing** = Techniques to smooth jagged edges (MSAA, FXAA, TAA)
- **Culling** = Discarding invisible triangles early (back-face, frustum)
- **Hardware** = Massively parallel rasterizer units
- **Output** = Fragments with position, depth, and interpolated attributes

**Rasterization is the bridge between the mathematical world of 3D geometry and the discrete world of pixels - it's what makes real-time 3D graphics possible by efficiently converting triangles into fragments for shading.**

---

**Next Step:** Ready to understand the fragment shader in detail?