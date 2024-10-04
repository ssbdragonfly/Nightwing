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
        except Exception:  # noqa: BLE001
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
        self.geometry("300x" + str(self.height_1 - 75) + "+" + str(self.width_1 - 310) + "+0")
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

    @pcall
    def send_code(self, code: str, name: str):
        try:
            response = requests.post(
                f"http://127.0.0.1:8000/quiz/quiz/{code}"
            )  # Initial POST request
            jsonified = response.json()
            self.quiz_id = jsonified["quiz_id"]
            self.name = name
            self.poll_server(code)
            self.render_waiting_screen()
        except Exception:  # noqa: BLE001
            show_error()
            self.code_entry.delete(0, tk.END)
            self.code_entry.insert(0, "")
            self.code_entry.focus_set()

    def poll_server(self, code: str):
        """Poll the server every second for a response."""
        try:
            response = requests.post(f"http://127.0.0.1:8000/quiz/quiz/{code}")
            jsonified = response.json()

            if jsonified.get("status") == "ready":
                print("Quiz is ready!")  # Placeholder because idk
                return

        except Exception:  # noqa: BLE001
            print("No questions")
            return  # no question out yet

        self.after(1000, lambda: self.poll_server(code))  # silly little loop

    def render_waiting_screen(self):
        self.clear_screen()
        self.title_gen()
        self.rendered_name = ctk.CTkLabel(
            self, text=self.name, font=("Calibri", int(0.02 * self.height_1))
        )
        self.rendered_name.place(relx=0.5, rely=0.125, anchor=ctk.CENTER)

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def title_gen(self):
        self.title = ctk.CTkLabel(
            self, text="NightWing Quizzes", font=("Calibri", int(0.05 * self.height_1))
        )
        self.title.place(relx=0.5, rely=0.075, anchor=ctk.CENTER)


"""
    def launch_function(self):
        print("test")
"""


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
