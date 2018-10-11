#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
**Project Name:**      

**Product Home Page:** 

**Code Home Page:**    

**Authors:**           

**Copyright(c):**      

**Licensing:**         

Abstract
--------



"""
import os
import sys
import json
import gui3d
import mh
import gui
import guirender
import log
import socket
import json
import scene
import log
import filecache
import filechooser as fc
import getpath
import random

from PyQt4.QtCore import *
from PyQt4.QtGui import *

DEFAULT_CSS = """
QRangeSlider * {
    border: 0px;
    padding: 0px;
}
QRangeSlider #Head {
    background: #737373;
}
QRangeSlider #Span {
    background: #ffcc00;
}
QRangeSlider #Span:active {
    background: #ff9933;
}
QRangeSlider #Tail {
    background: #737373;
}
QRangeSlider > QSplitter::handle {
    background: #393;
}
QRangeSlider > QSplitter::handle:vertical {
    height: 4px;
}
QRangeSlider > QSplitter::handle:pressed {
    background: #ca5;
}

"""

"""=================================================="""


class TextEdit(gui.GroupBox):
    def __init__(self, name, value=""):
        super(TextEdit, self).__init__(name)
        self.edit = self.addWidget(gui.TextEdit(value))

    def setValue(self, value):
        self.edit.setText(value)

    def getValue(self):
        return self.edit.getText()


def getRandomValue(minValue, maxValue, middleValue, sigmaFactor=0.2):
    rangeWidth = float(abs(maxValue - minValue))
    sigma = sigmaFactor * rangeWidth
    randomVal = random.gauss(middleValue, sigma)
    if randomVal < minValue:
        randomVal = minValue + abs(randomVal - minValue)
    elif randomVal > maxValue:
        randomVal = maxValue - abs(randomVal - maxValue)
    return max(minValue, min(randomVal, maxValue))


class RandomBodyTaskView(guirender.RenderTaskView):
    def __init__(self, category):
        self.human = gui3d.app.selectedHuman
        guirender.RenderTaskView.__init__(self, category, 'RandomBody')
        self.extension = 'mhrnd'
        # filecache.MetadataCacher.__init__(self, self.extension, 'randomizer_filecache.mhc')
        self.selectedFile = None
        self.selectedRnd = None

        self.sysDataPath = getpath.getSysDataPath('randomizers')
        self.userPath = getpath.getDataPath('randomizers')
        self.paths = [self.userPath, self.sysDataPath]
        if not os.path.exists(self.userPath):
            os.makedirs(self.userPath)

        savebox = self.addRightWidget(gui.GroupBox("Save"))

        self.nameField = savebox.addWidget(TextEdit("Name"))
        self.descrField = savebox.addWidget(TextEdit("Description"))
        self.tagsField = savebox.addWidget(TextEdit("Tags (separate with ;)"))
        self.authorField = savebox.addWidget(TextEdit("Author"))
        self.copyrightField = savebox.addWidget(TextEdit("Copyright"))
        self.licenseField = savebox.addWidget(TextEdit("License"))
        self.websiteField = savebox.addWidget(TextEdit("Website"))
        self.saveBtn = savebox.addWidget(gui.BrowseButton('save', "Save randomizer"))
        self.saveBtn.setFilter("MakeHuman randomizer file (*.mhrnd)")
        savepath = getpath.getDataPath('randomizers')
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        self.saveBtn.setDirectory(getpath.getDataPath('randomizers'))

        @self.saveBtn.mhEvent
        def onClicked(path):
            if path:
                if not os.path.splitext(path)[1]:
                    path = path + ".mhrnd"
                self.saveCurrentRandomizer(path)

        self.filechooser = self.addRightWidget(fc.ListFileChooser( \
            self.paths,
            self.extension,
            name='Randomizer'))
        self.filechooser.enableAutoRefresh(True)

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            self.loadRandomizer(filename)

        toolbox = self.addLeftWidget(gui.SliderBox('Randomize settings'))
        self.fromDefaultsBtn = toolbox.addWidget(gui.Button("from Defaults"))
        self.fromCurrentBtn = toolbox.addWidget(gui.Button("from Current"))

        self.macro = toolbox.addWidget(gui.CheckBox("Macro", True))
        self.face = toolbox.addWidget(gui.CheckBox("Face", True))
        self.body = toolbox.addWidget(gui.CheckBox("Body", True))

        self.symmetry = toolbox.addWidget(gui.Slider(value=0.7, min=0.0, max=1.0, label="Symmetry"))
        self.sigma = toolbox.addWidget(gui.Slider(value=0.2, min=0.0, max=1.0, label="Sigma"))



        self.randomBtn = toolbox.addWidget(gui.Button("Randomize"))

        #################################

        modifierGroups = []
        if self.macro:
            modifierGroups = modifierGroups + ['macrodetails', 'macrodetails-universal', 'macrodetails-proportions']
        if self.body:
            modifierGroups = modifierGroups + ['pelvis', 'hip', 'armslegs', 'stomach', 'breast', 'buttocks', 'torso']
        if self.face:
            modifierGroups = modifierGroups + ['eyebrows', 'eyes', 'chin',
                                               'forehead', 'head', 'mouth', 'nose', 'neck', 'ears',
                                               'cheek']

        modifierGroups = modifierGroups + [ 'custom' ]
        
        self.groups = {}
        self.modifiers = {}
        self.sliders = {}
        for mGroup in modifierGroups:
            self.groups[mGroup] = self.addLeftWidget(gui.RangeSliderBox(mGroup))
            modifiers = self.human.getModifiersByGroup(mGroup)
            for m in modifiers:
                try:
                    label=None
                    if label is None:
                        # Guess a suitable slider label from target name
                        tlabel = m.name.split('-')
                        if "|" in tlabel[len(tlabel) - 1]:
                            tlabel = tlabel[:-1]
                        if len(tlabel) > 1 and tlabel[0] == m.groupName:
                            label = tlabel[1:]
                        else:
                            label = tlabel
                        label = ' '.join([word.capitalize() for word in label])

                    # create range slider
                    rs = gui.RangeSlider(label)
                    rs.modifier = m
                    #rs.modifier_name = m.fullName
                    self.sliders[m.fullName] = self.groups[mGroup].addWidget(rs)
                    pass
                except:
                    print "error:", sys.exc_info()
                    exit(-1)
        pass

        @self.randomBtn.mhEvent
        def onClicked(event):
            self.randomize()

        @self.fromDefaultsBtn.mhEvent
        def onClicked(event):
            self.fromDefaults()

        @self.fromCurrentBtn.mhEvent
        def onClicked(event):
            self.fromCurrent()

    def fromDefaults(self):
        for m in self.sliders:
            print m, " ",self.human.getModifier(m).getDefaultValue()
            mod=self.human.getModifier(m)
            curval=99*(mod.getDefaultValue()-mod.getMin())/(mod.getMax()-mod.getMin())
            s = self.sliders[m]
            minval=max(int(curval-self.sigma.getValue()),0)
            maxval=min(int(curval+self.sigma.getValue()),99)
            s.setRange([minval,maxval])
        pass

    def fromCurrent(self):
        for m in self.sliders:
            print m, " ",self.human.getModifier(m).getValue()
            mod=self.human.getModifier(m)
            curval=99*(mod.getValue()-mod.getMin())/(mod.getMax()-mod.getMin())
            s = self.sliders[m]
            minval=max(int(curval-self.sigma.getValue()),0)
            maxval=min(int(curval+self.sigma.getValue()),99)
            s.setRange([minval,maxval])
        pass

# getSymmetricOpposite
    def randomize(self):
        print "randomize(body)"
        randomValues = {}
        for m in self.sliders:
            # get the slider gadget
            s = self.sliders[m]
            # get associated modifier
            mod=s.modifier
            #print "symmetry: ",self.symmetry.getValue()
            if mod.getSymmetrySide() is None or self.symmetry.getValue()<0.1:
                # no need to take symmetry into account -> random value
                svalue = float(getRandomValue(s.start(), s.end(), (s.end() + s.start()) / 2, self.sigma.getValue()))
                # translate to modifier value
                modvalue = float(mod.getMin()) + (float(svalue - s.min()) / float(s.max() - s.min())) * float(mod.getMax() - mod.getMin())
                # apply
                self.human.getModifier(m).setValue(modvalue)
            elif mod.getSymmetrySide() == 'l':
                #print "symmetric ", mod.fullName
                svalue = float(getRandomValue(s.start(), s.end(), (s.end() + s.start()) / 2, self.sigma.getValue()))
                modvalue = float(mod.getMin()) + (float(svalue - s.min()) / float(s.max() - s.min())) * float(mod.getMax() - mod.getMin())
                self.human.getModifier(m).setValue(modvalue)
                m2 = mod.getSymmetricOpposite()
                s2=self.sliders[m2]
                mod2=s2.modifier
                if svalue> s2.start() or svalue<s2.end():
                    svalue2 = float(getRandomValue(s2.start(), s2.end(), svalue, self.sigma.getValue()))
                else:
                    svalue2 = float(getRandomValue(s2.start(), s2.end(), (s2.end() + s2.start()) / 2, 1.0-self.symmetry.getValue()))
                modvalue2 = float(mod2.getMin()) + (float(svalue2 - s2.min()) / float(s2.max() - s2.min())) * float(mod2.getMax() - mod2.getMin())
                self.human.getModifier(m2).setValue(modvalue2)
                pass


        self.human.applyAllTargets()


    def saveCurrentRandomizer(self, filename):
        all = {}
        header = {"name": self.nameField.getValue(),
                  "description": self.descrField.getValue(),
                  # "tags": tags,
                  # "unit_poses": unitpose_values,
                  "author": self.authorField.getValue(),
                  "copyright": self.copyrightField.getValue(),
                  "license": self.licenseField.getValue(),
                  "homepage": self.websiteField.getValue(),
                  "version": 0.1
                  }
        all["info"] = header
        modif = {}
        for s in self.sliders:
            modif[s] = self.sliders[s].getRange()
        all["modifiers"] = modif
        json.dump(all, open(filename, 'w'), indent=4)
        log.message("Saved randomizer as %s" % filename)


    def loadRandomizer(self, filename):
        print "filename:", filename
        with open(filename) as json_data:
            _dict = json.load(json_data)
            # header infos
            header = _dict["info"]
            self.nameField.setValue(header["name"])
            self.descrField.setValue(header["description"])
            self.authorField.setValue(header["author"])
            self.copyrightField.setValue(header["copyright"])
            self.licenseField.setValue(header["license"])
            self.websiteField.setValue(header["homepage"])
            # modifiers infos
            modif = _dict["modifiers"]
            for k in modif:
                try:
                    self.sliders[k].setRange(modif[k])
                except:
                    pass

    def onShow(self, event):
        guirender.RenderTaskView.onShow(self, event)


category = None
taskview = None


def load(app):
    category = app.getCategory('Modelling')
    taskview = category.addTask(RandomBodyTaskView(category))


def unload(app):
    if taskview:
        taskview.closeSocket()
