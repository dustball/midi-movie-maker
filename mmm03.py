# Gas Movie Logger

import rtmidi
from mido import MidiFile
from moviepy.editor import *
import sys
import mido


import gizeh
import moviepy.editor as mpy


# Configuration
csv = open("/Users/brianklug/Desktop/datawow.csv",'r')
output_file = "/Users/brianklug/Desktop/out06-04.mp4"
o2 = "20.9"


W,H = 1920,1080 # width, height, in pixels

def make_frame(tt):
    
#    print ("t: "+str(tt))
#    print ("o2: "+o2)
    
    surface = gizeh.Surface(W,H)
    height = float(o2)
        
    
    gradient = gizeh.ColorGradient(type="linear",
                     stops_colors = [(0,(0,0,0)),(.3,(0.74,0.074,.066)) ,(0.60,(1,1,0)), (.88,(0,.54,0)),(1,(0,0,0))],
                     xy1=[W/2,1040], xy2=[W/2,336])


    p = gizeh.polyline(points=[(1888,1040), (1812,1040), (1812,336), (1888,336), (1888,1040)], stroke_width=2,
                     stroke=(1,1,1,1),fill=gradient)                     
    p.draw(surface)
    

    txt = gizeh.text(o2+"% ►", "Arial",20,fill=(1,1,1), h_align="right",fontweight='bold',xy=(1808,1040-(height*29.4)))
    txt.draw(surface)
        

    gradient = gizeh.ColorGradient(type="linear",
                     stops_colors = [(.3,(0,0,0)),(.15,(0,0,0)),(0,(0,0,0,0))],
                     xy1=[W/2,1040-(height*29.4)], xy2=[W/2,336])

    inset = 1
    p = gizeh.polyline(points=[(1888-inset,1040-(height*29.4)-inset), (1812+inset,1040-(height*29.4)-inset), (1812+inset,336+inset), (1888-inset,336+inset), (1888-inset,1040-(height*29.4)-inset)], stroke_width=0,fill=gradient)                     
    p.draw(surface)

    return surface.get_npimage()



t = 0  
clips = []

screensize = (W,H)

header = csv.readline()

# print (header)

for line in csv:
    
    values = line.split(",")
        
    
    line = line.replace(","," ")
    line = line.replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ")
    
    d = 2
    
    if values[25] and int(values[25]) > 0:
        
        d = int(values[25])
        
        
        if values[3] == '':
            values[3] = "Ready"
            
        text = "  Oxygen: "+values[17]+"% CO:" + values[11]+"ppm H2S:"+values[5]+"ppm LEL:" + values[21] + "\n  " + values[3] + " " + values[20] + "\n  " + values[0] + " " + values[1]
        o2 = values[17]
        
        print(text)
        txt_clip = TextClip(text , font='Arial', color='white', align="SouthWest",fontsize=24,size=screensize, transparent=True).set_duration(d).subclip(0,d).set_fps(1)
    else:
        
        
        text = "  " +values[3] + "\n  " + values[2] + "\n  " +  values[0] + " " + values[1] 
        
        print(text)
        txt_clip = TextClip( text, font='Arial', color='white', align="SouthWest",fontsize=24,size=screensize, transparent=True).set_duration(d).subclip(0,d).set_fps(1)
    
    
    #bclip = mpy.VideoClip(make_frame, duration=d).set_duration(d).subclip(0,d).set_fps(1)
    bclip = mpy.ImageClip(make_frame(0))
    r = CompositeVideoClip( [bclip, txt_clip]).set_duration(d).subclip(0,d).set_fps(1)
    
    clips.append(r)
    
    t = t + d

    print("")
    
#    if t >= 30:   # abort after 30 seconds
#        break

              
cclip =  concatenate_videoclips(clips).set_duration(t)
                                
cclip.write_videofile(output_file, audio=False, threads=3, fps=1)



