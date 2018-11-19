import tkinter
from Window import Window
from DndHandler import DndHandler

def main():
    root = tkinter.Tk()
    root.winfo_toplevel().title("RTT Behavior Tree Editor")

    t1 = Window(root)
    root.mainloop()

if __name__ == '__main__':
    main()