from minipatch import patch
import module

with patch("module.patchme", lambda: print("Patching worked!")):
    module.caller()
