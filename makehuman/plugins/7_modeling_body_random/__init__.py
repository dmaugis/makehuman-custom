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

from PyQt4.QtCore import *
from PyQt4.QtGui import *



class TextEdit(gui.GroupBox):
    def __init__(self, name, value=""):
        super(TextEdit, self).__init__(name)
        self.edit = self.addWidget(gui.TextEdit(value))

    def setValue(self, value):
        self.edit.setText(value)

    def getValue(self):
        return self.edit.getText()


def getRandomValue(minValue, maxValue, middleValue, sigmaFactor = 0.2):
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
        #filecache.MetadataCacher.__init__(self, self.extension, 'randomizer_filecache.mhc')
        self.selectedFile = None
        self.selectedRnd  = None

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


        toolbox = self.addLeftWidget(gui.SliderBox('Randomize settings'))
        self.macro = toolbox.addWidget(gui.CheckBox("Macro", True))
        self.face = toolbox.addWidget(gui.CheckBox("Face", True))
        self.body = toolbox.addWidget(gui.CheckBox("Body", True))

        self.symmetry = toolbox.addWidget(gui.Slider(value=0.7, min=0.0, max=1.0, label="Symmetry"))
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
        self.groups    = {}
        self.modifiers = {}
        self.sliders   = {}
        for mGroup in modifierGroups:
            self.groups[mGroup] = self.addLeftWidget(gui.SliderBox(mGroup))
            modifiers=self.human.getModifiersByGroup(mGroup)
            #self.modifiers = self.modifiers + self.human.getModifiersByGroup(mGroup)

            for m in modifiers:
               try:
                  #print m.fullName,"\t",m.getValue()," min ",m.getMin(), " max ",m.getMax(), " default ",m.getDefaultValue()
                  #self.sliders[m.fullName]=explorer.addWidget(gui.RangeSlider(start=1.0, end=999.0,min=0.0, max=1000.0, label=m.fullName))
                  self.sliders[m.fullName] = self.groups[mGroup].addWidget(gui.RangeSlider(start=1.0, end=999.0, min=0.0, max=1000.0, label=m.fullName))
               except:
                  pass

        @self.randomBtn.mhEvent
        def onClicked(event):
            randomize(self)

    def saveCurrentRandomizer(self, filename):
        import makehuman
        #unitpose_values = dict([(m, v) for m, v in self.modifiers.iteritems() if v != 0])
        #if len(unitpose_values) == 0:
        #    raise RuntimeError("Requires at least one pose to be specified")
        #tags = [t.strip() for t in self.tagsField.getValue().split(';')]

        data = {"name": self.nameField.getValue(),
                "description": self.descrField.getValue(),
                #"tags": tags,
                #"unit_poses": unitpose_values,
                "author": self.authorField.getValue(),
                "copyright": self.copyrightField.getValue(),
                "license": self.licenseField.getValue(),
                "homepage": self.websiteField.getValue()
                }
        print filename
        json.dump(data, open(filename, 'w'), indent=4)
        log.message("Saved randomizer as %s" % filename)


    def randomize(human):
        print "randomize(body)"
        randomValues = {}
        for m in self.modifiers:
            if m.fullName not in randomValues:
                randomValue = getRandomValue(m.getMin(), m.getMax(), m.getDefaultValue(),2.0)
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
