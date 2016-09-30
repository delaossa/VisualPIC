# -*- coding: utf-8 -*-

#Copyright 2016 Ángel Ferran Pousa
#
#This file is part of VisualPIC.
#
#VisualPIC is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#VisualPIC is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with VisualPIC.  If not, see <http://www.gnu.org/licenses/>.


import os
import abc
import sys
import h5py
import numpy as np

from VisualPIC.DataReading.dataReader import DataReader


class RawDataReaderBase(DataReader):
    """Parent class for all rawDataReaders"""
    __metaclass__ = abc.ABCMeta
    def __init__(self, location, speciesName, dataName, internalName):
        DataReader.__init__(self, location, speciesName, dataName, internalName)
        self.internalName = dataName

    def GetData(self, timeStep):
        if timeStep != self.currentTimeStep:
            self.currentTimeStep = timeStep
            self.OpenFileAndReadData()
        return self.data

    def GetDataUnits(self):
        if self.dataUnits == "":
            self.OpenFileAndReadUnits()
        return self.dataUnits

    def GetTime(self, timeStep):
        if timeStep != self.currentTimeStep:
            self.currentTimeStep = timeStep
            self.OpenFileAndReadData()
        return self.currentTime

    def GetTimeUnits(self):
        if self.timeUnits == "":
            self.OpenFileAndReadUnits()
        return self.timeUnits

class OsirisRawDataReader(RawDataReaderBase):
    def __init__(self, location, speciesName, dataName, internalName):
        RawDataReaderBase.__init__(self, location, speciesName, dataName, internalName)

    def OpenFileAndReadData(self):
        file_content = self.OpenFile(self.currentTimeStep)
        self.data = np.array(file_content.get(self.internalName))
        self.currentTime = file_content.attrs["TIME"][0]
        file_content.close()

    def OpenFileAndReadUnits(self):
        file_content = self.OpenFile(0)
        if sys.version_info[0] < 3:
            self.dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])
            self.timeUnits = str(file_content.attrs["TIME UNITS"][0])
        else:
            self.dataUnits = str(list(file_content[self.internalName].attrs["UNITS"])[0])[2:-1].replace("\\\\","\\")
            self.timeUnits = str(file_content.attrs["TIME UNITS"][0])[2:-1].replace("\\\\","\\")
        file_content.close()

    def OpenFile(self, timeStep):
        fileName = "RAW-" + self.speciesName + "-" + str(timeStep).zfill(6)
        ending = ".h5"
        file_path = self.location + "/" + fileName + ending
        file_content = h5py.File(file_path, 'r')
        return file_content


class HiPACERawDataReader(RawDataReaderBase):
    def __init__(self, location, speciesName, dataName, internalName):
        RawDataReaderBase.__init__(self, location, speciesName, dataName, internalName)

    def OpenFileAndReadData(self):
        file_content = self.OpenFile(self.currentTimeStep)
        self.data = np.array(file_content.get(self.internalName))
        file_content.close()

    def OpenFileAndReadUnits(self):
        # TODO: complete unit declarations
        sd_unit = r'c/\omega_p'
        imp_unit = r'c/\omega_p'
        q_unit = 'C'
        time_unit = r'1/\omega_p'
        sd_names = ['x1', 'x2', 'x3']
        imp_names = ['p1', 'p2', 'p3']

        if self.internalName in sd_names:
            self.dataUnits = sd_unit
            self.timeUnits = time_unit
        if self.internalName in imp_names:
            self.dataUnits = imp_unit
            self.timeUnits = time_unit
        if self.internalName == 'q':
            self.dataUnits = q_unit
            self.timeUnits = time_unit

    def OpenFile(self, timeStep):
        fileName = 'raw_{:}_{:06d}.h5'.format(self.speciesName, timeStep)
        file_path = os.path.join(self.location, fileName)
        file_content = h5py.File(file_path, 'r')
        return file_content


class PIConGPURawDataReader(RawDataReaderBase):
    def __init__(self, location, speciesName, dataName, internalName):
        RawDataReaderBase.__init__(self, location, speciesName, dataName, internalName)

    def OpenFileAndReadData(self):
        raise NotImplementedError

    def OpenFileAndReadUnits(self):
        raise NotImplementedError
