<img src"Krooz\icon\Tool.png"></img>
# Plugin for importing speedTree assets as USD-Ready Assets using stmap and mesh Data 

# Installation

<sub>1 . Copy Krooz folder to Houdini<$HOME> scripts Folder make sure you have a **__init__.py** file there.</sub><br />
<sub>2 . Open houdini add new tool name it anything you want and on the script tab paste this code.</sub>

---------------------------------------------
    from Krooz import kroozer as kr
    import importlib

    importlib.reload(kr)

    vr = kr.Cool_kroozer()
    vr.show()

---------------------------------------------
