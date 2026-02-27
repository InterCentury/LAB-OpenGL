# Coordinate Systems in Graphics 

## The Postal Service Analogy

Coordinate systems can be understood through a postal service delivering a package:

- **The Sculptor's Studio** = Local/Object Space (where the object is created)
- **The City Map** = World Space (where objects are placed in the scene)
- **The Observer's Location** = View/Eye Space (where the camera is positioned)
- **The Camera's View** = Clip Space (what the camera sees through its lens)
- **The Photograph** = Screen Space (the final 2D image)

**Just as a package goes through multiple transformations from sculptor to recipient, a vertex goes through multiple coordinate systems from model creation to final screen pixel.**

---

## Part 1: The Big Picture - Why Multiple Coordinate Systems?

### The Transformation Pipeline

```
OBJECT SPACE (local coordinates)
    ↓ [ MODEL MATRIX ]
WORLD SPACE (scene coordinates)
    ↓ [ VIEW MATRIX ]
VIEW/EYE SPACE (camera coordinates)
    ↓ [ PROJECTION MATRIX ]
CLIP SPACE (homogeneous coordinates)
    ↓ [ perspective division ]
NORMALIZED DEVICE COORDINATES (NDC)
    ↓ [ viewport transform ]
SCREEN SPACE (window coordinates)
```

### Why So Many Systems?

| Coordinate System | Purpose |
|-------------------|---------|
| **Object Space** | Model creation (sculpting, modeling) |
| **World Space** | Scene assembly (placing objects) |
| **View Space** | Camera positioning (where to look from) |
| **Clip Space** | Frustum culling (what's visible) |
| **NDC** | Hardware-friendly coordinates (-1 to 1) |
| **Screen Space** | Actual pixel positions |

---

## Part 2: Object/Local Space - The Sculptor's Studio

### Definition

**Object space** (also called **local space** or **model space**) is the coordinate system where a 3D model is defined. The model's origin is typically at its center or a convenient pivot point.

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Origin** | Usually at model's center or base |
| **Coordinates** | Relative to model's own pivot |
| **Independence** | Same regardless of where model is placed |
| **Creation** | Defined in 3D modeling software |
| **Reusability** | One model can be placed many times |

### Visual Example

```
A CUBE IN OBJECT SPACE:
        (+Y)
         ↑
         ●━━━●
        /|   /|
       ●━━━● │
       | │  | │
       | ●━━━|● → (+X)
       |/    |/
       ●━━━━●
      /
    (+Z)

Vertex positions (centered at origin):
Front-top-right:  ( 0.5,  0.5,  0.5)
Front-top-left:   (-0.5,  0.5,  0.5)  
Front-bottom-right:( 0.5, -0.5,  0.5)
Front-bottom-left: (-0.5, -0.5,  0.5)
Back-top-right:   ( 0.5,  0.5, -0.5)
... etc.

All vertices relative to center (0,0,0)
```

### Object Space in Code

```cpp
// A cube defined in object space (centered at origin)
float cubeVertices[] = {
    // Front face
    -0.5f, -0.5f,  0.5f,  // Vertex 0: bottom-left
     0.5f, -0.5f,  0.5f,  // Vertex 1: bottom-right
     0.5f,  0.5f,  0.5f,  // Vertex 2: top-right
    -0.5f,  0.5f,  0.5f,  // Vertex 3: top-left
    
    // Back face
    -0.5f, -0.5f, -0.5f,  // Vertex 4: bottom-left
     0.5f, -0.5f, -0.5f,  // Vertex 5: bottom-right
     0.5f,  0.5f, -0.5f,  // Vertex 6: top-right
    -0.5f,  0.5f, -0.5f,  // Vertex 7: top-left
};

// A sphere defined in object space (centered at origin)
// All vertices lie on sphere of radius 1.0
// Positions range from -1.0 to 1.0 in all axes
```

---

## Part 3: World Space - The City Map

### Definition

**World space** is the coordinate system where all objects in a scene are placed. Each object has its own position, rotation, and scale in world space.

### The Model Matrix

The **model matrix** transforms vertices from object space to world space:

```glsl
// Vertex shader
vec4 worldPosition = model * vec4(aPos, 1.0);
```

### Model Matrix Components

```
MODEL MATRIX = TRANSLATION × ROTATION × SCALE
(or in different orders depending on desired effect)

TRANSLATION MATRIX (move):
[ 1 0 0 tx ]
[ 0 1 0 ty ]
[ 0 0 1 tz ]
[ 0 0 0 1  ]

ROTATION MATRIX (rotate):
[ cosθ -sinθ 0 0 ]
[ sinθ  cosθ 0 0 ]
[ 0     0    1 0 ]
[ 0     0    0 1 ]

SCALE MATRIX (resize):
[ sx 0  0  0 ]
[ 0  sy 0  0 ]
[ 0  0  sz 0 ]
[ 0  0  0  1 ]
```

### Visual Example

```
WORLD SPACE WITH MULTIPLE OBJECTS:
    Y
    ↑
    |     ● (Tree at 5,0,10)
    |     
    |  🏠 (House at -10,0,15)
    |     □ (Car at 20,0,5)
    |         
    └──────────────────→ X
   /
  /
 ↓
 Z

Each object has its own position in world space:
- Tree: model matrix translates from object space to (5,0,10)
- House: model matrix translates to (-10,0,15) + rotates 90°
- Car: model matrix translates to (20,0,5) + scales 0.5
```

### World Space Example

```cpp
// Object space cube centered at origin
float cubeVertices[] = { /* ... */ };

// Different model matrices for different placements
glm::mat4 modelTree = glm::translate(glm::mat4(1.0f), glm::vec3(5.0f, 0.0f, 10.0f));

glm::mat4 modelHouse = glm::translate(glm::mat4(1.0f), glm::vec3(-10.0f, 0.0f, 15.0f));
modelHouse = glm::rotate(modelHouse, glm::radians(90.0f), glm::vec3(0.0f, 1.0f, 0.0f));

glm::mat4 modelCar = glm::translate(glm::mat4(1.0f), glm::vec3(20.0f, 0.0f, 5.0f));
modelCar = glm::scale(modelCar, glm::vec3(0.5f, 0.5f, 0.5f));

// Each cube rendered with different model matrix appears in different world positions
```

---

## Part 4: View/Eye Space - The Observer's Perspective

### Definition

**View space** (also called **eye space** or **camera space**) is the coordinate system with the camera at the origin. The camera looks down the negative Z axis (in OpenGL).

### The View Matrix

The **view matrix** transforms vertices from world space to view space:

```glsl
// Vertex shader
vec4 viewPosition = view * worldPosition;
```

### Camera Positioning

```
WORLD SPACE:                    VIEW SPACE (camera at origin):
    Y↑                              Y↑
     |                                |
     |    ● Object                    |    ● Object
     |  ↗                             |  ↗
     |📍 Camera                       |📍 Camera (now at origin)
     |                                |    Looks down -Z
     └──────→ X                       └──────→ X
    /                                 /
   /                                 /
  Z                                 Z

The view matrix effectively moves the entire world
so that camera is at origin looking down -Z.
```

### Building the View Matrix

```cpp
// Option 1: LookAt function (most common)
glm::mat4 view = glm::lookAt(
    glm::vec3(5.0f, 3.0f, 10.0f),  // Camera position in world
    glm::vec3(0.0f, 0.0f, 0.0f),   // Point camera looks at
    glm::vec3(0.0f, 1.0f, 0.0f)    // Up direction (usually Y)
);

// Option 2: Manual construction (translate then rotate)
glm::mat4 view = glm::translate(glm::mat4(1.0f), -cameraPosition);
view = glm::rotate(view, -cameraRotation.x, glm::vec3(1,0,0));
view = glm::rotate(view, -cameraRotation.y, glm::vec3(0,1,0));
```

### What View Space Looks Like

```
In view space:
- Camera is at (0,0,0)
- Camera looks down -Z axis
- +X is camera's right
- +Y is camera's up
- Objects in front of camera have negative Z
- Objects behind camera have positive Z

Example:
Object at world (5,0,10) with camera at (5,0,20) looking at origin:
World position relative to camera = (0,0,-10) in view space
```

---

## Part 5: Clip Space - The Camera's Lens

### Definition

**Clip space** is the coordinate system after applying projection. It's a homogeneous coordinate system (x, y, z, w) where the hardware determines if vertices are inside the visible region.

### The Projection Matrix

The **projection matrix** transforms vertices from view space to clip space:

```glsl
// Vertex shader
gl_Position = projection * viewPosition;
```

### Why Clip Space?

| Purpose | Description |
|---------|-------------|
| **Frustum Culling** | Determine what's visible |
| **Perspective Effect** | Objects farther appear smaller |
| **Homogeneous Coordinates** | Enable perspective division |
| **Clipping** | Cut geometry at view boundaries |

### Visualizing the Frustum

```
VIEW SPACE:                     CLIP SPACE (after projection):
    Y↑                              Y↑
     |  /────────┐                  |  ┌──────┐
     | /         │                  |  │      │
     |/          │                  |  │      │
     ○───────→ X   Far plane        |  │      │
    /|          │                   |  │      │
   / |          │                   |  └──────┘
  Z  └──────────┘                   └──────────→ X
     Near plane

Frustum (pyramid) becomes a cube (-1 to 1 in all axes)
```

---

## Part 6: Projection Matrices - Two Types

### Perspective Projection

Makes objects farther away appear smaller, like human vision.

```cpp
// Perspective projection matrix
glm::mat4 proj = glm::perspective(
    glm::radians(45.0f),  // Field of view (degrees converted to radians)
    16.0f / 9.0f,         // Aspect ratio (width/height)
    0.1f,                  // Near plane distance
    100.0f                 // Far plane distance
);

// Visual effect:
// - Objects at near plane appear normal size
// - Objects at far plane are tiny
// - Creates sense of depth and distance
```

### Orthographic Projection

Objects stay the same size regardless of distance, like engineering drawings.

```cpp
// Orthographic projection matrix
glm::mat4 proj = glm::ortho(
    -10.0f, 10.0f,   // Left, right
    -10.0f, 10.0f,   // Bottom, top
    0.1f, 100.0f     // Near, far
);

// Visual effect:
// - No perspective distortion
// - Parallel lines remain parallel
// - Good for 2D games, UI, CAD
```

### Comparison

```
PERSPECTIVE:                      ORTHOGRAPHIC:
    ██████                            ██████
       ██████                       ██████
          ██████                  ██████
             ██████              ██████
Objects shrink with distance    Same size regardless of distance
Realistic view                  Technical/2D view
```

---

## Part 7: Normalized Device Coordinates (NDC)

### Definition

After the vertex shader, OpenGL performs **perspective division** (dividing x, y, z by w) to transform clip space to **Normalized Device Coordinates (NDC)**.

### NDC Space

```
NDC COORDINATES:
    Y
    ↑
    │     (-1,1) ┌─────┐ (1,1)
    │            │     │
    │            │     │
    │            │     │
    │    (-1,-1) └─────┘ (1,-1)
    │
    └──────────────→ X
   /
  Z (into screen)

Range:
- X: -1 to 1 (left to right)
- Y: -1 to 1 (bottom to top)
- Z: -1 to 1 (near to far)

Any vertex outside these ranges is clipped (not rendered).
```

### The Perspective Division

```glsl
// After vertex shader, OpenGL automatically does:
ndc.x = gl_Position.x / gl_Position.w;
ndc.y = gl_Position.y / gl_Position.w;
ndc.z = gl_Position.z / gl_Position.w;

// This is why w component is important!
// For perspective: w contains distance information
// For orthographic: w is usually 1
```

---

## Part 8: Screen Space - The Final Image

### Definition

**Screen space** (also called **window space** or **pixel coordinates**) is the final 2D coordinate system where rendering actually happens.

### Viewport Transform

OpenGL automatically transforms NDC to screen space using the **viewport** settings:

```cpp
// Set viewport (usually in reshape callback)
glViewport(0, 0, windowWidth, windowHeight);

// Transformation formula:
screenX = (ndcX + 1.0) * (width / 2.0) + x;
screenY = (ndcY + 1.0) * (height / 2.0) + y;
screenZ = (ndcZ + 1.0) * (far - near) / 2.0 + near;

// Where:
// - x, y: viewport lower-left corner (usually 0,0)
// - width, height: viewport dimensions
// - near, far: depth range (usually 0,1)
```

### Visual Example

```
NDC (-1 to 1):                 SCREEN SPACE (0 to width/height):
    (-1,1)┌─────┐(1,1)             (0,0)┌─────┐(1920,0)
          │     │                       │     │
          │     │          →            │     │
          │     │                       │     │
   (-1,-1)└─────┘(1,-1)         (0,1080)└─────┘(1920,1080)

NDC point (0,0,0) → Screen point (960,540) on 1080p display
```

### Fragment Shader Access

```glsl
// In fragment shader, you can access screen coordinates
void main() {
    // gl_FragCoord.xy = screen space coordinates (pixels)
    // gl_FragCoord.z = depth (0 near, 1 far)
    
    // Create gradient based on screen position
    float red = gl_FragCoord.x / 1920.0;     // Horizontal gradient
    float green = gl_FragCoord.y / 1080.0;    // Vertical gradient
    
    FragColor = vec4(red, green, 0.0, 1.0);
}
```

---

## Part 9: Complete Transformation Example

### From Vertex to Pixel

```cpp
// Original vertex in object space
glm::vec3 vertexObject = glm::vec3(0.5f, 0.5f, 0.5f);

// 1. OBJECT → WORLD (model matrix)
glm::mat4 model = glm::mat4(1.0f);
model = glm::translate(model, glm::vec3(2.0f, 1.0f, -3.0f));
model = glm::rotate(model, glm::radians(45.0f), glm::vec3(0.0f, 1.0f, 0.0f));
glm::vec4 vertexWorld = model * glm::vec4(vertexObject, 1.0f);

// 2. WORLD → VIEW (view matrix)
glm::mat4 view = glm::lookAt(
    glm::vec3(5.0f, 3.0f, 10.0f),  // Camera position
    glm::vec3(0.0f, 0.0f, 0.0f),   // Look at origin
    glm::vec3(0.0f, 1.0f, 0.0f)    // Up vector
);
glm::vec4 vertexView = view * vertexWorld;

// 3. VIEW → CLIP (projection matrix)
glm::mat4 proj = glm::perspective(
    glm::radians(45.0f), 16.0f/9.0f, 0.1f, 100.0f
);
glm::vec4 vertexClip = proj * vertexView;

// 4. CLIP → NDC (perspective divide - automatic in hardware)
glm::vec3 vertexNDC = glm::vec3(
    vertexClip.x / vertexClip.w,
    vertexClip.y / vertexClip.w,
    vertexClip.z / vertexClip.w
);

// 5. NDC → SCREEN (viewport transform - automatic)
// Assuming 1920x1080 viewport
float screenX = (vertexNDC.x + 1.0f) * 960.0f;
float screenY = (vertexNDC.y + 1.0f) * 540.0f;
```

### In Vertex Shader (All at Once)

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    // Combined transformation in one line
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    
    // This single line does all steps 1-3!
    // Steps 4-5 are automatic in hardware
}
```

---

## Part 10: Coordinate System Conventions

### OpenGL vs Other APIs

| System | OpenGL | DirectX | Vulkan |
|--------|--------|---------|--------|
| **Object Space** | Right-handed | Left-handed | Configurable |
| **World Space** | Right-handed | Left-handed | Configurable |
| **View Space** | Camera at origin, looks down -Z | Camera at origin, looks down +Z | Configurable |
| **NDC** | X: -1..1, Y: -1..1, Z: -1..1 | X: -1..1, Y: -1..1, Z: 0..1 | X: -1..1, Y: -1..1 (Y flipped), Z: 0..1 |
| **Screen Space** | Y up | Y down | Y down |

### Important: Y Direction

```cpp
// OpenGL: Bottom-left is (0,0)
glViewport(0, 0, width, height);
// (0,0) = bottom-left corner

// Many image formats and window systems: Top-left is (0,0)
// This can cause textures to appear upside-down if not handled!
```

### Depth Range

```cpp
// OpenGL default depth range
glDepthRange(0.0, 1.0);  // Near = 0, Far = 1

// Can be changed
glDepthRange(0.2, 0.8);  // Custom range (rarely needed)
```

---

## Part 11: Common Coordinate System Operations

### Converting Between Systems

```cpp
// Screen to NDC
glm::vec2 screenToNDC(float screenX, float screenY, int width, int height) {
    float ndcX = (2.0f * screenX / width) - 1.0f;
    float ndcY = 1.0f - (2.0f * screenY / height);  // Flip Y if needed
    return glm::vec2(ndcX, ndcY);
}

// NDC to Screen
glm::vec2 ndcToScreen(float ndcX, float ndcY, int width, int height) {
    float screenX = (ndcX + 1.0f) * 0.5f * width;
    float screenY = (1.0f - ndcY) * 0.5f * height;  // Flip Y if needed
    return glm::vec2(screenX, screenY);
}

// Unproject (screen to world ray) - for picking
glm::vec3 screenToWorldRay(float screenX, float screenY, 
                           glm::mat4 view, glm::mat4 proj,
                           int width, int height) {
    // Convert to NDC
    glm::vec4 rayClip(
        (2.0f * screenX / width) - 1.0f,
        1.0f - (2.0f * screenY / height),
        -1.0f,  // Near plane
        1.0f
    );
    
    // Inverse transform
    glm::mat4 inverseVP = glm::inverse(proj * view);
    glm::vec4 rayWorld = inverseVP * rayClip;
    rayWorld /= rayWorld.w;
    
    return glm::normalize(glm::vec3(rayWorld));
}
```

### Billboard Sprites (Always Face Camera)

```glsl
// Vertex shader for billboard
#version 330 core
layout (location = 0) in vec3 aPos;  // Quad corner offsets
layout (location = 1) in vec2 aTexCoord;

out vec2 vTexCoord;

uniform vec3 billboardPos;  // World position
uniform mat4 view;
uniform mat4 projection;

void main() {
    // Extract camera right and up from view matrix
    vec3 cameraRight = vec3(view[0][0], view[1][0], view[2][0]);
    vec3 cameraUp = vec3(view[0][1], view[1][1], view[2][1]);
    
    // Billboard in world space (always facing camera)
    vec3 worldPos = billboardPos + 
                    cameraRight * aPos.x + 
                    cameraUp * aPos.y;
    
    gl_Position = projection * view * vec4(worldPos, 1.0);
    vTexCoord = aTexCoord;
}
```

---

## Part 12: Debugging Coordinate Systems

### Visual Debugging Techniques

```glsl
// Visualize world positions
FragColor = vec4(vFragPos * 0.1, 1.0);  // Position as color

// Visualize normals
FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);  // Normal as color

// Visualize UV coordinates
FragColor = vec4(vTexCoord, 0.0, 1.0);  // UV as color

// Visualize screen position
FragColor = vec4(gl_FragCoord.xy / 1000.0, 0.0, 1.0);

// Visualize depth
float depth = gl_FragCoord.z;
FragColor = vec4(vec3(depth), 1.0);
```

### Common Coordinate System Mistakes

```cpp
// MISTAKE 1: Forgetting to convert degrees to radians
glm::perspective(45.0f, aspect, 0.1f, 100.0f);  // WRONG - 45 is degrees!
// glm::perspective expects radians!

// CORRECT:
glm::perspective(glm::radians(45.0f), aspect, 0.1f, 100.0f);

// MISTAKE 2: Wrong matrix multiplication order
gl_Position = vec4(aPos, 1.0) * model * view * projection;  // WRONG!
// CORRECT: projection * view * model * vec4(aPos, 1.0)

// MISTAKE 3: Not handling Y-flip for textures
// If texture appears upside-down, flip Y in shader
vTexCoord = vec2(aTexCoord.x, 1.0 - aTexCoord.y);

// MISTAKE 4: Near plane too close, far plane too far
glm::perspective(45.0f, aspect, 0.0001f, 1000000.0f);  // Depth precision issues!
// Keep reasonable ranges for good depth buffer precision
```

---

## The 30-Second Summary

- **Object Space** = Model's own coordinate system (centered at origin)
- **World Space** = Scene coordinate system (objects placed in world)
- **View Space** = Camera coordinate system (camera at origin looking down -Z)
- **Clip Space** = After projection (homogeneous coordinates for clipping)
- **NDC** = After perspective division (-1 to 1 in all axes)
- **Screen Space** = Final pixel coordinates (0 to width/height)

**Transformations:**
- Model Matrix: Object → World
- View Matrix: World → View
- Projection Matrix: View → Clip
- Perspective Division: Clip → NDC (automatic)
- Viewport Transform: NDC → Screen (automatic)

**The journey from 3D model to 2D screen passes through multiple coordinate systems, each serving a specific purpose in the rendering pipeline.**

---

**Next Step:** Ready to understand transformations and matrices in detail?