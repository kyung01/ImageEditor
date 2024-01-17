import os
import json
from tkinter import Tk, Canvas, PhotoImage, Entry, Button
import PIL.Image
import PIL.ImageTk
from tkinter import Label
from tkinter import Frame

from datetime import datetime


class DataEntry:
    def __init__(self, image_file, json_file):
        self.image_file = image_file
        self.caption_file = json_file
    def getWeight(self):
        #load caption file
        weight = 0
        with open(self.caption_file, "r") as f:
            captions = json.load(f)
        for caption in captions:
            if caption["text"] != "DELETE_ME":
                weight += 1
            else:
                weight -= 1
        return weight


class ImageEditor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        #walk through the folder and get all image files
        image_file_paths = []
        image_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".gif"]
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in image_extensions:
                    #save full path to image file
                    image_file_paths.append(os.path.join(root, file))
        self.datas = []
        for image_file in image_file_paths:
            json_file = os.path.splitext(image_file)[0] + ".json"
            self.datas.append(DataEntry(image_file, json_file))
        
        #check if json file exists
        for data in self.datas:
            json_file = data.caption_file
            if not os.path.exists(json_file):
                print("JSON file not found for image file: " + image_file)
                #create json file with "[]" as content
                with open(json_file, "w") as f:
                    f.write("[]")
        #sort datas by weight
        self.datas.sort(key=lambda x: x.getWeight(), reverse=False)
        self.data_index = 0
        #move data until it has zero or positive weight
        while self.getCurrentDataWeight() < 0:
            self.getNextIndex()
        print("selected image file: " + str(self.data_index) + "Weight is " + str(self.getCurrentDataWeight()))
        
    def getNextIndex(self):
        #get next index
        self.data_index += 1
        #if index is out of range, reset it to 0
        if self.data_index >= len(self.datas):
            self.data_index -= len(self.datas)
        if self.data_index < 0:
            self.data_index += len(self.datas)
        return self.data_index
    
    def getPrevIndex(self):
        #get previous index
        self.data_index -= 1
        #if index is out of range, reset it to 0
        if self.data_index >= len(self.datas):
            self.data_index -= len(self.datas)
        if self.data_index < 0:
            self.data_index += len(self.datas)
        return self.data_index
    
    def getCurrentDataWeight(self):
        return self.datas[self.data_index].getWeight()
    
    def getCurrentImage(self) -> PIL.Image:
        #use pillow to load image then return it
        current_image_path = self.datas[self.data_index].image_file
        #resize image to fit inside 1000x1000 box
        max_size = 500
        image = PIL.Image.open(current_image_path)
        width, height = image.size
        if width > height:
            new_width = max_size
            new_height = int(height * max_size / width)
        else:
            new_height = max_size
            new_width = int(width * max_size / height)
        image = image.resize((new_width, new_height))

        return image
    
    def getCurrentImagePath(self):
        return self.datas[self.data_index].image_file
    
    def getCurrentCaptionPath(self):
        return self.datas[self.data_index].caption_file
    

    def run(self):
        # Initialize Tkinter window
        root = Tk()
        self.root = root
        root.title("Image Editor")
        root.config(bg="skyblue")

        
        left_frame = Frame(root, width=500, height=400)
        left_frame.grid(row=0, column=0, padx=0, pady=0)
        self.right_frame = Frame(root, width=500, height=400)
        self.right_frame.grid(row=0, column=1, padx=10, pady=5)
        self.right_bottom_frame = Frame(root, width=500, height=400)
        self.right_bottom_frame.grid(row=1, column=1, padx=10, pady=5)
        

        
        


        # Load initial image
        current_image = self.getCurrentImage()
        tk_image = PIL.ImageTk.PhotoImage(current_image)
        self.label_image = Label(left_frame, image=tk_image)
        self.label_image.grid(row=1, column=0, padx=5, pady=5)


        
        #if you press left arrow key, show previous image
        
        root.bind('<Left>', lambda event: self.show_prev_image())
        #if you press right arrow key, show next image
        root.bind('<Right>', lambda event: self.show_next_image())
        #if you press enter key, save caption
        root.bind('<Return>', lambda event: self.hdr_enter_pressed())

        self.display_text(self.right_frame,self.right_bottom_frame)
        
        root.mainloop()



    def display_text(self,right_frame=None,right_bottom_frame=None):
        row_index = 2
        self.label_path = Entry(right_frame ,width=200)
        self.label_path.grid(row=0, column=0, padx=5, pady=5)
        self.label_path.insert(0, self.getCurrentImagePath())

        
        self.label_path_caption = Entry(right_frame,width=200)
        self.label_path_caption.grid(row=1, column=0, padx=5, pady=5)
        self.label_path_caption.insert(0, self.getCurrentCaptionPath())
        #make label_path selectable text




        json_data = json.load(open(self.getCurrentCaptionPath()))
        self.description_labels = []
        for caption in json_data:
            text = caption["text"]
            if text != "DELETE_ME":
                label_text = Label(right_frame, text=text)
                label_text.grid(row=row_index, column=0, padx=5, pady=5)
                self.description_labels.append(label_text)
                row_index += 1

        self.label_text = Label(right_frame, text="Enter caption:")
        self.label_text .grid(row=row_index, column=0, padx=5, pady=5)
        self.entry_text = Entry(right_frame, width=50)
        self.entry_text.grid(row=row_index+1, column=0, padx=5, pady=5)
        self.entry_text.insert(0, "")

        #left and right buttons, use them with left arrow and right arrow keys
        self.button_prev = Button(self.right_bottom_frame, text="Prev", command=self.show_prev_image)
        self.button_prev.grid(row=0, column=0, padx=5, pady=5)
        self.button_next = Button(self.right_bottom_frame, text="Next", command=self.show_next_image)
        self.button_next.grid(row=0, column=1, padx=5, pady=5)

        #focuse on entry_text
        self.entry_text.focus_set()
    
    def remove_text(self):
        self.label_path.destroy()
        for label in self.description_labels:
            label.destroy()
        self.label_text.destroy()
        self.entry_text.destroy()
        self.button_prev.destroy()
        self.button_next.destroy()


    def get_current_formatted_time(self):
        # Get current time
        current_time = datetime.now()

        # Format it as a string
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        return formatted_time

    def hdr_enter_pressed(self):
        #Save in format of

        #{
        #"ID": 205953349093163008,
        #"type": "SENTENCE",
        #"time": year-month-day hour:min:sec,
        #"text": "photo, man with beard and arm tattoos wearing black jockstrap and vest, pink background"
        #}
        #load caption file
        self.save_caption()
        self.show_next_image()
    
    def save_caption(self):
        
        with open(self.getCurrentCaptionPath(), "r") as f:
            captions = json.load(f)
        #get caption text
        caption_text = self.entry_text.get()
        if(caption_text == ""):
            return
        #add caption text to captions lisst 
        my_id = 205953349093163008
        new_entry = {
            "ID": my_id,
            "type": "SENTENCE",
            "time": self.get_current_formatted_time(),
            "text": caption_text
        }
        captions.append(new_entry)
        #save caption file
        with open(self.getCurrentCaptionPath(), "w") as f:
            json.dump(captions, f, indent=4)


    def show_prev_image(self):
        self.getPrevIndex()
        self.update_image()

    def show_next_image(self):
        self.getNextIndex()
        self.update_image()

    def update_image(self):
        current_image = self.getCurrentImage()
        tk_image = PIL.ImageTk.PhotoImage(current_image)
        #self.root.destroy()
        #self.run()
        
        self.label_image.config(image=tk_image)
        self.label_image.image = tk_image  # Keep a reference to avoid garbage collectio
        self.remove_text()
        self.display_text(self.right_frame,self.right_bottom_frame)

if __name__ == "__main__":
    folder_path = r"D:\Python Projects\ImageEditor\data"  # Replace with the path to your image folder
    #get all image files in the folder
    image_editor = ImageEditor(folder_path)
    image_editor.run()
