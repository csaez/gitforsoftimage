from setuptools import setup, find_packages

setup(
    name="gitforsoftimage",
    version="0.1.1",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    package_data={"gitforsoftimage.layout": ["ui/*.*", "ui/images/*.*"],
                  "gitforsoftimage": ["data/.gitignore", "data/*.*"]},
    author="Cesar Saez",
    author_email="cesarte@gmail.com",
    description="Integrate git as version control on Softimage.",
    url="http://www.github.com/csaez/gitforsoftimage",
    license="GNU General Public License (GPLv3)",
    install_requires=["wishlib >= 0.1.4"],
    scripts=["GitForSoftimagePlugin.py"]
)
