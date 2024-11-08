"""TO DO
- Question counter
- Loading screen
- Quiz finished detection and score display
- Less ugly and logo
- Get rid of debugging nonsensical print statements
- Fragment all tk elements into functions and call functions
- Clean up structure and flow (see above)
- Add "-> None" to void methods
- Add types to parameters
- Question sizing (next up)
.
"""  # noqa: D205

import functools
import tkinter as tk
import traceback
import webbrowser
from collections.abc import Callable, Sequence
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
        self.quizzing = False
        self.name = ""
        self.geometry("400x" + str(self.height_1 - 75) + "+" + str(self.width_1 - 410) + "+0")
        self.start()

    def start(self):
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
        self.go = ctk.CTkButton(
            master=self,
            text="Join Quiz!",
            height=int(0.05 * self.height_1),
            width=int(0.08 * self.width_1),
            command=lambda: self.send_code(self.code_entry.get(), self.user_entry.get()),
            font=("Calibri", 15, "bold"),
        )
        self.go.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)

    def home(self):
        self.quizzing = False
        self.clear_screen()
        self.start()

    def home_button(self):
        self.close = ctk.CTkButton(
            master=self,
            text="Back",
            height=15,
            width=20,
            command=lambda: self.home(),
            font=("Calibri", 15, "bold"),
        )
        self.close.place(relx=0.07, rely=0.03, anchor=ctk.CENTER)

    @pcall
    def send_code(self, code: str, name: str):
        try:
            response = requests.post(
                f"http://127.0.0.1:8000/quiz/quiz/{code}/"
            )  # Initial POST request
            jsonified = response.json()
            self.quiz_id = jsonified["quiz_id"]
            self.name = name
            print("\tGot quiz id: {self.quiz_id}")
            self.quizzing = True
            self.render_waiting_screen()
            self.poll_server()
        except Exception:  # Broke :(
            show_error()
            self.code_entry.delete(0, tk.END)
            self.code_entry.focus_set()

    def poll_server(self):
        if not self.quizzing:
            return
        """Poll the server for a response."""
        print("Polled Server")
        try:
            response = requests.post(
                f"http://127.0.0.1:8000/quiz/quiz/{self.quiz_id}/question",
                data={"user": self.name},
            )
            jsonified = response.json()
            self.question(jsonified)
            print(f"\tPoll successful, {jsonified}")
        except Exception:
            self.after(1000, self.poll_server)  # Poll every 1 second

    @pcall
    def question(self, response):
        """Render the question and options on the screen."""
        print("Tried to render question")
        self.clear_screen()
        self.title_gen()
        self.home_button()
        self.rendered_name = ctk.CTkLabel(
            self, text=self.name, font=("Calibri", int(0.02 * self.height_1))
        )
        self.rendered_name.place(relx=0.5, rely=0.125, anchor=ctk.CENTER)
        # Render the question
        question_text = response["question"]
        self.render_question = ctk.CTkTextbox(
            master=self,
            wrap=tk.WORD,
            font=("Calibri", int(0.04 * self.height_1)),
            fg_color="transparent",
            width=self.winfo_width() - 100,
            height=150,
        )
        self.render_question.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)
        self.render_question.insert(tk.END, question_text)
        self.render_question.configure(state="disabled")
        # SIZE FOR QUESTION CODE SHOULD BE HERE
        options = [
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "option_e",
            "option_f",
            "option_g",
        ]
        frame = ctk.CTkFrame(self, fg_color="transparent")
        self.radio_var = tk.IntVar(value=26)
        for idx, option_key in enumerate(options):
            option_text = response.get(option_key, "")
            if option_text:
                radio_button = ctk.CTkRadioButton(
                    master=frame,
                    text=option_text,
                    variable=self.radio_var,
                    value=idx + 1,
                    font=("Calibri", int(0.03 * self.height_1)),
                )
                radio_button.grid(row=idx, column=0, sticky=tk.W)
        frame.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)

        self.after(2000, lambda: self.submit_answer(response["id"]))

    @pcall
    def submit_answer(self, current_question_id: int):
        if not self.quizzing:
            return
        print("Submitted answer")
        default = 26  # Default value for no selection
        if self.radio_var.get() == default:
            warning = ctk.CTkLabel(
                master=self,
                text="Hurry! No answer selected.",
                width=int(0.2 * self.width_1),
                height=int(0.04 * self.height_1),
                corner_radius=10,
                font=("Calibri", int(0.03 * self.height_1)),
            )
            warning.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)
            self.after(1000, warning.destroy)
            self.after(1000, lambda: self.submit_answer(current_question_id))
            return
        try:
            answer_str = f"option_{chr(self.radio_var.get() + 64)}"
            requests.post(
                f"http://localhost:8000/quiz/quiz/{self.quiz_id}/answer/{current_question_id}/{self.name}",
                data={"answer": answer_str.removeprefix("option_")},
            )

            response = requests.post(
                f"http://127.0.0.1:8000/quiz/quiz/{self.quiz_id}/question",
                data={"user": self.name},
            )
            jsonified = response.json()
            if "message" in jsonified:
                self.quizzing = False
                correct = jsonified['correct']
                total = jsonified['total']
                print((correct,total))
                self.render_quiz_finished(correct,total)
                return

            elif jsonified["id"] != current_question_id:
                self.question(jsonified)
            else:
                self.after(1000, lambda: self.submit_answer(current_question_id))
            print(f"\t Poll received {jsonified}")
        except Exception:  # noqa: BLE001
            self.after(1000, lambda: self.submit_answer(current_question_id))

    def render_waiting_screen(self):
        self.clear_screen()
        self.title_gen()
        self.rendered_name = ctk.CTkLabel(
            self, text=self.name, font=("Calibri", int(0.02 * self.height_1))
        )
        self.rendered_name.place(relx=0.5, rely=0.125, anchor=ctk.CENTER)

    def back_to_home_button(self):
        self.to_home = ctk.CTkButton(
            master=self,
            text="Home",
            height=15,
            width=20,
            command=lambda: self.home(),
            font=("Calibri", 30, "bold"),
        )
        self.to_home.place(relx=0.35, rely=0.5, anchor=ctk.CENTER)

    def to_web_button(self):
        self.web = ctk.CTkButton(
            master=self,
            text="Website",
            height=15,
            width=20,
            command=lambda: webbrowser.open_new_tab("http://127.0.0.1:8000/"),
            font=("Calibri", 30, "bold"),
        )
        self.web.place(relx=0.65, rely=0.5, anchor=ctk.CENTER)

    def render_quiz_finished(self, score, total):
        #print("Finished quiz func reached")
        self.clear_screen()
        self.title_gen()
        self.rendered_name = ctk.CTkLabel(
            self, text=self.name, font=("Calibri", int(0.02 * self.height_1))
        )
        self.rendered_name.place(relx=0.5, rely=0.125, anchor=ctk.CENTER)
        self.score = ctk.CTkLabel(
            self, text=f"You scored {score}/{total}", font=("Calibri", int(0.08 * self.height_1))
        )
        self.score.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)
        self.home_button()
        self.to_web_button()
        self.back_to_home_button()

    def clear_screen(self, whitelist: Sequence = ()) -> None:
        """Clear all widgets from the screen."""
        for widget in self.winfo_children():
            if widget not in whitelist:
                widget.destroy()

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
