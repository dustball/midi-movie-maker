# Midi Movie Maker by Brian Klug

import rtmidi
from mido import MidiFile
from moviepy.editor import *
import sys
import mido



# Configuration
original = MidiFile("/Users/brianklug/Desktop/source05.mid")
alt = MidiFile("/Users/brianklug/Desktop/source06.mid")
moviefile = "/Users/brianklug/Desktop/movie06.mp4"
audio_file = '/Users/brianklug/Desktop/music02.m4a'
output_file = "/Users/brianklug/Desktop/out06-01.mp4"
first_note_time = 21.833 # Time in movie when first key(s) are pressed (secs)

live_debug = False

t = 0  # original timeline (secs)
i = 0
last_time = 0
old_alt_pos = 0
alt_pos = 0
alt_t = first_note_time   # alt (dest) timeline
old_alt_t = 0
altive = []
notes_needed = []
notes_have = []
keys_down = []
offset = 0 # transpose alternate peice by how many notes
o_msg = []
clips = []
c = 0
fin = 0


for m in original:
    o_msg.append(m)

if live_debug:    
    alt = mido.open_input('Casio USB Keyboard')
else:
    for m in alt:
        altive.append(m)

clip = VideoFileClip(moviefile,audio=False)

def wait_for_notes():
    global alt_pos, old_alt_pos, alt_t, notes_needed, notes_have, clip, clips, altive, old_alt_t, last_time, fin
    
    print("Notes NEEDED at t = " + str(t) + ": " + str(notes_needed))

    #while not frozenset(notes_needed).issubset(frozenset(keys_down)):
    #while not notes_needed.sort()==keys_down.sort():
    while not frozenset(notes_needed).issubset(frozenset(keys_down)):     
    
        # print "alt_pos = "+str(alt_pos)
        # print "altive.length = "+str(len(altive))
        try:
            if live_debug:
                m =  alt.receive()  
            else:
                m =  altive[alt_pos]
        except (IndexError):
            notes_have = []  
            notes_needed = []
            fin = 1
            return
            
        print("INCOMING: "+str(m))

        alt_t = alt_t + m.time
        
        if "note_o" in m.type:
            if m.velocity > 0 and "note_on" in m.type:
                print (" IN N ON: " + str(m.note))
                if m.note not in keys_down:
                    keys_down.append(m.note)
                notes_have.append(m.note)
            else:
                print (" I N OFF: " + str(m.note))
                if m.note in keys_down:
                    keys_down.remove(m.note)                
            
        old_alt_pos = alt_pos
        alt_pos=alt_pos+1
        
    print ("Keys DOWN at alt_t = " + str(alt_t) + " : " + str(keys_down))
    
    if t-last_time!=0 and alt_t-old_alt_t!=0:        
        speed = (alt_t-old_alt_t) / (t-last_time)  # new duration / old duration
    else:
        speed = 1.0
            
    duration = t - last_time
    
    print (" i         = "+str(i))
    print (" last_time = "+str("%.2f" %last_time))
    print (" t         = "+str("%.2f" %t))
    print (" duration  = "+str("%.2f" %duration))
    print (" alt_t     = "+str("%.2f" %alt_t))
    print (" old_alt_t = "+str("%.2f" %old_alt_t))
    print (" duration  = "+str("%.2f" % (alt_t-old_alt_t)))
    print (" speed     = "+str("%.2f" %speed) + " x")

    if alt_t-old_alt_t == 0:
        return
        
    if alt_t > clip.duration:
        notes_have = []      
        return
    else:
        print ("Append> "+str("%.2f" %(old_alt_t))+" to "+ str("%.2f" %(alt_t)))
        c = clip.subclip(old_alt_t,alt_t)
        if speed != 1.0:
            print ("SetDur> "+str("%.2f" % duration))
            c = c.fl_time(lambda oo: oo * speed).set_duration(duration)
        else:
            duration = alt_t
            print ("FixDur> "+str("%.2f" % duration))
            print ("FixSpd> "+str("%.2f" % speed))
            
        txt_clip = TextClip("\nSpeed: "+str("%.2f" % speed)+" x \n"+"Duration: "+str("%.2f" % duration)+"s \nNotes: "+str(notes_needed)+" \n"+ "Src t: "+str("%.2f" % last_time) + " to "+str("%.2f" % t)+" \nAlt: "+str("%.2f" % old_alt_t) + " to "+str("%.2f" % alt_t)+" \n", font='Arial', color='white', fontsize=24)
        
        txt_clip = txt_clip.set_pos(('right','top'))
                                  
        final = CompositeVideoClip([c.set_duration(duration),txt_clip.set_duration(duration)]).set_duration(duration)

        clips.append(final)
        print("")
        

    old_alt_t = alt_t    
    notes_needed = []
    notes_have = []  
    
# End wait_for_notes

please_wait = False


for message in o_msg:

    try:
        next_msg = o_msg[c+1]
        nmt = next_msg.time
    except (IndexError):
        nmt = 0
    
    c = c + 1
        
    t = t + message.time 

    print ("ORIG MSG at " + str(t)+ ":\t"+str(message))
    
    
    if "note_off" in message.type:
        if message.note in notes_needed:
            notes_needed.remove(message.note)
    
    if "note_on" in message.type:
        if message.velocity > 0:
            print ("   OR NOTE ON:\t" +str(message.note+offset))
            notes_needed.append(message.note+offset)
            i = i + 1
        else:
            # note "on" with 0 velocity = off
            if message.note in notes_needed:
                notes_needed.remove(message.note)
        

#    print (" Lookahead, next time is: " + str(nmt) + " and notes needed is: " + str(notes_needed))
#    print (" t = " + str(t) + "   last_time = " + str(last_time))
    
#    if message.time > 0:
#        please_wait = True    
#        print ("\tWaiting enabled (current message advances time)")

#    if t > alt_t:
#        please_wait = True
#        print ("\tWaiting enabled (natural clock advance)")

    if nmt > 0:
        please_wait = True
        print ("\tWaiting enabled (next message advances time)")
                
    if please_wait and notes_needed and nmt != 0:
        print("\n>> Wait For Notes >>")
        wait_for_notes()
        please_wait = False
        notes_needed = []    
        last_time = t 

    if fin:
        print ("No more incoming notes, wrapping up")
        break
        
    if alt_t > clip.duration+first_note_time:
        print ("Out of video, wrapping up")
        break
    
    


    
cclip =  concatenate_videoclips(clips)

audio = AudioFileClip(audio_file).subclip(0,t+first_note_time)

caudio = CompositeAudioClip([audio.set_start(first_note_time)])
                                
cclip.set_audio(caudio).write_videofile(output_file, audio=True, threads=4)



