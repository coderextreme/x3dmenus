import xml.etree.ElementTree
import os
import re
# import glob

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
    menu_str = ""

    # First ill in the menu
    for fitem, input_file in enumerate(files):
        animation = findAnimation(input_file)
        folder = findFolder(input_file)
        if script_name == "FolderScript" and folder != "AnchorMenu":
            menu_str +=  menuItem('"'+fixURL(url)+folder+"/AnchorMenu.x3d"+'" "'+folder+"/AnchorMenu.x3d"+'"', folder+"/AnchorMenu.x3d", '"'+folder+'"', translation=f"-2 {ifs_start} 0.5", textTranslation="0.05 -0.011 0", load="false", size="1 0.1", fontSize="0.05", spacing="0.6")
            ifs_start += increment
        if script_name == "FileScript" and animation != "AnchorMenu":
            menu_str +=  menuItem('"'+fixURL(url)+animation+'.x3d" "'+animation+'.x3d"', animation, '"'+animation+'"', translation=f"-1 {ifs_start} 0.5", textTranslation="0.05 -0.011 0", load="false", size="1 0.1", fontSize="0.05", spacing="0.6")
            ifs_start += increment

    return menu_str

def menuItem(url, description, label, translation="-1.8 1 7.5", textTranslation="0.05 -0.011 0", load="false", size="1 0.1", fontSize="0.05", spacing="0.6"):
            
    menu_item_str = f'''
            <Group>
              <Anchor DEF={label} description='{description}' url='{url}'>
              <Transform translation="-1 0 0">
                <Transform translation="{translation}">
                  <Transform translation="{textTranslation}">
                    <Shape>
                      <Appearance>
                        <Material diffuseColor="1 1 1"/>
                      </Appearance>
                      <Text string='{label}'>
                        <FontStyle justify='"MIDDLE" "MIDDLE"' size="{fontSize}" spacing="{spacing}">
                        </FontStyle>
                      </Text>
                    </Shape>
                  </Transform>
                  <Transform translation="0 0.01 -0.01">
                    <Shape>
                      <Appearance>
                        <Material diffuseColor="0 0 1"/>
                      </Appearance>
                      <Rectangle2D size="{size}"></Rectangle2D>
                    </Shape>
                  </Transform>
                </Transform>
              </Transform>
            </Anchor>
            </Group>
    '''
    return menu_item_str

def walkX3d(dir, url, files, folders):
    if folders is None:
        files = sorted(set(files))
    else:
        files = sorted(set(folders + files))
    # print(folders)
    # produce final output
    finalX3D = xml.etree.ElementTree.Element('X3D')
    finalX3D.text = "\n"
    finalX3D.tail = "\n"
    finalX3D.set("profile", "Full")
    finalX3D.set("version", "4.1")
    head = xml.etree.ElementTree.Element('head')
    head.text = "\n"
    head.tail = "\n"

    component = xml.etree.ElementTree.Element('component')
    component.set("name", "Core")
    component.set("level", "1")
    component.text = ""
    component.tail = "\n"
    head.append(component)

    component = xml.etree.ElementTree.Element('component')
    component.set("name", "Grouping")
    component.set("level", "1")
    component.text = ""
    component.tail = "\n"
    head.append(component)

    component = xml.etree.ElementTree.Element('component')
    component.set("name", "Text")
    component.set("level", "1")
    component.text = ""
    component.tail = "\n"
    head.append(component)

    meta = xml.etree.ElementTree.Element('meta')
    meta.text = ""
    meta.tail = "\n"
    meta.set("name", "title")
    meta.set("content", "AnchorMenu.x3d")
    head.append(meta)

    meta = xml.etree.ElementTree.Element('meta')
    meta.text = ""
    meta.tail = "\n"
    meta.set("name", "identifier")
    meta.set("content", "https://coderextreme.net/x3dmenus/AnchorMenu.x3d")
    head.append(meta)

    meta = xml.etree.ElementTree.Element('meta')
    meta.text = ""
    meta.tail = "\n"
    meta.set("name", "description")
    meta.set("content", "Proto Menu Hierarchy")
    head.append(meta)

    meta = xml.etree.ElementTree.Element('meta')
    meta.text = ""
    meta.tail = "\n"
    meta.set("name", "created")
    meta.set("content", "20 March 2026")
    head.append(meta)

    meta = xml.etree.ElementTree.Element('meta')
    meta.text = ""
    meta.tail = "\n"
    meta.set("name", "modified")
    meta.set("content", "20 March 2026")
    head.append(meta)

    meta = xml.etree.ElementTree.Element('meta')
    meta.text = ""
    meta.tail = "\n"
    meta.set("name", "creator")
    meta.set("content", "John Carlson")
    head.append(meta)

    meta = xml.etree.ElementTree.Element('meta')
    meta.text = ""
    meta.tail = "\n"
    meta.set("name", "generator")
    meta.set("content", "CreateAnchorMenu.py")
    head.append(meta)

    finalX3D.append(head)

    scene = xml.etree.ElementTree.Element('Scene')
    scene.text = "\n"
    scene.tail = "\n"

    finalX3D.append(scene)

    header = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.1//EN" "https://www.web3d.org/specifications/x3d-4.1.dtd">\n'
    xmlstr = xml.etree.ElementTree.tostring(finalX3D, encoding='unicode')

    # produce menu
    menu_str = '''
        <WorldInfo title="AnchorMenu.x3d"/>
    '''
            # <field accessType="outputOnly" type="SFTime" name="touchTime"/>
    menu_str += displayMenu(folders, "FolderScript", url)
    menu_str += displayMenu(files, "FileScript", url)

    menu_str += '''
      </Scene>
    </X3D>
    '''

    xmlString = f"{header}{xmlstr[:-16]}{menu_str}"
    file_output = os.path.join(dir,os.path.basename("AnchorMenu.x3d"))
    print(file_output)
    with open(file_output, "w") as output_file:
        output_file.write(xmlString)

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
            if not d in ("_thumbnails", "_viewpoints", "nbproject", "originals"):
                filtered_dirs = filtered_dirs + [d];
        dirs = [ '..' ] + filtered_dirs
        print("filter", dirs)
        folders = ["{}/{}/{}".format(root, d, "AnchorMenu.x3d") for d in dirs ]
        print("anchor", folders)
        x3dfiles = ['{}/{}'.format(root, f) for f in files if f.endswith(".x3d") and not "new" in f]
        walkX3d(root, url, x3dfiles, folders)
