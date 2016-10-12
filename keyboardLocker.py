#coding=utf-8
#Python2.7解释器解析
import pythoncom
import pyHook
import win32api
import Tkinter
import tkFont
from time import sleep
import threading

left = None
isClosed = False

class leftLabel(object):
    'create leftrmation label'
    
    def __init__(self,location):
        self.__root = Tkinter.Tk()
        self.__initWidgets()
        
    def __initWidgets(self):
        'initialize widgets'
        self.__root.overrideredirect(True)#是否过滤标题栏和边框
        self.__root.attributes("-alpha", 0.5)#窗口透明度50%
        self.__root.attributes("-topmost",True)#窗口置于最顶层
        
        #获取屏幕宽高度 height = win32api.GetSystemMetrics(win32con.SM_CYFULLSCREEN)  
        screenHeight = self.__root.winfo_screenheight()
        ft = tkFont.Font(family='Arial',size=10,weight=tkFont.BOLD) #设置显示字体格式
        self.__label = Tkinter.Label(self.__root,fg='red',font=ft,
                text="键盘已被锁定,可按Ctrl+Alt+L关闭锁定\n双击本信息可关闭提示")
        self.__label.pack(fill='both',expand='yes') #label填充方式
        self.__root.geometry("260x40+0+"+str(screenHeight-90)) #设置窗体大小及坐标
        self.__root.bind("<Double-Button-1>",self.__mouseEvent) #绑定响应方法
        
    def __mouseEvent(self,event):
        '双击窗口让窗口关闭'
        global isClosed
        isClosed = True
        self.close()
        
    def show(self):
        ''
        self.__root.mainloop()
        
    def close(self):
        ''
        self.__root.destroy()


class KeyboardHook(object):
    '键盘监听类'
    def __init__(self):
        self.__keyList = []  #按键序列
        self.__index = 0  #最新序列下标
        self.__hook = pyHook.HookManager() 
        self.__hook.KeyDown = self.__onKeyboardEvent
        self.__hook.HookKeyboard()
        
    def __updateList(self,keyID):
        '更新按键列表'
        self.__index = (self.__index+3)%3
        if len(self.__keyList) < 3:
            self.__keyList.insert(self.__index,keyID)
        else:
            self.__keyList[self.__index] = keyID
        self.__index += 1
        
    def __onKeyboardEvent(self,event):
        '处理监听事件'
        self.__updateList(event.KeyID)

        #Lctrl=162;  Lmenu=164;  l=76;  L=76;  Rctrl=163;  Rmenu=165
        #如果连续按下Ctrl+Shift+L按键则关闭监听
        if (162 in self.__keyList or 163 in self.__keyList) and \
            (164 in self.__keyList or 165 in self.__keyList) and \
            (76 in self.__keyList):
            self.closeListening()
        
        #返回 True 以便将事件传给其它处理程序
        #注意，这儿如果返回 False ，则键盘事件将被全部拦截
        return False
    
    def startListening(self):
        print('start listening')
        pythoncom.PumpMessages(10000)
        
    def closeListening(self):
        print('stop listening')
        
        global left
        if not isClosed:
            left.close()
        win32api.PostQuitMessage() #关闭监听
    
class MyThread(threading.Thread):
    ''
    def __init__(self,func,args,name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        
    def getResult(self):
        return self.res
        
    def run(self):
        self.res = self.func(*self.args)
        
        
def main():
    global left
    left = leftLabel("left")
    leftThread = MyThread(left.show,(),name="leftThread")
    leftThread.start()

    hook = KeyboardHook()
    hook.startListening()

if __name__ == '__main__':
    main()