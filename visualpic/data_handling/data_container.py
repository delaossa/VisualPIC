""" Module for the DataContainer class """


from visualpic.data_handling.derived_field_definitions import (
    derived_field_definitions)
from visualpic.data_handling.fields import DerivedField
from visualpic.data_reading.folder_scanners import (OsirisFolderScanner,
                                                    OpenPMDFolderScanner,
                                                    HiPACEFolderScanner)


class DataContainer():
    
    """Class containing a providing access to all the simulation data"""

    def __init__(self, simulation_code, data_folder_path, plasma_density=None,
                 laser_wavelength=0.8e-6):
        """
        Initialize the data container.

        Parameters
        ----------

        simulation_code : str
            Name of the simulation code from which the data comes from.
            Possible values are 'Osiris, 'HiPACE' or 'openPMD' for any
            openPMD-compliant code.

        data_folder_path : str
            Path to the folder containing the simulation data.

        plasma_density : float
            (Optional) Value of the plasma density in m^{-3}. Needed only for
            'Osiris' and 'HiPACE' data to allow for conversion to
            non-normalized units.

        laser_wavelength : float
            Wavelength (in metres) of the laser in the simulation. Needed for
            computing the normalized vector potential.
        """
        self.simulation_code = simulation_code
        self.data_folder_path = data_folder_path
        self.sim_params = {'n_p': plasma_density,
                           'lambda_0': laser_wavelength}
        self.folder_scanner = self._get_folder_scanner(simulation_code,
                                                       plasma_density)
        self.folder_fields = []
        self.particle_species = []
        self.derived_fields = []

    def load_data(self, force_reload=False):
        """Load the data into the data container."""
        if not self.folder_fields or force_reload:
            self.folder_fields = self.folder_scanner.get_list_of_fields(
                self.data_folder_path)
        if not self.particle_species or force_reload:
            self.particle_species = self.folder_scanner.get_list_of_species(
                self.data_folder_path)
        if not self.derived_fields or force_reload:
            self.derived_fields = self._generate_derived_fields()

    def get_list_of_fields(self, include_derived=True):
        """Returns a list with the names of all available fields."""
        fields_list = []
        available_fields = self.folder_fields
        if include_derived:
            available_fields = available_fields + self.derived_fields
        for field in available_fields:
            fld_name = field.field_name
            fld_species = field.species_name
            if fld_species is not None:
                fld_name += ' [{}]'.format(fld_species)
            fields_list.append(fld_name)
        return fields_list

    def get_list_of_particle_species(self):
        """Returns a list with the names of all available particle species."""
        species_list = []
        for species in self.particle_species:
            species_list.append(species.species_name)
        return species_list

    def get_field(self, field_name, species_name=None):
        """
        Get a specified field from the available ones.

        Parameters
        ----------

        field_name : str
            Name of the field (in VisualPIC convention).

        species_name : str
            (Optional) Name of the particle species to which the field belongs.
            Only needed if the field actually belongs to a species.

        Returns
        -------
        A FolderField object containing the specified field.
        """
        for field in self.folder_fields + self.derived_fields:
            if (field_name == field.field_name and
                species_name == field.species_name):
                return field
        # raise error if no field has been found
        if species_name is not None:
            field_name = field_name + species_name
        available_fields = self.get_list_of_fields()
        raise ValueError("Field '{}' not found. ".format(field_name) +
                         "Available fields are {}.".format(available_fields))

    def get_particle_species(self, species_name):
        """
        Get a specified particle species from the available ones.

        Parameters
        ----------
        
        species_name : str
            Name of the particle species.

        Returns
        -------
        A ParticleSpecies object containing the specified species.
        """
        for species in self.particle_species:
            if species_name == species.species_name:
                return species
        # raise error if no species has been found
        available_species = self.get_list_of_particle_species()
        raise ValueError("Species '{}' not found. ".format(species_name) +
                         "Available species are {}.".format(available_species))

    def _get_folder_scanner(self, simulation_code, plasma_density=None):
        """Return the folder scanner corresponding to the simulation code."""
        if simulation_code == 'Osiris':
            return OsirisFolderScanner(plasma_density=plasma_density)
        elif simulation_code == 'HiPACE':
            return HiPACEFolderScanner(plasma_density=plasma_density)
        elif simulation_code == 'openPMD':
            return OpenPMDFolderScanner()
        else:
            raise ValueError("Unsupported code '{}'.".format(simulation_code) +
                             " Possible values are 'Osiris', 'HiPACE' or " +
                             "'openPMD'.")

    def _generate_derived_fields(self):
        """Returns a list with the available derived fields."""
        derived_field_list = []
        sim_geometry = self._get_simulation_geometry()
        folder_field_names = self.get_list_of_fields(include_derived=False)
        for derived_field in derived_field_definitions:
            if set(derived_field['requirements'][sim_geometry]).issubset(
                folder_field_names):
                base_fields = []
                for field_name in derived_field['requirements'][sim_geometry]:
                    base_fields.append(self.get_field(field_name))
                derived_field_list.append(DerivedField(
                    derived_field, sim_geometry, self.sim_params, base_fields))
        return derived_field_list

    def _get_simulation_geometry(self):
        """Returns a string with the geometry used in the simulation."""
        if self.folder_fields is not None:
            time_steps = self.folder_fields[0].timesteps
            fld_md = self.folder_fields[0].get_only_metadata(time_steps[0])
            return fld_md['field']['geometry']

