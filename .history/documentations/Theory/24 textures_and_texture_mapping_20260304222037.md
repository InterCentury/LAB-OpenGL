# Textures and Texture Mapping 

## The Wrapping Paper Analogy

Textures and texture mapping can be understood through gift wrapping:

- **The Gift Box** = The 3D model (cube, sphere, character)
- **The Wrapping Paper** = The texture image (2D picture)
- **The Alignment** = UV mapping (deciding where the paper goes)
- **The Tape** = Texture coordinates (holding the paper in place)
- **Folding at Corners** = Texture filtering (how the paper stretches)
- **Pattern Repetition** = Texture wrapping (when paper repeats)

**Just as wrapping paper transforms a plain box into a beautiful gift, textures transform simple 3D models into detailed, realistic objects.**

---

## Part 1: What is a Texture?

### Definition

A **texture** is a 2D image (or 1D/3D array) that is mapped onto a 3D surface to add visual detail without adding geometric complexity.

### Texture as Data

```
A TEXTURE IS A 2D ARRAY OF COLORS:

    U (horizontal) →
V   ┌─────────────────┐
↓   │ (0,0) ●     ●   │  Each cell = TEXEL (texture element)
    │                 │  Not pixel! A texel is a texture cell
    │    ●        ●   │  that gets sampled and possibly filtered
    │                 │  before becoming a pixel
    │ ●          ●    │
    └─────────────────┘

Resolution: width × height texels
Example: 512×512 texture = 262,144 texels
```

### Why Textures?

```
WITHOUT TEXTURE:                 WITH TEXTURE:
    ▲                                 ▲
   / \                               /█\
  /   \                             /███\
 /     \                           /█████\
/_______\                         /███████\

Plain color only                  Brick pattern, wood grain,
                                  detailed surfaces

Geometric detail requires         Visual detail from images,
thousands more triangles          no extra geometry!
```

---

## Part 2: Texture Coordinates (UVs)

### What are UV Coordinates?

**UV coordinates** define how a 2D texture maps onto a 3D surface. U is the horizontal axis, V is the vertical axis.

```
UV SPACE (0 to 1):
    U→
V   (0,0) ●──────● (1,0)
↓         |      |
          |      |
    (0,1) ●──────● (1,1)

Each vertex gets a UV coordinate:
- (0,0) = bottom-left of texture
- (1,0) = bottom-right
- (0,1) = top-left
- (1,1) = top-right
```

### UV Mapping Examples

```cpp
// Cube face with proper UV mapping
float cubeVertices[] = {
    // Position           // UV coordinates
    -0.5f, -0.5f, -0.5f,  0.0f, 0.0f,  // Bottom-left
     0.5f, -0.5f, -0.5f,  1.0f, 0.0f,  // Bottom-right
     0.5f,  0.5f, -0.5f,  1.0f, 1.0f,  // Top-right
     0.5f,  0.5f, -0.5f,  1.0f, 1.0f,  // Top-right
    -0.5f,  0.5f, -0.5f,  0.0f, 1.0f,  // Top-left
    -0.5f, -0.5f, -0.5f,  0.0f, 0.0f,  // Bottom-left
};

// UV values determine which part of texture each vertex gets
// Triangle interpolates UVs across its surface
```

### Visualizing UVs

```
UV MAPPING ON A CUBE:
    
    Front Face:          Back Face:
(0,1)━━━━(1,1)       (1,1)━━━━(0,1)
     ┃        ┃           ┃        ┃
     ┃  TEXT  ┃           ┃  TEXT  ┃
     ┃        ┃           ┃        ┃
    (0,0)━━━━(1,0)       (1,0)━━━━(0,0)

    Different faces can use different parts of the same texture
    or repeat the same UVs for tiled textures
```

---

## Part 3: Loading Textures

### Using STB Image (Recommended)

```cpp
// Include STB Image (single header library)
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

unsigned int loadTexture(const char* path) {
    unsigned int textureID;
    glGenTextures(1, &textureID);
    
    // Load image
    int width, height, nrChannels;
    unsigned char* data = stbi_load(path, &width, &height, &nrChannels, 0);
    
    if (data) {
        // Determine format based on channels
        GLenum format;
        if (nrChannels == 1)
            format = GL_RED;
        else if (nrChannels == 3)
            format = GL_RGB;
        else if (nrChannels == 4)
            format = GL_RGBA;
        
        // Bind texture
        glBindTexture(GL_TEXTURE_2D, textureID);
        
        // Upload texture data
        glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, 
                     GL_UNSIGNED_BYTE, data);
        
        // Generate mipmaps
        glGenerateMipmap(GL_TEXTURE_2D);
        
        // Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, 
                        GL_LINEAR_MIPMAP_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        
        stbi_image_free(data);
    } else {
        std::cout << "Failed to load texture: " << path << std::endl;
        stbi_image_free(data);
    }
    
    return textureID;
}
```

### Using Other Image Libraries

```cpp
// OpenCV
#include <opencv2/opencv.hpp>
cv::Mat img = cv::imread("texture.jpg", cv::IMREAD_COLOR);
cv::cvtColor(img, img, cv::COLOR_BGR2RGB);
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.cols, img.rows, 0, 
             GL_RGB, GL_UNSIGNED_BYTE, img.data);

// FreeImage
#include <FreeImage.h>
FIBITMAP* bitmap = FreeImage_Load(FIF_JPEG, "texture.jpg", 0);
BYTE* data = FreeImage_GetBits(bitmap);
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, FreeImage_GetWidth(bitmap),
             FreeImage_GetHeight(bitmap), 0, GL_BGR, GL_UNSIGNED_BYTE, data);

// DevIL
#include <IL/il.h>
ILuint imageID;
ilGenImages(1, &imageID);
ilBindImage(imageID);
ilLoadImage("texture.jpg");
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, ilGetInteger(IL_IMAGE_WIDTH),
             ilGetInteger(IL_IMAGE_HEIGHT), 0, GL_RGB, GL_UNSIGNED_BYTE,
             ilGetData());
```

---

## Part 4: Texture Parameters and Sampling

### Texture Wrapping Modes

```cpp
// How textures handle UV coordinates outside 0-1 range

glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);

// Available modes:
GL_REPEAT           // Repeat texture (default)
GL_MIRRORED_REPEAT  // Repeat with mirroring
GL_CLAMP_TO_EDGE    // Clamp to edge color
GL_CLAMP_TO_BORDER  // Use border color

// Visual effect:
GL_REPEAT:           GL_MIRRORED_REPEAT:
    [1][2][1][2]         [1][2][2][1]
    [3][4][3][4]         [3][4][4][3]
    
GL_CLAMP_TO_EDGE:    GL_CLAMP_TO_BORDER:
    [1][1][1][1]         [1][1][1][1]
    [1][1][1][1]         [1][1][1][1]
    [1][1][1][1]         [1][1][1][1]
                         [B][B][B][B]

// Set border color for GL_CLAMP_TO_BORDER
float borderColor[] = {1.0f, 0.0f, 0.0f, 1.0f};
glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor);
```

### Texture Filtering

```cpp
// How textures are sampled when magnified or minified

glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

// Minification filters (texture larger than on-screen area):
GL_NEAREST                // No mipmaps, nearest neighbor
GL_LINEAR                 // No mipmaps, linear interpolation
GL_NEAREST_MIPMAP_NEAREST // Mipmaps, nearest mipmap
GL_LINEAR_MIPMAP_NEAREST  // Mipmaps, linear between mipmap levels
GL_NEAREST_MIPMAP_LINEAR  // Mipmaps, nearest with interpolation
GL_LINEAR_MIPMAP_LINEAR   // Mipmaps, linear with interpolation (best)

// Magnification filters (texture smaller than on-screen area):
GL_NEAREST                // Pixelated look
GL_LINEAR                 // Smooth look (default)

// Visual comparison:
GL_NEAREST:               GL_LINEAR:
    ██  ██                    ██████
    ██  ██                    ██████
    Blocky/pixelated          Smooth/blurry
```

### Mipmapping

```cpp
// Mipmaps are pre-calculated, smaller versions of the texture
// They prevent aliasing and improve performance

// Original: 256x256
// Mip level 1: 128x128
// Mip level 2: 64x64
// Mip level 3: 32x32
// ... down to 1x1

// Generate mipmaps automatically
glGenerateMipmap(GL_TEXTURE_2D);

// Or generate manually
for (int level = 0; level < maxLevels; level++) {
    int mipWidth = width >> level;
    int mipHeight = height >> level;
    // Generate scaled image...
    glTexImage2D(GL_TEXTURE_2D, level, GL_RGB, mipWidth, mipHeight,
                 0, GL_RGB, GL_UNSIGNED_BYTE, scaledData);
}

// Set mipmap range
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 4);

// Set mipmap LOD bias (sharper or blurrier)
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_LOD_BIAS, -0.5f); // Sharper
```

---

## Part 5: Using Textures in Shaders

### Vertex Shader with UVs

```glsl
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

void main() {
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoord = aTexCoord;  // Pass UV to fragment shader
    
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
```

### Fragment Shader with Texture

```glsl
#version 330 core
in vec2 TexCoord;
in vec3 Normal;
in vec3 FragPos;

out vec4 FragColor;

uniform sampler2D ourTexture;  // Texture sampler
uniform vec3 lightPos;
uniform vec3 viewPos;

void main() {
    // Sample texture
    vec4 texColor = texture(ourTexture, TexCoord);
    
    // Simple lighting
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    
    // Combine
    FragColor = texColor * (0.5 + 0.5 * diff);
    
    // Or with ambient
    // FragColor = texColor * (0.2 + 0.8 * diff);
}
```

### Multiple Textures

```glsl
#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D texture1;
uniform sampler2D texture2;
uniform float mixValue;  // Blend factor

void main() {
    vec4 color1 = texture(texture1, TexCoord);
    vec4 color2 = texture(texture2, TexCoord);
    
    // Blend two textures
    FragColor = mix(color1, color2, mixValue);
    
    // Or multiply (lighting)
    // FragColor = color1 * color2;
    
    // Or add (emissive)
    // FragColor = color1 + color2;
}
```

### Setting Texture Units

```cpp
// In C++ code
glUseProgram(shaderProgram);

// Set texture units
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, texture1);
glUniform1i(glGetUniformLocation(shaderProgram, "texture1"), 0);

glActiveTexture(GL_TEXTURE1);
glBindTexture(GL_TEXTURE_2D, texture2);
glUniform1i(glGetUniformLocation(shaderProgram, "texture2"), 1);

// Now shader can access both textures
```

---

## Part 6: Texture Types

### 1D Textures

```cpp
// For gradients, data arrays
glBindTexture(GL_TEXTURE_1D, texture1D);
glTexImage1D(GL_TEXTURE_1D, 0, GL_RGB, width, 0, GL_RGB, GL_UNSIGNED_BYTE, data);

// Sampling in shader
uniform sampler1D tex1D;
float value = texture(tex1D, u).r;
```

### 2D Textures (Most Common)

```cpp
// Standard image textures
glBindTexture(GL_TEXTURE_2D, texture2D);
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
             GL_RGBA, GL_UNSIGNED_BYTE, data);

// Sampling
uniform sampler2D tex2D;
vec4 color = texture(tex2D, uv);
```

### 3D Textures

```cpp
// Volume textures, medical imaging, voxel games
glBindTexture(GL_TEXTURE_3D, texture3D);
glTexImage3D(GL_TEXTURE_3D, 0, GL_RGBA, width, height, depth, 0,
             GL_RGBA, GL_UNSIGNED_BYTE, data);

// Sampling requires 3D coordinates
uniform sampler3D tex3D;
vec4 color = texture(tex3D, vec3(u, v, w));
```

### Cube Maps

```cpp
// Skyboxes, environment mapping, reflection
glBindTexture(GL_TEXTURE_CUBE_MAP, cubeMap);

// Load 6 faces
for (int i = 0; i < 6; i++) {
    glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB,
                 width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, faceData[i]);
}

// Sampling requires direction vector
uniform samplerCube cubeMap;
vec4 color = texture(cubeMap, directionVector);
```

### Array Textures

```cpp
// Multiple textures in one object (texture atlases)
glBindTexture(GL_TEXTURE_2D_ARRAY, textureArray);
glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA, 
             width, height, layerCount, 0,
             GL_RGBA, GL_UNSIGNED_BYTE, nullptr);

// Upload each layer
for (int layer = 0; layer < layerCount; layer++) {
    glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 0, 0, layer,
                    width, height, 1, GL_RGBA, GL_UNSIGNED_BYTE, layerData[layer]);
}

// Sampling requires layer index
uniform sampler2DArray texArray;
vec4 color = texture(texArray, vec3(uv, layer));
```

---

## Part 7: Advanced Texture Mapping Techniques

### Normal Mapping

```glsl
// Store surface normals in texture (blue/purple look)
#version 330 core
in vec2 TexCoord;
in vec3 TangentLightPos;
in vec3 TangentViewPos;
in vec3 TangentFragPos;

uniform sampler2D diffuseMap;
uniform sampler2D normalMap;

void main() {
    // Sample normal from texture (convert 0-1 to -1-1)
    vec3 normal = texture(normalMap, TexCoord).rgb;
    normal = normalize(normal * 2.0 - 1.0);
    
    // Use this normal for lighting instead of vertex normal
    vec4 diffuse = texture(diffuseMap, TexCoord);
    
    // Lighting calculations with normal from texture
    // ... gives detailed surface appearance without extra geometry
}
```

### Parallax Mapping

```glsl
// Create illusion of depth by offsetting UV based on height
#version 330 core
in vec2 TexCoord;
in vec3 ViewDir;

uniform sampler2D diffuseMap;
uniform sampler2D heightMap;

void main() {
    float height = texture(heightMap, TexCoord).r;
    vec2 offset = ViewDir.xy * (height * 0.1);
    vec2 newTexCoord = TexCoord - offset;
    
    vec4 color = texture(diffuseMap, newTexCoord);
    FragColor = color;
}
```

### Displacement Mapping

```glsl
// Actually move vertices based on texture (in vertex shader)
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

uniform sampler2D displacementMap;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    float displacement = texture(displacementMap, aTexCoord).r;
    vec3 displacedPos = aPos + aNormal * displacement * scale;
    
    gl_Position = projection * view * model * vec4(displacedPos, 1.0);
}
```

---

## Part 8: Texture Compression and Formats

### Common Texture Formats

```cpp
// Unsigned byte (8-bit per channel) - most common
GL_RGB8, GL_RGBA8  // 24/32-bit color

// Float textures (HDR, lighting)
GL_RGB16F, GL_RGBA16F  // 16-bit float per channel
GL_RGB32F, GL_RGBA32F  // 32-bit float per channel

// Compressed formats
GL_COMPRESSED_RGB_S3TC_DXT1_EXT   // DXT1 (no alpha)
GL_COMPRESSED_RGBA_S3TC_DXT5_EXT  // DXT5 (alpha)
GL_COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT  // BPTC (HDR)

// Depth/stencil formats
GL_DEPTH_COMPONENT24  // 24-bit depth
GL_DEPTH24_STENCIL8   // 24-bit depth + 8-bit stencil
```

### When to Use Which Format

| Format | Use Case | Memory per 1024x1024 |
|--------|----------|---------------------|
| **RGB8** | Standard color | 3 MB |
| **RGBA8** | Color with alpha | 4 MB |
| **RGB16F** | HDR lighting | 6 MB |
| **DXT1** | Textures without alpha | 0.5 MB (6:1 compression) |
| **DXT5** | Textures with alpha | 1 MB (4:1 compression) |

### Checking for Compression Support

```cpp
GLint numFormats;
glGetIntegerv(GL_NUM_COMPRESSED_TEXTURE_FORMATS, &numFormats);

GLint* formats = new GLint[numFormats];
glGetIntegerv(GL_COMPRESSED_TEXTURE_FORMATS, formats);

for (int i = 0; i < numFormats; i++) {
    std::cout << "Supported format: 0x" << std::hex << formats[i] << std::endl;
}
```

---

## Part 9: Texture Parameters Reference

### Complete Parameter List

```cpp
// Wrap modes
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, mode);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, mode);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, mode); // 3D textures

// Filtering
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter);

// Mipmapping
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, levels);
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_LOD_BIAS, bias);
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_LOD, minLOD);
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_LOD, maxLOD);

// Border color (for GL_CLAMP_TO_BORDER)
float borderColor[] = {1.0f, 0.0f, 0.0f, 1.0f};
glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor);

// Comparison mode (for shadow maps)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, 
                GL_COMPARE_REF_TO_TEXTURE);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC, GL_LEQUAL);

// Swizzle (rearrange channels)
GLint swizzleMask[] = {GL_RED, GL_GREEN, GL_BLUE, GL_ALPHA};
glTexParameteriv(GL_TEXTURE_2D, GL_TEXTURE_SWIZZLE_RGBA, swizzleMask);
```

---

## Part 10: Performance Considerations

### Texture Memory Management

```cpp
// Calculate texture memory usage
size_t textureMemory = 0;
for (each texture) {
    size_t mipMemory = 0;
    for (int level = 0; level < mipLevels; level++) {
        int levelWidth = width >> level;
        int levelHeight = height >> level;
        mipMemory += levelWidth * levelHeight * bytesPerPixel;
    }
    textureMemory += mipMemory;
}

// At 4K textures with mipmaps: ~22 MB per texture
// 10 textures = 220 MB VRAM - can fill GPU memory quickly!
```

### Texture Streaming

```cpp
// For large worlds, load/unload textures dynamically
class TextureStreamer {
    std::map<std::string, Texture*> loadedTextures;
    
public:
    Texture* requestTexture(const std::string& path) {
        if (loadedTextures.find(path) == loadedTextures.end()) {
            // Check memory budget
            if (totalMemory > budget) {
                evictLeastUsed();  // Remove old textures
            }
            loadedTextures[path] = loadTexture(path);
        }
        return loadedTextures[path];
    }
};
```

### Texture Atlases

```cpp
// Combine multiple textures into one to reduce binds
// Instead of 10 textures:
for (int i = 0; i < 10; i++) {
    glBindTexture(GL_TEXTURE_2D, textures[i]);
    glDrawElements(...);  // 10 draw calls, 10 texture binds
}

// Use one texture atlas:
glBindTexture(GL_TEXTURE_2D, atlas);
for (int i = 0; i < 10; i++) {
    // Adjust UVs to point to correct sub-rectangle
    setUVsForSubRect(i);
    glDrawElements(...);  // Still 10 draws, but only 1 texture bind
}
```

---

## Part 11: Debugging Textures

### Visualizing UVs

```glsl
// Fragment shader to debug UV mapping
#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

void main() {
    // Visualize UVs directly
    FragColor = vec4(TexCoord.x, TexCoord.y, 0.0, 1.0);
    
    // Or with checkerboard pattern to see distortion
    float checker = mod(floor(TexCoord.x * 10.0) + 
                        floor(TexCoord.y * 10.0), 2.0);
    FragColor = vec4(vec3(checker), 1.0);
}
```

### Common Texture Problems

```cpp
// PROBLEM: Texture upside down
// Cause: OpenGL origin bottom-left, image formats top-left
// Fix 1: Flip Y in shader: TexCoord.y = 1.0 - TexCoord.y;
// Fix 2: Flip image when loading
stbi_set_flip_vertically_on_load(true);

// PROBLEM: Texture too dark/bright
// Cause: Color space issues (sRGB vs linear)
// Fix: Use sRGB texture format
glTexImage2D(GL_TEXTURE_2D, 0, GL_SRGB, width, height, 0,
             GL_RGB, GL_UNSIGNED_BYTE, data);

// PROBLEM: Texture blurry or pixelated
// Cause: Wrong filtering settings
// Fix: Set appropriate min/mag filters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

// PROBLEM: Texture seams at edges
// Cause: UV precision or wrapping issues
// Fix: Use correct wrap mode, ensure vertex UVs exactly match
```

### Debugging Texture Coordinates

```cpp
// Render wireframe with UV visualization
glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
// Draw object with debug shader
glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);

// Or render UV gradient
glBindTexture(GL_TEXTURE_2D, 0);  // No texture
// Use shader that outputs UVs as color
```

---

## Part 12: Practical Examples

### Example 1: Simple Textured Quad

```cpp
// Vertex data
float vertices[] = {
    // positions        // texture coords
     0.5f,  0.5f, 0.0f, 1.0f, 1.0f,  // top right
     0.5f, -0.5f, 0.0f, 1.0f, 0.0f,  // bottom right
    -0.5f, -0.5f, 0.0f, 0.0f, 0.0f,  // bottom left
    -0.5f,  0.5f, 0.0f, 0.0f, 1.0f   // top left
};

// Setup
unsigned int VAO, VBO;
glGenVertexArrays(1, &VAO);
glGenBuffers(1, &VBO);

glBindVertexArray(VAO);
glBindBuffer(GL_ARRAY_BUFFER, VBO);
glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

// Position attribute
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
glEnableVertexAttribArray(0);
// Texture coord attribute
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), 
                      (void*)(3 * sizeof(float)));
glEnableVertexAttribArray(1);

// Load texture
unsigned int texture = loadTexture("container.jpg");

// Render loop
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, texture);
glBindVertexArray(VAO);
glDrawArrays(GL_TRIANGLES, 0, 6);
```

### Example 2: Texture Blending

```glsl
// Fragment shader
#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D texture1;
uniform sampler2D texture2;
uniform float blendFactor;

void main() {
    vec4 color1 = texture(texture1, TexCoord);
    vec4 color2 = texture(texture2, TexCoord);
    FragColor = mix(color1, color2, blendFactor);
}
```

### Example 3: Animated Texture

```glsl
// Fragment shader with time-based UV offset
#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D texture1;
uniform float time;

void main() {
    // Animate UVs
    vec2 animatedUV = TexCoord + vec2(time * 0.1, 0.0);
    
    // Wrap manually (or use GL_REPEAT)
    animatedUV = fract(animatedUV);
    
    FragColor = texture(texture1, animatedUV);
}
```

---

## The 30-Second Summary

- **Texture** = 2D image mapped onto 3D surface
- **UV Coordinates** = (0-1) mapping of texture to vertices
- **Texel** = Texture element (pixel in texture space)
- **Sampling** = `texture(sampler, uv)` in shaders
- **Wrapping** = How texture repeats outside 0-1 (REPEAT, CLAMP, MIRROR)
- **Filtering** = How texture is scaled (NEAREST, LINEAR, mipmaps)
- **Mipmaps** = Pre-scaled versions for distant objects
- **Texture Units** = Multiple textures can be bound simultaneously
- **Formats** = RGB8, RGBA8, float, compressed (DXT, BPTC)

**Textures transform plain geometry into rich, detailed worlds - they're the difference between a wireframe and a photorealistic scene.**