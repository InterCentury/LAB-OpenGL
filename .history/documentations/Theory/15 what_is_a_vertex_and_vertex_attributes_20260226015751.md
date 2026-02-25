# What is a Vertex and Vertex Attributes? 

## The Building Block Analogy

A vertex can be understood through construction building blocks:

- **The Vertex** = A single building block with specific properties
- **Position** = Where the block sits in space (x, y, z coordinates)
- **Color** = What color the block is painted
- **Normal** = Which direction each face of the block points
- **UV Coordinates** = Where to place wallpaper on the block
- **The Mesh** = A structure built from many blocks connected together

**Just as a building has many blocks with different properties, a 3D model has many vertices, each carrying specific data that defines how it contributes to the final shape and appearance.**

---

## Part 1: What is a Vertex?

### Definition

A **vertex** (plural: **vertices**) is a point in 3D space that serves as a fundamental building block for geometric shapes. Vertices are connected to form edges, faces, and ultimately complete 3D models.

### Core Characteristics

| Aspect | Description |
|--------|-------------|
| **Analogy** | A corner point where surfaces meet |
| **Dimension** | Point in 3D space (x, y, z coordinates) |
| **Role** | Building block of all 3D geometry |
| **Data Container** | Holds multiple attributes beyond position |
| **GPU Processing** | Processed individually by vertex shaders |

### Visual Representation

```
A SINGLE VERTEX:
    ● (x, y, z)
    |
    |── Position: Where in space
    |── Color: What color at this point
    |── Normal: Which direction surface faces
    └── UV: Where on texture this maps to

TWO VERTICES FORM A LINE:
    ●─────────●

THREE VERTICES FORM A TRIANGLE:●
    | \
    |  \
    ●───●

MANY VERTICES FORM COMPLEX SHAPES:
    ●────●────●
    | \  | \  |
    |  \ |  \ |
    ●────●────●
    | \  | \  |
    |  \ |  \ |
    ●────●────●
```

---

## Part 2: Vertex Position - The Minimum Requirement

### Position Data

At minimum, a vertex must have a position in 3D space.

```cpp
// Simplest vertex - position only
float vertices[] = {
    // x     y     z
     0.5f,  0.5f, 0.0f,  // Vertex 0 (top right)
     0.5f, -0.5f, 0.0f,  // Vertex 1 (bottom right)
    -0.5f, -0.5f, 0.0f,  // Vertex 2 (bottom left)
    -0.5f,  0.5f, 0.0f   // Vertex 3 (top left)
};
```

### Coordinate Systems

```cpp
// Positions can be in different coordinate systems:
// 1. Object/Local space - relative to model origin
float localSpace[] = {
    -0.5f, -0.5f, 0.0f,  // Bottom left of model
     0.5f, -0.5f, 0.0f,  // Bottom right of model
     0.0f,  0.5f, 0.0f   // Top center of model
};

// 2. World space - absolute positions in scene
float worldSpace[] = {
    10.0f, 0.0f, 20.0f,  // Position 1 in world
    12.0f, 0.0f, 22.0f,  // Position 2 in world
    11.0f, 2.0f, 21.0f   // Position 3 in world
};
```

### Homogeneous Coordinates

In shaders, positions are typically treated as 4D homogeneous coordinates:

```glsl
// In vertex shader
vec4 position = vec4(aPos, 1.0);  // w=1 for points
// The w component enables perspective transformations
```

---

## Part 3: Vertex Attributes - What Vertices Can Carry

### Common Vertex Attributes

| Attribute | GLSL Type | Typical Location | Purpose |
|-----------|-----------|------------------|---------|
| **Position** | `vec3` | 0 | Where vertex is in space |
| **Normal** | `vec3` | 1 | Surface direction for lighting |
| **Color** | `vec3` or `vec4` | 2 | Per-vertex color |
| **Texture Coordinate (UV)** | `vec2` | 3 | Where on texture this maps to |
| **Tangent** | `vec3` | 4 | For normal mapping (surface orientation) |
| **Bitangent** | `vec3` | 5 | For normal mapping (completes basis) |
| **Bone IDs** | `ivec4` | 6 | Which bones affect this vertex (skinning) |
| **Bone Weights** | `vec4` | 7 | How much each bone influences |

### Complete Vertex Example

```cpp
// A vertex with multiple attributes
struct Vertex {
    // Position (12 bytes)
    float x, y, z;
    
    // Normal (12 bytes)
    float nx, ny, nz;
    
    // Color (16 bytes)
    float r, g, b, a;
    
    // Texture coordinates (8 bytes)
    float u, v;
    
    // Total: 48 bytes per vertex
};

// Array of vertices for a cube corner
Vertex vertices[] = {
    // Position           Normal           Color              UV
    { 0.5f, 0.5f, 0.5f,   1.0f,0.0f,0.0f,  1.0f,0.0f,0.0f,1.0f,  1.0f,1.0f },  // Vertex 0
    { 0.5f,-0.5f,0.5f,    1.0f,0.0f,0.0f,  0.0f,1.0f,0.0f,1.0f,  1.0f,0.0f },  // Vertex 1
    { -0.5f,-0.5f,0.5f,   1.0f,0.0f,0.0f,  0.0f,0.0f,1.0f,1.0f,  0.0f,0.0f },  // Vertex 2
    // ... more vertices
};
```

---

## Part 4: Vertex Position in Detail

### 3D Coordinates

```cpp
// 3D position (x, y, z)
float x = 1.5f;  // Left/Right
float y = 2.0f;  // Up/Down
float z = -3.0f; // Forward/Backward (OpenGL uses right-handed coordinates)

// Different coordinate systems have different orientation
// OpenGL: +X right, +Y up, +Z out of screen (camera looks down -Z)
// DirectX: +X right, +Y up, +Z into screen
```

### Position Data Layout Examples

```cpp
// Interleaved attributes (most common)
float vertices[] = {
    // Pos         Normal       UV
     0.5f, 0.5f, 0.0f, 0.0f,0.0f,1.0f, 1.0f,1.0f,  // Vertex 0
     0.5f,-0.5f, 0.0f, 0.0f,1.0f,0.0f, 1.0f,0.0f,  // Vertex 1
    -0.5f,-0.5f, 0.0f, 1.0f,0.0f,0.0f, 0.0f,0.0f   // Vertex 2
};

// Separate arrays (structure of arrays)
float positions[] = {
    0.5f, 0.5f, 0.0f,
    0.5f,-0.5f, 0.0f,
    -0.5f,-0.5f, 0.0f
};

float normals[] = {
    0.0f, 0.0f, 1.0f,
    0.0f, 1.0f, 0.0f,
    1.0f, 0.0f, 0.0f
};

float texCoords[] = {
    1.0f, 1.0f,
    1.0f, 0.0f,
    0.0f, 0.0f
};
```

---

## Part 5: Vertex Normals

### What is a Normal?

A **normal** is a vector perpendicular to the surface at the vertex location. It defines which direction the surface "faces" for lighting calculations.

```
Normal Visualized:
        ↑
        | Normal vector (perpendicular)
        |
        ●━━━━━━━━━━━ Surface
       Vertex

For a sphere:
    ●
     \    Normals point outward
      \   from center
       ●
        \
         ●←── Normal perpendicular to surface
```

### Normal Data

```cpp
// Normal as a 3D vector (nx, ny, nz)
// Should be normalized (length = 1.0) for correct lighting

// Cube face normals
float cubeNormals[] = {
    // Front face (all +Z)
    0.0f, 0.0f, 1.0f,  // Vertex 0
    0.0f, 0.0f, 1.0f,  // Vertex 1
    0.0f, 0.0f, 1.0f,  // Vertex 2
    0.0f, 0.0f, 1.0f,  // Vertex 3
    
    // Back face (all -Z)
    0.0f, 0.0f, -1.0f, // Vertex 4
    0.0f, 0.0f, -1.0f, // Vertex 5
    0.0f, 0.0f, -1.0f, // Vertex 6
    0.0f, 0.0f, -1.0f  // Vertex 7
};

// Sphere vertices have normals equal to normalized position
// For a sphere centered at origin:
// position = (x, y, z)
// normal = normalize(x, y, z)  // Same direction as position from center
```

### Why Normals Need Transformation

```glsl
// Vertex shader - transforming normals correctly
void main() {
    // Position transformation
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    
    // Normal transformation (special handling!)
    // Normals need inverse-transpose of model matrix
    // This handles non-uniform scaling correctly
    vNormal = mat3(transpose(inverse(model))) * aNormal;
    
    // For uniform scaling only, simpler version works:
    // vNormal = mat3(model) * aNormal;
}
```

---

## Part 6: Vertex Colors

### Per-Vertex Colors

Colors can be specified per vertex, which will be interpolated across triangles.

```cpp
// RGB colors (3 floats per vertex)
float colors[] = {
    1.0f, 0.0f, 0.0f,  // Vertex 0 - Red
    0.0f, 1.0f, 0.0f,  // Vertex 1 - Green
    0.0f, 0.0f, 1.0f,  // Vertex 2 - Blue
};

// RGBA colors (4 floats per vertex) - includes alpha/transparency
float colorsWithAlpha[] = {
    1.0f, 0.0f, 0.0f, 1.0f,  // Vertex 0 - Red, opaque
    0.0f, 1.0f, 0.0f, 0.5f,  // Vertex 1 - Green, semi-transparent
    0.0f, 0.0f, 1.0f, 0.0f,  // Vertex 2 - Blue, fully transparent
};
```

### Color Interpolation Example

```cpp
// Triangle with different colors at each vertex
float triangle[] = {
    // Position         Color
     0.0f,  1.0f, 0.0f, 1.0f, 0.0f, 0.0f,  // Top vertex - Red
    -1.0f, -1.0f, 0.0f, 0.0f, 1.0f, 0.0f,  // Bottom left - Green
     1.0f, -1.0f, 0.0f, 0.0f, 0.0f, 1.0f   // Bottom right - Blue
};

// Result: Triangle with smooth color gradient
// Center becomes mix of all three colors
```

---

## Part 7: Texture Coordinates (UVs)

### What are UV Coordinates?

UV coordinates map a 2D texture onto a 3D surface. U is horizontal, V is vertical.

```
Texture Space:
    U→
V   (0,0) ●──────● (1,0)
↓         |      |
          |      |
    (0,1) ●──────● (1,1)

UV Values:
- Range typically 0.0 to 1.0
- (0,0) = bottom-left of texture (in OpenGL)
- (1,1) = top-right of texture
- Values outside 0-1 can wrap, clamp, or repeat based on settings
```

### UV Data Examples

```cpp
// UV coordinates for a quad (two triangles)
float uvs[] = {
    // Triangle 1
    1.0f, 1.0f,  // Top-right of texture
    1.0f, 0.0f,  // Bottom-right
    0.0f, 0.0f,  // Bottom-left
    
    // Triangle 2
    0.0f, 0.0f,  // Bottom-left
    0.0f, 1.0f,  // Top-left
    1.0f, 1.0f   // Top-right
};

// UV mapping for a cube face
float cubeUVs[] = {
    // Front face
    0.0f, 0.0f,  // Bottom-left of texture
    1.0f, 0.0f,  // Bottom-right
    1.0f, 1.0f,  // Top-right
    0.0f, 1.0f,  // Top-left
    // ... other faces
};

// Tiling/repeating UVs (values > 1.0)
float tilingUVs[] = {
    2.0f, 2.0f,  // Texture repeats twice in both directions
    2.0f, 0.0f,
    0.0f, 0.0f,
    0.0f, 2.0f
};
```

---

## Part 8: Tangents and Bitangents

### What are Tangents?

Tangents and bitangents define the local orientation of the texture space on the surface, essential for normal mapping.

```
Normal Mapping Coordinate System:
        Bitangent (V direction)
            ↑
            |
            |    ● Surface
            |  ↗
            | Tangent (U direction)
            |
    Normal (pointing out)

The three vectors form an orthonormal basis:
- Normal: Perpendicular to surface
- Tangent: Points along U direction of texture
- Bitangent: Points along V direction (also called binormal)
```

### Tangent Space Basis

```cpp
// Vertex with tangent and bitangent
struct TangentSpaceVertex {
    // Position
    float px, py, pz;
    
    // Normal
    float nx, ny, nz;
    
    // UV
    float u, v;
    
    // Tangent (direction of U increase in texture)
    float tx, ty, tz;
    
    // Bitangent (direction of V increase, can be derived from cross product)
    float bx, by, bz;
    
    // Sign (handedness, -1 or 1)
    float sign;
};

// In vertex shader, transform all three to world space
vNormal = normalize(mat3(model) * aNormal);
vTangent = normalize(mat3(model) * aTangent);
vBitangent = normalize(mat3(model) * aBitangent);
// Or compute bitangent: vBitangent = cross(vNormal, vTangent) * aSign;
```

---

## Part 9: Bone Data for Skinning

### Skeletal Animation Data

For animated characters, vertices need information about which bones influence them.

```cpp
struct SkinnedVertex {
    // Position
    float px, py, pz;
    
    // Normal
    float nx, ny, nz;
    
    // UV
    float u, v;
    
    // Bone IDs (which bones affect this vertex)
    // Usually 4 bones per vertex maximum
    int boneIds[4];  // Indices into bone matrix array
    
    // Bone Weights (how much each bone influences)
    // Must sum to 1.0
    float boneWeights[4];
};

// Example: Vertex influenced by two bones
SkinnedVertex elbowVertex = {
    .position = {1.0f, 0.5f, 0.0f},
    .normal = {0.0f, 1.0f, 0.0f},
    .uv = {0.5f, 0.5f},
    .boneIds = {2, 3, 0, 0},  // Bones 2 and 3 affect this vertex
    .boneWeights = {0.7f, 0.3f, 0.0f, 0.0f}  // 70% bone 2, 30% bone 3
};
```

### Vertex Shader Skinning

```glsl
// Vertex shader for skeletal animation
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;
layout (location = 3) in ivec4 aBoneIds;
layout (location = 4) in vec4 aWeights;

uniform mat4 boneTransforms[100];

void main() {
    // Compute skinning matrix
    mat4 skinTransform = 
        boneTransforms[aBoneIds[0]] * aWeights[0] +
        boneTransforms[aBoneIds[1]] * aWeights[1] +
        boneTransforms[aBoneIds[2]] * aWeights[2] +
        boneTransforms[aBoneIds[3]] * aWeights[3];
    
    // Apply to position
    vec4 skinnedPos = skinTransform * vec4(aPos, 1.0);
    
    // Apply to normal (3x3 part only)
    mat3 skinNormalTransform = mat3(skinTransform);
    vec3 skinnedNormal = skinNormalTransform * aNormal;
    
    // Final transformation
    gl_Position = projection * view * model * skinnedPos;
    vNormal = skinnedNormal;
    vTexCoord = aTexCoord;
}
```

---

## Part 10: Vertex Data Layout in Memory

### Interleaved vs Separate Buffers

```cpp
// INTERLEAVED (most common)
// Each vertex's attributes are stored together
// Memory: [Pos0][Norm0][UV0][Pos1][Norm1][UV1]...
float interleaved[] = {
    // Vertex 0
    x0, y0, z0, nx0, ny0, nz0, u0, v0,
    // Vertex 1
    x1, y1, z1, nx1, ny1, nz1, u1, v1,
    // Vertex 2
    x2, y2, z2, nx2, ny2, nz2, u2, v2,
};

// SEPARATE (structure of arrays)
// Each attribute in its own buffer
// Memory: [Pos0][Pos1][Pos2]...
float positions[] = { x0,y0,z0, x1,y1,z1, x2,y2,z2 };
float normals[] = { nx0,ny0,nz0, nx1,ny1,nz1, nx2,ny2,nz2 };
float uvs[] = { u0,v0, u1,v1, u2,v2 };
```

### Setting Up Vertex Attributes

```cpp
// Interleaved setup
glBindBuffer(GL_ARRAY_BUFFER, vbo);
glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

// Position attribute (location 0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 
                      8 * sizeof(float), (void*)0);
glEnableVertexAttribArray(0);

// Normal attribute (location 1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 
                      8 * sizeof(float), (void*)(3 * sizeof(float)));
glEnableVertexAttribArray(1);

// UV attribute (location 2)
glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 
                      8 * sizeof(float), (void*)(6 * sizeof(float)));
glEnableVertexAttribArray(2);

// Separate buffers setup
glBindBuffer(GL_ARRAY_BUFFER, positionVBO);
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void*)0);
glEnableVertexAttribArray(0);

glBindBuffer(GL_ARRAY_BUFFER, normalVBO);
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void*)0);
glEnableVertexAttribArray(1);
```

---

## Part 11: Vertex Shader Reception

### How Vertex Shader Receives Attributes

```glsl
#version 330 core

// Attribute locations match C++ setup
layout (location = 0) in vec3 aPos;      // Position
layout (location = 1) in vec3 aNormal;    // Normal
layout (location = 2) in vec2 aTexCoord;  // UV
layout (location = 3) in vec4 aColor;     // Color
layout (location = 4) in ivec4 aBoneIds;  // Bone IDs
layout (location = 5) in vec4 aWeights;   // Bone weights

// Outputs to fragment shader
out vec2 vTexCoord;
out vec3 vNormal;
out vec3 vFragPos;
out vec4 vColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    // Transform position
    vec4 worldPos = model * vec4(aPos, 1.0);
    vFragPos = worldPos.xyz;
    gl_Position = projection * view * worldPos;
    
    // Transform normal
    vNormal = mat3(transpose(inverse(model))) * aNormal;
    
    // Pass through other attributes
    vTexCoord = aTexCoord;
    vColor = aColor;
}
```

---

## Part 12: Vertex Counts and Memory

### Typical Vertex Counts

| Model Type | Vertex Count | Memory (48 bytes/vertex) |
|------------|--------------|--------------------------|
| Simple quad | 4 vertices | 192 bytes |
| Cube | 24 vertices (4 per face × 6 faces) | 1.1 KB |
| Simple character | ~1000 vertices | 48 KB |
| Detailed character | ~10,000 vertices | 480 KB |
| Game environment | ~100,000 vertices | 4.8 MB |
| Open world scene | Millions | 10-100 MB |

### Vertex Throughput

```cpp
// Modern GPU can process millions of vertices per frame
// Example: 60 FPS, 1 million vertices
// Vertex throughput = 60,000,000 vertices per second
// Each vertex shader runs for each vertex
// That's why vertex shaders must be efficient!
```

---

## The 30-Second Summary

- **Vertex** = A point in 3D space that serves as a building block for geometry
- **Position** = Required attribute (x, y, z coordinates)
- **Attributes** = Additional data per vertex (normals, colors, UVs, tangents, bone data)
- **Normals** = Surface direction vectors for lighting (must be normalized)
- **UVs** = Texture coordinates mapping 2D images to 3D surfaces
- **Tangents/Bitangents** = Local texture space orientation for normal mapping
- **Bone Data** = IDs and weights for skeletal animation
- **Memory Layout** = Interleaved (most common) or separate buffers
- **Processing** = Each vertex processed independently by vertex shader

**Vertices are the fundamental building blocks of 3D graphics - every visible object is constructed from them, and every pixel on screen ultimately traces back to vertex data.**

---
