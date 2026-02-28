# Perspective vs Orthographic Projection - Beginner's Documentation

## The Artist vs Architect Analogy

Perspective and orthographic projection can be understood through two different ways of drawing a scene:

- **The Renaissance Artist** = Perspective projection - Draws railroad tracks converging in the distance, objects getting smaller as they recede
- **The Architect** = Orthographic projection - Draws blueprints where parallel lines remain parallel, objects stay the same size regardless of distance

**Both are "correct" ways to project 3D onto 2D - they just serve different purposes.**

---

## Part 1: What is Projection?

### Definition

**Projection** is the process of transforming 3D coordinates onto a 2D plane. In graphics, this means converting view space coordinates to clip space coordinates.

### The Two Families of Projection

```
3D VIEW SPACE                   2D SCREEN
    ┌──┐                           ┌──┐
    │  │                           │  │
    │  │   → [PROJECTION] →        │  │
    │  │                           │  │
    └──┘                           └──┘
   (x,y,z)                        (x,y)

Two ways to do this:
├─ PERSPECTIVE: Objects farther = smaller (realistic)
└─ ORTHOGRAPHIC: Size independent of distance (technical)
```

### Visual Comparison

```
PERSPECTIVE PROJECTION:           ORTHOGRAPHIC PROJECTION:
    ██████                            ██████
       ██████                       ██████
          ██████                  ██████
             ██████              ██████
             
Railroad tracks converge      Railroad tracks remain parallel
Distant objects smaller        Same size regardless of distance
Natural human vision           Engineering/technical drawings
Games, simulations             2D games, UI, CAD
```

---

## Part 2: Perspective Projection - The Human Eye

### How Perspective Works

Perspective projection mimics how human vision works: objects appear smaller as they get farther away.

```
VIEW FROM THE SIDE:
    Y
    ↑
    │  ● (near object - appears large)
    │
    │     ● (far object - appears small)
    │
    └────────────→ Z
   Camera
   at (0,0)

The same physical height projects to different screen heights
based on distance from camera.
```

### The Perspective Formula

The basic idea behind perspective:

```cpp
// Objects farther away get scaled by 1/distance
screenX = (worldX / worldZ) * scale;
screenY = (worldY / worldZ) * scale;

// This division by Z creates the perspective effect
// Objects with larger Z (farther) become smaller
```

### Perspective Projection Matrix

```cpp
// Creating perspective matrix in code
glm::mat4 projection = glm::perspective(
    glm::radians(45.0f),   // Field of view (vertical angle)
    (float)width / height, // Aspect ratio
    0.1f,                  // Near plane distance
    100.0f                 // Far plane distance
);

// Matrix form (simplified):
[ 1/(aspect*tan(fov/2))         0                0                 0      ]
[         0               1/tan(fov/2)           0                 0      ]
[         0                     0        -(far+near)/(far-near)  -1      ]
[         0                     0        -(2*far*near)/(far-near) 0      ]

// Note: The -1 in the third row, fourth column is what creates perspective
// It puts the Z value into the W component
```

### Visualizing the Frustum

```
PERSPECTIVE FRUSTUM (view from side):
    Y
    ↑
    │    /────────┐
    │   /         │  Far plane (farthest visible)
    │  /          │
    │ /           │
    │/            │
    ○───────→ Z   │
   Camera        /
    │ Near plane /
    │    └──────┘
    
The frustum is a truncated pyramid:
- Near plane: Where rendering starts
- Far plane: Where rendering ends
- Everything inside gets rendered
- Everything outside gets clipped
```

### Field of View (FOV)

```cpp
// Field of view determines how much of the scene is visible
glm::perspective(glm::radians(90.0f), aspect, 0.1f, 100.0f);  // Wide angle (fish-eye)
glm::perspective(glm::radians(45.0f), aspect, 0.1f, 100.0f);  // Normal view
glm::perspective(glm::radians(20.0f), aspect, 0.1f, 100.0f);  // Telephoto (zoomed)

// Visual effect:
// 90°: See a lot, but objects appear smaller, possible distortion
// 45°: Natural view, similar to human vision
// 20°: Zoomed in, objects appear larger, compressed depth
```

### Aspect Ratio

```cpp
// Aspect ratio = width / height
float aspect = 1280.0f / 720.0f;  // 16:9 widescreen

// Wrong aspect ratio causes stretching:
glm::perspective(45.0f, 4.0f/3.0f, 0.1f, 100.0f);  // 4:3 aspect on 16:9 screen
// Result: Circles become ovals, everything looks squashed horizontally

// Always update projection when window resizes:
void windowResize(int width, int height) {
    float aspect = (float)width / (float)height;
    projection = glm::perspective(glm::radians(45.0f), aspect, 0.1f, 100.0f);
    glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm::value_ptr(projection));
}
```

---

## Part 3: Orthographic Projection - The Blueprint

### How Orthographic Works

Orthographic projection ignores distance - objects stay the same size regardless of how far away they are.

```
VIEW FROM THE SIDE:
    Y
    ↑
    │  ● (near object)
    │  │
    │  ● (far object - same size!)
    │  │
    └────────────→ Z
   Camera
   at (0,0)

The projection lines are parallel, not converging.
Size is determined only by actual dimensions, not distance.
```

### The Orthographic Formula

```cpp
// Orthographic is simple - no division by Z
screenX = worldX * scale;
screenY = worldY * scale;

// Z is used only for depth testing, not for size
```

### Orthographic Projection Matrix

```cpp
// Creating orthographic matrix
glm::mat4 projection = glm::ortho(
    -10.0f, 10.0f,   // Left, right (X range)
    -10.0f, 10.0f,   // Bottom, top (Y range)
    0.1f, 100.0f     // Near, far (Z range)
);

// For 2D rendering (pixel-perfect coordinates):
glm::mat4 projection = glm::ortho(
    0.0f, (float)screenWidth,   // Left, right (0 to width)
    (float)screenHeight, 0.0f,  // Bottom, top (height to 0 - Y flipped!)
    -1.0f, 1.0f                  // Near, far
);

// Matrix form:
[ 2/(right-left)       0               0          -(right+left)/(right-left) ]
[       0         2/(top-bottom)        0          -(top+bottom)/(top-bottom) ]
[       0               0         -2/(far-near)    -(far+near)/(far-near)    ]
[       0               0               0                     1              ]
```

### Visualizing the Orthographic Volume

```
ORTHOGRAPHIC VIEW VOLUME (a box):
    Y
    ↑
    │  ┌──────────────┐
    │  │              │  Far plane
    │  │              │
    │  │              │
    │  │              │
    │  │              │
    │  └──────────────┘
    │  Near plane
    │
    └──────────────→ Z
    
The view volume is a rectangular box, not a pyramid.
Everything inside the box gets rendered orthographically.
```

---

## Part 4: Side-by-Side Comparison

### Key Differences

| Aspect | Perspective | Orthographic |
|--------|-------------|--------------|
| **Size with Distance** | Smaller as distance increases | Constant regardless of distance |
| **Parallel Lines** | Appear to converge | Remain parallel |
| **View Volume** | Frustum (truncated pyramid) | Rectangular box |
| **Division by Z** | Yes (creates perspective) | No |
| **W Component** | Contains Z distance | Usually 1 |
| **Depth Distribution** | Non-linear (more precision near camera) | Linear |
| **Realism** | Matches human vision | Technical/abstract |

### Visual Comparison Table

```
Same scene rendered both ways:

PERSPECTIVE:                     ORTHOGRAPHIC:
    ┌────┐                           ┌────┐
    │    │  ┌──┐                     │    │  ┌──┐
    │    │  │  │                     │    │  │  │
    │    │  │  │                     │    │  │  │
    └────┘  └──┘                     └────┘  └──┘
    
Far box smaller than near box    Both boxes same size
Tracks appear to meet            Tracks stay parallel
Natural looking                  "Blueprint" look
```

### Code Comparison

```cpp
// PERSPECTIVE - for 3D games
glm::mat4 perspectiveProj = glm::perspective(
    glm::radians(45.0f),     // FOV - wider = see more
    (float)width / height,   // Aspect ratio
    0.1f,                    // Near plane (as far as possible!)
    1000.0f                  // Far plane (as close as possible!)
);

// ORTHOGRAPHIC - for 2D games, UI
glm::mat4 orthoProj = glm::ortho(
    0.0f, (float)width,      // Left, right - match screen
    (float)height, 0.0f,     // Bottom, top - Y flipped for screen coords
    -1.0f, 1.0f              // Near, far - minimal range for depth
);
```

---

## Part 5: Depth and Z Fighting

### How Depth is Stored

```cpp
// PERSPECTIVE: Non-linear depth
// More precision near camera, less at distance
Z_view      Z_buffer (0 to 1)
-0.1    →   0.999 (lots of precision)
-1.0    →   0.5
-10.0   →   0.1
-100.0  →   0.02 (very little precision)

// ORTHOGRAPHIC: Linear depth
Z_view      Z_buffer (0 to 1)
-0.1    →   0.09
-1.0    →   0.5
-10.0   →   0.9
-100.0  →   0.99 (equal precision everywhere)
```

### Z-Fighting (Depth Fighting)

**Z-fighting** occurs when two surfaces are too close together in depth:

```
PERSPECTIVE Z-FIGHTING:
Near objects: Fine (lots of precision)
Far objects:  Prone to fighting (low precision)

Example: Two planes at Z = -99.9 and Z = -100.0
In perspective Z-buffer, these might map to the same value!
Result: Flickering, surfaces fighting.

ORTHOGRAPHIC Z-FIGHTING:
Equal precision everywhere, but still can happen
with extremely close surfaces.

Solution: Keep near/far planes as tight as possible!
```

### Choosing Near and Far Planes

```cpp
// BAD: Too much range kills depth precision
glm::perspective(45.0f, aspect, 0.0001f, 1000000.0f);
// Don't do this! Wastes precision on empty space

// GOOD: Tight ranges preserve precision
glm::perspective(45.0f, aspect, 0.1f, 100.0f);  // For indoor scene
glm::perspective(45.0f, aspect, 1.0f, 10000.0f); // For outdoor scene

// Rule: Near as far as possible, far as close as possible
```

---

## Part 6: Use Cases and Applications

### When to Use Perspective

| Application | Why Perspective |
|-------------|-----------------|
| **3D Games** | Realistic, immersive experience |
| **Flight Simulators** | Distance perception important |
| **Architectural Walkthroughs** | See how spaces feel |
| **VR/AR** | Must match human vision |
| **Cinematics** | Dramatic effect, depth cues |

### When to Use Orthographic

| Application | Why Orthographic |
|-------------|------------------|
| **2D Games** | Pixel-perfect rendering, no distortion |
| **User Interfaces** | Buttons stay same size regardless of "depth" |
| **CAD/CAM** | Accurate measurements, parallel lines |
| **Strategy Games** | Clear view of game area, no perspective distortion |
| **Blueprints/Diagrams** | True dimensions, parallel lines |
| **Minimaps** | Clear overhead view |

### Hybrid Approaches

Many games use both:

```cpp
// 3D world - perspective
worldProj = glm::perspective(45.0f, aspect, 0.1f, 1000.0f);

// UI overlay - orthographic
uiProj = glm::ortho(0.0f, screenWidth, screenHeight, 0.0f, -1.0f, 1.0f);

// Render order:
// 1. Render 3D scene with perspective
// 2. Render UI with orthographic (on top)
```

---

## Part 7: Mathematical Deep Dive

### Perspective Matrix Derivation

```cpp
// The perspective matrix does two things:
// 1. Scales X and Y based on FOV and aspect
// 2. Puts Z into W to create perspective divide

// Key insight: After matrix multiplication:
x_clip = (x_view * scaleX) / -z_view  // Division happens later!
y_clip = (y_view * scaleY) / -z_view
z_clip = (A * z_view + B) / -z_view

// The division by -z_view is what creates perspective
// This is why we need homogeneous coordinates (w)
```

### The W Component's Role

```cpp
// In perspective, w contains distance
gl_Position = projection * view * model * vec4(aPos, 1.0);
// After this:
// gl_Position.w = -z_view (distance from camera)

// Later, OpenGL does perspective divide:
ndc.x = gl_Position.x / gl_Position.w;
ndc.y = gl_Position.y / gl_Position.w;
ndc.z = gl_Position.z / gl_Position.w;

// This division creates the perspective effect!
```

### Orthographic Simplicity

```cpp
// Orthographic matrix keeps w = 1
gl_Position = projection * view * model * vec4(aPos, 1.0);
// After this:
// gl_Position.w = 1 (usually)

// Perspective divide does nothing:
ndc = gl_Position;  // w=1, so division changes nothing

// This is why orthographic has no distance scaling
```

---

## Part 8: Implementing Both in Code

### Complete Example: Switching Projections

```cpp
class Camera {
    glm::mat4 projection;
    glm::mat4 view;
    bool perspectiveMode;
    float fov = 45.0f;
    float orthoSize = 10.0f;
    float nearPlane = 0.1f;
    float farPlane = 100.0f;
    int width, height;
    
public:
    void setProjectionMode(bool perspective) {
        perspectiveMode = perspective;
        updateProjection();
    }
    
    void updateProjection() {
        float aspect = (float)width / (float)height;
        
        if (perspectiveMode) {
            projection = glm::perspective(
                glm::radians(fov), aspect, nearPlane, farPlane
            );
        } else {
            float halfHeight = orthoSize;
            float halfWidth = orthoSize * aspect;
            
            projection = glm::ortho(
                -halfWidth, halfWidth,
                -halfHeight, halfHeight,
                nearPlane, farPlane
            );
        }
    }
    
    void resize(int w, int h) {
        width = w;
        height = h;
        updateProjection();
    }
    
    // Toggle with key press
    void toggleProjection() {
        perspectiveMode = !perspectiveMode;
        updateProjection();
        std::cout << "Switched to " 
                  << (perspectiveMode ? "perspective" : "orthographic") 
                  << std::endl;
    }
};
```

### Vertex Shader (Same for Both!)

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 vTexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    // The projection matrix handles both types!
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    vTexCoord = aTexCoord;
}
```

### Fragment Shader Visualization

```glsl
// Visualize which projection is being used
#version 330 core
in vec2 vTexCoord;
out vec4 FragColor;

uniform bool perspectiveMode;

void main() {
    if (perspectiveMode) {
        // Perspective: warm colors
        FragColor = vec4(vTexCoord.x, vTexCoord.y, 1.0, 1.0);
    } else {
        // Orthographic: cool colors
        FragColor = vec4(0.5 + vTexCoord.x * 0.5, 
                         0.5 + vTexCoord.y * 0.5, 
                         1.0, 1.0);
    }
}
```

---

## Part 9: Common Effects and Techniques

### 1. Orthographic Fake Perspective (Mode 7 Effect)

```cpp
// Old racing games used this trick
// Orthographic ground with perspective scaling
float scale = 1.0f / (row + 1.0f);  // Further rows smaller
float screenX = baseX * scale;
float screenY = baseY + row * spacing;
```

### 2. Mixing Projections (Split Screen)

```cpp
// Left half of screen: perspective (3D view)
glViewport(0, 0, width/2, height);
perspectiveProj = glm::perspective(45.0f, (width/2.0f)/height, 0.1f, 100.0f);
render3DScene();

// Right half of screen: orthographic (map view)
glViewport(width/2, 0, width/2, height);
orthoProj = glm::ortho(-mapSize, mapSize, -mapSize, mapSize, 0.1f, 100.0f);
render2DMap();
```

### 3. Isometric Projection (Orthographic + Rotation)

```cpp
// Isometric games use orthographic with fixed rotation
glm::mat4 view = glm::lookAt(
    glm::vec3(10.0f, 10.0f, 10.0f),  // Isometric angle
    glm::vec3(0.0f, 0.0f, 0.0f),
    glm::vec3(0.0f, 1.0f, 0.0f)
);

glm::mat4 projection = glm::ortho(-10.0f, 10.0f, -10.0f, 10.0f, 0.1f, 100.0f);
// Result: 3D-looking game with no perspective distortion
```

---

## Part 10: Debugging Projection Issues

### Common Problems

```cpp
// PROBLEM: Objects stretch when window resizes
// FIX: Update aspect ratio
void resize(int w, int h) {
    float aspect = (float)w / (float)h;
    projection = glm::perspective(glm::radians(45.0f), aspect, 0.1f, 100.0f);
}

// PROBLEM: Objects disappear when too close/far
// FIX: Adjust near/far planes
if (camera gets too close to objects) {
    nearPlane = 0.01f;  // Smaller near plane
}

// PROBLEM: Z-fighting (flickering)
// FIX: Tighten near/far range
float minDist = getClosestObjectDistance();
float maxDist = getFarthestObjectDistance();
nearPlane = minDist * 0.5f;  // Some margin
farPlane = maxDist * 1.5f;

// PROBLEM: Perspective looks distorted
// FIX: Check FOV - 45° is natural, 90° is fisheye
// FOV should match screen distance and size
```

### Visual Debugging

```glsl
// Visualize depth to debug near/far issues
void main() {
    // gl_FragCoord.z is 0 (near) to 1 (far)
    float depth = gl_FragCoord.z;
    
    // Red near, blue far
    FragColor = vec4(depth, 0.0, 1.0 - depth, 1.0);
    
    // If everything is one color, near/far planes wrong
    // If near objects are blue, swap near/far?
}
```

### Projection Matrix Inspection

```cpp
void debugProjection(const glm::mat4& proj) {
    std::cout << "Projection matrix:" << std::endl;
    for (int row = 0; row < 4; row++) {
        for (int col = 0; col < 4; col++) {
            std::cout << proj[col][row] << " ";
        }
        std::cout << std::endl;
    }
    
    // Check if perspective (look at last row)
    if (proj[3][2] != 0.0f) {
        std::cout << "This is a perspective matrix" << std::endl;
    } else {
        std::cout << "This is an orthographic matrix" << std::endl;
    }
}
```

---

## The 30-Second Summary

- **Perspective Projection** = Objects farther = smaller (realistic, 3D games)
- **Orthographic Projection** = Size independent of distance (technical, 2D games, UI)
- **Frustum** = Perspective view volume (truncated pyramid)
- **Ortho Volume** = Orthographic view volume (rectangular box)
- **FOV** = Field of view (how much you see, 45° is natural)
- **Aspect Ratio** = Width/height (prevents stretching)
- **Near/Far Planes** = Clipping boundaries (keep tight for precision)
- **Z-Fighting** = Occurs when depth precision insufficient
- **W Component** = In perspective, stores distance for division

**Choose perspective when you want realism and depth cues. Choose orthographic when you need accurate measurements or consistent sizing. Many applications use both for different purposes.**

---

**Next Step:** Ready to understand how lighting and materials work?