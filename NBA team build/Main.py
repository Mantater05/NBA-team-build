import tkinter as tk
from PlayerDisplayApp import PlayerDisplayApp

class Main:
    def __init__(self):
        # Initialize the main window for the app
        self.root = tk.Tk()  
        self.app = PlayerDisplayApp(self.root)  # Create an instance of PlayerDisplayApp

    def run(self):
        # Run the Tkinter event loop to start the app
        self.root.mainloop()

if __name__ == "__main__":
    main_program = Main()  # Create the Main instance
    main_program.run()  # Start the app by running the Tkinter event loop
