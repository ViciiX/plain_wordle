from tkinter import *
root=Tk() # 源码来自wb98.com
root.geometry("512x512")
 
#root.grid_rowconfigure(1,weight=1) # row为1，缩放比为1
# root.grid_columnconfigure(0,weight=1) # column为0，缩放比为1
 
but1=Button(root,text="测试按钮1")
but1.grid(row=0,column=0,sticky=N+S+W+E, columnspan=2, rowspan=2)
but2=Button(root,text="测试按钮2")
but2.grid(row=0,column=2)
but3=Button(root,text="测试按钮3")
but3.grid(row=1,column=2)
# but4=Button(root,text="测试按钮4")
# but4.grid(row=1,column=1,sticky=N+S+W+E)
# but5=Button(root,text="测试按钮5")
# but5.grid(row=2,column=0,columnspan=2,sticky=N+S+W+E) # 跨2列
 
root.mainloop()