# Shader Compilation and GLSL Basics 

## The Recipe Book Analogy

Shader compilation can be understood through a professional cookbook publishing process:

- **The Recipe Writer** = The developer writing GLSL code
- **The Recipe Manuscript** = The shader source code (text)
- **The Editor** = The GLSL compiler (checks for errors)
- **The Cookbook Compilation** = The shader program linking
- **The Published Book** = The linked shader program ready to use
- **The Head Chef** = The GPU executing the shader

**Writing a shader is like writing a recipe. Compilation checks for errors. Linking combines recipes into a complete menu. Then the GPU kitchen can finally cook with it.**

---

## Part 1: What is Shader Compilation?

### The Compilation Pipeline

```
SHADER SOURCE CODE (text files or strings in C++)
    ↓
[ GLSL COMPILER ]  →  Error messages if invalid
    ↓
COMPILED SHADER OBJECTS (binary form)
    ↓
[ LINKER ]  →  Error messages if incompatible
    ↓
SHADER PROGRAM (ready for GPU execution)
    ↓
[ GPU EXECUTION ] during rendering
```

### Why Compilation is Necessary

| Reason | Explanation |
|--------|-------------|
| **Hardware Differences** | Different GPUs need different machine code |
| **Optimization** | Compilers rearrange code for maximum performance |
| **Error Checking** | Catch mistakes before rendering |
| **Validation** | Ensure shaders follow GLSL rules |
| **Linking** | Connect vertex and fragment shaders together |

---

## Part 2: The Shader Compilation Process in Code

### Step-by-Step Implementation

```cpp
// 1. CREATE SHADER OBJECTS
GLuint vertexShader = glCreateShader(GL_VERTEX_SHADER);
GLuint fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);

// 2. PROVIDE SOURCE CODE
const char* vertexShaderSource = R"(
    #version 330 core
    layout (location = 0) in vec3 aPos;
    void main() {
        gl_Position = vec4(aPos, 1.0);
    }
)";

glShaderSource(vertexShader, 1, &vertexShaderSource, NULL);

// 3. COMPILE SHADER
glCompileShader(vertexShader);

// 4. CHECK COMPILATION STATUS
int success;
char infoLog[512];
glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);

if (!success) {
    glGetShaderInfoLog(vertexShader, 512, NULL, infoLog);
    std::cout << "Vertex shader compilation failed:\n" << infoLog << std::endl;
}

// 5. CREATE PROGRAM AND ATTACH SHADERS
GLuint shaderProgram = glCreateProgram();
glAttachShader(shaderProgram, vertexShader);
glAttachShader(shaderProgram, fragmentShader);

// 6. LINK PROGRAM
glLinkProgram(shaderProgram);

// 7. CHECK LINKING STATUS
glGetProgramiv(shaderProgram, GL_LINK_STATUS, &success);

if (!success) {
    glGetProgramInfoLog(shaderProgram, 512, NULL, infoLog);
    std::cout << "Shader linking failed:\n" << infoLog << std::endl;
}

// 8. USE THE PROGRAM
glUseProgram(shaderProgram);

// 9. CLEANUP (after linking)
glDeleteShader(vertexShader);
glDeleteShader(fragmentShader);
```

### Complete Function Example

```cpp
GLuint createShaderProgram(const char* vertexPath, const char* fragmentPath) {
    // Read shader files
    std::string vertexCode = readFile(vertexPath);
    std::string fragmentCode = readFile(fragmentPath);
    
    const char* vSource = vertexCode.c_str();
    const char* fSource = fragmentCode.c_str();
    
    // Compile vertex shader
    GLuint vertexShader = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vertexShader, 1, &vSource, NULL);
    glCompileShader(vertexShader);
    
    // Check vertex shader
    int success;
    char infoLog[512];
    glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(vertexShader, 512, NULL, infoLog);
        std::cout << "Vertex shader compilation failed:\n" << infoLog << std::endl;
        return 0;
    }
    
    // Compile fragment shader
    GLuint fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fragmentShader, 1, &fSource, NULL);
    glCompileShader(fragmentShader);
    
    // Check fragment shader
    glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(fragmentShader, 512, NULL, infoLog);
        std::cout << "Fragment shader compilation failed:\n" << infoLog << std::endl;
        return 0;
    }
    
    // Link program
    GLuint program = glCreateProgram();
    glAttachShader(program, vertexShader);
    glAttachShader(program, fragmentShader);
    glLinkProgram(program);
    
    // Check linking
    glGetProgramiv(program, GL_LINK_STATUS, &success);
    if (!success) {
        glGetProgramInfoLog(program, 512, NULL, infoLog);
        std::cout << "Shader linking failed:\n" << infoLog << std::endl;
        return 0;
    }
    
    // Cleanup
    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);
    
    return program;
}
```

---

## Part 3: GLSL Basics - Language Fundamentals

### Shader Structure

Every GLSL shader has a standard structure:

```glsl
#version 330 core  // Version declaration (MUST be first line)

// Inputs (vertex attributes for vertex shader)
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

// Uniforms (global variables)
uniform float time;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

// Outputs (to next stage)
out vec2 vTexCoord;

// Function declarations (optional)
float calculateBrightness(vec3 color);

void main() {  // Entry point (MUST exist)
    // Shader logic here
    vTexCoord = aTexCoord;
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}

// Function definitions
float calculateBrightness(vec3 color) {
    return dot(color, vec3(0.299, 0.587, 0.114));
}
```

### Version Declaration

```glsl
#version 330 core  // OpenGL 3.3, Core Profile

// Common versions:
#version 100        // OpenGL ES 2.0
#version 300 es     // OpenGL ES 3.0
#version 330 core   // OpenGL 3.3
#version 400 core   // OpenGL 4.0
#version 410 core   // OpenGL 4.1
#version 420 core   // OpenGL 4.2
#version 430 core   // OpenGL 4.3
#version 440 core   // OpenGL 4.4
#version 450 core   // OpenGL 4.5
#version 460 core   // OpenGL 4.6
```

**IMPORTANT:** The version declaration must be the **very first line** of the shader, with no comments or blank lines before it.

---

## Part 4: GLSL Data Types

### Basic Types

| Type | Description | Example |
|------|-------------|---------|
| `void` | No return value | `void main()` |
| `bool` | Boolean | `bool visible = true;` |
| `int` | Signed integer | `int count = 42;` |
| `uint` | Unsigned integer | `uint id = 100u;` |
| `float` | Floating point | `float weight = 3.14;` |
| `double` | Double precision | `double precise = 3.14159265359;` |

### Vector Types

| Type | Components | Accessors | Use Case |
|------|------------|-----------|----------|
| `vec2` | 2 floats | x, y | 2D coordinates, UVs |
| `vec3` | 3 floats | x, y, z | Positions, RGB colors |
| `vec4` | 4 floats | x, y, z, w | Homogeneous coordinates, RGBA |
| `ivec2` | 2 ints | x, y | Pixel coordinates |
| `ivec3` | 3 ints | x, y, z | 3D indices |
| `ivec4` | 4 ints | x, y, z, w | Bone IDs |
| `bvec2` | 2 bools | x, y | Boolean vectors |
| `uvec2` | 2 uints | x, y | Unsigned coordinates |

### Vector Operations

```glsl
vec3 a = vec3(1.0, 2.0, 3.0);
vec3 b = vec3(4.0, 5.0, 6.0);

// Component-wise operations
vec3 sum = a + b;        // (5.0, 7.0, 9.0)
vec3 diff = a - b;       // (-3.0, -3.0, -3.0)
vec3 product = a * b;    // (4.0, 10.0, 18.0)
vec3 quotient = a / b;   // (0.25, 0.4, 0.5)

// Swizzling (reordering components)
vec2 xy = a.xy;          // (1.0, 2.0)
vec3 yzx = a.yzx;        // (2.0, 3.0, 1.0)
vec4 expanded = a.xyyy;  // (1.0, 2.0, 2.0, 2.0)
vec2 reversed = a.yx;    // (2.0, 1.0)

// Masking (rgba for colors)
vec4 color = vec4(0.2, 0.4, 0.6, 1.0);
float red = color.r;      // 0.2
vec3 rgb = color.rgb;     // (0.2, 0.4, 0.6)
vec4 bgra = color.bgra;   // (0.6, 0.4, 0.2, 1.0)
```

### Matrix Types

| Type | Description | Use Case |
|------|-------------|----------|
| `mat2` | 2x2 matrix | 2D transformations |
| `mat3` | 3x3 matrix | Normal transformations |
| `mat4` | 4x4 matrix | 3D transformations (MVP) |
| `mat2x3` | 2 columns, 3 rows | Non-square matrices |

```glsl
// Matrix creation
mat4 identity = mat4(1.0);  // Identity matrix
mat3 rotation = mat3(
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 0.0, 1.0
);

// Matrix operations
vec4 transformed = projection * view * model * vec4(position, 1.0);
vec3 normal = mat3(transpose(inverse(model))) * originalNormal;
```

### Sampler Types

| Type | Description | Use Case |
|------|-------------|----------|
| `sampler1D` | 1D texture | Gradients, data arrays |
| `sampler2D` | 2D texture | Images, diffuse maps |
| `sampler3D` | 3D texture | Volume textures |
| `samplerCube` | Cube map | Skyboxes, environment maps |
| `sampler2DArray` | Array of 2D textures | Texture atlases |
| `sampler2DShadow` | Shadow map | Depth comparison |

```glsl
uniform sampler2D diffuseMap;
uniform samplerCube skybox;
uniform sampler2DShadow shadowMap;

void main() {
    vec4 color = texture(diffuseMap, texCoord);
    vec4 env = texture(skybox, direction);
    float shadow = texture(shadowMap, vec3(coord, depth));
}
```

---

## Part 5: GLSL Qualifiers

### Storage Qualifiers

| Qualifier | Location | Description |
|-----------|----------|-------------|
| `in` | Shader input | Receives data from previous stage |
| `out` | Shader output | Sends data to next stage |
| `uniform` | Global | Constant for entire draw call |
| `const` | Local | Compile-time constant |

```glsl
// Vertex shader
in vec3 aPos;              // From vertex buffer
out vec3 vColor;           // To fragment shader
uniform mat4 mvp;          // Global matrix
const float PI = 3.14159;  // Local constant
```

### Interpolation Qualifiers (for fragment shader inputs)

| Qualifier | Description |
|-----------|-------------|
| `smooth` | Perspective-correct interpolation (default) |
| `flat` | No interpolation (takes first vertex value) |
| `noperspective` | Linear interpolation in screen space |

```glsl
// Vertex shader
smooth out vec2 vTexCoord;      // Default, smooth interpolation
flat out vec3 vFaceColor;       // Same for entire triangle
noperspective out vec2 vScreenPos; // Linear in screen space

// Fragment shader
smooth in vec2 vTexCoord;
flat in vec3 vFaceColor;
noperspective in vec2 vScreenPos;
```

### Layout Qualifiers

```glsl
// Attribute locations
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;

// Fragment output locations (for MRT)
layout (location = 0) out vec4 colorBuffer;
layout (location = 1) out vec4 normalBuffer;

// Uniform block layout
layout (std140) uniform Matrices {
    mat4 projection;
    mat4 view;
    vec4 cameraPos;
};

// Shader storage buffer layout
layout (std430, binding = 0) buffer Data {
    vec4 positions[];
};
```

---

## Part 6: Built-in Variables

### Vertex Shader Built-ins

| Variable | Type | Description |
|----------|------|-------------|
| `gl_Position` | `vec4` | Output position (must be written) |
| `gl_PointSize` | `float` | Point size for point primitives |
| `gl_VertexID` | `int` | Index of current vertex |
| `gl_InstanceID` | `int` | Instance index for instancing |

```glsl
void main() {
    gl_Position = mvp * vec4(aPos, 1.0);  // REQUIRED
    gl_PointSize = 5.0;                   // Optional
    
    // Use IDs for effects
    float offset = float(gl_VertexID) * 0.01;
    vec3 animatedPos = aPos + vec3(offset, 0.0, 0.0);
}
```

### Fragment Shader Built-ins

| Variable | Type | Description |
|----------|------|-------------|
| `gl_FragCoord` | `vec4` | Screen coordinates (x,y) and depth (z) |
| `gl_FrontFacing` | `bool` | True for front faces |
| `gl_PointCoord` | `vec2` | Within-point coordinates (0-1) |
| `gl_PrimitiveID` | `int` | Current primitive index |
| `gl_FragDepth` | `float` | Optional depth output |
| `gl_SampleID` | `int` | Sample number for MSAA |
| `gl_SamplePosition` | `vec2` | Sample position within pixel |

```glsl
void main() {
    // Screen position effects
    vec2 screenUV = gl_FragCoord.xy / resolution;
    
    // Two-sided rendering
    if (gl_FrontFacing) {
        color = frontColor;
    } else {
        color = backColor;
    }
    
    // Point sprite texture coordinates
    vec2 spriteUV = gl_PointCoord;
    
    // Optional depth modification (disables early Z)
    gl_FragDepth = gl_FragCoord.z - 0.01;
}
```

---

## Part 7: GLSL Functions

### Built-in Functions

| Category | Functions |
|----------|-----------|
| **Trigonometric** | `sin()`, `cos()`, `tan()`, `asin()`, `acos()`, `atan()` |
| **Exponential** | `pow()`, `exp()`, `log()`, `exp2()`, `log2()`, `sqrt()`, `inversesqrt()` |
| **Common** | `abs()`, `sign()`, `floor()`, `ceil()`, `fract()`, `mod()`, `min()`, `max()`, `clamp()` |
| **Geometric** | `dot()`, `cross()`, `normalize()`, `reflect()`, `refract()`, `distance()`, `length()` |
| **Matrix** | `transpose()`, `determinant()`, `inverse()` |
| **Vector Relational** | `lessThan()`, `greaterThan()`, `equal()`, `any()`, `all()` |
| **Texture** | `texture()`, `textureLod()`, `textureProj()`, `texelFetch()` |
| **Derivatives** | `dFdx()`, `dFdy()`, `fwidth()` |

### Function Examples

```glsl
// Normalize a vector
vec3 norm = normalize(surfaceNormal);

// Calculate distance between points
float dist = distance(pointA, pointB);

// Mix between two values (lerp)
float t = 0.5;
vec3 blended = mix(colorA, colorB, t);

// Clamp value to range
float brightness = clamp(lighting, 0.0, 1.0);

// Smoothstep for anti-aliased edges
float edge = smoothstep(0.4, 0.6, texCoord.x);

// Reflect vector (for specular)
vec3 reflection = reflect(incident, normal);

// Fract for repeating patterns
vec2 repeatedUV = fract(texCoord * 5.0);
```

### User-Defined Functions

```glsl
// Function declaration
float calculateAttenuation(float distance, float constant, float linear, float quadratic) {
    return 1.0 / (constant + linear * distance + quadratic * distance * distance);
}

// Function with out parameters
void decomposeColor(vec4 color, out float hue, out float saturation, out float value) {
    // Convert RGB to HSV
    float maxComp = max(color.r, max(color.g, color.b));
    float minComp = min(color.r, min(color.g, color.b));
    value = maxComp;
    
    if (maxComp != 0.0) {
        saturation = (maxComp - minComp) / maxComp;
    } else {
        saturation = 0.0;
    }
    
    // Hue calculation...
}

void main() {
    float atten = calculateAttenuation(distance, 1.0, 0.1, 0.01);
    
    float h, s, v;
    decomposeColor(diffuseColor, h, s, v);
}
```

---

## Part 8: Control Flow

### Conditionals

```glsl
// if-else (can cause divergence)
if (intensity > 0.5) {
    color = brightColor;
} else if (intensity > 0.2) {
    color = mediumColor;
} else {
    color = darkColor;
}

// switch statements (less common)
switch (materialType) {
    case 0:
        color = metalColor;
        break;
    case 1:
        color = plasticColor;
        break;
    default:
        color = defaultColor;
}

// Ternary operator (often optimized better)
color = (intensity > 0.5) ? brightColor : darkColor;
```

### Loops

```glsl
// for loop (must have compile-time constant limits typically)
for (int i = 0; i < 5; i++) {
    sum += samples[i];
}

// while loop
int i = 0;
while (i < 5) {
    sum += samples[i];
    i++;
}

// do-while loop
int i = 0;
do {
    sum += samples[i];
    i++;
} while (i < 5);

// Loop with break/continue
for (int i = 0; i < 10; i++) {
    if (i == 3) continue;  // Skip iteration
    if (sum > threshold) break;  // Exit loop
    sum += data[i];
}
```

**Performance Note:** Loops in shaders should have compile-time constant bounds when possible. Dynamic loops can be slow.

---

## Part 9: Shader Compilation Errors

### Common Compilation Errors

```glsl
// ERROR: Missing version declaration
void main() { }  // Version must be first line!

// ERROR: Wrong version syntax
#version 330  // Missing 'core' - should be "#version 330 core"

// ERROR: Type mismatch
vec4 color = 1.0;  // Cannot convert float to vec4
vec4 color = vec4(1.0);  // Correct

// ERROR: Undeclared variable
color = vec4(1.0);  // 'color' not declared
vec4 color = vec4(1.0);  // Correct

// ERROR: Mismatched input/output
// Vertex shader:
out vec3 vColor;
// Fragment shader:
in vec4 vColor;  // Type mismatch!

// ERROR: Writing to gl_Position in fragment shader
// (gl_Position only available in vertex shader)

// ERROR: Using texture without sampler
uniform vec4 myTexture;  // Wrong type!
uniform sampler2D myTexture;  // Correct
```

### Reading Compiler Output

```
Example error message:
0:12(20): error: 'assign' : cannot convert from 'float' to 'vec4'

Breakdown:
0:12        → Line 12
(20)        → Column 20
'assign'    → Operation type (assignment)
cannot convert from 'float' to 'vec4' → Problem description
```

### Debugging Tips

```cpp
// Always check compilation status
glCompileShader(shader);
glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
if (!success) {
    char infoLog[512];
    glGetShaderInfoLog(shader, 512, NULL, infoLog);
    
    // Print line numbers for easier debugging
    std::cout << "Shader compilation failed at line " 
              << extractLineNumber(infoLog) << ":\n"
              << infoLog << std::endl;
              
    // Print the shader source with line numbers
    printShaderSourceWithLineNumbers(source);
}
```

---

## Part 10: Uniforms and Attributes

### Setting Uniforms from C++

```cpp
// Get uniform location
GLint uniformLoc = glGetUniformLocation(program, "uniformName");

// Set different types
glUniform1f(uniformLoc, 3.14f);                    // float
glUniform2f(uniformLoc, 0.5f, 0.5f);               // vec2
glUniform3f(uniformLoc, 1.0f, 0.0f, 0.0f);         // vec3
glUniform4f(uniformLoc, 1.0f, 0.0f, 0.0f, 1.0f);   // vec4

glUniform1i(uniformLoc, 42);                        // int
glUniform1ui(uniformLoc, 100u);                      // uint

// Vectors from arrays
float values[3] = {1.0f, 2.0f, 3.0f};
glUniform3fv(uniformLoc, 1, values);                 // vec3 array

// Matrices
glUniformMatrix4fv(uniformLoc, 1, GL_FALSE, glm::value_ptr(matrix));

// Samplers (texture units)
glUniform1i(uniformLoc, 0);  // Use texture unit 0
```

### Uniform Blocks

```cpp
// GLSL side
layout (std140) uniform Matrices {
    mat4 projection;
    mat4 view;
    vec4 cameraPosition;
    float nearPlane;
    float farPlane;
};

// C++ side
GLuint ubo;
glGenBuffers(1, &ubo);
glBindBuffer(GL_UNIFORM_BUFFER, ubo);
glBufferData(GL_UNIFORM_BUFFER, sizeof(Matrices), NULL, GL_DYNAMIC_DRAW);
glBindBufferBase(GL_UNIFORM_BUFFER, 0, ubo);  // Bind to binding point 0

// Update data
glBindBuffer(GL_UNIFORM_BUFFER, ubo);
glBufferSubData(GL_UNIFORM_BUFFER, 0, sizeof(Matrices), &matricesData);
```

---

## Part 11: Shader Storage Buffers (SSBO)

### SSBO Example

```glsl
// GLSL side
layout (std430, binding = 0) buffer ParticleData {
    vec4 positions[];
    vec4 velocities[];
    float lifetimes[];
};

void main() {
    int idx = gl_VertexID;
    positions[idx] += velocities[idx] * deltaTime;
    
    if (lifetimes[idx] <= 0.0) {
        // Reset particle
        positions[idx] = vec4(0.0);
        lifetimes[idx] = 1.0;
    }
}
```

```cpp
// C++ side
struct Particle {
    glm::vec4 position;
    glm::vec4 velocity;
    float lifetime;
};

GLuint ssbo;
glGenBuffers(1, &ssbo);
glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo);
glBufferData(GL_SHADER_STORAGE_BUFFER, 
             sizeof(Particle) * MAX_PARTICLES, 
             particles, 
             GL_DYNAMIC_DRAW);
glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, ssbo);
```

---

## Part 12: Best Practices

### Code Organization

```glsl
// 1. Always start with version
#version 330 core

// 2. Group inputs by type
// Inputs
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;

// Uniforms (grouped by frequency)
// Per-frame uniforms
uniform mat4 view;
uniform mat4 projection;
uniform vec3 cameraPos;

// Per-object uniforms
uniform mat4 model;
uniform vec4 color;

// Samplers
uniform sampler2D diffuseMap;
uniform sampler2D specularMap;

// Outputs
out vec2 vTexCoord;
out vec3 vNormal;
out vec3 vFragPos;

// Constants
const float PI = 3.14159265359;
const float GAMMA = 2.2;

// Helper functions
float calculateLuminance(vec3 color) {
    return dot(color, vec3(0.299, 0.587, 0.114));
}

// Main function
void main() {
    // Shader logic
}
```

### Performance Tips

```glsl
// BAD: Expensive operation in every fragment
for (int i = 0; i < lightCount; i++) {
    // Complex lighting for many lights
}

// GOOD: Pre-compute what you can
// (if lightCount is uniform, this is fine)

// BAD: Dynamic branching causing divergence
if (gl_FragCoord.x > 500.0) {
    // Complex path A
} else {
    // Complex path B
}

// GOOD: Coherent branching (likely same for nearby pixels)

// BAD: Texture lookups in conditionals
if (condition) {
    color = texture(tex1, uv);  // Different texture paths
} else {
    color = texture(tex2, uv);
}

// GOOD: Single texture lookup with mix
vec4 c1 = texture(tex1, uv);
vec4 c2 = texture(tex2, uv);
color = mix(c2, c1, float(condition));
```

---

## The 30-Second Summary

- **Shader Compilation** = Process of converting GLSL text to GPU-executable code
- **Steps** = Create → Source → Compile → Attach → Link → Use
- **GLSL** = C-like language with vector/matrix types and graphics-specific functions
- **Data Types** = Vectors (vec2/3/4), Matrices (mat2/3/4), Samplers (texture2D)
- **Qualifiers** = in, out, uniform, const, layout
- **Built-ins** = gl_Position (VS), gl_FragCoord (FS), gl_FragColor
- **Error Handling** = Always check compilation and linking status
- **Best Practices** = Group uniforms, use std140 layout, minimize divergence

**Shader compilation transforms human-readable code into GPU machine code, with GLSL providing a specialized language for graphics programming.**

---

**Next Step:** Ready to understand how to pass data between shaders?