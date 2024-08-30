import customtkinter as ctk

class App(ctk.CTk):
    
    def __init__(self):
        super().__init__()
        self.title("NightWing")
        self.width_1 = self.winfo_screenwidth()
        self.height_1 = self.winfo_screenheight()
        self.geometry(
            "300x" + str(self.height_1-75)+ "+" + str(self.width_1-310) + "+0"
        )
        self.title_gen()

        self.entry = ctk.CTkEntry(master=self,
                               placeholder_text="Enter Code",
                               width=int(0.2 * self.width_1),
                               height=int(0.04 * self.height_1),
                               border_width=5,
                               corner_radius=10,
                               font=("Calibri",int(0.03 * self.height_1)))
        self.entry.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)
        self.entry.bind("<Return>", lambda event: self.send_code(self.entry))

    def send_code(self, code):
        #Placeholder for actual talking to website
        print(code.get())
        self.clear_screen()


    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def title_gen(self):
        self.title = ctk.CTkLabel(self,text="NightWing Quizes",font = ("Calibri", int(0.05 * self.height_1)))
        self.title.pack()

    def launch_function(self):
        print("test")

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()