import xml.etree.ElementTree
import os
import re
from x3d import *

# get the animation from the input file name
def findAnimation(input_filename):
    input_filename = input_filename.replace('\\', '/')
    animation = re.sub(r".*/", "", input_filename).replace(".x3d", "")
    return animation

# get the animation from the input file name
def findFolder(input_filename):
    input_filename = input_filename.replace('\\', '/')
    folder = re.sub(r".*/(.*)/.*", "\\1", input_filename)
    return folder

def fixURL(url):
    url = url.replace('\\', '/')
    return url

def displayMenu(files, script_name, url):
    ifs_start = 1
    increment = -1/14
    group = Group()

    # First ill in the menu
    for fitem, input_file in enumerate(files):
        animation = findAnimation(input_file)
        folder = findFolder(input_file)
        if script_name == "FolderScript" and folder != "AnchorMenu":
            group.children += menuItem(
                [folder+"/AnchorMenu.x3d", fixURL(url)+folder+"/AnchorMenu.x3d"],
                folder+"/AnchorMenu.x3d",
                [folder],
                translation=[-2, ifs_start, 0.5],
                textTranslation=[0.05, -0.011, 0],
                load=False,
                size=[1, 0.1],
                fontSize=0.05,
                spacing=0.6)
            ifs_start += increment
        if script_name == "FileScript" and animation != "AnchorMenu":
            group.children += menuItem(
                [animation+".x3d", fixURL(url)+animation+".x3d"],
                animation,
                [animation],
                translation=[-1, ifs_start, 0.5],
                textTranslation=[0.05, -0.011, 0],
                load=False,
                size=[1, 0.1],
                fontSize=0.05,
                spacing=0.6)
            ifs_start += increment

    return group

def menuItem(url, description, label, translation=[-1.8, 1, 7.5], textTranslation=[0.05, -0.011, 0], load=False, size=[1, 0.1], fontSize=0.05, spacing=0.6):
            
    group = Group(
        children=[
            Anchor(
                DEF=description.replace("/", "_").replace(".x3d", "").replace("..", "__"),
                description=description,
                parameter=[ "target=_self" ],
                url=url,
                children=[
                    Transform(
                        translation=[1, 0, 0],
                        children=[
                            Transform(
                                translation=translation,
                                children=[
                                    Transform(
                                        translation=textTranslation,
                                        children=[
                                            Shape(
                                                appearance=Appearance(
                                                    material=Material(
                                                    diffuseColor=[0, 0, 0]
                                                    )
                                                ),
                                                geometry=Text(
                                                    string=label,
                                                    fontStyle=FontStyle(
                                                        justify=["MIDDLE",  "MIDDLE"],
                                                        size=fontSize,
                                                        spacing=spacing
                                                    )
                                                )
                                            )
                                        ]
                                    ),
                                    Transform(
                                        translation=[0, 0.01, -0.01],
                                        children=[
                                            Shape(
                                                appearance=Appearance(
                                                    material=Material(
                                                    diffuseColor=[1, 1, 1]
                                                    )
                                                ),
                                                geometry=Rectangle2D(
                                                    size=size
                                                )
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    return group.children

def walkX3d(dir, url, files, folders):
    if folders is None:
        files = sorted(set(files))
    else:
        files = sorted(set(folders + files))
    # produce final output
    model =  X3D(
        profile="Full",
        version="4.1",
        head=head(
            children=[
                component(
                    name="Core",
                    level=1
                ),
                component(
                    name="Grouping",
                    level=1
                ),
                component(
                    name="Text",
                    level=1
               ),
                meta(
                    name="title",
                    content="AnchorMenu.x3d"
                    ),
                meta(
                    name="identifier",
                    content="https://coderextreme.net/x3dmenus/AnchorMenu.x3d"
                    ),
                meta(
                    name="description",
                    content="Proto Menu Hierarchy"
                    ),
                meta(
                    name="created",
                    content="20 March 2026"
                    ),
                meta(
                    name="modified",
                    content="20 March 2026"
                    ),
                meta(
                    name="creator",
                    content="John Carlson"
                    ),
                meta(
                    name="generator",
                    content="CreateAnchorMenu.py"
                    ),
            ]
        ),
        Scene=Scene(
            children=[
                WorldInfo(
                    title="AnchorMenu.x3d"
                ),
                Viewpoint(
                    description='Default Viewpoint',
                    position=[0, 0, 3.5]
                ),
                displayMenu(folders, "FolderScript", url),
                displayMenu(files, "FileScript", url)
            ]
        )
    )
    file_output = os.path.join(dir,os.path.basename("AnchorMenu.x3d"))
    print(file_output)
    with open(file_output, "w") as output_file:
        output_file.write(model.XML())

if __name__ == "__main__":
    HOME = "C:/Users/jcarl/"
    HTTPS = "https://"
    BASE = "www.web3d.org/x3d/content/examples/"
    PATH = HOME+BASE

    # Source - https://stackoverflow.com/a/9728478
    # Posted by dhobbs, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-03-20, License - CC BY-SA 3.0

    # files = glob.glob(PATH+'*.x3d')
    for root, dirs, files in os.walk(PATH):
        url = root.replace(HOME, HTTPS)+"/"
        filtered_dirs = []
        for d in dirs:
            if not d in ("_thumbnails", "_viewpoints", "images", "javadoc", "lib", "nbproject", "originals"):
                filtered_dirs = filtered_dirs + [d];
        dirs = [ '..' ] + filtered_dirs
        folders = ["{}/{}/{}".format(root, d, "AnchorMenu.x3d") for d in dirs ]
        x3dfiles = ['{}/{}'.format(root, f) for f in files if f.endswith(".x3d") and not "new" in f]
        walkX3d(root, url, x3dfiles, folders)
