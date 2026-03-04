# What is a Framebuffer? - Beginner's Documentation

## The Artist's Canvas Analogy

A framebuffer can be understood through an artist's studio with multiple canvases:

- **The Main Canvas** = The default framebuffer (what you see on screen)
- **Sketch Pads** = Off-screen framebuffers (for intermediate drawings)
- **Layered Art** = Multiple render targets (color, normals, depth all separate)
- **The Easel** = The GPU (where the painting happens)
- **The Gallery Wall** = Your monitor (where final art is displayed)

**Just as an artist might sketch on separate paper before combining elements onto the final canvas, a graphics programmer uses framebuffers to render scenes in multiple passes before showing the final result.**

---

## Part 1: What is a Framebuffer?

### Definition

A **framebuffer** is a collection of memory buffers (color, depth, stencil) that together represent a complete render target. It's the destination where all rendering operations write their results.

### The Default Framebuffer

```cpp
// When you create a window, OpenGL automatically creates a default framebuffer
// This is what you've been using all along!

// Clear the default framebuffer
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

// Draw to default framebuffer
glDrawArrays(GL_TRIANGLES, 0, 3);

// Swap buffers to display on screen
glfwSwapBuffers(window);
```

### Visual Representation

```
DEFAULT FRAMEBUFFER (on-screen):
┌─────────────────────────────────────┐
│                                     │
│         WHAT YOU SEE ON             │
│           YOUR MONITOR               │
│                                     │
│    Color   Depth   Stencil          │
│    Buffer  Buffer  Buffer           │
│     (RGB)   (Z)     (S)             │
└─────────────────────────────────────┘

OFF-SCREEN FRAMEBUFFER (invisible):
┌─────────────────────────────────────┐
│                                     │
│      INTERMEDIATE RENDERING         │
│           PASSES                    │
│                                     │
│    Used for shadows, reflections,   │
│    post-processing, etc.            │
└─────────────────────────────────────┘
```

---

## Part 2: Framebuffer Components

### The Three Essential Attachments

```cpp
struct Framebuffer {
    // Color attachment(s) - stores pixel colors
    Texture2D* colorBuffer;     // RGB/RGBA
    
    // Depth attachment - stores distance from camera
    Renderbuffer* depthBuffer;   // 24-bit depth
    
    // Stencil attachment - stores masks for effects
    Renderbuffer* stencilBuffer; // 8-bit stencil
    
    // Optional: Multiple color attachments for MRT
    Texture2D* colorBuffers[8];  // Up to 8 simultaneous outputs
};
```

### Color Buffer

```cpp
// Stores the actual colors of the rendered image
// What you normally see

// Clear color
glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
glClear(GL_COLOR_BUFFER_BIT);

// Multiple color buffers (MRT)
GLenum drawBuffers[] = { GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1 };
glDrawBuffers(2, drawBuffers);

// In fragment shader:
layout (location = 0) out vec4 colorBuffer;   // To attachment 0
layout (location = 1) out vec4 normalBuffer;  // To attachment 1
```

### Depth Buffer

```cpp
// Stores distance from camera for each pixel
// Used for visibility determination

// Enable depth testing
glEnable(GL_DEPTH_TEST);

// Clear depth
glClear(GL_DEPTH_BUFFER_BIT);

// Depth buffer format options:
// GL_DEPTH_COMPONENT16  - 16-bit (low precision)
// GL_DEPTH_COMPONENT24  - 24-bit (standard)
// GL_DEPTH_COMPONENT32  - 32-bit (high precision)
// GL_DEPTH24_STENCIL8   - 24-bit depth + 8-bit stencil
```

### Stencil Buffer

```cpp
// Stores per-pixel masks for advanced effects
// Used for: portals, mirrors, outlining, decals

// Enable stencil testing
glEnable(GL_STENCIL_TEST);

// Clear stencil
glClear(GL_STENCIL_BUFFER_BIT);

// Common stencil operations:
glStencilFunc(GL_EQUAL, 1, 0xFF);     // Pass if stencil == 1
glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE);  // Replace on pass
glStencilMask(0xFF);                   // Allow writing to all bits
```

---

## Part 3: Creating a Custom Framebuffer

### Step-by-Step Implementation

```cpp
// 1. Generate framebuffer object
unsigned int fbo;
glGenFramebuffers(1, &fbo);
glBindFramebuffer(GL_FRAMEBUFFER, fbo);

// 2. Create color texture attachment
unsigned int texColorBuffer;
glGenTextures(1, &texColorBuffer);
glBindTexture(GL_TEXTURE_2D, texColorBuffer);
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, 
             GL_RGB, GL_UNSIGNED_BYTE, NULL);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                       GL_TEXTURE_2D, texColorBuffer, 0);

// 3. Create depth/stencil renderbuffer
unsigned int rbo;
glGenRenderbuffers(1, &rbo);
glBindRenderbuffer(GL_RENDERBUFFER, rbo);
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height);
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT,
                          GL_RENDERBUFFER, rbo);

// 4. Check if framebuffer is complete
if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
    std::cout << "Framebuffer not complete!" << std::endl;
}

// 5. Unbind to return to default
glBindFramebuffer(GL_FRAMEBUFFER, 0);
```

### Framebuffer Status Checks

```cpp
GLenum status = glCheckFramebufferStatus(GL_FRAMEBUFFER);

switch(status) {
    case GL_FRAMEBUFFER_COMPLETE:
        // All good!
        break;
    case GL_FRAMEBUFFER_UNDEFINED:
        std::cout << "Framebuffer undefined" << std::endl;
        break;
    case GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
        std::cout << "Incomplete attachment" << std::endl;
        break;
    case GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
        std::cout << "Missing attachment" << std::endl;
        break;
    case GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER:
        std::cout << "Incomplete draw buffer" << std::endl;
        break;
    case GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER:
        std::cout << "Incomplete read buffer" << std::endl;
        break;
    case GL_FRAMEBUFFER_UNSUPPORTED:
        std::cout << "Unsupported format" << std::endl;
        break;
    case GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE:
        std::cout << "Incomplete multisample" << std::endl;
        break;
}
```

---

## Part 4: Renderbuffers vs Textures

### Comparison

| Aspect | Renderbuffer | Texture |
|--------|--------------|---------|
| **Purpose** | Off-screen rendering only | Can be sampled in shaders |
| **Access** | Cannot read in shaders | Can be read via `texture()` |
| **Performance** | Faster for depth/stencil | Slightly slower |
| **Use Case** | Depth buffers, stencil | Color buffers for post-processing |
| **Memory** | Optimized for rendering | Optimized for sampling |

### When to Use Each

```cpp
// USE RENDERBUFFER FOR:
// Depth buffer (no need to sample)
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, width, height);

// Stencil buffer (no need to sample)
glRenderbufferStorage(GL_RENDERBUFFER, GL_STENCIL_INDEX8, width, height);

// Combined depth+stencil (most common)
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height);

// USE TEXTURE FOR:
// Color buffer (need to sample for post-processing)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, 
             GL_RGB, GL_UNSIGNED_BYTE, NULL);

// Depth texture (for shadow mapping)
glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, width, height, 0,
             GL_DEPTH_COMPONENT, GL_FLOAT, NULL);
```

---

## Part 5: Multiple Render Targets (MRT)

### What is MRT?

**Multiple Render Targets** allow a fragment shader to output to several color buffers simultaneously.

```cpp
// Setup multiple color attachments
unsigned int colorBuffers[3];
glGenTextures(3, colorBuffers);

for (int i = 0; i < 3; i++) {
    glBindTexture(GL_TEXTURE_2D, colorBuffers[i]);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, width, height, 0,
                 GL_RGB, GL_FLOAT, NULL);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + i,
                           GL_TEXTURE_2D, colorBuffers[i], 0);
}

// Specify which attachments to draw to
GLenum attachments[3] = { 
    GL_COLOR_ATTACHMENT0, 
    GL_COLOR_ATTACHMENT1, 
    GL_COLOR_ATTACHMENT2 
};
glDrawBuffers(3, attachments);
```

### Fragment Shader for MRT

```glsl
#version 330 core

// Multiple outputs
layout (location = 0) out vec4 colorBuffer;   // Albedo
layout (location = 1) out vec4 normalBuffer;  // Normals
layout (location = 2) out vec4 positionBuffer;// World positions

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

uniform sampler2D diffuseTexture;

void main() {
    // Output to multiple buffers simultaneously
    colorBuffer = texture(diffuseTexture, TexCoord);  // Color
    normalBuffer = vec4(Normal * 0.5 + 0.5, 1.0);     // Normals
    positionBuffer = vec4(FragPos, 1.0);               // Positions
}
```

### Deferred Shading with MRT

```cpp
// PASS 1: Geometry pass - fill G-buffer
glBindFramebuffer(GL_FRAMEBUFFER, gBuffer);
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
renderScene();  // Writes to color, normal, position buffers

// PASS 2: Lighting pass - use G-buffer textures
glBindFramebuffer(GL_FRAMEBUFFER, 0);
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

// Bind G-buffer textures
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, gColor);
glActiveTexture(GL_TEXTURE1);
glBindTexture(GL_TEXTURE_2D, gNormal);
glActiveTexture(GL_TEXTURE2);
glBindTexture(GL_TEXTURE_2D, gPosition);

// Render fullscreen quad with lighting shader
renderFullscreenQuad();
```

---

## Part 6: Common Framebuffer Effects

### 1. Post-Processing Pipeline

```cpp
// Setup
unsigned int mainFBO, postFBO;
unsigned int sceneTexture, processedTexture;

// PASS 1: Render scene to texture
glBindFramebuffer(GL_FRAMEBUFFER, mainFBO);
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
renderScene();

// PASS 2: Apply first effect (e.g., blur)
glBindFramebuffer(GL_FRAMEBUFFER, postFBO);
glClear(GL_COLOR_BUFFER_BIT);
blurShader.use();
glBindTexture(GL_TEXTURE_2D, sceneTexture);
renderFullscreenQuad();

// PASS 3: Apply second effect (e.g., color grading)
glBindFramebuffer(GL_FRAMEBUFFER, 0);
glClear(GL_COLOR_BUFFER_BIT);
colorGradingShader.use();
glBindTexture(GL_TEXTURE_2D, processedTexture);
renderFullscreenQuad();
```

### 2. Shadow Mapping

```cpp
// PASS 1: Render depth from light's perspective
glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO);
glClear(GL_DEPTH_BUFFER_BIT);
glViewport(0, 0, shadowMapSize, shadowMapSize);
renderSceneFromLight();

// PASS 2: Render scene from camera, using shadow map
glBindFramebuffer(GL_FRAMEBUFFER, 0);
glViewport(0, 0, screenWidth, screenHeight);
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, depthMap);
mainShader.use();
// Set light space matrix uniform
renderScene();
```

### 3. Mirror/Portal Effect

```cpp
// PASS 1: Render scene from mirror's perspective
glBindFramebuffer(GL_FRAMEBUFFER, mirrorFBO);
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

// Set camera to mirror position/direction
glm::mat4 mirrorView = calculateMirrorView(camera, mirrorPlane);
setViewMatrix(mirrorView);

renderScene();  // Render to mirror texture

// PASS 2: Render main scene with mirror texture
glBindFramebuffer(GL_FRAMEBUFFER, 0);
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
setViewMatrix(cameraView);
renderScene();

// Draw mirror quad with mirror texture
glBindTexture(GL_TEXTURE_2D, mirrorTexture);
drawMirrorQuad();
```

---

## Part 7: Fullscreen Quad Technique

### The Fullscreen Quad

```cpp
// Simple quad that covers the entire screen
float quadVertices[] = {
    // positions   // texCoords
    -1.0f,  1.0f,  0.0f, 1.0f,
    -1.0f, -1.0f,  0.0f, 0.0f,
     1.0f, -1.0f,  1.0f, 0.0f,

    -1.0f,  1.0f,  0.0f, 1.0f,
     1.0f, -1.0f,  1.0f, 0.0f,
     1.0f,  1.0f,  1.0f, 1.0f
};

// Setup VAO, VBO (once)
unsigned int quadVAO, quadVBO;
glGenVertexArrays(1, &quadVAO);
glGenBuffers(1, &quadVBO);
glBindVertexArray(quadVAO);
glBindBuffer(GL_ARRAY_BUFFER, quadVBO);
glBufferData(GL_ARRAY_BUFFER, sizeof(quadVertices), &quadVertices, GL_STATIC_DRAW);
glEnableVertexAttribArray(0);
glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)0);
glEnableVertexAttribArray(1);
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)(2 * sizeof(float)));

// Render fullscreen quad
glBindVertexArray(quadVAO);
glDrawArrays(GL_TRIANGLES, 0, 6);
```

### Simple Post-Processing Shader

```glsl
#version 330 core
out vec4 FragColor;

in vec2 TexCoord;

uniform sampler2D screenTexture;
uniform float time;

void main() {
    vec4 color = texture(screenTexture, TexCoord);
    
    // Invert colors
    vec4 inverted = vec4(1.0 - color.rgb, color.a);
    
    // Grayscale
    float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    vec4 grayscale = vec4(gray, gray, gray, color.a);
    
    // Sharpen kernel
    vec2 texelSize = 1.0 / textureSize(screenTexture, 0);
    vec4 sharpen = color * 2.0;
    sharpen -= texture(screenTexture, TexCoord + vec2( texelSize.x, 0.0));
    sharpen -= texture(screenTexture, TexCoord + vec2(-texelSize.x, 0.0));
    sharpen -= texture(screenTexture, TexCoord + vec2( 0.0, texelSize.y));
    sharpen -= texture(screenTexture, TexCoord + vec2( 0.0,-texelSize.y));
    
    // Output desired effect
    FragColor = grayscale;  // or inverted, sharpen, etc.
}
```

---

## Part 8: Advanced Framebuffer Techniques

### HDR and Tone Mapping

```cpp
// Create HDR framebuffer with floating point texture
glBindTexture(GL_TEXTURE_2D, hdrTexture);
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, width, height, 0,
             GL_RGBA, GL_FLOAT, NULL);

// Render scene to HDR buffer (values > 1.0 possible)
glBindFramebuffer(GL_FRAMEBUFFER, hdrFBO);
renderScene();

// Tone mapping pass to convert HDR to LDR for display
glBindFramebuffer(GL_FRAMEBUFFER, 0);
toneMappingShader.use();
glBindTexture(GL_TEXTURE_2D, hdrTexture);
renderFullscreenQuad();
```

```glsl
// Tone mapping shader
#version 330 core
out vec4 FragColor;
in vec2 TexCoord;
uniform sampler2D hdrBuffer;
uniform float exposure;

void main() {
    vec3 hdrColor = texture(hdrBuffer, TexCoord).rgb;
    
    // Reinhard tone mapping
    vec3 mapped = hdrColor / (hdrColor + vec3(1.0));
    
    // Exposure tone mapping
    vec3 exposed = vec3(1.0) - exp(-hdrColor * exposure);
    
    FragColor = vec4(exposed, 1.0);
}
```

### Bloom Effect

```cpp
// PASS 1: Render scene to HDR buffer
glBindFramebuffer(GL_FRAMEBUFFER, hdrFBO);
renderScene();

// PASS 2: Extract bright areas
glBindFramebuffer(GL_FRAMEBUFFER, brightFBO);
brightShader.use();
glBindTexture(GL_TEXTURE_2D, hdrColorTexture);
renderFullscreenQuad();

// PASS 3: Gaussian blur bright texture (horizontal)
glBindFramebuffer(GL_FRAMEBUFFER, blurFBO1);
blurHorizontalShader.use();
glBindTexture(GL_TEXTURE_2D, brightTexture);
renderFullscreenQuad();

// PASS 4: Gaussian blur (vertical)
glBindFramebuffer(GL_FRAMEBUFFER, blurFBO2);
blurVerticalShader.use();
glBindTexture(GL_TEXTURE_2D, blurTexture1);
renderFullscreenQuad();

// PASS 5: Combine with original scene
glBindFramebuffer(GL_FRAMEBUFFER, 0);
combineShader.use();
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, hdrColorTexture);
glActiveTexture(GL_TEXTURE1);
glBindTexture(GL_TEXTURE_2D, blurTexture2);
renderFullscreenQuad();
```

---

## Part 9: Performance Considerations

### Memory Usage

```cpp
// Calculate framebuffer memory
size_t calculateFramebufferMemory(int width, int height, int attachments) {
    size_t total = 0;
    
    // Color attachments (4 bytes per pixel for RGBA8)
    total += width * height * 4 * attachments;
    
    // Depth-stencil attachment (4 bytes per pixel for 24+8)
    total += width * height * 4;
    
    return total;  // In bytes
}

// 1080p with 3 color attachments:
// 1920*1080*4*3 = 24.9 MB for color
// 1920*1080*4 = 8.3 MB for depth/stencil
// Total: ~33 MB per framebuffer
```

### Optimization Tips

```cpp
// 1. Reuse framebuffers when possible
// Don't create new FBOs each frame

// 2. Minimize framebuffer switches
glBindFramebuffer(GL_FRAMEBUFFER, fbo1);
// Do all rendering to fbo1
glBindFramebuffer(GL_FRAMEBUFFER, fbo2);
// Do all rendering to fbo2

// 3. Use appropriate resolutions
// Shadow maps can be lower resolution
glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, 
             1024, 1024, ...);  // Not full screen

// 4. Clear only what's needed
glClear(GL_COLOR_BUFFER_BIT);  // If depth hasn't changed

// 5. Use glInvalidateFramebuffer for tiles not needed
GLenum attachments[] = { GL_DEPTH_ATTACHMENT };
glInvalidateFramebuffer(GL_FRAMEBUFFER, 1, attachments);
```

---

## Part 10: Debugging Framebuffers

### Visualizing Framebuffer Contents

```glsl
// Debug shader to view individual framebuffer attachments
#version 330 core
out vec4 FragColor;
in vec2 TexCoord;

uniform sampler2D attachment0;
uniform sampler2D attachment1;
uniform sampler2D attachment2;
uniform int debugMode;  // 0,1,2 for different attachments

void main() {
    if (debugMode == 0) {
        FragColor = texture(attachment0, TexCoord);
    } else if (debugMode == 1) {
        // Visualize normals
        vec3 normal = texture(attachment1, TexCoord).rgb;
        FragColor = vec4(normal, 1.0);
    } else if (debugMode == 2) {
        // Visualize depth
        float depth = texture(attachment2, TexCoord).r;
        FragColor = vec4(vec3(depth), 1.0);
    }
}
```

### Common Framebuffer Issues

```cpp
// PROBLEM: Black screen
// Check: Is framebuffer bound? Is it complete?
if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
    // Handle error
}

// PROBLEM: Nothing renders to texture
// Check: glDrawBuffers set correctly?
GLenum buffers[] = { GL_COLOR_ATTACHMENT0 };
glDrawBuffers(1, buffers);

// PROBLEM: Incorrect aspect ratio
// Check: Viewport matches framebuffer size
glViewport(0, 0, fboWidth, fboHeight);

// PROBLEM: Depth testing issues
// Check: Depth attachment format and enabled state
glEnable(GL_DEPTH_TEST);

// PROBLEM: Texture sampling artifacts
// Check: Texture parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
```

### Debugging Tools

```cpp
// 1. RenderDoc - capture frames and inspect framebuffers
// 2. NSight Graphics - NVIDIA's debugging tool
// 3. AMD GPU PerfStudio - AMD's profiling tool
// 4. APITrace - trace OpenGL calls

// 5. Simple CPU-side readback (slow, for debugging only)
std::vector<float> pixels(width * height * 4);
glReadPixels(0, 0, width, height, GL_RGBA, GL_FLOAT, pixels.data());
// Analyze pixel data...
```

---

## Part 11: Framebuffer Blitting

### What is Blitting?

**Blitting** is copying a block of pixels from one framebuffer to another.

```cpp
// Copy color buffer from FBO to default framebuffer
glBindFramebuffer(GL_READ_FRAMEBUFFER, fbo);
glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);

glBlitFramebuffer(
    0, 0, width, height,          // Source rectangle
    0, 0, screenWidth, screenHeight, // Dest rectangle
    GL_COLOR_BUFFER_BIT,           // What to copy
    GL_LINEAR                      // Filtering
);

// Copy depth buffer
glBlitFramebuffer(0, 0, width, height, 0, 0, width, height,
                  GL_DEPTH_BUFFER_BIT, GL_NEAREST);

// Resolve multisampled FBO
glBindFramebuffer(GL_READ_FRAMEBUFFER, multisampleFBO);
glBindFramebuffer(GL_DRAW_FRAMEBUFFER, resolveFBO);
glBlitFramebuffer(0, 0, width, height, 0, 0, width, height,
                  GL_COLOR_BUFFER_BIT, GL_LINEAR);
```

---

## Part 12: Complete Example - Post-Processing Pipeline

### Full Implementation

```cpp
class PostProcessor {
    unsigned int fbo, vao, texture;
    int width, height;
    
public:
    PostProcessor(int w, int h) : width(w), height(h) {
        // Create framebuffer
        glGenFramebuffers(1, &fbo);
        glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        
        // Create color texture
        glGenTextures(1, &texture);
        glBindTexture(GL_TEXTURE_2D, texture);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, NULL);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                               GL_TEXTURE_2D, texture, 0);
        
        // Create depth buffer
        unsigned int rbo;
        glGenRenderbuffers(1, &rbo);
        glBindRenderbuffer(GL_RENDERBUFFER, rbo);
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height);
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT,
                                  GL_RENDERBUFFER, rbo);
        
        // Check completeness
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
            std::cout << "Framebuffer not complete!" << std::endl;
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        
        // Setup fullscreen quad
        setupQuad();
    }
    
    void beginRender() {
        glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glViewport(0, 0, width, height);
    }
    
    void endRender(Shader& postShader) {
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        
        postShader.use();
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, texture);
        glBindVertexArray(vao);
        glDrawArrays(GL_TRIANGLES, 0, 6);
    }
    
private:
    void setupQuad() {
        float vertices[] = {
            -1.0f,  1.0f, 0.0f, 1.0f,
            -1.0f, -1.0f, 0.0f, 0.0f,
             1.0f, -1.0f, 1.0f, 0.0f,
            -1.0f,  1.0f, 0.0f, 1.0f,
             1.0f, -1.0f, 1.0f, 0.0f,
             1.0f,  1.0f, 1.0f, 1.0f
        };
        
        glGenVertexArrays(1, &vao);
        glGenBuffers(1, &vbo);
        
        glBindVertexArray(vao);
        glBindBuffer(GL_ARRAY_BUFFER, vbo);
        glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
        
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)0);
        glEnableVertexAttribArray(1);
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)(2 * sizeof(float)));
    }
};

// Usage
PostProcessor postProc(1920, 1080);
Shader sceneShader("scene.vert", "scene.frag");
Shader postShader("post.vert", "post.frag");

// Render loop
while (running) {
    // Render scene to framebuffer
    postProc.beginRender();
    sceneShader.use();
    renderScene();
    
    // Apply post-processing
    postProc.endRender(postShader);
    
    glfwSwapBuffers(window);
}
```

---

## The 30-Second Summary

- **Framebuffer** = Collection of buffers (color, depth, stencil) for rendering
- **Default Framebuffer** = What you see on screen (created by window)
- **Custom Framebuffers** = Off-screen render targets for effects
- **Attachments** = Color textures, depth/stencil renderbuffers
- **MRT** = Multiple Render Targets (output to several color buffers)
- **Post-Processing** = Render scene to texture, then apply effects
- **Blitting** = Copying between framebuffers
- **Completeness** = Must have all required attachments to render

**Framebuffers are the foundation of advanced rendering techniques - they enable everything from simple post-processing to complex deferred shading and beyond.**