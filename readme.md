# Tool for importing speedTree tree assets using stmap and meshData 

# Installation
1 . Copy Krooz folder to Houdini<$HOME> scripts Folder make sure you have a **__init__.py** file there.
2 . Open houdini add new tool name it anything you want and on the script tab paste this code.

---------------------------------------------
    from Krooz import kroozer as kr
    import importlib

    importlib.reload(kr)

    vr = kr.Cool_kroozer()
    vr.show()
    
---------------------------------------------
