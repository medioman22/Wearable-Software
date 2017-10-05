from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders

#
vertex_shader = """
    #version 330
    in vec3 position;
    in vec3 color;
    
    uniform mat4 projection;
    uniform mat4 view;
    uniform mat4 model;
    uniform mat4 transform;

    out vec3 newColor;
    void main() {
        gl_Position =  projection * view * model * transform * vec4(position, 1.0f);
        newColor = color;
    }
    """

fragment_shader = """
    #version 330
    in vec3 newColor;
    uniform vec4 setColor;
    layout(location = 0) out vec4 outColor;
    layout(location = 1) out vec4 idColor;
    void main()
    {
        outColor = setColor;
        idColor = vec4(1.,0.,0.,1.);
    }
    """

    
shader = None

proj_loc = None
view_loc = None
model_loc = None
transform_loc = None
setColor_loc = None