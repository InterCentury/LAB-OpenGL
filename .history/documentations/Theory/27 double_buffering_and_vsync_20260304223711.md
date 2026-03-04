# Double Buffering and VSync

## The Theater Stage Analogy

Double buffering and VSync can be understood through a theater production:

- **The Stage** = The monitor (what the audience sees)
- **Backstage** = The back buffer (where the next scene is prepared)
- **Stagehands** = The GPU (workers building the scene)
- **Curtain Drop** = VSync (waiting for the right moment to reveal)
- **Scene Change** = Buffer swap (the moment the new scene is revealed)
- **Audience** = Your eyes (watching the performance)

**Just as a theater doesn't change sets while the audience watches, a graphics system shouldn't update the display while the monitor is drawing.**

---

## Part 1: The Problem - Tearing

### What is Tearing?

**Screen tearing** occurs when the monitor displays parts of multiple frames in a single screen refresh.

```
VISUAL TEARING:

Frame 1 (top half)    →      ┌─────────────────┐
                             │    Frame 1      │
                             │                 │
Frame 2 (bottom half) →      ├─────────────────┤  ← Tear line
                              │    Frame 2      │
                              │                 │
                              └─────────────────┘

The image appears "split" horizontally
Parts of two different frames visible simultaneously
```

### Why Tearing Happens

```
MONITOR REFRESH:           GPU RENDERING:
    ┌──┐                    ┌──┐
    │  │ Scanning...         │  │ Rendering Frame 2
    │  │                     │  │ while Frame 1
    │  │ Monitor expects     │  │ is being displayed
    │  │ complete frame      │  │
    └──┘                    └──┘

If GPU finishes Frame 2 during monitor refresh:
Monitor shows top of Frame 1 + bottom of Frame 2 = TEAR!
```

### The Root Cause

```cpp
// Single buffering (the problem)
while (running) {
    renderScene();           // Draw directly to screen memory
    // Monitor may read from this memory at any time!
    // If render takes 5ms and refresh takes 16.6ms,
    // tearing is guaranteed!
}
```

---

## Part 2: Double Buffering - The Solution

### What is Double Buffering?

**Double buffering** uses two buffers: a **front buffer** (displayed) and a **back buffer** (being rendered).

```
DOUBLE BUFFERING CONCEPT:

FRONT BUFFER (displayed):    BACK BUFFER (rendering):
┌─────────────────────┐      ┌─────────────────────┐
│                     │      │                     │
│   Frame 1 shown     │      │   GPU draws Frame 2 │
│   to user           │      │   here              │
│                     │      │                     │
└─────────────────────┘      └─────────────────────┘
         ↑                              ↑
    Monitor reads                  GPU writes
    from here                       to here

When Frame 2 complete: SWAP!
```

### The Swap Chain

```cpp
// Double buffering in action
while (running) {
    // 1. Render to back buffer
    glBindFramebuffer(GL_FRAMEBUFFER, backBuffer);
    glClear(GL_COLOR_BUFFER_BIT);
    renderScene();
    
    // 2. Swap buffers (atomic operation)
    glfwSwapBuffers(window);  // Or equivalent
    
    // 3. Front buffer now shows new frame
    //    Back buffer becomes available for next frame
}
```

### Visual Timeline

```
WITHOUT DOUBLE BUFFERING:
Time → 
Monitor: [Frame1][Frame1][Tear][Frame2][Frame2]
Render:  [Frame1---][Frame2---][Frame3---]

WITH DOUBLE BUFFERING:
Monitor: [Frame1][Frame1][Frame1][Frame2][Frame2]
Render:  [Frame1---][Frame2---][Frame3---]
Swap:                ^        ^
                     Swap     Swap

No tearing - monitor always sees complete frames!
```

---

## Part 3: Buffer Swap Mechanics

### How Buffer Swap Works

```cpp
// Pseudo-code of buffer swap
void swapBuffers() {
    // Atomically exchange front and back buffer pointers
    GPU.waitForAllRenderingToComplete();  // Optional
    swap(frontBufferPtr, backBufferPtr);
    
    // Old front buffer becomes new back buffer
    // Old back buffer (now front) becomes visible
}

// OpenGL/GLFW implementation
glfwSwapBuffers(window);  // Does the swap
glfwPollEvents();          // Process input while waiting
```

### Platform-Specific Implementation

```cpp
// Windows (WGL)
SwapBuffers(hdc);  // Swap buffers for device context

// Linux (GLX)
glXSwapBuffers(display, window);

// macOS (Cocoa)
[openGLContext flushBuffer];

// All do the same thing: exchange front/back buffers
```

### Triple Buffering

```cpp
// Triple buffering adds a third buffer for smoother rendering
// Front: Displayed
// Back1: Currently rendering
// Back2: Ready to swap

ADVANTAGE: GPU never waits for vsync to start rendering
DISADVANTAGE: Adds 1 frame of latency (usually)

TRIPLE BUFFERING TIMELINE:
Monitor: [F1][F1][F1][F2][F2][F2][F3][F3]
Render:  [F1---][F2---][F3---][F4---]
Queue:          Ready  Ready  Ready
                F2     F3     F4
```

---

## Part 4: VSync - Vertical Synchronization

### What is VSync?

**VSync** (Vertical Synchronization) synchronizes buffer swaps with the monitor's refresh cycle, preventing tearing by ensuring swaps only happen during the vertical blank interval.

```
MONITOR REFRESH CYCLE:

    ┌─────────────────┐
    │                 │ ← Scanout starts at top
    │  ACTIVE SCAN    │
    │                 │
    ├─────────────────┤
    │   VERTICAL      │ ← "Vertical Blank" interval
    │   BLANK         │   (safe to swap)
    └─────────────────┘
    
    Time → 16.6ms for 60Hz display
```

### Enabling VSync

```cpp
// GLFW - enable VSync
glfwSwapInterval(1);  // 1 = enable VSync, 0 = disable

// SDL
SDL_GL_SetSwapInterval(1);

// Windows WGL (if using manual context)
wglSwapIntervalEXT(1);

// Check if VSync is enabled
int interval = glfwGetSwapInterval();
std::cout << "VSync interval: " << interval << std::endl;
```

### VSync Behavior

```cpp
// WITH VSYNC (glfwSwapInterval(1))
while (running) {
    renderScene();
    glfwSwapBuffers(window);  // This will BLOCK until next vertical blank
    
    // If rendering takes 5ms, we wait ~11.6ms for next vsync
    // Result: 60 FPS exactly, no tearing
}

// WITHOUT VSYNC (glfwSwapInterval(0))
while (running) {
    renderScene();
    glfwSwapBuffers(window);  // Returns immediately
    
    // If rendering takes 5ms, we get 200 FPS
    // But tearing will occur
}
```

---

## Part 5: The Vertical Blank Interval

### What is Vertical Blank?

The **vertical blank** (vblank) is the period when the monitor's electron beam (or scanout) returns from bottom-right to top-left.

```
VERTICAL BLANK DETAIL:

    ┌─────────────────┐
    │                 │
    │  ACTIVE DISPLAY │ ← Monitor drawing image
    │                 │
    ├─────────────────┤
    │                 │
    │  VERTICAL BLANK │ ← No drawing happening
    │                 │   Safe time to swap
    ├─────────────────┤
    │                 │
    │  ACTIVE DISPLAY │ ← Next frame begins
    │                 │
    └─────────────────┘
    
    Vblank duration: ~0.5-1ms at 60Hz
    Total frame: 16.6ms
```

### Detecting Vertical Blank

```cpp
// OpenGL extension for vblank synchronization
// Usually handled by driver, but can query:

// GLX (Linux)
glXGetVideoSyncSGI(&syncCount);
glXWaitVideoSyncSGI(divisor, remainder, &count);

// WGL (Windows)
wglGetSyncValuesOML(hdc, &ust, &msc, &sbc);

// Most applications just use glfwSwapInterval(1)
```

---

## Part 6: Performance Implications

### Frame Timing Scenarios

```cpp
// SCENARIO 1: Fast rendering (< 16.6ms at 60Hz)
Render time: 5ms
VSync ON:   60 FPS (waits 11.6ms each frame)
VSync OFF:  200 FPS (but tearing)

// SCENARIO 2: Slow rendering (> 16.6ms)
Render time: 20ms
VSync ON:   50 FPS (misses vsync, effectively 50 FPS)
VSync OFF:  50 FPS (no benefit, still 50 FPS)

// SCENARIO 3: Variable rendering
Frame 1: 10ms
Frame 2: 18ms
Frame 3: 8ms

VSync ON:  FPS limited to refresh rate, consistent timing
VSync OFF: FPS varies, potentially more input lag
```

### Measuring Frame Time

```cpp
// Measure and log frame times
double lastTime = glfwGetTime();
int frameCount = 0;

while (running) {
    renderScene();
    glfwSwapBuffers(window);
    
    frameCount++;
    double currentTime = glfwGetTime();
    double delta = currentTime - lastTime;
    
    if (delta >= 1.0) {  // Every second
        double fps = frameCount / delta;
        double frameTimeMs = (delta / frameCount) * 1000.0;
        
        std::cout << "FPS: " << fps 
                  << " Frame time: " << frameTimeMs << "ms" 
                  << std::endl;
        
        frameCount = 0;
        lastTime = currentTime;
    }
}
```

---

## Part 7: Input Lag Considerations

### Sources of Input Lag

```
INPUT LAG PIPELINE:

1. Input peripheral (mouse/keyboard)   → 1-4ms
2. OS input processing                  → 1-2ms
3. Game logic update                     → 1-16ms
4. Rendering                             → 1-16ms
5. Buffer swap + VSync wait              → 0-16ms
6. Display processing                     → 1-10ms
7. Pixel response                         → 1-5ms

TOTAL: 5-70ms typical
```

### VSync and Input Lag

```cpp
// VSync adds up to 1 full frame of lag
// At 60Hz: up to 16.6ms additional lag

WITHOUT VSYNC:
Mouse click → Render → Display
   0ms        5ms      5ms total

WITH VSYNC:
Mouse click → Render → Wait → Display
   0ms        5ms     16.6ms  21.6ms total

// Competitive gamers often disable VSync
// But accept tearing for lower latency
```

### Adaptive VSync

```cpp
// NVIDIA Adaptive VSync (driver option)
// Enables VSync when FPS > refresh rate
// Disables VSync when FPS < refresh rate

// Pseudo-implementation
if (fps >= monitorRefreshRate) {
    glfwSwapInterval(1);  // Enable VSync
} else {
    glfwSwapInterval(0);  // Disable VSync (avoid stuttering)
}

// Best of both worlds: no tearing when possible,
// no stuttering when performance drops
```

---

## Part 8: Implementation Examples

### GLFW Complete Example

```cpp
#include <GLFW/glfw3.h>

int main() {
    glfwInit();
    
    // Create window with double buffering enabled by default
    GLFWwindow* window = glfwCreateWindow(800, 600, "Double Buffering", NULL, NULL);
    glfwMakeContextCurrent(window);
    
    // VSync control
    glfwSwapInterval(1);  // Enable VSync (default with GLFW)
    // glfwSwapInterval(0);  // Disable VSync
    
    int enableVSync = 1;
    
    while (!glfwWindowShouldClose(window)) {
        // Handle input
        if (glfwGetKey(window, GLFW_KEY_V) == GLFW_PRESS) {
            // Toggle VSync on V key press
            enableVSync = !enableVSync;
            glfwSwapInterval(enableVSync);
            
            // Debounce (simple)
            while (glfwGetKey(window, GLFW_KEY_V) == GLFW_PRESS) {
                glfwPollEvents();
            }
        }
        
        // Render frame
        glClear(GL_COLOR_BUFFER_BIT);
        // ... drawing commands ...
        
        // Swap buffers (may block if VSync enabled)
        glfwSwapBuffers(window);
        glfwPollEvents();
    }
    
    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
```

### Manual Double Buffering (OpenGL)

```cpp
// OpenGL automatically uses double buffering with GLFW
// But here's what happens behind the scenes:

// At context creation:
GLFWwindow* window = glfwCreateWindow(800, 600, "Title", NULL, NULL);
// Creates: Front buffer (visible), Back buffer (hidden)

// During rendering:
glDrawElements(GL_TRIANGLES, ...);  // Writes to back buffer

// At swap:
glfwSwapBuffers(window);
// 1. Waits for VSync if enabled
// 2. Exchanges front/back buffer pointers
// 3. Previous front buffer becomes new back buffer
// 4. New back buffer may need clearing
```

### SDL Implementation

```cpp
#include <SDL2/SDL.h>

int main() {
    SDL_Init(SDL_INIT_VIDEO);
    
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
    SDL_GL_SetAttribute(SDL_GL_SWAP_CONTROL, 1);  // VSync on
    
    SDL_Window* window = SDL_CreateWindow(
        "SDL Double Buffering",
        SDL_WINDOWPOS_UNDEFINED,
        SDL_WINDOWPOS_UNDEFINED,
        800, 600,
        SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN
    );
    
    SDL_GLContext context = SDL_GL_CreateContext(window);
    
    // Toggle VSync
    SDL_GL_SetSwapInterval(1);  // Enable
    // SDL_GL_SetSwapInterval(0);  // Disable
    
    int running = 1;
    SDL_Event event;
    
    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) running = 0;
            if (event.type == SDL_KEYDOWN) {
                if (event.key.keysym.sym == SDLK_v) {
                    // Toggle VSync
                    int interval = SDL_GL_GetSwapInterval();
                    SDL_GL_SetSwapInterval(interval ? 0 : 1);
                }
            }
        }
        
        // Render
        glClear(GL_COLOR_BUFFER_BIT);
        // ... drawing ...
        
        SDL_GL_SwapWindow(window);  // Swap buffers
    }
    
    SDL_GL_DeleteContext(context);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
```

---

## Part 9: Advanced Techniques

### Frame Pacing

```cpp
// Consistent frame pacing for smooth animation
class FramePacer {
    double targetFrameTime;  // 16.6ms for 60 FPS
    double lastFrameTime;
    
public:
    FramePacer(double targetFPS) {
        targetFrameTime = 1.0 / targetFPS;
        lastFrameTime = glfwGetTime();
    }
    
    void waitForNextFrame() {
        double now = glfwGetTime();
        double frameDuration = now - lastFrameTime;
        double timeToWait = targetFrameTime - frameDuration;
        
        if (timeToWait > 0) {
            // Busy wait or sleep
            std::this_thread::sleep_for(
                std::chrono::milliseconds((int)(timeToWait * 1000))
            );
        }
        
        lastFrameTime = glfwGetTime();
    }
};

// Usage with VSync disabled
FramePacer pacer(60.0);  // Target 60 FPS

while (running) {
    renderScene();
    glfwSwapBuffers(window);
    pacer.waitForNextFrame();  // Maintain 60 FPS
}
```

### Detecting Monitor Refresh Rate

```cpp
// GLFW - get monitor refresh rate
GLFWmonitor* monitor = glfwGetPrimaryMonitor();
const GLFWvidmode* mode = glfwGetVideoMode(monitor);
int refreshRate = mode->refreshRate;  // Usually 60, 120, 144, 240

std::cout << "Monitor: " << mode->width << "x" << mode->height
          << " @ " << refreshRate << "Hz" << std::endl;

// Set swap interval based on refresh rate
if (refreshRate >= 120) {
    glfwSwapInterval(1);  // 120+ FPS capable
} else {
    glfwSwapInterval(1);  // Still 1, but effective FPS limited
}

// For 30 FPS content (cinematic)
glfwSwapInterval(2);  // Swap every 2 vblanks = 30 FPS at 60Hz
```

### Late Swap Tearing Prevention

```cpp
// Some drivers provide "late swap" prevention
// If rendering misses vsync, wait for next vsync

// NVIDIA driver setting (control panel)
// "Vertical Sync" = "On" (not "Fast" or "Adaptive")

// AMD driver setting
// "Wait for Vertical Refresh" = "Always On"

// This prevents tearing but can cause stuttering
// when frame times are inconsistent
```

---

## Part 10: Common Issues and Solutions

### Issue 1: Stuttering

```cpp
// SYMPTOM: Animation stutters despite high FPS
// CAUSE: Inconsistent frame times

// SOLUTION 1: Profile and optimize heavy frames
// Track frame times
double frameTimes[60];
int frameIndex = 0;

void recordFrameTime() {
    static double lastTime = glfwGetTime();
    double now = glfwGetTime();
    frameTimes[frameIndex % 60] = now - lastTime;
    frameIndex++;
    lastTime = now;
}

// Identify and fix spikes
if (frameTime > 0.02) {  // > 20ms
    std::cout << "Slow frame: " << frameTime * 1000 << "ms" << std::endl;
    // Investigate what caused this
}

// SOLUTION 2: Use VSync to smooth delivery
glfwSwapInterval(1);
```

### Issue 2: VSync Off Tearing

```cpp
// SYMPTOM: Tearing with VSync off
// CAUSE: Buffer swaps during active scan

// SOLUTION: Accept tearing for lower latency (games)
// OR use triple buffering if available

// Check for triple buffering support
int extensions;
glGetIntegerv(GL_NUM_EXTENSIONS, &extensions);
for (int i = 0; i < extensions; i++) {
    const char* ext = (const char*)glGetStringi(GL_EXTENSIONS, i);
    if (strcmp(ext, "GLX_EXT_swap_control_tear") == 0) {
        // Supports "adaptive vsync" style tear control
    }
}
```

### Issue 3: VSync On Stuttering

```cpp
// SYMPTOM: Stuttering with VSync on
// CAUSE: Frame times > refresh interval

// VISUAL:
60 FPS target: 16.6ms per frame
Actual: [16ms][17ms][16ms][18ms][16ms]
Result: Some frames miss vsync, causing stutter

// SOLUTION 1: Optimize to stay under 16.6ms
// SOLUTION 2: Use adaptive VSync
// SOLUTION 3: Target 30 FPS with glfwSwapInterval(2)
if (cannotMaintain60FPS()) {
    glfwSwapInterval(2);  // Switch to 30 FPS mode
}

// SOLUTION 4: Use G-Sync/FreeSync (variable refresh rate)
// Requires compatible monitor and GPU
```

### Issue 4: Input Lag

```cpp
// SYMPTOM: Controls feel sluggish
// CAUSE: Multiple buffered frames

// Measure input-to-photon latency
double inputTime = glfwGetTime();
processInput();
render();
glfwSwapBuffers(window);
double displayTime = glfwGetTime();
double latency = displayTime - inputTime;

std::cout << "Input lag: " << latency * 1000 << "ms" << std::endl;

// Reduce by:
// 1. Disable VSync (adds ~16ms)
// 2. Reduce rendering complexity
// 3. Use lower buffer count (not always possible)
```

---

## Part 11: Platform-Specific Notes

### Windows

```cpp
// Windows DWM (Desktop Window Manager) adds complexity
// DWM itself uses triple buffering

// For fullscreen applications:
// - DirectFlip allows bypassing DWM
// - Lower latency, but may have mode switches

// For windowed mode:
// - DWM always composites
// - Additional copy operation
// - May add 1-2 frames of latency

// Best practice: Use fullscreen exclusive mode for games
glfwWindowHint(GLFW_FLOATING, GLFW_TRUE);  // Not enough
// Need to set display mode:
GLFWmonitor* monitor = glfwGetPrimaryMonitor();
const GLFWvidmode* mode = glfwGetVideoMode(monitor);
GLFWwindow* window = glfwCreateWindow(
    mode->width, mode->height, 
    "Fullscreen", monitor, NULL
);
```

### Linux

```cpp
// Linux with X11:
// - VSync handled by compositor (if using compositor)
// - Can bypass with fullscreen unredirect

// Check if compositor is running
// Disable for fullscreen games:
// In KDE: System Settings → Display and Monitor → Compositor
// Set "Allow applications to block compositing"

// Wayland:
// - Always VSync (cannot disable)
// - Tearing protection built-in
// - Lower latency than X11 + compositor

// GLX vs EGL:
// - GLX: Older, more compatible
// - EGL: Newer, better for embedded/Wayland
```

### macOS

```cpp
// macOS:
// - Always VSync in windowed mode (cannot disable)
// - Fullscreen can disable VSync
// - Metal API preferred over OpenGL

// Check vsync state:
GLint vsync = 0;
[CGLContextObj cglContext = CGLGetCurrentContext();
CGLGetParameter(cglContext, kCGLCPSwapInterval, &vsync);

// Set vsync:
GLint vsync = 1;  // 1 = on, 0 = off
CGLSetParameter(cglContext, kCGLCPSwapInterval, &vsync);
```

---

## Part 12: Best Practices

### Recommendations by Use Case

| Application Type | VSync Setting | Buffering | Reasoning |
|-----------------|---------------|-----------|-----------|
| **Competitive Games** | OFF | Double | Lowest latency, accept tearing |
| **Casual Games** | ON | Double | Smooth, no tearing |
| **Cutscenes/Cinematic** | ON (2 interval) | Triple | 30 FPS film look |
| **VR Applications** | ON | Double | Must match headset refresh |
| **UI/Desktop** | ON | Triple | Smooth, no tearing |
| **Video Playback** | ON | Triple | Match video frame rate |
| **Benchmarking** | OFF | Double | Measure raw performance |

### Implementation Checklist

```cpp
class GraphicsSetup {
public:
    void initialize() {
        // 1. Create window with double buffering
        window = glfwCreateWindow(width, height, title, monitor, NULL);
        
        // 2. Make context current
        glfwMakeContextCurrent(window);
        
        // 3. Set swap interval based on application needs
        if (competitiveMode) {
            glfwSwapInterval(0);  // VSync off
        } else {
            glfwSwapInterval(1);  // VSync on
        }
        
        // 4. Allow user override
        registerHotkey(GLFW_KEY_V, toggleVSync);
    }
    
    void toggleVSync() {
        int current = glfwGetSwapInterval();
        glfwSwapInterval(current ? 0 : 1);
        
        std::cout << "VSync " << (current ? "OFF" : "ON") << std::endl;
    }
    
    void renderLoop() {
        while (!glfwWindowShouldClose(window)) {
            // Handle input
            processInput();
            
            // Update logic
            update();
            
            // Render frame
            render();
            
            // Swap (may block)
            glfwSwapBuffers(window);
            
            // Poll events (includes input)
            glfwPollEvents();
        }
    }
};
```

### Performance Monitoring

```cpp
class PerformanceMonitor {
    double lastTime;
    int frameCount;
    double fps;
    double frameTime;
    int missedVSyncs;
    
public:
    void beginFrame() {
        lastTime = glfwGetTime();
    }
    
    void endFrame() {
        frameCount++;
        double now = glfwGetTime();
        frameTime = now - lastTime;
        
        // Detect missed VSync
        if (glfwGetSwapInterval() > 0) {
            double targetFrameTime = 1.0 / 60.0;  // Assume 60Hz
            if (frameTime > targetFrameTime * 1.5) {
                missedVSyncs++;
            }
        }
        
        // Update FPS every second
        static double fpsTimer = 0;
        fpsTimer += frameTime;
        if (fpsTimer >= 1.0) {
            fps = frameCount / fpsTimer;
            std::cout << "FPS: " << fps 
                      << " Missed VSyncs: " << missedVSyncs
                      << std::endl;
            
            frameCount = 0;
            fpsTimer = 0;
            missedVSyncs = 0;
        }
    }
};
```

---

## The 30-Second Summary

- **Double Buffering** = Two buffers: front (displayed) and back (rendering)
- **Buffer Swap** = Exchange front/back pointers (atomic operation)
- **Tearing** = Multiple frames visible at once (caused by during-scan swap)
- **VSync** = Synchronizes swaps with monitor refresh (eliminates tearing)
- **Swap Interval** = Number of vblanks between swaps (1 = 60 FPS at 60Hz)
- **Input Lag** = VSync adds up to 1 frame of latency (16.6ms at 60Hz)
- **Triple Buffering** = Three buffers for smoother rendering (more latency)
- **Adaptive VSync** = Enables/disables based on framerate

**Double buffering with VSync provides tear-free, smooth animation at the cost of potential input lag and framerate limiting. The choice depends entirely on application requirements - competitive speed or visual quality.**