#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#Test GUI for Impact code
#by Zhicong liu @ 20170622 

import os, sys, threading, subprocess
import math

if sys.version_info[0] < 3:
    print("Error: need python version 3.x!")
    exit(0)

import tkinter as tk
from tkinter import messagebox,filedialog,ttk

import numpy as np

import PreProcessing
import ConvertFunc
import LatticeFrame
import ImpactTSet
import ImpactTPlot
import ImpactZSet
import ImpactZPlot

_MPINAME   ='mpirun'
_IMPACT_T_NAME ='ImpactTv1.8b.exe'
_IMPACT_Z_NAME ='ImpactZv17.exe'

_width = 560
_height= 633


PARTICLE_TYPE       = {'Electron'   :'510998.9461 -1.0',
                       'Proton'     :'938272081.3 1.0',
                       'Positron'   :'510998.9461 1.0',
                       'Antiproton' :'938272081.3 -1.0',
                       'Other'      :'Other_NONE'}

DISTRIBUTION_TYPE = {'Uniform'   :'1',
                     'Gauss'     :'2',
                     'WaterBag'  :'3',
                     'SemiGuass' :'4',
                     'KV'        :'5',
                     'Read'      :'16',
                     'Read Parmela'   :'24',
                     'Read Elegant'   :'25',
                     'CylcoldZSob'    :'27'}

DISTRIBUTION_Z_TYPE = {'Uniform'   :'1',
                     'Gauss'     :'2',
                     'WaterBag'  :'3',
                     'SemiGuass' :'4',
                     'KV'        :'5',
                     'Read'      :'19',
                     'Multi-charge-state WaterBag'   :'16',
                     'Multi-charge-state Gaussian'   :'17'}

DIAGNOSTIC_TYPE   = {'At given time'    :'1',
                     'At bunch centroid':'2',
                     'No output'        :'3'}

OUTPUT_Z_TYPE        = {'Standard'          :'1',
                        '95% Emittance'     :'2'}

BOUNDARY_TYPE        = {'Trans:open,  Longi:open'     :'1',
                        'Trans:open,  Longi:period'   :'2',
                        'Trans-Round, Longi-open'     :'3',
                        'Trans-Round, Longi-perod'    :'4',
                        'Trans:Rect,  Longi-open'     :'5',
                        'Trans-Rect,  Longi-perod'    :'6'}
INTEGRATOR_TYPE      = {'Linear'    :'1',
                        'Non Linear':'2'}

class ImpactMainWindow(tk.Tk):
    LABEL_TEXT =[
        "This is a test version of IMPACT user interface..."
        #"Actually, it is also my learning toy.",
        #"It is my first time to make a GUI with Python.",
        #"So, don't feel strange if u meet some bug.",
        #"If u meet a bug, or have any question, pls contact zhicongliu@lbl.gov\n"
        #"GOOD LUCK, HAVE FUN!"
        ]

    PLOTTYPE = {'Centriod location' :2,
                'Rms size'          :3,
                'Centriod momentum' :4,
                'Rms momentum'      :5,
                'Twiss'             :6,
                'Emittance'         :7}

    count = 0
    AccKernel = 'ImpactT'
    ImpactThread=threading.Thread()
    ImpactThread.setDaemon(True)
    def __init__(self, master=None):  
        tk.Tk.__init__(self, master)
        self.title("Impact")
        self.createWidgets(master)
        #self.master.iconbitmap()
          
        for item in ImpactMainWindow.LABEL_TEXT:
            print(item)    
    def createWidgets(self, master):
        self.t= startWindow(self)
        w1  = 400
        h1  = 300
        ws1 = self.t.winfo_screenwidth() # width of the screen
        hs1 = self.t.winfo_screenheight() # height of the screen
        x1 = (ws1/2) - (w1/2)
        y1 = (hs1/2) - (h1/2)
        self.t.overrideredirect(1)
        self.t.geometry('%dx%d+%d+%d' % (w1, h1, x1, y1))
        self.withdraw()
        
        
        self.frame_left = tk.Frame(self, height =_height, width = _width)
        self.frame_left.grid(row=0,column=0)
        
        self.frame_logo = tk.Frame(self.frame_left, height =_height/10, width = _width)
        self.frame_logo.pack(side = 'top')
        #print(resource_path(os.path.join('icon','ImpactT.gif')))
        try:
            self.logo_ImpactT = tk.PhotoImage(file = resource_path(os.path.join('icon','ImpactT.gif')), format="gif")
            self.logo_ImpactZ = tk.PhotoImage(file = resource_path(os.path.join('icon','ImpactZ.gif')), format="gif")
            self.label_logo  = tk.Label(self.frame_logo,image = self.logo_ImpactT)
            self.label_logo.pack(fill = 'y',side = 'left')
        except:
            self.label_logo  = tk.Label(self.frame_logo,bitmap='error')
            self.label_logo.pack(fill = 'y',side = 'left')
        
        '''
        LARGE_FONT= ("Helvetica", 20,'italic')
        self.button_switch = tk.Button(self.frame_logo)
        self.button_switch["text"]        = "Switch Kernel"
        #self.run["font"]        = LARGE_FONT
        self.button_switch["command"]     = lambda: self.switch()
        self.button_switch.pack(fill = 'both',expand =1,side = 'top',padx = 150)
        '''
        """Frame1: CPU GPU information"""
        self.frame_input1 = tk.LabelFrame(self.frame_logo, height =_height/10, width = _width, 
                                                text="Configuration")
        #self.frame_input1.grid(row=1,column=0,columnspan=2,sticky='W')
        self.frame_input1.pack(side = 'right')
        
        self.frame_CPU = tk.Frame(self.frame_input1, height =_height/10, width = _width)
        self.frame_CPU.pack(side = 'top')
        
        vcmd = (self.register(self.validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.label_noc1 = tk.Label(self.frame_CPU, text="# of cores at Y",pady=1)
        self.entry_noc1 = tk.Entry(self.frame_CPU, 
                                   validate = 'key',
                                   validatecommand = vcmd,
                                   width=4)
        self.entry_noc1.insert(0, '1')
        self.label_noc1.pack(side='left')
        self.entry_noc1.pack(side='left')

        self.label_noc2 = tk.Label(self.frame_CPU, text="# of cores at Z",pady=1)
        self.entry_noc2 = tk.Entry(self.frame_CPU, 
                                   validate = 'key',
                                   validatecommand = vcmd,
                                   width=4)
        self.entry_noc2.insert(0, '1')
        self.label_noc2.pack(side='left')
        self.entry_noc2.pack(side='left')
        
        self.GPUflag   = tk.IntVar()
        self.check_GPU  = tk.Checkbutton(self.frame_CPU, text="GPU", variable=self.GPUflag)
        self.check_GPU.pack(side='left')
        '''
        self.label_dic = tk.Label(self.frame_input1, text="Work Dictionary",pady=1)
        self.label_dic.pack(side='left')
        '''
        self.entry_dic = tk.Entry(self.frame_input1, width=45)
        #self.entry_dic.insert(0, os.path.dirname(os.path.abspath(__file__)))
        self.entry_dic.insert(0, sys.path[0])
        self.entry_dic.pack(side='left')
        
        self.button_dic = tk.Button(self.frame_input1)
        self.button_dic["text"]        = "..."
        self.button_dic["command"]     = lambda: self.changeDic()
        self.button_dic.pack(side = 'left')
        
        """Frame2: Time step"""
        self.frame1 = tk.Frame(self.frame_left, 
                               height =_height/2, width = _width)
        #self.frame_input2.grid(row=2,column=0,sticky='W')
        self.frame1.pack(fill = 'x',side = 'top')
        
        self.frame_input2 = tk.LabelFrame(self.frame1, 
                                          height =_height/2, width = _width, 
                                          text="Numerical parameters")
        #self.frame_input2.grid(row=2,column=0,sticky='W')
        self.frame_input2.pack(fill = 'x',side = 'left')
        rowtemp=1
        frame2width = 7
        
        """dt"""
        self.label_dt    = tk.Label(self.frame_input2, text="Timestep")
        self.entry_dt    = tk.Entry(self.frame_input2, 
                                    validate = 'key',
                                    validatecommand = vcmd,
                                    width=frame2width)
        self.entry_dt.insert(0, '1.0e-9')
        self.label_dt.grid(row=rowtemp,sticky='W')
        self.entry_dt.grid(row=rowtemp,column=1,sticky='E')
        rowtemp+=1

        """Nstep"""
        self.label_Nstep = tk.Label(self.frame_input2, text="# of step")
        self.entry_Nstep = tk.Entry(self.frame_input2,
                                    validate = 'key',
                                    validatecommand = vcmd,
                                    width=frame2width)
        self.entry_Nstep.insert(0, '100')
        self.label_Nstep.grid(row=rowtemp,sticky='W')
        self.entry_Nstep.grid(row=rowtemp,column=1,sticky='E')
        rowtemp+=1

        """Np"""
        self.label_Np    = tk.Label(self.frame_input2, text="Particle number")
        self.entry_Np    = tk.Entry(self.frame_input2,
                                    validate = 'key',
                                    validatecommand = vcmd,
                                    width=frame2width)
        self.entry_Np.insert(0, '1.6e5')
        self.label_Np.grid(row=rowtemp,sticky='W')
        self.entry_Np.grid(row=rowtemp,column=1,sticky='E')
        rowtemp+=1
        
        """Grid X"""
        self.label_Ngx   = tk.Label(self.frame_input2, text="Grid number X")
        self.entry_Ngx   = tk.Entry(self.frame_input2,
                                    validate = 'key',
                                    validatecommand = vcmd,
                                    width=frame2width)
        self.entry_Ngx.insert(0, '64')
        self.label_Ngx.grid(row=rowtemp,sticky='W')
        self.entry_Ngx.grid(row=rowtemp,column=1,sticky='E')
        rowtemp+=1
        
        """Grid Y"""
        self.label_Ngy   = tk.Label(self.frame_input2, text="Grid number Y")
        self.entry_Ngy   = tk.Entry(self.frame_input2,
                                    validate = 'key',
                                    validatecommand = vcmd,
                                    width=frame2width)
        self.entry_Ngy.insert(0, '64')
        self.label_Ngy.grid(row=rowtemp,sticky='W')
        self.entry_Ngy.grid(row=rowtemp,column=1,sticky='E')
        rowtemp+=1
        
        """Grid Z"""
        self.label_Ngz   = tk.Label(self.frame_input2, text="Grid number Z")
        self.entry_Ngz   = tk.Entry(self.frame_input2,
                                    validate = 'key',
                                    validatecommand = vcmd,
                                    width=frame2width)
        self.entry_Ngz.insert(0, '64')
        self.label_Ngz.grid(row=rowtemp,sticky='W')
        self.entry_Ngz.grid(row=rowtemp,column=1,sticky='E')
        rowtemp+=1

        
        """Twiss"""
        twisswidth = 9
        self.frame_Twiss = tk.LabelFrame(self.frame1, 
                                         height =_height/2, width = _width, text="Beam Twiss")
        self.frame_Twiss.pack(fill = 'y',side = 'left')

        self.twiss_s = []
        self.twiss_chara = ["sigma(m)","sigmaP","muxpx"]
        for column in range(3):
            label = tk.Label(self.frame_Twiss, text=self.twiss_chara[column], 
                            borderwidth=0,
                            width=twisswidth)
            label.grid(row=0, column=column+1, sticky="ns", padx=1, pady=1)
            self.twiss_s.append(label)
            
        self.twiss_t = []
        self.twiss_Tchara = ["alpha","beta","emittance"]
        for column in range(3):
            label = tk.Label(self.frame_Twiss, text=self.twiss_Tchara[column], 
                            borderwidth=0,
                            width=twisswidth)
            label.grid(row=0, column=column+1, sticky="ns", padx=1, pady=1)
            self.twiss_t.append(label)
        
        self.twiss_x = []
        self.twiss_xchara = ["X","Y","Z"]
        for row in range(3):
            label = tk.Label(self.frame_Twiss, text=self.twiss_xchara[row], 
                                 borderwidth=0, width=2)
            label.grid(row=row+1, column=0, sticky="ns", padx=1, pady=1)
            self.twiss_x.append(label)
        
        '''Twiss and Sigma string'''
        self.twiss_param = [["3.84562e-4","0.001" ,"0.0", "1.0","1.0","0.0","0.0"],
                            ["3.84562e-4","0.001" ,"0.0", "1.0","1.0","0.0","0.0"],
                            ["1.18618e-6","0.0014","0.0", "1.0","1.0","0.5","0.002"]]
        self.string_sigma = []
        for row in range(3):
            current_row = []
            for column in range(7):
                t = tk.StringVar(value=self.twiss_param[row][column])
                current_row.append(t)
            self.string_sigma.append(current_row)
        
        self.string_twiss = []
        for row in range(3):
            current_row = []
            for column in range(3):
                t = tk.StringVar(value='0')
                current_row.append(t)
            self.string_twiss.append(current_row)

            
        '''Sigma Entry'''   
        self.entry_sigma = []
        for row in range(3):
            current_row = []
            for column in range(3):
                label = tk.Entry(self.frame_Twiss, 
                                 textvariable=self.string_sigma[row][column], 
                                 borderwidth=0,
                                 width=twisswidth)
                label.grid(row=row+1, column=column+1, sticky="ns", padx=2, pady=1)
                current_row.append(label)
            self.entry_sigma.append(current_row)
        
        '''Twiss Entry'''   
        self.entry_twiss = []
        for row in range(3):
            current_row = []
            for column in range(3):
                label = tk.Entry(self.frame_Twiss, 
                                 textvariable=self.string_twiss[row][column], 
                                 borderwidth=0,
                                 width=twisswidth)
                label.grid(row=row+1, column=column+1, sticky="ns", padx=2, pady=1)
                current_row.append(label)
            self.entry_twiss.append(current_row)
        
        """Distribution"""
        self.frame_Dist = tk.Frame(self.frame_Twiss,
                                   height =_height/2, width = _width)
        self.frame_Dist.grid(row=4, column=0, rowspan=1, columnspan=4,sticky="nsew", padx=1, pady=1)
        
        self.label_dist    = tk.Label(self.frame_Dist, text="Distribution")
        self.label_dist.grid(row=0, column=0,
                             sticky="nw", padx=1, pady=1)
        self.distTypeComx = tk.StringVar(self.frame_Dist,'WaterBag')
        self.distType = ttk.Combobox(self.frame_Dist,text=self.distTypeComx,
                                     values=['Uniform', 'Gauss', 'SemiGauss',
                                             'WaterBag','KV', 'Read',
                                             'Read Parmela', 'Read Elegant',
                                             'CylcoldZSob'])
        self.distType.grid(row=0, column=1,
                             sticky="nsew", padx=1, pady=1)
        
        """Particle Type"""
        self.label_ptcType    = tk.Label(self.frame_Dist, text="Particle")
        self.label_ptcType.grid(row=1, column=0,
                                sticky="nw", padx=1, pady=1)
        self.ptcTypeComx = tk.StringVar(self.frame_Dist,'Electron')
        self.ptcMass     = tk.StringVar(self.frame_Dist,'510998.9461')
        self.ptcCharge   = tk.StringVar(self.frame_Dist,'-1.0')
        self.ptcType = ttk.Combobox(self.frame_Dist,text=self.ptcTypeComx,
                                     values=['Electron', 'Proton', 'Positron', 'Antiproton','Other'])
        self.ptcType.grid(row=1, column=1,
                          sticky="nsew", padx=1, pady=1)
        
        """Particle"""
        self.frame_Particle = tk.LabelFrame(self.frame1, 
                                            height =_height/2, width = _width, 
                                            text="Beam")
        self.frame_Particle.pack(fill = 'both',side = 'top')
        rowtemp=0
                
        """Current"""
        self.label_cur   = tk.Label(self.frame_Particle, text="Current(A)")
        self.entry_cur   = tk.Entry(self.frame_Particle,
                                    validate = 'key',
                                    validatecommand = vcmd,
                                    width=frame2width)
        self.entry_cur.insert(0, '0.13')
        self.label_cur.grid(row=rowtemp,sticky='W')
        self.entry_cur.grid(row=rowtemp,column=1,sticky='E')
        rowtemp+=1
        
        """Energy"""
        self.label_Ek    = tk.Label(self.frame_Particle, text="Energy(eV)")
        self.entry_Ek    = tk.Entry(self.frame_Particle,
                                    validate = 'key',
                                    validatecommand = vcmd,
                                    width=frame2width)
        self.entry_Ek.insert(0, '1.0')
        self.label_Ek.grid(row=rowtemp,sticky='W')
        self.entry_Ek.grid(row=rowtemp,column=1,sticky='E')
        rowtemp+=1
        
        """Frequency"""
        self.label_frq   = tk.Label(self.frame_Particle, text="Frequency(Hz)")
        self.entry_frq   = tk.Entry(self.frame_Particle,
                                    validate = 'key',
                                    validatecommand = vcmd,
                                    width=frame2width)
        self.entry_frq.insert(0, '1.3e9')
        self.label_frq.grid(row=rowtemp,sticky='W')
        self.entry_frq.grid(row=rowtemp,column=1,sticky='E')
        rowtemp+=1
        
        '''Advanced Setting'''
        self.Nbunch      = tk.StringVar(value='1')
        self.Dim         = tk.StringVar(value='6')
        self.Flagmap     = tk.StringVar(value='Linear')
        self.Flagerr     = tk.StringVar(value='0')
        self.Flagdiag    = tk.StringVar(value='At bunch centroid')
        self.Flagimag    = tk.StringVar(value='0')
        self.Zimage      = tk.StringVar(value='0.02')
        self.Flagbc      = tk.StringVar(value='Trans:open,  Longi:open')
        
        self.Xrad        = tk.StringVar(value='0.15')
        self.Yrad        = tk.StringVar(value='0.15')
        self.Zrad        = tk.StringVar(value='1.0e5')
        
        self.FlagRestart  = tk.StringVar(value='0')
        
        self.Nemission   = tk.StringVar(value='1')
        self.Temission   = tk.StringVar(value='8.0e-11')
        self.Tinitial    = tk.StringVar(value='0.0')
        
        '''Advanced Set for ImpactZ'''
        self.FlagOutput_Z    = tk.StringVar(value='Standard')
        self.ZperiodSize     = tk.StringVar(value='0.1')
        self.FlagSubcycle    = tk.StringVar(value='0')
        self.NpList          = tk.StringVar(value='16000')
        self.CurrentList     = tk.StringVar(value='0.0')
        self.SchargeList     = tk.StringVar(value='1.06577993775845e-09')
           
        self.button_AdvancedControl = tk.Button(self.frame1,text='Advanced Setting',
                                                command = self.makeAdvancedSet)
        self.button_AdvancedControl.pack(fill='both',expand=1,padx = 15, pady=20)
        LARGE_FONT= ("Helvetica", 10)
        self.button_AdvancedControl["font"]        = LARGE_FONT
        
        self.button_AdvancedControl.bind("<Enter>", lambda event, h=self.button_AdvancedControl: h.configure(bg="yellow"))
        self.button_AdvancedControl.bind("<Leave>", lambda event, h=self.button_AdvancedControl: h.configure(bg="#FFFFFF"))
        """Lattice"""
        self.frame_input3 = tk.LabelFrame(self.frame_left, 
                                          height =_height/6, width = _width,
                                          text="Lattice")
        self.frame_input3.pack(fill="both", expand=1, side=tk.TOP)
        
        self.lattice = LatticeFrame.LatticeFrameC(self.frame_input3, height = _height/6,width = _width)
        self.lattice.pack(fill="both", expand=1, side=tk.TOP)
              
        """Console"""
        self.frame_console = tk.LabelFrame(self.frame_left, 
                                           height =_height/5, width = _width,
                                           text="Console")
        self.frame_console.pack(fill="both", expand=1, side=tk.TOP)
        
        self.console_sv = tk.Scrollbar(self.frame_console, orient=tk.VERTICAL)
        self.console = LatticeFrame.ConsoleText(self.frame_console,
                                   width = LatticeFrame._TextWidth, height=LatticeFrame._TextHeight,
                                   bg='black',fg='green', yscrollcommand=self.console_sv.set)
        self.console_sv.config(command=self.console.yview)  
        self.console_sv.pack(fill="y", expand=0, side=tk.RIGHT, anchor=tk.N)  
        self.console.pack(fill="both", expand=1, side=tk.TOP)
        self.console.start()
        
        """Control"""
        
        self.frame_control = tk.Frame(self.frame_left, height =_height/5, width = _width)
        self.frame_control.pack(fill="both", expand=1, side=tk.TOP)
        '''
        self.frame_output = tk.LabelFrame(self.frame_control,
                                          height =_height/5, width = _width,
                                          text="Plot")
        self.frame_output.pack(side='left')
        
        self.frame_plotControl = PlotControlFrame(self.frame_output,
                                             height =_height/5, width = _width)
        self.frame_plotControl.pack(side='left')
        '''
        
        '''Final button'''
        LARGE_FONT= ("Helvetica", 20,'italic')                
        self.button_initial = tk.Button(self.frame_control)
        self.button_initial["text"]        = "Pre-Process"
        self.button_initial["font"]        = LARGE_FONT
        self.button_initial["command"]     = lambda: self.thread_it(self.preprocessing)
        self.button_initial.pack(fill = 'both',expand =1,side = 'left')
        
        self.button_initial.bind("<Enter>", lambda event, h=self.button_initial: h.configure(bg="green"))
        self.button_initial.bind("<Leave>", lambda event, h=self.button_initial: h.configure(bg="#FFFFFF"))
        
        self.button_run = tk.Button(self.frame_control)
        self.button_run["text"]         = "Run"
        self.button_run["font"]         = LARGE_FONT
        self.button_run["command"]      = lambda: self.thread_it(self.startImpact)
        self.button_run.pack(fill = 'both',expand =1,side = 'left')
        self.run_lock = threading.RLock()
        
        self.button_run.bind("<Enter>", lambda event, h=self.button_run: h.configure(bg="green"))
        self.button_run.bind("<Leave>", lambda event, h=self.button_run: h.configure(bg="#FFFFFF"))
        
        self.button_plot = tk.Button(self.frame_control)
        self.button_plot["text"]        = "Post-Process"
        self.button_plot["font"]        = LARGE_FONT
        self.button_plot["command"]     = lambda: self.makeAdvancedPlot()
        self.button_plot.pack(fill = 'both',expand =1,side = 'left')
        
        self.button_plot.bind("<Enter>", lambda event, h=self.button_plot: h.configure(bg="green"))
        self.button_plot.bind("<Leave>", lambda event, h=self.button_plot: h.configure(bg="#FFFFFF"))
        

        

        
        '''
        self.test = tk.Button(self.frame_left)
        self.test["text"] = "debug"
        self.test["command"] = lambda: self.debug()
        self.test.pack(fill = 'both',expand =1,side = 'top')
        
        self.test2 = tk.Button(self.frame_left)
        self.test2["text"] = "debug2"
        self.test2["command"] = lambda: self.debug2()
        self.test2.pack(fill = 'both',expand =1,side = 'top')
        '''
        self.updateTwissLock    =0
        
        for i in range(3):    
            for j in range(3):
                self.string_sigma[i][j].trace('w',lambda a,b,c,h=i: self.updateTwiss(h))
                self.string_twiss[i][j].trace('w',lambda a,b,c,h=i: self.updateSigma(h))
        for row in range(3):
            for column in range(3):
                self.string_sigma[row][column].set(self.twiss_param[row][column])
                pass
        self.updatePtcTypeLock  =0
        self.ptcTypeComx.trace('w', self.updatePtc)
        self.ptcMass.trace('w', self.updatePtcType)
        self.ptcCharge.trace('w', self.updatePtcType)
        
        
        '''degue'''
        #self.t.startImpactT(self)
        #self.makeAdvancedPlot()

    def debug(self):
        self.lattice.convertNtoW(self.lattice.get('0.0', tk.END))
    
    def debug2(self):
        self.lattice.updateHide()
        
    def changeDic(self):
        filename = filedialog.askdirectory(parent=self)
        if filename=='':
            return
                
        os.chdir(filename)
        
        self.entry_dic.delete(0, 'end')
        self.entry_dic.insert(0, filename)
        print(filename)
    
    def updatePtcType(self,*args):
        if self.updatePtcTypeLock ==1:
            return
        self.updatePtcTypeLock = 1
        
        invermap = dict(map(lambda t:(t[1],t[0]), PARTICLE_TYPE.items()))
        ptcFound = 0
        for key in invermap.keys():
            ptc = key.split()
            try:
                if math.isclose(float(ptc[0]), float(self.ptcMass.get()),rel_tol=1e-3):
                    if math.isclose(float(ptc[1]), float(self.ptcCharge.get()),rel_tol=1e-3):
                        self.ptcTypeComx.set(invermap[key])
                        ptcFound = 1
                        break
            except:
                pass
        if ptcFound==0:
            self.ptcTypeComx.set('Other')
        self.updatePtcTypeLock = 0
        
    def updatePtc(self,*args):
        if self.updatePtcTypeLock ==1:
            return
        self.updatePtcTypeLock = 1
        
        if self.ptcTypeComx.get() !='Other':
            try:
                ptc = PARTICLE_TYPE[self.ptcTypeComx.get()].split()
                self.ptcMass.set(ptc[0])
                self.ptcCharge.set(ptc[1])
            except:
                pass
        self.updatePtcTypeLock = 0
        
    def updateTwiss(self,i):
        if self.updateTwissLock ==1:
            return
        self.updateTwissLock = 1
        
        try:
            s1,s2,s3 = float(self.string_sigma[i][0].get()), float(self.string_sigma[i][1].get()), float(self.string_sigma[i][2].get())
            f, m, k  = float(self.entry_frq.get()),    float(self.ptcMass.get()),      float(self.entry_Ek.get())
            re=[0]*3
            if i==1 or i==0:
                re[0],re[1],re[2] = ConvertFunc.Sigma2Twiss(s1,s2,s3, f,m,k)
            if i==2:
                re[0],re[1],re[2] = ConvertFunc.Sigma2TwissZ(s1,s2,s3, f,m,k)    
            for j in range(3):
                if not math.isclose(re[j], float(self.string_twiss[i][j].get()),rel_tol=1e-06):
                    self.string_twiss[i][j].set(str(re[j]))
        except:
            #print('Error')
            pass
        self.updateTwissLock = 0
    def updateSigma(self,i):
        if self.updateTwissLock == 1:
            return
        self.updateTwissLock = 1

        try:
            s1,s2,s3 = float(self.string_twiss[i][0].get()), float(self.string_twiss[i][1].get()), float(self.string_twiss[i][2].get())
            f, m, k  = float(self.entry_frq.get()),    float(self.ptcMass.get()),      float(self.entry_Ek.get())
            re=[0]*3
            if i==1 or i==0:
                re[0],re[1],re[2] = ConvertFunc.Twiss2Sigma(s1,s2,s3, f,m,k)
            if i==2:
                re[0],re[1],re[2] = ConvertFunc.Twiss2SigmaZ(s1,s2,s3, f,m,k)    
            for j in range(3):
                if not math.isclose(re[j], float(self.string_sigma[i][j].get()),rel_tol=1e-06):
                    self.string_sigma[i][j].set(str(re[j]))
                else:
                    pass
        except:
            #print('Error')
            pass
        self.updateTwissLock = 0
    def preprocessing(self):
        try:
            os.chdir(self.entry_dic.get())
        except:
            print("Error: cannot get to the dictionary" + self.entry_dic.get())
            return
        
        if self.AccKernel=='ImpactT':
            np = self.save('ImpactT.in')
            self.button_run     .config(state='disable')
            self.button_plot    .config(state='disable')
            self.button_initial .config(state='disable')
            PreProcessing.main()
            self.load('ImpactT.in')
            self.button_run     .config(state='normal')
            self.button_plot    .config(state='normal')
            self.button_initial .config(state='normal')
        elif self.AccKernel=='ImpactZ':
            np = self.save('test.in')
            print('PreProcessing cannot use at Z code')
            #PreProcessing.main('Z')
        else:
            print('Cannot find kernel: '+self.AccKernel)
    
    def switch(self):
        if self.AccKernel=='ImpactT':
            self.switchToImpactZ()
        elif self.AccKernel == 'ImpactZ':
            self.switchToImpactT()
        print("Switch kernel to "+self.AccKernel)
        
    def switchToImpactZ(self):
        self.AccKernel='ImpactZ'
        try:
            self.AdvancedSet.destroy()
            self.AdvancedPlot.destroy()
        except:
            pass
        
        try:
            self.label_logo.config(image = self.logo_ImpactZ)
        except:
            self.label_logo.config(bitmap='error')
        self.entry_Nstep.config(state='disabled')
        self.entry_dt.config(state='disabled')
        
        distT=['Uniform', 'Gauss', 'SemiGauss',
               'WaterBag','KV', 'Read',
               'Multi-charge-state WaterBag',
               'Multi-charge-state Gaussian']
        if self.distTypeComx.get() not in distT:
            self.distTypeComx.set(distT[0])
        self.distType['values'] =distT
        self.lattice.titleZ()
        
    def switchToImpactT(self):
        self.AccKernel='ImpactT'
        try:
            self.AdvancedSet.destroy()
            self.AdvancedPlot.destroy()
        except:
            pass
        try:
            self.label_logo.config(image = self.logo_ImpactT)
        except:
            self.label_logo.config(bitmap='error')
        self.entry_Nstep.config(state='normal')
        self.entry_dt.config(state='normal')
        self.Flagmap.set('Linear')
        distT =['Uniform', 'Gauss', 'SemiGauss',
                'WaterBag','KV', 'Read',
                'Read Parmela', 'Read Elegant',
                'CylcoldZSob']
        if self.distTypeComx.get() not in distT:
            self.distTypeComx.set(distT[0])
        self.distType['values'] =distT
        self.lattice.titleT()
    def makeAdvancedSet(self):
        try:
            self.AdvancedSet.destroy()
        except:
            pass
        if self.AccKernel=='ImpactT':
            self.AdvancedSet = ImpactTSet.AdvancedSetFrame(self,self.AccKernel)
        elif self.AccKernel=='ImpactZ':
            self.AdvancedSet = ImpactZSet.AdvancedSetFrame(self,self.AccKernel)
        else:
            print('Cannot find kernel: '+self.AccKernel)
                    
            
    def makeAdvancedPlot(self):
        try:
            self.AdvancedPlot.destroy()
        except:
            pass
        if self.AccKernel=='ImpactT':
            self.AdvancedPlot = ImpactTPlot.AdvancedPlotControlFrame(self)  
        elif self.AccKernel=='ImpactZ':
            self.AdvancedPlot = ImpactZPlot.AdvancedPlotControlFrame(self)
        else:
            print('Cannot find kernel: '+self.AccKernel)
    def thread_it(self,func):
        self.button_run['state']='disabled'
        self.run_lock.acquire()
        ImpactThread=threading.Thread(target=func)
        ImpactThread.setDaemon(True)
        ImpactThread.start()
        self.run_lock.release()
        self.button_run['state']='normal'
        
    def startImpact(self):
        if self.AccKernel=='ImpactT':
            try:
                os.chdir(self.entry_dic.get())
            except:
                print("Error: cannot get to the dictionary" + self.entry_dic.get())
                return
            np = self.save('ImpactT.in')
            
            ImpactExe = os.path.join(sys.path[0],'src',_IMPACT_T_NAME)
            
            if np==1:
                cmd = ImpactExe
            elif np>1:
                cmd = _MPINAME+' -n '+str(np)+' '+ImpactExe
            print(cmd)
            p=subprocess.Popen(cmd,stdout=subprocess.PIPE,bufsize=1)
            for line in iter(p.stdout.readline,b''):
                print(('>>{}'.format(line.rstrip())))
            p.stdout.close()
        elif self.AccKernel=='ImpactZ':
            try:
                os.chdir(self.entry_dic.get())
            except:
                print("Error: cannot get to the dictionary" + self.entry_dic.get())
                return
            np = self.save('test.in')
            
            ImpactExe = os.path.join(sys.path[0],'src',_IMPACT_T_NAME)
    
            if np==1:
                cmd = ImpactExe
            elif np>1:
                cmd = _MPINAME+' -n '+str(np)+' '+ImpactExe
            
            p=subprocess.Popen(cmd,stdout=subprocess.PIPE,bufsize=1)
            for line in iter(p.stdout.readline,b''):
                print(('>>{}'.format(line.rstrip())))
            p.stdout.close()
        else:
            print('Cannot find kernel: '+self.AccKernel)
  
    def validate(self, action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type, widget_name):
        for word in text:
            if word in 'eE0123456789.-+*/':
                try:
                    #float(value_if_allowed)
                    return True
                except ValueError:
                    self.bell()
                    return False
            else:
                self.bell()
                return False
            

    def save(self,fileName):
        if self.AccKernel=='ImpactT':
            return self.saveImpactT(fileName)
        elif self.AccKernel=='ImpactZ':
            return self.saveImpactZ(fileName)
        else:
            print('Cannot find kernel: '+self.AccKernel)

    def saveImpactT(self,fileName):
        try:
            ImpactInput = open(fileName,'w')
        except:
            print(( "  ERROR! Can't save file as '" + fileName + "'"))
            return False    

        ImpactInput.writelines(["!This is the input file for ImpactT. It is generated by GUI.\n", 
                                 "!If you meet any bug, please contact zhicongliu@lbl.gov\n\n"])
        
        ImpactInput.write( str(int(self.entry_noc1.get()))+' '
                          +str(int(self.entry_noc2.get()))+' '
                          +('5\n' if self.GPUflag.get() else '0\n'))
        np = int(self.entry_noc1.get())*int(self.entry_noc2.get())
        
        ImpactInput.write( str(float(   self.entry_dt.get()))+' '
                          +str(int(     self.entry_Nstep.get())) + ' '
                          +str(int(     self.Nbunch.get()))+'\n')
        ImpactInput.write(str(int(      self.Dim.get()))+' '+
                          str(int(float(self.entry_Np.get())))+' '+
                          INTEGRATOR_TYPE[self.Flagmap.get()] +' '+
                          str(int(float(self.Flagerr.get()))) +' '+
                          DIAGNOSTIC_TYPE[  self.Flagdiag.get()]+ ' '+
                          str(int(      self.Flagimag.get()))+' '+
                          str(float(    self.Zimage.get())) +'\n')
        ImpactInput.write( str(int(     self.entry_Ngx.get()))+' '
                          +str(int(     self.entry_Ngy.get()))+' '
                          +str(int(     self.entry_Ngz.get()))+' '
                          #+BOUNDARY_TYPE[   self.Flagbc.get()]+' '
                          +'1 '
                          +str(float(   self.Xrad.get()))+' '
                          +str(float(   self.Yrad.get()))+' '
                          +str(float(   self.Zrad.get()))+'\n')
        
        ImpactInput.write(DISTRIBUTION_TYPE[self.distType.get()]    +' '+
                          str(int(float(self.FlagRestart.get())))   +' '+
                          '0 '+    #Flagsbstp
                          str(int(float(self.Nemission.get())))     +' '+
                          str(float(self.Temission.get()))          +'\n')

        for row in range(3):
            for column in range(7):
                ImpactInput.write(str(float(self.string_sigma[row][column].get()))+' ')
            ImpactInput.write('\n')
        '''
        if self.ptcType.get()=='Other':
            pass
        else:
            self.ptcMass.set(PARTICLE_TYPE[self.ptcType.get()].split()[0])
            self.ptcCharge.set(PARTICLE_TYPE[self.ptcType.get()].split()[1])
        '''
        ImpactInput.write(str(float(self.entry_cur.get()))+' '
                          +str(float(self.entry_Ek.get()))+' '
                          +self.ptcMass.get()     + ' '
                          +self.ptcCharge.get()   + ' '
                          +str(float(self.entry_frq.get()))+' '
                          +str(float(self.Tinitial.get()))
                          +'\n\n')
        
        ImpactInput.write('!===========LATTICE===========\n')
        lattice = self.lattice.getHide().splitlines()
        print(lattice)
        for line in lattice:
            if line !='':
                ImpactInput.write(line+'\n')
        ImpactInput.close()
        return np
    
    def saveImpactZ(self,fileName):
        try:
            ImpactInput = open(fileName,'w')
        except:
            print(( "  ERROR! Can't save file as '" + fileName + "'"))
            return False    

        ImpactInput.writelines(["!This is the input file for ImpactZ. It is generated by GUI.\n", 
                                "!If you meet any bug about the GUI, please contact zhicongliu@lbl.gov\n\n"])
        
        ImpactInput.write( str(int(self.entry_noc1.get()))+' '
                          +str(int(self.entry_noc2.get()))+' '
                          +('5\n' if self.GPUflag.get() else '0\n'))
        np = int(self.entry_noc1.get())*int(self.entry_noc2.get())
        
        ImpactInput.write(str(int(              self.Dim.get()))+' '+
                          str(int(float(        self.entry_Np.get())))+' '+
                          INTEGRATOR_TYPE[      self.Flagmap.get()] +' '+
                          str(int(float(        self.Flagerr.get()))) +' '+
                          OUTPUT_Z_TYPE[        self.FlagOutput_Z.get()]+ '\n')
        
        ImpactInput.write( str(int(     self.entry_Ngx.get()))+' '
                          +str(int(     self.entry_Ngy.get()))+' '
                          +str(int(     self.entry_Ngz.get()))+' '
                          +BOUNDARY_TYPE[   self.Flagbc.get()]+' '
                          +str(float(   self.Xrad.get()))+' '
                          +str(float(   self.Yrad.get()))+' '
                          +str(float(   self.ZperiodSize.get()))+'\n')
        
        ImpactInput.write(DISTRIBUTION_Z_TYPE[self.distType.get()]    +' '+
                          str(int(float(self.FlagRestart.get())))   +' '+
                          str(int(float(self.FlagSubcycle.get())))  +' '+
                          str(int(float(self.Nbunch.get())))  +'\n')
        
        ImpactInput.write(self.NpList.get()+ '\n')
        ImpactInput.write(self.CurrentList.get()+ '\n')
        ImpactInput.write(self.SchargeList.get()+ '\n')

        for row in range(3):
            for column in range(7):
                ImpactInput.write(str(float(self.string_sigma[row][column].get()))+' ')
            ImpactInput.write('\n')
        
        ImpactInput.write(str(float(self.entry_cur.get()))+' '
                          +str(float(self.entry_Ek.get()))+' '
                          +self.ptcMass.get()     + ' '
                          +self.ptcCharge.get()   + ' '
                          +str(float(self.entry_frq.get()))+' '
                          +str(float(self.Tinitial.get()))
                          +'\n\n')
        
        ImpactInput.write('!===========LATTICE===========\n')
        lattice = self.lattice.getHide().splitlines()
        print(lattice)
        for line in lattice:
            if line !='':
                ImpactInput.write(line+'\n')
        ImpactInput.close()
        #ImpactInput.write('0.1  5 20 2 7.5 7.5 0.0 6.0d-3 /\n\n\n')
        ImpactInput.close()
        return np
    
    def DtoE(self,word):
        if 'D' in word or 'd' in word: 
            try:
                temp = float(word.replace('D','E',1).replace('d','e',1))
                return str(temp)
            except:
                return word
        else:
            return word
        
    def readInput(self,inputFileName):
        try:
            fin = open(inputFileName,'r')
            linesList  = fin.readlines()
            fin.close()
        except:
            print(( "  ERROR! Can't open file '" + inputFileName + "'"))
            return False

        i=0
        while i < len(linesList):
            if linesList[i].lstrip()=='' or linesList[i].lstrip().startswith('!'):
                del linesList[i]
                i=i-1
            else:
                index = linesList[i].lstrip().find('!')
                if index==-1:
                    linesList[i]=linesList[i].strip()+'\n'
                else:
                    linesList[i]=linesList[i].lstrip()[:index].rstrip()+'\n'
            i=i+1
        linesList  = [line.split() for line in linesList ]
        
        for i in range(0,len(linesList)):
            for j in range(0,len(linesList[i])):
                linesList[i][j] = self.DtoE(linesList[i][j])
        return linesList
        
    def load(self,inputFileName):
        
        if self.AccKernel=='ImpactT':
            self.loadImpactT(inputFileName)
        elif self.AccKernel=='ImpactZ':
            self.loadImpactZ(inputFileName)
        else:
            print('Cannot find kernel: '+self.AccKernel)
        path = os.path.dirname(os.path.abspath(inputFileName))
        os.chdir(path)
        print(path)
        self.entry_dic.delete(0, 'end')
        self.entry_dic.insert(0,path)

    def loadImpactT(self,inputFileName):
        linesList = self.readInput(inputFileName)
        if linesList ==False:
            return
        '''CPU'''
        self.entry_noc1.delete(0,tk.END)
        self.entry_noc1.insert(0, linesList[0][0])
        self.entry_noc2.delete(0,tk.END)
        self.entry_noc2.insert(0, linesList[0][1])
        try:
            self.GPUflag.set(0 if int(linesList[0][2])==0 else 1)
        except:
            self.GPUflag.set(0)
        '''TimeStep'''
        self.entry_dt.delete(0,tk.END)
        self.entry_dt.insert(0, linesList[1][0])
        self.entry_Nstep.delete(0,tk.END)
        self.entry_Nstep.insert(0, linesList[1][1])
        self.Nbunch.set(linesList[1][2])
              
        '''Particle'''

        self.Dim.set(linesList[2][0])
        self.entry_Np.delete(0,tk.END)
        self.entry_Np.insert(0, linesList[2][1])

        #self.Flagmap.set(1)
        self.Flagerr.set(0 if int(linesList[2][3])==0 else 1)
        
        invermap = dict(map(lambda t:(t[1],t[0]), DIAGNOSTIC_TYPE.items()))
        if linesList[2][4] not in ['1','2','3']:
            linesList[2][4] = '3'
        self.Flagdiag.set(invermap[linesList[2][4]])
        
        self.Flagimag.set(0 if int(linesList[2][5])==0 else 1)
        self.Zimage.set(linesList[2][6])
        
        '''Grid'''
        self.entry_Ngx.delete(0,tk.END)
        self.entry_Ngx.insert(0, linesList[3][0])
        self.entry_Ngy.delete(0,tk.END)
        self.entry_Ngy.insert(0, linesList[3][1])
        self.entry_Ngz.delete(0,tk.END)
        self.entry_Ngz.insert(0, linesList[3][2])
        
        invermap = dict(map(lambda t:(t[1],t[0]), BOUNDARY_TYPE.items()))
        self.Flagbc.set(invermap[linesList[3][3]])
        
        self.Xrad.set(linesList[3][4])
        self.Yrad.set(linesList[3][5])
        self.Zrad.set(linesList[3][6])
        
        '''Distribution'''
        invermap = dict(map(lambda t:(t[1],t[0]), DISTRIBUTION_TYPE.items()))
        try:
            self.distTypeComx.set(invermap[linesList[4][0]])
        except:
            self.distTypeComx.set(invermap['3'])
            print('Cannot recognize distribution type, Set as waterbag')
        self.FlagRestart.set(0 if int(linesList[4][1])==0 else 1)
        self.Nemission.set(linesList[4][3])
        self.Temission.set(linesList[4][4])

        '''Twiss'''
        for row in range(3):
            for column in range(7):
                self.string_sigma[row][column].set(linesList[5+row][column])
        
        '''Particle Type'''
        invermap = dict(map(lambda t:(t[1],t[0]), PARTICLE_TYPE.items()))
        ptcFound = 0
        for key in invermap.keys():
            ptc = key.split()
            try:
                if math.isclose(float(ptc[0]), float(linesList[8][2]),rel_tol=1e-3):
                    if math.isclose(float(ptc[1]), float(linesList[8][3]),rel_tol=1e-3):
                        self.ptcTypeComx.set(invermap[key])
                        ptcFound = 1
                        break
            except:
                pass
        if ptcFound==0:
            self.ptcTypeComx.set('Other')
        self.ptcMass    .set(linesList[8][2])
        self.ptcCharge  .set(linesList[8][3])
         
        """Current"""
        self.entry_cur.delete(0, tk.END)
        self.entry_cur.insert(0, linesList[8][0])
        
        """Energy"""
        self.entry_Ek.delete(0, tk.END)
        self.entry_Ek.insert(0, linesList[8][1])
        
        """Frequency"""
        self.entry_frq.delete(0, tk.END)
        self.entry_frq.insert(0, linesList[8][4])
        
        self.Tinitial.set(linesList[8][5]) 
        
        """Lattice"""
        self.lattice.latticeTextHide.delete(0.0, tk.END)
        for lineSet in linesList[9:]:
            for word in lineSet:
                self.lattice.latticeTextHide.insert(tk.END, word + ' ')
            self.lattice.latticeTextHide.insert(tk.END,'\n')
        self.lattice.update()
        
    def loadImpactZ(self,inputFileName):
        linesList = self.readInput(inputFileName)
        if linesList ==False:
            return
        rowtemp=0
        '''CPU'''
        self.entry_noc1.delete(0,tk.END)
        self.entry_noc1.insert(0, linesList[rowtemp][0])
        self.entry_noc2.delete(0,tk.END)
        self.entry_noc2.insert(0, linesList[rowtemp][1])
        try:
            self.GPUflag.set(0 if int(linesList[rowtemp][2])==0 else 1)
        except:
            self.GPUflag.set(0)
        rowtemp+=1
              
        '''Particle'''
        self.Dim.set(linesList[rowtemp][0])
        self.entry_Np.delete(0,tk.END)
        self.entry_Np.insert(0, linesList[rowtemp][1])

        invermap = dict(map(lambda t:(t[1],t[0]), INTEGRATOR_TYPE.items()))
        self.Flagmap.set(invermap[linesList[rowtemp][2]])
        
        self.Flagerr.set(0 if int(linesList[rowtemp][3])==0 else 1)
        
        invermap = dict(map(lambda t:(t[1],t[0]), OUTPUT_Z_TYPE.items()))
        self.Flagdiag.set(invermap[linesList[rowtemp][4]])
        rowtemp+=1
        
        '''Grid'''
        self.entry_Ngx.delete(0,tk.END)
        self.entry_Ngx.insert(0, linesList[rowtemp][0])
        self.entry_Ngy.delete(0,tk.END)
        self.entry_Ngy.insert(0, linesList[rowtemp][1])
        self.entry_Ngz.delete(0,tk.END)
        self.entry_Ngz.insert(0, linesList[rowtemp][2])
        
        invermap = dict(map(lambda t:(t[1],t[0]), BOUNDARY_TYPE.items()))
        self.Flagbc.set(invermap[linesList[rowtemp][3]])
        
        self.Xrad.set(str(float(linesList[rowtemp][4])))
        self.Yrad.set(str(float(linesList[rowtemp][5])))
        self.ZperiodSize.set(str(float(linesList[rowtemp][6])))
        rowtemp+=1
        
        '''Distribution'''
        invermap = dict(map(lambda t:(t[1],t[0]), DISTRIBUTION_Z_TYPE.items()))
        self.distTypeComx.set(invermap[linesList[rowtemp][0]])
        self.FlagRestart.set( 0 if int(linesList[rowtemp][1])==0 else 1)
        self.FlagSubcycle.set(0 if int(linesList[rowtemp][2])==0 else 1)
        self.Nbunch.set(linesList[rowtemp][3])
        rowtemp+=1
        
        '''Multiple Charge State'''
        self.NpList.set(' '.join(linesList[rowtemp])) 
        rowtemp+=1
        self.CurrentList.set(' '.join(linesList[rowtemp])) 
        rowtemp+=1
        self.SchargeList.set(' '.join(linesList[rowtemp])) 
        rowtemp+=1
        
        '''Twiss'''
        for row in range(3):
            for column in range(7):
                self.string_sigma[row][column].set(linesList[rowtemp][column])
            rowtemp+=1

        '''Particle Type'''
        #print(PARTICLE_TYPE)
        invermap = dict(map(lambda t:(t[1],t[0]), PARTICLE_TYPE.items()))
        #print(invermap)
        ptcFound = 0
        for key in invermap.keys():
            ptc = key.split()
            try:
                if math.isclose(float(ptc[0]), float(linesList[rowtemp][2]),rel_tol=1e-3):
                    if math.isclose(float(ptc[1]), float(linesList[rowtemp][3]),rel_tol=1e-3):
                        self.ptcTypeComx.set(invermap[key])
                        ptcFound = 1
                        break
            except:
                pass
        if ptcFound==0:
            self.ptcTypeComx.set('Other')
        
        self.ptcMass    .set(linesList[rowtemp][2])
        self.ptcCharge  .set(linesList[rowtemp][3])
        #print(rowtemp,linesList[rowtemp])
            
        """Current"""
        self.entry_cur.delete(0, tk.END)
        self.entry_cur.insert(0, linesList[rowtemp][0])
        
        """Energy"""
        self.entry_Ek.delete(0, tk.END)
        self.entry_Ek.insert(0, linesList[rowtemp][1])
        
        """Frequency"""
        self.entry_frq.delete(0, tk.END)
        self.entry_frq.insert(0, linesList[rowtemp][4])
        
        self.Tinitial.set(linesList[rowtemp][5]) 
        
        rowtemp+=1
        """Lattice"""
        self.lattice.latticeTextHide.delete(0.0, tk.END)
        for lineSet in linesList[rowtemp:]:
            for word in lineSet:
                self.lattice.latticeTextHide.insert(tk.END, word + ' ')
            self.lattice.latticeTextHide.insert(tk.END,'\n')
        self.lattice.update()

class PlotControlFrame(tk.Frame):
    """Output"""
    def __init__(self, master=None, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)
        """Plot Control"""
        self.frame_plotButton = tk.Frame(self, height =_height/5, width = _width)
        self.frame_plotButton.grid(column=0, row = 0, pady=5 ,padx=10, sticky="e")
        
        self.frame_se = tk.Frame(self.frame_plotButton)
        self.frame_se.pack(side='left')
        self.frame_radio = tk.Frame(self.frame_se)
        self.frame_radio.pack(side='left')
        
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
        
        self.plotTypeComx = tk.StringVar(self.frame_se,'Rms size')
        self.plotType = ttk.Combobox(self.frame_se,text=self.plotTypeComx,
                                     values=list(ImpactMainWindow.PLOTTYPE.keys()))
        self.plotType.pack(side = 'left')
        
        self.plot = tk.Button(self.frame_plotButton,text='plot',command=self.makePlot)
        self.plot.pack(fill = 'both',expand =1,side = 'left',padx=10)
        
        self.t = ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0, row = 1, sticky="we")

           
        self.frame2 = tk.Frame(self, height =_height/5, width = _width)
        self.frame2.grid(column=0, row = 2, pady=5 ,padx=10, sticky="we")
        
        self.ParticlePlot = tk.Button(self.frame2,text='Phase Space Plot',
                               command = self.makeParticlePlot)
        self.ParticlePlot.pack(fill = 'both',expand =1,side = 'left')
        
        self.button_AdvancedPlot = tk.Button(self.frame2,text='Advanced Plot',
                               command = self.makeAdvancedPlot)
        self.button_AdvancedPlot.pack(fill = 'both',expand =1,side = 'left')
    
    def makePlot(self):
        print((self.plotType))
        
        PlotFileName='fort.'+str(self.plotDirct.get()+24)        
        yx=ImpactMainWindow.PLOTTYPE[self.plotType.get()]
        yl=yx if self.plotDirct.get()!=2 else yx-1

        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=ImpactTPlot.PlotFrame(plotWindow,PlotFileName,0,yl)
        l.pack()
        
    def makeParticlePlot(self):
        print((self.plotType))
        filename = filedialog.askopenfilename(parent=self)
        try:
            t=open(filename)
            t.close()
        except:
            return
        
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Phase Space Plot')
        
        l=ImpactTPlot.PhaseSpaceFrame(plotWindow,filename)
        l.pack()            
    def makeAdvancedPlot(self):
        try:
            self.AdvancedPlot.destroy()
        except:
            pass
        if self.AccKernel=='ImpactT':
            self.AdvancedPlot = ImpactTPlot.AdvancedPlotControlFrame(self)  

class startWindow(tk.Toplevel):
    def __init__(self, master, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf, **kw)
        self.title('Start')
        self.focus_set()
        
        self.frame = tk.Frame(self,width = 300,height = 200)
        self.frame.pack(fill = 'both',expand =1,side = 'top')
        LARGE_FONT= ("Helvetica", 20,'italic')     
        
        
        self.button_ImpactT = tk.Button(self.frame,text='ImpactT',font = LARGE_FONT,
                                        command = lambda: self.startImpactT(master))
        self.button_ImpactT.pack(fill = 'both',expand =1,side = 'left')
        
        self.button_ImpactT.bind("<Enter>", lambda event, h=self.button_ImpactT: h.configure(bg="yellow"))
        self.button_ImpactT.bind("<Leave>", lambda event, h=self.button_ImpactT: h.configure(bg="SystemButtonFace"))

        
        self.button_ImpactZ = tk.Button(self.frame,text='ImpactZ',font = LARGE_FONT,
                                        command = lambda: self.startImpactZ(master))
        self.button_ImpactZ.pack(fill = 'both',expand =1,side = 'left')
        
        self.button_ImpactZ.bind("<Enter>", lambda event, h=self.button_ImpactZ: h.configure(bg="yellow"))
        self.button_ImpactZ.bind("<Leave>", lambda event, h=self.button_ImpactZ: h.configure(bg="SystemButtonFace"))
        
        self.button_close = tk.Button(self,text='QUIT',font = LARGE_FONT,
                                        command = lambda: master.quit())
        self.button_close.pack(fill = 'both',expand =0,side = 'bottom')
        
        self.button_close.bind("<Enter>", lambda event, h=self.button_close: h.configure(bg="yellow"))
        self.button_close.bind("<Leave>", lambda event, h=self.button_close: h.configure(bg="SystemButtonFace"))
        

        
    def startImpactT(self,master):
        master.switchToImpactT()
        master.deiconify()
        self.destroy()
    def startImpactZ(self,master):
        master.switchToImpactZ()
        master.deiconify()
        self.destroy()
class MyMenu():
    def __init__(self, root):

        self.menubar = tk.Menu(root)
        
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Load", command=lambda: self.file_open(root))
        filemenu.add_command(label="Save", command=self.file_save)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.destroy)
        
        controlMenu = tk.Menu(self.menubar, tearoff=0)
        controlMenu.add_command(label="Switch to ImpactT", command=lambda: self.control_switchToImpactT(root))
        controlMenu.add_command(label="Switch to ImpactZ", command=lambda: self.control_switchToImpactZ(root))

        
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="Help", command=self.help_help)
        helpmenu.add_command(label="About", command=self.help_about)
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.menubar.add_cascade(label="Switch", menu=controlMenu)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        
        root.config(menu=self.menubar)
          
    def file_new(self):
        messagebox.showinfo('about', 'GUI author: Zhicong Liu \n verion 1.0 \n zhicongliu@lbl.gov ')
        pass
          
    def file_open(self,root):
        filename = filedialog.askopenfilename(parent=root)
        if filename=='':
            return
        root.load(filename)
        pass

    def file_save(self):
        filename = filedialog.asksaveasfilename(parent=root)
        if filename=='':
            return
        root.save(filename)
        pass
        
    def control_switchToImpactT(self,root):
        root.switchToImpactT()
        root.bell()
        pass
    
    def control_switchToImpactZ(self,root):
        root.switchToImpactZ()
        root.bell()
        pass
        
    def edit_copy(self):
        messagebox.showinfo('about', 'GUI author: Zhicong Liu \n verion 1.0 \n zhicongliu@lbl.gov ')
        pass
        
    def edit_paste(self):
        messagebox.showinfo('about', 'GUI author: Zhicong Liu \n verion 1.0 \n zhicongliu@lbl.gov ')
        pass
    
    def help_help(self):
        messagebox.showinfo('Help', 'Please refer "ImpactTv1.8.pdf" at this folder ')
        pass
    
    def help_about(self):
        messagebox.showinfo('About', ' Version 1.0 \n\n Kernel author: Ji Qiang \n jqiang@lbl.gov \n\n GUI author: Zhicong Liu \n zhicongliu@lbl.gov ')
        pass
        
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        print(1,base_path)
    except Exception:
        base_path = os.path.abspath(".")
    #print(base_path,relative_path,os.path.join(base_path, relative_path))
    return os.path.join(base_path, relative_path)

def quitConfirm():
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
        root.destroy()
 
 
'''
            pyinsteller -F -add-data "icon\ImpactT.gif;icon" ImpactGUI.py
'''

'''
1, label at plot
2, unit
3, plot size/location
4, emit growth divided by zero
ok:
1,3,4
'''

'''
1, density plot
'''