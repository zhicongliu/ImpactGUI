#!/usr/bin/env python
#This code is to plot the result from ImpactZ
#Zhicong@21/10/2016
#Input : fort.xx
#Output: figures about beam size and emittance
# plots are saved at '/post'

import tkinter as tk
from tkinter import ttk,filedialog
import time,os,sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, FormatStrFormatter 
from scipy.stats import gaussian_kde
import numpy as np
import matplotlib as plt


_height=300
_width =200

ADVANCED_PLOT_TYPE= {'Centriod location (m)'    :2,
                     'Rms size (m)'             :3,
                     'Centriod momentum (MC)'   :4,
                     'Rms momentum (MC)'        :5,
                     'Twiss'                    :6,
                     'Emittance (m-rad)'        :7}

class AdvancedPlotControlFrame(tk.Toplevel):
    """Output"""
            
    def __init__(self, master=None, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf, **kw)
        self.title('ImpactT Plot')
        self.focus_set()  
        """Plot Control"""
        self.frame_plotButton = tk.Frame(self)
        self.frame_plotButton.grid(column=0, row = 0, pady=5 ,padx=10, sticky="we")
        
        self.frame_radio = tk.Frame(self.frame_plotButton)
        self.frame_radio.pack(side='top')
        
        self.plotDirct = tk.IntVar()
        self.plotDirct.set(0)
        self.frame_radio.x = tk.Radiobutton(self.frame_radio, variable=self.plotDirct,
                                           text="X", value=0)
        self.frame_radio.x.pack(side='left')
        self.frame_radio.y = tk.Radiobutton(self.frame_radio, variable=self.plotDirct,
                                           text="Y", value=1)
        self.frame_radio.y.pack(side='left')
        self.frame_radio.z = tk.Radiobutton(self.frame_radio, variable=self.plotDirct,
                                           text="Z", value=2)
        self.frame_radio.z.pack(side='left')
        
        self.plotTypeComx = tk.StringVar(self.frame_plotButton,'Rms size (m)')
        self.plotType = ttk.Combobox(self.frame_plotButton,text=self.plotTypeComx,
                                     width = 20,
                                     values=list(ADVANCED_PLOT_TYPE.keys()))
        self.plotType.pack(side = 'top')
        self.plot = tk.Button(self.frame_plotButton,text='plot',command=self.makePlot)
        self.plot.pack(fill = 'both',expand =1,side = 'top',padx=10)
        
        self.t = ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0, row = 1, sticky="we")

           
        self.frame2 = tk.Frame(self, height =_height/5, width = _width)
        self.frame2.grid(column=0, row = 2, pady=5 ,padx=10, sticky="nswe")
        
        rowN=0
        
        self.button_overall = tk.Button(self.frame2,text='Overall',
                               command = self.overallPlot)
        self.button_overall.grid(row = rowN, column=0,  pady=5 ,padx=5, columnspan = 2, sticky="nswe")
        rowN+=1
        
        self.button_emitGrowth      = tk.Button(self.frame2,text='EmitGrowth',
                                                command = self.emitGrowthPlot)
        self.button_emitGrowth      .grid(row = rowN, column=0, pady=5 ,padx=5, sticky="nswe")
        self.button_Ek              = tk.Button(self.frame2,text='Kinetic Energy',
                                                command = lambda: self.energyPlot(3,'Kinetic Energy (MeV)'))
        self.button_Ek              .grid(row = rowN, column=1, pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.button_beta            = tk.Button(self.frame2,text='Beta',
                                                command = lambda: self.energyPlot(4,'Beta'))
        self.button_beta            .grid(row = rowN, column=0, pady=5 ,padx=5, sticky="nswe")
        self.button_gamma           = tk.Button(self.frame2,text='Gamma',
                                                command = lambda: self.energyPlot(2,'Gamma'))
        self.button_gamma           .grid(row = rowN, column=1, pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.button_rmax            = tk.Button(self.frame2,text='Rmax',
                                                command = lambda: self.energyPlot(5,'Rmax (m)'))
        self.button_rmax            .grid(row = rowN, column=0, pady=5 ,padx=5, sticky="nswe")
        self.button_dw              = tk.Button(self.frame2,text='Rms delta E',
                                                command = lambda: self.energyPlot(6,'Rms delta E (MC^2)'))
        self.button_dw              .grid(row = rowN, column=1, pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.button_Temperature         = tk.Button(self.frame2,text='Temperature Plot',
                                                    command = self.makeTemperaturePlot)
        self.button_Temperature         .grid(row = rowN, column=0,  pady=5 ,padx=5, sticky="nswe")
        self.button_Loss                = tk.Button(self.frame2,text='live Particle #',
                                                    command = self.liveParticlePlot)
        self.button_Loss                .grid(row = rowN, column=1,  pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.t = ttk.Separator(self.frame2, orient=tk.HORIZONTAL).grid(column=0, row = rowN, columnspan=2,sticky="we")        
        rowN+=1
        
        self.max                        = tk.Button(self.frame2,text='Max amplitude',
                                                    command = self.maxPlot)
        self.max                        .grid(row = rowN, column=0,  pady=5 ,padx=5, columnspan=2,sticky="nswe")
        rowN+=1
        
        self.button_3order              = tk.Button(self.frame2,text='3 order parameter',
                                                    command = self.make3orderPlot)
        self.button_3order              .grid(row = rowN, column=0,  pady=5 ,padx=5, sticky="nswe")
        self.button_4order              = tk.Button(self.frame2,text='4 order parameter',
                                                    command = self.make4orderPlot)
        self.button_4order              .grid(row = rowN, column=1,  pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.t = ttk.Separator(self.frame2, orient=tk.HORIZONTAL).grid(column=0, row = rowN, columnspan=2,sticky="we")        
        rowN+=1

        
        self.button_Particle            = tk.Button(self.frame2,text='Phase Space Plot',
                                                    command = self.ParticlePlot)
        self.button_Particle            .grid(row = rowN, column=0,  pady=5 ,padx=5, sticky="nswe")
        self.button_ParticleDesity1D    = tk.Button(self.frame2,text='Density1D',
                                                    command = self.ParticleDensityPlot1D)
        self.button_ParticleDesity1D    .grid(row = rowN, column=1,  pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.button_ParticleDensity     = tk.Button(self.frame2,text='Density2D (by Grid)',
                                                    command = self.ParticleDensityPlot)
        self.button_ParticleDensity     .grid( row = rowN, column=0, pady=5 ,padx=5, sticky="nswe")
        self.button_ParticleDensity2    = tk.Button(self.frame2,text='Density2D (by Ptc)',
                                                    command = self.ParticleDensityPlot2)
        self.button_ParticleDensity2    .grid(row = rowN, column=1, pady=5 ,padx=5, sticky="nswe")
        rowN+=1



    def overallPlot(self):
        print(self.__class__.__name__)

        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=OverallFrame(plotWindow)
        l.pack()    
        
    def energyPlot(self,y,ylabel):
        print(sys._getframe().f_back.f_code.co_name)

        plotWindow = tk.Toplevel(self)
        plotWindow.title(sys._getframe().f_back.f_code.co_name)
        
        l=PlotFrame(plotWindow,'fort.18',1,y,ylabel)
        l.pack()
    
    def emitGrowthPlot(self):
        print(sys._getframe().f_back.f_code.co_name)

        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=EmitGrowthFrame(plotWindow)
        l.pack()   
        
    def makeTemperaturePlot(self):
        print((self.plotType))

        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=TemperatureFrame(plotWindow)
        l.pack()
        
    def liveParticlePlot(self):
        print(sys._getframe().f_back.f_code.co_name)

        plotWindow = tk.Toplevel(self)
        plotWindow.title(sys._getframe().f_back.f_code.co_name)
        
        l=PlotFrame(plotWindow,'fort.28',1,4,'Live particle number')
        l.pack()
        
    def ParticlePlot(self):
        print(self.__class__.__name__)
        filename = filedialog.askopenfilename(parent=self)
        try:
            t=open(filename)
            t.close()
        except:
            return
        
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Phase Space Plot')
        
        l=ParticleFrame(plotWindow,filename,1.0)
        l.pack() 
                
    def ParticleDensityPlot(self):
        print(self.__class__.__name__)
        fileName=filedialog.askopenfilename(parent=self)
        try:
            t=open(fileName)
            t.close()
        except:
            return
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=ParticleDensityFrame_weight2D(plotWindow,fileName,1.0)
        l.pack()
        
    def ParticleDensityPlot1D(self):
        print(self.__class__.__name__)
        fileName=filedialog.askopenfilename(parent=self)
        try:
            t=open(fileName)
            t.close()
        except:
            return
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=ParticleDensityFrame_weight1D(plotWindow,fileName,1.0)
        l.pack()
                    
    def ParticleDensityPlot2(self):
        print(self.__class__.__name__)
        fileName=filedialog.askopenfilename(parent=self)
        try:
            t=open(fileName)
            t.close()
        except:
            return
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=ParticleDensityFrame2D_slow(plotWindow,fileName,1.0)
        l.pack()
        
    def makePlot(self):
        print(self.__class__.__name__)
        
        PlotFileName='fort.'+str(self.plotDirct.get()+24)        
        yx=ADVANCED_PLOT_TYPE[self.plotType.get()]
        yl=yx if self.plotDirct.get()!=2 else yx-1

        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=PlotFrame(plotWindow,PlotFileName,1,yl,self.plotType.get())
        l.pack()
        

    def maxPlot(self):
        print(self.__class__.__name__)
        filename = 'fort.27'
        try:
            t=open(filename)
            t.close()
        except:
            return
        
        plotWindow = tk.Toplevel(self)
        plotWindow.title('maxPlot')
        
        l=PlotMaxFrame(plotWindow,filename)
        l.pack() 
    def make3orderPlot(self):
        print(self.__class__.__name__)
        filename = 'fort.29'
        try:
            t=open(filename)
            t.close()
        except:
            return
        
        plotWindow = tk.Toplevel(self)
        plotWindow.title('make3orderPlot')
        
        l=Plot3orderFrame(plotWindow,filename)
        l.pack() 
        
    def make4orderPlot(self):
        print(self.__class__.__name__)
        filename = 'fort.30'
        try:
            t=open(filename)
            t.close()
        except:
            return
        
        plotWindow = tk.Toplevel(self)
        plotWindow.title('make4orderPlot')
        
        l=Plot4orderFrame(plotWindow,filename)
        l.pack() 

class PlotBaseFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.fig = Figure(figsize=(7,5), dpi=100)
        self.subfig = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        

        
class PlotFrame(tk.Frame):
    def __init__(self, parent,PlotFileName,xl,yl,labelY):
        tk.Frame.__init__(self, parent)
        #LARGE_FONT= ("Verdana", 12)
        #label = tk.Label(self, font=LARGE_FONT,
        #                 text='plot '+PlotFileName+
        #                 ' use '+str(xl)+':'+str(yl))
        #label.pack(pady=10,padx=10)

        try:
            fin = open(PlotFileName,'r')
        except:
            print(( "  ERRPR! Can't open file '" + PlotFileName + "'"))
            return
        
        linesList  = fin.readlines()
        fin .close()
        linesList  = [line.split() for line in linesList ]
        x   = [float(xrt[xl]) for xrt in linesList]
        y   = [float(xrt[yl]) for xrt in linesList]
        
        fig = Figure(figsize=(7,5), dpi=100)
        subfig = fig.add_subplot(111)
        subfig.plot(x,y)
        subfig.set_xlabel('Z (m)')
        subfig.set_ylabel(labelY)

        xmajorFormatter = FormatStrFormatter('%2.2E')
        subfig.yaxis.set_major_formatter(xmajorFormatter)
        box = subfig.get_position()
        subfig.set_position([box.x0*1.45, box.y0*1.1, box.width, box.height])
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def quit(self):
        self.destroy()
                
class OverallFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.fig = Figure(figsize=(12,5), dpi=100)
        self.subfig = []
        self.subfig.append(self.fig.add_subplot(221))
        self.subfig.append(self.fig.add_subplot(222))
        self.subfig.append(self.fig.add_subplot(223))
        self.subfig.append(self.fig.add_subplot(224))

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.plot()
    def plot(self):
        picNum = 4
        fileList    = [[]*2]*picNum
        saveName    = []
        labelList   = [[]*2]*picNum
        xdataList   = [[]*2]*picNum
        ydataList   = [[]*2]*picNum
        xyLabelList = [[]*2]*picNum
        
        xl  = 2
        saveName.append('sizeX')
        fileList[0]     = ['fort.24','fort.27']
        labelList[0]    = ['rms.X','max.X']
        xdataList[0]    = [xl,xl]
        ydataList[0]    = [4,3]
        xyLabelList[0]  = ['z drection (m)','beam size in X (m)']
        
        saveName.append('sizeY')
        fileList[1]     = ['fort.25','fort.27']
        labelList[1]    = ['rms.Y','max.Y']
        xdataList[1]    = [xl,xl]
        ydataList[1]    = [4,5]
        xyLabelList[1]  = ['z drection (m)','beam size in Y (m)']
        
        saveName.append('sizeZ')
        fileList[2]     = ['fort.26','fort.27']
        labelList[2]    = ['rms.Z','max.Z']
        xdataList[2]    = [xl,xl]
        ydataList[2]    = [3,7]
        xyLabelList[2]  = ['z drection (m)','beam size in Z (m)']
        
        saveName.append('emitXY')
        fileList[3]     = ['fort.24','fort.25']
        labelList[3]    = ['emit.nor.X','emit.nor.Y']
        xdataList[3]    = [xl,xl]
        ydataList[3]    = [8,8]
        xyLabelList[3]  = ['z drection (m)','emittance at X and Y (m*rad)']
        
        lineType = ['r-','b--']

        for i in range(0,picNum):
            for j in range(0,2):
                try:
                    fin = open(fileList[i][j],'r')
                except:
                    print("ERRPR Can't open file ' " + fileList[i][j] + "'")
                    return
                linesList  = fin.readlines()
                fin .close()
                linesList  = [line.split() for line in linesList ]
                xId = xdataList[i][j]-1
                yId = ydataList[i][j]-1
                x   = [xrt[xId] for xrt in linesList]
                y   = [xrt[yId] for xrt in linesList]
                self.subfig[i].plot(x, y, lineType[j], linewidth=2, label=labelList[i][j])
            self.subfig[i].set_xlabel(xyLabelList[i][0])
            self.subfig[i].set_ylabel(xyLabelList[i][1])
            box = self.subfig[i].get_position()
            self.subfig[i].set_position([box.x0*1.1, box.y0*1.1, box.width, box.height *0.88])
            xmajorFormatter = FormatStrFormatter('%2.2E')
            self.subfig[i].yaxis.set_major_formatter(xmajorFormatter)  
            self.subfig[i].legend(loc='upper center', bbox_to_anchor=(0.5, 1.21),fancybox=True, shadow=True, ncol=5)
        self.canvas.draw()
        
class EmitGrowthFrame(PlotBaseFrame):
    def __init__(self, parent):
        PlotBaseFrame.__init__(self, parent)
        self.plot()
    def plot(self):        
        fileList        = ['fort.24','fort.25']
        xdataList       = [2,2]
        ydataList       = [8,8]
        xyLabelList     = ['Z (m)','Avg emit growth in X and Y']
        
        lineType = ['r-','b--']
        
        try:
            fin1 = open(fileList[0],'r')
        except:
            print("  ERRPR! Can't open file '" + fileList[0] + "'")
            return
        try:
            fin2 = open(fileList[1],'r')
        except:
            print("  ERRPR! Can't open file '" + fileList[1] + "'")
            return
        linesList1  = fin1.readlines()
        linesList2  = fin2.readlines()
        fin1 .close()
        fin2 .close()
        linesList1  = [line.split() for line in linesList1 ]
        linesList2  = [line.split() for line in linesList2 ]
        xId = xdataList[0]-1
        yId = ydataList[0]-1
        try:
            x   = [float(xrt[xId]) for xrt in linesList1]
            start = (float(linesList1[0][yId]) + float(linesList2[0][yId]))/2
            if start < 1.0e-16:
                start=1.0e-16
            y   = [(float(linesList1[k][yId]) + float(linesList2[k][yId]))/2 / start -1 for k in range(len(linesList1))]
        except:
            print("  ERRPR! Can't read data '" + fileList[1] + "'")
        
        self.subfig.cla()
        self.subfig.plot(x, y, lineType[0], linewidth=2, label='emit.growth')
        box = self.subfig.get_position()
        self.subfig.set_position([box.x0*1.4, box.y0, box.width, box.height])
        self.subfig.set_xlabel(xyLabelList[0])
        self.subfig.set_ylabel(xyLabelList[1])
        self.subfig.legend()
        
        self.canvas.draw()
        
class TemperatureFrame(PlotBaseFrame):
    def __init__(self, parent):
        PlotBaseFrame.__init__(self, parent)
        self.plot()
    def plot(self):
        arg=['ct','fort.24','fort.25','fort.26']
        labelList= ['X','Y','Z']
        lineType = ['-','--',':']
        col      = ['b','g','r']
        linew    = [2,2,3]
        picNum = len(arg) - 1
        plotPath = './post'
        if os.path.exists(plotPath) == False:
            os.makedirs(plotPath)
            
        self.subfig.cla()
        for i in range(1,picNum+1):
            try:
                fin = open(arg[i],'r')
            except:
                print( "  ERRPR! Can't open file '" + arg[i] + "'")
                return
    
            linesList  = fin.readlines()
            fin .close()
            linesList  = [line.split() for line in linesList ]
            x   = [float(xrt[0]) for xrt in linesList]
            yl=5
            if i==3:
                yl=4
            y   = [float(xrt[yl])*float(xrt[yl]) for xrt in linesList]
            self.subfig.plot(x, y, color = col[(i-1)],linestyle=lineType[i-1], linewidth=linew[i-1],label=labelList[i-1])
        
        box = self.subfig.get_position()
        self.subfig.set_position([box.x0*1.2, box.y0, box.width, box.height])    
        self.subfig.set_xlabel('T (s)')
        self.subfig.set_ylabel('Temperature')
        self.subfig.legend()
        
        self.canvas.draw()

class PlotHighOrderBaseFrame(tk.Frame):
    ParticleDirec = {'X (m)'    :2,
                     'Px (MC)'   :3,
                     'Y (m)'    :4,
                     'Py (MC)'   :5,
                     'Z (m)'    :6,
                     'Pz (MC)'   :7}
    data = np.array([])
    def __init__(self, parent, PlotFileName):
        tk.Frame.__init__(self, parent)
        try:
            self.data = np.loadtxt(PlotFileName)
        except:
            print(( "  ERROR! Can't open file '" + PlotFileName + "'"))
            return
        
        self.data = np.transpose(self.data)
        self.frame_PlotParticleControl = tk.Frame(self)
        self.frame_PlotParticleControl.pack()
        
        self.label_x    = tk.Label(self.frame_PlotParticleControl, text="Direction:")
        self.label_x.pack(side='left')

        self.ppc1Value  = tk.StringVar(self.frame_PlotParticleControl,'X (m)')
        self.ppc1       = ttk.Combobox(self.frame_PlotParticleControl,text=self.ppc1Value,
                                       width=6,
                                       values=['X (m)', 'Px (MC)', 'Y (m)', 'Py (MC)','Z (m)','Pz (MC)'])
        self.ppc1.pack(fill = 'both',expand =1,side = 'left')
        
        LARGE_FONT= ("Verdana", 12)
        self.button_ppc=tk.Button(self.frame_PlotParticleControl)
        self.button_ppc["text"] = "Plot"
        self.button_ppc["foreground"] = "blue"
        self.button_ppc["bg"] = "red"
        self.button_ppc["font"] = LARGE_FONT
        self.button_ppc["command"] = self.plot
        self.button_ppc.pack(fill = 'both',expand =1,side = 'left')

        x   = 1
        y   = self.ParticleDirec[self.ppc1.get()]
        
        self.fig = Figure(figsize=(7,5), dpi=100)
        self.subfig = self.fig.add_subplot(111)
        self.subfig.scatter(self.data[x],self.data[y],s=1)
        
        xmajorFormatter = FormatStrFormatter('%2.2E')
        self.subfig.yaxis.set_major_formatter(xmajorFormatter)
        box = self.subfig.get_position()
        self.subfig.set_position([box.x0*1.4, box.y0, box.width, box.height])

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.plot()
        
class PlotMaxFrame(PlotHighOrderBaseFrame):
    def __init__(self, parent,ifile):    
        PlotHighOrderBaseFrame.__init__(self, parent, ifile)
        
    def plot(self):
        y   = self.ParticleDirec[self.ppc1.get()]
        
        self.subfig.cla()
        self.subfig.plot(self.data[0],self.data[y])
        
        xmajorFormatter = FormatStrFormatter('%2.2E')
        self.subfig.yaxis.set_major_formatter(xmajorFormatter)

        self.subfig.set_xlabel('Z (m)')
        if y%2==0:
            self.subfig.set_ylabel('Max '+ self.ppc1.get())
        else:
            self.subfig.set_ylabel('Max '+ self.ppc1.get())
        self.canvas.draw()
        
class Plot3orderFrame(PlotHighOrderBaseFrame):
    def __init__(self, parent,ifile):    
        PlotHighOrderBaseFrame.__init__(self, parent, ifile)
        
    def plot(self):
        y   = self.ParticleDirec[self.ppc1.get()]
        
        self.subfig.cla()
        self.subfig.plot(self.data[0],self.data[y])
        
        xmajorFormatter = FormatStrFormatter('%2.2E')
        self.subfig.yaxis.set_major_formatter(xmajorFormatter)

        self.subfig.set_xlabel('Z (m)')
        if y%2==0:
            self.subfig.set_ylabel('cubic root of 3rd'+ self.ppc1.get())
        else:
            self.subfig.set_ylabel('cubic root of 3rd'+ self.ppc1.get())
        self.canvas.draw()
        
class Plot4orderFrame(PlotHighOrderBaseFrame):
    def __init__(self, parent,ifile):    
        PlotHighOrderBaseFrame.__init__(self, parent, ifile)
        
    def plot(self):
        y   = self.ParticleDirec[self.ppc1.get()]
        
        self.subfig.cla()
        self.subfig.plot(self.data[0],self.data[y])
        
        xmajorFormatter = FormatStrFormatter('%2.2E')
        self.subfig.yaxis.set_major_formatter(xmajorFormatter)

        self.subfig.set_xlabel('Z (m)')
        if y%2==0:
            self.subfig.set_ylabel('square square root of 4th '+ self.ppc1.get())
        else:
            self.subfig.set_ylabel('square square root of 4th '+ self.ppc1.get())
        self.canvas.draw()
    
class ParticleBaseFrame(tk.Frame):
    ParticleDirecWithUnit = {'X (mm)'       :0,
                     'Px (MC)'      :1,
                     'Y (mm)'       :2,
                     'Py (MC)'      :3,
                     'Z (mm)'       :4,
                     'Pz (MC)'      :5}
    ParticleDirec = {'X'       :0,
                     'Px'      :1,
                     'Y'       :2,
                     'Py'      :3,
                     'Z'       :4,
                     'Pz'      :5}
    DefaultUnit = ['mm','MC','mm','MC','mm','MC']
    data = np.array([])
    def __init__(self, parent, PlotFileName,scaling):
        tk.Frame.__init__(self, parent)
        try:
            self.data = np.loadtxt(PlotFileName)
        except:
            print( "  ERROR! Can't open file '" + PlotFileName + "'")
            return
        
        self.data = np.transpose(self.data)

        for i in range(0,6,2):
            try:
                self.data[i] = self.data[i] * 1000 * scaling
            except:
                print( "Warning: Can't read the column " + str(i)+" @ '" + PlotFileName + "'")
                    
        self.frame_PlotParticleControl = tk.Frame(self)
        self.frame_PlotParticleControl.pack()
        
        self.label_scalingX        = tk.Label(self.frame_PlotParticleControl, text="ScalingX:")
        self.label_scalingX.pack(side='left')
        self.scalingX       = tk.Entry(self.frame_PlotParticleControl,  width=7)
        self.scalingX.insert(0, '1.0')
        self.scalingX.pack(fill = 'both',expand =1,side = 'left')
        
        self.label_scalingY        = tk.Label(self.frame_PlotParticleControl, text="ScalingY:")
        self.label_scalingY.pack(side='left')
        self.scalingY       = tk.Entry(self.frame_PlotParticleControl,  width=7)
        self.scalingY.insert(0, '1.0')
        self.scalingY.pack(fill = 'both',expand =1,side = 'left')
        
        self.label_unitX        = tk.Label(self.frame_PlotParticleControl, text="UnitAxi1:")
        self.label_unitX.pack(side='left')
        self.unitX       = tk.Entry(self.frame_PlotParticleControl,  width=6)
        self.unitX.insert(0, 'mm')
        self.unitX.pack(fill = 'both',expand =1,side = 'left')
        
        self.label_unitY        = tk.Label(self.frame_PlotParticleControl, text="UnitAxi2:")
        self.label_unitY.pack(side='left')
        self.unitY       = tk.Entry(self.frame_PlotParticleControl,  width=6)
        self.unitY.insert(0, 'MC')
        self.unitY.pack(fill = 'both',expand =1,side = 'left')
        
        self.label_x        = tk.Label(self.frame_PlotParticleControl, text="Axi1:")
        self.label_x.pack(side='left')

        self.ppc1Value  = tk.StringVar(self.frame_PlotParticleControl,'X')
        self.ppc1       = ttk.Combobox(self.frame_PlotParticleControl,text=self.ppc1Value,
                                       width=5,
                                       values=['X', 'Px', 'Y', 'Py','Z','Pz'])
        #                               values=['X (mm)', 'Px (MC)', 'Y (mm)', 'Py (MC)','Z (deg)','Pz (MC)'])
        self.ppc1.pack(fill = 'both',expand =1,side = 'left')
        
        self.label_y        = tk.Label(self.frame_PlotParticleControl, text="Axi2:")
        self.label_y.pack(side='left')
        self.ppc2Value  = tk.StringVar(self.frame_PlotParticleControl,'Px')
        self.ppc2       = ttk.Combobox(self.frame_PlotParticleControl,text=self.ppc2Value,
                                       width=5,
                                       values=['X', 'Px', 'Y', 'Py','Z','Pz'])
        #                               values=['X (mm)', 'Px (MC)', 'Y (mm)', 'Py (MC)','Z (deg)','Pz (MC)'])
        self.ppc2.pack(fill = 'both',expand =1,side = 'left')
        
        LARGE_FONT= ("Verdana", 12)
        self.button_ppc=tk.Button(self.frame_PlotParticleControl)
        self.button_ppc["text"] = "Plot"
        self.button_ppc["foreground"] = "red"
        self.button_ppc["bg"] = "yellow"
        self.button_ppc["font"] = LARGE_FONT
        self.button_ppc["command"] = self.plot
        self.button_ppc.pack(fill = 'both',expand =1,side = 'right')
        
        self.ppc1Value.trace('w',lambda a,b,c,direc='X': self.update(direc))
        self.ppc2Value.trace('w',lambda a,b,c,direc='Y': self.update(direc))

        x   = self.ParticleDirec[self.ppc1.get()]
        y   = self.ParticleDirec[self.ppc2.get()]
        
        self.fig = Figure(figsize=(7,6), dpi=100)
        self.subfig = self.fig.add_subplot(111)
        self.subfig.scatter(self.data[x],self.data[y],s=1)
        
        box = self.subfig.get_position()
        self.subfig.set_position([box.x0*1.4, box.y0, box.width, box.height])
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
    def update(self,direction):
        if direction == 'X':
            self.scalingX.delete(0, 'end')
            self.scalingX.insert(0, '1.0')
            self.unitX.delete(0, 'end')
            try:
                ind = self.ParticleDirec[self.ppc1.get()]
                self.unitX.insert(0, self.DefaultUnit[ind])
            except:
                pass
        elif direction == 'Y':
            self.scalingY.delete(0, 'end')
            self.scalingY.insert(0, '1.0')
            self.unitY.delete(0, 'end')
            try:
                ind = self.ParticleDirec[self.ppc2.get()]
                self.unitY.insert(0, self.DefaultUnit[ind])
            except:
                pass
        else:
            print("Warning: no this direction")

class ParticleFrame(ParticleBaseFrame):
    def __init__(self, parent, PlotFileName,scaling):
        ParticleBaseFrame.__init__(self, parent,PlotFileName,scaling)
        self.plot()
        
    def plot(self):
        xData   = self.data[self.ParticleDirec[self.ppc1.get()]] * float(self.scalingX.get())
        yData   = self.data[self.ParticleDirec[self.ppc2.get()]] * float(self.scalingY.get())
        
        #self.fig.clf()
        #self.subfig = self.fig.add_subplot(111)
        self.subfig.cla()
        
        self.subfig.scatter(xData,yData,s=1)
        #self.subfig.relim()
        self.subfig.autoscale()
        
        sciFormatter = FormatStrFormatter('%2.2e')
        xMax = np.max(abs(xData))
        yMax = np.max(abs(yData))
        if xMax>1000 or xMax<0.001:
            self.subfig.xaxis.set_major_formatter(sciFormatter)
        if yMax>1000 or yMax<0.001:
            self.subfig.yaxis.set_major_formatter(sciFormatter)
        
        self.subfig.set_xlabel(self.ppc1.get()+' ('+self.unitX.get()+')')
        self.subfig.set_ylabel(self.ppc2.get()+' ('+self.unitY.get()+')')
        self.canvas.draw()
        
    def quit(self):
        self.destroy()
        


class ParticleDensityFrame_weight1D(ParticleBaseFrame):
    def __init__(self, parent, PlotFileName,scaling):
        ParticleBaseFrame.__init__(self, parent,PlotFileName,scaling)
        self.ppc2.pack_forget()
        self.label_y.pack_forget()
        
        self.unitY.pack_forget()
        self.label_unitY.pack_forget()
        
        self.label_scalingY.pack_forget()
        self.scalingY.pack_forget()
        
        self.plot()
        
    def plot(self):
        xData   = self.data[self.ParticleDirec[self.ppc1.get()]] * float(self.scalingX.get())
        
        self.subfig.cla()
        
        nx = 200
        
        xMax = np.max(xData)
        xMin = np.min(xData)
        
        hx = (xMax-xMin)/(nx-1)
        
        count = np.zeros(nx)
        tickx  = [xMin + i * (xMax-xMin)/(nx-1) for i in range(nx)]
        
        for i in range(0,len(xData)):
            ix = int((xData[i] - xMin)/hx)
            if ix<0:
                ix=0
                print("Error at density plot weight 1D! ix<0")
            if ix>=nx-1:
                ix=nx-2
            ab = (xData[i] - (xMin+ix*hx))/hx
            
            count[ix  ] += 1.0-ab
            count[ix+1] += ab
            pass
        count = count/np.max(count)
        self.subfig.fill_between(tickx,0,count)#,extent=(xMin,xMax,yMin,yMax))#plt.cm.ocean)
        #plt.colorbar()
        
        
        sciFormatter = FormatStrFormatter('%2.2e')
        xMax = np.max(abs(xData))
        if xMax>1000 or xMax<0.001:
            self.subfig.xaxis.set_major_formatter(sciFormatter)
        
        self.subfig.set_xlabel(self.ppc1.get()+' ('+self.unitX.get()+')')
        self.subfig.set_ylabel('Density')

        self.canvas.draw()        
class ParticleDensityFrame_weight2D(ParticleBaseFrame):
    def __init__(self, parent, PlotFileName,scaling):
        ParticleBaseFrame.__init__(self, parent,PlotFileName,scaling)
        
        self.label_gridSizeX        = tk.Label(self.frame_PlotParticleControl, text="GridSize:")
        self.label_gridSizeX.pack(side='left')
        self.gridSizeX       = tk.Entry(self.frame_PlotParticleControl,  width=5)
        self.gridSizeX.insert(0, '200')
        self.gridSizeX.pack(fill = 'both',expand =1,side = 'left')
        
        '''
        self.label_gridSizeY        = tk.Label(self.frame_PlotParticleControl, text="GridSizeY:")
        self.label_gridSizeY.pack(side='left')
        self.gridSizeY       = tk.Entry(self.frame_PlotParticleControl,  width=5)
        self.gridSizeY.insert(0, '100')
        self.gridSizeY.pack(fill = 'both',expand =1,side = 'left')
        '''
        
        '''
        self.button_ppc["text"] = "ContourPlot"
        LARGE_FONT= ("Verdana", 12)
        self.button_ppc1=tk.Button(self.frame_PlotParticleControl)
        self.button_ppc1["text"] = "gridDensity"
        self.button_ppc1["foreground"] = "red"
        self.button_ppc1["bg"] = "yellow"
        self.button_ppc1["font"] = LARGE_FONT
        self.button_ppc1["command"] = lambda:self.plot(flag = 'gridDensity')
        self.button_ppc1.pack(fill = 'both',expand =1,side = 'right')
        '''
        
        self.plot()
        
    def plot(self,flag='ContourPlot'):
        xData   = self.data[self.ParticleDirec[self.ppc1.get()]] * float(self.scalingX.get())
        yData   = self.data[self.ParticleDirec[self.ppc2.get()]] * float(self.scalingY.get())
        
        self.subfig.cla()
        
        try:
            nx=int(self.gridSizeX.get())
            ny=int(self.gridSizeX.get())
        except:
            nx=200
            ny=200
            print("Warning: cannot get gridSizeX or gridSizeY, set to 100")
        if nx<10:
            nx=10
        if ny<10:
            ny=10
        xMax = np.max(xData)
        yMax = np.max(yData)
        xMin = np.min(xData)
        yMin = np.min(yData)
        
        hx = (xMax-xMin)/(nx-1)
        hy = (yMax-yMin)/(ny-1)
        
        count = np.zeros([ny,nx])
        
        for i in range(0,len(xData)):
            ix = int((xData[i] - xMin)/hx)
            iy = int((yData[i] - yMin)/hy)
            if ix<0:
                ix=0
                print("Error at density plot weight 2D! ix<0")
            if iy<0:
                iy=0
                print("Error at density plot weight 2D! iy<0")
            if ix>=nx-1:
                ix=nx-2
            if iy>=ny-1:
                iy=ny-2
            ab = (xData[i] - (xMin+ix*hx))/hx
            cd = (yData[i] - (yMin+iy*hy))/hy
            
            #iy=ny-iy-2
            count[iy  ,ix  ] += (1.0-ab) * (1.0-cd)
            count[iy+1,ix  ] += (    ab) * (1.0-cd) 
            count[iy  ,ix+1] += (1.0-ab) * (    cd) 
            count[iy+1,ix+1] += (    ab) * (    cd) 
            pass
        
        count[count == 0.0] = -0.0000001
        tmap = plt.cm.jet
        print(tmap)
        tmap.set_under('white',0.)
        #tmap.set_bad('white',0.)
        if flag=='ContourPlot':
            x = np.linspace(xMin, xMax, nx)
            y = np.linspace(yMin, yMax, ny)
            self.msh = self.subfig.contourf(x, y, count,level=12,interpolation='gaussian',cmap =tmap , vmin=0.0001)
        else:
            self.msh = self.subfig.imshow(count, origin = "lower", interpolation='bilinear', 
                                      cmap=tmap,vmin=0.0000001,
                                      extent=(xMin,xMax,yMin,yMax),aspect="auto")#plt.cm.ocean)
        #self.msh = self.subfig.imshow(count, origin = "lower", interpolation='nearest', 
        #                              cmap='gray_r',vmin=0.0000001,
        #                              extent=(xMin,xMax,yMin,yMax),aspect="auto")#plt.cm.ocean)
        #self.cax = self.subfig.add_collection(self.msh)
        #plt.colorbar(self.mshself.cax)
        
        sciFormatter = FormatStrFormatter('%2.2e')
        xMax = np.max(abs(xData))
        yMax = np.max(abs(yData))
        if xMax>1000 or xMax<0.001:
            self.subfig.xaxis.set_major_formatter(sciFormatter)
        if yMax>1000 or yMax<0.001:
            self.subfig.yaxis.set_major_formatter(sciFormatter)
        '''
        ntick = 7
        tickx  = [i*(nx-0)/(ntick-1) for i in range(ntick)]
        labelx = ['{:2.2e}'.format(xMin+i*(xMax-xMin)/(ntick-1)) for i in range(ntick)]
        self.subfig.set_xticks(tickx)
        self.subfig.set_xticklabels(labelx)
        
        ticky  = [i*(ny-0)/(ntick-1) for i in range(ntick)]
        labely = ['{:2.2e}'.format(yMin+i*(yMax-yMin)/(ntick-1)) for i in range(ntick)]
        self.subfig.set_yticks(ticky)
        self.subfig.set_yticklabels(labely)
'''
        self.subfig.set_xlabel(self.ppc1.get()+' ('+self.unitX.get()+')')
        self.subfig.set_ylabel(self.ppc2.get()+' ('+self.unitY.get()+')')

        self.canvas.draw()
        
class ParticleDensityFrame1D(ParticleBaseFrame):
    def __init__(self, parent, PlotFileName,scaling):
        ParticleBaseFrame.__init__(self, parent,PlotFileName,scaling)
        self.ppc2.pack_forget()
        self.label_y.pack_forget()
        
        self.label_scalingY.pack_forget()
        self.scalingY.pack_forget()
        self.plot()
        
    def plot(self):
        xData   = self.data[self.ParticleDirec[self.ppc1.get()]] * float(self.scalingX.get())
        
        self.subfig.cla()
        self.subfig.hist(xData,bins=100)

        sciFormatter = FormatStrFormatter('%2.2e')
        xMax = np.max(abs(xData))
        if xMax>1000 or xMax<0.001:
            self.subfig.xaxis.set_major_formatter(sciFormatter)
        
        self.subfig.set_xlabel(self.ppc1.get()+' ('+self.unitX.get()+')')
        self.subfig.set_ylabel('Density')

        self.canvas.draw()
        
class ParticleDensityFrame2D(ParticleBaseFrame):
    def __init__(self, parent,ifile,scaling):    
        ParticleBaseFrame.__init__(self, parent, ifile, scaling)
        self.plot()
        
    def plot(self):
        xData   = self.data[self.ParticleDirec[self.ppc1.get()]] * float(self.scalingX.get())
        yData   = self.data[self.ParticleDirec[self.ppc2.get()]] * float(self.scalingY.get())
        
        self.subfig.cla()
        self.subfig.hist2d(xData,yData,(100, 100),cmap = 'jet')

        sciFormatter = FormatStrFormatter('%2.2e')
        xMax = np.max(abs(xData))
        yMax = np.max(abs(yData))
        if xMax>1000 or xMax<0.001:
            self.subfig.xaxis.set_major_formatter(sciFormatter)
        if yMax>1000 or yMax<0.001:
            self.subfig.yaxis.set_major_formatter(sciFormatter)
        
        self.subfig.set_xlabel(self.ppc1.get()+' ('+self.unitX.get()+')')
        self.subfig.set_ylabel(self.ppc2.get()+' ('+self.unitY.get()+')')

        self.canvas.draw()
        
class ParticleDensityFrame2D_slow(ParticleBaseFrame):
    def __init__(self, parent, PlotFileName,scaling):
        ParticleBaseFrame.__init__(self, parent,PlotFileName,scaling)
        self.plot()
        
    def plot(self):
        xData   = self.data[self.ParticleDirec[self.ppc1.get()]] * float(self.scalingX.get())
        yData   = self.data[self.ParticleDirec[self.ppc2.get()]] * float(self.scalingY.get())
        
        self.subfig.cla()       
        '''Calculate the point density'''
        xy = np.vstack([xData,yData])
        z = gaussian_kde(xy)(xy)
    
        '''Sort the points by density, so that the densest points are plotted last'''
        idx = z.argsort()
        x, y, z = xData[idx], yData[idx], z[idx]        
        
        self.subfig.scatter(x, y, c=z, s=10, edgecolor='')

        sciFormatter = FormatStrFormatter('%2.2e')
        xMax = np.max(abs(xData))
        yMax = np.max(abs(yData))
        if xMax>1000 or xMax<0.001:
            self.subfig.xaxis.set_major_formatter(sciFormatter)
        if yMax>1000 or yMax<0.001:
            self.subfig.yaxis.set_major_formatter(sciFormatter)
        
        self.subfig.set_xlabel(self.ppc1.get()+' ('+self.unitX.get()+')')
        self.subfig.set_ylabel(self.ppc2.get()+' ('+self.unitY.get()+')')

        self.canvas.draw()    
