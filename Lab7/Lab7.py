"""Experiment 7: Interactive Phong illumination model for a 3D object.

Requirements: pip install pygame PyOpenGL PyOpenGL_accelerate numpy
Run: python Lab7.py
Controls: left-drag rotates; right-drag moves light; wheel zooms; Space pauses;
1/2/3 select sphere/torus/cube; M changes material; A/D/S toggle light terms;
L toggles light marker; R resets; Esc quits.
"""
import ctypes
import math, sys, time
try:
    import numpy as np
    import pygame
    from OpenGL.GL import *
    from OpenGL.GL.shaders import compileProgram, compileShader
except ImportError as exc:
    print("Install: pip install pygame PyOpenGL PyOpenGL_accelerate numpy\n" + str(exc), file=sys.stderr)
    raise SystemExit(1)

WIDTH, HEIGHT = 1100, 720
VERTEX = """
#version 330 core
layout(location=0) in vec3 p; layout(location=1) in vec3 n;
uniform mat4 model, view, projection;
out vec3 world_pos;
out vec3 world_normal;
void main(){ vec4 w=model*vec4(p,1); world_pos=w.xyz; world_normal=mat3(transpose(inverse(model)))*n; gl_Position=projection*view*w; }
"""
FRAGMENT = """
#version 330 core
in vec3 world_pos; in vec3 world_normal; out vec4 color_out;
uniform vec3 camera_pos, light_pos, light_color, object_color;
uniform float ambient_k, diffuse_k, specular_k, shininess;
void main(){
 vec3 N=normalize(world_normal), L=normalize(light_pos-world_pos), V=normalize(camera_pos-world_pos);
 vec3 ambient=ambient_k*light_color;
 vec3 diffuse=diffuse_k*max(dot(N,L),0.0)*light_color;
 vec3 R=reflect(-L,N); vec3 specular=specular_k*pow(max(dot(V,R),0.0),shininess)*light_color;
 vec3 c=(ambient+diffuse)*object_color+specular;
 float d=length(light_pos-world_pos); c*=1.0/(1.0+0.018*d+0.001*d*d);
 color_out=vec4(pow(max(c,vec3(0)),vec3(1.0/2.2)),1);
}
"""
MARKER_VS = """
#version 330 core
layout(location=0) in vec3 p; uniform mat4 model, view, projection;
void main(){gl_Position=projection*view*model*vec4(p,1);}
"""
MARKER_FS = """
#version 330 core
out vec4 color_out; uniform vec3 marker_color;
void main(){color_out=vec4(marker_color,1);}
"""

def normalize(v):
    v=np.asarray(v,dtype=np.float32); n=np.linalg.norm(v)
    return v/n if n>1e-8 else v

def perspective(fov,aspect,near,far):
    f=1/math.tan(math.radians(fov)/2); m=np.zeros((4,4),dtype=np.float32)
    m[0,0]=f/aspect; m[1,1]=f; m[2,2]=(far+near)/(near-far); m[2,3]=2*far*near/(near-far); m[3,2]=-1
    return m

def look_at(eye,target):
    f=normalize(np.asarray(target,dtype=np.float32)-eye); s=normalize(np.cross(f,(0,1,0))); u=np.cross(s,f)
    m=np.identity(4,dtype=np.float32); m[0,:3]=s; m[1,:3]=u; m[2,:3]=-f
    m[0,3]=-np.dot(s,eye); m[1,3]=-np.dot(u,eye); m[2,3]=np.dot(f,eye)
    return m

def rot_x(a):
    c,s=math.cos(a),math.sin(a); return np.array([[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1]],dtype=np.float32)

def rot_y(a):
    c,s=math.cos(a),math.sin(a); return np.array([[c,0,s,0],[0,1,0,0],[-s,0,c,0],[0,0,0,1]],dtype=np.float32)

def packed(v,n): return np.ascontiguousarray(np.column_stack((v,n)),dtype=np.float32)

def sphere_mesh(rings=40,sectors=56):
    v=[]; n=[]
    for i in range(rings):
        a0=-math.pi/2+math.pi*i/rings; a1=-math.pi/2+math.pi*(i+1)/rings
        for j in range(sectors):
            b0=2*math.pi*j/sectors; b1=2*math.pi*(j+1)/sectors
            for a,b in ((a0,b0),(a1,b0),(a1,b1),(a0,b0),(a1,b1),(a0,b1)):
                p=(math.cos(a)*math.cos(b),math.sin(a),math.cos(a)*math.sin(b)); v.append(p); n.append(p)
    return packed(v,n)

def torus_mesh(M=64,N=24,R=.72,r=.29):
    v=[]; n=[]
    for i in range(M):
        u0,u1=2*math.pi*i/M,2*math.pi*(i+1)/M
        for j in range(N):
            v0,v1=2*math.pi*j/N,2*math.pi*(j+1)/N
            for u,w in ((u0,v0),(u1,v0),(u1,v1),(u0,v0),(u1,v1),(u0,v1)):
                q=R+r*math.cos(w); v.append((q*math.cos(u),r*math.sin(w),q*math.sin(u)))
                n.append((math.cos(w)*math.cos(u),math.sin(w),math.cos(w)*math.sin(u)))
    return packed(v,n)

def cube_mesh():
    faces=[((1,0,0),[(1,-1,-1),(1,1,-1),(1,1,1),(1,-1,1)]),((-1,0,0),[(-1,-1,1),(-1,1,1),(-1,1,-1),(-1,-1,-1)]),((0,1,0),[(-1,1,-1),(-1,1,1),(1,1,1),(1,1,-1)]),((0,-1,0),[(-1,-1,1),(-1,-1,-1),(1,-1,-1),(1,-1,1)]),((0,0,1),[(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]),((0,0,-1),[(1,-1,-1),(-1,-1,-1),(-1,1,-1),(1,1,-1)])]
    v=[]; n=[]
    for normal,q in faces:
        for i in (0,1,2,0,2,3): v.append(q[i]); n.append(normal)
    return packed(v,n)

def make_vao(mesh,positions_only=False):
    vao=glGenVertexArrays(1); vbo=glGenBuffers(1); glBindVertexArray(vao); glBindBuffer(GL_ARRAY_BUFFER,vbo)
    glBufferData(GL_ARRAY_BUFFER,mesh.nbytes,mesh,GL_STATIC_DRAW); stride=12 if positions_only else 24
    glEnableVertexAttribArray(0); glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(0))
    if not positions_only: glEnableVertexAttribArray(1); glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(12))
    glBindVertexArray(0); return vao,len(mesh)

def umat(program,name,m): glUniformMatrix4fv(glGetUniformLocation(program,name),1,GL_TRUE,m)

def main():
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION,3); pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION,3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,pygame.GL_CONTEXT_PROFILE_CORE); pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE,24)
    pygame.display.set_mode((WIDTH,HEIGHT),pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE); pygame.display.set_caption("Experiment 7 | Phong Illumination")
    glEnable(GL_DEPTH_TEST); glEnable(GL_CULL_FACE); glCullFace(GL_BACK); glClearColor(.025,.035,.065,1)
    try:
        prog=compileProgram(compileShader(VERTEX,GL_VERTEX_SHADER),compileShader(FRAGMENT,GL_FRAGMENT_SHADER))
        marker=compileProgram(compileShader(MARKER_VS,GL_VERTEX_SHADER),compileShader(MARKER_FS,GL_FRAGMENT_SHADER))
    except Exception as exc:
        pygame.quit(); raise RuntimeError("Shader compilation failed; OpenGL 3.3 support is required.") from exc
    meshes={"Sphere":make_vao(sphere_mesh()),"Torus":make_vao(torus_mesh()),"Cube":make_vao(cube_mesh())}
    light_mesh=sphere_mesh(12,18)[:,:3].copy(); marker_vao,marker_count=make_vao(light_mesh,True)
    names=list(meshes); shape=0; mat=0
    materials=[("Sapphire",(.10,.42,.95),44),("Ruby",(.95,.13,.25),64),("Jade",(.12,.78,.48),28),("Gold",(1,.62,.13),80),("Violet",(.66,.29,.96),36)]
    yaw,pitch,zoom,light_angle=-.35,.22,4.2,.7; auto=True; show_light=True; terms={"a":True,"d":True,"s":True}
    drag=None; last=(0,0); clock=pygame.time.Clock(); start=time.perf_counter(); fps=60; running=True
    while running:
        dt=min(clock.tick(120)/1000, .05); fps=.92*fps+.08/max(dt,1e-5)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.VIDEORESIZE: glViewport(0,0,max(1,e.w),max(1,e.h))
            elif e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: running=False
                elif e.key==pygame.K_SPACE: auto=not auto
                elif e.key in (pygame.K_1,pygame.K_2,pygame.K_3): shape=e.key-pygame.K_1
                elif e.key==pygame.K_m: mat=(mat+1)%len(materials)
                elif e.key in (pygame.K_a,pygame.K_d,pygame.K_s): k=pygame.key.name(e.key); terms[k]=not terms[k]
                elif e.key==pygame.K_l: show_light=not show_light
                elif e.key==pygame.K_r: yaw,pitch,zoom,light_angle=-.35,.22,4.2,.7; auto=True; show_light=True; terms={"a":True,"d":True,"s":True}
            elif e.type==pygame.MOUSEBUTTONDOWN:
                if e.button in (1,3): drag=e.button; last=e.pos
                elif e.button==4: zoom=max(2.4,zoom-.25)
                elif e.button==5: zoom=min(8,zoom+.25)
            elif e.type==pygame.MOUSEBUTTONUP and e.button in (1,3): drag=None
            elif e.type==pygame.MOUSEMOTION and drag:
                dx=e.pos[0]-last[0]; dy=e.pos[1]-last[1]
                if drag==1: yaw+=dx*.008; pitch=max(-1.35,min(1.35,pitch+dy*.008))
                else: light_angle+=dx*.012
                last=e.pos
        if auto and drag!=1: yaw+=dt*.24
        elapsed=time.perf_counter()-start
        light=np.array((2.5*math.cos(light_angle),1.65+.7*math.sin(elapsed*.85),2.5*math.sin(light_angle)),dtype=np.float32)
        camera=np.array((zoom*math.sin(yaw)*math.cos(pitch),zoom*math.sin(pitch),zoom*math.cos(yaw)*math.cos(pitch)),dtype=np.float32)
        view=look_at(camera,np.zeros(3,dtype=np.float32)); ww,hh=pygame.display.get_window_size()
        projection=perspective(42,max(1,ww)/max(1,hh),.1,100); model=rot_y(yaw*.34)@rot_x(pitch*.45)
        name=names[shape]; vao,count=meshes[name]; mat_name,obj_color,shine=materials[mat]
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT); glUseProgram(prog)
        for key,value in (("model",model),("view",view),("projection",projection)): umat(prog,key,value)
        glUniform3f(glGetUniformLocation(prog,"camera_pos"),*camera); glUniform3f(glGetUniformLocation(prog,"light_pos"),*light)
        glUniform3f(glGetUniformLocation(prog,"light_color"),1,.91,.77); glUniform3f(glGetUniformLocation(prog,"object_color"),*obj_color)
        glUniform1f(glGetUniformLocation(prog,"ambient_k"),.16 if terms["a"] else 0); glUniform1f(glGetUniformLocation(prog,"diffuse_k"),.95 if terms["d"] else 0)
        glUniform1f(glGetUniformLocation(prog,"specular_k"),1 if terms["s"] else 0); glUniform1f(glGetUniformLocation(prog,"shininess"),shine)
        glBindVertexArray(vao); glDrawArrays(GL_TRIANGLES,0,count); glBindVertexArray(0)
        if show_light:
            marker_model=np.identity(4,dtype=np.float32); marker_model[:3,3]=light; marker_model=marker_model@np.diag([.11,.11,.11,1]).astype(np.float32)
            glUseProgram(marker)
            for key,value in (("model",marker_model),("view",view),("projection",projection)): umat(marker,key,value)
            glUniform3f(glGetUniformLocation(marker,"marker_color"),1,.78,.34); glBindVertexArray(marker_vao); glDrawArrays(GL_TRIANGLES,0,marker_count); glBindVertexArray(0)
        pygame.display.flip(); pygame.display.set_caption(f"Experiment 7 | Phong Illumination | {name} / {mat_name} | {fps:3.0f} FPS")
    pygame.quit()

if __name__=="__main__": main()
