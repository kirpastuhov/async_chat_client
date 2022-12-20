from tkinter import messagebox


class InvalidTokenException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        messagebox.showinfo("Invalid Token", "Please check if your token is valid")
