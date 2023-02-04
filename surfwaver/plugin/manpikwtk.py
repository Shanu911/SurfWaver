from tkinter  import *
import tkinter as tk
import json
from PIL import Image, ImageTk
import os
import math
from attrdict import AttrDict

BTN_FONT = ('Ariel',11,'bold')

def main():
    window = manWindow()
    window.mainloop()

def RootDir():      
    filename = "log/settings.json"  
    try:
        file= open(filename, "r")
        data = AttrDict(json.load(file))
        return data.gframe.rootdir
    except:
        print(f"Preference settings file -> {filename} not found")
        return None
    
class manWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        min_win_w = 400
        min_win_h = 400

        max_win_w = self.winfo_screenwidth()
        try:
            import ctypes

            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            titleBar_h = int(ctypes.windll.user32.GetSystemMetrics(4))
        except AttributeError:
            titleBar_h =  max_win_w*10/1366

        with open("log/disper_peaks.json", "r") as f:
            jobj = json.load(f)
            self.vmn = int(jobj['v_phase_lim'][0])
            self.vmx = int(jobj['v_phase_lim'][1])
            self.fmn = int(jobj['freq_lim'][0])
            self.fmx = int(jobj['freq_lim'][1])

        max_win_h = self.winfo_screenheight() - titleBar_h
        rto = ((15,2), (272, 144))
        pad = int(max_win_w/rto[1][0])
        self.pad = pad

        self.ROOT = RootDir()
        
        self.file = open(self.ROOT + "/dispersion/dispdata.json", 'r') 
        self.data = json.load(self.file)
        self.cmpcc_loc = list(self.data['disp_dict'].keys())
        self.len = len(self.cmpcc_loc)
        self.sc = StringVar()
        self.slocidnx = 0
        self.flag = 0
        self.samplesDict = dict()  # contains frequency, velocity and ids
        
        btnfrme_w = int(max_win_w*rto[0][1]/(sum(rto[0])))
        self.cnvs_w = max_win_w-btnfrme_w-pad*2 
        self.cnvs_h = max_win_h-pad*2 

        self.xmx = self.cnvs_w - self.pad*15 - 25
        self.xmn = self.pad*12+12
        self.ymx = self.cnvs_h-self.pad*16+10
        self.ymn = self.pad*10


        self.title('Manual picking')
        self.geometry("%dx%d" % (max_win_w, max_win_h))
        self.minsize(min_win_w, min_win_h)
        self.maxsize(max_win_w, max_win_h)

        self.mainframe = Frame(self, width=max_win_w, height=max_win_h, bg="#ddd")
        self.mainframe.place(x=0,y=0)

        self.btnfrme = Frame(self.mainframe, width=btnfrme_w-pad, height=max_win_h-pad*2, bg="#eee")
        self.btnfrme.place(x=pad, y=pad)
        self.cnvsFrame = Frame(self.mainframe, width=max_win_w-btnfrme_w-pad*2, height=max_win_h-pad*2, bg="#eee") 
        self.cnvsFrame.place(x=btnfrme_w,y=pad)

        self.cnvs = Canvas(self.cnvsFrame, width=self.cnvs_w, height=self.cnvs_h, bg="#fff")
        self.cnvs.place(x=2,y=2)
        
        self.dots = Dots(canvas=self.cnvs, pad=pad, xmn=self.xmn, xmx=self.xmx, ymn=self.ymn, ymx=self.ymx, fmn=self.fmn, fmx=self.fmx, vmn=self.vmn, vmx= self.vmx)
        self.plot()
        

        #========== functionalities in left side ======================================#
        self.sloc = Label(self.btnfrme, text="Source @", font=BTN_FONT, fg='#248aa2')
        self.sloc.place(x=pad, y= pad+3+10)
        self.leftbtn = Button(self.btnfrme, text="<", command=self.prevsr, font=BTN_FONT ,width=2)
        self.leftbtn.place(x=pad*5, y=pad*2+10 + 20)
        self.sloc_entry = Entry(self.btnfrme, textvariable=self.sc,  width=7, justify=RIGHT, font=BTN_FONT, relief=RIDGE, borderwidth=2)
        self.sloc_entry.place(x=pad*6+24, y=pad*2+3+10 + 20)
        self.rgtbtn = Button(self.btnfrme, text=">",command=self.nextsr, font=BTN_FONT, width=2)
        self.rgtbtn.place(x=pad*8+77, y=pad*2+10 +20)

        

        self.add = Button(self.btnfrme, text="Add points", command=lambda : self.flagset(0), width=12, pady=pad*2, bg="#ff9", font=BTN_FONT)
        self.add.place(x=(btnfrme_w-pad)/2-55, y=pad*5+10+25*3)

        self.dele = Button(self.btnfrme, text="Delete points", command=lambda : self.flagset(1), width=12,pady=pad*2, bg="#faa", font=BTN_FONT)
        self.dele.place(x=(btnfrme_w-pad)/2-55, y=pad*12+10+25*4)

        self.shw = Button(self.btnfrme, text="Show saved data", wraplength=100, command=self.show, width=12,pady=pad*2, bg="#fff", font=BTN_FONT)
        self.shw.place(x=(btnfrme_w-pad)/2-55, y=pad*19+10+25*5)

        self.sv = Button(self.btnfrme, text="Save data", command=self.save, width=12,pady=pad*2, bg="#9f9", font=BTN_FONT)
        self.sv.place(x=(btnfrme_w-pad)/2-55, y=pad*26+10+25*6 + 20)

        self.svall = Button(self.btnfrme, text="Save all", command=self.exportdata, width=12, pady=pad*2, bg="#fff", font=BTN_FONT)
        self.svall.place(x=(btnfrme_w-pad)/2-55, y=pad*33+10+25*7+ 20)



        # ================ main canvas =================#
        self.w = self.cnvs_w
        self.h = self.cnvs_h
        
        self.cnvs.create_text(pad*5, (self.cnvs_h/2), text="Phase Velocity", fill="black", font=('Ariel',10,''), angle=90, tags='text')
        self.cnvs.create_text((self.cnvs_w/2-50), (self.cnvs_h-pad*5), text="Frequency (Hz)", fill="black", font=('Ariel',10,''), tags='text')
        self.cnvs.create_line(self.xmn-2,self.ymn,self.xmn-2,self.ymx, width=5, tags='ln')
        self.cnvs.create_line(self.xmn-2,self.ymx,self.xmx,self.ymx, width=5, tags='ln')

        self.x = self.y = None
        self.cnvs.bind('<Motion>', self.cool_design, '+')
        
        
        self.plotclorbar(w=25)
        self.ticks()
        self.flagset(0)

        self.ignor = []
        for it in ['text', 'ln', 'img']:
            for i in self.cnvs.find_withtag(it):
                self.ignor.append(i) 
        #, command=self.onDrag)
        
        

    def cool_design(self, event):
        self.kill_xy()
        dashes = [self.pad-1, self.pad-3]
        if self.xmn <= event.x <= self.xmx and self.ymn <= event.y <= self.ymx:
            self.x = self.cnvs.create_line(event.x, self.ymn, event.x, self.ymx, dash=dashes, tags='no', fill='#fff')
            self.y = self.cnvs.create_line(self.xmn, event.y, self.xmx, event.y, dash=dashes, tags='no', fill='#fff')
            self.cnvs.config(cursor="cross")
        
        else:
            self.cnvs.config(cursor="arrow")


    def kill_xy(self, event=None):
        self.cnvs.delete('no')

    def prevsr(self):
        if self.slocidnx:
            self.slocidnx -= 1
            self.dots.mkzero()
            self.plot()
    
    def nextsr(self):        
        if self.slocidnx < self.len-1:
            self.slocidnx += 1
            self.dots.mkzero()
            self.plot()
    
    

    def plot(self):
        loc = self.ROOT + "/dispersion/dispOri/src-"+self.cmpcc_loc[self.slocidnx]+".png"
        self.sc.set(self.cmpcc_loc[self.slocidnx])
        var1 = Image.open(loc)
        var2 = var1.resize((int(self.xmx-self.xmn), int(self.ymx-self.ymn)))
        self.imgs = ImageTk.PhotoImage(image=var2)
        self.cnvs.create_image((self.xmn, self.ymn), anchor=NW, image=self.imgs, tags='img')

    def ticks(self):
        """
        x and y ticks in canvas
        """
        dec = self.vmx - self.vmn
        for v in range(self.vmx, self.vmn-10, -10):
            y = int((self.ymx - self.ymn)*(v-self.vmn)/(self.vmx-self.vmn)) + self.ymn
            if v%50==0:
                t = v - dec            
                self.cnvs.create_line(self.xmn-self.pad*3, y, self.xmn, y, width= 2, tags='ln')
                self.cnvs.create_text(self.xmn-self.pad*5, y, text=t, angle=90)
                dec -= 100
            else:
                self.cnvs.create_line(self.xmn-self.pad*2, y, self.xmn, y, width= 1, tags='ln')
        f = self.fmx
        while f>=self.fmn:
            if f == 0:
                f = 1
            x = int((self.xmx - self.xmn)*(math.log10(f/self.fmn))/math.log10(self.fmx/self.fmn)) + math.log10(self.fmn)      
            if f==10 or f==self.fmn or f==self.fmx:                
                t = f            
                self.cnvs.create_line(self.xmn+x, self.ymx, self.xmn+x, self.ymx+self.pad*3, width= 2, tags='ln')
                self.cnvs.create_text(self.xmn+x-self.pad, self.ymx+self.pad*5, text=t)
            else:
                self.cnvs.create_line(self.xmn+x, self.ymx, self.xmn+x, self.ymx+self.pad*2, width= 1, tags='ln')
            #print(f, 10**math.floor(math.log10(f)))
            if math.floor(math.log10(f)) == math.log10(f):
                f -= 10**(math.floor(math.log10(f))-1)
            else:
                f -= 10**(math.floor(math.log10(f)))
            



    def mkdot(self, event):
        if self.flag==0:
            if self.xmn <= event.x <= self.xmx and self.ymn <= event.y <= self.ymx:
                x1 = event.x - self.pad 
                x2 = event.x + self.pad
                y1 = event.y - self.pad
                y2 = event.y + self.pad
                self.dots.mkpoint([x1, y1], [x2, y2], fill='#fff', width=1, tags='dot')
                
    
    def onDrag(self, start, end):
        if self.flag == 1:
            items = self.dots.hit_test(start, end)
            items = [x for x in items if x not in self.ignor]
            ids = []
            for x in self.dots.items:
                if x in items:
                    ids.append(x)
                    self.cnvs.delete(x)
            return ids

    def delit(self, e):
        id = e.widget.find_withtag('current')[0]
        self.cnvs.delete(id)
        
    
    


    def plotclorbar(self, w, hi=8):
        colors = ['#800000', '#a40000', '#c80000', '#ed0400', '#ff2200', '#ff3f00', '#ff5d00', '#ff7a00', '#ff9800', '#ffb600', '#ffd300', '#fbf100', '#e1ff16', '#c7ff30', '#adff49', '#94ff63', '#7aff7d', '#60ff97', '#46ffb1', '#2cffca', '#13fce4', '#00dcfe', '#00bcff', '#009cff', '#007cff', 
'#005cff', '#003cff', '#001cff', '#0000ff', '#0000e8', '#0000c4', '#00009f'] 
        s=st=0
        e = hi
        txt = [0, 0.25, 0.5, 0.75, 1]
        k=4
        for c in range(len(colors)):
            self.cnvs.create_rectangle(self.xmx+self.pad*5, self.ymn+s, self.xmx+self.pad*5+w, self.ymn+e, fill=colors[c], width=1, tags='img')
            s += hi
            if c in [0, 7, 15, 23, 31]:
                if s!=hi:
                    st = s
                self.cnvs.create_line(self.xmx+self.pad*5+w, self.ymn+st, self.xmx+self.pad*5+w + self.pad*1, self.ymn+st, width=1, tags='ln')
                self.cnvs.create_text(self.xmx+self.pad*5+w + self.pad*4, self.ymn+st,text=txt[k])
                k-=1                  
            e += hi 

    def flagset(self, f):
        self.flag = f
        if f:            
            self.dots.set_flg(1)
            self.dots.autodraw(fill="", width=2, command=self.onDrag)
        else:
            self.dots.set_flg(0)
            self.bind('<Button-1>', self.mkdot)
    
    def save(self):
        self.selfrq, self.selvel, self.selid = self.dots.save()
        self.samplesDict.update({str(self.cmpcc_loc[self.slocidnx]) : {"freq":self.selfrq, "vel": self.selvel, "ids": self.selid}})
        print(self.samplesDict)

    def show(self):
        if self.cmpcc_loc[self.slocidnx] in list(self.samplesDict.keys()):
            fvi_dict = self.samplesDict[self.cmpcc_loc[self.slocidnx]]
            self.dots.show(fvi_dict["freq"], fvi_dict['vel'], fvi_dict['ids'])
    
    def exportdata(self):
        keys = list(self.samplesDict.keys())
        fname = self.ROOT + '/inversion/inver.json'
        if os.path.isfile(fname):
            file = open(fname, 'r')        
            jobj = json.load(file)
            file.close()
            indent = list(jobj.keys())
            for x in keys:
                if x in jobj.keys():
                    jobj[x]["frequency"] = self.samplesDict[x]['freq']
                    jobj[x]["velocity"] = self.samplesDict[x]['vel']
                    jobj[x]["valid"] = ['True'] * len(self.samplesDict[x]['freq'])

            jobj2 = json.dumps(jobj, indent=len(indent))
            with open(fname, 'w') as f:
                f.write(jobj2)
                f.close()

def groups(glist, numPerGroup=2):
    result = []

    i = 0
    cur = []
    for item in glist:
        if not i < numPerGroup:
            result.append(cur)
            cur = []
            i = 0

        cur.append(item)
        i += 1

    if cur:
        result.append(cur)

    return result


def average(points):
    aver = [0, 0]

    for point in points:
        aver[0] += point[0]
        aver[1] += point[1]

    return aver[0]/len(points), aver[1]/len(points)


class Dots:

    def __init__(self, canvas,pad = 5, xmn=0, xmx=1000, ymn=0, ymx=1000, flg=0, fmx=100, fmn=0, vmx=500, vmn= 100):
        self.canvas = canvas
        self.item = None
        self.xmn = xmn
        self.xmx = xmx
        self.ymn = ymn
        self.ymx = ymx  
        self.fmx = fmx 
        self.fmn = fmn 
        self.vmx = vmx         
        self.vmn = vmn             
        self.flg = flg          # flag: 0-> adding point  # 1-> deleting point
        self.pad = pad    
        self.sample = dict()
        self.freq = list()
        self.vel = list()
        self.ids = list()
    
    def set_flg(self,f):
        self.flg = f

    def mkpoint(self, start, end, **opts):
        """Draw the circuler point"""
        ex = start[0] + self.pad - self.xmn
        ey = self.ymx - start[1] - self.pad
        self.freq.append(self.findf((self.xmx-self.xmn), ex))
        self.vel.append(self.findv((self.ymx-self.ymn), ey))
        id = self.canvas.create_oval(*(list(start)+list(end)), **opts)
        self.ids.append(id)
        print(self.freq, self.vel, self.ids)



    def draw(self, start, end, **opts):
        """Draw the rectangle"""
        if self.flg:
            return self.canvas.create_rectangle(*(list(start)+list(end)), **opts)
    
    def findf(self, mxlim, e):
        return round(10**((math.log10(self.fmx/self.fmn)*(e - math.log10(self.fmn))/mxlim + math.log10(self.fmn))), 2)

    def findv(self, mxlim, e):
        return round(((self.vmx-self.vmn)*e/mxlim + self.vmn), 2)

    def mkzero(self):
        self.freq = []
        self.vel = []
        self.ids = []

    def save(self):
        print(len(self.freq))
        for i in range(len(self.freq)-1):
            for j in range(i+1, len(self.freq)):
                print(f"{i} : {self.freq[i]}")
                print(f"{j} : {self.freq[j]}")
                #if self.freq[i] == self.freq[j]:
                #    if self.vel[i] == self.vel[j]:
                #        self.freq.pop(j)
                #        self.vel.pop(j)
                if self.freq[i] > self.freq[j]:
                    print("b2l")
                    temp = self.freq[i]
                    self.freq[i] = self.freq[j]
                    self.freq[j] = temp
                    temp = self.vel[i]
                    self.vel[i] = self.vel[j]
                    self.vel[j] = temp      

        return self.freq, self.vel, self.ids


    def autodraw(self, **opts):
        """Setup automatic drawing; supports command option"""
        if self.flg:
            self.start = None
            self.canvas.bind("<Button-1>", self.__update, '+')
            self.canvas.bind("<B1-Motion>", self.__update, '+')
            self.canvas.bind("<ButtonRelease-1>", self.__stop, '+')
    
            self._command = opts.pop('command', lambda *args: None)
            self.rectopts = opts
    
    def __update(self, event):
        if not self.start:
            self.start = [event.x, event.y]
            return

        if self.item is not None:
            self.canvas.delete(self.item)
        self.item = self.draw(self.start, (event.x, event.y), **self.rectopts)
        ids = []
        ids = self._command(self.start, (event.x, event.y))
        if ids:
            for id in ids:
                for i, idx in enumerate(self.ids):
                    if idx == id:                
                        self.ids.remove(self.ids[i])
                        self.freq.remove(self.freq[i])
                        self.vel.remove(self.vel[i])
                        break

    def __stop(self, event):
        self.start = None
        self.canvas.delete(self.item)
        self.item = None
        

    def hit_test(self, start, end, tags=None):
        """
        Check to see if there are items between the start and end
        """

        # first filter all of the items in the canvas
        if isinstance(tags, str):
            tags = [tags]

        if tags:
            tocheck = []
            for tag in tags:
                tocheck.extend(self.canvas.find_withtag(tag))
        else:
            tocheck = self.canvas.find_all()
        tocheck = [x for x in tocheck if x != self.item]

        self.items = tocheck
        # then figure out the box
        xlow = min(start[0], end[0])
        xhigh = max(start[0], end[0])

        ylow = min(start[1], end[1])
        yhigh = max(start[1], end[1])

        items = []
        for item in tocheck:
            x, y = average(groups(self.canvas.coords(item)))
            if (xlow < x < xhigh) and (ylow < y < yhigh):
                items.append(item)

        return items

    def show(self, fr, kv, id):
        pad = self.pad

        if len(fr) == len(kv) != None:
            for f, v in zip(fr, kv):
                #f = x -> findx
                #v = y -> findy   
                # start -> [findx-pad, findy-pad]
                # end -> [findx+pad, findy+pad]
                # create_oval(*(list(strat)+ list(end)), , fill='#fff', width=1, tags='dot')
               
                x = self.findx(f)
                y = self.findy(v)
                id = self.canvas.create_oval(x-pad, y-pad, x+pad, y+pad , fill='#fff', width=1, tags='dot')
                self.ids.append(id)
            print(self.ids)

 
    def findx(self, f):
        return int((self.xmx - self.xmn)*math.log10(f/self.fmn)/math.log10(self.fmx/self.fmn)) +  self.xmn 

    def findy(self, v):
        return int(self.ymx - (self.ymx - self.ymn)*(v-self.vmn)/(self.vmx-self.vmn))

 
if __name__=="__main__":
    main() 
