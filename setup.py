from setuptools import setup, find_packages

setup(
    name="gitforsoftimage",
    version="0.2.0",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    package_data={"gitforsoftimage.layout": ["ui/*.*", "ui/images/*.*"],
                  "gitforsoftimage": ["data/.gitignore", "data/*.*"]},
    author="Cesar Saez",
    author_email="cesarte@gmail.com",
    description="Git integration on Softimage.",
    url="https://www.github.com/csaez/gitforsoftimage",
    license="GNU General Public License (GPLv3)",
    install_requires=["wishlib >= 0.1.4"],
    scripts=["GitForSoftimagePlugin.py"]
)
