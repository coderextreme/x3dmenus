# import xml.etree.ElementTree
import os
import re
import math
import urllib.request
from urllib.error import URLError, HTTPError
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

def createProxyPage(dir, original_file, menu_url, base_url):
    proxy_filename = f"AnchorMenu_{original_file}"
    base_filename = original_file.rsplit('.', 1)[0]

    encodings = {
        "XML (.x3d)": f"{base_filename}.x3d",
        "Classic VRML (.x3dv)": f"{base_filename}.x3dv",
        "JSON (.json)": f"{base_filename}.json",
        "X3DJSAIL (.java)": f"{base_filename}.java",
        "X3DPSAIL (.py)": f"{base_filename}.py",
        "Turtle (.ttl)": f"{base_filename}.ttl"
    }

    text_children = []
    routes = []
    button_children = []

    choice_index = 0
    y_offset = 2.0

    # Read encoding files and setup Text Switch UI
    for label, enc_file in encodings.items():
        enc_path = os.path.join(dir, enc_file)
        enc_url = f"{base_url}{enc_file}"
        content_lines = []

        # 1. Try fetching from Local File System
        if os.path.exists(enc_path):
            try:
                with open(enc_path, 'r', encoding='utf-8', errors='replace') as cf:
                    lines = cf.readlines()
                    # Truncate at 50 lines to keep X3D rendering from getting swamped
                    content_lines = [line.rstrip().replace('\t', '  ') for line in lines[:50]]
                    if len(lines) > 50:
                        content_lines.append("... (truncated)")
            except Exception as e:
                content_lines = [f"Error reading local file: {e}"]
        #else:
        #    # 2. Fallback to reading from URL if not found locally
        #    try:
        #        req = urllib.request.Request(enc_url, headers={'User-Agent': 'Mozilla/5.0'})
        #        with urllib.request.urlopen(req, timeout=5) as response:
        #            text = response.read().decode('utf-8', errors='replace')
        #            lines = text.splitlines()
        #            content_lines = [line.replace('\t', '  ') for line in lines[:50]]
        #            if len(lines) > 50:
        #                content_lines.append("... (truncated)")
        #    except HTTPError as e:
        #        content_lines = [f"File missing locally. HTTP Error {e.code}: {e.reason}"]
        #    except URLError as e:
        #        content_lines = [f"File missing locally. URL Error: {e.reason}"]
        #    except Exception as e:
        #        content_lines = [f"Error fetching URL: {e}"]

        text_shape = Shape(
            appearance=Appearance(
                material=Material(diffuseColor=[0.1, 0.9, 0.1]) # Terminal green code!
            ),
            geometry=Text(
                string=content_lines,
                fontStyle=FontStyle(size=0.1, family=["TYPEWRITER"], justify=["BEGIN", "FIRST"])
            )
        )
        text_children.append(text_shape)

        btn_def = f"Btn_{choice_index}"
        sensor_def = f"Sensor_{choice_index}"
        trigger_def = f"Trigger_{choice_index}"

        button = Transform(
            translation=[-2.5, y_offset, 0],
            children=[
                Shape(
                    appearance=Appearance(material=Material(diffuseColor=[0.2, 0.2, 0.8])),
                    geometry=Rectangle2D(size=[2.0, 0.3])
                ),
                Transform(
                    translation=[-0.9, -0.05, 0.01],
                    children=[
                        Shape(
                            appearance=Appearance(material=Material(diffuseColor=[1, 1, 1])),
                            geometry=Text(string=[label], fontStyle=FontStyle(size=0.15, justify=["BEGIN", "MIDDLE"]))
                        )
                    ]
                ),
                TouchSensor(DEF=sensor_def, description=f"Show {label}")
            ]
        )
        button_children.append(button)
        button_children.append(IntegerTrigger(DEF=trigger_def, integerKey=choice_index))

        routes.append(ROUTE(fromNode=sensor_def, fromField="isActive", toNode=trigger_def, toField="set_boolean"))
        routes.append(ROUTE(fromNode=trigger_def, fromField="triggerValue", toNode="TextSwitch", toField="whichChoice"))

        choice_index += 1
        y_offset -= 0.4

    # Setup browser UI
    browsers = [
        ("Castle Model Viewer", f"https://castle-engine.io/castle-model-viewer-web/?model={base_url}{original_file}"),
        ("X3DOM", f"https://www.web3d.org/x3d/content/examples/X3domViewer.html?url={base_url}{original_file}"),
        ("X_ITE", f"https://create3000.github.io/x_ite/playground/?url={base_url}{original_file}")
    ]

    browser_children = []
    y_offset = -1.0
    for b_label, b_url in browsers:
        b_btn = Transform(
            translation=[-2.5, y_offset, 0],
            children=[
                Anchor(
                    url=[b_url],
                    parameter=["target=_blank"],
                    description=f"Open in {b_label}",
                    children=[
                        Shape(
                            appearance=Appearance(material=Material(diffuseColor=[0.8, 0.2, 0.2])),
                            geometry=Rectangle2D(size=[2.0, 0.3])
                        ),
                        Transform(
                            translation=[-0.9, -0.05, 0.01],
                            children=[
                                Shape(
                                    appearance=Appearance(material=Material(diffuseColor=[1, 1, 1])),
                                    geometry=Text(string=[b_label], fontStyle=FontStyle(size=0.15, justify=["BEGIN", "MIDDLE"]))
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        browser_children.append(b_btn)
        y_offset -= 0.4

    back_btn = Transform(
        translation=[-2.5, 3.0, 0],
        children=[
            Anchor(
                url=[menu_url],
                description="Back to Menu",
                children=[
                    Shape(
                        appearance=Appearance(material=Material(diffuseColor=[0.8, 0.8, 0.2])),
                        geometry=Rectangle2D(size=[2.0, 0.3])
                    ),
                    Transform(
                        translation=[-0.9, -0.10, 0.01],
                        children=[
                            Shape(
                                appearance=Appearance(material=Material(diffuseColor=[0, 0, 0])),
                                geometry=Text(string=["< Back to Menu"], fontStyle=FontStyle(size=0.15, justify=["BEGIN", "MIDDLE"]))
                            )
                        ]
                    )
                ]
            )
        ]
    )

    # We scale down HUD extremely to prevent any complex large scene geometries from clipping through it
    hud_transform = Transform(
        DEF="HUD_Transform",
        children=[
            # Lower HUD by setting Y from 0 to -0.03
            Transform(
                translation=[0, -0.03, -0.4],
                scale=[0.05, 0.05, 0.05],
                children=[
                    back_btn,
                    Group(children=button_children),
                    Group(children=browser_children),
                    Transform(
                        translation=[-1.0, 3.0, 0],
                        children=[
                            Transform(
                                translation=[2.5, -3.0, -0.01],
                                children=[
                                    Shape(
                                        appearance=Appearance(material=Material(diffuseColor=[0, 0, 0], transparency=0.7)),
                                        geometry=Rectangle2D(size=[6.0, 6.5])
                                    )
                                ]
                            ),
                            Switch(
                                DEF="TextSwitch",
                                whichChoice=0,
                                children=text_children
                            )
                        ]
                    )
                ]
            )
        ]
    )

    hud_sensor = ProximitySensor(DEF="HUD_Sensor", size=[100000, 100000, 100000])

    routes.append(ROUTE(fromNode="HUD_Sensor", fromField="position_changed", toNode="HUD_Transform", toField="translation"))
    routes.append(ROUTE(fromNode="HUD_Sensor", fromField="orientation_changed", toNode="HUD_Transform", toField="rotation"))

    model_inline = Inline(DEF="Original_Model", url=[original_file])

    scene_children = [
        WorldInfo(title=proxy_filename),
        Viewpoint(description="Proxy View", position=[0, 0, 10]),
        hud_sensor,
        hud_transform,
        model_inline
    ] + routes

    proxy_model = X3D(
        profile="Full",
        version="4.1",
        head=head(
            children=[
                component(name="Core", level=1),
                component(name="EventUtilities", level=1),
                component(name="Geometry2D", level=2),
                component(name="Grouping", level=1),
                component(name="Scripting", level=1),
                component(name="Text", level=1),
                meta(name="title", content=proxy_filename),
                meta(name="generator", content="CreateDEFUSE2.py")
            ]
        ),
        Scene=Scene(children=scene_children)
    )

    file_output = os.path.join(dir, proxy_filename)
    with open(file_output, "w", encoding='utf-8') as output_file:
        output_file.write(proxy_model.XML())

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
            proxy_filename = f"AnchorMenu_{animation}.x3d"
            group.children += menuItem(
                [proxy_filename, fixURL(url)+proxy_filename],
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

        # Dynamically generate Proxy Page wrappers containing HUD encoding viewers for each item
        for f in page_files:
            original_file = os.path.basename(f)
            menu_url = "AnchorMenu.x3d" if p == 0 else f"AnchorMenu_{p+1}.x3d"
            createProxyPage(dir, original_file, menu_url, url)

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
