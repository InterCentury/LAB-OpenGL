# Explanation about Vertex-Shader 

## The Assembly Line Worker Analogy

A vertex shader can be understood through an automotive assembly line worker:

- **The Worker** = The vertex shader instance (one per vertex)
- **The Car Part** = The vertex (a single point in 3D space)
- **The Blueprint** = The shader program (instructions)
- **The Toolbox** = Uniforms (global tools available to all workers)
- **The Assembly Instructions** = Vertex attributes (data attached to each part)
- **The Finished Component** = The transformed vertex ready for the next stage

**Each worker takes one raw part, follows the same blueprint, and transforms it into a standardized component. Thousands of workers do this simultaneously.**

---

## Part 1: What is a Vertex Shader?

### Definition

A **vertex shader** is a programmable stage in the graphics pipeline that processes each vertex individually. It is the first stage in the pipeline and **mandatory** in modern OpenGL.

### Core Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Position Transformation** | Convert 3D coordinates from model space to screen space |
| **Data Preparation** | Calculate and pass data to fragment shader |
| **Per-Vertex Lighting** | Compute lighting at vertices (legacy approach) |
| **Vertex Animation** | Animate vertices (skinning, waves, etc.) |
| **Attribute Processing** | Read and interpret vertex attributes |

### Key Characteristics

| Aspect | Value |
|--------|-------|
| **Invocation** | Once per vertex in the draw call |
| **Input** | Vertex attributes + Uniforms |
| **Output** | Transformed vertex + Varying data |
| **Parallelism** | Thousands of instances simultaneously |
| **Mandatory?** | Yes (in Core Profile) |

---

## Part 2: Vertex Shader Inputs

### Input Category 1: Vertex Attributes

Vertex attributes are data associated with **each individual vertex**.

```cpp
// C++ side - defining vertex data
float vertices[] = {
    // Position        // Color         // UV
     0.5f,  0.5f, 0.0f, 1.0f, 0.0f, 0.0f, 1.0f, 0.0f,  // Vertex 0
     0.5f, -0.5f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f, 1.0f,  // Vertex 1
    -0.5f, -0.5f, 0.0f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f   // Vertex 2
};

// Setting up attribute pointers
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)0);
glEnableVertexAttribArray(0);  // Position (location 0)

glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(3 * sizeof(float)));
glEnableVertexAttribArray(1);  // Color (location 1)

glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(6 * sizeof(float)));
glEnableVertexAttribArray(2);  // UV (location 2)
```

```glsl
// GLSL side - receiving vertex attributes
#version 330 core

// Attribute locations match the C++ side
layout (location = 0) in vec3 aPos;     // Position
layout (location = 1) in vec3 aColor;   // Color  
layout (location = 2) in vec2 aTexCoord; // UV coordinates

void main()
{
    // Use these attributes
    gl_Position = vec4(aPos, 1.0);
    // aColor and aTexCoord available for processing
}
```

### Common Vertex Attributes

| Attribute | GLSL Type | Typical Location | Purpose |
|-----------|-----------|------------------|---------|
| **Position** | `vec3` or `vec4` | 0 | Vertex location in 3D space |
| **Normal** | `vec3` | 1 | Surface direction for lighting |
| **Color** | `vec3` or `vec4` | 2 | Per-vertex color |
| **UV** | `vec2` | 3 | Texture coordinates |
| **Tangent** | `vec3` | 4 | For normal mapping |
| **Bitangent** | `vec3` | 5 | For normal mapping |
| **Bone IDs** | `ivec4` | 6 | Skeletal animation |
| **Bone Weights** | `vec4` | 7 | Skeletal animation influence |

### Input Category 2: Uniforms

Uniforms are **global** values that are the same for all vertices in a draw call.

```cpp
// C++ side - setting uniforms
glUseProgram(shaderProgram);

// Matrix uniforms
glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm::value_ptr(projection));

// Time uniform
glUniform1f(timeLoc, glfwGetTime());

// Light position
glUniform3f(lightPosLoc, 5.0f, 5.0f, 5.0f);
```

```glsl
// GLSL side - receiving uniforms
#version 330 core

layout (location = 0) in vec3 aPos;

// Uniforms - same for all vertices
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float time;
uniform vec3 lightPos;

void main()
{
    // Use uniforms in calculations
    vec4 worldPos = model * vec4(aPos, 1.0);
    gl_Position = projection * view * worldPos;
    
    // time and lightPos also available
}
```

### Input Category 3: System Values

Special built-in variables and inputs.

```glsl
#version 330 core

layout (location = 0) in vec3 aPos;

// Built-in system values
// gl_VertexID - index of this vertex (0, 1, 2, ...)
// gl_InstanceID - instance index (for instanced rendering)

void main()
{
    // Use vertex ID for procedural effects
    float offset = float(gl_VertexID) * 0.1;
    vec3 animatedPos = aPos + vec3(offset, 0.0, 0.0);
    
    gl_Position = vec4(animatedPos, 1.0);
}
```

---

## Part 3: Vertex Shader Outputs

### Mandatory Output: gl_Position

Every vertex shader **must** write to `gl_Position` - the clip-space position of the vertex.

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 mvp;  // Model-View-Projection matrix

void main()
{
    // REQUIRED: Write to gl_Position
    gl_Position = mvp * vec4(aPos, 1.0);
    
    // If you don't write to gl_Position, behavior is undefined!
}
```

**What happens to gl_Position:**
1. Vertex shader outputs position in **clip space**
2. OpenGL performs **perspective division** (x/w, y/w, z/w)
3. Transforms to **normalized device coordinates** (-1 to 1)
4. Viewport transform maps to **screen coordinates**

### Optional Outputs: Varying Variables

Variables passed to the fragment shader, prefixed with `out` in vertex shader and `in` in fragment shader.

```glsl
// VERTEX SHADER
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;

// Outputs to fragment shader (varyings)
out vec3 vNormal;
out vec2 vTexCoord;
out vec3 vFragPos;
out float vVertexId;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    // Calculate world position
    vec4 worldPos = model * vec4(aPos, 1.0);
    vFragPos = worldPos.xyz;
    
    // Transform normal to world space
    vNormal = mat3(transpose(inverse(model))) * aNormal;
    
    // Pass through texture coordinate
    vTexCoord = aTexCoord;
    
    // Pass vertex ID as float (for effects)
    vVertexId = float(gl_VertexID);
    
    // Final position
    gl_Position = projection * view * worldPos;
}
```

```glsl
// FRAGMENT SHADER
#version 330 core

// Inputs from vertex shader (interpolated!)
in vec3 vNormal;
in vec2 vTexCoord;
in vec3 vFragPos;
in float vVertexId;

out vec4 FragColor;

void main()
{
    // Use interpolated values
    // vNormal varies smoothly across the triangle
    // vTexCoord varies smoothly
    // vFragPos varies smoothly
    
    FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);
}
```

---

## Part 4: The Transformation Pipeline

### Coordinate Systems

```
OBJECT SPACE (local coordinates)
    ↓ [ MODEL MATRIX ]
WORLD SPACE (scene coordinates)
    ↓ [ VIEW MATRIX ]
VIEW SPACE (camera coordinates)
    ↓ [ PROJECTION MATRIX ]
CLIP SPACE (homogeneous coordinates)
    ↓ [ perspective division ]
NORMALIZED DEVICE COORDINATES (-1 to 1)
    ↓ [ viewport transform ]
WINDOW COORDINATES (pixel positions)
```

### Complete Transformation Example

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;

// Transformation matrices
uniform mat4 model;      // Object → World
uniform mat4 view;       // World → View (camera)
uniform mat4 projection; // View → Clip

// Outputs
out vec3 vNormal;
out vec2 vTexCoord;
out vec3 vWorldPos;

void main()
{
    // 1. Object → World space
    vec4 worldPos = model * vec4(aPos, 1.0);
    vWorldPos = worldPos.xyz;
    
    // 2. World → View → Clip space (all in one go)
    gl_Position = projection * view * worldPos;
    
    // 3. Transform normal to world space
    // (inverse transpose handles non-uniform scaling correctly)
    vNormal = mat3(transpose(inverse(model))) * aNormal;
    
    // 4. Pass texture coordinate
    vTexCoord = aTexCoord;
}
```

### Matrix Multiplication Order

**IMPORTANT:** Matrix multiplication order matters!

```glsl
// CORRECT: Scale → Rotate → Translate → View → Project
gl_Position = projection * view * translation * rotation * scale * vec4(aPos, 1.0);

// This reads RIGHT to LEFT:
// 1. scale the vertex
// 2. rotate the vertex
// 3. translate the vertex
// 4. apply view (camera)
// 5. apply projection

// WRONG: Wrong order gives completely different results!
gl_Position = scale * rotation * translation * view * projection * vec4(aPos, 1.0);
```

---

## Part 5: Common Vertex Shader Operations

### 1. Simple Passthrough

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 vTexCoord;

uniform mat4 mvp;

void main()
{
    gl_Position = mvp * vec4(aPos, 1.0);
    vTexCoord = aTexCoord;  // Just pass through
}
```

### 2. Wave Animation

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 vTexCoord;

uniform mat4 mvp;
uniform float time;

void main()
{
    // Animate Y position based on X and time
    vec3 animatedPos = aPos;
    animatedPos.y += sin(aPos.x * 2.0 + time * 3.0) * 0.2;
    
    gl_Position = mvp * vec4(animatedPos, 1.0);
    vTexCoord = aTexCoord;
}
```

### 3. Billboard (Sprite Always Faces Camera)

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 vTexCoord;

uniform mat4 view;
uniform mat4 projection;
uniform vec3 billboardPosition;

void main()
{
    // Extract camera right and up vectors from view matrix
    vec3 cameraRight = vec3(view[0][0], view[1][0], view[2][0]);
    vec3 cameraUp = vec3(view[0][1], view[1][1], view[2][1]);
    
    // Billboard: position + offset in camera space
    vec3 worldPos = billboardPosition + 
                    cameraRight * aPos.x + 
                    cameraUp * aPos.y;
    
    gl_Position = projection * view * vec4(worldPos, 1.0);
    vTexCoord = aTexCoord;
}
```

### 4. Skinning (Skeletal Animation)

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;
layout (location = 3) in ivec4 aBoneIDs;  // Which bones affect this vertex
layout (location = 4) in vec4 aWeights;   // How much each bone influences

out vec2 vTexCoord;
out vec3 vNormal;
out vec3 vWorldPos;

const int MAX_BONES = 100;
uniform mat4 boneTransforms[MAX_BONES];
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    // Compute skinning matrix by blending bone transforms
    mat4 skinTransform = 
        boneTransforms[aBoneIDs[0]] * aWeights[0] +
        boneTransforms[aBoneIDs[1]] * aWeights[1] +
        boneTransforms[aBoneIDs[2]] * aWeights[2] +
        boneTransforms[aBoneIDs[3]] * aWeights[3];
    
    // Apply skinning to position
    vec4 skinnedPos = skinTransform * vec4(aPos, 1.0);
    
    // Apply skinning to normal (3x3 part only)
    mat3 skinNormalTransform = mat3(skinTransform);
    vNormal = skinNormalTransform * aNormal;
    
    // Final transformation
    vec4 worldPos = model * skinnedPos;
    vWorldPos = worldPos.xyz;
    gl_Position = projection * view * worldPos;
    
    vTexCoord = aTexCoord;
}
```

### 5. Instancing

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;
layout (location = 2) in mat4 instanceTransform;  // Per-instance matrix

out vec2 vTexCoord;

uniform mat4 view;
uniform mat4 projection;

void main()
{
    // Use instance-specific transform
    vec4 worldPos = instanceTransform * vec4(aPos, 1.0);
    gl_Position = projection * view * worldPos;
    vTexCoord = aTexCoord;
}
```

---

## Part 6: Vertex Shader Limitations

### What Vertex Shader Cannot Do

| Limitation | Reason |
|------------|--------|
| **Create new vertices** | Fixed input → fixed output count |
| **Delete vertices** | Cannot cull geometry |
| **Access other vertices** | Each vertex processed independently |
| **Know primitive topology** | Doesn't know if part of triangle/line |
| **Access textures arbitrarily** | Limited texture access (usually not recommended) |
| **Write to framebuffer** | Only fragment shader writes colors |
| **Persist data between invocations** | No shared memory between vertices |

### Performance Constraints

| Constraint | Typical Limit | Implication |
|------------|---------------|-------------|
| **Maximum attributes** | 16 vec4 inputs | Limited data per vertex |
| **Maximum uniform size** | 64KB | Limited global data |
| **Instruction count** | Thousands | Complex operations slow |
| **Texture access** | Slow | Avoid in vertex shaders |
| **Branching** | Divergence penalty | Keep uniform control flow |

---

## Part 7: Debugging Vertex Shaders

### Common Vertex Shader Errors

```glsl
// ERROR: Missing gl_Position assignment
void main()
{
    // Nothing here - undefined behavior!
}

// ERROR: Wrong output variable name
out vec3 myColor;  // This is fine, but...
// In fragment shader: in vec3 vColor;  // Names must match!
// Better to use same name or layout(location)

// ERROR: Matrix multiplication order
gl_Position = vec4(aPos, 1.0) * mvp;  // Wrong! Matrix * vector, not vector * matrix

// ERROR: Forgetting to transform normals
vNormal = aNormal;  // Wrong! Normals need inverse-transpose of model matrix
```

### Debugging Techniques

```cpp
// 1. Output vertex positions as colors (temporary debugging)
// Vertex shader:
out vec3 vColor;
void main() {
    vColor = aPos * 0.5 + 0.5;  // Map -1..1 to 0..1
    gl_Position = mvp * vec4(aPos, 1.0);
}

// Fragment shader:
in vec3 vColor;
void main() {
    FragColor = vec4(vColor, 1.0);  // See positions as colors
}

// 2. Check compilation errors
glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
if (!success) {
    glGetShaderInfoLog(vertexShader, 512, NULL, infoLog);
    std::cout << "Vertex shader compilation failed:\n" << infoLog << std::endl;
}

// 3. Use renderDoc or similar GPU debuggers
```

---

## Part 8: Vertex Shader vs Fragment Shader

### Comparison Table

| Aspect | Vertex Shader | Fragment Shader |
|--------|---------------|-----------------|
| **Invocation count** | Number of vertices | Number of pixels (much higher) |
| **Input** | Raw vertex attributes | Interpolated vertex data |
| **Output** | Clip-space position + varyings | Final color + depth |
| **Can discard?** | No | Yes (`discard`) |
| **Can write position?** | Yes (mandatory) | No |
| **Can write color?** | No | Yes |
| **Can access textures?** | Limited, slow | Yes, optimized |
| **Derivatives** | No | Yes (`dFdx`, `dFdy`) |
| **Parallelism** | Per-vertex | Per-fragment (more threads) |

### Data Flow Between Them

```
VERTEX SHADER (runs 3 times for a triangle)
├─ Vertex 0: outputs vColor = red
├─ Vertex 1: outputs vColor = green  
└─ Vertex 2: outputs vColor = blue

RASTERIZER (interpolates)
├─ Pixel at center: vColor = mix of red, green, blue
└─ Pixel at edge: vColor = mostly red + little green

FRAGMENT SHADER (runs for each pixel)
└─ Uses interpolated vColor to compute final color
```

---

## Part 9: Advanced Vertex Shader Concepts

### Geometry Shader vs Vertex Shader

```glsl
// Vertex shader: one in, one out
VS(vertex) → transformed vertex

// Geometry shader: one in, many out possible
GS(triangle) → up to N triangles

// Use vertex shader for per-vertex operations
// Use geometry shader for primitive-level operations
```

### Tessellation Relationship

```
VERTEX SHADER (processes control points)
    ↓
TESSELLATION CONTROL SHADER (determines subdivision)
    ↓
TESSELLATION EVALUATION SHADER (positions new vertices)
    ↓
GEOMETRY SHADER (optional further processing)
```

### Compute Shader Comparison

Vertex shaders are specialized for graphics. Compute shaders are general-purpose:

- Vertex shader: fixed role in graphics pipeline
- Compute shader: can do anything, anywhere
- Vertex shader: automatic parallelism per vertex
- Compute shader: manual work group management

---

## Part 10: Optimization Tips

### Do's and Don'ts

| Do | Don't |
|----|-------|
| **Minimize calculations** per vertex | Compute the same thing for every vertex |
| **Pass data to fragment shader** for per-pixel work | Do per-pixel work in vertex shader |
| **Use uniform buffers** for frequent data | Update uniforms every draw call |
| **Transform lights to view space** once per frame | Transform lights per vertex |
| **Use `invariant` qualifier** for consistent results | Rely on identical results across vendors |

### Performance Examples

```glsl
// BAD: Expensive calculation per vertex
uniform vec3 lightPos;
uniform vec3 lightColor;
void main() {
    // This lighting calculation should be in fragment shader!
    float distance = length(lightPos - vFragPos);
    float attenuation = 1.0 / (distance * distance);
    vLighting = lightColor * attenuation;  // Wrong place!
}

// GOOD: Pass data to fragment shader
void main() {
    vFragPos = worldPos.xyz;
    vLightPos = lightPos;  // Pass to fragment shader
    // Let fragment shader do per-pixel lighting
}
```

---

## The 30-Second Summary

- **Vertex Shader** = Program that processes each vertex individually
- **Mandatory** = Must be present in modern OpenGL
- **Input** = Vertex attributes (per-vertex) + Uniforms (global)
- **Output** = `gl_Position` (required) + Varying variables (optional)
- **Main Job** = Transform vertices from 3D model space to 2D screen space
- **Parallelism** = Runs once per vertex, thousands simultaneously
- **Cannot** = Create/delete vertices, access other vertices, write colors
- **Common Uses** = Transformations, animation, data preparation

**The vertex shader is the gateway to the GPU pipeline - every visible object must pass through it, and its transformations determine everything that follows.**

---

**Next Step:** Ready to understand the fragment shader in detail?