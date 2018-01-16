# -*- coding: UTF-8 -*-
import array

import wx
import wx.lib.newevent
import wx.lib.filebrowsebutton as fb

import df_files as df
import commented_json as c_json

NewEventResetPanel, EVT_RESET_PANEL = wx.lib.newevent.NewEvent()
# ConfigFrame
ID_APPLY_CONFIG = wx.NewId()
ID_SAVE_CONFIG = wx.NewId()
# EditColorFrame
ID_SAVE_COLORSCHEME = wx.NewId()
ID_APPLY_COLORSCHEME = wx.NewId()


class ConfigFrame(wx.Frame):
    count = 0

    def __init__(self, parent, title):
        style = (wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX
                 | wx.CLIP_CHILDREN)
        wx.Frame.__init__(self, parent, title=title, size=(420, 570), style=style)
        self.parent = parent
        self.nb = wx.Notebook(self, wx.ID_ANY, pos=(0, 0), size=(420, 300),
                              style=wx.CLIP_CHILDREN | wx.NB_TOP)
        self.txtctrl = wx.TextCtrl(self.nb,
                                   style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_RICH)
        self.txtctrl.LoadFile("config.json")
        self.nb.AddPage(self.txtctrl, "config.json")
        wx.Button(self, ID_APPLY_CONFIG, "Appliquer immédiatement",
                  pos=(0, 302), size=(200, 26))
        wx.Button(self, ID_SAVE_CONFIG, "Sauvegarder les modifications",
                  pos=(205, 302), size=(200, 26))
        print(self.FindWindow(ID_APPLY_CONFIG).GetSize().GetHeight())
        self.SetSize(420, 312+5+2*self.FindWindow(ID_APPLY_CONFIG)
                                      .GetDefaultSize()
                                      .GetHeight())
        # events
        self.Bind(wx.EVT_BUTTON, self.onSaveConfig, id=ID_SAVE_CONFIG)
        self.Bind(wx.EVT_BUTTON, self.onApplyConfig, id=ID_APPLY_CONFIG)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        ConfigFrame.count += 1

    def onApplyConfig(self, event):
        text = ""
        for i in range(self.txtctrl.GetNumberOfLines()):
            text += self.txtctrl.GetLineText(i) + "\n"
        self.parent.config = c_json.load(text)
        self.parent.loadRessources()
        if self.parent.map is not None:
            # we reload the map
            self.parent.loadArena()

    def onSaveConfig(self, event):
        try:
            open("config.json", 'r')
        except FileNotFoundError:
            open("config.json", 'w').close()
        else:
            self.txtctrl.SaveFile("config.json")

    def onClose(self, event):
        ConfigFrame.count -= 1
        self.Destroy()


class EditColorFrame(wx.Frame):
    count = 0
    Colors = [
        "BLACK",
        "BLUE",
        "GREEN",
        "CYAN",
        "RED",
        "MAGENTA",
        "BROWN",
        "DGRAY",
        "LGRAY",
        "LBLUE",
        "LGREEN",
        "LCYAN",
        "LRED",
        "LMAGENTA",
        "YELLOW",
        "WHITE",
    ]

    def __init__(self, parent, title):
        style = (wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX
                 | wx.CLIP_CHILDREN)
        wx.Frame.__init__(self, parent, title=title, style=style)
        self.parent = parent
        self.colors = parent.colorscheme
        self.panel = wx.Panel(self, -1)
        self.initPanel()
        EditColorFrame.count += 1

    def initPanel(self):
        gbs = wx.GridBagSizer(5, 5)
        hint = "Modifiez une couleur en cliquant dessus"
        gbs.Add(wx.StaticText(self.panel, wx.ID_ANY, hint),
                (0, 0), (1, 6), wx.ALIGN_CENTER | wx.ALL, 5)
        for i, color in enumerate(EditColorFrame.Colors):
            if i < 8:
                y = i+1
                x = 0
            else:
                y = i - 8 + 1
                x = 4
            gbs.Add(wx.StaticText(self.panel, wx.ID_ANY, color+" :"),
                    (y, x), flag=wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, border=5)
            r, g, b, a = self.colors[color].Get()
            data = [r, g, b]
            data = array.array('B', data)
            img = wx.Image(1, 1, data).Rescale(20, 20)
            n_id = wx.NewId()
            bmp = wx.StaticBitmap(self.panel, n_id, img.ConvertToBitmap(), name=color)
            gbs.Add(bmp, (y, x+1), flag=wx.EXPAND)
            bmp.Bind(wx.EVT_LEFT_DOWN, self.onEditColor, id=n_id)
        gbs.SetEmptyCellSize((1, 1))
        gbs.Add(wx.StaticLine(self.panel, -1, size=(200, 1), style=wx.LI_HORIZONTAL),
                (9, 0), (1, 6), wx.ALIGN_CENTER | wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self.fb = fb.FileBrowseButton(self.panel, wx.ID_ANY,
                                      labelText="Charger depuis un fichier :",
                                      buttonText="Parcourir",
                                      toolTip="",
                                      dialogTitle="Choisissez un fichier",
                                      changeCallback=self.onChooseFile)
        gbs.Add(self.fb, (10, 0), (1, 6), wx.EXPAND, 5)
        gbs.Add(wx.Button(self.panel, ID_APPLY_COLORSCHEME,
                "Appliquer les modifications"), (11, 0), (1, 3), wx.EXPAND, 5)
        gbs.Add(wx.Button(self.panel, ID_SAVE_COLORSCHEME, "Enregistrer"), (11, 3),
                (1, 3), wx.EXPAND, 5)
        self.panel.SetSizer(gbs)
        boxsizer = wx.BoxSizer()
        boxsizer.Add(self.panel)
        self.SetSizer(boxsizer)
        self.Fit()
        # events binding
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onSaveColors, id=ID_SAVE_COLORSCHEME)
        self.Bind(wx.EVT_BUTTON, self.onApplyColors, id=ID_APPLY_COLORSCHEME)
        self.Bind(EVT_RESET_PANEL, self.onResetPanel)

    def onClose(self, event):
        EditColorFrame.count -= 1
        self.Destroy()

    def onEditColor(self, event):
        colorId = event.Id
        children = self.panel.GetChildren()
        for child in children:
            if child.GetId() == colorId:
                # it's the one we want
                img = child.GetBitmap().ConvertToImage()
                r = img.GetRed(1, 1)
                g = img.GetGreen(1, 1)
                b = img.GetBlue(1, 1)
                dlg = wx.ColourDialog(self)
                data = dlg.GetColourData()
                data.SetChooseFull(True)
                data.SetColour(wx.Colour(r, g, b))
                if dlg.ShowModal() == wx.ID_OK:
                    # we get the new image
                    data = dlg.GetColourData()
                    nr, ng, nb, na = data.GetColour()
                    name = child.GetName()
                    gbs = self.panel.GetSizer()
                    newimg = wx.Image(1, 1, array.array('B', [nr, ng, nb]))
                    newimg.Rescale(20, 20)
                    # then replace the old staticbitmap
                    pos = gbs.GetItemPosition(child)
                    windowPos = child.GetPosition()
                    child.Destroy()
                    self.Freeze()
                    n_id = wx.NewId()
                    bmp = wx.StaticBitmap(self.panel, n_id, newimg.ConvertToBitmap(),
                                          pos=windowPos, name=name)
                    gbs.Add(bmp, pos, flag=wx.EXPAND)
                    bmp.Bind(wx.EVT_LEFT_DOWN, self.onEditColor, id=n_id)
                    self.panel.SetSizer(gbs)
                    self.Layout()  # repaint everything following sizer's rules
                    self.Thaw()
                    self.colors[name] = wx.Colour(nr, ng, nb)
                    break

    def onChooseFile(self, event):
        # we can't really destroy the panel while in its event's handler
        # so we push an event for that
        self.QueueEvent(NewEventResetPanel())

    def onResetPanel(self, event):
        file = self.fb.GetValue().replace('\\', '/')
        dfcolors = df.loadColorScheme(file).items()
        self.colors = {key: wx.Colour(value) for key, value in dfcolors}
        self.Freeze()
        self.panel.DestroyChildren()
        self.initPanel()
        self.Layout()
        self.Thaw()

    def onSaveColors(self, event):
        dlg = wx.FileDialog(self, "Enregistrer le fichier", "saved", "colors.txt",
                            wildcard="fichiers textes (*.txt)|*.txt",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            df.saveColorScheme(self.colors, file)

    def onApplyColors(self, event):
        self.parent.colorscheme = self.colors
        self.parent.loadRessources(loadColors=False)
        if self.parent.map is not None:
            self.parent.loadArena()
            self.parent.arenaChanged = False
