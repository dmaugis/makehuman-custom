# MHAPI

MHAPI is a set of convenience calls intented to help you get access to things which might be difficult to find in the code otherwise.

If you place 1_mhapi in the plugins directory, it will self-register so that app.mhapi becomes available. Then (in a plugin or whatever
it is you are working with) you can make a call to one of MHAPI's functions. For example:

    from core import G
    someDir = G.app.mhapi.locations.getUserDataDir()

This would store the location of the "data" directory located amongst the user's makehuman files, i.e ~/makehuman/v1/data on a unixoid
system or MY DOCUMENTS\makehuman\v1\data on windows. 

In the following, "G.app.mhapi" has been excluded. So "internals" actually means "G.app.mhapi.internals".

## assets

These are calls related to reading, parsing and manipulating assets.

**openAssetFile(path, strip = False)** 

This opens an asset file and returns an [assetInfo](assetInfo.md) dict. If strip is set to True, the raw data is excluded from the dict. 

**writeAssetFile(assetInfo, createBackup = True)**

This (over)writes the asset file named in the assetInfo's "absolute path" key. If createBackup is set to True, any pre-existing file will be backed up to it's former name + ".bak"

## internals

These are calls which you would normally not need to make. They give you low-level access to internal MakeHuman objects. In most cases 
you would do operations via calls in other namespaces, not directly on these. 

**getHuman()**

Returns the central human object.

**getApp()**

Returns the central "app" object.

**getSkeleton()**

Returns the current Human's skeleton. This will return None if no skeleton is assigned.

## locations

Gives you information about file and directory locations. 

**getUnicodeAbsPath(path)**

Returns the abspath version of path, and ensures that it is correctly encoded

**getInstallationPath(subpath = "")**

Returns the unicode-encoded absolute path to the directory which contains the makehuman.py file. If subpath is given, assume that a subdirectory is indicated and return the combined path.

**getUserDataPath(subpath = "")**

Returns the unicode-encoded absolute path to the location of the user's "data" directory (as opposed to the installation's data directory). If subpath is given, assume that a subdirectory is indicated and return the combined path.

**getUserHomePath(subpath = "")**

Returns the unicode-encoded absolute path to the location of the user's makehuman directory (i.e normally ~/makehuman). If subpath is given, assume that a subdirectory is indicated and return the combined path.

**getSystemDataPath(subpath = "")**

Returns the unicode-encoded absolute path to the location of the installation's "data" directory (as opposed to the user's data directory). If subpath is given, assume that a subdirectory is indicated and return the combined path.

## mesh

Operations on and info about the mesh as such (ie direct access to vertices, edges and faces)

**getVertexCoordinates()**

Returns an array with the location of all vertices.

## modifiers

Gives you control and information about modifiers and targets.

**applyModifier(modifierName, power)**

Applies the named modifier, using the power (which is usually between 0.0 and 1.0, but sometimes between -1.0 and +1.0)

**applyTarget(targetName,power)**

Applies the named target, using the power (which is usually between 0.0 and 1.0, but sometimes between -1.0 and +1.0)

**getAppliedTargets()**

Get a list of which targets have been applied, and to what extent

**setAge(age)**

-

**setWeight(weight)**

-

**setMuscle(muscle)**

-

**setHeight(height)**

-

**setGender(gender)**

-

**getAvailableModifierNames()**

Get the full list of available modifiers. 

**applySymmetryLeft()**

-

**applySymmetryRight()**

-

## version

Information about hg and the current makehuman version.

**getBranch()**

Returns the name of the current local code branch, for example 'default'. If this is not possible to deduce, None is returned.

**getRevision()**

Return the full textual representation of the Hg revision, for example 'r1604 (d48f36771cc0)'. If this is not possible to deduce, None is returned.

**getRevisionId()**

Returns the hash id of the current local revision as an integer, for example d48f36771cc0. If this is not possible to deduce, None is returned.

**getRevisionNumber()**

Returns the number of the current local revision as an integer, for example 1604. If this is not possible to deduce, None is returned.

**getVersion()**

Returns the full textual description of the current version, for example 'MakeHuman unstable 20141120' or 'MakeHuman 1.0.2'.

**getVersionNumberAsArray()**

Returns the numeric representation of the version number as cells in an array, for example [1, 0, 2].

**getVersionNumberAsString()**

Returns the string representation of the version number, for example '1.0.2'.


