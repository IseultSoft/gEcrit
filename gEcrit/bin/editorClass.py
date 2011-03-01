
#   Distributed under the terms of the GPL (GNU Public License)
#
#   gEcrit is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#editorClass.py


import wx.lib.inspection
import sys,collections
import wx.richtext
from TinyFeatures import *
from configClass import *
from logClass import *
from aboutClass import  *
from SyntaxHighlight import *
from Fonts import *
from ConfigWindow import *
from PrintDialog import *
from FindReplaceText import *
from SourceBrowser import *
from AutoCompletition import *
from ShellEmulator import *
from PastebinDialog import *
from SyntaxChecker import *
from StcControl import *
from DirTreeCtrl import *

class Editor(wx.Frame):
    def __init__(self,id,parent):
        SHELLTAB_ID = 4002
        BASH_ID = 4000
        PY_ID = 4001

        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))    #  Finding where
        os.chdir(pathname)        #  gEcrit is running

        self.SaveRecord = {}
        self.IdRange = []


        if  "editorClass.py" not in sys.argv[-1]:
            self.TargetFile = os.path.normpath(os.path.realpath(sys.argv[-1]))
            self.job_file = True
            Name = self.TargetFile.split("/")[-1]


        else:
            self.job_file = False
            self.TargetFile = "New Document"   #Default Name
            Name = "New Document"

        self.MainFrame = wx.Frame.__init__(self,parent,1000,'gEcrit', size=(700,600))

        self.Bind(wx.EVT_CLOSE, self.OnQuit)


        self.NewTabImage = wx.Image('icons/newtab.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.OpenImage = wx.Image('icons/open.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.SaveImage = wx.Image('icons/save.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.SaveAsImage = wx.Image('icons/saveas.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        ConfigImage = wx.Image('icons/config.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.QuitImage = wx.Image('icons/quit.bmp', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.CloseImage = wx.Image("icons/close.png",wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.PrintImage = wx.Image("icons/printer.bmp",wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.RunImage = wx.Image("icons/run.png",wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        if Config.GetOption("StatusBar"):
            self.StatusBar = self.CreateStatusBar()
            self.StatusBar.SetStatusText("Done")
            self.StatusBar.SetFieldsCount(2)
            self.StatusBar.SetId(999)

        menubar = wx.MenuBar()
        file = wx.Menu()
        edit = wx.Menu()
        help = wx.Menu()
        search = wx.Menu()
        view = wx.Menu()
        document = wx.Menu()

        file.Append(500, '&New Tab\tCtrl+N', 'Open a new tab.')
        file.Append(501, '&Open\tCtrl+O', 'Open a new document.')
        file.Append(502, '&Save\tCtrl+S', 'Save the document.')
        file.Append(503, 'Save As', 'Save the document under a different name.')
        file.Append(506,"Save All","Saves all the open documents that have a path.")
        file.Append(504, '&Print\tCtrl+P', 'Print the current document.')
        file.Append(505, 'Close &Tab\tCtrl+W', 'Close the current tab.')

        file.AppendSeparator()
        quit = wx.MenuItem(file, 506, '&Quit\tCtrl+Q', 'Quit gEcrit.')
        file.AppendItem(quit)

        edit.Append(520,"&Undo\tCtrl+Z","Cancel the last action.")
        edit.Append(521,"&Redo\tCtrl+Y","Bring back the last action.")
        edit.AppendSeparator()
        edit.Append(522,"&Cut\tCtrl+X","Cut the selection.")
        edit.Append(523,"C&opy\tCtrl+C","Copy the selection.")
        edit.Append(524,"P&aste\tCtrl+V","Paste the selection.")
        edit.AppendSeparator()
        edit.Append(525,"Select All\tCtrl+A","Select all the document.")
        edit.AppendSeparator()
        edit.Append(529, "Indent\tCtrl+K","Indent the selected lines.")
        edit.Append(528,"Dedent\tCtrl+J","Dedent the selected lines.")

        edit.AppendSeparator()
        edit.Append(526,"Insert date","Insert the date at cursor position.")
        edit.AppendSeparator()
        edit.Append(527,"Preferences\tCtrl+E","Open the configuration window.")

        search.Append(530,"Find\tCtrl+F","Search text in the current document.")
        search.Append(531,"Find and Replace\tCtrl+H","Search and replace text in the current document.")

        view.Append(535, "Zoom In\tCtrl++","Increase the size of the text.")
        view.Append(536, "Zoom Out\tCtrl+-","Decrease the size of the text.")
        view.Append(537,"Normal Size\tCtrl+0","Set the size of the text to normal.")
        view.AppendSeparator()
        view.AppendCheckItem(538, "Line Numbers", "Show/Hide line numbers.").Check(Config.GetOption("LineNumbers"))
        view.AppendCheckItem(539, "Fold Marks", "Show/Hide fold marks.").Check(Config.GetOption("FoldMarks"))
        view.AppendCheckItem(540, "White Space", "Show/Hide white spaces.").Check(Config.GetOption("Whitespace"))
        view.AppendCheckItem(541, "Indentation Guides", "Show/Hide indentation guides.").Check(Config.GetOption("IndetationGuides"))
        view.AppendCheckItem(546,"Edge Line","Show/Hide the edge line.").Check(Config.GetOption("EdgeLine"))
        view.AppendCheckItem(547,"Syntax Highlight","Enable/Disable Syntax Highlight.").Check(Config.GetOption("SyntaxHighlight"))
        view.AppendSeparator()
        view.AppendCheckItem(542,"Python Shell","Stop/Start a python shell.").Check(Config.GetOption("PythonShell"))
        view.AppendCheckItem(543, "OS Shell", "Stop/Start an OS shell.").Check(Config.GetOption("BashShell"))
        view.AppendCheckItem(544, "Source Browser", "Show/Hide the source browser.").Check(Config.GetOption("SourceBrowser"))
        view.AppendCheckItem(555, "FileTree","Show/Hide the file browser.").Check(Config.GetOption("FileTree"))
        view.AppendCheckItem(545, "Statusbar", "Show/Hide statusbar.").Check(Config.GetOption("StatusBar"))

        document.Append(549,"Send to Pastebin\tCtrl+I","Submit the current document to pastebin.com")
        document.Append(548,"Check for errors\tCtrl+B","Check the current document for errors.(python only)")

        help.Append(550,"About","Open the about window.")

        menubar.Append(file, '&File')
        menubar.Append(edit, '&Edit')
        menubar.Append(search,"&Search")
        menubar.Append(view, "&View")
        menubar.Append(document,"&Document")
        menubar.Append(help, '&Help')

        self.SetMenuBar(menubar)

        mega_sizer = wx.BoxSizer(wx.VERTICAL)

        #tsk_icon = wx.TaskBarIcon()
        #tsk_icon.SetIcon(wx.Icon('icons/gEcrit.png', wx.BITMAP_TYPE_PNG))
        self.SetIcon(wx.Icon('icons/gEcrit.png', wx.BITMAP_TYPE_PNG))

        self.text_id = 0


        main_splitter = wx.SplitterWindow(self,-1, style=wx.SP_3D|wx.SP_BORDER)
        main_splitter.SetMinimumPaneSize(150)
        tab_panel = wx.Panel(main_splitter)
        nb_panel = wx.Panel(main_splitter)
        nb_panel.SetId(998)  #needed in configClass.py

        self.HOMEDIR =  os.path.expanduser('~')
        os.chdir(os.path.abspath(self.HOMEDIR))

        ShellTabs = wx.Notebook(tab_panel, id = SHELLTAB_ID,size = (700,100), style =wx.BORDER_SUNKEN)

        BashPanel = wx.Panel(ShellTabs)
        PythonPanel = wx.Panel(ShellTabs)
        self.BashShell = ShellEmulator(BashPanel, Config.GetOption("OSPath"), BASH_ID)
        self.PythonShell = ShellEmulator(PythonPanel, Config.GetOption("PyPath"), PY_ID)

        python_sizer = wx.BoxSizer(wx.VERTICAL)
        python_sizer.Add(self.PythonShell,1,wx.ALL|wx.EXPAND)
        PythonPanel.SetSizer(python_sizer)
        PythonPanel.Fit()


        bash_sizer = wx.BoxSizer(wx.VERTICAL)
        bash_sizer.Add(self.BashShell,1,wx.ALL|wx.EXPAND)
        BashPanel.SetSizer(bash_sizer)
        PythonPanel.Fit()

        if Config.GetOption("PythonShell") or Config.GetOption("BashShell"):
            if Config.GetOption("BashShell"):
                self.BashShell.OnRun(0, Config.GetOption("OSPath"))

                ShellTabs.AddPage(BashPanel,"OS Shell")

            if Config.GetOption("PythonShell"):
                self.PythonShell.OnRun(0, Config.GetOption("PyPath"))

                ShellTabs.AddPage(PythonPanel, "Python")
            will_split = True
        else:
            will_split = False


        self.nb = wx.aui.AuiNotebook(nb_panel,style= wx.aui.AUI_NB_TOP )
        self.nb.SetId(900) #Needed in StcControl.py
        nb_sizer = wx.BoxSizer(wx.VERTICAL)
        nb_sizer.Add(self.nb,1,wx.EXPAND)
        nb_panel.SetSizer(nb_sizer)
        nb_panel.Fit()



        tab_sizer = wx.BoxSizer(wx.VERTICAL)
        tab_sizer.Add(ShellTabs,1,wx.EXPAND)
        tab_panel.SetSizer(tab_sizer)
        tab_panel.Fit()



        main_splitter_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_splitter_sizer.Add(nb_sizer,0,wx.EXPAND)
        main_splitter_sizer.Add(tab_sizer)
        main_splitter.SetSizer(main_splitter_sizer)
        main_splitter.Fit()

        os.chdir(pathname)


        main_splitter.SplitHorizontally(nb_panel,tab_panel,-1)

        if not will_split:
            main_splitter.Unsplit(tab_panel)
##FILE
        f = wx.FindWindowById
        self.Bind(wx.EVT_MENU, lambda event: self.NewTab(event,"New Document","New Document"),id=500)
        self.Bind(wx.EVT_MENU, lambda event: self.OpenFile(event),id=501)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).Save(event),id=502)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).SaveAs(event),id=503)
        self.Bind(wx.EVT_MENU, lambda event: self.OnPrint(event,self.IdRange[self.nb.GetSelection()]),id=504)
        self.Bind(wx.EVT_MENU, lambda event: self.ManageCloseTab(event,self.IdRange[self.nb.GetSelection()]),id=505)
        self.Bind(wx.EVT_MENU, lambda event: self.OnQuit(event),id=506)
        self.Bind(wx.EVT_MENU, self.SaveAll, id = 506)

##EDIT

        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnUndo(event),id=520)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnRedo(event),id=521)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnCut(event),id=522)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnCopy(event),id=523)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnPaste(event),id=524)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnSelectAll(event),id=525)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnInsertDate(event),id=526)
        self.Bind(wx.EVT_MENU, lambda event: self.OnPrefs(event),id=527)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnDedent(event),id = 528)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnIndent(event),id = 529)


##SEARCH
        self.Bind(wx.EVT_MENU, lambda event: FindRepl.FindDocText(self.IdRange[self.nb.GetSelection()]),id = 530)
        self.Bind(wx.EVT_MENU, lambda event: FindRepl.ReplaceDocText(self.IdRange[self.nb.GetSelection()]),id = 531)

##VIEW

        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnZoomIn(event),id = 535)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnZoomOut(event),id = 536)
        self.Bind(wx.EVT_MENU, lambda event: f(self.IdRange[self.nb.GetSelection()]).OnResetZoom(event),id = 537)

        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("LineNumbers", view.IsChecked(538),self.IdRange),id = 538)
        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("FoldMarks", view.IsChecked(539),self.IdRange),id = 539)
        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("Whitespace", view.IsChecked(540),self.IdRange),id = 540)
        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("IndetationGuides", view.IsChecked(541),self.IdRange),id = 541)
        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("EdgeLine", view.IsChecked(546),self.IdRange),id = 546)
        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("SyntaxHighlight",view.IsChecked(547),self.IdRange),id=547)
        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("PythonShell", view.IsChecked(542),self.IdRange),id = 542)
        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("BashShell", view.IsChecked(543),self.IdRange),id = 543)
        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("SourceBrowser", view.IsChecked(544),self.IdRange),id = 544)
        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("FileTree",view.IsChecked(555),self.IdRange),id = 555)
        self.Bind(wx.EVT_MENU,lambda event: Config.ChangeOption("StatusBar", view.IsChecked(545),self.IdRange),id = 545)


##DOCUMENT
        self.Bind(wx.EVT_MENU,lambda event: self.PastebinDlg.ShowMe(event,self.IdRange[self.nb.GetSelection()]),id =549)
        self.Bind(wx.EVT_MENU,lambda event:  SyntaxDoc.CheckSyntax(event,self.IdRange[self.nb.GetSelection()]),id = 548)
##HELP
        self.Bind(wx.EVT_MENU, lambda event: self.OnAbout(event), id = 550)


        toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL | wx.NO_BORDER)
        toolbar.AddSimpleTool(600, self.NewTabImage, 'New', 'Open a new tab.')
        toolbar.AddSimpleTool(601, self.OpenImage, 'Open', 'Open a new document.')
        toolbar.AddSimpleTool(602, self.SaveImage, 'Save', 'Save the current document.')
        toolbar.AddSimpleTool(603, self.SaveAsImage, 'Save As', 'Save the current document under a differend name.')
        toolbar.AddSimpleTool(604, ConfigImage, 'Settings', 'Open the configuration window.')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(605, self.QuitImage, 'Quit', 'Quit gEcrit')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(606, self.CloseImage, 'Close tab', 'Close the current tab.')

        self.FontCtrl = wx.FontPickerCtrl(toolbar, 607,size=(100,30))
        #self.FontCtrl.SetSelectedFont()
        self.Bind(wx.EVT_FONTPICKER_CHANGED,lambda event: ChangeFont(event, self.FontCtrl.GetSelectedFont(), self.IdRange))

        toolbar.AddControl(self.FontCtrl)
        toolbar.AddControl(wx.TextCtrl(toolbar, 608, size =(-1,-1), style = wx.TE_PROCESS_ENTER))
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(609,self.PrintImage,"Print","Print the current document.")
        toolbar.AddSimpleTool(610,self.RunImage,"Run","Run the current file.(Python only)")
        toolbar.Realize()

        self.Bind(wx.EVT_TOOL,lambda event: self.NewTab(event,"New Document","New Document"), id=600)
        self.Bind(wx.EVT_TOOL, self.OpenFile, id=601)
        self.Bind(wx.EVT_TOOL,lambda event: f(self.IdRange[self.nb.GetSelection()]).Save(event), id=602)
        self.Bind(wx.EVT_TOOL,lambda event: f(self.IdRange[self.nb.GetSelection()]).SaveAs(event), id=603)
        self.Bind(wx.EVT_TOOL, self.OnPrefs, id=604)
        self.Bind(wx.EVT_TOOL, self.OnQuit, id=605)
        self.Bind(wx.EVT_TOOL, lambda event: self.ManageCloseTab(event,self.IdRange[self.nb.GetSelection()]),id=606)

        self.Bind(wx.EVT_TEXT_ENTER , lambda event: self.OnGotoBox(event,self.IdRange[self.nb.GetSelection()]),id=608)

        self.Bind(wx.EVT_TOOL, lambda event: self.OnPrint(event,self.IdRange[self.nb.GetSelection()]),id=609)
        self.Bind(wx.EVT_TOOL, lambda event: self.OnRun(event,self.IdRange[self.nb.GetSelection()]),id=610)

        self.NewTab(0,Name,self.TargetFile)

        mega_sizer.Add(toolbar,0)

        mega_sizer.Add(main_splitter, 1, wx.EXPAND)
#~
        #~ mega_sizer.Add(ShellTabs,0,wx.EXPAND)


        self.SetSizer(mega_sizer)

        self.Centre()
        self.PastebinDlg = PastebinWin(self)
        self.GoConfWin = ConfFrame = CfgFrame(self.IdRange, None)



    def OnPrefs(self,event):
        self.GoConfWin.ShowMe(0)


    def UpdateCords(self,event,text_id):
        cur_doc = wx.FindWindowById(text_id)
        if Config.GetOption("StatusBar"):
            self.StatusBar.SetStatusText("line: "+str(cur_doc.GetCurrentLine())\
            +"    col: "+str(cur_doc.GetColumn(cur_doc.GetCurrentPos())),1)
        event.Skip()


    def NewTab(self,event,nb,TargetFile):
        if TargetFile == False:
            return
        panel = wx.Panel(self)
        panel.identifierTag = nb
        TABBER = self.nb
        # Put text_id into a local variable.
        # We do this so that the lambda takes the current value,
        # and not the constantly-incrementing one.
        text_id = self.text_id

        splitter = wx.SplitterWindow(panel, -1, style=wx.SP_3D|wx.SP_BORDER)
        splitter.SetMinimumPaneSize(150)
        notebk_panel = wx.Panel(splitter)
        side_nb = wx.Notebook(notebk_panel,-1,pos=(0,0),size=(-1,-1))
        side_nb.SetId(4003+text_id)

        notebk_sizer = wx.BoxSizer(wx.HORIZONTAL)
        notebk_sizer.Add(side_nb,1,wx.EXPAND)
        notebk_panel.SetSizer(notebk_sizer)
        notebk_panel.Fit()

        if TargetFile != "New Document" and TargetFile != "":
            file_dir = os.path.split(TargetFile)[0]
        else:
            file_dir = self.HOMEDIR+"/"

        dir_ctrl_panel = wx.Panel(side_nb)
        dir_ctrl = DirTreeCtrl(dir_ctrl_panel,-1,file_dir,pos = (0,0), size =(-1,-1))
        dir_ctrl.SetId(5000+text_id)
        dir_ctrl_pnl_sz = wx.BoxSizer(wx.VERTICAL)
        dir_ctrl_pnl_sz.Add(dir_ctrl, 1, wx.EXPAND)
        dir_ctrl_panel.SetSizer(dir_ctrl_pnl_sz)
        dir_ctrl_panel.Fit()

        #print dir_ctrl.GetPyData(file_dir)
        dir_ctrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED,lambda event: self.NewTab
        (event,os.path.split(dir_ctrl.GetSelectedPath(event))[-1],dir_ctrl.GetSelectedPath(event))
        )


        src_br_panel = wx.Panel(side_nb)
        text_panel = wx.Panel(splitter)
        text_panel.SetId(1001+text_id)

        splitter.SplitVertically(notebk_panel, text_panel,20)

        self.InitSrcBr = SrcBrowser(TargetFile, nb, text_id,src_br_panel)

        self.TextWidget =  StcTextCtrl(text_panel,self.text_id,self.InitSrcBr,TargetFile)

        text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_sizer.Add(self.TextWidget,1,wx.EXPAND)
        text_panel.SetSizer(text_sizer)
        text_panel.Fit()

        self.IdRange.append(self.text_id)
        self.TextWidget.SetBufferedDraw(True)
        self.TextWidget.StyleSetFont(0, self.FontCtrl.GetSelectedFont())

        cur_doc = wx.FindWindowById(text_id)

        # Like a flattened tree control using square headers
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN,    wx.stc.STC_MARK_BOXMINUS,          "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER,        wx.stc.STC_MARK_BOXPLUS,           "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB,     wx.stc.STC_MARK_VLINE,             "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL,    wx.stc.STC_MARK_LCORNER,           "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND,     wx.stc.STC_MARK_BOXPLUSCONNECTED,  "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080")
        cur_doc.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL, wx.stc.STC_MARK_TCORNER,           "white", "#808080")

        Config.ApplyIDEConfig(text_id, TargetFile.split(".")[-1])

        cur_doc.SetXOffset(1)

        cur_doc.Bind(wx.EVT_KEY_DOWN, lambda event: AutoComp.OnKeyPressed(event, text_id))

        cur_doc.Bind(wx.stc.EVT_STC_UPDATEUI, lambda event: self.UpdateCords(event, text_id))

        cur_doc.Bind(wx.stc.EVT_STC_UPDATEUI,lambda event: OnUpdateUI(event,text_id))
        cur_doc.Bind(wx.stc.EVT_STC_MARGINCLICK,lambda event: OnMarginClick(event,text_id))

        self.TabCount = self.text_id
        self.SaveRecord[text_id] = wx.FindWindowById(text_id).GetText()

        cur_doc.Bind(wx.EVT_KEY_UP, lambda event: AutoIndent(event,text_id))

        src_sizer = wx.BoxSizer(wx.HORIZONTAL)
        src_sizer.Add(self.InitSrcBr,1,wx.EXPAND)
        src_br_panel.SetSizer(src_sizer)
        src_br_panel.Fit()


        if Config.GetOption("SourceBrowser"): side_nb.AddPage(src_br_panel,"Source Browser")
        if Config.GetOption("FileTree"): side_nb.AddPage(dir_ctrl_panel,"File Browser")
        # Vertical sizer for  text

        widget_sizer = wx.BoxSizer(wx.HORIZONTAL)
        widget_sizer.Add(src_sizer,0, wx.EXPAND)
        widget_sizer.Add(text_sizer,0, wx.EXPAND)
        splitter.SetSizer(widget_sizer)
        splitter.Fit()

        if Config.GetOption("SourceBrowser") or Config.GetOption("FileTree"):
            will_split = True
        else:
            will_split = False
        if not will_split:
            splitter.Unsplit(notebk_panel)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(splitter, 1,wx.EXPAND)

        # Assign the sizer to the panel, and resize it
        panel.SetSizer(main_sizer)
        main_sizer.Fit(panel)

        self.nb.AddPage(panel, str(nb), select = True)

       #Increment the ID.
        self.text_id += 1



    def OnRun(self,event, text_id):
        cur_doc = wx.FindWindowById(text_id)
        cur_doc.Save(0)
        os.system("xterm -e python "+cur_doc.SaveTarget)


    def OnGotoBox(self, event, text_id):
        cur_doc = wx.FindWindowById(text_id)
        Goto = wx.FindWindowById(608)
        #try:
        scroll_pos = int(Goto.GetLineText(0))
        #except:
        #    pass #User entered non numerical value
        cur_doc.ScrollToLine(scroll_pos-1)


    def OnPrint(self ,event, text_id):
        FileName = wx.FindWindowById(text_id).SaveTarget
        if "/" not in FileName:
            FileName = "ForPrint"
        GoPrint = PrettyPrinter(FileName, text_id, self)

    def OnAbout(self,event):
        ShowAbout = AboutWindow
        ShowAbout()


    def OnQuit(self,event):
        Warn = wx.MessageDialog(None,"Please make sure that your data is\
 saved.\nAre you sure you want to quit?","Are you sure?",style = wx.YES_NO)
        WarnAnswer = Warn.ShowModal()
        if WarnAnswer != 5104:
            if Config.GetOption("BashShell"):
                self.BashShell.OnClose(event)
            if Config.GetOption("PythonShell"):
                self.PythonShell.OnClose(event)
            quit()


    def ManageCloseTab(self,event,text_id):
        cur_doc = wx.FindWindowById(text_id)
        TextCheck = cur_doc.GetText()
        if cur_doc.SaveRecord != TextCheck:
            SavePrompt = wx.MessageDialog(None, "The file "\
            +os.path.split(cur_doc.SaveTarget)[-1]+" is not saved.\n\
Do you wish to save it?","",style = wx.CANCEL | wx.YES| wx.NO )
            PromptValue = SavePrompt.ShowModal()
            if PromptValue == 5103:     #yes
                if not cur_doc.Save(0):
                    return
            elif PromptValue == 5101:    #Cancel
                return

            elif PromptValue == 5102:
                pass

            SavePrompt.Destroy()

        if self.TabCount == 0:
                try:
                    if Config.GetOption("BashShell"):
                        self.BashShell.OnClose(event)
                    if Config.GetOption("PythonShell"):
                        self.PythonShell.OnClose(event)
                except: pass
                quit()

        else:
            self.TabCount -= 1
            try:
                self.IdRange.remove(text_id)
            except: pass
            self.nb.RemovePage(self.nb.GetSelection())  #Memory leak
            cur_doc.Destroy()
            wx.FindWindowById(4003+text_id).GetParent().GetSizer().Clear(True)
            wx.FindWindowById(1001+text_id).Destroy()
        event.Skip()



    def OpenFile(self,event):
        OpenFileGetPath = wx.FileDialog(None, style = wx.OPEN|wx.FD_MULTIPLE)
        OpenFileGetPath.SetDirectory(self.HOMEDIR)

        if OpenFileGetPath.ShowModal() == wx.ID_OK:
            paths = OpenFileGetPath.GetPaths()
            for f in paths:
                self.NewTab(0,os.path.split(f)[-1], f)
                Log.AddLogEntry(time.ctime() + ": Opened file "+f)

        OpenFileGetPath.Destroy()


    def SetStatus(self,event,Text):
        self.StatusBar.SetStatusText(Text)
        event.Skip()


    def ResetStatus(self,event):
        self.StatusBar.SetStatusText("")
        event.Skip()


    def SaveAll(self,event):
        for id in self.IdRange:
            cur_doc = wx.FindWindowById(id)
            if cur_doc.SaveTarget != "" and cur_doc.SaveTarget != "New Document":
                    cur_doc.Save(0)



if __name__ == '__main__':
    app=wx.PySimpleApp()
    frame=Editor(parent=None,id=-1)
    frame.Show()
    app.MainLoop()
