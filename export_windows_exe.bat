pyinstaller -F main.py --hidden-import scipy._lib.messagestream --hidden-import sklearn.tree --hidden-import sklearn.neighbors.typedefs --hidden-import sklearn.neighbors.quad_tree --hidden-import sklearn.tree._utils