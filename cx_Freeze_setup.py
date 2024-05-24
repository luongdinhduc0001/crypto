from cx_Freeze import setup, Executable

setup(

    name="MA-ABE System",

    version="1.0",

    description="Your application description",

    executables=[Executable("gui.py")],

)