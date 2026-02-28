# Matrices and Linear Algebra Basics 

## The Treasure Map Analogy

Matrices and linear algebra can be understood through a treasure map system:

- **A Vector** = A set of instructions: "Walk 3 steps East, 2 steps North"
- **A Matrix** = A transformation rule: "Rotate the map 90 degrees" or "Double all distances"
- **Matrix Multiplication** = Applying multiple transformations: "Rotate first, then double distances"
- **Identity Matrix** = "Keep everything exactly as is"
- **Inverse Matrix** = "Reverse the transformation" (how to get back)

**Just as maps and directions use coordinates to describe locations, computer graphics uses vectors and matrices to describe positions, directions, and transformations in 3D space.**

---

## Part 1: What is Linear Algebra?

### Definition

**Linear algebra** is the branch of mathematics concerning vector spaces and linear mappings between them. In computer graphics, it's the fundamental language for describing:

- Positions in 3D space
- Directions and orientations
- Transformations (move, rotate, scale)
- Projections (3D to 2D)
- Lighting calculations

### Why Graphics Programmers Need Linear Algebra

| Graphics Task | Linear Algebra Concept |
|---------------|----------------------|
| Where is a vertex? | Vector (x, y, z) |
| Move an object | Translation matrix |
| Rotate an object | Rotation matrix |
| Change size | Scale matrix |
| Position the camera | View matrix |
| 3D to 2D projection | Projection matrix |
| Which way does light bounce? | Dot product, reflection |
| Is a surface facing the light? | Dot product (normals) |
| Smooth shading | Interpolation (lerp) |

---

## Part 2: Vectors - The Building Blocks

### What is a Vector?

A **vector** is a quantity that has both magnitude (length) and direction. In graphics, we use vectors to represent:

- **Positions**: Where something is in space
- **Directions**: Which way something is pointing
- **Velocities**: How fast and in what direction something moves
- **Colors**: Amounts of red, green, and blue
- **Normals**: Which way a surface faces

### Vector Representation

```glsl
// In GLSL shaders
vec2 position2D = vec2(3.0, 4.0);      // 2D vector (x, y)
vec3 position3D = vec3(1.0, 2.0, 3.0);  // 3D vector (x, y, z)
vec4 color = vec4(1.0, 0.5, 0.0, 1.0);  // 4D vector (r, g, b, a)

// In C++ with GLM
glm::vec2 v2(3.0f, 4.0f);
glm::vec3 v3(1.0f, 2.0f, 3.0f);
glm::vec4 v4(1.0f, 0.5f, 0.0f, 1.0f);
```

### Vector Visualization

```
2D VECTOR (3, 2):
    Y
    ↑
   2 ┤          ● (3,2)
   1 ┤
   0 ┼────┬────┬────→ X
       1   2   3

The vector points from origin (0,0) to (3,2)
Length = √(3² + 2²) = √13 ≈ 3.6 units
Direction = angle of about 33.7° from X axis
```

### Vector Operations

```cpp
// Addition (move in both directions)
glm::vec3 a(1.0f, 2.0f, 3.0f);
glm::vec3 b(4.0f, 5.0f, 6.0f);
glm::vec3 c = a + b;  // (5.0, 7.0, 9.0)

// Subtraction (difference between points)
glm::vec3 direction = b - a;  // (3.0, 3.0, 3.0)

// Scalar multiplication (scaling)
glm::vec3 scaled = a * 2.0f;  // (2.0, 4.0, 6.0)

// Length (magnitude)
float len = glm::length(a);  // √(1²+2²+3²) = √14 ≈ 3.74

// Normalization (make length = 1.0)
glm::vec3 normalized = glm::normalize(a);  // a / length
```

### Dot Product (Crucial for Lighting!)

The **dot product** measures how much two vectors point in the same direction.

```cpp
float dot = glm::dot(a, b);  // a·b = |a||b|cos(θ)

// Result:
dot > 0  : Vectors point roughly same direction
dot = 0  : Vectors are perpendicular (90°)
dot < 0  : Vectors point opposite directions

// In lighting:
float brightness = glm::dot(normal, lightDirection);
// If brightness > 0, surface is lit
// If brightness < 0, surface faces away from light
```

### Cross Product (Finding Perpendicular Vectors)

The **cross product** returns a vector perpendicular to both input vectors.

```cpp
glm::vec3 up(0.0f, 1.0f, 0.0f);
glm::vec3 right(1.0f, 0.0f, 0.0f);
glm::vec3 forward = glm::cross(up, right);  // (0.0, 0.0, -1.0)

// Properties:
// - Result is perpendicular to both inputs
// - Length = |a||b|sin(θ)
// - Used to calculate normals, camera axes, etc.
```

---

## Part 3: Matrices - The Transformers

### What is a Matrix?

A **matrix** is a rectangular array of numbers that represents a linear transformation. In graphics, we use 4×4 matrices to transform 3D points and vectors.

### Matrix Dimensions

```
2×2 Matrix:      3×3 Matrix:      4×4 Matrix (used in graphics):
[ a b ]          [ a b c ]        [ a b c d ]
[ c d ]          [ d e f ]        [ e f g h ]
                 [ g h i ]        [ i j k l ]
                                  [ m n o p ]
```

### Identity Matrix (The "Do Nothing" Matrix)

```cpp
glm::mat4 identity = glm::mat4(1.0f);

// Matrix form:
[ 1 0 0 0 ]
[ 0 1 0 0 ]
[ 0 0 1 0 ]
[ 0 0 0 1 ]

// Multiplying by identity does nothing
glm::vec4 v(1.0f, 2.0f, 3.0f, 1.0f);
glm::vec4 result = identity * v;  // (1.0, 2.0, 3.0, 1.0)
```

### Matrix Multiplication (The Heart of Transformations)

```cpp
// In GLSL/GLM, multiplication is done with * operator
glm::vec4 result = matrix * vector;

// Order matters! Read from right to left:
glm::vec4 final = projection * view * model * vertex;

// This means:
// 1. Apply model transform (object → world)
// 2. Apply view transform (world → camera)
// 3. Apply projection transform (camera → clip)
```

### Matrix Multiplication Rules

```
Matrix multiplication is NOT commutative:
A × B ≠ B × A (generally)

Multiplication is associative:
(A × B) × C = A × (B × C)

Dimensions must match:
4×4 matrix × 4×1 vector = 4×1 vector
4×4 × 4×4 = 4×4
```

---

## Part 4: Transformation Matrices in Detail

### Translation Matrix (Moving)

```cpp
// Translation by (tx, ty, tz)
glm::mat4 translate = glm::translate(glm::mat4(1.0f), 
                                      glm::vec3(tx, ty, tz));

// Matrix form:
[ 1 0 0 tx ]
[ 0 1 0 ty ]
[ 0 0 1 tz ]
[ 0 0 0 1  ]

// Example: Move point (1,2,3) by (5,0,-2)
glm::mat4 T = glm::translate(glm::mat4(1.0f), glm::vec3(5,0,-2));
glm::vec4 p(1,2,3,1);
glm::vec4 result = T * p;  // (6, 2, 1, 1)
```

### Scale Matrix (Resizing)

```cpp
// Scale by (sx, sy, sz)
glm::mat4 scale = glm::scale(glm::mat4(1.0f), 
                              glm::vec3(sx, sy, sz));

// Matrix form:
[ sx 0  0  0 ]
[ 0  sy 0  0 ]
[ 0  0  sz 0 ]
[ 0  0  0  1 ]

// Example: Double X, halve Y
glm::mat4 S = glm::scale(glm::mat4(1.0f), glm::vec3(2.0, 0.5, 1.0));
glm::vec4 p(1,2,3,1);
glm::vec4 result = S * p;  // (2, 1, 3, 1)
```

### Rotation Matrix (Turning)

```cpp
// Rotation around X axis by angle θ (in radians)
glm::mat4 rotX = glm::rotate(glm::mat4(1.0f), angle, 
                              glm::vec3(1.0f, 0.0f, 0.0f));

// Matrix form (around X):
[ 1 0       0      0 ]
[ 0 cosθ   -sinθ  0 ]
[ 0 sinθ    cosθ  0 ]
[ 0 0       0      1 ]

// Rotation around Y axis:
glm::mat4 rotY = glm::rotate(glm::mat4(1.0f), angle, 
                              glm::vec3(0.0f, 1.0f, 0.0f));

// Rotation around Z axis:
glm::mat4 rotZ = glm::rotate(glm::mat4(1.0f), angle, 
                              glm::vec3(0.0f, 0.0f, 1.0f));
```

### Combining Transformations (Order Matters!)

```cpp
// Example: Rotate 45° around Y, then translate by (2,0,0)
glm::mat4 T = glm::translate(glm::mat4(1.0f), glm::vec3(2,0,0));
glm::mat4 R = glm::rotate(glm::mat4(1.0f), glm::radians(45.0f), 
                           glm::vec3(0,1,0));

// First rotate, then translate
glm::mat4 model1 = T * R;  // Translate after rotate

// First translate, then rotate (different result!)
glm::mat4 model2 = R * T;  // Rotate after translate

// Visual difference:
// model1: Object rotates at origin, then moves to (2,0,0)
// model2: Object moves to (2,0,0), then rotates around origin
```

---

## Part 5: The Model-View-Projection Pipeline

### Complete MVP Transformation

```cpp
// In application code
glm::mat4 model = glm::mat4(1.0f);
model = glm::translate(model, position);
model = glm::rotate(model, rotation.y, glm::vec3(0,1,0));
model = glm::rotate(model, rotation.x, glm::vec3(1,0,0));
model = glm::scale(model, scale);

glm::mat4 view = glm::lookAt(
    cameraPos,     // Where camera is
    cameraTarget,  // What it looks at
    glm::vec3(0,1,0)  // Up direction
);

glm::mat4 projection = glm::perspective(
    glm::radians(45.0f),  // Field of view
    aspectRatio,          // Width/height
    0.1f,                 // Near plane
    100.0f                // Far plane
);

// Combine into MVP (note order!)
glm::mat4 mvp = projection * view * model;

// In vertex shader
gl_Position = mvp * vec4(aPos, 1.0);
```

### What Each Matrix Does

```
OBJECT SPACE (local coordinates)
    ↓ [ MODEL MATRIX ]
WORLD SPACE (scene coordinates)
    ↓ [ VIEW MATRIX ]
VIEW SPACE (camera coordinates)
    ↓ [ PROJECTION MATRIX ]
CLIP SPACE (homogeneous coordinates)
    ↓ [ perspective division ]
NDC (-1 to 1)
    ↓ [ viewport transform ]
SCREEN SPACE (pixel coordinates)
```

---

## Part 6: Important Matrix Properties

### Determinant (Scale Factor)

The **determinant** tells you how much a matrix scales volume:

```cpp
float det = glm::determinant(matrix);

// Interpretation:
det > 0  : Transformation preserves orientation
det < 0  : Transformation flips orientation (mirror)
det = 0  : Matrix is singular (flattens space)
|det| > 1: Volume increases
|det| < 1: Volume decreases
```

### Inverse (Undoing Transformations)

The **inverse** matrix reverses a transformation:

```cpp
glm::mat4 original = glm::translate(glm::mat4(1.0f), glm::vec3(5,0,0));
glm::mat4 inverse = glm::inverse(original);  // Translate by (-5,0,0)

// original * inverse = identity
// inverse * original = identity

// Used for:
// - Transforming normals (inverse-transpose)
// - Unprojecting screen coordinates
// - Camera/view matrix construction
```

### Transpose (Flipping Rows and Columns)

```cpp
glm::mat4 original = /* some matrix */;
glm::mat4 transposed = glm::transpose(original);

// Used for:
// - Normals (inverse-transpose = transpose(inverse))
// - Converting between row-major and column-major
```

### Identity Matrix Properties

```cpp
glm::mat4 I = glm::mat4(1.0f);

// Properties:
I * A = A  // Multiplying by identity does nothing
A * I = A
I * v = v  // Vector unchanged
```

---

## Part 7: Quaternions (Rotation Without Gimbal Lock)

### What are Quaternions?

**Quaternions** are a 4D number system perfect for representing rotations without the problems of Euler angles (gimbal lock).

```cpp
// Creating quaternions
glm::quat q1 = glm::quat(1.0f, 0.0f, 0.0f, 0.0f);  // Identity
glm::quat q2 = glm::angleAxis(glm::radians(90.0f),  // 90° around Y
                               glm::vec3(0,1,0));

// Converting to matrix for shaders
glm::mat4 rotationMatrix = glm::mat4_cast(q2);

// Combining rotations
glm::quat combined = q1 * q2;  // Apply q2 then q1

// Spherical linear interpolation (smooth rotation)
glm::quat slerp = glm::slerp(q1, q2, 0.5f);  // Halfway between
```

### Why Quaternions?

| Euler Angles (Yaw, Pitch, Roll) | Quaternions |
|--------------------------------|-------------|
| Gimbal lock problem | No gimbal lock |
| Interpolation looks weird | Smooth slerp interpolation |
| Hard to combine rotations | Easy multiplication |
| 3 values (compact) | 4 values (slightly larger) |
| Intuitive to understand | Abstract, harder to grasp |

---

## Part 8: Practical Examples in Graphics

### Example 1: Camera LookAt Matrix

```cpp
glm::mat4 lookAt(glm::vec3 position, glm::vec3 target, glm::vec3 up) {
    // Forward direction (camera looks down -Z)
    glm::vec3 forward = glm::normalize(position - target);
    
    // Right vector (perpendicular to forward and up)
    glm::vec3 right = glm::normalize(glm::cross(up, forward));
    
    // Recompute up to ensure orthonormal basis
    glm::vec3 newUp = glm::cross(forward, right);
    
    // Build view matrix
    glm::mat4 view(1.0f);
    view[0][0] = right.x;   view[1][0] = right.y;   view[2][0] = right.z;
    view[0][1] = newUp.x;   view[1][1] = newUp.y;   view[2][1] = newUp.z;
    view[0][2] = forward.x; view[1][2] = forward.y; view[2][2] = forward.z;
    
    // Translation (camera position)
    view[3][0] = -glm::dot(right, position);
    view[3][1] = -glm::dot(newUp, position);
    view[3][2] = -glm::dot(forward, position);
    
    return view;
}
```

### Example 2: Normal Transformation

```glsl
// Vertex shader - transforming normals correctly
void main() {
    // Position transformation
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    
    // Normal transformation - use inverse-transpose!
    // This handles non-uniform scaling correctly
    vNormal = mat3(transpose(inverse(model))) * aNormal;
    
    // If only uniform scaling/rotation, simpler version:
    // vNormal = mat3(model) * aNormal;
}
```

### Example 3: Billboard (Sprite Always Faces Camera)

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

## Part 9: Common Linear Algebra Operations in GLM

### GLM (OpenGL Mathematics) Library

```cpp
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

// Vectors
glm::vec2 v2(1.0f, 2.0f);
glm::vec3 v3(1.0f, 2.0f, 3.0f);
glm::vec4 v4(1.0f, 2.0f, 3.0f, 4.0f);

// Matrices
glm::mat4 m4(1.0f);  // Identity

// Common operations
float len = glm::length(v3);
float dot = glm::dot(v3, v3);
glm::vec3 cross = glm::cross(v3, v3);
glm::vec3 norm = glm::normalize(v3);

// Transformations
glm::mat4 translate = glm::translate(glm::mat4(1.0f), glm::vec3(1,2,3));
glm::mat4 rotate = glm::rotate(glm::mat4(1.0f), glm::radians(45.0f), 
                                glm::vec3(0,1,0));
glm::mat4 scale = glm::scale(glm::mat4(1.0f), glm::vec3(2,1,1));

// Combined
glm::mat4 model = translate * rotate * scale;

// Projection matrices
glm::mat4 perspective = glm::perspective(glm::radians(45.0f), 
                                          16.0f/9.0f, 0.1f, 100.0f);
glm::mat4 ortho = glm::ortho(0.0f, 800.0f, 0.0f, 600.0f, 0.1f, 100.0f);

// View matrix
glm::mat4 view = glm::lookAt(
    glm::vec3(5,3,10),  // Camera position
    glm::vec3(0,0,0),   // Look at point
    glm::vec3(0,1,0)    // Up vector
);

// Convert to array for OpenGL
glUniformMatrix4fv(location, 1, GL_FALSE, glm::value_ptr(matrix));
```

---

## Part 10: Common Pitfalls and Debugging

### Matrix Multiplication Order

```cpp
// CORRECT: Read right to left
gl_Position = projection * view * model * vec4(aPos, 1.0);
// model first, then view, then projection

// WRONG: Read left to right
gl_Position = vec4(aPos, 1.0) * model * view * projection;  // NO!
```

### Row-Major vs Column-Major

```cpp
// OpenGL/GLM use column-major storage
// Matrix elements accessed as matrix[col][row]

glm::mat4 m;
m[0][0] = 1.0f;  // First column, first row
m[1][0] = 2.0f;  // Second column, first row
// etc.

// When uploading to shaders:
glUniformMatrix4fv(loc, 1, GL_FALSE, glm::value_ptr(m));
// GL_FALSE means "don't transpose" (keep column-major)
```

### Debugging Matrix Values

```cpp
void printMatrix(const glm::mat4& m) {
    for (int row = 0; row < 4; row++) {
        for (int col = 0; col < 4; col++) {
            std::cout << m[col][row] << " ";  // Note: col, row order!
        }
        std::cout << std::endl;
    }
}

// Check for NaN or Inf
if (glm::any(glm::isnan(m)) || glm::any(glm::isinf(m))) {
    std::cout << "Invalid matrix detected!" << std::endl;
}
```

### Common Mistakes

```cpp
// MISTAKE 1: Forgetting to convert degrees to radians
glm::rotate(45.0f, glm::vec3(0,1,0));  // WRONG - expects radians
// CORRECT: glm::rotate(glm::radians(45.0f), glm::vec3(0,1,0));

// MISTAKE 2: Wrong matrix multiplication order
model = translate * scale;  // Scale then translate?
// Usually want scale first, then rotate, then translate

// MISTAKE 3: Not normalizing vectors for lighting
float brightness = dot(normal, lightDir);  // WRONG if vectors not normalized!
// CORRECT: brightness = dot(normalize(normal), normalize(lightDir));

// MISTAKE 4: Transforming normals like positions
vNormal = mat3(model) * aNormal;  // WRONG for non-uniform scale!
// CORRECT: vNormal = mat3(transpose(inverse(model))) * aNormal;
```

---

## The 30-Second Summary

- **Vectors** = Positions, directions, colors (x, y, z, w)
- **Matrices** = Transformations (4×4 for 3D graphics)
- **Matrix Multiplication** = Apply transformations in sequence (right to left)
- **Model Matrix** = Object → World (position, rotate, scale)
- **View Matrix** = World → Camera (where camera is)
- **Projection Matrix** = Camera → Clip (perspective/orthographic)
- **Dot Product** = Measures alignment (crucial for lighting)
- **Cross Product** = Finds perpendicular vectors
- **Normalization** = Makes vectors length 1 (for lighting)
- **GLM** = The standard math library for OpenGL

**Linear algebra is the language of 3D graphics - mastering vectors and matrices transforms graphics programming from memorizing functions to understanding and creating.**