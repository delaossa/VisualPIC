import sys
from setuptools import setup, find_packages

# Read version number
version = {}
with open("./visualpic/__version__.py") as fp:
    exec(fp.read(), version)

# Read long description
with open("README.md", "r") as fh:
    long_description = fh.read()

def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f.readlines()]

# Main setup command
setup(name='VisualPIC',
      version=version['__version__'],
      author='Angel Ferran Pousa',
      author_email="angel.ferran.pousa@desy.de",
      description='Data visualizer for PIC codes',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/AngelFP/VisualPIC',
      license='GPLv3',
      packages=find_packages('.'),
      package_data={
          'visualpic': ['ui/*',
                        'ui/icons/*',
                        'visualization/assets/vtk_visualizer/colormaps/*.h5',
                        'visualization/assets/vtk_visualizer/opacities/*.h5']
          },
      install_requires=read_requirements(),
      platforms='any',
      classifiers=(
          "Development Status :: 3 - Alpha",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Physics",
          "Topic :: Scientific/Engineering :: Visualization",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: OS Independent"),
      )
