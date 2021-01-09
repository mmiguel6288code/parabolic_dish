import pyglet
from pyglet import shapes, text, clock
from math import atan2, pi, cos, sin, tan, sqrt, atan
from cmath import exp


window_dimensions = (640,480)
window = pyglet.window.Window(*window_dimensions)
batch = pyglet.graphics.Batch()

vertex = (window_dimensions[0]/2,0)
parabola_width = window_dimensions[0]/2
parabola_height = window_dimensions[1]/3

a = parabola_height/(parabola_width/2)**2
plane_length = 200

plane = shapes.Line(0,0,0,0,color=(50,225,30),batch=batch)
num_rays = 20
num_balls = 50
bdr = wavelength = 30 
period = 100
#bdr = 58

rays = []
refs = []
rtexts = []
balls = []
for i in range(num_rays):
    rays.append(shapes.Line(0,0,0,0,color=(50,225,30),batch=batch))
    refs.append(shapes.Line(0,0,0,0,color=(50,125,30),batch=batch))
    rtexts.append(text.Label('',x=10,y=window_dimensions[1]-30*(i+1)))
    balls.append([])
    for j in range(num_balls):
        if j % 2 == 0:
            balls[-1].append(shapes.Circle(0,0,4,color=(250,20,20),batch=batch))
        else:
            balls[-1].append(shapes.Circle(0,0,4,color=(20,20,250),batch=batch))
phase_text = text.Label('',x=10,y=window_dimensions[1]-30*(num_rays+1))
time_text = text.Label('',x=10,y=window_dimensions[1]-30*(num_rays+2),batch=batch)

last_x = last_y = None
lines = []


for x in range(int(vertex[0]-parabola_width/2),int(vertex[0]+parabola_width/2)):
    y = (x-vertex[0])**2*a+vertex[1]
    if last_x is not None:
        lines.append(shapes.Line(last_x,last_y,x,y,width=10,color=(255,255,255),batch=batch))
    last_x = x
    last_y = y

focus_x, focus_y = vertex[0], vertex[1]+1/(4*a)
focus = shapes.Circle(focus_x,focus_y,5,color=(200,0,200),batch=batch)
focus_line = shapes.Line(focus_x-30,focus_y,focus_x+30,focus_y,width=5,color=(200,0,200),batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()
t = [0]
x=[0]
y=[0]
def update(dt,t=t,x=x,y=y):
    #x = vertex[0]+parabola_width*sin(t[0]*2*pi/300)/3
    #y = window_dimensions[1]-100
    t[0] += 1
    time_text.text = str(t[0])
    redraw(x[0],y[0])

@window.event
def on_mouse_motion(x,y,dx,dy,xx=x,yy=y):
    #redraw(x,y)
    xx[0] = x
    yy[0] = y

def redraw(x,y,tt=t):
    vector = (x-focus_x,y-focus_y)
    if abs(vector[0]) > 1e-8:
        theta = atan2(vector[1],vector[0])
        phi = theta+pi/2
        r = plane_length
        plane.x,plane.y = x+r/2*cos(phi),y+r/2*sin(phi)
        plane.x2,plane.y2 = x-r/2*cos(phi),y-r/2*sin(phi)
        
        t = tan(theta)
        b = -(2*a*vertex[0]+t)

        phase1 = 0 
        phase2 = 0 
        for i,(ray,ref,rtext) in enumerate(zip(rays,refs,rtexts)): 
            denom = len(rays)-1
            ray.x,ray.y = plane.x-i/denom*r*cos(phi),plane.y-i/denom*r*sin(phi)
            c = a*vertex[0]**2+vertex[1]-ray.y+t*ray.x
            try:
                x1 = (-b+sqrt(b**2-4*a*c))/(2*a)
                x2 = (-b-sqrt(b**2-4*a*c))/(2*a)
                if vertex[0]-parabola_width/2 <= x1 <= vertex[0] + parabola_width/2:
                    ray.x2 = x1
                else:
                    ray.x2 = x2
                ray.y2 = (ray.x2-vertex[0])**2*a+vertex[1]
            except:
                pass

            y_prime = 2*a*(ray.x2-vertex[0])
            pt = atan(y_prime)
            ptm = (pt+pi) % (2*pi)
            if abs(theta-pt) < abs(theta-ptm):
                if theta < pt:
                    theta_out = ptm+abs(theta-pt)
                else:
                    theta_out = ptm-abs(theta-pt)
            else:
                if theta < ptm:
                    theta_out = pt+abs(theta-ptm)
                else:
                    theta_out = pt-abs(theta-ptm)
            ref.x,ref.y,ref.x2,ref.y2 = ray.x2,ray.y2,ray.x2+500*cos(theta_out),ray.y2+500*sin(theta_out)
            bl = 0
            ray_length = sqrt((ray.x2-ray.x)**2+(ray.y2-ray.y)**2)
            ray_uv = (ray.x2-ray.x)/ray_length,(ray.y2-ray.y)/ray_length
            reflected = False
            tp = (tt[0]%period)/period
            bx,by = ray.x,ray.y
            bx,by = bx+ray_uv[0]*bdr*2*tp,by+ray_uv[1]*bdr*2*tp
            bl += bdr*2*tp

            for j,ball in enumerate(balls[i]):
                if not reflected:
                    if bl+bdr < ray_length:
                        bx,by = bx+ray_uv[0]*bdr,by+ray_uv[1]*bdr
                        if ball.color[2] > 50:
                            ball.color = (10,10,100)
                        else:
                            ball.color = (100,10,10)
                        bl += bdr
                    else:
                        bx,by = ref.x,ref.y
                        remaining_offset = (bl+bdr-ray_length)
                        ref_length = sqrt((ref.x2-ref.x)**2+(ref.y2-ref.y)**2)
                        ref_uv = (ref.x2-ref.x)/ref_length,(ref.y2-ref.y)/ref_length
                        bx,by = bx+ref_uv[0]*remaining_offset,by+ref_uv[1]*remaining_offset
                        reflected = True
                        bl += bdr
                else:
                    if ball.color[2] > 50:
                        ball.color = (20,20,200)
                    else:
                        ball.color = (200,20,20)
                    bx,by = bx+ref_uv[0]*bdr,by+ref_uv[1]*bdr
                    bl += bdr
                ball.x = bx
                ball.y = by



            if False:
                path_length = sqrt((ray.x2-ray.x)**2+(ray.y2-ray.y)**2)+sqrt((ref.x2-ref.x)**2+(ref.y2-ref.y)**2)

                f1 = 30e4
                f2 = 20e4
                w1 = 3e9/f1*39.37
                w2 = 3e9/f2*39.37
                in_pp = 29/parabola_width
                path_length_in = in_pp*path_length
                p1 = (path_length_in % w1)/w1*2*pi
                p2 = (path_length_in % w2)/w2*2*pi
                rtext.text = '%0.3f, %0.3f' % (p1,p2)
                phase1 += exp(1j*p1)
                phase2 += exp(1j*p2)
        #phase_text.text = '%0.3f, %0.3f' % (atan2(phase1.imag,phase1.real)*180/pi,atan2(phase2.imag,phase2.real)*180/pi)




clock.schedule_interval(update,0.01)
pyglet.app.run()

import os
os.environ['PYTHONINSPECT'] = '1'
