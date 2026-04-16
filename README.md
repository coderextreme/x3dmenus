# x3dmenus
Menus for X3D

### Production build at 
https://coderextreme.net/AnchorMenu.zip

### Production demo at
https://coderextreme.net/AnchorMenu.x3d

To build ~/www.web3d.org/x3d/content/examples/

Edit CreateProxy.py and edit HOME, HTTPS, BASE to taste near bottom of the file.  PATH should be a local folder on your machine. BASE is a common path between the file system and the web.

HOME = "C:/Users/jcarl/"
HTTPS = "https://"
BASE = "www.web3d.org/x3d/content/examples/"
PATH = HOME+BASE

Run

```
python -m venv venv
source venv/Scripts/activate
python CreateProxy.py
castle-model-viewer.exe ~/www.web3d.org/x3d/content/examples/AnchorMenu.x3d
```

Enjoy!
