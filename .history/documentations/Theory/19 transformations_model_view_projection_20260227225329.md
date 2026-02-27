# Transformations: Model, View, Projection 

## The Film Production Analogy

Transformations can be understood through a film production process:

- **The Actor** = The 3D model (vertices in object space)
- **The Director's Instructions** = Model matrix (where actor stands, how they pose)
- **The Camera Operator** = View matrix (where camera is positioned, where it points)
- **The Lens Choice** = Projection matrix (wide-angle, telephoto, or orthographic)
- **The Final Film Frame** = Screen space (the final 2D image)

**Just as a film goes through multiple stages from actor to screen, 3D vertices undergo multiple transformations before becoming pixels.**

---

## Part 1: The Big Picture - MVP in One Sentence

### The MVP Matrix

The **MVP** (Model-View-Projection) matrix is the combined transformation that takes vertices from their original object space to the final clip space:

```glsl
// The complete transformation in one line
gl_Position = projection * view * model * vec4(aPos, 1.0);

// Read from right to left:
// 1. model      : Object → World
// 2. view       : World → View (camera)
// 3. projection : View → Clip
```

### Visual Pipeline

```
OBJECT SPACE          WORLD SPACE           VIEW SPACE            CLIP SPACE
    ●━━━━━━●            🏠    ●                ○───●                  ┌───┐
    │      │     →     🏙️  🏠  ●       →        ○    ●        →      │   │
    ●━━━━━━●            ●    🏠                 ○   ○                  └───┘
    
[Model Matrix]      [View Matrix]       [Projection Matrix]    [Perspective Divide]
    Local to           World to            3D to 2D                → NDC/Screen
    World space        Camera space        frustum
```

---

## Part 2: Model Matrix - Object to World

### What Does the Model Matrix Do?

The **model matrix** transforms vertices from **object space** (where the model was created) to **world space** (where it exists in the scene).

### Components of Model Matrix

The model matrix typically combines three operations in this order (usually):

```
MODEL = TRANSLATION × ROTATION × SCALE

Or more commonly (for hierarchical transforms):
MODEL = TRANSLATION × ROTATION × SCALE

But order matters! Different orders give different results:
```

### Translation (Moving)

```cpp
// Translation matrix moves an object
glm::mat4 translation = glm::translate(glm::mat4(1.0f), 
                                        glm::vec3(5.0f, 2.0f, -3.0f));

// Matrix form:
[ 1 0 0 5 ]
[ 0 1 0 2 ]
[ 0 0 1 -3 ]
[ 0 0 0 1  ]

// Effect: All vertices move by (5, 2, -3) in world space
```

### Rotation (Turning)

```cpp
// Rotation around Y axis (yaw)
glm::mat4 rotationY = glm::rotate(glm::mat4(1.0f), 
                                   glm::radians(45.0f), 
                                   glm::vec3(0.0f, 1.0f, 0.0f));

// Matrix form (45° around Y):
[ cos45° 0 sin45° 0 ]
[ 0      1 0      0 ]
[ -sin45°0 cos45° 0 ]
[ 0      0 0      1 ]

// Rotation around multiple axes:
glm::mat4 rotation = glm::rotate(glm::mat4(1.0f), pitch, glm::vec3(1,0,0));
rotation = glm::rotate(rotation, yaw, glm::vec3(0,1,0));
rotation = glm::rotate(rotation, roll, glm::vec3(0,0,1));
```

### Scale (Resizing)

```cpp
// Scale matrix changes size
glm::mat4 scale = glm::scale(glm::mat4(1.0f), 
                              glm::vec3(2.0f, 1.0f, 0.5f));

// Matrix form:
[ 2 0 0   0 ]
[ 0 1 0   0 ]
[ 0 0 0.5 0 ]
[ 0 0 0   1 ]

// Uniform scaling (same in all axes):
glm::mat4 uniformScale = glm::scale(glm::mat4(1.0f), 
                                     glm::vec3(2.0f));
```

### Complete Model Matrix Example

```cpp
// Building a model matrix step by step
glm::mat4 model = glm::mat4(1.0f);  // Start with identity

// 1. Scale first (local size)
model = glm::scale(model, glm::vec3(2.0f, 1.0f, 2.0f));

// 2. Then rotate (orientation)
model = glm::rotate(model, glm::radians(45.0f), glm::vec3(0.0f, 1.0f, 0.0f));

// 3. Finally translate (position)
model = glm::translate(model, glm::vec3(10.0f, 5.0f, -20.0f));

// Order matters! Try different orders to see the difference
```

### Why Order Matters

```
SCALE → ROTATE → TRANSLATE (Common for objects):
1. Scale the object at origin
2. Rotate the scaled object
3. Move to final position
Result: Object scales, then rotates, then moves - good for most objects

TRANSLATE → ROTATE → SCALE (Different effect):
1. Move object away from origin
2. Rotate around origin (orbits!)
3. Scale the result
Result: Object orbits origin while scaling - good for planetary systems
```

---

## Part 3: View Matrix - World to Camera

### What Does the View Matrix Do?

The **view matrix** transforms vertices from **world space** to **view space** (also called camera space or eye space), where the camera is at the origin looking down the negative Z axis.

### Camera Positioning

```cpp
// Option 1: LookAt function (easiest)
glm::mat4 view = glm::lookAt(
    glm::vec3(5.0f, 3.0f, 10.0f),  // Camera position in world
    glm::vec3(0.0f, 0.0f, 0.0f),   // Point camera looks at
    glm::vec3(0.0f, 1.0f, 0.0f)    // Up direction (usually Y)
);

// Option 2: Manual construction (understanding what happens)
glm::mat4 view = glm::mat4(1.0f);

// First, move world opposite to camera position
view = glm::translate(view, -cameraPosition);

// Then, rotate world opposite to camera orientation
view = glm::rotate(view, -cameraPitch, glm::vec3(1,0,0));
view = glm::rotate(view, -cameraYaw, glm::vec3(0,1,0));
```

### Visualizing View Transformation

```
WORLD SPACE:                    VIEW SPACE:
    Y↑                            Y↑
     |                              |
     |    ● Object                  |    ● Object
     |  ↗                           |  ↗
     |📍 Camera                     |📍 Camera (now at origin)
     |                              |    Looks down -Z
     └──────→ X                     └──────→ X
    /                               /
   /                               /
  Z                               Z

The view matrix effectively moves the entire world
so that camera is at origin looking down -Z.
```

### First-Person Camera

```cpp
class FirstPersonCamera {
    glm::vec3 position;
    float yaw, pitch;  // Rotation angles
    
public:
    glm::mat4 getViewMatrix() {
        // Calculate direction vectors
        glm::vec3 front;
        front.x = cos(glm::radians(yaw)) * cos(glm::radians(pitch));
        front.y = sin(glm::radians(pitch));
        front.z = sin(glm::radians(yaw)) * cos(glm::radians(pitch));
        front = glm::normalize(front);
        
        glm::vec3 right = glm::normalize(glm::cross(front, glm::vec3(0,1,0)));
        glm::vec3 up = glm::normalize(glm::cross(right, front));
        
        // Construct view matrix directly
        glm::mat4 view(1.0f);
        view[0][0] = right.x;   view[1][0] = right.y;   view[2][0] = right.z;
        view[0][1] = up.x;      view[1][1] = up.y;      view[2][1] = up.z;
        view[0][2] = -front.x;  view[1][2] = -front.y;  view[2][2] = -front.z;
        view[3][0] = -glm::dot(right, position);
        view[3][1] = -glm::dot(up, position);
        view[3][2] = glm::dot(front, position);
        
        return view;
    }
};
```

---

## Part 4: Projection Matrix - 3D to 2D

### What Does the Projection Matrix Do?

The **projection matrix** transforms vertices from **view space** to **clip space**. It defines the visible region (frustum) and how 3D scenes project onto a 2D surface.

### Two Types of Projection

| Type | Use Case | Characteristics |
|------|----------|-----------------|
| **Perspective** | 3D games, realistic rendering | Objects farther = smaller |
| **Orthographic** | UI, 2D games, CAD | Size independent of distance |

### Perspective Projection

```cpp
// Perspective projection matrix
glm::mat4 proj = glm::perspective(
    glm::radians(45.0f),     // Field of view (vertical)
    (float)width / height,   // Aspect ratio
    0.1f,                    // Near plane distance
    100.0f                   // Far plane distance
);

// Visual effect:
// - Objects at near plane appear normal size
// - Objects at far plane are tiny
// - Creates sense of depth
```

### Perspective Frustum

```
VIEW SPACE:                     CLIP SPACE:
    Y↑                            Y↑
     |  /────────┐                 |  ┌──────┐
     | /         │                 |  │      │
     |/          │                 |  │      │
     ○───────→ X  Far plane        |  │      │
    /|          │                  |  │      │
   / |          │                  |  └──────┘
  Z  └──────────┘                  └──────────→ X
     Near plane

The frustum (truncated pyramid) becomes a cube (-1 to 1)
```

### Orthographic Projection

```cpp
// Orthographic projection matrix
glm::mat4 proj = glm::ortho(
    -10.0f, 10.0f,   // Left, right
    -10.0f, 10.0f,   // Bottom, top
    0.1f, 100.0f     // Near, far
);

// Or for 2D rendering with pixel-perfect coordinates:
glm::mat4 proj = glm::ortho(
    0.0f, (float)width,    // Left, right
    0.0f, (float)height,   // Bottom, top
    -1.0f, 1.0f            // Near, far
);

// Orthographic frustum is a rectangular box, not a pyramid
```

### Comparison: Perspective vs Orthographic

```
PERSPECTIVE:                    ORTHOGRAPHIC:
    ██████                          ██████
       ██████                     ██████
          ██████                ██████
             ██████            ██████
             
Railroad tracks converge    Railroad tracks remain parallel
Realistic view               Technical/2D view
```

---

## Part 5: The Complete MVP Pipeline

### Step-by-Step Transformation

```cpp
// Original vertex in object space
glm::vec4 objectPos(1.0f, 2.0f, 3.0f, 1.0f);

// 1. MODEL TRANSFORM (Object → World)
glm::mat4 model = glm::mat4(1.0f);
model = glm::translate(model, glm::vec3(5.0f, 0.0f, -10.0f));
model = glm::rotate(model, glm::radians(45.0f), glm::vec3(0.0f, 1.0f, 0.0f));
model = glm::scale(model, glm::vec3(2.0f));

glm::vec4 worldPos = model * objectPos;
// worldPos now in world space

// 2. VIEW TRANSFORM (World → View)
glm::mat4 view = glm::lookAt(
    glm::vec3(5.0f, 3.0f, 10.0f),
    glm::vec3(0.0f, 0.0f, 0.0f),
    glm::vec3(0.0f, 1.0f, 0.0f)
);

glm::vec4 viewPos = view * worldPos;
// viewPos now in camera space (camera at origin)

// 3. PROJECTION TRANSFORM (View → Clip)
glm::mat4 proj = glm::perspective(
    glm::radians(45.0f),
    16.0f/9.0f,
    0.1f,
    100.0f
);

glm::vec4 clipPos = proj * viewPos;
// clipPos now in homogeneous clip space

// 4. PERSPECTIVE DIVIDE (Clip → NDC) - automatic in hardware
glm::vec3 ndc = glm::vec3(
    clipPos.x / clipPos.w,
    clipPos.y / clipPos.w,
    clipPos.z / clipPos.w
);

// 5. VIEWPORT TRANSFORM (NDC → Screen) - automatic
// screenX = (ndc.x + 1) * width/2 + viewportX
// screenY = (ndc.y + 1) * height/2 + viewportY
```

### In Vertex Shader (All at Once)

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 vNormal;
out vec2 vTexCoord;
out vec3 vFragPos;  // World space position for lighting

void main() {
    // World space position (for lighting)
    vec4 worldPos = model * vec4(aPos, 1.0);
    vFragPos = worldPos.xyz;
    
    // Transform normal to world space
    vNormal = mat3(transpose(inverse(model))) * aNormal;
    
    // Pass texture coordinate
    vTexCoord = aTexCoord;
    
    // Final clip space position
    gl_Position = projection * view * worldPos;
    // Equivalent to: projection * view * model * vec4(aPos, 1.0)
}
```

---

## Part 6: Matrix Math Deep Dive

### Homogeneous Coordinates

The 4th component (w) is crucial for transformations:

```glsl
vec4 position = vec4(x, y, z, 1.0);   // A point in space
vec4 direction = vec4(x, y, z, 0.0);  // A direction vector

// Why? Translation affects points but not directions:
mat4 translation = translate(5,0,0);
translation * point;      // Adds (5,0,0) - correct
translation * direction;  // Direction unchanged - correct!
```

### Matrix Multiplication Order

```glsl
// CORRECT ORDER (right to left):
gl_Position = projection * view * model * vec4(aPos, 1.0);
// 1. model: object → world
// 2. view: world → camera
// 3. projection: camera → clip

// WRONG ORDER:
gl_Position = model * view * projection * vec4(aPos, 1.0);
// This applies transformations in wrong order - geometry will be wrong!
```

### Why Order Matters Visually

```
Apply translate then rotate:
    ●━━━●          ●━━━●
    │   │    →     │   │    →   ╱    (rotated around origin)
    ●━━━●          ●━━━●      ╱

Apply rotate then translate:
    ●━━━●           ╲          ●━━━●
    │   │    →       ╲    →    │   │    (rotated then moved)
    ●━━━●             ╲         ●━━━●
```

---

## Part 7: Common Transformation Scenarios

### Scenario 1: Orbiting Camera

```cpp
// Camera orbits around object at radius R
float time = glfwGetTime();
float radius = 10.0f;
float camX = sin(time) * radius;
float camZ = cos(time) * radius;

glm::mat4 view = glm::lookAt(
    glm::vec3(camX, 3.0f, camZ),  // Camera orbits
    glm::vec3(0.0f, 0.0f, 0.0f),  // Looking at center
    glm::vec3(0.0f, 1.0f, 0.0f)
);
```

### Scenario 2: Hierarchical Transformations (Robot Arm)

```cpp
// Robot arm with shoulder, elbow, wrist
glm::mat4 model = glm::mat4(1.0f);

// Base transform
model = glm::translate(model, basePos);
model = glm::rotate(model, baseRot, glm::vec3(0,1,0));

// Shoulder (relative to base)
glm::mat4 shoulder = model;
shoulder = glm::translate(shoulder, shoulderOffset);
shoulder = glm::rotate(shoulder, shoulderAngle, glm::vec3(0,0,1));

// Elbow (relative to shoulder)
glm::mat4 elbow = shoulder;
elbow = glm::translate(elbow, elbowOffset);
elbow = glm::rotate(elbow, elbowAngle, glm::vec3(0,0,1));

// Wrist (relative to elbow)
glm::mat4 wrist = elbow;
wrist = glm::translate(wrist, wristOffset);
wrist = glm::rotate(wrist, wristAngle, glm::vec3(0,0,1));

// Render each part with its own model matrix
renderShoulder(shoulder);
renderElbow(elbow);
renderWrist(wrist);
```

### Scenario 3: Billboarding (Always Face Camera)

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

## Part 8: Performance and Optimization

### Precomputing MVP

```cpp
// For static objects, precompute MVP on CPU
glm::mat4 mvp = projection * view * model;

// Upload once per frame/object
glUniformMatrix4fv(mvpLoc, 1, GL_FALSE, glm::value_ptr(mvp));

// Simpler shader:
#version 330 core
layout (location = 0) in vec3 aPos;
uniform mat4 mvp;

void main() {
    gl_Position = mvp * vec4(aPos, 1.0);
}
```

### Matrix Palettes for Instancing

```cpp
// For many similar objects (instancing)
struct InstanceData {
    glm::mat4 model;
    glm::vec4 color;
};

// Upload array of instance data
glBindBuffer(GL_ARRAY_BUFFER, instanceVBO);
glBufferData(GL_ARRAY_BUFFER, instanceCount * sizeof(InstanceData), 
             instances, GL_STATIC_DRAW);

// Set up instanced attributes
for (int i = 0; i < 4; i++) {
    glVertexAttribPointer(3 + i, 4, GL_FLOAT, GL_FALSE,
                          sizeof(InstanceData),
                          (void*)(offsetof(InstanceData, model) + i * sizeof(glm::vec4)));
    glVertexAttribDivisor(3 + i, 1);  // Advance per instance
    glEnableVertexAttribArray(3 + i);
}

// Draw all instances
glDrawArraysInstanced(GL_TRIANGLES, 0, vertexCount, instanceCount);
```

### Matrix Decomposition

```cpp
// Extract components from model matrix (for physics, etc.)
glm::vec3 scale;
glm::quat rotation;
glm::vec3 translation;
glm::vec3 skew;
glm::vec4 perspective;

glm::decompose(model, scale, rotation, translation, skew, perspective);

// Now use components
glm::vec3 position = translation;
float uniformScale = (scale.x + scale.y + scale.z) / 3.0f;
```

---

## Part 9: Debugging Transformations

### Visual Debugging

```glsl
// Visualize world positions
FragColor = vec4(vFragPos * 0.1, 1.0);

// Visualize normals
FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);

// Visualize depth (distance from camera)
float depth = gl_FragCoord.z;
FragColor = vec4(vec3(depth), 1.0);

// Visualize which side of object
if (gl_FrontFacing) {
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Front red
} else {
    FragColor = vec4(0.0, 0.0, 1.0, 1.0);  // Back blue
}
```

### Common Transformation Mistakes

```cpp
// MISTAKE 1: Wrong matrix multiplication order
gl_Position = vec4(aPos, 1.0) * model * view * projection;  // WRONG!
// CORRECT: projection * view * model * vec4(aPos, 1.0)

// MISTAKE 2: Forgetting to convert degrees to radians
glm::perspective(45.0f, aspect, 0.1f, 100.0f);  // WRONG - 45 is degrees!
// CORRECT: glm::perspective(glm::radians(45.0f), aspect, 0.1f, 100.0f);

// MISTAKE 3: Near plane too close
glm::perspective(45.0f, aspect, 0.0001f, 1000000.0f);  // Depth precision issues!
// Keep reasonable ranges for good depth buffer precision

// MISTAKE 4: Not handling aspect ratio
// If screen resizes, update projection matrix!

// MISTAKE 5: Scaling normals like positions
vNormal = mat3(model) * aNormal;  // WRONG for non-uniform scale!
// CORRECT: vNormal = mat3(transpose(inverse(model))) * aNormal;
```

### Debugging Matrix Values

```cpp
// Print matrix for debugging
void printMat4(const glm::mat4& m) {
    for (int row = 0; row < 4; row++) {
        for (int col = 0; col < 4; col++) {
            std::cout << m[col][row] << " ";  // Note: column-major!
        }
        std::cout << std::endl;
    }
}

// Check if matrix is valid (not NaN, not infinite)
if (glm::any(glm::isnan(m)) || glm::any(glm::isinf(m))) {
    std::cout << "Invalid matrix detected!" << std::endl;
}
```

---

## The 30-Second Summary

- **Model Matrix** = Object → World (position, rotation, scale)
- **View Matrix** = World → Camera (where camera is and looks)
- **Projection Matrix** = Camera → Clip (frustum, perspective/orthographic)
- **MVP** = projection × view × model (combined transformation)
- **Order Matters** = Read right to left: model first, then view, then projection
- **Homogeneous Coordinates** = w=1 for points, w=0 for directions
- **Perspective** = Objects farther appear smaller (realistic)
- **Orthographic** = Size independent of distance (technical/2D)

**Transformations are the mathematical machinery that places 3D objects in a scene, positions the camera, and projects the result onto a 2D screen - they're the foundation of all 3D graphics.**

---

