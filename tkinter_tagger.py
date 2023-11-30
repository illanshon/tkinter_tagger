# путь до проекта без русских букв, радактирование тегов работает с jpg , с png работает, но пока с ошибками
# pip install pillow

import tkinter as tk
from tkinter import filedialog
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from PIL import *
import os
import subprocess

# dynamic_vars = {}
# dynamic_vars["var1"] = 1
# dynamic_vars["var2"] = 2
# print(dynamic_vars["var2"])

class ImageViewer:
    
    checkbox_list = []
    image_path = ''
    checkbox_value = []
    dynamic_var = {}
    dynamic_cb = {}

    def __init__(self, master):
        self.master = master
        self.image_files = []
        self.current_index = 0
        self.create_widgets()

    def create_widgets(self):
        self.open_button = ttk.Button(self.master, text="Открыть каталог", width=23, command=self.open_directory)
        self.open_button.pack(anchor=NE)

        self.close_button = ttk.Button(self.master, text="Выход", width=23, command=lambda: exit())
        self.close_button.pack(anchor=NE) # grid(row=2, column=2,sticky=NW)

        # создаем картинку
        self.label = ttk.Label(self.master)
        self.label.pack(anchor=NE) # anchor=CENTER, fill=BOTH, expand=True 
        self.label.lower()
   
        self.master.bind("e", self.fullscreen_change)
        self.master.bind("<Left>", self.show_previous_image)
        self.master.bind("<Right>", self.show_next_image)
        self.master.bind("w", self.resize_image)
        self.master.bind("q", self.exit)


    def open_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.image_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]
        if self.image_files:
            self.show_image()

    def resize_image(self, event):
        image = Image.open(self.image_files[self.current_index])
        original_width, original_height = image.size
        root.winfo_height() 

        # Получаем новую ширину и высоту окна
        new_width = root.winfo_width() 
        new_height = root.winfo_height() 
        ratio = min(new_width/original_width, new_height/original_height)        
        new_size = (int(original_width*ratio), int(original_height*ratio))      
        image = image.resize(new_size, Image.LANCZOS) # растянули/сжали   NEAREST, BILINEAR, BICUBIC и LANCZOS
        photo = ImageTk.PhotoImage(image)
        self.label.config(image=photo)
        self.label.image = photo
        self.label.place(x = 0,y = 0)            



    def show_image(self):
             
        self.resize_image(event=self.resize_image)

        self.image_path = self.image_files[self.current_index]
              
        # command = f'{exiftool_path} -Subject {self.image_path}'
        # subprocess.run(command, shell=True)

        # берем теги (доделать)
        command = f'{exiftool_path} -Keywords {self.image_path}'
        process = subprocess.run(command, shell=True)

        # берем теги с иерархией
        command = f'{exiftool_path} -Subject {self.image_path}'
        process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, _ = process.communicate()
        output = str(output)

        # создаем список убираем лишнее
        output = output.replace("b'", "").replace("\\r\\n'", "").replace("Keywords", "").replace(" ", "").replace(":", "").replace("Subject", "").replace("`", "").replace("'", "")  
        output = output.split(",")
        print(output)
       
        if process.returncode == 0:
   
                self.delete_checkboxes()
                self.dynamic_var = {}
                self.dynamic_cb = {}  


                if output != '':
                # создаем список тегов которые уже есть в изображении            
                    for tag in output: 
                                                        
                        self.dynamic_var[tag] = tk.IntVar()
                        self.checkbox_value.append(self.dynamic_var[tag])                 
                        self.dynamic_cb[tag] = tk.Checkbutton(root, text=tag, variable=self.dynamic_var[tag], command=lambda f = self.dynamic_var[tag], t = tag: self.select2(f, t))                    
                        self.dynamic_cb[tag].pack(anchor=NE)                    
                        self.checkbox_list.append(self.dynamic_cb[tag])
                        print(self.dynamic_var[tag])  

                    for i in self.checkbox_value:
                        i.set(1)

                # создаем список тегов которые указаны в tag_list.txt      
                for tag in tag_list:   

                    if tag in output:
                        print("уже есть")
                    else:
                        self.dynamic_var[tag] = tk.IntVar()
                        self.checkbox_value.append(self.dynamic_var[tag])
                        self.dynamic_cb[tag] = tk.Checkbutton(root, text=tag, variable=self.dynamic_var[tag], command=lambda f = self.dynamic_var[tag], t = tag: self.select2(f, t))
                        
                        self.dynamic_cb[tag].pack(anchor=NE)                        
                        self.checkbox_list.append(self.dynamic_cb[tag])         

        else:
            print("Произошла ошибка при выполнении команды exiftool")

    # Очищаем чекбоксы после каждой смены изображений
    def delete_checkboxes(self):

        for cb in self.checkbox_list:
            print(f"destroy{cb}")
            cb.destroy()            

        self.checkbox_list.clear()
        
    # обработка событий нажатия на чекбоксы
    def select2(self, var2, category):
        print(var2.get())
        print(var2)

        # Добавляем теги
        if var2.get() == 1:            
            new_category = category
            command = f'{exiftool_path} -XMP:Subject+={new_category} {self.image_path}'
            subprocess.run(command, shell=True)
            # Команда для изменения тега категории с использованием exiftool
            command = f'{exiftool_path} -Keywords+={new_category} {self.image_path}'
           
            subprocess.run(command, shell=True)

            # удаляем дубликат .origin
            try:
                os.remove(self.image_path + "_original")
            except FileNotFoundError:
                pass

        # удаляем теги   
        else:
            new_category = category
            command = f'{exiftool_path} -XMP:Subject-={new_category} {self.image_path}'
            subprocess.run(command, shell=True)
            # Команда для изменения тега категории с использованием exiftool
            command = f'{exiftool_path} -Keywords-={new_category} {self.image_path}'
          
            subprocess.run(command, shell=True)

            try:
                os.remove(self.image_path + "_original")
            except FileNotFoundError:
                pass

    def show_previous_image(self, event):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()

    def show_next_image(self, event):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.show_image()

    def fullscreen_change(self, event):
        global first_init
        global fullscreen_enabled
             
        if first_init == True:
            fullscreen_enabled = False
            first_init = False
        
        if fullscreen_enabled == False:
            root.attributes('-fullscreen', True) 
            fullscreen_enabled = True
            print('+Fullscreen')
        else:  
            root.attributes('-fullscreen', False) 
            fullscreen_enabled = False
            print('-Fullscreen')

        self.resize_image(event=self.resize_image)
            
    def exit(self, event):
        print("exit")
        exit()
   
if __name__ == "__main__": 

    with open("tag_list.txt", 'r', encoding="utf-8") as f:
        tag_list = f.read()
        tag_list = tag_list.split("\n")

    first_init = False
    fullscreen_enabled = False
    exiftool_path = 'exiftool.exe'

    root = tk.Tk()
    # root.overrideredirect(1)
    # root.state('zoomed')
    root.title("Просмотр фотографий")
    root.attributes("-toolwindow", False)  
    root.geometry("700x700") 
    
    # Получаем размеры окна
    scr_res_x = root.winfo_screenwidth()
    scr_res_y = root.winfo_screenheight()  # root.winfo_height() - получить размер экрана

    label = Label(text="q - выход", width=20, background="#B3E5FC") # создаем текстовую метку
    label.pack(anchor=NE)  
    label = Label(text="e - полный экран",width=20, background="#B3E5FC") # создаем текстовую метку
    label.pack(anchor=NE)  
    label = Label(text="w - растянуть картинку",width=20, background="#B3E5FC") # создаем текстовую метку
    label.pack(anchor=NE)  

    image_viewer = ImageViewer(root)

    root.mainloop()