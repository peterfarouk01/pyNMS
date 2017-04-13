# NetDim (contact@netdim.fr)

import tkinter as tk
from os.path import join
from objects.objects import *
from tkinter import ttk
from PIL import ImageTk
from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict
from graph_generation.network_dimension import NetworkDimension
from miscellaneous.decorators import update_paths

class ViewMenu(ScrolledFrame):
    
    def __init__(self, notebook, controller):
        self.controller = controller
        super().__init__(
                         notebook, 
                         width = 200, 
                         height = 600, 
                         borderwidth = 1, 
                         relief = 'solid'
                         )
                         
        font = ('Helvetica', 8, 'bold')
        
        # label frame to switch between site and network view
        lf_site_display = Labelframe(self.infr)
        lf_site_display.text = 'Viewing mode'
        lf_site_display.grid(0, 0, sticky='nsew')
        
        # label frame to switch between logical and geographical coordinates
        lf_coordinates = Labelframe(self.infr)
        lf_coordinates.text = 'Coordinates'
        lf_coordinates.grid(1, 0, sticky='nsew')
        
        self.dict_image = {}
        
        self.dict_size_image = {
        'network_view': (100, 100),
        'site': (100, 100),
        'logical_coord': (100, 100),
        'geo_coord': (100, 100)
        }
        
        for image_type, image_size in self.dict_size_image.items():
            x, y = image_size
            img_path = join(self.controller.path_icon, image_type + '.png')
            img_pil = ImageTk.Image.open(img_path).resize(image_size)
            img = ImageTk.PhotoImage(img_pil)
            self.dict_image[image_type] = img
        
        self.type_to_button = {}
        font = ('Helvetica', 8, 'bold')
        self.current_view = 'network'
                
        # site view
        self.network_view_button = TKButton(self.infr)
        self.network_view_button.config(
                                        image = self.dict_image['network_view'],
                                        text = 'Network view',
                                        compound = 'top', 
                                        font = font
                                        )
        self.network_view_button.command = lambda: self.switch_view('network')
        self.network_view_button.config(width=125, height=125, relief='sunken')
        self.network_view_button.grid(0, 0, 2, 2, padx=20, in_=lf_site_display)
        
        self.site_view_button = TKButton(self.infr)
        self.site_view_button.config(
                                     image = self.dict_image['site'],
                                     text = 'Site view',
                                     compound = 'top', 
                                     font = font
                                     )
        self.site_view_button.command = lambda: self.switch_view('site')
        self.site_view_button.config(width=125, height=125)
        self.site_view_button.grid(0, 2, 2, 2, padx=20, in_=lf_site_display)
        
        self.logical_coord_button = TKButton(self.infr)
        self.logical_coord_button.config(
                                         image = self.dict_image['logical_coord'],
                                         text = 'Logical coordinates',
                                         compound = 'top', 
                                         font = font
                                         )
        self.logical_coord_button.command = self.logical_coordinates
        self.logical_coord_button.config(width=125, height=125)
        self.logical_coord_button.grid(0, 0, 2, 2, padx=20, in_=lf_coordinates)
        
        self.geo_coord_button = TKButton(self.infr)
        self.geo_coord_button.config(
                                     image = self.dict_image['geo_coord'],
                                     text = 'Geo coordinates',
                                     compound = 'top', 
                                     font = font
                                     )
        self.geo_coord_button.command = self.geographical_coordinates
        self.geo_coord_button.config(width=125, height=125)
        self.geo_coord_button.grid(0, 2, 2, 2, padx=20, in_=lf_coordinates)
        
    @update_paths
    def logical_coordinates(self):
        self.scenario.move_to_logical_coordinates(*self.scenario.so['node'])
        
    @update_paths
    def geographical_coordinates(self):
        self.scenario.move_to_geographical_coordinates(*self.scenario.so['node'])
        
    @update_paths
    def switch_view(self, view):
        self.current_view = view        
        if view == 'site':
            self.site_view_button.config(relief='sunken')
            self.network_view_button.config(relief='raised')
            self.scenario.pack_forget()
            self.site_scenario.pack()
            # update current scenario
            self.scenario = self.site_scenario
        else:
            # view is network
            self.site_view_button.config(relief='raised')
            self.network_view_button.config(relief='sunken')
            self.scenario.pack_forget()
            self.network_scenario.pack()
            # update current scenario
            self.scenario = self.network_scenario
            
    @update_paths
    def enter_site(self, site):
        self.scenario.pack_forget()
        site.scenario.pack()
        self.scenario = site.scenario
        self.current_view = site
        # destroy the pwindow of the site scenario
        self.site_scenario.pwindow.destroy()
                    