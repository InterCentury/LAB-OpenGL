# How the Rendering Pipeline Works

## The Restaurant Kitchen Analogy

The rendering pipeline can be understood through a restaurant kitchen preparing a meal:

- **The Recipe** = Shader programs (instructions for each stage)
- **The Ingredients** = Vertex data (positions, colors, textures)
- **The Prep Cooks** = Vertex Shader (prepare each ingredient)
- **The Portion Controller** = Tessellation (divide into appropriate portions)
- **The Plate Designer** = Geometry Shader (arrange on plate)
- **The Oven** = Rasterization (transform preparation to final cooking)
- **The Line Cooks** = Fragment Shader (cook each pixel)
- **The Quality Check** = Per-Fragment Operations (taste test before serving)
- **The Finished Plate** = Framebuffer (final image ready for customer)

**Each stage has a specific job, and data flows through them in order.**

---

## Part 1: What is the Rendering Pipeline?

### Definition

The **rendering pipeline** (also called the graphics pipeline) is the sequence of steps that graphics data follows from application memory to the final screen image.

### Key Concepts

| Concept | Explanation |
|---------|-------------|
| **Pipeline** | Data flows through stages, each transforming the data |
| **Programmable Stages** | Stages where custom code (shaders) runs |
| **Fixed Function Stages** | Hardware-controlled stages with configurable settings |
| **Vertex** | A point in 3D space (position, plus optional data) |
| **Primitive** | A basic shape (point, line, triangle) |
| **Fragment** | A potential pixel (before depth testing) |
| **Pixel** | The final screen dot (after all tests) |

### Pipeline Overview

```
APPLICATION (CPU)
    ↓ (Vertex Data)
VERTEX SHADER (Programmable)
    ↓ (Processed Vertices)
TESSELLATION (Optional, Programmable)
    ↓ (Refined Geometry)
GEOMETRY SHADER (Optional, Programmable)
    ↓ (Primitives)
RASTERIZATION (Fixed Function)
    ↓ (Fragments)
FRAGMENT SHADER (Programmable)
    ↓ (Colored Fragments)
PER-FRAGMENT OPERATIONS (Fixed Function)
    ↓ (Final Pixels)
FRAMEBUFFER (Screen/Texture)
```

---

## Part 2: Stage 1 - Application (CPU Side)

### What Happens

Before the GPU pipeline begins, the CPU prepares data and issues commands:

```cpp
// CPU-side preparation
// 1. Create and fill buffers
GLuint vbo;
glGenBuffers(1, &vbo);
glBindBuffer(GL_ARRAY_BUFFER, vbo);
glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

// 2. Set up vertex attributes
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)0);
glEnableVertexAttribArray(0);

// 3. Bind shaders and textures
glUseProgram(shaderProgram);
glBindTexture(GL_TEXTURE_2D, texture);

// 4. Set uniforms (global variables for shaders)
glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));

// 5. Draw call
glDrawArrays(GL_TRIANGLES, 0, 3);  // Pipeline starts here!
```

### Draw Call Anatomy

A single `glDrawArrays` or `glDrawElements` contains:
- **Primitive Type**: Points, lines, triangles, etc.
- **First Vertex**: Starting index in buffer
- **Count**: Number of vertices to process
- **Instance Count**: (Optional) for instanced rendering

### What Gets Sent

| Data Type | Description | Example |
|-----------|-------------|---------|
| **Vertex Positions** | 3D coordinates | (0.5, 0.5, 0.0) |
| **Normals** | Direction vectors for lighting | (0.0, 1.0, 0.0) |
| **Texture Coordinates** | UV mapping | (0.5, 0.5) |
| **Colors** | Per-vertex colors | (1.0, 0.0, 0.0) |
| **Tangents/Bitangents** | For normal mapping | (1.0, 0.0, 0.0) |

---

## Part 3: Stage 2 - Vertex Shader (Programmable)

### Purpose

Process each vertex individually, transforming from 3D world space to screen space.

### Input → Output

```
INPUT PER VERTEX:
┌─────────────────────┐
│ Position (vec3)     │
│ Normal (vec3)       │
│ UV (vec2)           │
│ Color (vec4)        │
└─────────────────────┘
        ↓
[ VERTEX SHADER ]
        ↓
OUTPUT PER VERTEX:
┌─────────────────────┐
│ gl_Position (vec4)  │ ← Special: clip space position
│ UV (vec2)           │ ← Pass-through
│ Color (vec4)        │ ← Pass-through
│ Normal (vec3)       │ ← Pass-through (transformed)
└─────────────────────┘
```

### Vertex Shader Code Example

```glsl
#version 330 core

// Input attributes (per vertex)
layout (location = 0) in vec3 aPos;    // Position
layout (location = 1) in vec3 aNormal; // Normal
layout (location = 2) in vec2 aTexCoord; // UV

// Uniforms (same for all vertices)
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

// Outputs to fragment shader
out vec2 TexCoord;
out vec3 Normal;
out vec3 FragPos;

void main()
{
    // Transform position: local → world → view → clip space
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    
    // Pass through texture coordinate
    TexCoord = aTexCoord;
    
    // Transform normal to world space (for lighting)
    Normal = mat3(transpose(inverse(model))) * aNormal;
    
    // Calculate fragment position in world space
    FragPos = vec3(model * vec4(aPos, 1.0));
}
```

### Important Concepts

| Concept | Explanation |
|---------|-------------|
| **Clip Space** | Coordinate system after projection, before perspective divide |
| **Invocation Count** | Vertex shader runs once per vertex |
| **No Vertex Creation** | Cannot create new vertices |
| **No Vertex Destruction** | Cannot discard vertices |

---

## Part 4: Stage 3 - Tessellation (Optional, Programmable)

### Purpose

Subdivide geometry to add detail dynamically based on distance or other factors.

### Three Sub-Stages

```
CONTROL SHADER
    ↓ (Determines how much to subdivide)
TESSELLATION PRIMITIVE GENERATOR (Fixed Function)
    ↓ (Creates new vertices)
EVALUATION SHADER
    ↓ (Positions new vertices)
```

### Tessellation Example

```
Original Triangle (3 vertices):
    ▲
   / \
  /   \
 /     \
─────────

After Tessellation (many vertices):
    ▲
   / \
  /   \
 /     \
/_______\
/\     /\
/  \   /  \
/    \ /    \
─────────────
```

### When to Use

| Use Case | Benefit |
|----------|---------|
| **Terrain Rendering** | More detail near camera |
| **Subdivision Surfaces** | Smooth models from coarse meshes |
| **Adaptive Detail** | Performance optimization |
| **Displacement Mapping** | Add geometric detail from textures |

---

## Part 5: Stage 4 - Geometry Shader (Optional, Programmable)

### Purpose

Process entire primitives (points, lines, triangles) and can:
- Amplify geometry (create more primitives)
- Reduce geometry (discard primitives)
- Change primitive type

### Input → Output

```
INPUT: One primitive (triangle with 3 vertices)
    ↓
[ GEOMETRY SHADER ]
    ↓
OUTPUT: 0, 1, or many primitives (any type)
```

### Geometry Shader Example

```glsl
#version 330 core
layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;

void main()
{
    // Pass through original triangle
    for(int i = 0; i < 3; i++)
    {
        gl_Position = gl_in[i].gl_Position;
        EmitVertex();
    }
    EndPrimitive();
    
    // Could emit more primitives here
    // For example: create a second triangle offset upward
}
```

### Use Cases

| Use Case | Description |
|----------|-------------|
| **Billboarding** | Make sprites always face camera |
| **Shadow Volume Generation** | Create shadow volumes from silhouettes |
| **Particle Systems** | Generate quads from points |
| **Wireframe Rendering** | Convert triangles to lines |
| **Point Sprite Expansion** | Turn points into quads |

---

## Part 6: Stage 5 - Rasterization (Fixed Function)

### Purpose

Convert geometric primitives into fragments (potential pixels).

### The Rasterization Process

```
TRIANGLE IN SCREEN SPACE:
(0,0)                     (1920,0)
    ┌─────────────────────┐
    │                     │
    │      ▲              │
    │     / \             │
    │    /   \            │
    │   /     \           │
    │  /       \          │
    │ /         \         │
    │/           \        │
    └─────────────────────┘
(0,1080)                (1920,1080)

AFTER RASTERIZATION:
    ┌─────────────────────┐
    │                     │
    │      ████           │
    │    ████████         │
    │   ██████████        │
    │  ████████████       │
    │ ██████████████      │
    │████████████████     │
    └─────────────────────┘
Each █ represents one fragment (pixel candidate)
```

### What Rasterization Does

| Operation | Description |
|-----------|-------------|
| **Scan Conversion** | Determine which pixels are inside triangles |
| **Interpolation** | Smoothly vary vertex attributes across triangle |
| **Perspective Correction** | Correct interpolation for 3D perspective |
| **Early Z-Test** | Optional depth test before fragment shading |

### Interpolation Example

```
Vertex Attributes:
    Red (1,0,0) at top
    Green (0,1,0) at left
    Blue (0,0,1) at right

Rasterizer Interpolates:
    Top edge: Red → Green gradient
    Bottom: Red → Blue gradient
    Center: Mix of all three

Result: Smooth color transition across triangle
```

---

## Part 7: Stage 6 - Fragment Shader (Programmable)

### Purpose

Calculate the final color of each fragment.

### Input → Output

```
INPUT PER FRAGMENT:
┌─────────────────────┐
│ UV coordinates      │ ← Interpolated from vertices
│ Color (if provided) │ ← Interpolated
│ Normal              │ ← Interpolated
│ World Position      │ ← Interpolated
└─────────────────────┘
        ↓
[ FRAGMENT SHADER ]
        ↓
OUTPUT PER FRAGMENT:
┌─────────────────────┐
│ Final Color (vec4)  │ ← RGBA output
│ Depth (optional)    │ ← Can modify depth
└─────────────────────┘
```

### Fragment Shader Code Example

```glsl
#version 330 core

// Inputs from vertex shader (interpolated)
in vec2 TexCoord;
in vec3 Normal;
in vec3 FragPos;

// Uniforms
uniform sampler2D ourTexture;
uniform vec3 lightPos;
uniform vec3 lightColor;
uniform vec3 viewPos;

// Output
out vec4 FragColor;

void main()
{
    // Texture sampling
    vec4 texColor = texture(ourTexture, TexCoord);
    
    // Simple lighting calculation
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    
    // Diffuse lighting
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // Ambient lighting
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;
    
    // Combine
    vec3 result = (ambient + diffuse) * texColor.rgb;
    
    // Output final color
    FragColor = vec4(result, 1.0);
}
```

### Common Fragment Shader Operations

| Operation | Purpose |
|-----------|---------|
| **Texture Sampling** | Apply images to surfaces |
| **Lighting Calculations** | Diffuse, specular, ambient |
| **Normal Mapping** | Fake surface detail |
| **Discard** | Make fragments transparent (holes) |
| **Alpha Blending** | Transparency |
| **Post-Processing** | Color grading, effects |

---

## Part 8: Stage 7 - Per-Fragment Operations (Fixed Function)

### Purpose

Test and combine fragments before final output.

### Operation Order

```
FRAGMENT FROM SHADER
    ↓
PIXEL OWNERSHIP TEST (Is this window pixel mine?)
    ↓
SCISSOR TEST (Is fragment inside scissor rectangle?)
    ↓
ALPHA TEST (Legacy, rarely used)
    ↓
STENCIL TEST (Stencil buffer operations)
    ↓
DEPTH TEST (Z-buffer compare)
    ↓
BLENDING (Combine with existing framebuffer color)
    ↓
DITHERING (Color precision reduction)
    ↓
LOGIC OPERATION (AND, OR, XOR, etc. - rarely used)
    ↓
FRAMEBUFFER (Final pixel written)
```

### Depth Testing

```
DEPTH BUFFER CONCEPT:
Screen pixel (x,y) stores depth value z

Before writing new fragment:
if (newFragment.z < depthBuffer[x][y]) {
    // New fragment is closer
    depthBuffer[x][y] = newFragment.z;
    write fragment color;
} else {
    // New fragment is behind existing
    discard fragment;
}
```

### Stencil Testing

```
STENCIL BUFFER:
Each pixel stores an integer value (usually 8-bit)

Common uses:
- Portals (only render through portal shape)
- Mirrors (render reflection only in mirror area)
- Shadows (stencil shadow volumes)
- Outlines (render only around objects)
```

### Blending

```glsl
// Enable blending
glEnable(GL_BLEND);
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

// Blend equation:
FinalColor = SourceColor * SourceFactor + DestColor * DestFactor
// For transparency:
FinalColor = SourceColor * src_alpha + DestColor * (1 - src_alpha)
```

---

## Part 9: Complete Pipeline Example

### Drawing a Simple Textured Cube

```
APPLICATION:
├─ Create vertex buffer with 36 vertices (6 faces × 2 triangles × 3 vertices)
├─ Create texture and load image
├─ Set model matrix (rotate 45 degrees)
├─ Set view matrix (camera at (5,5,5))
├─ Set projection matrix (perspective)
└─ glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, 0)

VERTEX SHADER (36 invocations):
├─ Transform each vertex using model-view-projection
├─ Pass UV coordinates
└─ Pass transformed normal

RASTERIZATION:
├─ Determine which pixels are covered by cube triangles
├─ Interpolate UVs and normals across faces
└─ Generate fragments (varies by resolution: 1080p = ~2M fragments)

FRAGMENT SHADER (one per fragment):
├─ Sample texture using interpolated UVs
├─ Calculate lighting using interpolated normals
└─ Output final color

PER-FRAGMENT OPERATIONS:
├─ Test depth (hide back faces)
├─ Test stencil (if enabled)
├─ Blend (if transparent)
└─ Write to framebuffer

FRAMEBUFFER:
└─ Display final image on screen
```

---

## Part 10: Pipeline Variations

### Forward Rendering

```
One pass per light:
Geometry → Shade with Light 1 → Geometry → Shade with Light 2 → ...

Pros: Simple, MSAA works well
Cons: Many passes with many lights
```

### Deferred Rendering

```
Pass 1: Geometry → Write G-Buffer (position, normal, color, etc.)
Pass 2: Light calculations using G-buffer

Pros: Many lights efficiently
Cons: No MSAA, high memory bandwidth
```

### Ray Tracing Pipeline (Modern)

```
Ray Generation → Ray Intersection → Any Hit → Miss → Closest Hit

Different paradigm: Trace rays rather than rasterize triangles
```

---

## Part 11: Performance Considerations

### Bottlenecks by Stage

| Stage | Common Bottleneck | Solution |
|-------|-------------------|----------|
| **Vertex Shader** | Too many vertices | LOD, culling, instancing |
| **Tessellation** | Over-subdivision | Adaptive tessellation |
| **Geometry Shader** | Amplification | Use sparingly, consider compute shaders |
| **Rasterization** | Overdraw (many layers) | Early Z, depth prepass |
| **Fragment Shader** | Complex calculations | Simplify shaders, reduce resolution |
| **Per-Fragment** | Bandwidth limits | Compression, reduced bit depth |

### Optimization Techniques

| Technique | Description |
|-----------|-------------|
| **Culling** | Don't process what isn't visible |
| **LOD (Level of Detail)** | Use simpler geometry far away |
| **Instancing** | Draw many copies with one call |
| **Early Z** | Reject hidden fragments early |
| **Texture Atlases** | Reduce texture binds |
| **Shader LOD** | Simpler shaders for distant objects |

---

## The 30-Second Summary

- **Rendering Pipeline** = The sequence of stages from vertices to pixels
- **Programmable Stages** = Vertex, Tessellation, Geometry, Fragment shaders
- **Fixed Function Stages** = Rasterization, Per-Fragment Operations
- **Vertex Shader** = Processes each vertex (position transformation)
- **Rasterization** = Converts triangles to fragments (pixel candidates)
- **Fragment Shader** = Colors each fragment (textures, lighting)
- **Per-Fragment Ops** = Tests and blending before final write
- **Output** = Final image in framebuffer ready for display

**The pipeline transforms abstract 3D data into the colorful 2D images seen on screen, with each stage contributing essential processing.**

---
