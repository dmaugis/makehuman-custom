#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman community assets

**Product Home Page:** http://www.makehumancommunity.org

**Code Home Page:**    https://github.com/makehumancommunity/community-plugins

**Authors:**           Joel Palmius

**Copyright(c):**      Joel Palmius 2016

**Licensing:**         MIT

Abstract
--------

This plugin manages community assets

"""

import gui3d
import mh
import gui
import log
import json
import urllib2
import os
import re
import platform
import calendar, datetime


from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *

from progress import Progress

from core import G

mhapi = gui3d.app.mhapi

class AssetDownloadTaskView(gui3d.TaskView):

    def __init__(self, category):        
        
        gui3d.TaskView.__init__(self, category, 'Download assets')

        self.notfound = mhapi.locations.getSystemDataPath("notfound.thumb")

        self.human = gui3d.app.selectedHuman

        self.selectBox = self.addLeftWidget(gui.GroupBox('Select asset'))

        self.selectBox.addWidget(gui.TextView("\nType"))
        #self.typeList = self.selectBox.addWidget(gui.ListView())
        #self.typeList.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)


        types = [
            "Target",
            "Clothes",
            "Hair",
            "Teeth",
            "Eyebrows",
            "Eyelashes",
            "Skin",
            "Proxy",
            "Pose",
            "Material",
            "Model",
            "Rig"
        ]

        self.typeList = mhapi.ui.createComboBox(types,self.onTypeChange)
        self.selectBox.addWidget(self.typeList)

        #self.typeList.setData(types)
        #self.typeList.setCurrentRow(0)
        #self.typeList.selectionModel().selectionChanged.connect(self.onTypeChange)

        categories = [
            "All"
        ]

        self.selectBox.addWidget(gui.TextView("\nCategory"))
        self.categoryList = mhapi.ui.createComboBox(categories,self.onCategoryChange)
        self.selectBox.addWidget(self.categoryList)
        self.categoryList.setCurrentRow(0)

        self.selectBox.addWidget(gui.TextView("\nAsset"))
        self.assetList = self.selectBox.addWidget(gui.ListView())
        self.assetList.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)

        assets = [
        ]

        self.assetList.setData(assets)
        self.assetList.selectionModel().selectionChanged.connect(self.onAssetChange)

        self.selectBox.addWidget(gui.TextView(" "))

        self.downloadButton = self.selectBox.addWidget(gui.Button('Download'))
        self.downloadButton.setDisabled(True)

        self.downloadLabel = self.selectBox.addWidget(gui.TextView(" "))
        self.downloadLabel.setWordWrap(True)
        
        @self.downloadButton.mhEvent
        def onClicked(event):
            self.downloadButtonClick()

        self.refreshBox = self.addRightWidget(gui.GroupBox('Synchronize'))
        refreshString = "Synchronizing data with the server can take some time, so it is not done automatically. Synchronizing will also download thumbnails and screenshots, if available. Click here to start the synchronization."
        self.refreshLabel = self.refreshBox.addWidget(gui.TextView(refreshString))
        self.refreshLabel.setWordWrap(True)
        self.refreshButton = self.refreshBox.addWidget(gui.Button('Synchronize'))

        @self.refreshButton.mhEvent
        def onClicked(event):
            self.refreshButtonClick()

        self.mainPanel = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()

        self.assetInfoBox = gui.GroupBox("Asset info")
        self.assetInfoText = self.assetInfoBox.addWidget(gui.TextView("No asset selected"))
        self.assetDescription = self.assetInfoBox.addWidget(gui.TextView("-"))
        self.assetDescription.setWordWrap(True)

        layout.addWidget(self.assetInfoBox)

        self.assetThumbBox = gui.GroupBox("Asset thumbnail (if any)")
        self.thumbnail = self.assetThumbBox.addWidget(gui.TextView())
        self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
        self.thumbnail.setGeometry(0,0,128,128)

        layout.addWidget(self.assetThumbBox)

        self.assetScreenieBox = gui.GroupBox("Asset screenshot (if any)")
        self.screenshot = self.assetScreenieBox.addWidget(gui.TextView(""))
        self.screenshot.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))

        layout.addWidget(self.assetScreenieBox)

        layout.addStretch(1)

        self.mainPanel.setLayout(layout)

        self.addTopWidget(self.mainPanel)

        self.setupAssetDir()

    def comboChange(self,item = None):
        log.debug("comboChange")

    def showMessage(self,message,title="Information"):
        self.msg = QtGui.QMessageBox()
        self.msg.setIcon(QtGui.QMessageBox.Information)
        self.msg.setText(message)
        self.msg.setWindowTitle(title)
        self.msg.setStandardButtons(QtGui.QMessageBox.Ok)
        self.msg.show()

    def onTypeChange(self,item = None):
        assetType = str(item)
        log.debug("onTypeChange: " + assetType)

        if assetType == "Clothes":
            cats = sorted(self.clothesAssets.keys())
            self.categoryList.setData(cats)
            self.assetList.setData(sorted(self.clothesNames["All"]))
        else:
            self.categoryList.setData(["All"])
            self.categoryList.setCurrentRow(0)

            assets = []

            if assetType == "Target":
                assets = self.targetNames
            if assetType == "Hair":
                assets = self.hairNames
            if assetType == "Proxy":
                assets = self.proxyNames
            if assetType == "Skin":
                assets = self.skinNames
            if assetType == "Pose":
                assets = self.poseNames
            if assetType == "Material":
                assets = self.materialNames
            if assetType == "Rig":
                assets = self.rigNames
            if assetType == "Model":
                assets = self.modelNames
            if assetType == "Teeth":
                assets = self.teethNames
            if assetType == "Eyebrows":
                assets = self.eyebrowsNames
            if assetType == "Eyelashes":
                assets = self.eyelashesNames
                
            self.assetList.setData(sorted(assets))

        self.categoryList.setCurrentItem("All")

        self.screenshot.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
        self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
        self.assetInfoText.setText("Nothing selected")

    def getScreenshotPath(self,asset):
        if not asset:
            return None
        if not "files" in asset:
            return None

        files = asset["files"]

        r = None

        if "render" in files:
            r = files["render"]
        else:
            if "illustration" in files:
                r = files["illustration"]

        if not r:
            return None

        fn = r.rsplit('/', 1)[-1]

        if not fn:
            return None

        extension = os.path.splitext(fn)[1]

        if not extension:
            return None

        extension = extension.lower()

        filename = "screenshot" + extension
        assetDir = os.path.join(self.root,str(asset["nid"]))
        fullPath = mhapi.locations.getUnicodeAbsPath(os.path.join(assetDir,filename))

        log.debug("Screenshot path: " + fullPath)

        return fullPath


    def onCategoryChange(self,item = None):
        assetType = str(self.typeList.getCurrentItem())
        log.debug("onCategoryChange() " + assetType)

        if assetType == "Clothes":            
            category = str(self.categoryList.getCurrentItem())
            if category == '' or not category:
                category = "All"
            self.assetList.setData(sorted(self.clothesNames[category]))
            self.screenshot.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
            self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
            self.assetInfoText.setText("Nothing selected")

    def onAssetChange(self):
        assetType = str(self.typeList.getCurrentItem())
        self.downloadButton.setDisabled(False)

        log.debug("Asset change: " + assetType)

        if assetType == "Target":
            self.onSelectTarget()
        if assetType == "Skin":
            self.onSelectSkin()
        if assetType == "Clothes":
            self.onSelectClothes()
        if assetType == "Hair":
            self.onSelectHair()
        if assetType == "Pose":
            self.onSelectPose()
        if assetType == "Proxy":
            self.onSelectProxy()
        if assetType == "Material":
            self.onSelectMaterial()
        if assetType == "Rig":
            self.onSelectRig()
        if assetType == "Model":
            self.onSelectModel()
        if assetType == "Teeth":
            self.onSelectTeeth()
        if assetType == "Eyebrows":
            self.onSelectEyebrows()
        if assetType == "Eyelashes":
            self.onSelectEyelashes()
            
    def showButtonClick(self):
        self.showMessage("message","title")

    def downloadButtonClick(self):      
        assetType = str(self.typeList.getCurrentItem())

        log.debug("Download: " + assetType)

        if assetType == "Target":
            self.downloadTarget()
        if assetType == "Skin":
            self.downloadSkin()
        if assetType == "Clothes":
            self.downloadClothes()
        if assetType == "Hair":
            self.downloadHair()
        if assetType == "Pose":
            self.downloadPose()
        if assetType == "Proxy":
            self.downloadProxy()
        if assetType == "Material":
            self.downloadMaterial()
        if assetType == "Rig":
            self.downloadRig()
        if assetType == "Model":
            self.downloadModel()
        if assetType == "Teeth":
            self.downloadTeeth()
        if assetType == "Eyebrows":
            self.downloadEyebrows()
        if assetType == "Eyelashes":
            self.downloadEyelashes()
            
    def refreshButtonClick(self):

        self.progress = Progress()
        self.progress(0.0,0.1)

        web = urllib2.urlopen("http://www.makehumancommunity.org/sites/default/files/assets.json");
        jsonstring = web.read()
        assetJson = json.loads(jsonstring)

        increment = 0.8 / len(assetJson.keys())
        current = 0.1

        log.debug("Finished downloading json file")

        for key in assetJson.keys():
            current = current + increment
            self.progress(current,current + increment)
            self.setupOneAsset(assetJson[key])

        with open(os.path.join(self.root,"assets.json"),"w") as f:
            f.write(jsonstring)

        self.loadAssetsFromJson(assetJson)

        self.progress(1.0)

    def downloadUrl(self, url, saveAs=None, asset=None, fileName=None):
        try:
            url = re.sub(r"\s","%20",url)
            data = urllib2.urlopen(url).read()
            newData = self.normalizeFiles(data,asset,saveAs,fileName)
            with open(saveAs,"wb") as f:
                f.write(newData)                
        except:
            log.debug("failed to write file")
            return False    
        return True

    def loadAssetsFromJson(self, assetJson):

        self.clothesAssets = dict()
        self.clothesAssets["All"] = [];

        self.hairAssets = []
        self.skinAssets = []
        self.targetAssets = []
        self.proxyAssets = []
        self.poseAssets = []
        self.materialAssets = []
        self.rigAssets = []
        self.modelAssets = []
        self.teethAssets = []
        self.eyebrowsAssets = []
        self.eyelashesAssets = []
        
        self.clothesNames = dict()
        self.clothesNames["All"] = [];

        self.hairNames = []
        self.skinNames = []
        self.targetNames = []
        self.proxyNames = []
        self.poseNames = []
        self.materialNames = []
        self.rigNames = []
        self.modelNames = []
        self.teethNames = []
        self.eyebrowsNames = []
        self.eyelashesNames = []
        
        for key in assetJson.keys():
            asset = assetJson[key]
            aType = asset["type"]
            aCat = "All"

            found = False
            
            """To incresse load times there may be a way to turn on or off the checkAssetDir onload,
            This will cause the items a user has downlaoded to appair in the selection lists.."""
            if aType == "clothes":
                aCat = asset["category"]

                if aCat == "Hair":
                    if self.checkAssetDir(asset,"hair"):
                        self.hairAssets.append(asset)
                        self.hairNames.append(asset["title"])
                        found = True
                elif aCat == "Teeth":
                    if self.checkAssetDir(asset,"teeth"):
                        self.teethAssets.append(asset)
                        self.teethNames.append(asset["title"])
                        found = True
                elif aCat == "Eyebrows":
                    if self.checkAssetDir(asset,"eyebrows"):
                        self.eyebrowsAssets.append(asset)
                        self.eyebrowsNames.append(asset["title"])
                        found = True
                elif aCat == "Eyelashes":
                    if self.checkAssetDir(asset,"eyelashes"):
                        self.eyelashesAssets.append(asset)
                        self.eyelashesNames.append(asset["title"])
                        found = True
                else:
                    if self.checkAssetDir(asset):
                        self.clothesAssets["All"].append(asset)
                        self.clothesNames["All"].append(asset["title"])
                        if not aCat in self.clothesAssets.keys():
                            self.clothesAssets[aCat] = []
                        if not aCat in self.clothesNames.keys():
                            self.clothesNames[aCat] = []
                        self.clothesAssets[aCat].append(asset)
                        self.clothesNames[aCat].append(asset["title"])
                        found = True

            if aType == "target":
                if self.checkAssetDir(asset,"custom"):
                    self.targetAssets.append(asset)
                    self.targetNames.append(asset["title"])
                    found = True

            if aType == "skin":
                if self.checkAssetDir(asset,"skins"):
                    self.skinAssets.append(asset)
                    self.skinNames.append(asset["title"])
                    found = True

            if aType == "proxy":
                if self.checkAssetDir(asset,"proxymeshes"):
                    self.proxyAssets.append(asset)
                    self.proxyNames.append(asset["title"])
                    found = True

            if aType == "pose":
                if self.checkAssetDir(asset,"poses"):
                    self.poseAssets.append(asset)
                    self.poseNames.append(asset["title"])
                    found = True
                    
            if aType == "material":
                if self.checkAssetDir(asset,"material"):
                    self.materialAssets.append(asset)
                    self.materialNames.append(asset["title"])
                    found = True
                    
            if aType == "rig":
                if self.checkAssetDir(asset,"rigs"):
                    self.rigAssets.append(asset)
                    self.rigNames.append(asset["title"])
                    found = True
                    
            if aType == "model":
                if self.checkAssetDir(asset,"model"):
                    self.modelAssets.append(asset)
                    self.modelNames.append(asset["title"])
                    found = True
                    
            if not found:
                log.debug("Unmatched asset type. " + str(asset["nid"]) + " (" + asset["type"] + "): " + asset["title"])

        self.assetList.setData(sorted(self.hairNames))
        self.typeList.setCurrentItem("Hair")
        self.categoryList.setCurrentItem("All")
        
    def setupOneAsset(self, jsonHash):

        assetDir = os.path.join(self.root,str(jsonHash["nid"]))
        if not os.path.exists(assetDir):
            os.makedirs(assetDir)
        if "files" in jsonHash.keys():
            files = jsonHash["files"]
            if "render" in files.keys():
                #fn = os.path.join(assetDir,"screenshot.png")
                fn = self.getScreenshotPath(jsonHash)
                if not os.path.exists(fn):                    
                    #log.debug("Downloading " + files["render"])
                    self.downloadUrl(files["render"],fn)
                else:
                    log.debug("Screenshot already existed")

            if "thumb" in files.keys():
                fn = os.path.join(assetDir,"thumb.png")
                if not os.path.exists(fn):                    
                    log.debug("Downloading " + files["thumb"])
                    self.downloadUrl(files["thumb"],fn)
                else:
                    log.debug("thumb already existed")

    def setupAssetDir(self):

        self.root = mhapi.locations.getUserDataPath("community-assets")

        if not os.path.exists(self.root):
            os.makedirs(self.root)

        assets = mhapi.locations.getUnicodeAbsPath(os.path.join(self.root,"assets.json"))

        if os.path.exists(assets):
            with open(assets,"r") as f:
                jsonstring = f.read()
                assetJson = json.loads(jsonstring)
                self.loadAssetsFromJson(assetJson)
                
    def checkAssetDir(self,asset, typeHint= None):

        if typeHint:
            assetTypeDir = mhapi.locations.getUserDataPath(typeHint)        
        else:
            assetTypeDir = mhapi.locations.getUserDataPath(asset["type"])        

        name = asset["title"]
        name = re.sub(r"\s","_",name)
        name = re.sub(r"\W","",name)

        if typeHint == "custom":
            head, tail = os.path.split(asset["files"]["file"])
            assetDir = os.path.join(assetTypeDir, tail)
            """assetDir = assetTypeDir"""
        else:
            assetDir = mhapi.locations.getUnicodeAbsPath(os.path.join(assetTypeDir,name))

        if typeHint == "material":
           if "belongs_to" in asset:
              if "belonging_is_assigned" in asset["belongs_to"]:
                 if asset["belongs_to"]["belonging_is_assigned"] == True:
                      #log.debug("material belongs to " + asset["belongs_to"]["belongs_to_title"]) 
                      name = asset["belongs_to"]["belongs_to_title"]
                      name = re.sub(r"\s","_",name)
                      name = re.sub(r"\W","",name)
                      tempPath = asset["belongs_to"]["belongs_to_type"]
                      #log.debug(tempPath)
                      assetTypeDir = mhapi.locations.getUserDataPath(tempPath)
                      assetDir = mhapi.locations.getUnicodeAbsPath(os.path.join(os.path.join(assetTypeDir,name),"material"))
                 else:
                      log.debug("material has no belongs to")
              else:
                  log.debug("material belongs_to_assigned not found")
           else:
                log.debug("material belongs_to not found")
                
        log.debug("Checking : " + assetDir)
        
        if os.path.exists(assetDir):
            from datetime import datetime as dt
            for files in asset["files"]:
                assetFile = asset["files"][files] 
                log.debug(assetFile)
                head, tail = os.path.split(assetFile)
                assetFile = os.path.join(assetDir, tail)
                if os.path.exists(assetFile):
                    if typeHint == "custom":
                       assetFile = assetDir
                    changed = asset.get("changed",None)
                    if changed:
                       remoteDate = dt.strptime(asset["changed"], '%Y-%m-%d')
                       #log.debug(remoteDate)
                       #log.debug("Checking : " + assetFile)
                       localDate = dt.strptime(self.get_modified_date(assetFile), '%Y-%m-%d')
                       #log.debug(localDate)
                       if localDate > remoteDate:
                           return False
                       else:
                           return True
                    else:
                        return False
                else:
                    return False
        else:
             return True
            
    """This may cause an error if the file dont have a .ext"""
    
    def get_extension(self,filename):
        output = filename.split(".")
        return output[-1] if len(output)>1 else ''
    
    def get_modified_date(self,path_to_file):
        return datetime.datetime.utcfromtimestamp(os.path.getmtime(path_to_file)).strftime('%Y-%m-%d')

    def setThumbScreenshot(self,asset):
        assetDir = mhapi.locations.getUnicodeAbsPath(os.path.join(self.root,str(asset["nid"])))
        screenshot = self.getScreenshotPath(asset)
        thumbnail = mhapi.locations.getUnicodeAbsPath(os.path.join(assetDir,"thumb.png"))
 
        if screenshot and os.path.exists(screenshot):
            self.screenshot.setPixmap(QtGui.QPixmap(os.path.abspath(screenshot)))
        else:
            self.screenshot.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
 
        if os.path.exists(thumbnail):
            self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(thumbnail)))
        else:
            self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
 
        self.thumbnail.setGeometry(0,0,128,128)

    def setDescription(self,asset):
        desc = "<big>" + asset["title"] + "</big><br />\n&nbsp;<br />\n"
        desc = desc + "<b><tt>Author.........: </tt></b>" + asset["username"] + "<br />\n"

        if "license" in asset.keys():
            desc = desc + "<b><tt>License........: </tt></b>" + asset["license"] + "<br />\n"
        if "compatibility" in asset.keys():
            desc = desc + "<b><tt>Compatibility..: </tt></b>" + asset["compatibility"] + "<br />\n"


        key = None

        if asset["type"] == "clothes":
            key = "mhclo"
        if asset["type"] == "hair":
            key = "mhclo"
        if asset["type"] == "teeth":
            key = "mhmat"
        if asset["type"] == "eyebrows":
            key = "mhmat"
        if asset["type"] == "eyelashes":
            key = "mhmat"
        if asset["type"] == "skin":
            key = "mhmat"
        if asset["type"] == "target":
            key = "file"
        if asset["type"] == "proxy":
            key = "file"
        if asset["type"] == "target":
            key = "file"
        if asset["type"] == "material":
            key = "mhmat"
        if asset["type"] == "rig":
            key = "file"
        if asset["type"] == "model":
            key = "file"


        if key:
            url = asset["files"][key]
            fn = url.rsplit('/', 1)[-1]
            fn = fn.replace("." + key,"")
            fn = fn.replace("_"," ")            
            desc = desc + "<b><tt>Name in MH.....: </tt></b>" + fn + "<br />\n"

        self.assetInfoText.setText(desc)
        self.assetDescription.setText(asset["description"])
        #debug.log(desc + asset["description"])

    def onSelectTarget(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.targetAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def onSelectPose(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.poseAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)
            
    def onSelectMaterial(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.materialAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)
            
    def onSelectRig(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.rigAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def onSelectModel(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.modelAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)
            
    def onSelectProxy(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.proxyAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def onSelectEyebrows(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.eyebrowsAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def onSelectEyelashes(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.eyelashesAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def onSelectSkin(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.skinAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def onSelectClothes(self):
        foundAsset = None
        category = str(self.categoryList.getCurrentItem())
        name = str(self.assetList.currentItem().text)
        for asset in self.clothesAssets[category]:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def onSelectHair(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.hairAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)
            
    def onSelectTeeth(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.teethAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def downloadAsset(self,asset,typeHint = None):
        files = asset["files"]

        if typeHint:
            assetTypeDir = mhapi.locations.getUserDataPath(typeHint)        
        else:
            assetTypeDir = mhapi.locations.getUserDataPath(asset["type"])        

        name = asset["title"]
        name = re.sub(r"\s","_",name)
        name = re.sub(r"\W","",name)

        if typeHint == "custom":
            assetDir = assetTypeDir
        else:
            assetDir = mhapi.locations.getUnicodeAbsPath(os.path.join(assetTypeDir,name))

        if typeHint == "material":
           if "belongs_to" in asset:
              if "belonging_is_assigned" in asset["belongs_to"]:
                 if asset["belongs_to"]["belonging_is_assigned"] == True:
                      #log.debug("material belongs to " + asset["belongs_to"]["belongs_to_title"]) 
                      name = asset["belongs_to"]["belongs_to_title"]
                      name = re.sub(r"\s","_",name)
                      name = re.sub(r"\W","",name)
                      tempPath = asset["belongs_to"]["belongs_to_type"]
                      #log.debug(tempPath)
                      assetTypeDir = mhapi.locations.getUserDataPath(tempPath)
                      assetDir = mhapi.locations.getUnicodeAbsPath(os.path.join(os.path.join(assetTypeDir,name),"material"))
                 else:
                      msg = "Asset was not downloaded. Please visit http://www.makehumancommunity.org/materials.html to download this asset."
                      self.downloadLabel.setText(msg)
                      return
              else:
                  log.debug("material belongs_to_assigned not found")
           else:
                log.debug("material belongs_to not found") 
        log.debug("Downloading to: " + assetDir)

        if not os.path.exists(assetDir):
            os.makedirs(assetDir)

        self.progress = Progress()
        self.progress(0.0,0.1)

        increment = 0.8 / len(files.keys())
        current = 0.1

        key = None

        if asset["type"] == "clothes":
            key = "mhclo"
        if asset["type"] == "hair":
            key = "mhclo"
        if asset["type"] == "teeth":
            key = "mhmat"
        if asset["type"] == "eyebrows":
            key = "mhmat"
        if asset["type"] == "eyelashes":
            key = "mhmat"
        if asset["type"] == "skin":
            key = "mhmat"
        if asset["type"] == "material":
            key = "mhmat"
        if asset["type"] == "rig":
            key = "mhskel"
        if asset["type"] == "pose":
            key = "bvh"
        if asset["type"] == "proxy":
            key = "file"
        if asset["type"] == "target":
            key = "file"
        if asset["type"] == "model":
            key = "file"
        ext = key

        if asset["type"] == "target":
            ext = "target"
        if asset["type"] == "proxy":
            ext = "proxy"
        if asset["type"] == "model":
            ext = "mhm"
            
        msg = "Asset was downloaded"
        base = ""

        if key:
            url = asset["files"][key]
            mbase = url.rsplit('/', 1)[-1]
            mbase = mbase.replace("." + ext,"")
            base = mbase
            mbase = mbase.replace("_"," ")            
            msg = msg + " as \"" + mbase + "\""

        for f in files.keys():
            if f != "render":
                current = current + increment
                url = files[f]
                if f == "thumb":
                    fn = base + ".thumb"
                else:
                    fn = url.rsplit('/', 1)[-1]
                saveAs = os.path.join(assetDir,fn)
                
                log.debug("Downloading " + url)
                self.downloadUrl(url,saveAs, asset, fn)
                self.progress(current, current + increment)
                
                
        self.progress(1.0)
        self.downloadLabel.setText(msg)
        """self.showMessage(msg)"""

    def normalizeFiles(self, data, asset, saveAs, fileName):
        if not fileName == None:
            if self.get_extension(fileName) == "mhmat":
                lines = data.split("\n")
                output = []
                for line in lines:
                    if "name" in line:
                         filename = os.path.basename(saveAs)
                         name = os.path.splitext(filename)[0]
                         line = "name " + name
                         log.debug(line)
                    if "obj_file" in line:
                        if "obj" in asset["files"]:
                            of = asset["files"]["obj"].rsplit('/', 1)[-1]
                            line = "obj_file  " + of
                        else:
                            msg = msg + "Fix the Obj File"
                    if "diffuseTexture" in line:
                        if "diffuse" in asset["files"]:
                            dn = asset["files"]["diffuse"].rsplit('/', 1)[-1]
                            line = "diffuseTexture " + dn
                            log.debug(line)
                        else:
                            msg = msg + "Fix the Diffuse Texture"
                    if "normalmapTexture " in line:
                        if "normals" in asset["files"]:
                           nn = asset["files"]["normals"].rsplit('/', 1)[-1]
                           line = "normalmapTexture " + nn
                           log.debug(line)
                        else:
                            msg = msg + "Fix the Normals Map"
                    if "specularTexture" in line:
                        if "glossy" in asset["files"]:
                            sn = asset["files"]["glossy"].rsplit('/', 1)[-1]
                            line = "specularTexture " + sn
                            log.debug(line)
                        else:
                            msg = msg + "Fix the Specular Map"
                    if "displacementTexture " in line:
                        if "displacement" in asset["files"]:
                            dtn = asset["files"]["displacement"].rsplit('/', 1)[-1]
                            line = "displacementTexture  " + dtn
                            log.debug(line)
                        else:
                            msg = msg + "Fix the Displacement Map"
                    if "bumpTexture " in line:
                        if "bump" in asset["files"]:
                            bn = asset["files"]["bump"].rsplit('/', 1)[-1]
                            line = "bumpTexture  " + bn
                            log.debug(line)
                        else:
                            msg = msg + "Fix the Bump Map"
                           
                    if "aomapTexture " in line:
                        if "aomap" in asset["files"]:
                            bn = asset["files"]["aomap"].rsplit('/', 1)[-1]
                            line = "aomapTexture  " + bn
                            log.debug(line)
                        else:
                            msg = msg + "Fix the A O Map"
                    output.append(line)

                return '\n'.join(output)

            if self.get_extension(fileName) == "mhclo":
                lines = data.split("\n")
                output = []
                for line in lines:
                    if "material" in line:
                        dn = asset["files"]["mhmat"].rsplit('/', 1)[-1]
                        line = "material " + dn
                    if "name" in line:
                        filename = os.path.basename(saveAs)
                        name = os.path.splitext(filename)[0]
                        line = "name " + name
                    if "obj_file" in line:
                        of = asset["files"]["obj"].rsplit('/', 1)[-1]
                        line = "obj_file  " + of
                    output.append(line)
                    
                return '\n'.join(output)


            if self.get_extension(fileName) == "proxy":
                lines = data.split("\n")
                output = []
                for line in lines:
                    if "name" in line:
                       filename = os.path.basename(saveAs)
                       name = os.path.splitext(filename)[0]
                       line = "name " + name
                       log.debug(line)
                    if "obj_file" in line:
                       of = asset["files"]["obj_file"].rsplit('/', 1)[-1]
                       line = "obj_file  " + of
                       log.debug(line)
                    output.append(line)

                return '\n'.join(output)
            
        return data
    
    def downloadClothes(self):
        foundAsset = None
        category = str(self.categoryList.getCurrentItem())
        name = str(self.assetList.currentItem().text)
        for asset in self.clothesAssets[category]:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset)
            self.assetList.takeItem(self.assetList.currentRow())

    def downloadHair(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.hairAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"hair")
            self.assetList.takeItem(self.assetList.currentRow())

    def downloadEyebrows(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.eyebrowsAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"eyebrows")
            self.assetList.takeItem(self.assetList.currentRow())

    def downloadEyelashes(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.eyelashesAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"eyelashes")
            self.assetList.takeItem(self.assetList.currentRow())
            
    def downloadTeeth(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.teethAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"teeth")
            self.assetList.takeItem(self.assetList.currentRow())
            
    def downloadModel(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.modelAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"model")
            self.assetList.takeItem(self.assetList.currentRow())
            
    def downloadTarget(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.targetAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"custom")
            self.assetList.takeItem(self.assetList.currentRow())

    def downloadSkin(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.skinAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"skins")
            self.assetList.takeItem(self.assetList.currentRow())

    def downloadPose(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.poseAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"poses")
            self.assetList.takeItem(self.assetList.currentRow())
            
    def downloadMaterial(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.materialAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"material")
            self.assetList.takeItem(self.assetList.currentRow())
            
    def downloadProxy(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.proxyAssets:
            if str(asset["title"]) == name:
                foundAsset = asset
                
        if foundAsset:
            self.downloadAsset(foundAsset,"proxymeshes")
            self.assetList.takeItem(self.assetList.currentRow())
            
    def downloadRig(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.rigAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"rigs")
            self.assetList.takeItem(self.assetList.currentRow())
            
