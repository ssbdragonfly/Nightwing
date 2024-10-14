import functools
import tkinter as tk
import traceback
from collections.abc import Callable
from typing import ParamSpec, TypeVar

import customtkinter as ctk
import requests

P = ParamSpec("P")
T = TypeVar("T")

def pcall(func: Callable[P, object]) -> Callable[P, None]:
    """Call a function, suppressing all errors."""
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            func(*args, **kwargs)
        except Exception:
            traceback.print_exc()

    return wrapper

def show_error():
    tk.messagebox.showerror("Error", "Code Invalid")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NightWing")
        self.width_1 = self.winfo_screenwidth()
        self.height_1 = self.winfo_screenheight()
        self.name = ""
        self.geometry("400x" + str(self.height_1 - 75) + "+" + str(self.width_1 - 410) + "+0")
        self.title_gen()

        self.user_entry = ctk.CTkEntry(
            master=self,
            placeholder_text="Enter Name",
            width=int(0.2 * self.width_1),
            height=int(0.04 * self.height_1),
            border_width=5,
            corner_radius=10,
            font=("Calibri", int(0.03 * self.height_1)),
        )
        self.user_entry.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)
        self.user_entry.bind(
            "<Return>", lambda event: self.send_code(self.code_entry.get(), self.user_entry.get())
        )

        self.code_entry = ctk.CTkEntry(
            master=self,
            placeholder_text="Enter Code",
            width=int(0.2 * self.width_1),
            height=int(0.04 * self.height_1),
            border_width=5,
            corner_radius=10,
            font=("Calibri", int(0.03 * self.height_1)),
        )
        self.code_entry.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)
        self.code_entry.bind(
            "<Return>", lambda event: self.send_code(self.code_entry.get(), self.user_entry.get())
        )
        self.go = ctk.CTkButton(master=self, 
                               text="Join Quiz!", 
                               height=int(0.05 * self.height_1),
                               width=int(0.08 * self.width_1),
                               command=lambda: self.send_code(self.code_entry.get(), self.user_entry.get()), 
                               font = ("Calibri", 15,'bold'))
        self.go.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)

    @pcall
    def send_code(self, code: str, name: str):
        try:
            response = requests.post(
                f"http://127.0.0.1:8000/quiz/quiz/{code}/"
            )  # Initial POST request
            jsonified = response.json()
            self.quiz_id = jsonified["quiz_id"]
            self.name = name
            self.render_waiting_screen()
            self.poll_server(code)
        except Exception: #Broke :(
            show_error()
            self.code_entry.delete(0, tk.END)
            self.code_entry.insert(0, "")
            self.code_entry.focus_set()

    def poll_server(self, code: str):
        """Poll the server every second for a response."""
        try:
            response = requests.post(f"http://127.0.0.1:8000/quiz/quiz/{self.quiz_id}/question")
            jsonified = response.json()
            print(jsonified)
            self.question(jsonified)
            
        except Exception as e:  # noqa: BLE001
            self.after(1000, lambda: self.poll_server(code))  # Poll every 1 second
            print(type(e))
            return  # no question out yet

    def render_waiting_screen(self):
        self.clear_screen()
        self.title_gen()
        self.rendered_name = ctk.CTkLabel(
            self, text=self.name, font=("Calibri", int(0.02 * self.height_1))
        )
        self.rendered_name.place(relx=0.5, rely=0.125, anchor=ctk.CENTER)
        #MORE

    def clear_screen(self):
        """Clear all widgets from the screen."""
        for widget in self.winfo_children():
            widget.destroy()

    def question(self, response):
        """Render the question and options on the screen."""
        print(response)
        self.clear_screen()
        self.title_gen()
        self.rendered_name = ctk.CTkLabel(self, text=self.name, font=("Calibri", int(0.02 * self.height_1)))
        self.rendered_name.place(relx=0.5, rely=0.125, anchor=ctk.CENTER)
        #Render the question
        question_text = response["question"]
        self.render_question = ctk.CTkTextbox(
            master=self,
            wrap=tk.WORD,
            font=("Calibri", int(0.05 * self.height_1)),
            width=400,
            height=100
        )
        self.render_question.place(relx=0.5, rely=0.23, anchor=ctk.CENTER)
        self.render_question.insert(tk.END, question_text)
        self.render_question.configure(state="disabled")

        options = ["option_a", "option_b", "option_c", "option_d", "option_e", "option_f", "option_g"]
        radio_var = tk.IntVar(value=0)
        for idx, option_key in enumerate(options):
            option_text = response.get(option_key, "")
            if option_text:
                radio_button = ctk.CTkRadioButton(
                    master=self,
                    text=option_text,
                    variable=radio_var,
                    value=idx+1,
                    font=("Calibri", int(0.03 * self.height_1))
                )
                radio_button.place(relx=0.5, rely=0.4 + idx * 0.05, anchor=ctk.CENTER)

    def title_gen(self):
        """Generate the title of the app."""
        self.title = ctk.CTkLabel(
            self, text="NightWing Quizzes", font=("Calibri", int(0.05 * self.height_1))
        )
        self.title.place(relx=0.5, rely=0.075, anchor=ctk.CENTER)


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
