from tkinter import *

m1 = PanedWindow()
m1.pack(fill=BOTH, expand=1)

left = Label(m1, text="left pane")
m1.add(left)

middle = Label(m1, text="middle pane")
m1.add(middle)

right = Label(m1, text="right pane")
m1.add(right)

mainloop()