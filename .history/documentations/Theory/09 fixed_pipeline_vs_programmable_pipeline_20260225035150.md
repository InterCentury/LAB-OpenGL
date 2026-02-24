# Fixed Pipeline vs Programmable Pipeline

## The Restaurant Chain Analogy

The difference between fixed and programmable pipelines can be understood through restaurant chain evolution:

### Fixed Pipeline (Old Way) = McDonald's in the 1980s
- **Every burger** must be made exactly the same way
- **Equipment** is specialized: bun toaster only toasts, grill only grills
- **Employees** follow rigid procedures: "put patty, add pickle, add ketchup"
- **Menu** is fixed: cannot make a custom sandwich
- **Consistency** is guaranteed but creativity is impossible

### Programmable Pipeline (Modern Way) = Modern Kitchen
- **Chefs** can create any dish they imagine
- **Equipment** is versatile: same stove can boil, fry, sauté
- **Recipes** (shaders) can be written for each dish
- **Menu** is unlimited: anything that can be cooked
- **Creativity** is unlimited but requires skilled chefs

**The fixed pipeline gave consistent results but limited possibilities. The programmable pipeline puts the chef in control.**

---

## Part 1: What is the Fixed Pipeline?

### Definition

The **fixed function pipeline** (OpenGL 1.0-2.1) had every stage of rendering pre-programmed by the hardware manufacturer. Developers could only configure parameters, not change how stages processed data.

### Fixed Pipeline Characteristics

| Aspect | Description |
|--------|-------------|
| **Stages** | Hardwired into GPU hardware |
| **Control** | Through function calls (glEnable, glLight, glMaterial) |
| **Customization** | Limited to provided options |
| **Predictability** | Same behavior across implementations |
| **Learning Curve** | Easier to start, harder to do advanced effects |

### Fixed Pipeline Example

```cpp
// OpenGL 1.0 fixed function code
glBegin(GL_TRIANGLES);
    // Set color for this vertex
    glColor3f(1.0f, 0.0f, 0.0f);  // Red
    glVertex3f(0.0f, 1.0f, 0.0f); // Top
    
    glColor3f(0.0f, 1.0f, 0.0f);  // Green
    glVertex3f(-1.0f, -1.0f, 0.0f); // Bottom left
    
    glColor3f(0.0f, 0.0f, 1.0f);  // Blue
    glVertex3f(1.0f, -1.0f, 0.0f); // Bottom right
glEnd();

// Configure lighting (fixed function)
glEnable(GL_LIGHTING);
glEnable(GL_LIGHT0);

// Set light parameters (only these options exist)
GLfloat light_position[] = { 1.0, 1.0, 1.0, 0.0 };
GLfloat light_ambient[] = { 0.2, 0.2, 0.2, 1.0 };
GLfloat light_diffuse[] = { 0.8, 0.8, 0.8, 1.0 };

glLightfv(GL_LIGHT0, GL_POSITION, light_position);
glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient);
glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse);

// Set material properties (only these options exist)
glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient);
glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse);
```

---

## Part 2: What is the Programmable Pipeline?

### Definition

The **programmable pipeline** (OpenGL 2.0+) replaces fixed stages with **shaders** - small programs written by developers that run on the GPU.

### Programmable Pipeline Characteristics

| Aspect | Description |
|--------|-------------|
| **Stages** | Programmable via shader code |
| **Control** | Through GLSL (OpenGL Shading Language) |
| **Customization** | Unlimited - anything expressible in code |
| **Predictability** | Developer controls exact behavior |
| **Learning Curve** | Steeper start, unlimited potential |

### Programmable Pipeline Example

```cpp
// Modern OpenGL with shaders

// Vertex Shader (custom program)
const char* vertexShaderSource = R"(
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

out vec3 ourColor;

uniform mat4 transform;

void main()
{
    gl_Position = transform * vec4(aPos, 1.0);
    ourColor = aColor;  // Pass color to fragment shader
}
)";

// Fragment Shader (custom program)
const char* fragmentShaderSource = R"(
#version 330 core
in vec3 ourColor;
out vec4 FragColor;

void main()
{
    // Can do ANY calculation here, not just fixed options
    float brightness = sin(gl_FragCoord.x * 0.01); // Custom effect
    FragColor = vec4(ourColor * brightness, 1.0);
}
)";

// Compile and use custom shaders
GLuint vertexShader = glCreateShader(GL_VERTEX_SHADER);
glShaderSource(vertexShader, 1, &vertexShaderSource, NULL);
glCompileShader(vertexShader);

// ... linking and rendering code
```

---

## Part 3: Side-by-Side Comparison

### Stage-by-Stage Comparison

| Pipeline Stage | Fixed Function (Pre-2004) | Programmable (Modern) |
|----------------|---------------------------|----------------------|
| **Vertex Processing** | `glTranslate`, `glRotate`, `glScale` built-in | Vertex Shader (custom code) |
| **Lighting** | `glLight`, `glMaterial` parameters only | Calculated manually in shaders |
| **Texture Mapping** | Basic texenv modes (replace, modulate, decal) | Custom texture sampling and blending |
| **Color Calculation** | Fixed lighting + material equation | Any mathematical expression |
| **Fog** | Linear, exp, exp2 only | Custom fog equations |
| **Alpha Test** | Fixed comparison functions | `discard` keyword in fragment shader |
| **Pixel Processing** | Fixed texenv + fog | Complete freedom |

### Control Comparison

```cpp
// FIXED: Configure built-in behavior
glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
glFogi(GL_FOG_MODE, GL_EXP);
glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE);

// PROGRAMMABLE: Write custom behavior
// In fragment shader:
vec4 color = texture(myTexture, TexCoord);
color.rgb *= lightingCalculation(normal, lightPos);
if (distanceToCamera > fogDistance) {
    color = mix(color, fogColor, fogFactor);
}
```

---

## Part 4: Evolution Timeline

### The Fixed Function Era (1992-2004)

```
OpenGL 1.0 (1992):
├─ Immediate mode (glBegin/glEnd)
├─ Fixed transformation pipeline
├─ Basic lighting (Gouraud shading)
└─ Simple texturing

OpenGL 1.1 (1995):
├─ Vertex arrays
├─ Texture objects
└─ Polygon offset

OpenGL 1.2-1.5 (1998-2003):
├─ Multitexturing
├─ Cube maps
├─ Vertex Buffer Objects (VBOs)
└─ Occlusion queries

LIMITATIONS:
✗ Cannot create new lighting models
✗ Cannot access individual pixels in pipeline
✗ Fixed number of texture units
✗ No custom effects
```

### The Transition (2004-2008)

```
OpenGL 2.0 (2004):
├─ FIRST PROGRAMMABLE SHADERS
├─ GLSL introduced
├─ Vertex and Fragment shaders
└─ Fixed function still available (optional)

OpenGL 2.1 (2006):
├─ More GLSL features
├─ Better integration
└─ Dual pipeline support
```

### The Programmable Era (2008-Present)

```
OpenGL 3.0-3.3 (2008-2010):
├─ Core Profile (no fixed function)
├─ Deprecation model
├─ Geometry shaders
└─ Modern pipeline standard

OpenGL 4.0+ (2010-2017):
├─ Tessellation shaders
├─ Compute shaders
├─ Direct State Access
└─ Complete programmability
```

---

## Part 5: Fixed Pipeline Components (What Was Replaced)

### Transformation Pipeline (Fixed)

```
VERTEX (object space)
    ↓
[ MODELVIEW MATRIX ] (glMultMatrix, glTranslate, glRotate, glScale)
    ↓
VERTEX (eye space)
    ↓
[ LIGHTING ] (glLight, glMaterial)
    ↓
[ PROJECTION MATRIX ] (glFrustum, gluPerspective)
    ↓
CLIP SPACE
    ↓
[ PERSPECTIVE DIVIDE ] (automatic)
    ↓
NORMALIZED DEVICE COORDINATES
    ↓
[ VIEWPORT TRANSFORM ] (glViewport)
    ↓
WINDOW COORDINATES
```

### Texture Environment (Fixed)

```cpp
// Fixed function texture combining
glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
// Result = texture_color * vertex_color
// Other options: GL_REPLACE, GL_DECAL, GL_BLEND, GL_ADD

// No way to do: texture_color * vertex_color + specular * 0.5
// without multiple passes and blending
```

### Fog (Fixed)

```cpp
// Fixed fog options only
glFogi(GL_FOG_MODE, GL_LINEAR);  // or GL_EXP, GL_EXP2
glFogf(GL_FOG_DENSITY, 0.5f);
glFogf(GL_FOG_START, 1.0f);
glFogf(GL_FOG_END, 10.0f);

// Cannot create: height-based fog, animated fog, colored fog per pixel
```

---

## Part 6: Programmable Pipeline Advantages

### 1. Unlimited Lighting Models

```glsl
// Fixed function: Only Phong shading model
// Programmable: Any lighting model imaginable

// Toon shading (cel-shading)
float intensity = dot(normal, lightDir);
if (intensity > 0.95)
    color = vec4(1.0, 1.0, 1.0, 1.0);
else if (intensity > 0.5)
    color = vec4(0.7, 0.7, 0.7, 1.0);
else if (intensity > 0.25)
    color = vec4(0.4, 0.4, 0.4, 1.0);
else
    color = vec4(0.1, 0.1, 0.1, 1.0);

// PBR (Physically Based Rendering)
vec3 fresnel = mix(vec3(0.04), albedo, pow(1.0 - dot(view, half), 5.0));
vec3 specular = (D * G * fresnel) / (4.0 * dot(N, V) * dot(N, L) + 0.001);
```

### 2. Advanced Texturing

```glsl
// Fixed function: Simple texenv modes
// Programmable: Complex texture operations

// Normal mapping
vec3 normal = texture(normalMap, TexCoord).rgb;
normal = normalize(normal * 2.0 - 1.0);
float diff = max(dot(normal, lightDir), 0.0);

// Parallax mapping
float height = texture(heightMap, TexCoord).r;
vec2 parallaxOffset = viewDir.xy * (height * 0.1);
vec2 newTexCoord = TexCoord - parallaxOffset;

// Procedural textures
vec3 proceduralColor = vec3(
    sin(position.x * 10.0) * 0.5 + 0.5,
    cos(position.y * 10.0) * 0.5 + 0.5,
    sin(position.z * 10.0) * 0.5 + 0.5
);
```

### 3. Per-Pixel Effects

```glsl
// Fixed function: Per-vertex lighting only
// Programmable: Per-pixel everything

// Post-processing effects
void main()
{
    vec4 color = texture(screenTexture, TexCoord);
    
    // Sepia effect
    float r = dot(color.rgb, vec3(0.393, 0.769, 0.189));
    float g = dot(color.rgb, vec3(0.349, 0.686, 0.168));
    float b = dot(color.rgb, vec3(0.272, 0.534, 0.131));
    
    FragColor = vec4(r, g, b, color.a);
    
    // Motion blur, bloom, depth of field all possible
}
```

---

## Part 7: Code Comparison - Same Effect Both Ways

### Fixed Function Approach

```cpp
// Fixed function - limited options
glEnable(GL_LIGHTING);
glEnable(GL_LIGHT0);
glEnable(GL_TEXTURE_2D);

// Light properties
GLfloat light_diffuse[] = { 1.0, 0.8, 0.8, 1.0 };
glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse);

// Material properties
GLfloat mat_diffuse[] = { 0.8, 0.8, 0.8, 1.0 };
glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse);

// Texture environment
glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);

// Draw
glBegin(GL_TRIANGLES);
    // vertices with normals
glEnd();

// RESULT: Standard Phong shading, texture modulated with lighting
// CANNOT change: specular color separately, rim lighting, etc.
```

### Programmable Approach

```glsl
// Vertex Shader
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;

out vec2 TexCoord;
out vec3 Normal;
out vec3 FragPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoord = aTexCoord;
    gl_Position = projection * view * vec4(FragPos, 1.0);
}

// Fragment Shader
#version 330 core
in vec2 TexCoord;
in vec3 Normal;
in vec3 FragPos;

out vec4 FragColor;

uniform sampler2D ourTexture;
uniform vec3 lightPos;
uniform vec3 viewPos;

void main()
{
    vec4 texColor = texture(ourTexture, TexCoord);
    
    // Custom rim lighting effect (impossible in fixed function)
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    vec3 viewDir = normalize(viewPos - FragPos);
    
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * vec3(1.0, 0.8, 0.8);
    
    // Rim lighting (custom)
    float rim = 1.0 - max(dot(viewDir, norm), 0.0);
    rim = pow(rim, 2.0);
    vec3 rimLight = rim * vec3(1.0, 0.5, 0.5);
    
    vec3 result = (diffuse + rimLight) * texColor.rgb;
    FragColor = vec4(result, 1.0);
}
```

---

## Part 8: Performance Considerations

### Fixed Function Performance

| Aspect | Characteristic |
|--------|---------------|
| **Driver Overhead** | Lower (less validation) |
| **Optimization** | Hardware vendors optimized common cases |
| **Predictability** | Very predictable performance |
| **State Changes** | Cheap |
| **Complex Effects** | Multiple passes, slower |

### Programmable Performance

| Aspect | Characteristic |
|--------|---------------|
| **Driver Overhead** | Higher (shader compilation, validation) |
| **Optimization** | Developer must optimize |
| **Predictability** | Varies with shader complexity |
| **State Changes** | Shader switches expensive |
| **Complex Effects** | Single pass, potentially faster |

### When Fixed Function Was Faster

```cpp
// Simple texturing - fixed function was optimized in hardware
glEnable(GL_TEXTURE_2D);
glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
// Draw... Hardware did texture sampling very efficiently

// Same in shaders requires:
// - Shader compilation overhead
// - Register allocation
// - More pipeline stages
// - Potentially slower for simple cases
```

---

## Part 9: Why Fixed Function Was Removed

### Reasons for Deprecation

| Reason | Explanation |
|--------|-------------|
| **Driver Complexity** | Maintaining two pipelines doubled driver work |
| **Hardware Evolution** | New GPUs didn't map well to fixed concepts |
| **Developer Demand** | Games needed effects beyond fixed function |
| **Consistency** | Different vendors implemented fixed function differently |
| **Learning Curve** | Programmable model is more logical once learned |

### The Core Profile Decision

OpenGL 3.2 introduced **Core Profile**:

```
COMPATIBILITY PROFILE:
├─ All fixed function features retained
├─ Immediate mode (glBegin/glEnd)
├─ Display lists
└─ Works with legacy code

CORE PROFILE:
├─ Only programmable pipeline
├─ Modern features only
├─ Cleaner design
└─ Required for new OpenGL development
```

---

## Part 10: Modern Equivalent of Fixed Features

### What Replaced What

| Fixed Function Feature | Modern Equivalent |
|------------------------|-------------------|
| `glTranslate`, `glRotate`, `glScale` | Manual matrix math in shaders or GLM |
| `glLight`, `glMaterial` | Custom lighting in shaders |
| `glTexEnv` | Custom texture combining in shaders |
| `glFog` | Custom fog equations in fragment shader |
| `glAlphaFunc` | `discard` in fragment shader |
| `glColorMaterial` | Vertex attributes + shader logic |
| `glBegin`/`glEnd` | Vertex Buffer Objects (VBOs) |
| Display Lists | Vertex Buffer Objects (VBOs) |

### Implementing Fixed Function Effects in Modern OpenGL

```glsl
// Emulating fixed function texture modulation in shader
vec4 fixedFunctionModulate(vec4 texColor, vec4 vertexColor)
{
    // GL_MODULATE = texture * vertex color
    return texColor * vertexColor;
}

// Emulating fixed function lighting
vec3 fixedFunctionLight(
    vec3 normal, vec3 lightDir, vec3 lightColor,
    vec3 ambient, float shininess)
{
    float diff = max(dot(normal, lightDir), 0.0);
    // This is exactly what fixed function did
    return ambient + lightColor * diff;
}
```

---

## Part 11: Learning Path Considerations

### Should Beginners Learn Fixed Function?

**Arguments Against:**

| Reason | Detail |
|--------|--------|
| **Obsolete** | No new development uses fixed function |
| **Bad Habits** | Immediate mode encourages inefficient code |
| **Not Transferable** | Skills don't apply to other modern APIs |
| **Limited** | Can't do modern effects |

**Arguments For:**

| Reason | Detail |
|--------|--------|
| **Simplicity** | Easier first triangle |
| **Conceptual** | Understand what shaders replace |
| **Historical** | Context for modern design |

### Recommended Approach

```
Modern Learning Path (Recommended):
├─ Modern OpenGL (3.3+ Core Profile)
├─ Learn shaders immediately
├─ Understand fixed function only as history
└─ Build effects programmatically from start

Traditional Learning Path (Not Recommended):
├─ Fixed function first (1.x)
├─ Then migrate to shaders
├─ Unlearn old habits
└─ More time, confusing transition
```

---

## The 30-Second Summary

- **Fixed Pipeline** = Hardware-defined rendering stages, only configurable parameters
- **Programmable Pipeline** = Software-defined rendering via custom shader programs
- **Era** = Fixed (1992-2004), Transition (2004-2008), Programmable (2008-present)
- **Control** = Fixed: limited options, Programmable: unlimited possibilities
- **Flexibility** = Fixed: cannot create new effects, Programmable: any effect imaginable
- **Performance** = Fixed: optimized for common cases, Programmable: developer optimized
- **Modern Standard** = Core Profile (programmable only), Compatibility Profile (legacy support)

**The fixed pipeline gave training wheels. The programmable pipeline gives a rocket ship. Modern OpenGL expects developers to fly.**

---

