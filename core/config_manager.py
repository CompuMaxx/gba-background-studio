# core/config_manager.py
import configparser
import os
from pathlib import Path

class ConfigManager:
    APP_VERSION = "2.0.1"
    
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')

            if not self.config.has_option('SETTINGS', 'version') or \
               self.config.get('SETTINGS', 'version') != self.APP_VERSION:
                self.config.set('SETTINGS', 'version', self.APP_VERSION)
                self.save_config()
        else:
            self.config['SETTINGS'] = {
                'version': self.APP_VERSION,
                'language': 'english',
                'save_preview_files': 'False',
                'keep_transparent_color': 'False',
                'keep_temp_files': 'False',
                'load_last_output': 'False',
                'save_conversion_params': 'False',
                'show_success_dialog': 'True',
                'show_grid': 'True',
                'remember_file_paths': 'False'
            }
            self.config['DISPLAY'] = {
                'grid_color': '255,255,255',
                'grid_alpha': '128',
                'overlay_text_color': '0,0,0',
                'overlay_alpha': '128'
            }
            self.config['PATHS'] = {
                'last_image_directory': '',
                'last_save_directory': ''
            }
            self.config['CONVERSION'] = {
                'bpp': '0',
                'use_palettes': 'True',
                'selected_palettes': '0',
                'transparent_color': '0,0,0',
                'extra_transparent': '0',
                'tileset_width': '0',
                'origin': '0,0',
                'output_size': 'Original',
                'custom_width': '32',
                'custom_height': '20',
                'tilemap_width': '32',
                'tilemap_height': '20',
                'rotation_mode': '0',
                'start_index': '0',
                'palette_size': '1'
            }
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
    
    def get(self, section, key, default=None):
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def getboolean(self, section, key, default=False):
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)
        self.save_config()
