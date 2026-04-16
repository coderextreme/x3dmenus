# import xml.etree.ElementTree
import os
import re
import math
from x3d import *

# get the animation from the input file name
def findAnimation(input_filename):
    input_filename = input_filename.replace('\\', '/')
    animation = re.sub(r".*/", "", input_filename).replace(".x3d", "")
    return animation

# get the folder from the input file name
def findFolder(input_filename):
    input_filename = input_filename.replace('\\', '/')
    folder = re.sub(r".*/(.*)/.*", "\\1", input_filename)
    return folder

def fixURL(url):
    url = url.replace('\\', '/')
    return url

def displayMenu(files, script_name, url, def_tracker):
    ifs_start = 1
    increment = -1/14
    group = Group()

    # Fill in the menu
    for fitem, input_file in enumerate(files):
        animation = findAnimation(input_file)
        folder = findFolder(input_file)
        if script_name == "FolderScript" and folder != "AnchorMenu":
            group.children += menuItem(
                [folder+"/AnchorMenu.x3d", fixURL(url)+folder+"/AnchorMenu.x3d"],
                folder+"/AnchorMenu.x3d",
                [folder],
                def_tracker,
                translation=[-2, ifs_start, 0.5],
                textTranslation=[-0.4, -0.011, 0],
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
                def_tracker,
                translation=[-1, ifs_start, 0.5],
                textTranslation=[-0.4, -0.011, 0],
                load=False,
                size=[1, 0.1],
                fontSize=0.05,
                spacing=0.6,
                thumbnail_url=["_thumbnails/"+animation+"Thumbnail.png", fixURL(url)+"_thumbnails/"+animation+"Thumbnail.png"],
                thumbnail_size=[0.1, 0.1])
            ifs_start += increment

    return group

def displayNavigation(prev_url, next_url, def_tracker):
    group = Group()
    # Place "Previous Page" at the top center
    if prev_url:
        group.children += menuItem(
            [prev_url],
            "PrevPage",
            ["<- Previous Page"],
            def_tracker,
            translation=[-1.5, 1.15, 0.5],
            textTranslation=[-0.4, -0.011, 0],
            load=False,
            size=[1.2, 0.1],
            fontSize=0.05,
            spacing=0.6)
    # Place "Next Page" at the bottom center
    if next_url:
        group.children += menuItem(
            [next_url],
            "NextPage",
            ["Next Page ->"],
            def_tracker,
            translation=[-1.5, -0.9, 0.5], 
            textTranslation=[-0.4, -0.011, 0],
            load=False,
            size=[1.2, 0.1],
            fontSize=0.05,
            spacing=0.6)
    return group

def menuItem(url, description, label, def_tracker, translation=[-1.8, 1, 7.5], textTranslation=[0.05, -0.011, 0], load=False, size=[1, 0.1], fontSize=0.05, spacing=0.6, thumbnail_url=None, thumbnail_size=[0.1, 0.1]):
    # Setup shared resources with DEF / USE
    
    # 1. Text Material and Appearance
    if 'TextMaterial' not in def_tracker:
        def_tracker['TextMaterial'] = True
        text_mat = Material(DEF='TextMaterial', diffuseColor=[0, 0, 0])
    else:
        text_mat = Material(USE='TextMaterial')

    if 'TextAppearance' not in def_tracker:
        def_tracker['TextAppearance'] = True
        text_app = Appearance(DEF='TextAppearance', material=text_mat)
    else:
        text_app = Appearance(USE='TextAppearance')

    # 2. FontStyle
    font_def = f"MenuFontStyle_{str(fontSize).replace('.', '_')}_{str(spacing).replace('.', '_')}"
    if font_def not in def_tracker:
        def_tracker[font_def] = True
        font_style = FontStyle(DEF=font_def, horizontal=True, justify=["BEGIN",  "BEGIN"], size=fontSize, spacing=spacing)
    else:
        font_style = FontStyle(USE=font_def)

    # 3. Background Material and Appearance
    if 'BackgroundMaterial' not in def_tracker:
        def_tracker['BackgroundMaterial'] = True
        bg_mat = Material(DEF='BackgroundMaterial', diffuseColor=[1, 1, 1])
    else:
        bg_mat = Material(USE='BackgroundMaterial')

    if 'BackgroundAppearance' not in def_tracker:
        def_tracker['BackgroundAppearance'] = True
        bg_app = Appearance(DEF='BackgroundAppearance', material=bg_mat)
    else:
        bg_app = Appearance(USE='BackgroundAppearance')

    # 4. Background Rectangle, Background Shape, and Background Transform
    bg_rect_def = f"BackgroundRectangle_{str(size[0]).replace('.', '_')}_{str(size[1]).replace('.', '_')}"
    if bg_rect_def not in def_tracker:
        def_tracker[bg_rect_def] = True
        bg_rect = Rectangle2D(DEF=bg_rect_def, size=size)
    else:
        bg_rect = Rectangle2D(USE=bg_rect_def)

    bg_shape_def = f"BackgroundShape_{str(size[0]).replace('.', '_')}_{str(size[1]).replace('.', '_')}"
    if bg_shape_def not in def_tracker:
        def_tracker[bg_shape_def] = True
        bg_shape = Shape(DEF=bg_shape_def, appearance=bg_app, geometry=bg_rect)
    else:
        bg_shape = Shape(USE=bg_shape_def)

    # We can share the Background Transform if it relies on identical dimensions
    bg_transform_def = f"BackgroundTransform_{str(size[0]).replace('.', '_')}_{str(size[1]).replace('.', '_')}"
    if bg_transform_def not in def_tracker:
        def_tracker[bg_transform_def] = True
        bg_transform = Transform(DEF=bg_transform_def, translation=[0, 0.01, -0.01], children=[bg_shape])
    else:
        bg_transform = Transform(USE=bg_transform_def)

    # 5. Thumbnail Rectangle and Thumbnail Transform
    if thumbnail_size is None:
        thumbnail_size = [0.1, 0.1]
    thumb_rect_def = f"ThumbnailRectangle_{str(thumbnail_size[0]).replace('.', '_')}_{str(thumbnail_size[1]).replace('.', '_')}"
    if thumb_rect_def not in def_tracker:
        def_tracker[thumb_rect_def] = True
        thumb_rect = Rectangle2D(DEF=thumb_rect_def, size=thumbnail_size)
    else:
        thumb_rect = Rectangle2D(USE=thumb_rect_def)

    if not thumbnail_url:
        # If there's no specific thumbnail, the entire thumbnail Transform is identical and can be safely shared
        empty_thumb_transform_def = f"EmptyThumbnailTransform_{str(thumbnail_size[0]).replace('.', '_')}_{str(thumbnail_size[1]).replace('.', '_')}"
        if empty_thumb_transform_def not in def_tracker:
            def_tracker[empty_thumb_transform_def] = True
            thumb_transform = Transform(
                DEF=empty_thumb_transform_def,
                translation=[-0.45, 0.01, 0.0],
                children=[
                    Shape(
                        appearance=Appearance(
                            texture=ImageTexture(url="")
                        ),
                        geometry=thumb_rect
                    )
                ]
            )
        else:
            thumb_transform = Transform(USE=empty_thumb_transform_def)
    else:
        # Custom thumbnails possess unique image textures; they cannot be cached with DEF/USE
        thumb_transform = Transform(
            translation=[-0.45, 0.01, 0.0],
            children=[
                Shape(
                    appearance=Appearance(
                        texture=ImageTexture(url=thumbnail_url)
                    ),
                    geometry=thumb_rect
                )
            ]
        )

    # Build the scene graph for this menu item
    group = Group(
        children=[
            Anchor(
                DEF=description.replace("/", "_").replace(".x3d", "").replace("..", "__"),
                description=description,
                parameter=[ "target=_self" ],
                url=url,
                children=[
                    TouchSensor(
                        description=description,
                    ),
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
                                                appearance=text_app,
                                                geometry=Text(
                                                    string=label,
                                                    fontStyle=font_style
                                                )
                                            )
                                        ]
                                    ),
                                    bg_transform,
                                    thumb_transform
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
    # Setup pagination variables
    ITEMS_PER_PAGE = 25 # Limits list size to fit screen height nicely
    
    folders_list = [] if folders is None else sorted(set(folders))
    files_list = sorted(set(files))

    total_folders = len(folders_list)
    total_files = len(files_list)
    
    # Calculate how many pages are required
    num_pages = max(1, math.ceil(total_folders / ITEMS_PER_PAGE), math.ceil(total_files / ITEMS_PER_PAGE))

    for p in range(num_pages):
        # We start a fresh tracker for DEF values per each dynamically created .x3d file
        def_tracker = {}

        # Slice out just the items for the current page
        page_folders = folders_list[p * ITEMS_PER_PAGE : (p + 1) * ITEMS_PER_PAGE]
        page_files = files_list[p * ITEMS_PER_PAGE : (p + 1) * ITEMS_PER_PAGE]

        filename = "AnchorMenu.x3d" if p == 0 else f"AnchorMenu_{p+1}.x3d"
        
        # Build Navigation URLs
        prev_url = None
        next_url = None
        
        if p > 0:
            prev_url = "AnchorMenu.x3d" if p == 1 else f"AnchorMenu_{p}.x3d"
        if p < num_pages - 1:
            next_url = f"AnchorMenu_{p+2}.x3d"

        # Produce final output for the page
        model =  X3D(
            profile="Full",
            version="4.1",
            head=head(
                children=[
                    component(name="Core", level=1),
                    component(name="Grouping", level=1),
                    component(name="Text", level=1),
                    meta(name="title", content=filename),
                    meta(name="identifier", content=f"https://coderextreme.net/x3dmenus/{filename}"),
                    meta(name="description", content="Proto Menu Hierarchy"),
                    meta(name="generator", content="CreateAnchorMenu.py"),
                ]
            ),
            Scene=Scene(
                children=[
                    WorldInfo(
                        title=filename
                    ),
                    Viewpoint(
                        description=f'Default Viewpoint Page {p+1}',
                        position=[0, 0, 3.5]
                    ),
                    displayMenu(page_folders, "FolderScript", url, def_tracker),
                    displayMenu(page_files, "FileScript", url, def_tracker),
                    displayNavigation(prev_url, next_url, def_tracker)
                ]
            )
        )
        file_output = os.path.join(dir, os.path.basename(filename))
        print(file_output)
        with open(file_output, "w") as output_file:
            output_file.write(model.XML())

if __name__ == "__main__":
    HOME = "C:/Users/jcarl/"
    HTTPS = "https://"
    BASE = "www.web3d.org/x3d/content/examples/"
    PATH = HOME+BASE

    for root, dirs, files in os.walk(PATH):
        url = root.replace(HOME, HTTPS)+"/"
        filtered_dirs = []
        for d in dirs:
            if not d in ("_thumbnails", "_viewpoints", "images", "javadoc", "lib", "nbproject", "originals"):
                filtered_dirs = filtered_dirs + [d];
        dirs = [ '..' ] + filtered_dirs
        
        # Get target anchors
        folders = ["{}/{}/{}".format(root, d, "AnchorMenu.x3d") for d in dirs ]
        
        # IMPORTANT: Filter out 'AnchorMenu*.x3d' files dynamically generated by this script so they aren't indexed as content!
        x3dfiles = ['{}/{}'.format(root, f) for f in files if f.endswith(".x3d") and not "new" in f and not "AnchorMenu" in f]
        
        walkX3d(root, url, x3dfiles, folders)
